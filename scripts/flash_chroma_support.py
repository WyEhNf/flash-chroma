"""单头文件实际执行的宿主FFI；模型、库和运行配置均保留身份。"""
from __future__ import annotations

import ctypes as ct
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import p16_unified_support as native

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {'desktop': 1, 'mobile': 2, 'embedded': 3, 'portable': 4}
BACKENDS = {'auto': 0, 'scalar': 1, 'avx2': 2, 'avx512': 8}
REPRESENTATIONS = {'sparse': 0, 'direct_u8': 1, 'direct_u16': 2, 'direct_rgb24': 3}
STATUS = {0: '成功', 1: '空指针', 2: '格式错误', 3: '容量错误', 4: '范围错误',
          5: '尺寸溢出', 6: '内存重叠', 7: '状态错误', 8: '后端或目标不支持',
          9: '工作区预算不足', 10: '调色板容量不足'}
U8 = ct.POINTER(ct.c_uint8)


class Bytes(ct.Structure):
    _fields_ = [('data', U8), ('size', ct.c_size_t)]


class Config(ct.Structure):
    _fields_ = [('target', ct.c_uint32), ('backend', ct.c_uint32),
                ('representation', ct.c_uint32), ('threads', ct.c_uint32),
                ('block_pixels', ct.c_uint64), ('max_workspace_bytes', ct.c_uint64)]


class Info(ct.Structure):
    _fields_ = [(key, ct.c_uint64) for key in ('persistent_bytes', 'temporary_bytes',
                'arena_bytes', 'model_bytes', 'alignment', 'object_bytes')] + [
                ('selected_backend', ct.c_uint32), ('palette_entries', ct.c_uint32)]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def sha(array):
    return hashlib.sha256(memoryview(array).cast('B')).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def configuration(representation='sparse', backend='auto', threads=1, target='desktop',
                  block_pixels=65536, max_workspace_bytes=(1 << 63)-1):
    return dict(target=target, backend=backend, representation=representation, threads=threads,
                block_pixels=block_pixels, max_workspace_bytes=max_workspace_bytes)


def config_struct(config):
    if not 1 <= config['threads'] <= 256 or not 1 <= config['block_pixels'] <= (1 << 63)-1:
        raise ValueError('线程或块大小超出允许范围')
    if not 0 <= config['max_workspace_bytes'] <= (1 << 63)-1:
        raise ValueError('工作区预算超出允许范围')
    return Config(TARGETS[config['target']], BACKENDS[config['backend']],
                  REPRESENTATIONS[config['representation']], config['threads'],
                  config['block_pixels'], config['max_workspace_bytes'])


class Model:
    def __init__(self, profile, root):
        if profile.get('interpolation_basis') != 'tetra_q16':
            raise ValueError('单头文件仅接受tetra_q16模型')
        if len(profile['models']) != 4 or len(profile['sidecars']) != 4:
            raise ValueError('模型必须有四级及四个侧表槽')
        self.profile = profile
        self.buffers = []
        self.records = []
        def read(record):
            if record is None:
                return Bytes(None, 0)
            path = Path(record['path'])
            if not path.is_absolute():
                path = root / path
            payload = path.read_bytes()
            actual = hashlib.sha256(payload).hexdigest()
            if actual != record['sha256']:
                raise ValueError('模型SHA不一致：' + str(path))
            storage = (ct.c_uint8 * len(payload)).from_buffer_copy(payload)
            self.buffers.append(storage)
            self.records.append({'path': str(path.resolve()), 'sha256': actual, 'bytes': len(payload)})
            return Bytes(ct.cast(storage, U8), len(payload))
        self.models = (Bytes * 4)(*(read(v) for v in profile['models']))
        self.sidecars = (Bytes * 4)(*(read(v) for v in profile['sidecars']))
        self.total_bytes = sum(record['bytes'] for record in self.records)


def load_models(manifest, names=None):
    path = Path(manifest).resolve()
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value.get('profiles'),dict) or not value['profiles']:
        raise ValueError('模型清单至少需要一个profile，不能把空集合当作验证通过')
    root = Path(value.get('path_root', path.parent))
    if not root.is_absolute():
        root = path.parent / root
    profiles = {name:dict(row, interpolation_basis=row.get('interpolation_basis',value.get('interpolation_basis')))
                for name,row in value['profiles'].items()}
    return value, {name: Model(profiles[name], root) for name in (names or profiles)}


class Library:
    def __init__(self, path):
        native.setup()
        self.path = Path(path).resolve()
        self.sha256 = digest(self.path)
        receipt_path = Path(str(self.path)+'.build.json')
        self.build_receipt = json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else None
        if self.build_receipt is not None and self.build_receipt.get('library_sha256') != self.sha256:
            raise ValueError('库SHA与实际链接回执不同')
        self.dll = ct.CDLL(str(self.path))
        d = self.dll
        d.fc_bridge_capabilities.argtypes = []
        d.fc_bridge_capabilities.restype = ct.c_uint32
        d.fc_bridge_query.argtypes = [ct.POINTER(Bytes), ct.POINTER(Bytes), ct.POINTER(Config), ct.POINTER(Info)]
        d.fc_bridge_query.restype = ct.c_int
        d.fc_bridge_create.argtypes = [ct.POINTER(Bytes), ct.POINTER(Bytes), ct.POINTER(Config), ct.POINTER(ct.c_void_p), ct.POINTER(Info)]
        d.fc_bridge_create.restype = ct.c_int
        d.fc_bridge_apply.argtypes = [ct.c_void_p, U8, ct.c_size_t, ct.c_size_t, U8, ct.c_size_t,
                                     ct.c_size_t, ct.c_size_t, ct.c_size_t]
        d.fc_bridge_apply.restype = ct.c_int
        d.fc_bridge_destroy.argtypes = [ct.c_void_p]
        d.fc_bridge_destroy.restype = None
        self.prepare_info = getattr(d, 'fc_bridge_prepare_info', None)
        if self.prepare_info is not None:
            self.prepare_info.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint64), ct.c_size_t]
            self.prepare_info.restype = ct.c_int
        d.fc_c_bridge_apply.argtypes = [ct.POINTER(Bytes), ct.POINTER(Bytes), U8, ct.c_size_t,
            ct.c_size_t, U8, ct.c_size_t, ct.c_size_t, ct.c_size_t, ct.c_size_t]
        d.fc_c_bridge_apply.restype = ct.c_int
        self.capabilities = int(d.fc_bridge_capabilities())

    def record(self):
        return {'path': str(self.path), 'sha256': self.sha256, 'available_backends': self.capabilities,
                'build_receipt': self.build_receipt,
                'headers': self.build_receipt['headers'] if self.build_receipt else None,
                'header_identity_scope': '链接后来源回执' if self.build_receipt else '缺少链接回执，不以当前文件推断编译来源'}

    def query(self, model, config):
        cfg, info = config_struct(config), Info()
        status = int(self.dll.fc_bridge_query(model.models, model.sidecars, ct.byref(cfg), ct.byref(info)))
        return status, {key: int(getattr(info, key)) for key, _ in Info._fields_}

    def create(self, model, config):
        return Engine(self, model, config)

    def c_apply(self, model, source, target):
        check_arrays(source,target)
        if source.size % 3 or target.nbytes < source.nbytes:
            raise ValueError('连续RGB8缓冲的长度或目标容量错误')
        pixels = source.size // 3
        return int(self.dll.fc_c_bridge_apply(model.models, model.sidecars, source.ctypes.data_as(U8),
            source.nbytes, pixels*3, target.ctypes.data_as(U8), target.nbytes, pixels*3, pixels, 1))


def check_arrays(source,target):
    if not isinstance(source,np.ndarray) or not isinstance(target,np.ndarray):
        raise ValueError('图像必须是numpy数组')
    if source.dtype != np.uint8 or target.dtype != np.uint8 or not source.flags.c_contiguous or not target.flags.c_contiguous:
        raise ValueError('FFI只接受连续uint8图像视图')
    if not target.flags.writeable:
        raise ValueError('输出缓冲必须可写')


class Engine:
    def __init__(self, library, model, config):
        self.library, self.model, self.config = library, model, dict(config)
        self.handle, info, cfg = ct.c_void_p(), Info(), config_struct(config)
        begin = time.perf_counter_ns()
        status = int(library.dll.fc_bridge_create(model.models, model.sidecars, ct.byref(cfg),
                                                  ct.byref(self.handle), ct.byref(info)))
        self.prepare_ms = (time.perf_counter_ns() - begin) / 1e6
        if status:
            raise RuntimeError(f'运行库准备失败：{status} {STATUS.get(status, "宿主适配错误")}；{config}')
        self.info = {key: int(getattr(info, key)) for key, _ in Info._fields_}
        self.preparation = None
        diagnostic = getattr(library, 'prepare_info', None)
        if diagnostic is not None:
            values = (ct.c_uint64 * 2)()
            if diagnostic(self.handle, values, 2):
                self.close()
                raise RuntimeError('准备路径诊断失败')
            self.preparation = {'suffix_cache': bool(values[0]), 'cache_entries': int(values[1])}

    def apply(self, source, target, width=None, height=1, source_stride=None, target_stride=None):
        check_arrays(source,target)
        if width is None and source.size % 3:
            raise ValueError('连续RGB8像素字节数必须为3的倍数')
        width = source.size // 3 if width is None else width
        source_stride = width*3 if source_stride is None else source_stride
        target_stride = width*3 if target_stride is None else target_stride
        begin = time.perf_counter_ns()
        status = int(self.library.dll.fc_bridge_apply(self.handle, source.ctypes.data_as(U8), source.nbytes,
            source_stride, target.ctypes.data_as(U8), target.nbytes, target_stride, width, height))
        elapsed = (time.perf_counter_ns() - begin) / 1e6
        if status:
            raise RuntimeError(f'映射失败：{status} {STATUS.get(status)}')
        return elapsed

    def close(self):
        if self.handle:
            self.library.dll.fc_bridge_destroy(self.handle)
            self.handle = ct.c_void_p()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
