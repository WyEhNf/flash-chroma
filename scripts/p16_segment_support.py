"""90分段实验的显式C ABI和只读数据支持，不隐式选择批处理策略。"""
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import numpy as np
import psutil
from study_p16_direct_compile import Library,save,digest,env
from bench_p16_model_pair import checked,source
from outplace_support import bind_to

U8=ct.POINTER(ct.c_uint8)
def output_hash(arrays):
    h=hashlib.sha256()
    for a in arrays:
        if a is not None and a.nbytes:h.update(memoryview(a).cast('B'))
    return h.hexdigest()
def arrays(sources,destinations):
    count=len(sources);assert count==len(destinations)
    s=(U8*count)(*(a.ctypes.data_as(U8) if a is not None and a.nbytes else None for a in sources))
    d=(U8*count)(*(a.ctypes.data_as(U8) if a is not None and a.nbytes else None for a in destinations))
    n=(ct.c_size_t*count)(*(a.nbytes if a is not None else 0 for a in sources))
    return s,d,n
def apply_segments(c,sources,destinations,kernel=1,threads=1):
    a=arrays(sources,destinations);error=ct.create_string_buffer(1024)
    rc=c.library.dll.jshc_cc_apply_to_segments(c.handle,*a,len(sources),kernel,threads,error,len(error))
    assert not rc,error.value

def setup(plan,load_frames=True):
    psutil.Process().cpu_affinity(plan['cpus']);directory=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    libs={k:Library(checked(v),v['sha256']) for k,v in plan['libraries'].items()}
    assert libs['baseline'].revision==87 and libs['candidate'].revision==90
    for lib in libs.values():bind_to(lib.dll)
    f=libs['candidate'].dll.jshc_cc_apply_to_segments
    f.argtypes=[ct.c_void_p,ct.POINTER(U8),ct.POINTER(U8),ct.POINTER(ct.c_size_t),ct.c_size_t,ct.c_int,ct.c_int,ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    driver=ct.CDLL(str(checked(plan['driver'])));f=driver.jshc_segment_driver
    f.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.POINTER(U8),ct.POINTER(U8),ct.c_size_t,ct.c_size_t,U8,U8,
        ct.c_int,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    mp=json.loads(checked(plan['model_plan']).read_text(encoding='utf-8'));chains={}
    for role,models in plan['roles'].items():
        paths=[checked(p) for p in models['models']];sides=[checked(p) if p else None for p in models['sidecars']]
        chains[role]={v:lib.chain(paths,sides) for v,lib in libs.items()}
    frames=source(mp)[0] if load_frames else None
    return libs,chains,frames,f,mp,directory,driver

def run_driver(f,pair,src,dst,packed_src,packed_dst,layout,role,threads,repeats):
    s,d,n=arrays(src,dst);times=np.empty(repeats,np.float64);error=ct.create_string_buffer(1024)
    old=pair['baseline'];new=pair['candidate']
    rc=f(ct.cast(old.library.dll.jshc_cc_apply_to,ct.c_void_p),ct.cast(new.library.dll.jshc_cc_apply_to_segments,ct.c_void_p),old.handle,new.handle,
        s,d,src[0].nbytes,len(src),packed_src.ctypes.data_as(U8),packed_dst.ctypes.data_as(U8),layout,role,threads,repeats,times.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error))
    assert not rc,error.value
    return times.tolist()

def close(chains):
    for pair in chains.values():
        for c in pair.values():c.close()
