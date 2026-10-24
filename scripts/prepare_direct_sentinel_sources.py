"""冻结290手写源和288输入后，唯一生成新运行源；不构建、求值或计时。"""
from __future__ import annotations
import ast
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/p16-direct-sentinel-source-v1'

def sha(data: bytes) -> str:return hashlib.sha256(data).hexdigest()

def main() -> None:
    if OUT.exists():raise FileExistsError(f'拒绝覆盖冻结目录：{OUT}')
    old=ROOT/'experiments/p16-direct-u16-ilp-runtime'
    new=ROOT/'experiments/p16-direct-sentinel-runtime'
    paths=[Path(__file__),ROOT/'scripts/generate_direct_sentinel.py',ROOT/'AGENTS.md',ROOT/'experiments/p16-direct-sentinel-plan-v1.md']
    paths += [old/name for name in ('channel_runtime.cpp','compile_avx2.cpp','direct_u16_avx2.cpp','linear.cpp','andn_inplace.cpp','andn_outplace.cpp','normal_inplace.cpp','CMakeLists.txt')]
    paths += [new/name for name in ('direct_sentinel.hpp','sentinel_read_avx2.hpp','sentinel_prepare.hpp','contracts.cpp')]
    content={str(path.relative_to(ROOT)).replace('\\','/'):path.read_bytes() for path in paths}
    ast_records=[]
    for name,data in content.items():
        if name.endswith('.py'):
            parsed=ast.parse(data.decode('utf-8-sig'),filename=name)
            ast_records.append({'path':name,'nodes':sum(1 for _ in ast.walk(parsed)),'passed':True})
    OUT.mkdir(parents=True)
    for name,data in content.items():
        target=OUT/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    manifest={'status':'源冻结与生成，未构建或执行模型','utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'machine':platform.machine(),'sources':{name:{'sha256':sha(data),'bytes':len(data)} for name,data in content.items()},'ast':ast_records,'performance_calls':0}
    frozen=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')+b'\n'
    (OUT/'freeze.json').write_bytes(frozen)
    command=[sys.executable,str(ROOT/'scripts/generate_direct_sentinel.py')]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,check=False)
    (OUT/'generate-stdout.txt').write_bytes(result.stdout);(OUT/'generate-stderr.txt').write_bytes(result.stderr)
    (OUT/'execution.json').write_text(json.dumps({'command':command,'returncode':result.returncode,'freeze_sha256':sha(frozen),'performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if result.returncode:raise RuntimeError('生成失败，保留冻结源、日志及部分产物，禁止覆盖重跑')
    generated=json.loads((ROOT/'artifacts/p16-direct-sentinel-generated-v1.json').read_text(encoding='utf-8'))
    checks=[]
    for name,expected in generated['sources'].items():
        key=f'experiments/p16-direct-u16-ilp-runtime/{name}'
        checks.append(manifest['sources'][key]['sha256']==expected)
    for name,expected in generated['outputs'].items():
        data=(new/name).read_bytes();checks.append(sha(data)==expected)
        (OUT/'generated').mkdir(exist_ok=True);(OUT/'generated'/name).write_bytes(data)
    checks += [path.read_bytes()==content[str(path.relative_to(ROOT)).replace('\\','/')] for path in paths]
    if not all(checks):raise RuntimeError('冻结或生成后身份不符，保留失败现场')
    (OUT/'source-check.json').write_text(json.dumps({'passed':True,'checks':len(checks),'freeze_sha256':sha(frozen),'generated':generated['outputs'],'performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'source_count':len(content),'generated_count':len(generated['outputs']),'freeze_sha256':sha(frozen),'performance_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
