"""紧凑封存±1完整安全规模与扩展固定外域下界，原始JSON仅进ZIP。"""
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
    if args.output.exists():raise FileExistsError('不覆盖±1阶段紧凑归档')
    base=ROOT/'artifacts';unit=base/'cinema-current-all-max-unit-v1';expanded=base/'cinema-current-expanded-outside-rank-v1'
    frozen=read(unit/'frozen.json');summary=read(unit/'summary.json');audit_path=base/'cinema-current-all-max-unit-independent-v1.json';audit=read(audit_path)
    assert audit['pass'] and audit['summary_sha256']==sha(unit/'summary.json') and summary['within_gate'] and summary['zero_safe_rows']==0 and summary['solver_calls']==0
    for name,expected in frozen['source_sha256'].items():assert sha(ROOT/name)==expected,name
    for name,expected in frozen['inputs_sha256'].items():assert sha(name)==expected,name
    ef=read(expanded/'frozen.json');er=read(expanded/'results.json');assert er['pass'] and er['frozen_sha256']==sha(expanded/'frozen.json')
    for name,expected in {**ef['sources_sha256'],**ef['inputs_sha256']}.items():assert sha(name)==expected,name
    root_head=base/'p16-direct-cache2-head-audit-v1.json';parent=read(root_head);assert parent['passed'] and parent['mode']=='HEAD' and len(parent['blob_sha256'])==77 and parent['zip_members']==1681
    sources=set(frozen['source_sha256'])|{Path(n).relative_to(ROOT).as_posix() for n in ef['sources_sha256']}|{
        'experiments/p16-cinema-current-expanded-outside-rank-note-v1.md','scripts/archive_cinema_current_all_max_unit.py',
        'scripts/audit_cinema_current_unit_git.py','scripts/audit_tail_git_evidence.py'}
    evidence={}
    for name in ('frozen.json','contract.json','run-input.json','summary.json','aabb.npz','screen.npz','danger-allowed.npz'):evidence['unit/'+name]=unit/name
    evidence['unit/independent.json']=audit_path
    for name in ('frozen.json','results.json'):evidence['expanded/'+name]=expanded/name
    for label in ('freeze','contract','run','audit'):evidence['logs/'+label+'.log']=base/('cinema-current-all-max-unit-'+label+'-v1.log')
    evidence['logs/expanded-rank.log']=base/'cinema-current-expanded-outside-rank-v1.log'
    evidence['parent/tail-head-incremental.json']=base/'cinema-current-outside-scale-head-incremental-v1.json'
    evidence['parent/cache2-head-audit.json']=root_head
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.writestr(name,(ROOT/name).read_bytes())
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    compact={'within_resource_gate':True,'shared_assignment_found':False,'solver_calls':0,'selected_nodes':273,'support_rows':171271,
        'all_q41_count':231,'aabb_states':summary['aabb_states'],'dangerous_rows':summary['dangerous_rows'],'safe_rows':summary['safe_rows'],
        'zero_safe_rows':0,'outside_max_squared':38,'optimistic_p99_lower_bound':{k:v['optimistic_p99_lower_bound'] for k,v in er['groups'].items()},
        'inherited_label_note':'辅助comparison.interpretation继承122字面量，实际273上下文见独立勘误；原件保留，数值未补跑。',
        'performance_measured':False,'overall_upgrade':False}
    (args.output/'summary.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    references={}
    for field,stage in [('reused_expanded_support_manifest','p16-cinema-current-outside-max-scale-20261024'),
        ('reused_current_full_quality_manifest','p16-cinema-current-full-quality-20261024'),('reused_current_feasible_manifest','p16-cinema-current-feasible-cpsat-20261024')]:
        p=ROOT/'report/data'/stage/'manifest.json';references[field]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
    zip_metadata={}
    for archive in ('source.zip','support-evidence.zip'):
        with zipfile.ZipFile(args.output/archive) as z:
            assert z.testzip() is None
            zip_metadata[archive]={n:{'sha256':hashlib.sha256(z.read(n)).hexdigest(),'crc32':z.getinfo(n).CRC,'bytes':z.getinfo(n).file_size} for n in z.namelist()}
    manifest={'source_sha256':{n:sha(ROOT/n) for n in sorted(sources)},'support_member_sha256':{n:sha(p) for n,p in evidence.items()},
        'zip_member_metadata':zip_metadata,**references,'files':{p.name:sha(p) for p in args.output.iterdir()},
        'scope':'±1新域安全规模1400540/4058/74081/0空，原始JSON仅ZIP；不是共享解/CP/性能，旧±2超门保持。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'files':len(manifest['files']),'source_members':len(sources),'support_members':len(evidence),'all_crc_sha_pass':True},flush=True)


if __name__=='__main__':main()
