"""隔离环境枚举有限CP全部解，核原环境独立整数穷举的完整节点投影。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from ortools.sat.python import cp_model
from cinema_first_direct_budget_model import build_direct_model


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__(); self.variables = variables; self.assignments = set()
    def on_solution_callback(self):
        self.assignments.add(tuple(int(self.value(v)) for v in self.variables))
        if len(self.assignments) > 1000: raise AssertionError('有限合同越界')


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖直接预算有限合同结果')
    data = json.loads(args.input.read_text(encoding='utf-8')); root = Path(__file__).resolve().parents[1]
    for name, h in data['source_sha256'].items():
        if sha(root/name) != h: raise ValueError('直接预算有限合同源已变：'+name)
    records = []
    for item in data['cases']:
        problem = item['problem']; model, variables = build_direct_model(problem)
        solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = 20261024; solver.parameters.max_time_in_seconds = 5.
        solver.parameters.enumerate_all_solutions = True; collector = Collect(variables[:problem['n_node_variables']])
        status = solver.solve(model, collector)
        actual = sorted([list(v) for v in collector.assignments]); expected = item['expected_node_assignments']
        if actual != expected: raise AssertionError('CP完整节点可行集不同于原环境独立穷举：'+item['name'])
        if expected and status != cp_model.OPTIMAL: raise AssertionError('有限合同未完整枚举全部解')
        if not expected and status != cp_model.INFEASIBLE: raise AssertionError('有限无解合同未正确停止')
        records.append({'name': item['name'], 'status': solver.status_name(status), 'expected_node_assignments': expected,
            'cp_node_assignments': actual, 'complete_equal': True, 'variables': len(variables)})
    result = {'pass': True, 'input_sha256': sha(args.input), 'source_sha256': data['source_sha256'], 'cases': records,
        'scope': '仅有限小域逐项全集合同，包含强制非零可行/预算无解/p99原余量/保守退款；未构建或求解真实10335点模型。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print({'pass': True, 'cases': len(records)}, flush=True)


if __name__ == '__main__': main()
