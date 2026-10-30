"""封存当前完整安全minL1唯一20秒UNKNOWN及无incumbent边界。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import zipfile
from cinema_current_safe_identity import sha,verify_frozen
ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前安全minL1 UNKNOWN归档')
    base=ROOT/'artifacts';problem_path=base/'cinema-current-safe-cpsat-problem-v1.json';problem=read(problem_path);verify_frozen(problem)
    raw={'frozen.json':base/'cinema-current-safe-cpsat-frozen-v1.json','contract.json':base/'cinema-current-safe-cpsat-contract-v1.json',
         'preflight.json':base/'cinema-current-safe-cpsat-preflight-v1.json','independent-audit.json':base/'cinema-current-safe-cpsat-problem-independent-v1.json',
         'solution.json':base/'cinema-current-safe-cpsat-solution-v1.json'}
    contract=read(raw['contract.json']);preflight=read(raw['preflight.json']);audit=read(raw['independent-audit.json']);solution=read(raw['solution.json'])
    if not contract['pass'] or not preflight['pass'] or preflight['solver_called'] or not audit['pass']:raise ValueError('前置证据未过')
    if any(r['problem_sha256']!=sha(problem_path) for r in (preflight,audit,solution)):raise ValueError('原件问题身份不一致')
    if solution['status']!='UNKNOWN' or solution['feasible'] or solution['variables'] is not None or solution['l1_objective_integer'] is not None:
        raise ValueError('不是唯一无incumbent UNKNOWN状态')
    if solution['preflight_sha256']!=sha(raw['preflight.json']) or solution['model_proto_sha256']!=preflight['model_proto_sha256'] or sha(solution['model_proto_path'])!=solution['model_proto_sha256']:
        raise ValueError('实际solver与预检身份不同')
    if problem['frozen_sha256']!=sha(raw['frozen.json']) or problem['contract_sha256']!=sha(raw['contract.json']):raise ValueError('冻结或合同不符')
    args.output.mkdir(parents=True)
    for name,path in raw.items():shutil.copyfile(path,args.output/name)
    sources=set(problem['source_sha256'])|{'scripts/archive_cinema_current_safe_cpsat.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    evidence={'problem.json':problem_path,'preflight.pb':raw['preflight.json'].with_suffix('.pb'),'actual-solver.pb':Path(solution['model_proto_path'])}
    for case in contract['cases']:
        path=base/('cinema-current-safe-cpsat-contract-v1-'+case['name']+'.pb')
        if sha(path)!=case['model_proto_sha256']:raise ValueError('有限合同PB已变')
        evidence['finite/'+path.name]=path
    for phase in ('contract','prepare','preflight','audit','solver'):
        evidence['logs/'+phase+'.log']=base/('cinema-current-safe-cpsat-'+phase+'-execution-v1.log')
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    reused={}
    for field,folder in (('reused_max48_risk_manifest','p16-cinema-max48-risk-upper-20261024'),
        ('reused_environment_manifest','p16-cinema-first-cpsat-20261024'),('reused_quality_manifest','p16-cinema-max48-pareto-quality-20261024')):
        path=ROOT/'report/data'/folder/'manifest.json';reused[field]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    manifest={'source_sha256':{name:sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256':{name:sha(path) for name,path in evidence.items()},**reused,
        'files':{path.name:sha(path) for path in args.output.iterdir()},
        'scope':'当前122节点4985完整安全表单worker/seed20261024/20s minL1，UNKNOWN且无incumbent，按冻结STOP。8有限投影与最优L1/真实Q16独立审计通过，但未生成新模型或执行真实候选质量/性能。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for archive,field in (('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name,expected in manifest[field].items():
                import hashlib
                if hashlib.sha256(z.read(name)).hexdigest()!=expected:raise AssertionError('ZIP成员SHA不同')
    print({'files':len(manifest['files']),'sources':len(sources),'support_members':len(evidence)},flush=True)


if __name__=='__main__':main()
