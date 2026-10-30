"""冻结81静态失败证据；仅复制/核对字节，不执行候选原生代码。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'report/data/skylake-input256-v1'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def main():
    plan_path=ROOT/'experiments/skylake-input256-v1.json';plan=read(plan_path)
    build_path=ROOT/'artifacts/skylake-input256-linux-build-v1';build=read(build_path/'build.json')
    static_path=ROOT/'artifacts/skylake-input256-static-v1'
    initial=read(static_path/'results.json');result=read(static_path/'results-v2.json')
    independent=read(static_path/'independent_results.json')
    assert not initial['accepted'] and not result['accepted'] and not independent['accepted']
    assert result['failure_reason']==['input256/64/no_stack']
    assert build['plan_sha256']==sha(plan_path)==result['plan_sha256']
    assert result['build_sha256']==sha(build_path/'build.json')
    assert build['source_sha256']==plan['source_sha256']
    assert all(sha(ROOT/p)==h for p,h in plan['source_sha256'].items())
    assert build['libraries']['reference']['sha256']=='b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e'
    assert all(sha(Path(s['path'].replace('/mnt/f/','F:/')))==s['sha256'] for s in build['libraries'].values())
    assert not HERE.exists(),'不得覆盖档案'
    HERE.mkdir(parents=True)
    files=[]
    target=HERE/'skylake-input256-linux-build-v1';target.mkdir()
    chosen=['build.json','build-log.json','compile_commands.json','libraries-Release.json','measured-source.zip',*sorted(p.name for p in build_path.glob('libjshc*.so'))]
    for name in chosen:shutil.copy2(build_path/name,target/name)
    with zipfile.ZipFile(target/'build-intermediates.zip','w',zipfile.ZIP_DEFLATED) as stream:
        for p in sorted(build_path.rglob('*')):
            if p.is_file() and p.name not in chosen:stream.write(p,p.relative_to(build_path).as_posix())
    files.extend(p for p in target.rglob('*') if p.is_file())
    for name in ('skylake-input256-static-v1','skylake-input256-preflight-v1'):
        shutil.copytree(ROOT/'artifacts'/name,HERE/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        files.extend(p for p in (HERE/name).rglob('*') if p.is_file())
    for name in ('prepare_input256_glue.py','archive_input256_static.py','audit_input256_delivery.py'):
        dest=HERE/'skylake-input256-preflight-v1'/('root-'+name)
        shutil.copy2(ROOT/'artifacts'/name,dest);files.append(dest)
    save(HERE/'manifest.json',{'schema':1,'files':{p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)}})
    cube_sources={p:sha(ROOT/p) for p in plan['source_sha256']}
    with zipfile.ZipFile(target/'measured-source.zip') as stream:
        for p,h in cube_sources.items():assert hashlib.sha256(stream.read(p)).hexdigest()==h
        assert stream.read(plan_path.relative_to(ROOT).as_posix())==plan_path.read_bytes()
    save(HERE/'audit.json',dict(purpose=__doc__,pass_check=True,source_entries=len(cube_sources),manifest_files=len(files),
        plan_sha256=sha(plan_path),build_sha256=sha(build_path/'build.json'),static_sha256=sha(static_path/'results-v2.json'),
        independent_sha256=sha(static_path/'independent_results.json'),accepted=False,
        stopping_reason='完整64像素区段出现真实32B栈spill与reload，原无热区栈门槛未过。',
        full_rgb8_executed=False,performance_executed=False,confirmation_executed=False,candidate_library_loads=0,pixel_calls=0,performance_calls=0))
    print(json.dumps({'manifest_files':len(files),'source_entries':len(cube_sources),'accepted':False},ensure_ascii=False))

if __name__=='__main__':main()
