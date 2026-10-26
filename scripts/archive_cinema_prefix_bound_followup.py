"""封存局部MILP负例与独立整数原色对下界，保留实际执行源不改数值原件。"""
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


def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists() and any(f.name!='README.md' for f in a.output.iterdir()):raise ValueError('不覆盖下界阶段归档')
    a.output.mkdir(parents=True,exist_ok=True);art=ROOT/'artifacts';raw={};expected={}
    for filename in ('cinema-last-milp-v1-contract.json','cinema-arrival-pair-bound-v1.json'):
        path=art/filename;raw['results/'+filename]=path;expected.update(read(path)['source_sha256'])
    for path in (art/'cinema-last-milp-v1').iterdir():
        if path.is_file():raw['results/cinema-last-milp-v1/'+path.name]=path
    expected.update(read(art/'cinema-last-milp-v1/run.json')['source_sha256'])
    for name,value in expected.items():
        path=ROOT/name
        if sha(path)!=value:raise AssertionError('测量源已改变：'+name)
        raw['execution-source/'+name.replace('\\','/')]=path
    raw['execution-source/scripts/archive_cinema_prefix_bound_followup.py']=Path(__file__)
    members={}
    with zipfile.ZipFile(a.output/'evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,path in sorted(raw.items()):z.write(path,name);members[name]={'bytes':path.stat().st_size,'sha256':sha(path)}
    with zipfile.ZipFile(a.output/'evidence.zip') as z:
        if z.testzip():raise AssertionError('ZIP CRC不符')
        for name,v in members.items():
            b=z.read(name)
            if len(b)!=v['bytes'] or hashlib.sha256(b).hexdigest()!=v['sha256']:raise AssertionError('ZIP SHA不符')
    for name,path in [('milp-summary.json',art/'cinema-last-milp-v1/summary.json'),('pair-certificate.json',art/'cinema-arrival-pair-bound-v1.json')]:shutil.copyfile(path,a.output/name)
    save(a.output/'manifest.json',{'evidence_sha256':sha(a.output/'evidence.zip'),'members':members,
        'reused_complete_joint_evidence':'report/data/p16-cinema-arrival-budget-v1/evidence.zip',
        'scope':'不重复上传16M输入/参考/861行支撑；实际SHA及数学见证在run和证书，依赖前阶段完整域上界验证。'})
    save(a.output/'publication-audit.json',{'raw_files':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in a.output.iterdir() if f.is_file() and f.name!='README.md'},
        'zip_member_count':len(members),'zip_crc_and_sha_passed':True,'git_blob':'暂存后另检查，不预称通过'})
    print({'zip_members':len(members),'zip_bytes':(a.output/'evidence.zip').stat().st_size})


if __name__=='__main__':main()
