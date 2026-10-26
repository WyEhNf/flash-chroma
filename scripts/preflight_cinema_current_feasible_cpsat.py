"""首解模型仅构建/验证/导出，无objective且不调用solver。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cinema_first_cpsat_model import build_model
from cinema_current_feasible_identity import process_peaks,sha,verify_frozen,verify_lock


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True);p.add_argument('--environment-lock',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖首解预检')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));verify_frozen(problem);verify_lock(problem,args.environment_lock)
    model,variables=build_model(problem)
    if model.has_objective():raise AssertionError('首解模型仍含目标')
    path=args.output.with_suffix('.pb');args.output.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() or not model.export_to_file(str(path)):raise ValueError('首解PB已存在或导出失败')
    value={'pass':True,'solver_called':False,'problem_sha256':sha(args.problem),'model_proto_sha256':sha(path),'constraint_sha256':problem['constraint_sha256'],
        'source_sha256':sha(__file__),'environment_lock_sha256':sha(args.environment_lock),'integer_variables':len(variables),'abs_variables':0,
        'rounding_rows':len(problem['rows']),'allowed_tables':len(problem['points']),'safe_rows':sum(len(p['allowed_deltas']) for p in problem['points']),
        'objective_encoded':model.has_objective(),'model_stats':model.model_stats(),'process_peaks':process_peaks(),
        'scope':'同一数学安全约束去目标首解的无搜索预检，未执行真实60秒solver。'}
    args.output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:value[k] for k in ('pass','solver_called','integer_variables','allowed_tables','safe_rows','objective_encoded')},flush=True)


if __name__=='__main__':main()
