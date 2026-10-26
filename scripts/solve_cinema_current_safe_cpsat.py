"""隔离环境对当前4985完整安全表执行唯一20秒minL1，不导入NumPy/Numba。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
from cinema_first_safe_cpsat_model import build_safe_model
from cinema_current_safe_identity import SOLVE,process_peaks,sha,verify_frozen,verify_lock


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True)
    p.add_argument('--environment-lock',type=Path,required=True);p.add_argument('--preflight',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前安全模型唯一求解')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));verify_frozen(problem);verify_lock(problem,args.environment_lock)
    preflight=json.loads(args.preflight.read_text(encoding='utf-8'))
    if not preflight['pass'] or preflight['solver_called'] or preflight['problem_sha256']!=sha(args.problem):raise ValueError('预检不属于当前问题')
    from ortools.sat.python import cp_model
    model,variables,absolutes=build_safe_model(problem);path=args.output.with_name(args.output.stem+'-model.pb')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() or not model.export_to_file(str(path)):raise ValueError('求解PB已存在或导出失败')
    if sha(path)!=preflight['model_proto_sha256']:raise ValueError('唯一求解PB不等于已验预检')
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=SOLVE['num_search_workers'];solver.parameters.random_seed=SOLVE['random_seed']
    solver.parameters.max_time_in_seconds=SOLVE['max_time_in_seconds'];solver.parameters.log_search_progress=False
    started=time.perf_counter();status=solver.solve(model);seconds=time.perf_counter()-started
    feasible=status in (cp_model.FEASIBLE,cp_model.OPTIMAL);values=[int(solver.value(v)) for v in variables] if feasible else None
    abs_values=[int(solver.value(v)) for v in absolutes] if feasible else None
    if feasible and abs_values!=[abs(v) for v in values[:problem['n_node_variables']]]:raise AssertionError('实际abs不等于节点delta绝对值')
    result={'problem_sha256':sha(args.problem),'environment_lock_sha256':sha(args.environment_lock),'preflight_sha256':sha(args.preflight),
        'source_sha256':sha(__file__),'model_proto_sha256':sha(path),'model_proto_path':str(path.resolve()),
        'status':solver.status_name(status),'feasible':feasible,'variables':values,'abs_variables':abs_values,
        'l1_objective_integer':sum(abs_values) if feasible else None,'best_objective_bound':solver.best_objective_bound,
        'seconds':seconds,'parameters':str(solver.parameters),'response_stats':solver.response_stats(),
        'python':sys.version,'executable':sys.executable,'process_peaks':process_peaks(),
        'scope':'当前122节点完整安全表唯一minL1；L1不保证精度，UNKNOWN非无解，初门只在真实fresh支撑重放后判断。'}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:result[k] for k in ('status','feasible','seconds','l1_objective_integer')},flush=True)


if __name__=='__main__':main()
