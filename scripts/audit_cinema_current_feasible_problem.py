"""按完整整数约束恒等性转移已过八角帽权审计，不新增RGB查询。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cinema_current_feasible_identity import MATH_FIELDS,constraint_signature,sha,verify_frozen


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True);p.add_argument('--prior-problem',type=Path,required=True)
    p.add_argument('--prior-audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖首解完整约束恒等审计')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));verify_frozen(problem)
    prior=json.loads(args.prior_problem.read_text(encoding='utf-8'));audit=json.loads(args.prior_audit.read_text(encoding='utf-8'))
    if sha(args.prior_problem)!=problem['prior_problem_sha256'] or not audit['pass'] or audit['problem_sha256']!=sha(args.prior_problem):raise ValueError('原独立八角审计身份不符')
    for name in MATH_FIELDS:
        if problem[name]!=prior[name]:raise AssertionError('完整数学约束不恒等：'+name)
    if constraint_signature(prior)!=problem['constraint_sha256']:raise AssertionError('原数学签名不符')
    if (audit['checked_points'],audit['checked_q16_rows'],audit['checked_allowed_rgb'])!=(4985,14955,386612):raise ValueError('转移审计不完整')
    result={'pass':True,'problem_sha256':sha(args.problem),'prior_problem_sha256':sha(args.prior_problem),'prior_audit_sha256':sha(args.prior_audit),
        'constraint_sha256':problem['constraint_sha256'],'identical_math_fields':list(MATH_FIELDS),'checked_points':4985,'checked_q16_rows':14955,'checked_allowed_rgb':386612,
        'scope':'完整变量/原始及gcd行/全部表与公共初门逐项相等，原独立八角Q16/安全误差证据可转移；没有新RGB查询、模型搜索或解存在证明。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'math_fields':len(MATH_FIELDS),'tables':4985},flush=True)


if __name__=='__main__':main()
