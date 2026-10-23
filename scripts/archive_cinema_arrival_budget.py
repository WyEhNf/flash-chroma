"""归档前缀下界检验、完整联合支撑与两次末级试验，逐字节核对执行来源。"""
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True)
    p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists() and any(f.name!='README.md' for f in args.output.iterdir()):raise ValueError('不覆盖本阶段归档')
    args.output.mkdir(parents=True,exist_ok=True);out=args.output;art=ROOT/'artifacts'
    first=read(art/'cinema-arrival-last-unit-v1/run.json');second=read(art/'cinema-arrival-last-budget-v1/run.json')
    prefix=read(art/'cinema-prefix-bound-v1/run.json');accept=read(art/'cinema-arrival-budget-accept-v1/results.json')
    expected={**first['sources'],**second['sources'],**second['previous_sources'],**prefix['source_sha256'],**accept['source_sha256']}
    source_paths={}
    for name,value in expected.items():
        path=ROOT/name
        if sha(path)!=value:raise AssertionError('执行源码已改变：'+name)
        source_paths[path.relative_to(ROOT).as_posix()]=path
    for name in ('scripts/audit_cinema_arrival_budget.py','scripts/archive_cinema_arrival_budget.py',
                 'scripts/inspect_tail_runtime_eligibility.py','python/lutlab/study_provenance.py',
                 'experiments/channel-runtime/channel_native.py'):
        source_paths[name]=ROOT/name
    source_identity={}
    for name,path in source_paths.items():
        work=path.read_bytes();old=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True)
        source_identity[name]={'execution_sha256':hashlib.sha256(work).hexdigest(),
            'previous_head_sha256':hashlib.sha256(old.stdout).hexdigest() if old.returncode==0 else None,
            'same_as_previous_head':old.returncode==0 and old.stdout==work,
            'normalized_lf_equals_previous_head':old.returncode==0 and work.replace(b'\r\n',b'\n')==old.stdout.replace(b'\r\n',b'\n')}
    if sha(args.library)!=accept['library_sha256']:raise AssertionError('所测87库不同')
    raw={}
    for folder in ('cinema-prefix-bound-v1','cinema-arrival-last-unit-v1','cinema-arrival-last-budget-v1',
                   'cinema-arrival-budget-audit-preflight-v1','cinema-arrival-budget-audit-preflight-v2'):
        for path in sorted((art/folder).rglob('*')):
            if path.is_file():raw[f'results/{folder}/{path.relative_to(art/folder).as_posix()}']=path
    for name in ('cinema-arrival-last-unit-v1-contract.json','cinema-arrival-budget-audit-v1.json','cinema-arrival-budget-eligibility-v1.json'):
        raw['results/'+name]=art/name
    raw['results/cinema-arrival-budget-accept-v1/results.json']=art/'cinema-arrival-budget-accept-v1/results.json'
    raw['results/a399-original-results.json']=args.cache_root/'artifacts/cinema-current-anchor-accept-v1/results.json'
    raw['models/previous-best-stage4.slut']=Path(first['inputs']['last']['path'])
    for k in (2,3):raw[f'models/selected-stage{k}.slut']=args.cache_root/f'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage{k}.slut'
    for name,path in source_paths.items():raw['execution-source/'+name]=path
    raw['measured-library/libjshc_direct_prepare_simd.dll']=args.library
    members={}
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in sorted(raw.items()):
            archive.write(path,name);members[name]={'bytes':path.stat().st_size,'sha256':sha(path)}
    with zipfile.ZipFile(out/'evidence.zip') as archive:
        if archive.testzip() is not None:raise AssertionError('ZIP CRC错误')
        for name,item in members.items():
            data=archive.read(name)
            if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise AssertionError('ZIP原字节不符')
    for name,path in [('accuracy-results.json',art/'cinema-arrival-budget-accept-v1/results.json'),
        ('budget-summary.json',art/'cinema-arrival-last-budget-v1/summary.json'),('unit-summary.json',art/'cinema-arrival-last-unit-v1/summary.json'),
        ('independent-audit.json',art/'cinema-arrival-budget-audit-v1.json'),('prefix-summary.json',art/'cinema-prefix-bound-v1/summary.json'),
        ('runtime-eligibility.json',art/'cinema-arrival-budget-eligibility-v1.json')]:shutil.copyfile(path,out/name)
    save(out/'source-identity.json',source_identity)
    excluded=[]
    for path in [art/'cinema-arrival-budget-accept-v1/candidate.rgb',*[Path(v['path']) for v in first['inputs'].values() if v['path'].endswith(('.npy','.rgb'))]]:
        excluded.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'reason':'大参考/输入或可重放完整流，保留本地不重复上传；输入身份已绑定，完整流可按终验命令恢复。'})
    save(out/'manifest.json',{'evidence_sha256':sha(out/'evidence.zip'),'zip_members':members,'excluded_large_inputs':excluded,
        'source_identity_file':'source-identity.json','scope':'完整原始试验和执行源码，无新性能；旧继承源码工作区CRLF与Git LF差异逐项保留，不改旧文件。'})
    note={'small_ball_contract':{'observed_tool_exit_code':0,'cases':120,'independent_python_integer_mismatches':0,
        'command':'python scripts/check_integer_rgb_ball.py'},
        'acceptance_command':'python scripts/accept_channel_tail_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --models artifacts/cinema-arrival-last-budget-v1 --modes candidate --suffix-stage4 artifacts/cinema-arrival-last-budget-v1/candidate/stage4.slut --baseline-cube artifacts/cinema-last-stage-accept-v1/candidate.rgb --library F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll --library-sha256 58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158 --output artifacts/cinema-arrival-budget-accept-v1',
        'acceptance_inputs_sha256':{name:value for name,value in first['inputs'].items()},
        'runtime_model_sha256':{name:sha(art/'cinema-arrival-last-budget-v1/candidate'/name) for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage4.slut')},
        'scope':'合同120项来自实际工具stdout记录；其余结果为上述ZIP原件。完整独立oracle/scalar1/AVX2请求4及100图已执行；真正分离/四情形吞吐另由速度分支验收。'}
    save(out/'execution-receipt.json',note)
    save(out/'publication-audit.json',{'raw_files':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(out.iterdir()) if f.is_file() and f.name!='README.md'},
        'zip_crc_and_all_member_sha_passed':True,'zip_member_count':len(members),'git_index_check':'暂存后必须另逐blob复核；本记录不预称已通过。'})
    print({'zip_members':len(members),'zip_bytes':(out/'evidence.zip').stat().st_size,'source_files':len(source_paths)},flush=True)


if __name__=='__main__':main()
