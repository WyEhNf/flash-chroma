"""原环境生成直接预算有限合同或真实纯整数JSON，不导入ORTools。"""
from __future__ import annotations
import argparse
import copy
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
from lutlab import integer_error_cost as cost
from cinema_first_direct_budget_model import empty_problem, attach_error_cost, finish_problem
from prepare_cinema_first_cpsat import add_point, contract_cases
from run_channel_tail_nodes import digest, save


NEW_SOURCES = ('experiments/p16-cinema-first-direct-budget-cpsat-v1.json',
    'scripts/cinema_first_direct_budget_model.py', 'scripts/prepare_cinema_first_direct_budget.py',
    'scripts/check_cinema_first_direct_budget.py', 'scripts/preflight_cinema_first_direct_budget.py',
    'scripts/solve_cinema_first_direct_budget.py', 'scripts/verify_cinema_first_direct_budget.py',
    'scripts/cinema_first_direct_budget_identity.py')


def coefficients(q, q0, weight, qt_u, qt_t, independent=False):
    method = cost.sqrt_difference_squared if independent else cost.sqrt_difference_interval
    mean = method(q, q0); rms = q-q0
    p99_u, p99_t = int(q > qt_u)-int(q0 > qt_u), int(q > qt_t)-int(q0 > qt_t)
    cvar_u = cost.excess_difference(q, q0, qt_u, method=method)
    cvar_t = cost.excess_difference(q, q0, qt_t, method=method)
    return [mean, weight*mean, rms, weight*rms, p99_u, weight*p99_t, cvar_u, weight*cvar_t]


def add_budget_point(problem, acc, terms, rows, q0, training, qt_u, qt_t, metadata=None):
    safe = [row for row in rows if row[3] <= 49]
    if not safe: raise ValueError('直接预算点没有安全输出')
    add_point(problem, acc, terms, [row[:3] for row in safe], metadata)
    point = problem['points'][-1]
    point.update(original_squared=q0, training_count=training, uniform_threshold_squared=qt_u, training_threshold_squared=qt_t)
    matrix = {q: coefficients(q, q0, training, qt_u, qt_t) for q in {row[3] for row in safe}}
    attach_error_cost(problem, point, safe, matrix)


def expected_assignments(problem):
    n = problem['n_node_variables']; accepted = []
    for assignment in itertools.product(*[range(v['lower'], v['upper']+1) for v in problem['variables'][:n]]):
        totals = [0]*8; valid = True
        for point in problem['points']:
            z = [(point['original_acc'][c]+sum(w*assignment[i] for i, w in point['node_terms'][c])+32768)//65536-point['original_rgb'][c] for c in range(3)]
            truth = {tuple(row[:3]): row[3] for row in point['finite_truth_by_delta']}
            if tuple(z) not in truth or z not in point['allowed_deltas'] or truth[tuple(z)] > 49:
                valid = False; break
            q = truth[tuple(z)]
            values = coefficients(q, point['original_squared'], point['training_count'],
                point['uniform_threshold_squared'], point['training_threshold_squared'], independent=True)
            totals = [a+b for a, b in zip(totals, values)]
        if valid and all(a <= b for a, b in zip(totals, problem['budget_limits'])): accepted.append(list(assignment))
    return sorted(accepted)


def finite_cases():
    cases = []
    for old in contract_cases():
        before = old['problem']; n = before['n_node_variables']; problem = empty_problem(copy.deepcopy(before['variables'][:n]), [0]*8)
        for j, point in enumerate(before['points']):
            origin = point['original_rgb']; rows = []; truth = []
            for z in itertools.product(*[range(before['variables'][i]['lower'], before['variables'][i]['upper']+1) for i in point['z_indices']]):
                q = 3+2*z[0]+z[1]+z[2]
                if q < 0: raise ValueError('有限误差平方公式越界')
                truth.append([*z, q])
                if list(z) in point['allowed_deltas']: rows.append([*[origin[c]+z[c] for c in range(3)], q])
            add_budget_point(problem, point['original_acc'], point['node_terms'], rows, 3, j % 2,
                3, 3, {'finite_truth_by_delta': truth})
        finish_problem(problem); cases.append({'name': old['name'], 'problem': problem})
    custom = [
        ('forced_nonzero_constant_q', [{-1: 49, 0: 50, 1: 49}], [1], 49, 49, [0]*8),
        ('shared_nonzero_budget_feasible', [{-1: 49, 0: 50, 1: 48}, {-1: 1, 0: 0, 1: 0}], [1, 0], 9, 12, [0]*8),
        ('shared_mean_budget_infeasible', [{-1: 49, 0: 50, 1: 50}, {-1: 1, 0: 0, 1: 0}], [1, 0], 9, 12, [0]*8),
        ('zero_training_still_protect_uniform', [{-1: 48, 0: 50, 1: 50}, {-1: 49, 0: 0, 1: 0}], [1, 0], 9, 12, [0]*8),
        ('p99_original_rank_slack', [{-1: 48, 0: 50, 1: 50}, {-1: 9, 0: 8, 1: 8}, {-1: 25, 0: 36, 1: 36}], [1, 1, 1], 8, 8, [0, 0, 0, 0, 1, 1, 0, 0]),
        ('p99_zero_slack_blocks', [{-1: 48, 0: 50, 1: 50}, {-1: 9, 0: 8, 1: 8}, {-1: 25, 0: 36, 1: 36}], [1, 1, 1], 8, 8, [0]*8),
        ('ceil_refund_conservative', [{-1: 2, 0: 1, 1: 4}, {-1: 1, 0: 2, 1: 4}], [1, 1], 1, 1, [0]*8),
    ]
    for name, maps, masses, qt_u, qt_t, limits in custom:
        problem = empty_problem([{'name': 'shared_d', 'physical_node': 0, 'channel': 0,
            'original_value': 127, 'lower': -1, 'upper': 1}], limits)
        for mapping, mass in zip(maps, masses):
            origin = [10, 100, 100]; acc = [v*65536 for v in origin]
            rows = [[origin[0]+z, origin[1], origin[2], q] for z, q in sorted(mapping.items())]
            truth = [[z, 0, 0, q] for z, q in sorted(mapping.items())]
            add_budget_point(problem, acc, [[[0, 65536]], [], []], rows, mapping[0], mass, qt_u, qt_t,
                {'finite_truth_by_delta': truth})
        finish_problem(problem); cases.append({'name': name, 'problem': problem})
    for case in cases: case['expected_node_assignments'] = expected_assignments(case['problem'])
    by_name = {case['name']: case for case in cases}
    assert by_name['forced_nonzero_constant_q']['expected_node_assignments'] == [[-1], [1]]
    assert by_name['shared_nonzero_budget_feasible']['expected_node_assignments'] == [[1]]
    assert not by_name['shared_mean_budget_infeasible']['expected_node_assignments']
    assert not by_name['zero_training_still_protect_uniform']['expected_node_assignments']
    assert by_name['p99_original_rank_slack']['expected_node_assignments'] == [[-1]]
    assert not by_name['p99_zero_slack_blocks']['expected_node_assignments']
    assert by_name['ceil_refund_conservative']['expected_node_assignments'] == [[0]]
    assert cost.sqrt_difference_squared(2, 1)+cost.sqrt_difference_squared(1, 2) == 1
    return cases


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('mode', choices=('contract', 'problem'))
    p.add_argument('--contract', type=Path); p.add_argument('--environment-lock', type=Path)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖直接预算问题或有限合同')
    names = set(NEW_SOURCES) | {'scripts/cinema_first_cpsat_model.py', 'scripts/prepare_cinema_first_cpsat.py', 'python/lutlab/integer_error_cost.py'}
    if args.mode == 'contract':
        save(args.output, {'cases': finite_cases(), 'source_sha256': {name: digest(ROOT/name) for name in sorted(names)},
            'scope': '原环境独立整数节点穷举与第二根差法生成完整预期节点可行集，不运行真实CP。'})
        return
    if args.contract is None or args.environment_lock is None: raise ValueError('真实问题需要已执行有限合同及隔离环境锁')
    import numpy as np
    from lutlab import channel_hotspot_support as hs
    from run_channel_tail_nodes import load_model
    stage = ROOT/'artifacts/cinema-first-narrow-cost-census-v1'; run = json.loads((stage/'run.json').read_text(encoding='utf-8'))
    summary = json.loads((stage/'summary.json').read_text(encoding='utf-8'))
    audit_path = ROOT/'artifacts/cinema-first-narrow-cost-independent-v1.json'; audit = json.loads(audit_path.read_text(encoding='utf-8'))
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass'] or not audit['pass'] or not audit['resource_gate_pass'] or not summary['within_frozen_resource_gate']:
        raise ValueError('窄域资源门、独立审计或有限合同未过')
    if audit['summary_sha256'] != digest(stage/'summary.json') or audit['census_sha256'] != digest(stage/'census.npz'):
        raise ValueError('窄域审计不是固定统计原件')
    for table in (run['source_sha256'], contract['source_sha256']):
        for name, h in table.items():
            if digest(ROOT/name) != h: raise ValueError('窄域或直接预算实际源已变：'+name)
    for spec in [*run['inputs'].values(), run['witness']]:
        if digest(spec['path']) != spec['sha256']: raise ValueError('窄域输入已变')
    with np.load(stage/'census.npz') as data: arrays = {name: data[name] for name in data.files}
    if (int(arrays['retained'].sum()), int(arrays['safe_table_rows'][arrays['retained']].sum())) != (10335, 51926):
        raise ValueError('不是唯一完整成本普查')
    model = load_model(run['inputs']['first']['path']); flat = model.nodes.reshape(-1, 3)
    selected = np.argwhere(arrays['active_components']); mapping = {(int(n), int(c)): i for i, (n, c) in enumerate(selected)}
    nodes = [{'name': 'd_'+str(int(n))+'_'+str(int(c)), 'physical_node': int(n), 'channel': int(c),
        'original_value': int(flat[n, c]), 'lower': int(arrays['lower_delta'][n, c]),
        'upper': int(arrays['upper_delta'][n, c])} for n, c in selected]
    qt_u, qt_t = summary['uniform_tail']['threshold_squared'], summary['training_tail']['threshold_squared']
    limits = [0]*8
    limits[4] = summary['uniform_tail']['above_count_cap']-summary['uniform_tail']['baseline_above_count']
    limits[5] = summary['training_tail']['above_count_cap']-summary['training_tail']['baseline_above_count']
    problem = empty_problem(nodes, limits)
    positions = np.flatnonzero(arrays['retained']); keys = arrays['keys'][positions]; points = hs.rgb(keys)
    indices, weights, acc = hs.basis(model, points)
    gold = np.load(run['inputs']['reference']['path'], mmap_mode='r')
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'; suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    for j, position in enumerate(positions):
        terms = []
        for c in range(3):
            terms.append([[mapping[(int(n), c)], int(w)] for n, w in zip(indices[c, j], weights[c, j])
                if int(w) and (int(n), c) in mapping])
        rows = []; low, high = arrays['lower_rgb'][position], arrays['upper_rgb'][position]
        for rgb in itertools.product(*[range(int(a), int(b)+1) for a, b in zip(low, high)]):
            key = (rgb[0]<<16)|(rgb[1]<<8)|rgb[2]; out = suffix[key]
            q = sum((int(out[c])-int(gold[keys[j], c]))**2 for c in range(3))
            if q <= 49: rows.append([*rgb, q])
        if len(rows) != int(arrays['safe_table_rows'][position]): raise ValueError('安全表尺寸不同于唯一普查')
        add_budget_point(problem, [int(v) for v in acc[j]], terms, rows, int(arrays['original_squared'][position]),
            int(arrays['training_counts'][position]), qt_u, qt_t, {'source_key': int(keys[j]), 'support_position': int(position)})
    finish_problem(problem)
    if len(problem['variables']) != 63090 or len(problem['rows']) != 31005:
        raise ValueError('真实模型规模不同于唯一普查')
    for row in problem['budget_rows']:
        expected = summary['coefficient_int64_audit'][row['name']]
        if row['constant'] != expected['constant_cost'] or sum(abs(c) for _, c in row['terms']) != expected['selector_coefficient_abs_sum']:
            raise ValueError('真实预算行不同于完整成本普查')
    names |= set(run['source_sha256'])
    frozen = {str(path.relative_to(ROOT)): digest(path) for path in
        (stage/'run.json', stage/'summary.json', stage/'census.npz', audit_path, args.contract)}
    problem.update(source_sha256={name: digest(ROOT/name) for name in sorted(names)}, frozen_evidence_sha256=frozen,
        inputs=run['inputs'], witness=run['witness'], environment_lock_sha256=digest(args.environment_lock),
        support_index_sha256=digest(prior/'support-index.npz'), suffix_sha256=digest(prior/'suffix.npy'),
        baseline_uniform=summary['uniform_before'], baseline_training=summary['training_before'],
        original_resource_gate={'retained_points_max': 16384, 'safe_table_rows_max': 500000, 'selectors_max': 131072})
    save(args.output, problem)
    print({'variables': len(problem['variables']), 'points': len(problem['points']), 'rounding_rows': len(problem['rows']),
        'safe_table_rows': sum(len(v['allowed_error_rows']) for v in problem['points']), 'cp_solver_called': False}, flush=True)


if __name__ == '__main__': main()
