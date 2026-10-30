"""原环境生成精确Q16节点耦合JSON；不导入ORTools，不执行热点求解。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
from cinema_first_cpsat_model import reduce_row, validate_problem
Q, HALF = 65536, 32768


def add_point(problem, acc, terms, allowed_rgb, metadata=None):
    original = [(v+HALF)//Q for v in acc]; indices = []
    for c in range(3):
        low, high = acc[c], acc[c]
        for index, weight in terms[c]:
            variable = problem['variables'][index]
            low += weight*variable['lower']; high += weight*variable['upper']
        lo, hi = (low+HALF)//Q-original[c], (high+HALF)//Q-original[c]
        index = len(problem['variables']); indices.append(index)
        problem['variables'].append({'name': 'z_'+str(len(problem['points']))+'_'+str(c), 'lower': lo, 'upper': hi})
    allowed = []
    for candidate in allowed_rgb:
        delta = [int(candidate[c])-original[c] for c in range(3)]
        if all(problem['variables'][indices[c]]['lower'] <= delta[c] <= problem['variables'][indices[c]]['upper'] for c in range(3)):
            allowed.append(delta)
    for c in range(3):
        lower = original[c]*Q-HALF-acc[c]; upper = (original[c]+1)*Q-HALF-1-acc[c]
        problem['rows'].append(reduce_row([*terms[c], [indices[c], -Q]], lower, upper, problem['variables']))
    problem['points'].append({'original_acc': acc, 'original_rgb': original, 'node_terms': terms, 'z_indices': indices,
                              'allowed_deltas': sorted(allowed), **(metadata or {})})


def contract_cases():
    cases = []
    for name, weights, value in [('half_exact', [32768, 32768, 0, 0], 1),
                                  ('half_below', [32767, 32769, 0, 0], 1),
                                  ('half_above', [32769, 32767, 0, 0], 1)]:
        problem = {'variables': [{'name': 'd0', 'lower': -1, 'upper': 1}], 'n_node_variables': 1, 'rows': [], 'points': []}
        acc = [weights[0]*value, 127*Q, 127*Q]; origin = (acc[0]+HALF)//Q
        add_point(problem, acc, [[[0, weights[0]]], [], []], [[origin+d, 127, 127] for d in (-1, 0, 1)])
        cases.append({'name': name, 'problem': problem})
    for incompatible in (False, True):
        problem = {'variables': [{'name': 'zero_node', 'lower': 0, 'upper': 2}, {'name': 'white_node', 'lower': -2, 'upper': 0}],
                   'n_node_variables': 2, 'rows': [], 'points': []}
        w = [16384, 16384, 16384, 16384]; acc = [sum(a*b for a, b in zip(w, (0, 255, 17, 19))), 127*Q, 127*Q]
        origin = (acc[0]+HALF)//Q
        add_point(problem, acc, [[[0, w[0]], [1, w[1]]], [], []], [[origin+d, 127, 127] for d in ((-1,) if incompatible else (-1, 0))])
        second_w = w if incompatible else [32768, 8192, 8192, 16384]
        second_acc = [sum(a*b for a, b in zip(second_w, (0, 255, 17, 19))), 127*Q, 127*Q]
        second_origin = (second_acc[0]+HALF)//Q
        add_point(problem, second_acc, [[[0, second_w[0]], [1, second_w[1]]], [], []],
                  [[second_origin+d, 127, 127] for d in ((0,) if incompatible else (0, 1))])
        cases.append({'name': 'shared_infeasible' if incompatible else 'shared_clipped_fixed_corners', 'problem': problem})
    return cases


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('mode', choices=('contract', 'problem'))
    p.add_argument('--environment-lock', type=Path); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖精确JSON冻结')
    from run_channel_tail_nodes import save, digest, load_model
    if args.mode == 'contract':
        cases = contract_cases()
        for case in cases: validate_problem(case['problem'])
        save(args.output, {'schema': 'cinema_first_cpsat_contract_v1', 'cases': cases,
             'sources': {name: digest(ROOT/name) for name in ('scripts/prepare_cinema_first_cpsat.py', 'scripts/cinema_first_cpsat_model.py',
                 'scripts/check_cinema_first_cpsat_solver.py', 'scripts/solve_cinema_first_cpsat.py')}})
        return
    if args.environment_lock is None: raise ValueError('实际问题须有隔离环境锁')
    import numpy as np
    from lutlab import integer_first_box as box
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    old = json.loads((prior/'run.json').read_text(encoding='utf-8')); summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    for spec in old['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原max_first字节已变')
    if digest(prior/'suffix.npy') != summary['suffix_sha256']: raise ValueError('原后缀字节已变')
    model = load_model(old['inputs']['first']['path']); gold = np.load(old['inputs']['reference']['path'], mmap_mode='r')
    suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    with np.load(prior/'support-index.npz') as data: selected, hotspots = data['selected_nodes'], data['hotspot_keys']
    mapping = {int(node): i for i, node in enumerate(selected)}; flat = model.nodes.reshape(-1, 3)
    variables = [{'name': 'd_'+str(int(node))+'_'+str(c), 'physical_node': int(node), 'channel': c, 'original_value': int(flat[node, c]),
                  'lower': max(-2, -int(flat[node, c])), 'upper': min(2, 255-int(flat[node, c]))} for node in selected for c in range(3)]
    problem = {'schema': 'cinema_first_cpsat_problem_v1', 'variables': variables, 'n_node_variables': len(variables), 'rows': [], 'points': [],
               'solve': {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0}}
    for source in hotspots:
        key = int(source); rgb = [key>>16, (key>>8)&255, key&255]; bounds = box.point_box(model, rgb, selected)
        acc = [int(ch['baseline_acc']) for ch in bounds['channels']]
        terms = [[[3*mapping[node]+c, weight] for node, weight in box.scalar_basis(model, rgb, c) if node in mapping] for c in range(3)]
        allowed = []
        for r, g, b in itertools.product(*[range(lo, hi+1) for lo, hi in zip(bounds['lower_rgb'], bounds['upper_rgb'])]):
            final = suffix[(r<<16)|(g<<8)|b]
            error = [int(final[c])-int(gold[key, c]) for c in range(3)]
            if sum(v*v for v in error) <= 49: allowed.append([r, g, b])
        add_point(problem, acc, terms, allowed, {'source_key': key, 'source_rgb': rgb, 'gold_rgb': gold[key].tolist()})
    validate_problem(problem)
    source_names = {'scripts/prepare_cinema_first_cpsat.py', 'scripts/cinema_first_cpsat_model.py', 'scripts/solve_cinema_first_cpsat.py',
                    'scripts/check_cinema_first_cpsat_solver.py', 'scripts/verify_cinema_first_cpsat.py',
                    'experiments/p16-cinema-first-cpsat-v1.json', 'python/lutlab/integer_first_box.py'} | set(old['sources_sha256'])
    problem.update(source_sha256={name: digest(ROOT/name) for name in sorted(source_names)}, inputs=old['inputs'],
                   environment_lock_sha256=digest(args.environment_lock), support_index_sha256=digest(prior/'support-index.npz'),
                   suffix_sha256=summary['suffix_sha256'], plan_sha256=digest(ROOT/'experiments/p16-cinema-first-cpsat-v1.json'))
    save(args.output, problem)
    print({'node_variables': len(selected)*3, 'output_variables': len(hotspots)*3, 'integer_rows': len(problem['rows']),
           'allowed_triples': sum(len(p['allowed_deltas']) for p in problem['points'])}, flush=True)


if __name__ == '__main__': main()
