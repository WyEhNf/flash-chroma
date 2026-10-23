"""封存训练尾部单扫、原始整数频数诊断和固定前缀覆盖下界。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists() and any(x.name!='README.md' for x in args.output.iterdir()):raise ValueError('不覆盖训练尾部封存')
    args.output.mkdir(parents=True,exist_ok=True);art=ROOT/'artifacts';out=args.output
    run=read(art/'cinema-training-tail-v1/run.json');frozen=read(art/'cinema-training-tail-frozen-v1/frozen.json')
    probe=read(art/'cinema-training-tail-probe-v1.json');bound=read(art/'cinema-training-bound-v1.json')
    expected=dict(run['sources'])
    expected.update({'scripts/certify_cinema_training_bound.py':bound['source_sha256'],
        'experiments/p16-cinema-training-bound-v1.json':bound['plan_sha256'],'scripts/archive_cinema_training_tail.py':sha(Path(__file__))})
    raw={};identity={}
    for name,value in frozen['sources'].items():
        if sha(ROOT/name)!=value['sha256'] or sha(art/'cinema-training-tail-frozen-v1/sources'/name)!=value['sha256']:raise AssertionError('构建前实际源已变：'+name)
    for name,digest in sorted(expected.items()):
        path=ROOT/name
        if sha(path)!=digest:raise AssertionError('实际执行源已变：'+name)
        old=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True);work=path.read_bytes()
        identity[name]={'execution_sha256':digest,'previous_head_sha256':hashlib.sha256(old.stdout).hexdigest() if old.returncode==0 else None,
            'same_as_previous_head':old.returncode==0 and old.stdout==work,'normalized_lf_equals_previous_head':old.returncode==0 and old.stdout.replace(b'\r\n',b'\n')==work.replace(b'\r\n',b'\n')}
        raw['execution-source/'+name]=path
    for path in sorted((art/'cinema-training-tail-v1').rglob('*')):
        if path.is_file():raw['results/cinema-training-tail-v1/'+path.relative_to(art/'cinema-training-tail-v1').as_posix()]=path
    for name in ('cinema-training-tail-probe-v1.json','cinema-training-tail-contract-v1.json','cinema-training-bound-v1.json'):
        raw['results/'+name]=art/name
    raw['results/pre-execution-frozen.json']=art/'cinema-training-tail-frozen-v1/frozen.json'
    members={}
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in sorted(raw.items()):archive.write(path,name);members[name]={'bytes':path.stat().st_size,'sha256':sha(path)}
    with zipfile.ZipFile(out/'evidence.zip') as archive:
        if archive.testzip() is not None:raise AssertionError('ZIP CRC失败')
        for name,value in members.items():
            data=archive.read(name)
            if len(data)!=value['bytes'] or hashlib.sha256(data).hexdigest()!=value['sha256']:raise AssertionError('ZIP原字节不符')
    for source,name in (('cinema-training-tail-probe-v1.json','probe.json'),('cinema-training-tail-contract-v1.json','finite-contract.json'),
        ('cinema-training-tail-v1/summary.json','summary.json'),('cinema-training-tail-v1/profile.json','profile.json'),('cinema-training-bound-v1.json','coverage-bound.json')):
        shutil.copyfile(art/source,out/name)
    save(out/'source-identity.json',identity)
    inputs={name:{**value,'uploaded':False} for name,value in probe['inputs'].items()}
    save(out/'manifest.json',{'evidence_sha256':sha(out/'evidence.zip'),'zip_members':members,'inherited_inputs':inputs,
        'scope':'单扫训练p99未变，未追加完整四级/native/百图/速度；覆盖下界未排除目标，不当可实现模型或终验。'})
    save(out/'execution-receipt.json',{'observed_exit_codes':{'probe':0,'finite_contract':0,'single_sweep':0,'coverage_bound':0},
        'training_strict_gate_passed':False,'counts':{'before':627527,'after':543481,'coverage_lower_bound':148154,'training_pixels':47185920},
        'new_native_or_photos_or_runtime_perf_executed':False,'raw_source_snapshot_verified':True,'git_head_blob_audit':'须后续逐路径核对，不能由ZIP核验替代。'})
    print({'zip_members':len(members),'source_files':len(expected),'zip_bytes':(out/'evidence.zip').stat().st_size},flush=True)


if __name__=='__main__':main()
