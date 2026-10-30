"""隔离环境cap40预检或唯一60秒无目标首解；不导入NumPy。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
from cinema_first_cpsat_model import build_model
from cinema_current_cap40_identity import SOLVE,sha,verify,verify_lock,process_peaks
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/cinema-current-cap40-cpsat-v1'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['preflight','solve']);args=p.parse_args()
    target=OUT/('preflight.json' if args.mode=='preflight' else 'solution.json')
    if target.exists():raise FileExistsError('不覆盖新cap40预检或唯一solver')
    path=OUT/'problem.json';problem=json.loads(path.read_text(encoding='utf-8'));verify(problem)
    frozen=json.loads((OUT/'frozen.json').read_text(encoding='utf-8'));verify_lock(problem,frozen['environment_lock'])
    independent=json.loads((OUT/'problem-independent.json').read_text(encoding='utf-8'));assert independent['pass'] and independent['problem_sha256']==sha(path)
    model,variables=build_model(problem);assert not model.has_objective()
    pb=OUT/('preflight.pb' if args.mode=='preflight' else 'solution-model.pb')
    if pb.exists() or not model.export_to_file(str(pb)):raise ValueError('PB已存在或导出失败')
    common={'problem_sha256':sha(path),'model_proto_sha256':sha(pb),'model_proto_path':str(pb.resolve()),'constraint_sha256':problem['constraint_sha256'],
        'environment_lock_sha256':problem['environment_lock_sha256'],'source_sha256':sha(__file__),'objective_encoded':False}
    if args.mode=='preflight':
        result={**common,'pass':True,'solver_called':False,'integer_variables':len(variables),'rounding_rows':12174,'allowed_tables':4058,'safe_rows':74081,
            'model_stats':model.model_stats(),'process_peaks':process_peaks(),'scope':'CPValidate/PB导出，无真实搜索。'}
    else:
        prior=json.loads((OUT/'preflight.json').read_text(encoding='utf-8'))
        assert prior['pass'] and not prior['solver_called'] and prior['problem_sha256']==sha(path) and prior['model_proto_sha256']==sha(pb) and not prior['objective_encoded']
        from ortools.sat.python import cp_model
        solver=cp_model.CpSolver()
        for k,v in SOLVE.items():setattr(solver.parameters,k,v)
        solver.parameters.log_search_progress=True;started=time.perf_counter();status=solver.solve(model);seconds=time.perf_counter()-started
        feasible=status in (cp_model.FEASIBLE,cp_model.OPTIMAL);values=[int(solver.value(v)) for v in variables] if feasible else None
        result={**common,'preflight_sha256':sha(OUT/'preflight.json'),'status':solver.status_name(status),'feasible':feasible,'variables':values,
            'observed_node_l1':sum(abs(v) for v in values[:819]) if feasible else None,'seconds':seconds,'parameters':str(solver.parameters),
            'response_stats':solver.response_stats(),'python':sys.version,'executable':sys.executable,'process_peaks':process_peaks(),
            'scope':'唯一1worker/seed20261024/60秒首解；无hint/objective，UNKNOWN非无解，未作精度验解。'}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:result[k] for k in ('pass','solver_called','integer_variables') if k in result} if args.mode=='preflight' else {k:result[k] for k in ('status','feasible','seconds','observed_node_l1')},flush=True)


if __name__=='__main__':main()
