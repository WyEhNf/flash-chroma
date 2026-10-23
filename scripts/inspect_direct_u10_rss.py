"""288/289各三模型的六个fresh进程RSS；不读照片/oracle，不调用apply。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'experiments/channel-runtime')]
import psutil
from channel_native import Library


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def memory():
    return dict(psutil.Process().memory_info()._asdict())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--role', choices=['288', '289'])
    p.add_argument('--model', choices=['max_first', 'p99_first', 'old_best'])
    p.add_argument('--driver-sha256')
    args = p.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖RSS观察')
    frozen_path = ROOT / 'artifacts/p16-direct-u10-quality-frozen-v1/frozen.json'
    quality_path = ROOT / 'artifacts/p16-direct-u10-quality-v1/results.json'
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    quality = json.loads(quality_path.read_text(encoding='utf-8'))
    if not quality['passed'] or quality['library_sha256'] != frozen['library_sha256'] or quality['frozen_sha256'] != sha(frozen_path):
        raise ValueError('必须绑定已成功完整质量')
    libraries = {'288': (frozen['frozen_288_library'], frozen['frozen_288_sha256']),
                 '289': (frozen['library'], frozen['library_sha256'])}
    if args.role is None:
        args.output.mkdir(parents=True)
        driver_sha = sha(Path(__file__))
        save(args.output / 'run.json', {'driver_sha256': driver_sha, 'quality_sha256': sha(quality_path),
            'frozen_sha256': sha(frozen_path), 'libraries': libraries,
            'roles': ['288', '289'], 'models': ['max_first', 'p99_first', 'old_best'],
            'fresh_processes': 6, 'performance_calls': 0, 'apply_calls': 0,
            'scope': __doc__, 'environment': {'python': sys.version, 'psutil': psutil.__version__}})
        for role in ('288', '289'):
            for model in ('max_first', 'p99_first', 'old_best'):
                subprocess.run([sys.executable, str(Path(__file__)), '--output',
                    str(args.output / (role + '-' + model + '.json')), '--role', role, '--model', model,
                    '--driver-sha256', driver_sha], check=True, cwd=ROOT)
        return
    if not args.model or args.driver_sha256 != sha(Path(__file__)):
        raise ValueError('子进程参数或驱动身份不同')
    spec = frozen['models'][args.model]
    for name, expected in spec['input_sha256'].items():
        if sha(name) != expected:
            raise ValueError('模型改变')
    path, expected = libraries[args.role]
    dirs = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(Path(path).parent))]
    library = Library(path, expected)
    before = memory()
    start = time.perf_counter()
    chain = library.chain(spec['models'], spec['sidecars'])
    construct = time.perf_counter() - start
    after = memory()
    capacity = chain.model_bytes

    class Info(ct.Structure):
        _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'format', 'reason', 'palette_size', 'id_bytes', 'guard_bytes', 'reserved')]
        _fields_ += [(n, ct.c_uint64) for n in ('input_entries', 'raw_words', 'table_capacity_bytes', 'palette_capacity_bytes', 'temporary_peak_bytes', 'guaranteed_alignment', 'data_mod_64')]
        _fields_ += [('prepare_seconds', ct.c_double)]

    name = 'p16_cc_get_direct_u10_info' if args.role == '289' else 'p16_cc_get_direct_u16_info'
    fn = getattr(library.dll, name)
    fn.argtypes = [ct.c_void_p, ct.POINTER(Info), ct.c_size_t]
    fn.restype = ct.c_int
    value = Info()
    if ct.sizeof(value) != 96 or fn(chain.handle, ct.byref(value), 96):
        raise AssertionError('只读诊断失败')
    diagnostic = {n: getattr(value, n) for n, _ in Info._fields_}
    chain.close()
    closed = memory()
    result = {'model': args.model, 'revision': library.revision, 'library_sha256': library.sha256,
        'driver_sha256': args.driver_sha256, 'frozen_sha256': sha(frozen_path), 'quality_sha256': sha(quality_path),
        'before': before, 'after_construct': after, 'after_destroy': closed,
        'rss_delta_after_construct': after['rss'] - before['rss'],
        'OS_peak_wset_before': before.get('peak_wset'), 'OS_peak_wset_after_construct': after.get('peak_wset'),
        'model_bytes': capacity, 'wide': diagnostic, 'diagnostic_construction_seconds': construct,
        'performance_calls': 0, 'apply_calls': 0,
        'environment': {'platform': sys.platform, 'machine': os.environ.get('PROCESSOR_IDENTIFIER'),
                        'python': sys.version, 'psutil': psutil.__version__},
        'scope': '每角色/模型一个fresh进程；仅导入Python/NumPy/psutil和本角色DLL，模型SHA流式读取；不加载照片/oracle或另一个DLL。构造秒数仅资源诊断，不是排他性能。OS峰值含模块/allocator/OpenMP，不能当精确table或系统最小RAM。'}
    save(args.output, result)
    print(json.dumps({'role': args.role, 'model': args.model, 'model_bytes': capacity,
        'rss_delta': result['rss_delta_after_construct'], 'peak_wset': result['OS_peak_wset_after_construct']}), flush=True)


if __name__ == '__main__':
    main()
