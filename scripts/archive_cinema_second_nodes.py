"""封存第二级两候选质量/资格/前缀证书，核对完整原件及执行源SHA。"""
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists() and any(path.name!='README.md' for path in args.output.iterdir()):raise ValueError('不覆盖第二级阶段原件')
    args.output.mkdir(parents=True,exist_ok=True);out=args.output;art=ROOT/'artifacts';study=art/'cinema-second-nodes-v1'
    run=read(study/'run.json');expected=dict(run['sources'])
    expected.update(read(art/'cinema-second-nodes-v1-contract.json')['sources'])
    expected.update(read(art/'cinema-second-palette-v1.json')['sources'])
    expected.update(read(art/'cinema-second-bound-v1.json')['source_sha256'])
    for mode in ('max_first','p99_first'):expected.update(read(art/f'cinema-second-accept-{mode}-v1/identity.json')['sources'])
    expected['scripts/audit_cinema_second_nodes.py']=read(art/'cinema-second-nodes-audit-v1.json')['source_sha256']
    expected['scripts/archive_cinema_second_nodes.py']=sha(Path(__file__))
    source_identity={};raw={}
    for name,value in sorted(expected.items()):
        path=ROOT/name
        if sha(path)!=value:raise AssertionError('实际执行源变更：'+name)
        work=path.read_bytes();previous=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True)
        source_identity[name]={'execution_sha256':value,'previous_head_sha256':hashlib.sha256(previous.stdout).hexdigest() if previous.returncode==0 else None,
            'same_as_previous_head':previous.returncode==0 and previous.stdout==work,
            'normalized_lf_equals_previous_head':previous.returncode==0 and previous.stdout.replace(b'\r\n',b'\n')==work.replace(b'\r\n',b'\n')}
        raw['execution-source/'+name]=path
    for path in sorted(study.rglob('*')):
        if path.is_file():raw['results/cinema-second-nodes-v1/'+path.relative_to(study).as_posix()]=path
    for name in ('cinema-second-nodes-v1-contract.json','cinema-second-nodes-audit-v1.json','cinema-second-palette-v1.json','cinema-second-bound-v1.json'):
        raw['results/'+name]=art/name
    for mode in ('max_first','p99_first'):
        folder=art/f'cinema-second-accept-{mode}-v1'
        for name in ('identity.json','results.json'):raw[f'results/{folder.name}/{name}']=folder/name
    # 老87是已冻结的外部分支实测二进制，本阶段不虚构重编译；保留原件供质量重放。
    if sha(args.library)!='58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158':raise ValueError('所测87库不同')
    raw['measured-library/libjshc_direct_prepare_simd.dll']=args.library
    for name in ('stage2','stage3','last'):raw['baseline-models/'+name+'.slut']=Path(run['inputs'][name]['path'])
    members={}
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in sorted(raw.items()):
            archive.write(path,name);members[name]={'bytes':path.stat().st_size,'sha256':sha(path)}
    with zipfile.ZipFile(out/'evidence.zip') as archive:
        if archive.testzip() is not None:raise AssertionError('ZIP CRC错误')
        for name,value in members.items():
            data=archive.read(name)
            if len(data)!=value['bytes'] or hashlib.sha256(data).hexdigest()!=value['sha256']:raise AssertionError('ZIP原字节不符')
    copies={'fit-summary.json':study/'summary.json','profile.json':study/'profile.json',
        'independent-audit.json':art/'cinema-second-nodes-audit-v1.json','palette-eligibility.json':art/'cinema-second-palette-v1.json',
        'prefix-bound.json':art/'cinema-second-bound-v1.json'}
    for mode in ('max_first','p99_first'):copies[mode+'-accuracy.json']=art/f'cinema-second-accept-{mode}-v1/results.json'
    for name,path in copies.items():shutil.copyfile(path,out/name)
    save(out/'source-identity.json',source_identity)
    excluded=[]
    for path in [*[Path(row['path']) for row in run['inputs'].values() if row['path'].endswith(('.npy','.rgb'))],
        *[art/f'cinema-second-accept-{mode}-v1/candidate.rgb' for mode in ('max_first','p99_first')]]:
        excluded.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),
            'reason':'大完整输入/真值/可重放输出，保留本地，不重复上传；SHA与重放命令绑定。'})
    save(out/'manifest.json',{'evidence_sha256':sha(out/'evidence.zip'),'zip_members':members,'excluded_large_inputs':excluded,
        'source_identity_file':'source-identity.json','scope':'本阶段只交付两候选精度和旧87资格；无新吞吐/16bit内核成绩；两个候选均未升级综合best。'})
    save(out/'execution-receipt.json',{'observed_exit_codes':{'finite_contract':0,'two_mode_fit':0,'max_first_full_accept':0,
        'p99_first_full_accept':0,'independent_audit':0,'old87_palette_eligibility':0,'prefix_bound':0},
        'finite_contract':{'random_selector_cases':512,'constructed_priority_cases':2,'reject_cases':3},
        'diagnostic_preflight':{'command':'提取逐图恶化的临时stdlib命令','observed_exit_code':1,
            'reason':'Path.read_text未指定UTF-8，Windows默认GBK解码失败；显式encoding=utf-8后退出0。未改拟合、验收、审计的源/参数/原始数据。'},
        'performance':'未执行；prepare_seconds仅资格描述，不可作为受控性能。16bit runtime仍是后续独立研究。',
        'old87_provenance':'实测DLL与上一Cinema末级验收完全相同；原构建源/编译记录见速度PR89及其冻结87阶段，不声称本阶段重编译。'})
    save(out/'publication-audit.json',{'raw_files':{path.name:{'bytes':path.stat().st_size,'sha256':sha(path)} for path in sorted(out.iterdir()) if path.is_file() and path.name!='README.md'},
        'zip_crc_and_all_member_sha_passed':True,'zip_member_count':len(members),'git_blob_check':'须暂存后另核，未预称通过。'})
    print({'zip_members':len(members),'source_files':len(expected),'zip_bytes':(out/'evidence.zip').stat().st_size},flush=True)


if __name__=='__main__':main()
