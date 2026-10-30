"""只读检查固定64字节块的精确去重潜力，不执行性能计时。"""
import argparse
import collections
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
from skylake_server_support import ROOT, read, save, checked, digest
from verify_skylake_linux_stdlib import bind, create


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不得覆盖分析')
    os.sched_setaffinity(0, [0, 2, 4, 6])
    os.environ.update(OMP_NUM_THREADS='4', OMP_DYNAMIC='FALSE')
    plan_path = ROOT / 'experiments/skylake-id-batch4-v1.json'
    build_path = ROOT / 'artifacts/skylake-id-batch4-linux-build-v1/build.json'
    plan, build = read(plan_path), read(build_path)
    models = [checked(plan['fixed_inputs']['base']), *[checked(x) for x in plan['suffix_models']]]
    sides = [checked(plan['fixed_inputs']['sidecar']), None, None, None]
    d = bind(checked(build['libraries']['candidate']))
    h = create(d, models, sides)
    try:
        words = (ct.c_uint32 * (2**22))()
        f = d.jshc_cc_copy_direct
        f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
        f.restype = ct.c_int
        assert f(h, words, len(words)) == 0
        raw = bytes(words)
    finally:
        d.jshc_cc_destroy(h)
    unique = {}
    counts = collections.Counter()
    indices = []
    for offset in range(0, len(raw), 64):
        block = raw[offset:offset+64]
        if block not in unique:
            unique[block] = len(unique)
        number = unique[block]
        indices.append(number)
        counts[number] += 1
    pool_bytes = len(unique) * 64
    map_entry_bytes = 2 if len(unique) <= 65536 else 4
    map_bytes = len(indices) * map_entry_bytes
    assert all(raw[offset:offset+64] in unique for offset in range(0, len(raw), 64))
    result = {'purpose': __doc__, 'table_sha256': hashlib.sha256(raw).hexdigest(),
        'plan_sha256': digest(plan_path), 'build_sha256': digest(build_path),
        'library': build['libraries']['candidate'], 'script_sha256': digest(Path(__file__)),
        'block_bytes': 64, 'input_bytes': len(raw), 'block_count': len(indices),
        'unique_blocks': len(unique), 'pool_bytes': pool_bytes, 'map_entry_bytes': map_entry_bytes,
        'map_bytes': map_bytes, 'total_bytes': pool_bytes+map_bytes,
        'capacity_ratio': (pool_bytes+map_bytes)/len(raw),
        'most_common_block_uses': counts.most_common(8),
        'limitation': '精确集合分析，增加一级依赖读取；容量收益不能推断周期或吞吐。'}
    args.output.mkdir(parents=True)
    save(args.output/'analysis.json', result)
    (args.output/'analyze.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
