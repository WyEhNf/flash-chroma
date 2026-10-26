"""独立进程验证同libgomp的逐TID固定/恢复与冻结模型输出；无性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'experiments/channel-runtime')]
import numpy as np
import psutil
from channel_native import Library


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class Record(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'omp_tid', 'team_size', 'os_tid', 'cpu_before', 'cpu_after',
        'group_before', 'group_after', 'query_before_ok', 'set_attempted', 'set_error', 'query_after_ok')]
    _fields_ += [(n, ct.c_uint64) for n in ('mask_before', 'previous_mask', 'mask_after')]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--cache-root', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖绑定控制质量')
    if ct.sizeof(Record) != 72:
        raise ValueError('诊断结构ABI不同')
    source = ROOT / 'experiments/p16-omp-affinity-control-v1'
    module = Path('E:/mingw64/bin/libgomp-1.dll')
    module_sha = 'fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88'
    if sha(module) != module_sha:
        raise ValueError('实际libgomp与静态审查身份不同')
    libs = {'87': (Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll'),
                   '58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158'),
            '94': (Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-shared-prepare-build-v1/libjshc_shared_prepare.dll'),
                   '3d51f78e2f2ab50777243dc9e83d59d4add94521dde222548265c69fd275c834')}
    first = args.cache_root / 'artifacts/cinema-current-anchor-accept-v1'
    suffix = args.cache_root / 'artifacts/cinema-envelope-v1/stage4_sweep004'
    models = [first / 'candidate-base.slut', *[suffix / ('selected-stage' + str(s) + '.slut') for s in (2, 3, 4)]]
    sides = [first / 'channel-frac.bin', None, None, None]
    oracle = first / 'cube.rgb'
    if sha(oracle) != '3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':
        raise ValueError('已验oracle不同')
    frozen = {'source_sha256': {str(path): sha(path) for path in [source / 'control.cpp', source / 'plan.md', Path(__file__),
        ROOT / 'experiments/channel-runtime/channel_native.py']},
        'helper': str(args.library.resolve()), 'helper_sha256': sha(args.library),
        'models_sha256': {str(path): sha(path) for path in [*models, sides[0]]},
        'oracle': str(oracle), 'oracle_sha256': sha(oracle),
        'target_libraries': {name: {'path': str(path), 'sha256': expected} for name, (path, expected) in libs.items()},
        'libgomp': str(module), 'libgomp_sha256': module_sha,
        'quality_scope': '独立进程0x55，4线程pool先snapshot/pin，87/94构造及4线程apply各两轮后核同TID/mask，最后restore；不计时。'}
    for path, expected in libs.values():
        if sha(path) != expected:
            raise ValueError('冻结原运行时不同')
    args.output.mkdir(parents=True)
    save(args.output / 'frozen.json', frozen)
    psutil.Process().cpu_affinity([0, 2, 4, 6])
    dirs = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(args.library.resolve().parent))]
    helper = ct.CDLL(str(args.library.resolve()))
    fn = helper.p16_omp_affinity
    fn.argtypes = [ct.POINTER(Record), ct.c_size_t, ct.c_size_t, ct.c_uint32, ct.POINTER(Record)]
    fn.restype = ct.c_int
    rows = []

    def call(action, saved=None):
        values = (Record * 4)()
        code = fn(values, 4, 72, action, saved)
        row = {'action': action, 'return_code': code,
               'team': [{n: getattr(v, n) for n, _ in Record._fields_} for v in values]}
        rows.append(row)
        save(args.output / 'partial.json', rows)
        if code:
            raise AssertionError('线程控制API失败：' + str(code))
        assert all(r['version'] == 1 and r['team_size'] == 4 and r['omp_tid'] == t for t, r in enumerate(row['team']))
        assert len({r['os_tid'] for r in row['team']}) == 4
        return values

    original = call(0)
    pinned = call(1)
    expected_tids = [v.os_tid for v in pinned]
    assert expected_tids == [v.os_tid for v in original]

    def check_pinned():
        state = call(0)
        assert [v.os_tid for v in state] == expected_tids
        assert all(v.mask_before == v.mask_after == (1 << (2 * t)) and v.cpu_after == 2 * t for t, v in enumerate(state))

    reference = np.memmap(oracle, np.uint8, 'r', shape=(1 << 24, 3))
    keys = (np.arange(65537, dtype=np.uint32) * 257) & 0xffffff
    rgb = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
    expected = reference[keys]
    outputs = []
    for name, (path, library_sha) in libs.items():
        lib = Library(path, library_sha)
        assert lib.revision == int(name)
        for repeat in range(2):
            with lib.chain(models, sides) as chain:
                check_pinned()
                actual = chain.apply(rgb.copy(), kernel='avx2', threads=4)
                np.testing.assert_array_equal(actual, expected)
                outputs.append({'revision': lib.revision, 'repeat': repeat,
                    'output_sha256': hashlib.sha256(actual.tobytes()).hexdigest(), 'mismatches': 0})
                check_pinned()
    modules = {str(Path(m.path).resolve()) for m in psutil.Process().memory_maps() if Path(m.path).name.lower() == 'libgomp-1.dll'}
    assert len(modules) == 1 and next(iter(modules)).lower() == str(module.resolve()).lower()
    assert sha(next(iter(modules))) == module_sha
    restored = call(2, pinned)
    assert [v.os_tid for v in restored] == expected_tids
    assert all(v.mask_after == pinned[t].previous_mask for t, v in enumerate(restored))
    final = call(0)
    assert [v.os_tid for v in final] == expected_tids
    assert all(v.mask_after == original[t].mask_before for t, v in enumerate(final))
    rejected = 0
    poisoned = (Record * 4)()
    ct.memset(ct.byref(poisoned), 0xa7, ct.sizeof(poisoned))
    before = bytes(poisoned)
    for output, count, stride, action, saved in [(None, 4, 72, 0, None), (poisoned, 3, 72, 0, None),
        (poisoned, 4, 71, 0, None), (poisoned, 4, 73, 0, None), (poisoned, 4, 72, 3, None), (poisoned, 4, 72, 2, None)]:
        assert fn(output, count, stride, action, saved) == 1 and bytes(poisoned) == before
        rejected += 1
    assert sha(args.library) == frozen['helper_sha256'] and sha(module) == module_sha
    for path, expected_sha in frozen['source_sha256'].items():
        assert sha(path) == expected_sha
    for path, expected_sha in frozen['models_sha256'].items():
        assert sha(path) == expected_sha
    save(args.output / 'results.json', {'passed': True, 'records': rows, 'outputs': outputs,
        'rejections': rejected, 'actual_libgomp_paths': sorted(modules), 'libgomp_sha256': module_sha,
        'frozen_sha256': sha(args.output / 'frozen.json'), 'performance_calls': 0,
        'scope': '只证该Windows进程/4线程pool的固定与恢复及原输出；非旧漂移原因、非速度收益，不恢复旧资格。'})
    print(json.dumps({'passed': True, 'team_snapshots': len(rows), 'target_outputs': len(outputs), 'rejections': rejected,
        'one_libgomp': True, 'restored': True, 'performance_calls': 0}))


if __name__ == '__main__':
    main()
