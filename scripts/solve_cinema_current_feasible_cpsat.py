"""隔离环境仅一次60秒首解搜索，节点L1只记录而不优化。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
from cinema_first_cpsat_model import build_model
from cinema_current_feasible_identity import SOLVE,process_peaks,sha,verify_frozen,verify_lock


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True);p.add_argument('--environment-lock',type=Path,required=True)
    p.add_argument('--preflight',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖唯一首解搜索')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));verify_frozen(problem);verify_lock(problem,args.environment_lock)
    preflight=json.loads(args.preflight.read_text(encoding='utf-8'))
    if not preflight['pass'] or preflight['solver_called'] or preflight['objective_encoded'] or preflight['problem_sha256']!=sha(args.problem):raise ValueError('不是该无目标首解预检')
    from ortools.sat.python import cp_model
    model,variables=build_model(problem)
    if model.has_objective():raise AssertionError('禁止隐含优化目标')
    path=args.output.with_name(args.output.stem+'-model.pb');args.output.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() or not model.export_to_file(str(path)):raise ValueError('实际首解PB已存在或导出失败')
    if sha(path)!=preflight['model_proto_sha256']:raise ValueError('实际首解PB不同于已验预检')
    solver=cp_model.CpSolver()
    for name,value in SOLVE.items():setattr(solver.parameters,name,value)
    solver.parameters.log_search_progress=False;started=time.perf_counter();status=solver.solve(model);seconds=time.perf_counter()-started
    feasible=status in (cp_model.FEASIBLE,cp_model.OPTIMAL);values=[int(solver.value(v)) for v in variables] if feasible else None
    result={'problem_sha256':sha(args.problem),'environment_lock_sha256':sha(args.environment_lock),'preflight_sha256':sha(args.preflight),
        'model_proto_sha256':sha(path),'model_proto_path':str(path.resolve()),'source_sha256':sha(__file__),'constraint_sha256':problem['constraint_sha256'],
        'status':solver.status_name(status),'feasible':feasible,'variables':values,'observed_node_l1':sum(abs(v) for v in values[:problem['n_node_variables']]) if feasible else None,
        'objective_encoded':False,'seconds':seconds,'parameters':str(solver.parameters),'response_stats':solver.response_stats(),
        'python':sys.version,'executable':sys.executable,'process_peaks':process_peaks(),
        'scope':'仅一次无目标首解搜索，首个解即停；节点L1是观察量非最优值，UNKNOWN非无解，未执行精度终验。'}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:result[k] for k in ('status','feasible','seconds','observed_node_l1')},flush=True)


if __name__=='__main__':main()
