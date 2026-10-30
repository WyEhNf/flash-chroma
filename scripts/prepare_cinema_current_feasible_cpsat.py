"""复制认证完整安全数学约束并移除minL1，仅导出首解问题而不搜索。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cinema_current_safe_identity import verify_frozen as verify_prior
from cinema_current_feasible_identity import SOLVE,MATH_FIELDS,constraint_signature,sha,validate_feasible
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖首解真实问题')
    freeze=json.loads(args.frozen.read_text(encoding='utf-8'));contract=json.loads(args.contract.read_text(encoding='utf-8'))
    if not freeze['ast_pass'] or not contract['pass']:raise ValueError('先冻结并完成首解有限合同')
    for sources in (freeze['source_sha256'],contract['source_sha256']):
        for name,expected in sources.items():
            if sha(ROOT/name)!=expected:raise ValueError('首解源已变：'+name)
    for spec in freeze['inputs'].values():
        if sha(spec['path'])!=spec['sha256']:raise ValueError('首解冻结输入已变')
    prior=json.loads(Path(freeze['inputs']['original_problem']['path']).read_text(encoding='utf-8'));verify_prior(prior)
    problem={name:prior[name] for name in MATH_FIELDS}
    problem.update(schema='cinema_current_feasible_problem_v1',experiment='cinema_current741_cap47_feasible_v1',solve=SOLVE,
        constraint_sha256=constraint_signature(prior),source_sha256=freeze['source_sha256'],
        frozen_risk_sha256=freeze['frozen_risk_sha256'],inputs=prior['inputs'],source_inputs=prior['source_inputs'],
        environment_lock_sha256=prior['environment_lock_sha256'],prior_problem_sha256=sha(freeze['inputs']['original_problem']['path']),
        contract_sha256=sha(args.contract),frozen_sha256=sha(args.frozen))
    for name in MATH_FIELDS:
        if problem[name]!=prior[name]:raise AssertionError('移除目标时数学项发生改变')
    validate_feasible(problem);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(problem,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'variables':len(problem['variables']),'tables':len(problem['points']),'safe_rows':sum(len(p['allowed_deltas']) for p in problem['points']),
        'constraint_sha256':problem['constraint_sha256'],'objective_encoded':False,'solver_called':False},flush=True)


if __name__=='__main__':main()
