"""增量核cap40归档的全部新blob及ZIP SHA/CRC，旧证据消费不可变祖先。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1];BASE='eb61615ec412286dac000656ab33d6506bc73f8c'
STAGE='report/data/p16-cinema-current-cap40-feasible-20261024'
NEW=('experiments/p16-cinema-current-cap40-feasible-v1.json','experiments/p16-cinema-current-cap40-feasible-proposal-v1.md',
    'scripts/cinema_current_cap40_identity.py','scripts/prepare_cinema_current_cap40.py','scripts/check_cinema_current_cap40.py',
    'scripts/audit_cinema_current_cap40_problem.py','scripts/run_cinema_current_cap40_solver.py','scripts/verify_cinema_current_cap40.py',
    'scripts/archive_cinema_current_cap40.py','scripts/audit_cinema_current_cap40_git.py','scripts/audit_tail_git_evidence.py')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--git-ref',default='HEAD');p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖cap40增量HEAD审计')
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
    def digest(v):return hashlib.sha256(v).hexdigest()
    subprocess.run(['git','merge-base','--is-ancestor',BASE,args.git_ref],cwd=ROOT,check=True)
    assert all(n.startswith(STAGE+'/') for n in git('diff','--name-only',BASE,args.git_ref,'--','report/data').decode().splitlines())
    blob=git('show',args.git_ref+':'+STAGE+'/manifest.json');manifest=json.loads(blob);checks=[]
    def check(kind,path,value,expected):
        actual=digest(value);checks.append({'kind':kind,'path':path,'actual_sha256':actual,'expected_sha256':expected,'pass':actual==expected});assert actual==expected,path
    for name,expected in manifest['files'].items():check('new_git_blob',STAGE+'/'+name,git('show',args.git_ref+':'+STAGE+'/'+name),expected)
    check('manifest',STAGE+'/manifest.json',blob,digest((ROOT/STAGE/'manifest.json').read_bytes()))
    for name in NEW:check('new_source_blob',name,git('show',args.git_ref+':'+name),manifest['source_sha256'][name])
    for field in ('reused_unit_manifest','reused_current_full_quality_manifest'):
        ref=manifest[field];check(field,ref['path'],git('show',args.git_ref+':'+ref['path']),ref['sha256'])
    for archive,field in [('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')]:
        with zipfile.ZipFile(io.BytesIO(git('show',args.git_ref+':'+STAGE+'/'+archive))) as z:
            assert z.testzip() is None and set(z.namelist())==set(manifest[field])
            for name,expected in manifest[field].items():
                check(field,STAGE+'/'+archive+'!/'+name,z.read(name),expected);m=manifest['zip_member_metadata'][archive][name]
                assert m['sha256']==expected and m['crc32']==z.getinfo(name).CRC and m['bytes']==z.getinfo(name).file_size
            if archive=='support-evidence.zip':
                prior=json.loads(z.read('parent/unit-head-incremental.json'));assert prior['pass'] and prior['checked_commit']==BASE and len(prior['new_checks'])==56
    result={'pass':True,'checked_commit':git('rev-parse',args.git_ref).decode().strip(),'new_checks':checks,'reused_ancestor_commit':BASE,
        'consumed_prior_new_checks':56,'consumed_tail_immutable_checks':1578,'consumed_parent_blob_count':77,'consumed_parent_zip_members':1681,
        'old_evidence_directories_unchanged':True,'all_crc_sha_pass':True,'failures':[],
        'scope':'新归档逐blob/ZIP SHA/CRC，前56+tail1578+root77/1681消费已验不可变原件；无数值或solver补跑。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'new_checks':len(checks),'all_crc_sha_pass':True},flush=True)


if __name__=='__main__':main()
