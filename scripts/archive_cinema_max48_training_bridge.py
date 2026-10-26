"""封存公共训练两预算桥安全表超门负例，不包含CP或候选。"""
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
    if args.output.exists():raise ValueError('不覆盖两训练预算桥负例归档')
    stage=ROOT/'artifacts/cinema-max48-training-bridge-census-v1';run=read(stage/'run.json');summary=read(stage/'summary.json')
    audit_path=ROOT/'artifacts/cinema-max48-training-bridge-independent-v1.json';audit=read(audit_path)
    if not audit['pass'] or audit['summary_sha256']!=sha(stage/'summary.json') or audit['classification_sha256']!=sha(stage/'classification.npz'):
        raise ValueError('不是已验两预算规模普查')
    if summary['within_resource_gates'] or summary['cp_model_built'] or summary['cp_solver_called'] or summary['new_rgb_queries']:
        raise ValueError('超门STOP边界不符')
    for name,expected in run['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('执行源已变：'+name)
    raw={'frozen.json':ROOT/'artifacts/cinema-max48-training-bridge-frozen-v1.json',
         'contract.json':ROOT/'artifacts/cinema-max48-training-bridge-contract-v1.json',
         'run.json':stage/'run.json','summary.json':stage/'summary.json','independent-audit.json':audit_path}
    if sha(raw['frozen.json'])!=run['frozen_sha256'] or sha(raw['contract.json'])!=run['contract_sha256']:raise ValueError('冻结/合同身份已变')
    args.output.mkdir(parents=True)
    for name,path in raw.items():shutil.copyfile(path,args.output/name)
    sources=set(run['source_sha256'])|{'scripts/archive_cinema_max48_training_bridge.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    evidence={'classification.npz':stage/'classification.npz','execution.log':ROOT/'artifacts/cinema-max48-training-bridge-execution-v1.log'}
    with zipfile.ZipFile(args.output/'support-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in evidence.items():z.write(path,name)
    reused={}
    for field,folder in (('reused_max48_risk_manifest','p16-cinema-max48-risk-upper-20261024'),('reused_quality_manifest','p16-cinema-max48-pareto-quality-20261024')):
        path=ROOT/'report/data'/folder/'manifest.json';reused[field]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    manifest={'source_sha256':{name:sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256':{name:sha(path) for name,path in evidence.items()},**reused,
        'files':{path.name:sha(path) for path in args.output.iterdir()},
        'scope':'公共best训练mean/p99桥唯一规模普查：13091点、608964安全行、12565成本/flag；安全行超预定500000门严格STOP，未建CP/新RGB查询/拟合/候选。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for archive,field in (('source.zip','source_sha256'),('support-evidence.zip','support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name,expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=expected:raise AssertionError('ZIP原字节SHA不符')
    print({'files':len(manifest['files']),'sources':len(sources),'support_members':len(evidence)},flush=True)


if __name__=='__main__':main()
