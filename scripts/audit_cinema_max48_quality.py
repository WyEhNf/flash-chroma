"""离线独立复算三分母质量指标、逐图分档/阈值及24配置身份，不重跑像素。"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import itertools
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def metrics(hist):
    values = [int(v) for v in hist]; n = sum(values); cumulative = list(itertools.accumulate(values))
    rank, remainder = divmod(99*(n-1), 100); lo = bisect.bisect_right(cumulative, rank)
    hi = bisect.bisect_right(cumulative, rank+int(remainder != 0)); k = (n+99)//100; left = k; terms = []
    for q in range(len(values)-1, -1, -1):
        take = min(left, values[q]); terms.append(take*math.sqrt(q)); left -= take
        if not left: break
    maximum = max(q for q, v in enumerate(values) if v)
    return {'n': n, 'mean': math.fsum(v*math.sqrt(q) for q, v in enumerate(values))/n,
        'rms': math.sqrt(sum(q*v for q, v in enumerate(values))/n),
        'p99': math.sqrt(lo)+remainder/100*(math.sqrt(hi)-math.sqrt(lo)),
        'max_squared': maximum, 'max': math.sqrt(maximum), 'cvar_1pct': math.fsum(terms)/k}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖独立三分母审计')
    folder = ROOT/'artifacts/cinema-max48-pareto-quality-v1'; result = read(folder/'results.json'); identity = read(folder/'identity.json')
    frozen_path = ROOT/'artifacts/cinema-max48-pareto-quality-frozen-v1.json'; frozen = read(frozen_path)
    assert identity['frozen_sha256'] == sha(frozen_path) and frozen['ast_pass']
    assert identity['source_sha256'] == frozen['source_sha256']
    for name, expected in frozen['source_sha256'].items(): assert sha(ROOT/name) == expected, name
    for name, expected in frozen['input_sha256'].items(): assert sha(name) == expected, name
    import numpy as np
    with np.load(folder/'histograms.npz') as data: histograms = {name: data[name] for name in data.files}
    roles = ('a399', 'best', 'max_first', 'candidate'); names = ('mean', 'rms', 'p99', 'max', 'cvar_1pct')
    for scope, group in (('cube', result['cube']), ('photos', result['photos']), ('training60', result['training60']),
            ('standalone_first', result['standalone_first_vs_original_table1'])):
        for role in roles:
            actual = metrics(histograms[scope+'_'+role])
            for name, value in actual.items(): assert abs(value-group[role][name]) <= 1e-12, (scope, role, name)
    expected_cube = {'a399': '3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22',
        'best': '373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed',
        'max_first': '143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e', 'candidate': sha(folder/'candidate.rgb')}
    assert result['candidate_oracle_sha256'] == expected_cube['candidate']
    assert result['reference_payload_sha256'] == '493c9084a90186a15ec42cd4553e02ee6b915f9ee4511d77cb2b40adcb82f0a9'
    for role, hashes in result['native_full_stream_sha256'].items():
        assert len(hashes) == 6 and set(hashes.values()) == {expected_cube[role]}
    assert result['full_native_configs'] == 24 and result['full_and_photo_native_mismatches'] == 0
    comparison_rows = 0
    for base in ('a399', 'best', 'max_first'):
        for scope in ('cube', 'photos', 'training60'):
            before = result[scope][base]; after = result[scope]['candidate']; item = result['pairs'][base][scope]; ratios = []
            for name in names:
                a, b = before[name], after[name]; ratio = 100. if b == 0 else min(100., a/b*100) if a else 0.
                assert abs(item['metrics'][name]['retained_percent']-ratio) <= 1e-12; ratios.append(ratio)
            assert abs(item['minimum_retained_percent']-min(ratios)) <= 1e-12
        old = result['photos'][base]['per_image']; new = result['photos']['candidate']['per_image']; comparisons = result['pairs'][base]['per_image']
        assert len(old) == len(new) == len(comparisons) == 100
        totals = {name: {'好': 0, '平': 0, '差': 0} for name in names}; worst = 100.
        for a, b, item in zip(old, new, comparisons):
            assert a['image'] == b['image'] == item['image']; ratios = []
            for name in names:
                label = '平' if abs(a[name]-b[name]) <= 1e-12 else '好' if b[name] < a[name] else '差'; totals[name][label] += 1
                ratio = 100. if b[name] == 0 else min(100., a[name]/b[name]*100) if a[name] else 0.
                assert item['metrics'][name]['change'] == label and abs(item['metrics'][name]['retained_percent']-ratio) <= 1e-12; ratios.append(ratio)
            minimum = min(ratios); worst = min(worst, minimum)
            assert abs(item['minimum_retained_percent']-minimum) <= 1e-12
            assert item['tiers_pass'] == {str(t): minimum+1e-12 >= t for t in (100, 90, 80, 70, 60, 50)}
            comparison_rows += 1
        assert totals == result['pairs'][base]['per_metric_changes'] and abs(worst-result['pairs'][base]['worst_image_retained_percent']) <= 1e-12
    for role in roles:
        rows = result['photos'][role]['per_image']; assert len({row['image'] for row in rows}) == 100
        for threshold in (4, 5, 6, 7, 7.5, 7.7, 8, 8.2):
            assert result['nonofficial_strict_max_T_counts'][role][str(threshold)] == sum(row['max'] < threshold for row in rows)
    old_failure = read(ROOT/'artifacts/cinema-first-safe-cpsat-accept-v2/summary.json')
    assert len(old_failure['failures']) == 6 and not old_failure['eligible_for_independent_final_checks']
    assert result['old_minl1_failed_metrics'] == old_failure['failures'] and not result['overall_upgrade']
    passed = all(result['cube']['candidate']['mean'] <= result['cube'][role]['mean']+1e-12 and
        result['photos']['candidate']['mean'] <= result['photos'][role]['mean']+1e-12 for role in ('a399', 'best'))
    assert result['mean_qualified_against_common_baselines'] == passed
    value = {'pass': True, 'source_sha256': sha(__file__), 'results_sha256': sha(folder/'results.json'),
        'source_files_checked': len(frozen['source_sha256']), 'input_files_checked': len(frozen['input_sha256']),
        'histogram_metrics_groups': 16, 'native_configs_checked': 24, 'per_image_comparisons_checked': comparison_rows,
        'mean_qualified': passed, 'old_six_budget_failure_preserved': True, 'overall_upgrade': False,
        'scope': '只读复算16组整数直方图、300逐图比较/六档/T及完整流/源身份；没有重跑原生像素或补跑选择。'}
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print({'pass': True, 'histogram_groups': 16, 'comparisons': comparison_rows}, flush=True)


if __name__ == '__main__': main()
