"""隔离环境仅执行一次20秒直接八预算可行性搜索，保留无incumbent状态。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
from cinema_first_direct_budget_model import build_direct_model
from cinema_first_direct_budget_identity import sha, verify_identity, process_memory


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--environment-lock', type=Path, required=True); p.add_argument('--preflight', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖唯一真实直接预算求解')
    from ortools.sat.python import cp_model
    value = json.loads(args.problem.read_text(encoding='utf-8')); verify_identity(value, args.environment_lock)
    preflight = json.loads(args.preflight.read_text(encoding='utf-8'))
    if not preflight['pass'] or preflight['solver_called'] or preflight['problem_sha256'] != sha(args.problem):
        raise ValueError('不是此冻结问题的无搜索预检')
    model, variables = build_direct_model(value); path = args.output.with_name(args.output.stem+'-model.pb')
    if path.exists() or not model.export_to_file(str(path)): raise ValueError('不覆盖真实PB或导出失败')
    if sha(path) != preflight['model_proto_sha256']: raise ValueError('实际模型不同于冻结预检PB')
    solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 20261024; solver.parameters.max_time_in_seconds = 20.
    solver.parameters.log_search_progress = False
    started = time.perf_counter(); status = solver.solve(model); seconds = time.perf_counter()-started
    feasible = status in (cp_model.FEASIBLE, cp_model.OPTIMAL)
    result = {'problem_sha256': sha(args.problem), 'environment_lock_sha256': sha(args.environment_lock),
        'preflight_sha256': sha(args.preflight), 'source_sha256': sha(__file__), 'model_proto_sha256': sha(path),
        'status': solver.status_name(status), 'feasible': feasible,
        'variables': [int(solver.value(v)) for v in variables] if feasible else None,
        'seconds': seconds, 'parameters': str(solver.parameters), 'response_stats': solver.response_stats(),
        'python': sys.version, 'executable': sys.executable, 'process_memory': process_memory(), 'solver_called': True,
        'scope': '唯一1worker/seed20261024/20s直接八预算可行性搜索，无目标/hint；UNKNOWN不是无解。须回原环境fresh完整支撑和八预算再判。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print({k: result[k] for k in ('status', 'feasible', 'seconds')}, flush=True)


if __name__ == '__main__': main()
