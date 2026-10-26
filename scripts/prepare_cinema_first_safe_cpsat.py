"""从已独立核验的完整危险CSR导出精确整数问题，不执行CP搜索。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
from prepare_cinema_first_cpsat import add_point
from cinema_first_safe_cpsat_model import validate_safe_problem


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--environment-lock', type=Path, required=True); p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖完整危险表问题冻结')
    import numpy as np
    from lutlab import integer_first_box as box
    from run_channel_tail_nodes import save, digest, load_model
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'; risk = ROOT/'artifacts/cinema-first-risk-v1'
    run = json.loads((risk/'run.json').read_text(encoding='utf-8'))
    summary = json.loads((risk/'summary.json').read_text(encoding='utf-8'))
    audit_path = ROOT/'artifacts/cinema-first-risk-independent-v1.json'
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    if not summary['within_predeclared_resource_gate'] or not audit['pass']:
        raise ValueError('危险筛查门槛或独立审计未通过')
    if (summary['possibly_dangerous_rows'], summary['safe_triples_in_dangerous_rows'], summary['outside_support_max_squared']) != (2224, 126765, 48):
        raise ValueError('不是已冻结的唯一危险筛查')
    if audit['summary_sha256'] != digest(risk/'summary.json') or audit['screen_sha256'] != digest(risk/'screen.npz'):
        raise ValueError('独立筛查审计不属于当前原件')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('最小L1有限合同未通过')
    for name, expected in contract['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('最小L1合同源已变：'+name)
    for name, expected in run['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('筛查实际源已变：'+name)
    for spec in run['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原模型/数据已变')
    if digest(prior/'suffix.npy') != run['suffix_sha256'] or digest(prior/'support-index.npz') != run['support_index_sha256']:
        raise ValueError('完整后缀或正支撑已变')
    with np.load(risk/'screen.npz') as data:
        selected = data['selected_nodes']; danger_keys = data['keys'][data['dangerous_rows']]
    with np.load(risk/'danger-allowed.npz') as data:
        keys, offsets, allowed = data['source_keys'], data['offsets'], data['allowed_rgb']
    np.testing.assert_array_equal(keys, danger_keys)
    if len(keys) != 2224 or len(allowed) != 126765 or len(selected) != 86 or len(offsets) != len(keys)+1:
        raise ValueError('冻结CSR尺寸不符')
    if int(offsets[0]) != 0 or int(offsets[-1]) != len(allowed) or np.any(np.diff(offsets) <= 0):
        raise ValueError('危险CSR存在空表或越界')
    model = load_model(run['inputs']['first']['path']); flat = model.nodes.reshape(-1, 3)
    gold = np.load(run['inputs']['reference']['path'], mmap_mode='r')
    mapping = {int(node): i for i, node in enumerate(selected)}
    variables = [{'name': 'd_'+str(int(node))+'_'+str(c), 'physical_node': int(node), 'channel': c,
        'original_value': int(flat[node, c]), 'lower': max(-2, -int(flat[node, c])),
        'upper': min(2, 255-int(flat[node, c]))} for node in selected for c in range(3)]
    problem = {'schema': 'cinema_first_safe_cpsat_problem_v1', 'variables': variables,
        'n_node_variables': len(variables), 'points': [], 'rows': [],
        'objective': {'kind': 'minimize_node_delta_l1', 'node_variables': len(variables)},
        'objective_absolute_upper_bound': sum(max(abs(v['lower']), abs(v['upper'])) for v in variables),
        'solve': {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0}}
    for i, source in enumerate(keys):
        key = int(source); rgb = [key>>16, (key>>8)&255, key&255]
        bounds = box.point_box(model, rgb, selected)
        acc = [int(ch['baseline_acc']) for ch in bounds['channels']]
        terms = [[[3*mapping[node]+c, weight] for node, weight in box.scalar_basis(model, rgb, c) if node in mapping] for c in range(3)]
        candidates = allowed[int(offsets[i]):int(offsets[i+1])].tolist()
        add_point(problem, acc, terms, candidates, {'source_key': key, 'source_rgb': rgb, 'gold_rgb': gold[key].tolist()})
        if len(problem['points'][-1]['allowed_deltas']) != len(candidates):
            raise AssertionError('导出时丢失危险表安全三元组')
    validate_safe_problem(problem)
    source_names = set(run['source_sha256']) | {
        'experiments/p16-cinema-first-safe-cpsat-v1.json', 'scripts/cinema_first_safe_cpsat_model.py',
        'scripts/prepare_cinema_first_safe_cpsat.py', 'scripts/solve_cinema_first_safe_cpsat.py',
        'scripts/preflight_cinema_first_safe_cpsat.py', 'scripts/check_cinema_first_safe_cpsat.py',
        'scripts/verify_cinema_first_safe_cpsat.py', 'scripts/cinema_first_cpsat_model.py', 'scripts/prepare_cinema_first_cpsat.py'}
    frozen = {str(path.relative_to(ROOT)): digest(path) for path in
        (risk/'run.json', risk/'summary.json', risk/'screen.npz', risk/'danger-allowed.npz', audit_path)}
    problem.update(source_sha256={name: digest(ROOT/name) for name in sorted(source_names)},
        frozen_risk_sha256=frozen, inputs=run['inputs'], environment_lock_sha256=digest(args.environment_lock),
        support_index_sha256=run['support_index_sha256'], suffix_sha256=run['suffix_sha256'],
        plan_sha256=digest(ROOT/'experiments/p16-cinema-first-safe-cpsat-v1.json'), contract_sha256=digest(args.contract))
    save(args.output, problem)
    print({'node_variables': 258, 'output_variables': len(keys)*3, 'abs_variables': 258,
        'integer_rows': len(problem['rows']), 'safe_triples': len(allowed), 'cp_solver_called': False}, flush=True)


if __name__ == '__main__': main()
