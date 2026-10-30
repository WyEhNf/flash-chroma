"""隔离环境只读整数JSON执行一次CP-SAT，不导入lutlab/NumPy/Numba。"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
from cinema_first_cpsat_model import build_model


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--environment-lock', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖唯一20秒热点求解')
    from ortools.sat.python import cp_model
    if importlib.metadata.version('ortools') != '9.15.6755': raise ValueError('不是冻结ORTools版本')
    problem = json.loads(args.problem.read_text(encoding='utf-8'))
    if problem['schema'] != 'cinema_first_cpsat_problem_v1' or problem['solve'] != {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0}:
        raise ValueError('不是冻结单次单worker/seed/20sec问题')
    root = Path(__file__).resolve().parents[1]
    for name, expected in problem['source_sha256'].items():
        if sha(root/name) != expected: raise ValueError('实际求解源已变：'+name)
    if sha(args.environment_lock) != problem['environment_lock_sha256']: raise ValueError('隔离环境锁已变')
    lock = json.loads(args.environment_lock.read_text(encoding='utf-8'))
    for name, version in lock['packages'].items():
        if importlib.metadata.version(name) != version: raise ValueError('隔离依赖版本已变：'+name)
    for name, expected in lock['installed_record_sha256'].items():
        distribution = importlib.metadata.distribution(name)
        records = [f for f in distribution.files or [] if str(f).endswith('.dist-info/RECORD')]
        if len(records) != 1 or sha(distribution.locate_file(records[0])) != expected:
            raise ValueError('隔离依赖RECORD已变：'+name)
    model, variables = build_model(problem); solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1; solver.parameters.random_seed = 20261024
    solver.parameters.max_time_in_seconds = 20.; solver.parameters.log_search_progress = False
    model_path = args.output.with_name(args.output.stem+'-model.pb')
    if model_path.exists(): raise ValueError('不覆盖实际CP模型字节')
    if not model.export_to_file(str(model_path)): raise ValueError('CP模型导出失败')
    model_hash = sha(model_path)
    started = time.perf_counter(); status = solver.solve(model); seconds = time.perf_counter()-started
    feasible = status in (cp_model.FEASIBLE, cp_model.OPTIMAL)
    result = {'problem_sha256': sha(args.problem), 'environment_lock_sha256': sha(args.environment_lock),
              'source_sha256': sha(__file__), 'model_proto_sha256': model_hash,
              'status': solver.status_name(status), 'feasible': feasible, 'variables': [int(solver.value(v)) for v in variables] if feasible else None,
              'parameters': str(solver.parameters), 'seconds': seconds, 'response_stats': solver.response_stats(),
              'python': sys.version, 'executable': sys.executable,
              'scope': '一次局部热点精确整数求解；UNKNOWN非无解，INFEASIBLE无独立形式证明不升级全局结论；解尚须原环境完整支撑验收。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'seconds': seconds, 'feasible': feasible}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
