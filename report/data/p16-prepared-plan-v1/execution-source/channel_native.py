"""独立实验C ABI的显式加载器；不把侧表模型伪装成SLUT v1。"""
from __future__ import annotations
import ctypes as ct
import hashlib
from pathlib import Path
import sys
import numpy as np


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


class Library:
    def __init__(self,path,expected_sha256):
        self.path=Path(path).resolve()
        if sys.byteorder!='little' or digest(self.path)!=expected_sha256:
            raise ValueError('实验库要求little-endian与冻结DLL SHA')
        self.sha256=expected_sha256
        self.dll=ct.CDLL(str(self.path))
        d=self.dll;u8=ct.POINTER(ct.c_uint8);text=ct.POINTER(ct.c_char)
        d.jshc_cc_abi_version.argtypes=[];d.jshc_cc_abi_version.restype=ct.c_uint32
        d.jshc_cc_capabilities.argtypes=[];d.jshc_cc_capabilities.restype=ct.c_uint32
        d.jshc_cc_create.argtypes=[ct.POINTER(ct.c_char_p),ct.POINTER(ct.c_char_p),ct.c_size_t,ct.POINTER(ct.c_void_p),text,ct.c_size_t];d.jshc_cc_create.restype=ct.c_int
        d.jshc_cc_destroy.argtypes=[ct.c_void_p];d.jshc_cc_destroy.restype=None
        d.jshc_cc_model_bytes.argtypes=[ct.c_void_p];d.jshc_cc_model_bytes.restype=ct.c_size_t
        d.jshc_cc_apply.argtypes=[ct.c_void_p,u8,ct.c_size_t,ct.c_int,ct.c_int,text,ct.c_size_t];d.jshc_cc_apply.restype=ct.c_int
        d.jshc_cc_bench.argtypes=[ct.c_void_p,u8,u8,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_double),text,ct.c_size_t];d.jshc_cc_bench.restype=ct.c_int
        if d.jshc_cc_abi_version()!=1:raise ValueError('未知实验ABI版本')
        self.capabilities=int(d.jshc_cc_capabilities())
        self.revision=1
        if hasattr(d,'jshc_cc_revision'):
            d.jshc_cc_revision.argtypes=[];d.jshc_cc_revision.restype=ct.c_uint32
            self.revision=int(d.jshc_cc_revision())

    def chain(self,models,sidecars=None):return Chain(self,models,sidecars)


class Chain:
    def __init__(self,library,models,sidecars=None):
        self.library=library;self.handle=ct.c_void_p()
        if not 1<=len(models)<=4:raise ValueError('实验链需要1..4个模型')
        if sidecars is None:sidecars=[None]*len(models)
        if len(sidecars)!=len(models):raise ValueError('侧表必须逐级对应')
        self.models=[Path(p).resolve() for p in models]
        self.sidecars=[Path(p).resolve() if p is not None else None for p in sidecars]
        for p in [*self.models,*[p for p in self.sidecars if p is not None]]:
            if not p.is_file():raise FileNotFoundError(p)
        paths=(ct.c_char_p*len(models))(*(str(p).encode('utf-8') for p in self.models))
        fractions=(ct.c_char_p*len(models))(*(str(p).encode('utf-8') if p is not None else None for p in self.sidecars))
        error=ct.create_string_buffer(1024)
        if library.dll.jshc_cc_create(paths,fractions,len(models),ct.byref(self.handle),error,len(error)):
            raise RuntimeError(error.value.decode('utf-8',errors='replace'))
        try:
            self.inputs_sha256={str(p):digest(p) for p in [*self.models,*[p for p in self.sidecars if p is not None]]}
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.handle.value:self.library.dll.jshc_cc_destroy(self.handle);self.handle=ct.c_void_p()

    def __enter__(self):return self
    def __exit__(self,*args):self.close()

    def _check(self):
        if not self.handle.value:raise ValueError('实验句柄已经关闭')

    @property
    def model_bytes(self):
        self._check();return int(self.library.dll.jshc_cc_model_bytes(self.handle))

    @staticmethod
    def _rgb(array,writable=False):
        a=np.asarray(array)
        if (a.dtype!=np.uint8 or a.ndim<2 or a.shape[-1]!=3 or not a.flags.c_contiguous
                or (writable and not a.flags.writeable)):
            raise ValueError('需要连续RGB8，原地映射要求可写')
        return a

    def apply(self,rgb,*,kernel='scalar',threads=1):
        self._check();rgb=self._rgb(rgb,True)
        if kernel not in ('scalar','avx2'):raise ValueError('只有scalar/avx2实验后端')
        error=ct.create_string_buffer(1024)
        code=self.library.dll.jshc_cc_apply(self.handle,rgb.ctypes.data_as(ct.POINTER(ct.c_uint8)),rgb.nbytes,
            int(kernel=='avx2'),threads,error,len(error))
        if code:raise RuntimeError(error.value.decode('utf-8',errors='replace'))
        return rgb

    def bench(self,source,*,kernel='avx2',threads=4,repeats=5):
        self._check();source=self._rgb(source)
        if kernel not in ('scalar','avx2') or not isinstance(repeats,int) or isinstance(repeats,bool) or not 1<=repeats<=100:
            raise ValueError('实验基准后端或次数不合法')
        work=np.empty_like(source);apply=np.empty(repeats,np.float64);total=np.empty(repeats,np.float64)
        error=ct.create_string_buffer(1024)
        code=self.library.dll.jshc_cc_bench(self.handle,source.ctypes.data_as(ct.POINTER(ct.c_uint8)),
            work.ctypes.data_as(ct.POINTER(ct.c_uint8)),source.nbytes,int(kernel=='avx2'),threads,repeats,
            apply.ctypes.data_as(ct.POINTER(ct.c_double)),total.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error))
        if code:raise RuntimeError(error.value.decode('utf-8',errors='replace'))
        return {'apply_seconds':apply.tolist(),'copy_apply_seconds':total.tolist()}
