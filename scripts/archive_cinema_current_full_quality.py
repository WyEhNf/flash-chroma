"""封存完整资格的v1前置失败、机械v2通过及全部独立证据。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖完整双DLL资格归档')
    base=ROOT/'artifacts';folder=base/'cinema-current-full-quality-v2';f1=base/'cinema-current-full-quality-frozen-v1.json';f2=base/'cinema-current-full-quality-frozen-v2.json'
    one,two=read(f1),read(f2);proof_path=base/'cinema-current-full-quality-mechanical-v2.json';proof=read(proof_path)
    result=read(folder/'results.json');audit_path=base/'cinema-current-full-quality-independent-v2.json';audit=read(audit_path)
    if not audit['pass'] or audit['results_sha256']!=sha(folder/'results.json') or audit['histograms_sha256']!=sha(folder/'histograms.npz'):raise ValueError('不是独立已验资格')
    if sha(f1)!='96589fdd296e8be93fec31d9c84acab76d67f4dd925deaed45bb8c9b2b962b9e' or not proof['pass'] or proof['v1_frozen_sha256']!=sha(f1):raise ValueError('v1失败身份不同')
    for name,expected in one['source_sha256'].items():
        if sha(ROOT/name)!=expected or two['source_sha256'].get(name)!=expected:raise ValueError('原v1源未完整保留：'+name)
    for name,expected in two['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('v2执行源已变：'+name)
    for name,expected in proof['v2_generated_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('机械生成字节已变')
    if proof['generator_sha256']!=sha(ROOT/'scripts/prepare_cinema_current_full_v2.py'):raise ValueError('机械生成器已变')
    if result['mismatches'] or result['full_native_configs']!=12 or result['whole4t_streams']!=4 or result['actual_photo_configs']!=400 or result['overall_upgrade']:raise ValueError('范围/资格边界不符')
    if sha(folder/'candidate.rgb')!=result['candidate_oracle_sha256']:raise ValueError('完整oracle流已变')
    raw={'frozen-v1.json':f1,'frozen-v2.json':f2,'mechanical-v2.json':proof_path,'identity-v2.json':folder/'identity.json',
         'results-v2.json':folder/'results.json','independent-v2.json':audit_path,'full-checkpoint-v2.json':folder/'full-checkpoint.json',
         'process-affinity-v2.json':folder/'process-affinity.json'}
    args.output.mkdir(parents=True)
    for name,path in raw.items():shutil.copyfile(path,args.output/name)
    sources=set(two['source_sha256'])|{'scripts/archive_cinema_current_full_quality.py','scripts/audit_cinema_current_quality_git.py','scripts/audit_tail_git_evidence.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.writestr(name,(ROOT/name).read_bytes())
    evidence={'candidate.rgb':folder/'candidate.rgb','histograms.npz':folder/'histograms.npz',
        'v1/identity.json':base/'cinema-current-full-quality-v1/identity.json','v1/candidate.rgb':base/'cinema-current-full-quality-v1/candidate.rgb',
        'v1/freeze.log':base/'cinema-current-full-quality-freeze-execution-v1.log','v1/failed-execution.log':base/'cinema-current-full-quality-execution-v1.log',
        'v2/freeze.log':base/'cinema-current-full-quality-freeze-execution-v2.log','v2/execution.log':base/'cinema-current-full-quality-execution-v2.log',
        'v2/independent-audit.log':base/'cinema-current-full-quality-audit-execution-v2.log',
        'rgb24/build-check.json':base/'p16-direct-rgb24-build-v1/build-check.json','rgb24/build-frozen.json':base/'p16-direct-rgb24-build-frozen-v1/frozen.json',
        'ancestor-head-audit.json':base/'cinema-current-cpsat-pair-head-audit-v1.json'}
    for i in range(1,9):
        name='team-attempt-%02d.json'%i;evidence['v2/'+name]=folder/name
        team=read(folder/name)
        if team['return_code'] or len(team['records'])!=4:raise ValueError('观察原始返回码或team不符')
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    reused={}
    for field,stage in (('reused_current_feasible_manifest','p16-cinema-current-feasible-cpsat-20261024'),
        ('reused_quality_manifest','p16-cinema-max48-pareto-quality-20261024'),('reused_max48_risk_manifest','p16-cinema-max48-risk-upper-20261024')):
        path=ROOT/'report/data'/stage/'manifest.json';reused[field]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    manifest={'source_sha256':{name:sha(ROOT/name) for name in sorted(sources)},'support_member_sha256':{name:sha(path) for name,path in evidence.items()},**reused,
        'files':{path.name:sha(path) for path in args.output.iterdir()},
        'scope':'固定91d完整双DLL/16M/100图质量：v1线程观察器前置失败保留，机械v2在导入前process0x55并完整12流/4whole4T/400照片通过；逐图代价及cache预算断崖保留，未证速度50或默认升级。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for archive,field in (('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name,expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=expected:raise AssertionError('全资格ZIP字节SHA不符')
    print({'files':len(manifest['files']),'sources':len(sources),'support_members':len(evidence)},flush=True)


if __name__=='__main__':main()
