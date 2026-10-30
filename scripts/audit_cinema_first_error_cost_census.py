"""离线核成本普查规模、原固定域、成本池和超门判定，不重扫RGB状态。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import integer_error_cost as cost
from run_channel_tail_nodes import digest, save


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖成本普查离线审计')
    stage = ROOT/'artifacts/cinema-first-error-cost-census-v1'
    run = json.loads((stage/'run.json').read_text(encoding='utf-8')); summary = json.loads((stage/'summary.json').read_text(encoding='utf-8'))
    frozen = json.loads((ROOT/'artifacts/cinema-first-cost-census-frozen-v1.json').read_text(encoding='utf-8'))
    contract = json.loads((ROOT/'artifacts/cinema-first-error-cost-contract-v1.json').read_text(encoding='utf-8'))
    assert frozen['ast_pass'] and contract['pass'] and frozen['source_sha256'] == contract['source_sha256']
    for name, expected in run['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('实际执行源已变：'+name)
    for name, expected in frozen['source_sha256'].items(): assert digest(ROOT/name) == expected
    with np.load(stage/'census.npz') as data: census = {k: data[k] for k in data.files}
    with np.load(ROOT/'artifacts/cinema-first-risk-v1/screen.npz') as data: screen = {k: data[k] for k in data.files}
    keys, origin, retained, counts, distinct, training = [census[k] for k in
        ('keys', 'original_squared', 'retained', 'safe_table_rows', 'distinct_safe_squared', 'training_counts')]
    np.testing.assert_array_equal(keys, screen['keys']); np.testing.assert_array_equal(counts, screen['safe_count'])
    gold = np.load(run['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(run['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(16777216, 3))
    delta = baseline[keys].astype(np.int64)-gold[keys].astype(np.int64)
    np.testing.assert_array_equal(origin, np.sum(delta*delta, axis=1))
    expected_retained = (screen['maximum_squared'] > 49)|(screen['minimum_squared'] != origin)|(screen['maximum_squared'] != origin)
    np.testing.assert_array_equal(retained, expected_retained)
    multiple = retained & (distinct > 1)
    points, rows, selectors, q_variables = int(retained.sum()), int(counts[retained].sum()), int(distinct[multiple].sum()), int(multiple.sum())
    assert (points, rows, selectors, q_variables) == (summary['retained_points'], summary['safe_table_rows'], summary['cost_selectors'], summary['q_variables'])
    assert summary['predicted_variables_without_abs'] == 258+3*points+q_variables+selectors
    assert summary['predicted_rounding_rows'] == 3*points
    gate = points <= 16384 and rows <= 500000 and selectors <= 131072
    assert gate == summary['within_frozen_resource_gate'] and not gate
    assert summary['complete_aabb_states'] == int(screen['query_count'].sum()) == 1187079
    pool = census['cost_pool']; qt_u = summary['uniform_tail']['threshold_squared']; qt_t = summary['training_tail']['threshold_squared']
    for a in range(50):
        for b in range(51):
            expected = (cost.sqrt_difference_squared(a, b), a-b, int(a > qt_u)-int(b > qt_u), int(a > qt_t)-int(b > qt_t),
                cost.excess_difference(a, b, qt_u, method=cost.sqrt_difference_squared),
                cost.excess_difference(a, b, qt_t, method=cost.sqrt_difference_squared))
            assert tuple(int(v) for v in pool[a, b]) == expected
    inside = [0]*51; inside_train = [0]*51
    for q, weight in zip(origin, training): inside[int(q)] += 1; inside_train[int(q)] += int(weight)
    assert [int(v) for v in census['baseline_hist']-census['outside_hist']] == inside
    assert [int(v) for v in census['baseline_training_hist']-census['outside_training_hist']] == inside_train
    assert max(i for i, v in enumerate(census['outside_hist']) if v) == 48
    for value in summary['coefficient_int64_audit'].values():
        assert value['pass'] and value['total_abs_bound'] == abs(value['constant_cost'])+value['selector_coefficient_abs_sum']
        assert 0 <= value['maximum_coefficient_abs'] <= (1 << 62)-1 and 0 <= value['total_abs_bound'] <= (1 << 62)-1
    assert not run['cp_model_built'] and not summary['cp_model_built'] and not run['cp_solver_called'] and not summary['cp_solver_called']
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'summary_sha256': digest(stage/'summary.json'),
        'census_sha256': digest(stage/'census.npz'), 'retained_points_checked': points, 'safe_rows_checked': rows,
        'selectors_checked': selectors, 'cost_pool_entries_checked': 50*51, 'resource_gate_pass': gate,
        'scope': '只读核风险min/max/安全计数导出的保留规则、原误差与外直方图、第二整数法成本池及超门判定；未再次枚举RGB状态或建CP。distinct q计数复用唯一完整普查数组。'})
    print({'pass': True, 'resource_gate_pass': gate, 'points': points, 'rows': rows}, flush=True)


if __name__ == '__main__': main()
