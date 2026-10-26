"""保留新第二级后的末级单扫和有界MILP负例，不把未晋级拟合当终验。"""
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
    if args.output.exists() and any(path.name!='README.md' for path in args.output.iterdir()):raise ValueError('不覆盖两项补充研究封存')
    args.output.mkdir(parents=True,exist_ok=True);out=args.output;art=ROOT/'artifacts'
    post=read(art/'cinema-post-second-last-v1/run.json');milp=read(art/'cinema-second-milp-v1/run.json')
    contract=read(art/'cinema-second-milp-v1-contract.json')
    expected={**post['sources'],**milp['source_sha256'],**milp['prior_sources'],**contract['source_sha256']}
    expected['scripts/archive_cinema_second_refinement.py']=sha(Path(__file__));raw={};identities={}
    for name,digest in sorted(expected.items()):
        path=ROOT/name
        if sha(path)!=digest:raise AssertionError('实际执行源已变：'+name)
        work=path.read_bytes();previous=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True)
        identities[name]={'execution_sha256':digest,'previous_head_sha256':hashlib.sha256(previous.stdout).hexdigest() if previous.returncode==0 else None,
            'same_as_previous_head':previous.returncode==0 and previous.stdout==work,
            'normalized_lf_equals_previous_head':previous.returncode==0 and previous.stdout.replace(b'\r\n',b'\n')==work.replace(b'\r\n',b'\n')}
        raw['execution-source/'+name]=path
    for folder in ('cinema-post-second-last-v1','cinema-second-milp-v1'):
        for path in sorted((art/folder).rglob('*')):
            if path.is_file():raw['results/'+folder+'/'+path.relative_to(art/folder).as_posix()]=path
    raw['results/cinema-second-milp-v1-contract.json']=art/'cinema-second-milp-v1-contract.json'
    members={}
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in sorted(raw.items()):
            archive.write(path,name);members[name]={'bytes':path.stat().st_size,'sha256':sha(path)}
    with zipfile.ZipFile(out/'evidence.zip') as archive:
        if archive.testzip() is not None:raise AssertionError('ZIP CRC失败')
        for name,value in members.items():
            data=archive.read(name)
            if len(data)!=value['bytes'] or hashlib.sha256(data).hexdigest()!=value['sha256']:raise AssertionError('ZIP原件不符')
    for name,path in {'post-summary.json':art/'cinema-post-second-last-v1/summary.json',
        'post-profile.json':art/'cinema-post-second-last-v1/profile.json','milp-summary.json':art/'cinema-second-milp-v1/summary.json',
        'finite-contract.json':art/'cinema-second-milp-v1-contract.json'}.items():shutil.copyfile(path,out/name)
    save(out/'source-identity.json',identities)
    references=[]
    for path in (art/'cinema-second-nodes-v1/joint-support.npz',art/'cinema-second-accept-max_first-v1/candidate.rgb',
        ROOT/'report/data/p16-cinema-second-nodes-v1/manifest.json'):
        references.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),
            'reason':'继承完整域支撑/输出或其已提交manifest；不重复打包，原阶段SHA和本次起点验证绑定。'})
    save(out/'manifest.json',{'evidence_sha256':sha(out/'evidence.zip'),'zip_members':members,'inherited_inputs':references,
        'scope':'两次各自预注册的独立离线研究，均未晋级新完整域/native/百图/速度，不填写这些未测结论。'})
    save(out/'execution-receipt.json',{'observed_exit_codes':{'post_second_last_single_sweep':0,'parameterized_finite_contract':0,'bounded_milp':0},
        'post_gate':{'max_first':False,'p99_first':False,'reason':'mean改善但p99/max均相同，未通过严格尾部晋级门'},
        'milp':{'status':1,'time_limit_seconds':20,'incumbent':False,'iterations_executed':1,'reason':'达到首轮冻结时限，无incumbent立即停；未加轮/扩大节点盒，非不可行证明'},
        'environment_note':'Windows/Ryzen/Python3.12.14/NumPy1.26.4/Numba0.60/SciPy1.15.2；质量/拟合期间其他代理构建或封存，不以过程seconds作为运行时性能。'})
    save(out/'publication-audit.json',{'raw_files':{path.name:{'bytes':path.stat().st_size,'sha256':sha(path)} for path in sorted(out.iterdir()) if path.is_file() and path.name!='README.md'},
        'zip_crc_and_member_sha_passed':True,'zip_members':len(members),'git_blob_check':'须后续逐blob核验，不由本ZIP核对代替。'})
    print({'zip_members':len(members),'source_files':len(expected),'zip_bytes':(out/'evidence.zip').stat().st_size},flush=True)


if __name__=='__main__':main()
