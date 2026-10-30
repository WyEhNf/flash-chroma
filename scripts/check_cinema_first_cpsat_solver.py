"""隔离CP-SAT对有限小域完整枚举，与纯Python原acc舍入穷举集合一致。"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from ortools.sat.python import cp_model
from cinema_first_cpsat_model import build_model, reduce_row, SAFE


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖CP整数穷举合同')
    value = json.loads(args.input.read_text(encoding='utf-8')); records = []
    root = Path(__file__).resolve().parents[1]
    for name, expected_sha in value['sources'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected_sha:
            raise ValueError('有限合同输入的实际源已变：'+name)
    for case in value['cases']:
        problem = case['problem']; model, variables = build_model(problem)
        model_path = args.output.with_name(args.output.stem+'-'+case['name']+'.pb')
        if model_path.exists() or not model.export_to_file(str(model_path)): raise ValueError('不覆盖或未能导出有限CP模型')
        class Capture(cp_model.CpSolverSolutionCallback):
            def __init__(self): super().__init__(); self.rows = []
            def on_solution_callback(self): self.rows.append(tuple(int(self.value(v)) for v in variables))
        callback = Capture(); solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1
        solver.parameters.enumerate_all_solutions = True; solver.parameters.max_time_in_seconds = 10.
        status = solver.solve(model, callback); actual = set(callback.rows)
        expected = set(); n = problem['n_node_variables']
        for assignment in itertools.product(*[range(v['lower'], v['upper']+1) for v in problem['variables'][:n]]):
            output = list(assignment)+[0]*(len(variables)-n); valid = True
            for point in problem['points']:
                delta = []
                for c in range(3):
                    acc = point['original_acc'][c]+sum(weight*assignment[index] for index, weight in point['node_terms'][c])
                    z = (acc+32768)//65536-point['original_rgb'][c]; delta.append(z); output[point['z_indices'][c]] = z
                if delta not in point['allowed_deltas']: valid = False; break
            if valid: expected.add(tuple(output))
        if actual != expected: raise AssertionError('CP完整可行集合不等于原始整数舍入穷举：'+case['name'])
        if status not in (cp_model.OPTIMAL, cp_model.INFEASIBLE): raise AssertionError('有限穷举没有完成')
        records.append({'name': case['name'], 'status': solver.status_name(status), 'solutions': len(actual), 'complete_set_equal': True})
    rejected = 0
    for terms, domains in (([[0, SAFE]], [{'lower': -2, 'upper': 2}]), ([[0, SAFE+1]], [{'lower': 0, 'upper': 1}])):
        try: reduce_row(terms, -1, 1, domains)
        except OverflowError: rejected += 1
        else: raise AssertionError('溢出行未拒绝')
    result = {'pass': True, 'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(), 'cases': records, 'overflow_rows_rejected': rejected,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': '有限小节点域精确可行集合合同；未执行实际116点20sec热点求解'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pass': True, 'cases': len(records), 'overflow_rejects': rejected}), flush=True)


if __name__ == '__main__': main()
