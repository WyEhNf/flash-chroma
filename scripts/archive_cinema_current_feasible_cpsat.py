"""封存无目标首解与当前完整支撑初门，不冒充native/百图资格。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from cinema_current_feasible_identity import sha,verify_frozen
ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖无目标首解初门归档')
    base=ROOT/'artifacts';problem_path=base/'cinema-current-feasible-cpsat-problem-v1.json';problem=read(problem_path);verify_frozen(problem)
    accept=base/'cinema-current-feasible-cpsat-accept-v1'
    raw={'frozen.json':base/'cinema-current-feasible-cpsat-frozen-v1.json','contract.json':base/'cinema-current-feasible-cpsat-contract-v1.json',
         'preflight.json':base/'cinema-current-feasible-cpsat-preflight-v1.json','independent-audit.json':base/'cinema-current-feasible-cpsat-problem-independent-v1.json',
         'solution.json':base/'cinema-current-feasible-cpsat-solution-v1.json','accept-summary.json':accept/'summary.json'}
    contract=read(raw['contract.json']);preflight=read(raw['preflight.json']);audit=read(raw['independent-audit.json']);solution=read(raw['solution.json']);summary=read(raw['accept-summary.json'])
    if not contract['pass'] or not preflight['pass'] or preflight['solver_called'] or preflight['objective_encoded'] or not audit['pass']:raise ValueError('首解前置证据未过')
    if any(r['problem_sha256']!=sha(problem_path) for r in (preflight,audit,solution)):raise ValueError('首解问题SHA不一致')
    if not solution['feasible'] or solution['status'] not in ('FEASIBLE','OPTIMAL') or solution['objective_encoded']:raise ValueError('不是无目标真实首解')
    if not summary['eligible_for_independent_final_checks'] or summary['failures'] or summary['after_uniform']['max_squared']!=41:raise ValueError('不是已过固定初门的首解')
    if solution['preflight_sha256']!=sha(raw['preflight.json']) or solution['model_proto_sha256']!=preflight['model_proto_sha256'] or sha(solution['model_proto_path'])!=solution['model_proto_sha256']:
        raise ValueError('首解实际PB身份不符')
    if problem['frozen_sha256']!=sha(raw['frozen.json']) or problem['contract_sha256']!=sha(raw['contract.json']):raise ValueError('首解冻结/合同不符')
    candidate=accept/'candidate'
    if sha(candidate/'model.npz')!=summary['candidate_npz_sha256']:raise ValueError('首解模型已变')
    args.output.mkdir(parents=True)
    for name,path in raw.items():shutil.copyfile(path,args.output/name)
    sources=set(problem['source_sha256'])|{'scripts/archive_cinema_current_feasible_cpsat.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    evidence={'problem.json':problem_path,'preflight.pb':raw['preflight.json'].with_suffix('.pb'),'actual-solver.pb':Path(solution['model_proto_path']),
              'accept/replay.npz':accept/'replay.npz'}
    for case in contract['cases']:
        path=base/('cinema-current-feasible-cpsat-contract-v1-'+case['name']+'.pb')
        if sha(path)!=case['model_proto_sha256']:raise ValueError('首解有限PB已变')
        evidence['finite/'+path.name]=path
    for phase in ('contract','prepare','preflight','audit','solver','verify'):
        evidence['logs/'+phase+'.log']=base/('cinema-current-feasible-cpsat-'+phase+'-execution-v1.log')
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    models={name:candidate/name for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage2.slut','stage4.slut')}
    models['stage3.slut']=Path(problem['inputs']['stage3']['path'])
    with zipfile.ZipFile(args.output/'models.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in models.items():z.write(path,name)
    reused={}
    for field,folder in (('reused_current_minl1_manifest','p16-cinema-current-safe-cpsat-20261024'),
        ('reused_max48_risk_manifest','p16-cinema-max48-risk-upper-20261024'),('reused_quality_manifest','p16-cinema-max48-pareto-quality-20261024')):
        path=ROOT/'report/data'/folder/'manifest.json';reused[field]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    manifest={'source_sha256':{name:sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256':{name:sha(path) for name,path in evidence.items()},'model_member_sha256':{name:sha(path) for name,path in models.items()},**reused,
        'files':{path.name:sha(path) for path in args.output.iterdir()},
        'scope':'同一完整安全约束无objective唯一首解，31.554s可行、观察L1=442非最优；145/4985/80751 freshu64与公共best cube/train mean/p99初门过，全域max²41。没有native/100图/性能或整体升级资格。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for archive,field in (('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256'),('models.zip','model_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name,expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=expected:raise AssertionError('首解ZIP原字节SHA不符')
    print({'files':len(manifest['files']),'sources':len(sources),'support_members':len(evidence),'model_members':len(models)},flush=True)


if __name__=='__main__':main()
