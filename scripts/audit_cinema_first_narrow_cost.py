"""只读核窄域、完整支撑统计、成本池和三项资源门，不重建CP或重扫RGB。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import integer_error_cost as cost
from run_channel_tail_nodes import digest, load_model, save


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--stage', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖窄域成本独立审计')
    stage = args.stage
    run = json.loads((stage/'run.json').read_text(encoding='utf-8'))
    summary = json.loads((stage/'summary.json').read_text(encoding='utf-8'))
    for name, expected in run['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('窄域实际执行源已变：'+name)
    for spec in [*run['inputs'].values(), run['witness']]:
        if digest(spec['path']) != spec['sha256']: raise ValueError('原模型、见证或输入已变')
    with np.load(stage/'census.npz') as data: values = {k: data[k] for k in data.files}
    original = load_model(run['inputs']['first']['path']); witness = load_model(run['witness']['path'])
    delta = witness.nodes.reshape(-1, 3).astype(np.int64)-original.nodes.reshape(-1, 3).astype(np.int64)
    np.testing.assert_array_equal(values['lower_delta'], np.minimum(delta, 0))
    np.testing.assert_array_equal(values['upper_delta'], np.maximum(delta, 0))
    np.testing.assert_array_equal(values['active_components'], delta != 0)
    assert np.max(np.abs(delta)) <= 2
    active_count = int(np.count_nonzero(delta))
    keys, origin, retained, training = [values[k] for k in ('keys', 'original_squared', 'retained', 'training_counts')]
    assert len(keys) == summary['complete_support_rows'] and len(keys) > 0 and np.all(keys[1:] > keys[:-1])
    profile = summary['support_profile']
    assert profile['active_components'] == active_count and profile['support_rows'] == len(keys)
    assert profile['full_domain_independent_rows'] == 16777216 and profile['support_mismatches'] == 0
    assert not profile['construction_uses_old70571_filter']
    lower, upper = values['lower_rgb'].astype(np.int64), values['upper_rgb'].astype(np.int64)
    assert np.all(lower <= upper) and np.all(upper-lower <= 2)
    states = np.prod(upper-lower+1, axis=1, dtype=np.int64)
    assert int(states.sum()) == summary['complete_aabb_states']
    minimum, maximum = values['minimum_squared'], values['maximum_squared']
    np.testing.assert_array_equal(retained, (maximum > 49)|(minimum != origin)|(maximum != origin))
    counts, distinct = values['safe_table_rows'], values['distinct_safe_squared']
    assert np.all(counts > 0) and np.all(counts <= states) and np.all(distinct > 0) and np.all(distinct <= counts)
    assert np.all(minimum <= maximum) and np.all(minimum <= 48)
    multiple = retained & (distinct > 1)
    points, rows, selectors, q_variables = int(retained.sum()), int(counts[retained].sum()), int(distinct[multiple].sum()), int(multiple.sum())
    assert (points, rows, selectors, q_variables) == (summary['retained_points'], summary['safe_table_rows'], summary['cost_selectors'], summary['q_variables'])
    assert summary['predicted_variables_without_abs'] == active_count+3*points+q_variables+selectors
    assert summary['predicted_rounding_rows'] == 3*points
    gate = points <= 16384 and rows <= 500000 and selectors <= 131072
    assert gate == summary['within_frozen_resource_gate']
    gold = np.load(run['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(run['inputs']['cube']['path'], np.uint8, 'r', shape=(16777216, 3))
    difference = baseline[keys].astype(np.int64)-gold[keys].astype(np.int64)
    np.testing.assert_array_equal(origin, np.sum(difference*difference, axis=1))
    pool = values['cost_pool']; qt_u = summary['uniform_tail']['threshold_squared']; qt_t = summary['training_tail']['threshold_squared']
    for q in range(50):
        for q0 in range(51):
            expected = (cost.sqrt_difference_squared(q, q0), q-q0, int(q > qt_u)-int(q0 > qt_u), int(q > qt_t)-int(q0 > qt_t),
                cost.excess_difference(q, q0, qt_u, method=cost.sqrt_difference_squared),
                cost.excess_difference(q, q0, qt_t, method=cost.sqrt_difference_squared))
            assert tuple(int(v) for v in pool[q, q0]) == expected
    inside, inside_train = [0]*51, [0]*51
    for q, weight in zip(origin, training): inside[int(q)] += 1; inside_train[int(q)] += int(weight)
    assert [int(v) for v in values['baseline_hist']-values['outside_hist']] == inside
    assert [int(v) for v in values['baseline_training_hist']-values['outside_training_hist']] == inside_train
    assert int(values['baseline_hist'].sum()) == 16777216 and int(values['baseline_training_hist'].sum()) == 47185920
    assert max(i for i, v in enumerate(values['outside_hist']) if v) <= 49
    assert summary['witness_support_max_squared'] <= 48
    for value in summary['coefficient_int64_audit'].values():
        assert value['pass'] and value['total_abs_bound'] == abs(value['constant_cost'])+value['selector_coefficient_abs_sum']
        assert 0 <= value['maximum_coefficient_abs'] <= (1 << 62)-1 and 0 <= value['total_abs_bound'] <= (1 << 62)-1
    assert not run['cp_model_built'] and not summary['cp_model_built'] and not run['cp_solver_called'] and not summary['cp_solver_called']
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'summary_sha256': digest(stage/'summary.json'),
        'census_sha256': digest(stage/'census.npz'), 'active_components_checked': active_count, 'retained_points_checked': points,
        'safe_rows_checked': rows, 'selectors_checked': selectors, 'cost_pool_entries_checked': 2550, 'resource_gate_pass': gate,
        'scope': '独立由两固定模型重构分量域，核唯一完整普查的几何完成标记、原误差、外直方图、第二整数法成本池及资源判定；安全状态数与distinct q复用唯一普查数组，未重新枚举状态或建CP。'})
    print({'pass': True, 'resource_gate_pass': gate, 'points': points, 'rows': rows}, flush=True)


if __name__ == '__main__': main()
