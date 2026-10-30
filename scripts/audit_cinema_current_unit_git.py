"""消费e94d不可变父审计，逐blob/ZIP SHA/CRC核本次紧凑阶段。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1];BASE='e94d279e41ff67f4363fc1ede5b1c0e72c84c88a'
STAGE='report/data/p16-cinema-current-all-max-unit-20261024'
NEW=('experiments/p16-cinema-current-all-max-unit-v1.json','experiments/p16-cinema-current-expanded-outside-rank-note-v1.md',
     'scripts/screen_cinema_current_all_max_unit.py','scripts/audit_cinema_current_all_max_unit.py','scripts/check_cinema_current_expanded_outside_rank.py',
     'scripts/archive_cinema_current_all_max_unit.py','scripts/audit_cinema_current_unit_git.py','scripts/audit_tail_git_evidence.py')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--git-ref',default='HEAD');p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖紧凑阶段增量HEAD审计')
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
    def digest(v):return hashlib.sha256(v).hexdigest()
    subprocess.run(['git','merge-base','--is-ancestor',BASE,args.git_ref],cwd=ROOT,check=True)
    assert all(n.startswith(STAGE+'/') for n in git('diff','--name-only',BASE,args.git_ref,'--','report/data').decode().splitlines())
    blob=git('show',args.git_ref+':'+STAGE+'/manifest.json');manifest=json.loads(blob);checks=[]
    def check(kind,name,value,expected):
        actual=digest(value);checks.append({'kind':kind,'path':name,'actual_sha256':actual,'expected_sha256':expected,'pass':actual==expected});assert actual==expected,name
    for name,expected in manifest['files'].items():check('new_git_blob',STAGE+'/'+name,git('show',args.git_ref+':'+STAGE+'/'+name),expected)
    check('manifest',STAGE+'/manifest.json',blob,digest((ROOT/STAGE/'manifest.json').read_bytes()))
    for name in NEW:check('new_source_git_blob',name,git('show',args.git_ref+':'+name),manifest['source_sha256'][name])
    for field in ('reused_expanded_support_manifest','reused_current_full_quality_manifest','reused_current_feasible_manifest'):
        ref=manifest[field];check(field,ref['path'],git('show',args.git_ref+':'+ref['path']),ref['sha256'])
    for archive,field in [('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')]:
        with zipfile.ZipFile(io.BytesIO(git('show',args.git_ref+':'+STAGE+'/'+archive))) as z:
            assert set(z.namelist())==set(manifest[field]) and z.testzip() is None
            for name,expected in manifest[field].items():
                check(field,STAGE+'/'+archive+'!/'+name,z.read(name),expected);meta=manifest['zip_member_metadata'][archive][name]
                assert meta['sha256']==expected and z.getinfo(name).CRC==meta['crc32'] and z.getinfo(name).file_size==meta['bytes']
            if archive=='support-evidence.zip':
                parent=json.loads(z.read('parent/cache2-head-audit.json'));prior=json.loads(z.read('parent/tail-head-incremental.json'))
                assert parent['passed'] and parent['mode']=='HEAD' and len(parent['blob_sha256'])==77 and parent['zip_members']==1681
                assert prior['pass'] and len(prior['new_checks'])==52 and prior['reused_immutable_checks']==1526
    result={'pass':True,'checked_commit':git('rev-parse',args.git_ref).decode().strip(),'new_checks':checks,'reused_ancestor_commit':BASE,
        'reused_tail_immutable_checks':1578,'consumed_parent_head_blob_count':77,'consumed_parent_zip_members':1681,
        'prior_evidence_unchanged':True,'all_crc_sha_pass':True,'failures':[],
        'scope':'新成员逐字节与CRC；消费父阶段77blob/1681ZIP原始审计及tail1578不可变历史，不冒称本阶段重做父数值或全部旧成员核。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'new_checks':len(checks),'reused_tail_checks':1578,'consumed_parent_blobs':77,'consumed_parent_members':1681},flush=True)


if __name__=='__main__':main()
