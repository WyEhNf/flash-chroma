"""当前4985完整安全表仅构建/CPvalidate/导出PB，禁止真实搜索。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cinema_first_safe_cpsat_model import build_safe_model
from cinema_current_safe_identity import process_peaks,sha,verify_frozen,verify_lock


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True)
    p.add_argument('--environment-lock',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前完整安全模型无搜索预检')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));verify_frozen(problem);verify_lock(problem,args.environment_lock)
    model,variables,absolutes=build_safe_model(problem);path=args.output.with_suffix('.pb')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() or not model.export_to_file(str(path)):raise ValueError('PB已存在或导出失败')
    value={'pass':True,'solver_called':False,'problem_sha256':sha(args.problem),'model_proto_sha256':sha(path),'source_sha256':sha(__file__),
        'environment_lock_sha256':sha(args.environment_lock),'base_variables':len(variables),'abs_variables':len(absolutes),
        'total_integer_variables':len(variables)+len(absolutes),'rounding_rows':len(problem['rows']),'allowed_tables':len(problem['points']),
        'safe_triples':sum(len(p['allowed_deltas']) for p in problem['points']),'objective_upper_bound':problem['objective_absolute_upper_bound'],
        'maximum_raw_absolute_bound':max(r['int64_audit']['raw_absolute_sum_bound'] for r in problem['rows']),
        'maximum_reduced_absolute_bound':max(r['int64_audit']['absolute_sum_bound'] for r in problem['rows']),
        'model_stats':model.model_stats(),'process_peaks':process_peaks(),
        'scope':'当前完整安全表minL1只构建和验证，未搜索；初门精度预算没有编码入CP。'}
    args.output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:value[k] for k in ('pass','solver_called','total_integer_variables','allowed_tables','safe_triples')},flush=True)


if __name__=='__main__':main()
