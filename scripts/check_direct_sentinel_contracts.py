"""唯一执行290有限像素合同；核原冻结、真实DLL/EXE，不计性能或拟合精度。"""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'artifacts/p16-direct-sentinel-build-v1'
OUT=ROOT/'artifacts/p16-direct-sentinel-contracts-v1'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    if OUT.exists():raise FileExistsError('不覆盖有限合同现场')
    frozen_path=ROOT/'artifacts/p16-direct-sentinel-build-frozen-v1/frozen.json'
    frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    build=json.loads((BUILD/'build-check.json').read_text(encoding='utf-8'))
    if not build['passed'] or build['frozen_sha256']!=sha(frozen_path):raise ValueError('构建审计不符')
    for name,row in frozen['sources'].items():
        if sha(ROOT/name)!=row['sha256']:raise ValueError('冻结源变更：'+name)
    dll=BUILD/'libjshc_direct_sentinel.dll';exe=BUILD/'p16_direct_sentinel_contracts.exe'
    if sha(dll)!=build['dll_sha256'] or sha(exe)!=build['contract_sha256']:raise ValueError('构建产物变更')
    env=os.environ.copy();env['PATH']='E:/mingw64/bin'+os.pathsep+env['PATH'];env['OMP_NUM_THREADS']='1'
    OUT.mkdir(parents=True)
    protocol={'purpose':'有限格式/像素核正确性，不是全域模型精度或速度','utc':datetime.now(timezone.utc).isoformat(),'checker_sha256':sha(__file__),'python':sys.version,'platform':platform.platform(),'frozen_sha256':sha(frozen_path),'dll_sha256':sha(dll),'contract_sha256':sha(exe),'selection_cases':9,'compile_id_cases':3,'scalar_cases':80,'guarded_cases_allowed':[380,1520],'expected_mismatches':0,'performance_calls':0}
    (OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result=subprocess.run([str(exe)],cwd=ROOT,env=env,capture_output=True,check=False)
    (OUT/'stdout.txt').write_bytes(result.stdout);(OUT/'stderr.txt').write_bytes(result.stderr)
    (OUT/'execution.json').write_text(json.dumps({'command':[str(exe)],'returncode':result.returncode,'protocol_sha256':sha(OUT/'protocol.json'),'performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if result.returncode:raise RuntimeError('有限合同失败；保留原始源/输出，禁止覆盖或按成功处理')
    actual=json.loads(result.stdout.decode('utf-8'))
    if not actual['passed'] or actual['performance_calls']!=0:raise ValueError('合同状态不符')
    for name in ('selection_cases','compile_id_cases','scalar_cases'):
        if actual[name]!=protocol[name]:raise ValueError('有限覆盖数量不同：'+name)
    if actual['guarded_cases'] not in protocol['guarded_cases_allowed']:raise ValueError('guard覆盖数量不同')
    for name,row in frozen['sources'].items():
        if sha(ROOT/name)!=row['sha256']:raise ValueError('执行后冻结源变更：'+name)
    if sha(dll)!=build['dll_sha256'] or sha(exe)!=build['contract_sha256']:raise ValueError('执行后产物变更')
    (OUT/'results.json').write_text(json.dumps({'passed':True,'contract':actual,'protocol_sha256':sha(OUT/'protocol.json'),'sources_unchanged':len(frozen['sources']),'dll_unchanged':True,'performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'contract':actual,'sources_unchanged':len(frozen['sources']),'performance_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
