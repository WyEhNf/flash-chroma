"""有限小域穷举原acc，独立验证最小节点L1目标及固定角舍入。"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from ortools.sat.python import cp_model
from prepare_cinema_first_cpsat import contract_cases
from cinema_first_safe_cpsat_model import build_safe_model, validate_safe_problem


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖最小L1有限合同')
    records = []
    for case in contract_cases():
        problem = case['problem']; n = problem['n_node_variables']
        problem.update(schema='cinema_first_safe_cpsat_problem_v1',
            objective={'kind': 'minimize_node_delta_l1', 'node_variables': n},
            objective_absolute_upper_bound=sum(max(abs(v['lower']), abs(v['upper'])) for v in problem['variables'][:n]))
        feasible = []
        for assignment in itertools.product(*[range(v['lower'], v['upper']+1) for v in problem['variables'][:n]]):
            outputs = list(assignment)+[0]*(len(problem['variables'])-n); valid = True
            for point in problem['points']:
                delta = []
                for c in range(3):
                    acc = point['original_acc'][c]+sum(weight*assignment[index] for index, weight in point['node_terms'][c])
                    z = (acc+32768)//65536-point['original_rgb'][c]; delta.append(z); outputs[point['z_indices'][c]] = z
                if delta not in point['allowed_deltas']: valid = False; break
            if valid: feasible.append((sum(abs(v) for v in assignment), tuple(outputs)))
        model, variables, absolutes = build_safe_model(problem)
        path = args.output.with_name(args.output.stem+'-'+case['name']+'.pb')
        if path.exists() or not model.export_to_file(str(path)): raise ValueError('不覆盖或未能导出有限模型')
        solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1; solver.parameters.max_time_in_seconds = 10.
        status = solver.solve(model)
        if feasible:
            if status != cp_model.OPTIMAL: raise AssertionError('有限L1合同未求得最优')
            expected = min(v[0] for v in feasible); actual = tuple(int(solver.value(v)) for v in variables)
            objective = sum(int(solver.value(v)) for v in absolutes)
            if (objective, actual) not in feasible or objective != expected: raise AssertionError('最小L1不等于独立整数穷举')
            if [int(solver.value(v)) for v in absolutes] != [abs(v) for v in actual[:n]]: raise AssertionError('abs等式不成立')
        else:
            if status != cp_model.INFEASIBLE: raise AssertionError('有限无解域未正确拒绝')
            expected = objective = None
        records.append({'name': case['name'], 'status': solver.status_name(status), 'complete_feasible_assignments': len(feasible),
            'brute_minimum_l1': expected, 'cp_l1': objective, 'integer_brute_equal': True, 'model_proto_sha256': sha(path)})
    root = Path(__file__).resolve().parents[1]
    sources = ['scripts/check_cinema_first_safe_cpsat.py', 'scripts/cinema_first_safe_cpsat_model.py',
        'scripts/cinema_first_cpsat_model.py', 'scripts/prepare_cinema_first_cpsat.py']
    result = {'pass': True, 'cases': records, 'source_sha256': {name: sha(root/name) for name in sources},
        'scope': '只运行五组有限小域最小L1合同，不执行2224危险点真实求解。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pass': True, 'cases': len(records)}), flush=True)


if __name__ == '__main__': main()
