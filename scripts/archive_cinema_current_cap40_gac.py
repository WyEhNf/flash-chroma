"""紧凑归档GAC未判定与88条合法删值，保持原CP状态边界。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖GAC紧凑归档')
    base=ROOT/'artifacts';folder=base/'cinema-current-cap40-gac-v1';frozen=read(folder/'frozen.json');contract=read(folder/'contract.json');cert=read(folder/'certificate.json');independent=read(folder/'independent.json')
    assert cert['status']=='GAC_FIXPOINT_UNDECIDED' and independent['pass'] and not independent['contradiction_replayed']
    assert independent['certificate_sha256']==sha(folder/'certificate.json') and cert['frozen_sha256']==sha(folder/'frozen.json')
    assert independent['independently_checked_deletions']==cert['deletions']==88 and len(contract['cases'])==10 and contract['pass']
    assert cert['point_revisions']<=frozen['plan']['资源门']['point_revisions_max'] and cert['local_assignments']<=frozen['plan']['资源门']['local_assignments_max']
    assert cert['problem_sha256']==frozen['problem_sha256']==sha(frozen['problem_path'])
    for name,expected in frozen['source_sha256'].items():assert sha(ROOT/name)==expected,name
    sources=set(frozen['source_sha256'])|{'scripts/archive_cinema_current_cap40_gac.py','scripts/audit_cinema_current_gac_git.py','scripts/audit_tail_git_evidence.py'}
    evidence={n:folder/n for n in ('frozen.json','contract.json','certificate.json','independent.json')}
    for label in ('freeze','contract','run','audit'):evidence['logs/'+label+'.log']=base/('cinema-current-cap40-gac-'+label+'-v1.log')
    evidence['parent/cap40-head-incremental.json']=base/'cinema-current-cap40-head-incremental-v1.json'
    evidence['parent/frontier-plot-head-audit.json']=base/'p16-tail-frontier-plot-head-audit-v1.json'
    parent=read(evidence['parent/frontier-plot-head-audit.json']);assert parent['passed'] and parent['scope']=='head' and (parent['files'],parent['zip_members'],parent['exact_source_population_rows'])==(15,23,12)
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in sorted(sources):z.writestr(n,(ROOT/n).read_bytes())
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n,path in evidence.items():z.write(path,n)
    summary={k:cert[k] for k in ('status','reason','point_revisions','local_assignments','deletions','search_calls')}
    summary.update(contradiction_replayed=False,shared_assignment_found=False,independent_local_assignments=independent['independent_local_assignments'],
        reason_points=len(independent['reason_point_indices']),reason_variables=len(independent['reason_variable_indices']),reason_physical_nodes=len(independent['certificate_reason_physical_nodes']),
        mixed_radius_enabled=False,overall_upgrade=False,scope='合法删值和非空固定点独立重放；不是矛盾证书或SAT，不更域。')
    (args.output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ref=ROOT/'report/data/p16-cinema-current-cap40-feasible-20261024/manifest.json';metadata={}
    for archive in ('source.zip','support-evidence.zip'):
        with zipfile.ZipFile(args.output/archive) as z:
            assert z.testzip() is None;metadata[archive]={n:{'sha256':hashlib.sha256(z.read(n)).hexdigest(),'crc32':z.getinfo(n).CRC,'bytes':z.getinfo(n).file_size} for n in z.namelist()}
    manifest={'source_sha256':{n:sha(ROOT/n) for n in sorted(sources)},'support_member_sha256':{n:sha(p) for n,p in evidence.items()},
        'zip_member_metadata':metadata,'reused_cap40_manifest':{'path':ref.relative_to(ROOT).as_posix(),'sha256':sha(ref)},
        'files':{p.name:sha(p) for p in args.output.iterdir()},'scope':'唯一无搜索GAC未判定，10有限合同/88合法删值与独立固定点；不把原CP INFEASIBLE扩成区间矛盾。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'files':len(manifest['files']),'source_members':len(sources),'support_members':len(evidence),'all_crc_sha_pass':True},flush=True)


if __name__=='__main__':main()
