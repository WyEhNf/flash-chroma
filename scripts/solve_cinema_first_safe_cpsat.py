"""隔离环境对全部危险表执行唯一20秒最小L1求解，不导入lutlab/Numba。"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
from cinema_first_safe_cpsat_model import build_safe_model


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--environment-lock', type=Path, required=True); p.add_argument('--preflight', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖完整危险表唯一20秒求解')
    from ortools.sat.python import cp_model
    if importlib.metadata.version('ortools') != '9.15.6755': raise ValueError('不是冻结ORTools版本')
    problem = json.loads(args.problem.read_text(encoding='utf-8')); root = Path(__file__).resolve().parents[1]
    if problem['solve'] != {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0}:
        raise ValueError('不是冻结单worker、seed、20秒参数')
    for name, expected in {**problem['source_sha256'], **problem['frozen_risk_sha256']}.items():
        if sha(root/name) != expected: raise ValueError('实际源/风险证据已变：'+name)
    if sha(args.environment_lock) != problem['environment_lock_sha256']: raise ValueError('隔离环境锁已变')
    lock = json.loads(args.environment_lock.read_text(encoding='utf-8'))
    for name, version in lock['packages'].items():
        if importlib.metadata.version(name) != version: raise ValueError('隔离依赖版本已变：'+name)
    for name, expected in lock['installed_record_sha256'].items():
        distribution = importlib.metadata.distribution(name)
        records = [v for v in distribution.files or [] if str(v).endswith('.dist-info/RECORD')]
        if len(records) != 1 or sha(distribution.locate_file(records[0])) != expected:
            raise ValueError('隔离依赖RECORD已变：'+name)
    preflight = json.loads(args.preflight.read_text(encoding='utf-8'))
    if not preflight['pass'] or preflight['solver_called'] or preflight['problem_sha256'] != sha(args.problem):
        raise ValueError('不是此冻结问题的无搜索预检')
    model, variables, absolutes = build_safe_model(problem)
    model_path = args.output.with_name(args.output.stem+'-model.pb')
    if model_path.exists() or not model.export_to_file(str(model_path)): raise ValueError('模型导出失败或已存在')
    if sha(model_path) != preflight['model_proto_sha256']: raise ValueError('实际求解PB不同于无搜索预检')
    solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 20261024; solver.parameters.max_time_in_seconds = 20.
    solver.parameters.log_search_progress = False
    started = time.perf_counter(); status = solver.solve(model); seconds = time.perf_counter()-started
    feasible = status in (cp_model.FEASIBLE, cp_model.OPTIMAL)
    values = [int(solver.value(v)) for v in variables] if feasible else None
    abs_values = [int(solver.value(v)) for v in absolutes] if feasible else None
    if feasible and abs_values != [abs(v) for v in values[:problem['n_node_variables']]]:
        raise AssertionError('abs辅助整数不等于实际节点delta绝对值')
    result = {'problem_sha256': sha(args.problem), 'environment_lock_sha256': sha(args.environment_lock),
        'preflight_sha256': sha(args.preflight), 'source_sha256': sha(__file__), 'model_proto_sha256': sha(model_path),
        'status': solver.status_name(status), 'feasible': feasible, 'variables': values, 'abs_variables': abs_values,
        'l1_objective_integer': sum(abs_values) if feasible else None, 'best_objective_bound': solver.best_objective_bound,
        'seconds': seconds, 'parameters': str(solver.parameters), 'response_stats': solver.response_stats(),
        'python': sys.version, 'executable': sys.executable,
        'scope': '仅一次完整危险表最小L1求解；L1不是精度保证，UNKNOWN非无解，平均/尾部预算必须回原环境完整验解。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'feasible', 'seconds', 'l1_objective_integer')}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
