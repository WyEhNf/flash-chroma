"""唯一构建只读异常观察器；不修改290原库、不吞异常。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/p16-exception-probe-build-v1'
SOURCE=ROOT/'experiments/p16-exception-probe-v1/probe.cpp'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    if OUT.exists():raise FileExistsError('不覆盖诊断构建')
    OUT.mkdir(parents=True)
    compiler=Path('E:/mingw64/bin/g++.exe');dll=OUT/'libp16_exception_probe.dll'
    command=[str(compiler),'-O2','-std=c++17','-shared','-Wall','-Wextra',str(SOURCE),'-o',str(dll)]
    frozen={'purpose':'本进程首次AV的只读寄存器观察；不改原代码或控制流','source_sha256':sha(SOURCE),'builder_sha256':sha(__file__),'compiler_sha256':sha(compiler),'command':command,'python':sys.version,'performance_calls':0}
    (OUT/'source.cpp').write_bytes(SOURCE.read_bytes());(OUT/'builder.py').write_bytes(Path(__file__).read_bytes())
    (OUT/'frozen.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    env=os.environ.copy();env['PATH']='E:/mingw64/bin'+os.pathsep+env['PATH']
    result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,check=False)
    (OUT/'stdout.txt').write_bytes(result.stdout);(OUT/'stderr.txt').write_bytes(result.stderr)
    receipt={'returncode':result.returncode,'frozen_sha256':sha(OUT/'frozen.json'),'dll_sha256':sha(dll) if dll.exists() else None,'performance_calls':0}
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if result.returncode:raise RuntimeError('观察器构建失败，保留现场')
    print(json.dumps(receipt))

if __name__=='__main__':main()
