"""102统一运行时验证与百图基准共用的最小C ABI封装。"""
from __future__ import annotations

import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
from PIL import Image
import psutil

U8 = ct.POINTER(ct.c_uint8)
TEXT = ct.POINTER(ct.c_char)
BACKENDS = {'scalar': 0, 'avx2': 1, 'avx512': 2}
PIXELS = 100 * 1024 * 768
DLL_DIRECTORIES = []


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def sha(array):
    return hashlib.sha256(memoryview(array).cast('B')).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def resolve_record(record, root):
    if not isinstance(record, dict) or set(('path', 'sha256')) - record.keys():
        raise ValueError('输入记录必须含path与sha256')
    path = Path(record['path'])
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if digest(path) != record['sha256']:
        raise ValueError('文件摘要不符：' + str(path))
    return {'path': str(path), 'sha256': record['sha256']}


def load_plan(path):
    """只读取本轮实际需要的输入，不把旧计划的源冻结称为本轮重新验收。"""
    path = Path(path).resolve()
    value = json.loads(path.read_text(encoding='utf-8'))
    root = Path(value.get('path_root', path.parent))
    if not root.is_absolute():
        root = path.parent / root
    models = {}
    for name, row in value['models'].items():
        if len(row['models']) != 4 or len(row['sidecars']) != 4:
            raise ValueError('本阶段要求固定四级模型与四个对应侧表槽')
        models[name] = {'models': [resolve_record(v, root) for v in row['models']],
            'sidecars': [resolve_record(v, root) if v else None for v in row['sidecars']]}
        oracle = value.get('oracles', {}).get(name, row.get('oracle'))
        if oracle is None:
            raise ValueError('每个模型必须提供独立完整RGB8 cube')
        models[name]['oracle'] = resolve_record(oracle, root)
        if Path(models[name]['oracle']['path']).stat().st_size != (1 << 24) * 3:
            raise ValueError('完整RGB8 cube必须为256³个RGB8像素')
    photo_record = resolve_record(value['photo_model_plan'], root)
    photo_path = Path(photo_record['path'])
    photo_plan = json.loads(photo_path.read_text(encoding='utf-8'))
    photo_root = Path(photo_plan.get('path_root', photo_path.parent))
    if not photo_root.is_absolute():
        photo_root = photo_path.parent / photo_root
    manifest = resolve_record(photo_plan['manifest'], photo_root)
    data_root = Path(photo_plan['data_root'])
    if not data_root.is_absolute():
        data_root = photo_root / data_root
    return {'input_plan': {'path': str(path), 'sha256': digest(path)}, 'models': models,
        'photo_model_plan': photo_record, 'manifest': manifest, 'data_root': str(data_root.resolve()),
        'photo_source_sha256': value['photo_source_sha256'],
        'scope': '固定输入模型与侧表；路径相对path_root或计划所在目录解析，SHA逐文件检查。'}


def photos(plan):
    manifest = json.loads(Path(plan['manifest']['path']).read_text(encoding='utf-8'))
    if len(manifest['images']) != 100:
        raise ValueError('本阶段批次必须正好100图')
    frames = np.empty((100, 768, 1024, 3), np.uint8)
    inputs = []
    for index, row in enumerate(manifest['images']):
        item = row['evaluation']
        path = Path(plan['data_root']) / item['path']
        if digest(path) != item['sha256']:
            raise ValueError('照片文件摘要不符：' + str(path))
        with Image.open(path) as image:
            image.load()
            pixels = np.asarray(image)
        if pixels.shape != (768, 1024, 3) or pixels.dtype != np.uint8:
            raise ValueError('照片必须为1024×768 RGB8')
        frames[index] = pixels
        if sha(frames[index]) != item['pixel_sha256']:
            raise ValueError('照片解码像素摘要不符：' + str(path))
        inputs.append({'path': str(path.resolve()), 'sha256': item['sha256'],
            'pixel_sha256': item['pixel_sha256']})
    if sha(frames) != plan['photo_source_sha256']:
        raise ValueError('百图源像素摘要不符')
    return frames, inputs


def expected_photos(frames, cube):
    results = []
    stream = hashlib.sha256()
    for frame in frames:
        values = frame.astype(np.uint32)
        indices = (values[:, :, 0] << 16) | (values[:, :, 1] << 8) | values[:, :, 2]
        prediction = cube[indices]
        results.append(sha(prediction))
        stream.update(memoryview(prediction).cast('B'))
    return {'batch_sha256': stream.hexdigest(), 'per_image_sha256': results}


def rss():
    value = psutil.Process().memory_info()
    return {name: int(getattr(value, name)) for name in ('rss', 'vms', 'peak_wset', 'private')
        if hasattr(value, name)}


def environment(build_receipt=None):
    cpu = platform.processor()
    if os.name == 'nt':
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    result = {'platform': platform.platform(), 'machine': platform.machine(), 'cpu': cpu,
        'python': sys.version, 'numpy': np.__version__, 'pillow': Image.__version__,
        'psutil': psutil.__version__, 'affinity': psutil.Process().cpu_affinity(),
        'physical_cores': psutil.cpu_count(logical=False), 'logical_cpus': psutil.cpu_count(),
        'cpu_only': True, 'locked_frequency': False, 'compiler_and_flags': '未提供构建回执，不推断',
        'target_cpu': 'Intel Xeon Gold 6140；仅当实际cpu相符时才属于目标机结果'}
    if build_receipt is not None:
        path = Path(build_receipt).resolve()
        result['build_receipt'] = {'path': str(path), 'sha256': digest(path),
            'content': json.loads(path.read_text(encoding='utf-8'))}
        result['compiler_and_flags'] = '见绑定的构建回执；本脚本不改编译参数'
    try:
        result['commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
            cwd=Path(__file__).resolve().parents[1], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        result['commit'] = None
    result['script_sha256'] = {str(Path(__file__).resolve()): digest(__file__)}
    return result


def setup(dll_directory=None, cpus=None):
    if cpus:
        psutil.Process().cpu_affinity([int(value) for value in cpus.split(',')])
    if os.name == 'nt':
        directory = Path(dll_directory) if dll_directory else Path('E:/mingw64/bin')
        if directory.is_dir():
            DLL_DIRECTORIES.append(os.add_dll_directory(str(directory)))


class Library:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.sha256 = digest(self.path)
        if sys.byteorder != 'little':
            raise ValueError('当前实验ABI仅验证little-endian')
        self.dll = ct.CDLL(str(self.path))
        d = self.dll
        for name in ('jshc_cc_abi_version', 'jshc_cc_revision', 'jshc_cc_capabilities'):
            getattr(d, name).argtypes = []
            getattr(d, name).restype = ct.c_uint32
        if d.jshc_cc_abi_version() != 1:
            raise ValueError('未知实验ABI')
        self.revision = int(d.jshc_cc_revision())
        self.capabilities = int(d.jshc_cc_capabilities())
        d.jshc_cc_create_for_workload.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p),
            ct.c_size_t, ct.c_uint64, ct.POINTER(ct.c_void_p), TEXT, ct.c_size_t]
        d.jshc_cc_create_for_workload.restype = ct.c_int
        d.jshc_cc_destroy.argtypes = [ct.c_void_p]
        d.jshc_cc_destroy.restype = None
        d.jshc_cc_model_bytes.argtypes = [ct.c_void_p]
        d.jshc_cc_model_bytes.restype = ct.c_size_t
        d.jshc_cc_apply.argtypes = [ct.c_void_p, U8, ct.c_size_t, ct.c_int, ct.c_int, TEXT, ct.c_size_t]
        d.jshc_cc_apply.restype = ct.c_int
        d.jshc_cc_apply_to.argtypes = [ct.c_void_p, U8, U8, ct.c_size_t, ct.c_int, ct.c_int, TEXT, ct.c_size_t]
        d.jshc_cc_apply_to.restype = ct.c_int

    def record(self):
        return {'path': str(self.path), 'sha256': self.sha256, 'revision': self.revision,
            'capabilities': self.capabilities, 'avx512_cpu_os_available': bool(self.capabilities & 8)}

    def supported(self, backend):
        return backend == 'scalar' or bool(self.capabilities & (2 if backend == 'avx2' else 8))

    def create(self, row, hint=PIXELS):
        if type(hint) is not int or not 0 <= hint <= (1 << 64) - 1:
            raise ValueError('预计像素必须为0..UINT64_MAX的Python int')
        paths = (ct.c_char_p * 4)(*(v['path'].encode('utf-8') for v in row['models']))
        sides = (ct.c_char_p * 4)(*(v['path'].encode('utf-8') if v else None for v in row['sidecars']))
        return Chain(self, paths, sides, hint)


class Chain:
    def __init__(self, library, paths, sides, hint):
        self.library = library
        self.handle = ct.c_void_p()
        error = ct.create_string_buffer(1024)
        started = time.perf_counter_ns()
        rc = library.dll.jshc_cc_create_for_workload(paths, sides, 4, hint,
            ct.byref(self.handle), error, len(error))
        self.prepare_seconds = (time.perf_counter_ns() - started) * 1e-9
        self.creation_started_ns = started
        if rc:
            raise RuntimeError(error.value.decode('utf-8', 'replace'))

    def _check(self):
        if not self.handle.value:
            raise ValueError('句柄已关闭')

    @property
    def model_bytes(self):
        self._check()
        return int(self.library.dll.jshc_cc_model_bytes(self.handle))

    def close(self):
        if self.handle.value:
            self.library.dll.jshc_cc_destroy(self.handle)
            self.handle = ct.c_void_p()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def apply(self, source, target, backend, threads, same=False):
        error = ct.create_string_buffer(1024)
        started = time.perf_counter_ns()
        if same:
            rc = self.library.dll.jshc_cc_apply(self.handle, target.ctypes.data_as(U8), target.nbytes,
                BACKENDS[backend], threads, error, len(error))
        else:
            rc = self.library.dll.jshc_cc_apply_to(self.handle, source.ctypes.data_as(U8),
                target.ctypes.data_as(U8), source.nbytes, BACKENDS[backend], threads, error, len(error))
        stopped = time.perf_counter_ns()
        if rc:
            raise RuntimeError(error.value.decode('utf-8', 'replace'))
        return (stopped - started) * 1e-9, stopped


class DirectInfo(ct.Structure):
    _fields_ = [(name, ct.c_uint32) for name in ('version', 'enabled', 'format', 'reserved')]
    _fields_ += [(name, ct.c_uint64) for name in ('entries', 'table_capacity_bytes')]
    _fields_ += [(name, ct.c_int32) for name in ('dg_min', 'db_min')]


class CacheInfo(ct.Structure):
    _fields_ = [(name, ct.c_uint32) for name in ('version', 'enabled', 'reason', 'reserved')]
    _fields_ += [(name, ct.c_uint64) for name in
        ('entries', 'valid_entries', 'table_capacity_bytes', 'temporary_capacity_bytes')]
    _fields_ += [('prepare_seconds', ct.c_double)]
    _fields_ += [(name, ct.c_int32) for name in ('r_min', 'r_max', 'dg_min', 'dg_max', 'db_min', 'db_max')]


class U16Info(ct.Structure):
    _fields_ = [(name, ct.c_uint32) for name in
        ('version', 'enabled', 'format', 'reason', 'palette_size', 'id_bytes', 'guard_bytes', 'reserved')]
    _fields_ += [(name, ct.c_uint64) for name in ('input_entries', 'raw_words', 'table_capacity_bytes',
        'palette_capacity_bytes', 'temporary_peak_bytes', 'guaranteed_alignment', 'data_mod_64')]
    _fields_ += [('prepare_seconds', ct.c_double)]


def diagnostic(chain, symbol, structure):
    function = getattr(chain.library.dll, symbol)
    function.argtypes = [ct.c_void_p, ct.POINTER(structure), ct.c_size_t]
    function.restype = ct.c_int
    value = structure()
    if function(chain.handle, ct.byref(value), ct.sizeof(value)) or value.version != 1:
        raise ValueError('诊断ABI不符：' + symbol)
    return {name: getattr(value, name) for name, _ in value._fields_}


def diagnostics(chain):
    return {'model_capacity_bytes': chain.model_bytes,
        'direct': diagnostic(chain, 'jshc_cc_get_direct_info', DirectInfo),
        'suffix_cache': diagnostic(chain, 'jshc_cc_get_cache_info', CacheInfo),
        'direct_u16': diagnostic(chain, 'p16_cc_get_direct_u16_info', U16Info)}


def script_records(*paths):
    return {str(Path(path).resolve()): digest(path) for path in paths}
