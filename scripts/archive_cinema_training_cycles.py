"""封存最多四轮训练尾部搜索的全部扫次，保留停止与未晋级结论。"""
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists() and any(x.name!='README.md' for x in a.output.iterdir()):raise ValueError('不覆盖四轮训练封存')
    a.output.mkdir(parents=True,exist_ok=True);art=ROOT/'artifacts';out=a.output;run=read(art/'cinema-training-cycles-v1/run.json')
    frozen=read(art/'cinema-training-cycles-frozen-v1/frozen.json');expected={**run['sources'],'scripts/archive_cinema_training_cycles.py':sha(Path(__file__))}
    for name,value in frozen['sources'].items():
        if sha(ROOT/name)!=value['sha256'] or sha(art/'cinema-training-cycles-frozen-v1/sources'/name)!=value['sha256']:raise AssertionError('执行前原字节已变：'+name)
    raw={};identity={}
    for name,digest in sorted(expected.items()):
        path=ROOT/name
        if sha(path)!=digest:raise AssertionError('实际源已变：'+name)
        old=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True);work=path.read_bytes()
        identity[name]={'execution_sha256':digest,'previous_head_sha256':hashlib.sha256(old.stdout).hexdigest() if old.returncode==0 else None,
            'same_as_previous_head':old.returncode==0 and old.stdout==work,'normalized_lf_equals_previous_head':old.returncode==0 and old.stdout.replace(b'\r\n',b'\n')==work.replace(b'\r\n',b'\n')}
        raw['execution-source/'+name]=path
    for path in sorted((art/'cinema-training-cycles-v1').rglob('*')):
        if path.is_file():raw['results/'+path.relative_to(art).as_posix()]=path
    raw['results/pre-execution-frozen.json']=art/'cinema-training-cycles-frozen-v1/frozen.json';members={}
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in sorted(raw.items()):z.write(path,name);members[name]={'bytes':path.stat().st_size,'sha256':sha(path)}
    with zipfile.ZipFile(out/'evidence.zip') as z:
        if z.testzip() is not None:raise AssertionError('ZIP CRC失败')
        for name,value in members.items():
            data=z.read(name)
            if len(data)!=value['bytes'] or hashlib.sha256(data).hexdigest()!=value['sha256']:raise AssertionError('ZIP原字节不符')
    for name in ('run.json','summary.json','sweeps.json'):shutil.copyfile(art/'cinema-training-cycles-v1'/name,out/name)
    save(out/'source-identity.json',identity)
    references=[art/'cinema-training-tail-v1/run.json',art/'cinema-training-tail-contract-v1.json',art/'cinema-training-tail-probe-v1.json',
        ROOT/'report/data/p16-cinema-training-tail-v1/manifest.json']
    save(out/'manifest.json',{'evidence_sha256':sha(out/'evidence.zip'),'zip_members':members,
        'inherited_inputs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'uploaded':False} for p in references],
        'scope':'同一原起点最多四扫次，全部保留；最后训练计数停滞未达到p99严格门，未追加native/百图/速度。'})
    save(out/'execution-receipt.json',{'observed_exit_code':0,'sweeps_executed':4,'batches_executed':32,
        'training_above_11_by_sweep':[543481,513681,509581,509581],'eligible_for_independent_final_checks':False,
        'stop_reason':'第四完整扫次训练计数未严格减少；同时达到预注册最多四扫次，未补轮或换目标',
        'new_native_or_photos_or_runtime_perf_executed':False,'raw_frozen_sources_verified':True,'git_head_blob_audit':'须后续单独核对'})
    print({'zip_members':len(members),'source_files':len(expected),'zip_bytes':(out/'evidence.zip').stat().st_size},flush=True)


if __name__=='__main__':main()
