"""复用9c历史不可变证据，仅逐blob核本次完整资格及新成员。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE='9c7a84c8ebcf405d9987401af831d51ea96ccfbb'
STAGE='report/data/p16-cinema-current-full-quality-20261024'
NEW_SOURCE=('experiments/p16-cinema-current-full-quality-v1.json','experiments/p16-cinema-current-full-quality-v2.json',
    'scripts/qualify_cinema_current_full.py','scripts/audit_cinema_current_full_quality.py','scripts/prepare_cinema_current_full_v2.py',
    'scripts/qualify_cinema_current_full_v2.py','scripts/audit_cinema_current_full_quality_v2.py','scripts/archive_cinema_current_full_quality.py',
    'scripts/audit_cinema_current_quality_git.py','scripts/audit_tail_git_evidence.py')


def digest(value):return hashlib.sha256(value).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--git-ref',default='HEAD');p.add_argument('--prior-audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖增量HEAD证据审计')
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
    prior_bytes=args.prior_audit.read_bytes();prior=json.loads(prior_bytes)
    if not prior['pass'] or prior['checked_commit']!=BASE or len(prior['checks'])!=1285 or prior['failures']:raise ValueError('不是已交接9c完整历史审计')
    subprocess.run(['git','merge-base','--is-ancestor',BASE,args.git_ref],cwd=ROOT,check=True)
    old_folders=sorted({row['path'].split('!/')[0].rsplit('/',1)[0] for row in prior['checks'] if row['path'].startswith('report/data/')})
    if git('diff','--name-only',BASE,args.git_ref,'--',*old_folders).strip():raise ValueError('历史证据目录有改动，不能复用旧审计')
    manifest_bytes=git('show',args.git_ref+':'+STAGE+'/manifest.json');manifest=json.loads(manifest_bytes);checks=[]
    def check(kind,path,actual,expected):
        checks.append({'kind':kind,'path':path,'actual_sha256':digest(actual),'expected_sha256':expected,'pass':digest(actual)==expected})
        if digest(actual)!=expected:raise AssertionError('增量原字节SHA不符：'+path)
    for name,expected in manifest['files'].items():check('new_git_blob',STAGE+'/'+name,git('show',args.git_ref+':'+STAGE+'/'+name),expected)
    check('manifest_working_bytes',STAGE+'/manifest.json',manifest_bytes,digest((ROOT/STAGE/'manifest.json').read_bytes()))
    for name in NEW_SOURCE:check('new_source_git_blob',name,git('show',args.git_ref+':'+name),manifest['source_sha256'][name])
    for field in ('reused_current_feasible_manifest','reused_quality_manifest','reused_max48_risk_manifest'):
        spec=manifest[field];check(field,spec['path'],git('show',args.git_ref+':'+spec['path']),spec['sha256'])
    for archive,field in (('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')):
        with zipfile.ZipFile(io.BytesIO(git('show',args.git_ref+':'+STAGE+'/'+archive))) as z:
            if set(z.namelist())!=set(manifest[field]):raise AssertionError('ZIP成员不完整')
            for name,expected in manifest[field].items():check(field,STAGE+'/'+archive+'!/'+name,z.read(name),expected)
    result={'pass':True,'git_ref':args.git_ref,'checked_commit':git('rev-parse',args.git_ref).decode().strip(),'new_checks':checks,
        'reused_ancestor_commit':BASE,'reused_prior_audit_sha256':digest(prior_bytes),'reused_immutable_checks':1285,
        'ancestor_relationship_pass':True,'prior_evidence_directories_unchanged':old_folders,'failures':[],
        'scope':'旧1285项只消费已交接不可变commit及目录无改动；本次新增raw/source blob/ZIP/引用逐字节复核，无数值或性能补跑。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'new_checks':len(checks),'reused_immutable_checks':1285,'prior_directories_unchanged':len(old_folders)},flush=True)


if __name__=='__main__':main()
