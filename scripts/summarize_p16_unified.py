"""从绑定的质量和全部七轮批次原件复算统一运行时汇总，不运行native或重新采样。"""
import argparse
import json
from pathlib import Path
import statistics

from p16_unified_support import digest, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', type=Path, required=True)
    parser.add_argument('--correctness', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('汇总保留已存在的原件')
    bench = json.loads(args.benchmark.read_text(encoding='utf-8'))
    quality = json.loads(args.correctness.read_text(encoding='utf-8'))
    assert bench['completed'] and quality['passed']
    assert bench['library']['sha256'] == quality['library']['sha256']
    assert bench['source_sha256'] == quality['source_sha256']
    expected = {row['model']: row['expected_photos']['batch_sha256'] for row in quality['models']}
    values = {}
    for row in bench['records']:
        if not row['executed']:
            continue
        raw = row['batch_total_seconds_raw']
        assert len(raw) == 7 and all(v > 0 for v in raw)
        assert statistics.median(raw) == row['batch_total_seconds_median']
        assert min(raw) == row['batch_total_seconds_min']
        assert max(raw) == row['batch_total_seconds_max']
        assert len(set(row['per_round_output_sha256'])) == 1
        assert row['per_round_output_sha256'][0] == expected[row['model']]
        values[row['model'], row['threads'], row['backend']] = row
    comparisons = []
    for model, threads, backend in sorted(values):
        if backend != 'avx2' or (model, threads, 'avx512') not in values:
            continue
        a, b = values[model, threads, 'avx2'], values[model, threads, 'avx512']
        assert a['state']['model_capacity_bytes'] == b['state']['model_capacity_bytes']
        comparisons.append({'model': model, 'threads': threads,
            'avx2_batch_median_ms': a['batch_total_seconds_median'] * 1000,
            'avx512_batch_median_ms': b['batch_total_seconds_median'] * 1000,
            'avx512_median_throughput_vs_avx2': a['batch_total_seconds_median'] / b['batch_total_seconds_median'],
            'avx2_create_to_first_batch_ms': a['create_to_first_batch_wall_seconds'] * 1000,
            'avx512_create_to_first_batch_ms': b['create_to_first_batch_wall_seconds'] * 1000,
            'model_capacity_bytes': a['state']['model_capacity_bytes'],
            'source_image_bytes': a['memory']['source_image_bytes'],
            'output_image_bytes': a['memory']['output_image_bytes']})
    result = {'passed': True, 'benchmark': {'path': str(args.benchmark), 'sha256': digest(args.benchmark)},
        'correctness': {'path': str(args.correctness), 'sha256': digest(args.correctness)},
        'library': bench['library'], 'environment': bench['environment'],
        'comparisons': comparisons, 'timed_batches': len(values) * 7,
        'scope': '单场分组计时的描述性中位比较，无A/A或跨机结论；冷wall每格仅一个新句柄，不能称冷启动中位或稀疏拟合全流程。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save(args.output, result)
    print(json.dumps(comparisons, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
