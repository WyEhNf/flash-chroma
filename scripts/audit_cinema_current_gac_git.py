"""GAC阶段增量原字节/CRC审计，消费不可变cap40与父图收据。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1];BASE='f82836b65362d301566b3ca7d91a0dd94ca01a0a'
STAGE='report/data/p16-cinema-current-cap40-gac-20261024'
NEW=('experiments/p16-cinema-current-cap40-gac-v1.json','experiments/p16-cinema-current-cap40-gac-proposal-v1.md',
    'scripts/cinema_cap40_gac_core.py','scripts/cinema_cap40_gac_checker.py','scripts/run_cinema_current_cap40_gac.py',
    'scripts/archive_cinema_current_cap40_gac.py','scripts/audit_cinema_current_gac_git.py','scripts/audit_tail_git_evidence.py')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--git-ref',default='HEAD');p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖GAC增量HEAD审计')
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
    def digest(v):return hashlib.sha256(v).hexdigest()
    subprocess.run(['git','merge-base','--is-ancestor',BASE,args.git_ref],cwd=ROOT,check=True)
    assert all(n.startswith(STAGE+'/') for n in git('diff','--name-only',BASE,args.git_ref,'--','report/data').decode().splitlines())
    blob=git('show',args.git_ref+':'+STAGE+'/manifest.json');m=json.loads(blob);checks=[]
    def check(kind,name,value,expected):
        actual=digest(value);checks.append({'kind':kind,'path':name,'actual_sha256':actual,'expected_sha256':expected,'pass':actual==expected});assert actual==expected,name
    for name,expected in m['files'].items():check('new_git_blob',STAGE+'/'+name,git('show',args.git_ref+':'+STAGE+'/'+name),expected)
    check('manifest',STAGE+'/manifest.json',blob,digest((ROOT/STAGE/'manifest.json').read_bytes()))
    for n in NEW:check('new_source_blob',n,git('show',args.git_ref+':'+n),m['source_sha256'][n])
    ref=m['reused_cap40_manifest'];check('reused_cap40_manifest',ref['path'],git('show',args.git_ref+':'+ref['path']),ref['sha256'])
    for archive,field in [('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')]:
        with zipfile.ZipFile(io.BytesIO(git('show',args.git_ref+':'+STAGE+'/'+archive))) as z:
            assert z.testzip() is None and set(z.namelist())==set(m[field])
            for n,expected in m[field].items():
                check(field,STAGE+'/'+archive+'!/'+n,z.read(n),expected);meta=m['zip_member_metadata'][archive][n]
                assert meta['sha256']==expected and meta['crc32']==z.getinfo(n).CRC and meta['bytes']==z.getinfo(n).file_size
            if archive=='support-evidence.zip':
                prior=json.loads(z.read('parent/cap40-head-incremental.json'));parent=json.loads(z.read('parent/frontier-plot-head-audit.json'))
                assert prior['pass'] and prior['checked_commit']=='4db91f8c9566b3edbd34103c8e76e32d7c2f85fe' and len(prior['new_checks'])==68
                assert parent['passed'] and (parent['files'],parent['zip_members'],parent['exact_source_population_rows'])==(15,23,12)
    result={'pass':True,'checked_commit':git('rev-parse',args.git_ref).decode().strip(),'new_checks':checks,'reused_ancestor_commit':BASE,
        'consumed_cap40_new_checks':68,'consumed_parent_plot_objects':15,'consumed_parent_plot_zip_members':23,'consumed_parent_plot_source_rows':12,
        'prior_evidence_directories_unchanged':True,'all_crc_sha_pass':True,'failures':[],
        'scope':'新增raw/source/ZIP SHA/CRC逐项；旧cap40祖先及父图收据消费，父attrs与额外字节补记不冒称在15对象内。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'new_checks':len(checks),'all_crc_sha_pass':True},flush=True)


if __name__=='__main__':main()
