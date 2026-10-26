"""复用27050b1不可变祖先，只核本阶段raw/source/ZIP和旧目录无改动。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1];BASE='27050b19565c095a9583329bbff545d6ed0352e7'
STAGE='report/data/p16-cinema-current-outside-max-scale-20261024'
NEW=('experiments/p16-cinema-current-hint-proposal-v1.md','experiments/p16-cinema-current-outside-rank-v1.json',
     'experiments/p16-cinema-current-all-max-support-proposal-v1.md','experiments/p16-cinema-current-all-max-support-v1.json',
     'scripts/check_cinema_current_outside_rank.py','scripts/screen_cinema_current_all_max.py','scripts/audit_cinema_current_all_max.py',
     'scripts/archive_cinema_current_outside_scale.py','scripts/audit_cinema_current_scale_git.py','scripts/audit_tail_git_evidence.py')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--git-ref',default='HEAD');p.add_argument('--prior-audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖增量HEAD审计')
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
    def digest(v):return hashlib.sha256(v).hexdigest()
    prior_bytes=args.prior_audit.read_bytes();prior=json.loads(prior_bytes)
    assert prior['pass'] and prior['checked_commit']==BASE and len(prior['new_checks'])==241 and prior['reused_immutable_checks']==1285
    subprocess.run(['git','merge-base','--is-ancestor',BASE,args.git_ref],cwd=ROOT,check=True)
    changed=git('diff','--name-only',BASE,args.git_ref,'--','report/data').decode().splitlines();assert all(n.startswith(STAGE+'/') for n in changed)
    blob=git('show',args.git_ref+':'+STAGE+'/manifest.json');manifest=json.loads(blob);checks=[]
    def check(kind,name,value,expected):
        actual=digest(value);checks.append({'kind':kind,'path':name,'actual_sha256':actual,'expected_sha256':expected,'pass':actual==expected});assert actual==expected,name
    for name,expected in manifest['files'].items():check('new_git_blob',STAGE+'/'+name,git('show',args.git_ref+':'+STAGE+'/'+name),expected)
    check('new_manifest',STAGE+'/manifest.json',blob,digest((ROOT/STAGE/'manifest.json').read_bytes()))
    for name in NEW:check('new_source_git_blob',name,git('show',args.git_ref+':'+name),manifest['source_sha256'][name])
    for field in ('reused_current_full_quality_manifest','reused_current_feasible_manifest','reused_max48_risk_manifest'):
        spec=manifest[field];check(field,spec['path'],git('show',args.git_ref+':'+spec['path']),spec['sha256'])
    for archive,field in [('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')]:
        with zipfile.ZipFile(io.BytesIO(git('show',args.git_ref+':'+STAGE+'/'+archive))) as z:
            assert set(z.namelist())==set(manifest[field])
            for name,expected in manifest[field].items():check(field,STAGE+'/'+archive+'!/'+name,z.read(name),expected)
    result={'pass':True,'checked_commit':git('rev-parse',args.git_ref).decode().strip(),'new_checks':checks,'reused_ancestor_commit':BASE,
        'prior_audit_sha256':digest(prior_bytes),'reused_immutable_checks':1526,'prior_evidence_unchanged':True,'failures':[],
        'scope':'复用27050b1的241增量加9c的1285不可变证据，全部旧report目录无改动；仅本次新增成员逐字节核验，无数值补跑。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'new_checks':len(checks),'reused_immutable_checks':1526},flush=True)


if __name__=='__main__':main()
