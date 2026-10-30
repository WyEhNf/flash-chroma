"""封存固定外域秩下界与全部最劣点扩展的严格规模STOP。"""
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
    if args.output.exists():raise FileExistsError('不覆盖外域与规模阶段归档')
    base=ROOT/'artifacts';rank=base/'cinema-current-outside-rank-v1';scale=base/'cinema-current-all-max-support-v1'
    a,b=read(rank/'frozen.json'),read(scale/'frozen.json');result=read(rank/'results.json');summary=read(scale/'summary.json')
    audit_path=base/'cinema-current-all-max-support-independent-v1.json';audit=read(audit_path)
    assert result['pass'] and audit['pass'] and audit['summary_sha256']==sha(scale/'summary.json')
    assert summary['stop']=='state_count_gate' and summary['aabb_states']==5284765 and summary['state_queries']==0 and summary['solver_calls']==0
    assert summary['aabb_states']>b['plan']['资源门']['maximum_total_aabb_states']==4194304
    for name,expected in a['sources_sha256'].items():assert sha(name)==expected,name
    for name,expected in a['inputs_sha256'].items():assert sha(name)==expected,name
    for name,expected in b['source_sha256'].items():assert sha(ROOT/name)==expected,name
    for spec in b['inputs'].values():assert sha(spec['path'])==spec['sha256'],spec['path']
    raw={'outside-frozen.json':rank/'frozen.json','outside-results.json':rank/'results.json','scale-frozen.json':scale/'frozen.json',
        'contract.json':scale/'contract.json','selection.json':scale/'selection.json','run-input.json':scale/'run-input.json',
        'scale-summary.json':scale/'summary.json','scale-independent.json':audit_path}
    args.output.mkdir(parents=True)
    for name,path in raw.items():shutil.copyfile(path,args.output/name)
    sources=set(b['source_sha256'])|{Path(n).relative_to(ROOT).as_posix() for n in a['sources_sha256']}|{
        'scripts/archive_cinema_current_outside_scale.py','scripts/audit_cinema_current_scale_git.py','scripts/audit_tail_git_evidence.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.writestr(name,(ROOT/name).read_bytes())
    evidence={'selection.npz':scale/'selection.npz','aabb.npz':scale/'aabb.npz',
        'ancestor-head-incremental.json':base/'cinema-current-full-quality-head-incremental-v2.json'}
    for label in ('freeze','contract','select','run','audit'):
        evidence[label+'.log']=base/('cinema-current-all-max-support-'+label+'-v1.log')
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    reused={}
    for field,stage in [('reused_current_full_quality_manifest','p16-cinema-current-full-quality-20261024'),
        ('reused_current_feasible_manifest','p16-cinema-current-feasible-cpsat-20261024'),('reused_max48_risk_manifest','p16-cinema-max48-risk-upper-20261024')]:
        path=ROOT/'report/data'/stage/'manifest.json';reused[field]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    manifest={'source_sha256':{name:sha(ROOT/name) for name in sorted(sources)},'support_member_sha256':{name:sha(path) for name,path in evidence.items()},
        **reused,'files':{path.name:sha(path) for path in args.output.iterdir()},
        'scope':'旧122固定外域阻断p99/max；新273完整支撑171271，5284765状态超新4194304门严格STOP，0状态查询/0CP，不作无解或晋级结论。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for archive,field in [('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')]:
        with zipfile.ZipFile(args.output/archive) as z:
            assert set(z.namelist())==set(manifest[field])
            for name,expected in manifest[field].items():assert hashlib.sha256(z.read(name)).hexdigest()==expected,name
    print({'files':len(manifest['files']),'source_members':len(sources),'support_members':len(evidence)},flush=True)


if __name__=='__main__':main()
