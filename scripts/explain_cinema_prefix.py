"""复算冻结颜色流的误差分解与条件矩松弛，不重新映射或拟合模型。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numpy as np
from lutlab import error_analysis as ea, io, study_provenance
from lutlab.compatibility import write_json
from run_chain_error_study import colours, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有归因')
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    run, training = read(args.run/'run.json'), read(args.run/'training.json')
    plan = run['identity']['plan']
    inputs = {name: args.run/name for name in ('envelope-arrivals.npy', 'envelope-reference.npy', 'cube-arrival-frequency.npy')}
    for name, path in inputs.items():
        if digest(path) != training['artifact_sha256'][name]:
            raise ValueError('冻结归因数组SHA不同')
    baseline_path = ROOT/plan['baseline_evidence']['cube']['path']
    table_path = ROOT/plan['tables'][3]['path']
    if digest(baseline_path) != plan['baseline_evidence']['cube']['sha256'] or digest(table_path) != plan['tables'][3]['sha256']:
        raise ValueError('旧颜色流或第四原表SHA不同')
    arrivals = np.load(inputs['envelope-arrivals.npy'], mmap_mode='r')
    truth = np.load(inputs['envelope-reference.npy'], mmap_mode='r')
    frequency = np.load(inputs['cube-arrival-frequency.npy'], mmap_mode='r')
    baseline = np.memmap(baseline_path, np.uint8, 'r', shape=arrivals.shape)
    table = io.load_full(table_path, mmap=True)
    own = table[arrivals[:, 0], arrivals[:, 1], arrivals[:, 2]]
    local = baseline.astype(np.int32)-own.astype(np.int32)
    propagated = own.astype(np.int32)-truth.astype(np.int32)
    total = baseline.astype(np.int32)-truth.astype(np.int32)
    identity_mismatches = int(np.count_nonzero(np.any(local+propagated != total, axis=1)))
    sse = lambda a: int(np.sum(a.astype(np.int64)**2, dtype=np.int64))
    moments = {'local': sse(local), 'propagated': sse(propagated),
               'interaction': int(2*np.sum(local.astype(np.int64)*propagated.astype(np.int64), dtype=np.int64)),
               'total': sse(total)}
    if identity_mismatches or moments['local']+moments['propagated']+moments['interaction'] != moments['total']:
        raise AssertionError('全域向量或SSE恒等式不成立')
    metrics = {'local': ea.metrics(baseline, own), 'propagated': ea.metrics(own, truth),
               'total': ea.metrics(baseline, truth)}
    occupied = np.flatnonzero(frequency)
    count = frequency[occupied].astype(np.int64)
    keys = arrivals.astype(np.int64)@np.array([65536, 256, 1], np.int64)
    inverse = np.searchsorted(occupied, keys)
    if not np.array_equal(np.bincount(inverse, minlength=len(occupied)), count):
        raise ValueError('到达频数与冻结到达流不同')
    sums, squares = [], []
    for channel in range(3):
        value = truth[:, channel].astype(np.int64)
        sums.append(np.bincount(inverse, weights=value, minlength=len(occupied)).astype(np.int64))
        squares.append(np.bincount(inverse, weights=value*value, minlength=len(occupied)).astype(np.int64))
    # 桶矩都是精确整数，先以Python整数构造分子，再转换为浮点商求和。
    numerators = [sum(int(n)*int(squares[c][i])-int(sums[c][i])**2 for c in range(3)) for i, n in enumerate(count)]
    if min(numerators) < 0:
        raise AssertionError('条件方差分子为负')
    lower_sse = math.fsum(value/int(n) for value, n in zip(numerators, count))
    key = (2 << 16) | (2 << 8) | 1
    ids = np.flatnonzero(keys == key)
    first = int(ids[0])
    second = int(ids[np.flatnonzero(np.any(truth[ids] != truth[first], axis=1))[0]])
    bucket = int(np.searchsorted(occupied, key))
    witness = {'original_rgb': colours(np.array([first, second], np.int64)).tolist(),
        'shared_arrival': arrivals[first].tolist(), 'references': truth[[first, second]].tolist(),
        'old_output': baseline[[first, second]].tolist(), 'bucket_count': len(ids),
        'conditional_mean': [int(s[bucket])/len(ids) for s in sums]}
    result = {'parent_run_identity': run['identity_sha256'], 'source_sha256': digest(Path(__file__)),
        'environment': study_provenance.environment_fingerprint(),
        'input_sha256': {name: digest(path) for name, path in inputs.items()},
        'baseline_cube_sha256': digest(baseline_path), 'table4_sha256': digest(table_path),
        'rows': len(arrivals), 'identity_mismatches': identity_mismatches, 'metrics': metrics,
        'sse': moments, 'mean_interaction': moments['interaction']/len(arrivals),
        'fixed_prefix': {'distinct_arrivals': len(occupied), 'largest_bucket': int(count.max()),
            'buckets_with_nonconstant_reference': sum(n > 0 for n in numerators),
            'unrestricted_continuous_minimum_sse': lower_sse,
            'unrestricted_continuous_rms_lower_bound': math.sqrt(lower_sse/len(arrivals)),
            'scope': '固定前三稀疏级、允许任意连续末级函数的SSE松弛；浮点汇总精确整数桶矩，不是合法SLUT拟合，也不是mean/p99下界'},
        'collision_witness': witness,
        'scope': '读取既有全域流与原表，未调用模型映射、拟合或原生程序，不产生新精度终验或性能结论'}
    write_json(args.output, result)
    print(json.dumps({'sse': moments, 'fixed_prefix': result['fixed_prefix'], 'collision': witness}, ensure_ascii=False))


if __name__ == '__main__':
    main()
