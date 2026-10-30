"""只读封存唯一cap40首解的INFEASIBLE，原始大JSON/PB/log压入ZIP。"""
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
    if args.output.exists():raise FileExistsError('不覆盖cap40首解归档')
    base=ROOT/'artifacts';folder=base/'cinema-current-cap40-cpsat-v1';frozen=read(folder/'frozen.json');solution=read(folder/'solution.json')
    contract=read(folder/'contract.json');independent=read(folder/'problem-independent.json');preflight=read(folder/'preflight.json')
    assert solution['status']=='INFEASIBLE' and not solution['feasible'] and solution['variables'] is None and solution['observed_node_l1'] is None
    assert solution['problem_sha256']==sha(folder/'problem.json')==independent['problem_sha256']==preflight['problem_sha256']
    assert solution['preflight_sha256']==sha(folder/'preflight.json') and solution['model_proto_sha256']==sha(folder/'solution-model.pb')==sha(folder/'preflight.pb')
    assert contract['pass'] and independent['pass'] and preflight['pass'] and not preflight['solver_called']
    assert len(contract['cases'])==7 and contract['overflow_rows_rejected']==2 and contract['environment']['packages']['ortools']=='9.15.6755'
    assert not (base/'cinema-current-cap40-cpsat-accept-v1').exists()
    for name,expected in frozen['source_sha256'].items():assert sha(ROOT/name)==expected,name
    for name,expected in frozen['inputs_sha256'].items():assert sha(name)==expected,name
    sources=set(frozen['source_sha256'])|{'scripts/archive_cinema_current_cap40.py','scripts/audit_cinema_current_cap40_git.py','scripts/audit_tail_git_evidence.py'}
    evidence={name:folder/name for name in ('frozen.json','contract.json','problem.json','problem-independent.json','preflight.json','preflight.pb','solution.json','solution-model.pb')}
    for label in ('freeze','contract','problem','audit','preflight','solve'):evidence['logs/'+label+'.log']=base/('cinema-current-cap40-'+label+'-v1.log')
    evidence['environment-lock.json']=Path(frozen['environment_lock'])
    evidence['parent/unit-head-incremental.json']=base/'cinema-current-all-max-unit-head-incremental-v1.json'
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.writestr(name,(ROOT/name).read_bytes())
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    compact={'status':'INFEASIBLE','seconds':solution['seconds'],'feasible':False,'observed_node_l1':None,'candidate_created':False,
        'node_variables':819,'integer_variables':12993,'rounding_rows':12174,'allowed_tables':4058,'safe_rows':74081,
        'problem_sha256':solution['problem_sha256'],'model_proto_sha256':solution['model_proto_sha256'],'solution_sha256':sha(folder/'solution.json'),
        'process_peaks':solution['process_peaks'],'real_verify_executed':False,'native_or_photos_executed':False,'overall_upgrade':False,
        'scope':'唯一固定273节点±1/完整cap40表的CP状态，不具有独立形式证书，不推广旧±2或全局无解。'}
    (args.output/'summary.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    refs={}
    for field,stage in [('reused_unit_manifest','p16-cinema-current-all-max-unit-20261024'),('reused_current_full_quality_manifest','p16-cinema-current-full-quality-20261024')]:
        path=ROOT/'report/data'/stage/'manifest.json';refs[field]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    metadata={}
    for archive in ('source.zip','support-evidence.zip'):
        with zipfile.ZipFile(args.output/archive) as z:
            assert z.testzip() is None
            metadata[archive]={n:{'sha256':hashlib.sha256(z.read(n)).hexdigest(),'crc32':z.getinfo(n).CRC,'bytes':z.getinfo(n).file_size} for n in z.namelist()}
    manifest={'source_sha256':{n:sha(ROOT/n) for n in sorted(sources)},'support_member_sha256':{n:sha(path) for n,path in evidence.items()},
        'zip_member_metadata':metadata,**refs,'files':{path.name:sha(path) for path in args.output.iterdir()},
        'scope':'cap40唯一solver INFEASIBLE、预检/有限/独立数学审计和所有原始大JSON/PB/log；无candidate/验解/性能。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'files':len(manifest['files']),'source_members':len(sources),'support_members':len(evidence),'all_crc_sha_pass':True},flush=True)


if __name__=='__main__':main()
