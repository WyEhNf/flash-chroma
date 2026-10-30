"""离线独立核真实预算编码、两个端点与失败保留，不调用任何CP solver。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_hotspot_support as hs, integer_error_cost as cost
from run_channel_tail_nodes import digest, load_model, save
from cinema_first_direct_budget_model import BUDGETS, validate_direct_problem


def independent_coefficients(q, q0, mass, qt_u, qt_t):
    mean, rms = cost.sqrt_difference_squared(q, q0), q-q0
    cvar_u = cost.excess_difference(q, q0, qt_u, method=cost.sqrt_difference_squared)
    cvar_t = cost.excess_difference(q, q0, qt_t, method=cost.sqrt_difference_squared)
    return [mean, mass*mean, rms, mass*rms, int(q > qt_u)-int(q0 > qt_u),
        mass*(int(q > qt_t)-int(q0 > qt_t)), cvar_u, mass*cvar_t]


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖直接预算独立审计')
    base = ROOT/'artifacts'; read = lambda name: json.loads((base/name).read_text(encoding='utf-8'))
    problem = read('cinema-first-direct-budget-problem-v2.json'); validate_direct_problem(problem)
    preflight = read('cinema-first-direct-budget-preflight-v2.json'); solution = read('cinema-first-direct-budget-solution-v2.json')
    problem_sha = digest(base/'cinema-first-direct-budget-problem-v2.json')
    if not preflight['pass'] or preflight['solver_called'] or preflight['problem_sha256'] != problem_sha:
        raise ValueError('不是冻结问题的无搜索预检')
    if solution['problem_sha256'] != problem_sha or solution['preflight_sha256'] != digest(base/'cinema-first-direct-budget-preflight-v2.json'):
        raise ValueError('不是唯一冻结问题的实际结果')
    if solution['status'] != 'INFEASIBLE' or solution['feasible'] or solution['variables'] is not None:
        raise ValueError('本审计只封存实际窄域INFEASIBLE，不改状态')
    pbs = [base/'cinema-first-direct-budget-preflight-v2.pb', base/'cinema-first-direct-budget-solution-v2-model.pb']
    if any(digest(path) != preflight['model_proto_sha256'] for path in pbs) or solution['model_proto_sha256'] != preflight['model_proto_sha256']:
        raise ValueError('实际PB不同于预检PB')
    for name, expected in {**problem['source_sha256'], **problem['frozen_evidence_sha256']}.items():
        if digest(ROOT/name) != expected: raise ValueError('实际源或冻结证据已变：'+name)
    for spec in [*problem['inputs'].values(), problem['witness']]:
        if digest(spec['path']) != spec['sha256']: raise ValueError('固定模型或数据已变')
    if (len(problem['variables']), len(problem['rows']), len(problem['points'])) != (63090, 31005, 10335):
        raise ValueError('模型规模不同于唯一窄域')
    stage = base/'cinema-first-narrow-cost-census-v1'
    with np.load(stage/'census.npz') as data: census = {k: data[k] for k in data.files}
    positions = np.flatnonzero(census['retained']); keys = census['keys'][positions]
    model = load_model(problem['inputs']['first']['path']); witness = load_model(problem['witness']['path'])
    count = problem['n_node_variables']; mapping = {}
    endpoint_delta = []
    for i, variable in enumerate(problem['variables'][:count]):
        node, c = variable['physical_node'], variable['channel']; mapping[node, c] = i
        assert [variable['lower'], variable['upper']] == [int(census['lower_delta'][node, c]), int(census['upper_delta'][node, c])]
        endpoint_delta.append(int(witness.nodes.reshape(-1, 3)[node, c])-int(model.nodes.reshape(-1, 3)[node, c]))
    if len(mapping) != 95: raise AssertionError('活动节点分量不是95个')
    corner_nodes, weights = hs.corners(model, hs.rgb(keys))
    acc = np.sum(weights.astype(np.uint64)*model.nodes.reshape(-1, 3)[corner_nodes].astype(np.uint64), axis=1, dtype=np.uint64)
    suffix_path = base/'cinema-first-hotspot-v1/suffix.npy'
    if digest(suffix_path) != problem['suffix_sha256']: raise ValueError('完整固定后缀已变')
    suffix = np.load(suffix_path, mmap_mode='r'); gold = np.load(problem['inputs']['reference']['path'], mmap_mode='r')
    coefficient_cache = {}; safe_rows = 0; witness_costs = [0]*8; zero_costs = [0]*8
    zero_unsafe, witness_unsafe = 0, 0
    for j, point in enumerate(problem['points']):
        position = int(positions[j]); assert point['source_key'] == int(keys[j]) and point['support_position'] == position
        assert point['original_acc'] == [int(v) for v in acc[j]]
        assert point['original_squared'] == int(census['original_squared'][position])
        assert point['training_count'] == int(census['training_counts'][position])
        expected_terms = []
        for c in range(3):
            terms = [[mapping[int(node), c], int(w)] for node, w in zip(corner_nodes[j], weights[j, :, c])
                if w and (int(node), c) in mapping]
            expected_terms.append(sorted(terms))
        if [sorted(terms) for terms in point['node_terms']] != expected_terms: raise AssertionError('四角JSON不同于独立八角正权')
        rows = np.array(point['allowed_error_rows'], np.int64); rgb = rows[:, :3]+np.array(point['original_rgb'], np.int64)
        if np.any(rgb < census['lower_rgb'][position]) or np.any(rgb > census['upper_rgb'][position]):
            raise AssertionError('安全状态超出已认证窄域端点')
        error = suffix[hs.key(rgb.astype(np.uint8))].astype(np.int64)-gold[keys[j]].astype(np.int64)
        actual_squared = np.sum(error*error, axis=1)
        np.testing.assert_array_equal(actual_squared, rows[:, 3])
        if len(rows) != int(census['safe_table_rows'][position]) or len(set(actual_squared)) != int(census['distinct_safe_squared'][position]):
            raise AssertionError('安全表的完整状态数或q数不等于唯一普查')
        safe_rows += len(rows)
        q0, mass, qt_u, qt_t = point['original_squared'], point['training_count'], point['uniform_threshold_squared'], point['training_threshold_squared']
        for q in point['error_options']:
            signature = (q, q0, mass, qt_u, qt_t)
            if signature not in coefficient_cache: coefficient_cache[signature] = independent_coefficients(*signature)
            if point['coefficients'][str(q)] != coefficient_cache[signature]: raise AssertionError('点成本不同于独立符号平方算法')
        for delta, costs, label in (([0]*count, zero_costs, 'zero'), (endpoint_delta, witness_costs, 'witness')):
            output = [(int(acc[j, c])+sum(w*delta[i] for i, w in expected_terms[c])+32768)//65536 for c in range(3)]
            z = [output[c]-point['original_rgb'][c] for c in range(3)]
            value = suffix[(output[0]<<16)|(output[1]<<8)|output[2]]
            q = sum((int(value[c])-int(gold[keys[j], c]))**2 for c in range(3))
            present = [*z, q] in point['allowed_error_rows']
            if label == 'zero':
                if not present: zero_unsafe += 1
                assert q == q0
            else:
                if not present: witness_unsafe += 1
                if not present or q > 49: raise AssertionError('已知max48见证未通过无预算的真实完整表')
            contribution = independent_coefficients(q, q0, mass, qt_u, qt_t)
            for b, v in enumerate(contribution): costs[b] += v
    assert safe_rows == 51926 and zero_costs == [0]*8 and zero_unsafe == 116 and witness_unsafe == 0
    assert all(witness_costs[b] > problem['budget_limits'][b] for b in (0, 1, 2, 3, 6, 7))
    assert all(witness_costs[b] <= problem['budget_limits'][b] for b in (4, 5))
    old_contract = read('cinema-first-direct-budget-contract-v1.json'); new_contract = read('cinema-first-direct-budget-contract-v2.json')
    assert old_contract['pass'] and new_contract['pass'] and len(old_contract['cases']) == len(new_contract['cases']) == 12
    for a, b in zip(old_contract['cases'], new_contract['cases']):
        assert (a['name'], a['expected_node_assignments'], a['cp_node_assignments']) == (b['name'], b['expected_node_assignments'], b['cp_node_assignments'])
    assert not (base/'cinema-first-direct-budget-problem-v1.json').exists()
    log = base/'cinema-first-direct-budget-preflight-execution-v1.log'
    assert 'relative_to' in log.read_text(encoding='utf-8') and 'ValueError' in log.read_text(encoding='utf-8')
    fixed_bounds = {}
    for label, outside_name, baseline_name in (('uniform', 'outside_hist', 'baseline_hist'),
                                               ('training', 'outside_training_hist', 'baseline_training_hist')):
        outside = census[outside_name]; total = int(census[baseline_name].sum())
        optimistic = outside.copy(); affected = total-int(outside.sum()); optimistic[0] += affected
        metrics = hs.metrics(optimistic); threshold = 9 if label == 'uniform' else 12
        fixed_bounds[label] = {'total_mass': total, 'affected_mass': affected,
            'fixed_max_squared': int(np.flatnonzero(outside)[-1]), 'fixed_count_at_squared48': int(outside[48]),
            'fixed_count_above_next_lower_squared': int(outside[threshold:].sum()),
            'optimistic_p99_lower_bound': metrics['p99'], 'optimistic_max_squared_lower_bound': metrics['max_squared'],
            'scope': '把全部受影响质量乐观置零，仅保留原完整支撑外固定直方图；是任何此分量域候选的误差顺序统计下界，不保证该乐观分配可达。'}
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'problem_sha256': problem_sha,
        'solution_sha256': digest(base/'cinema-first-direct-budget-solution-v2.json'), 'status': solution['status'],
        'rounding_points_eight_corner_checked': len(problem['points']), 'safe_error_rows_checked': safe_rows,
        'cost_signatures_second_method_checked': len(coefficient_cache), 'finite_cases_identical_v1_v2': 12,
        'zero_endpoint_unsafe_points': zero_unsafe, 'zero_endpoint_integer_costs': dict(zip(BUDGETS, zero_costs)),
        'witness_endpoint_unsafe_points': witness_unsafe, 'witness_endpoint_integer_costs': dict(zip(BUDGETS, witness_costs)),
        'fixed_outside_optimistic_bounds': fixed_bounds,
        'v1_metadata_failure_preserved': True, 'new_cp_solver_calls': 0,
        'scope': '只读独立八角核原acc/活动权，逐安全行核真实suffix误差、成本第二整数法、V1/V2有限全集同一性；两个端点说明安全与预算各自不等于联合可行。仅记录该窄域保守编码solver无解，无独立形式证明或全局无解结论。'})
    print({'pass': True, 'points': len(problem['points']), 'safe_rows': safe_rows, 'status': solution['status']}, flush=True)


if __name__ == '__main__': main()
