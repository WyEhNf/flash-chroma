"""freestanding C99→wasm32实际执行门禁；无C++/OpenMP/SIMD/分配器依赖。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--roms',type=Path,required=True);p.add_argument('--cube',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--clang',default='C:/Program Files/LLVM/bin/clang.exe');p.add_argument('--node',default='node')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    support=ROOT/'experiments/memory-rom-wasm';core=ROOT/'experiments/memory-rom'
    cmd=[a.clang,'--target=wasm32','-std=c99','-O3','-ffreestanding','-fno-builtin','-nostdlib',
         '-I'+str(support/'include'),'-I'+str(core),str(core/'memory_rom.c'),
         str(support/'harness.c'),str(support/'minilib.c'),'-Wl,--no-entry','-Wl,--export-all',
         '-Wl,--initial-memory=33554432','-Wl,--max-memory=33554432','-Wl,-z,stack-size=65536',
         '-o',str(out/'memory_rom.wasm')]
    run=subprocess.run(cmd,capture_output=True,text=True)
    (out/'build.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    metadata={'purpose':__doc__,'platform':platform.platform(),'python':sys.version,'command':cmd,
              'build_returncode':run.returncode,'compiler':subprocess.run([a.clang,'--version'],capture_output=True,text=True).stdout,
              'source_sha256':{str(f.relative_to(ROOT)):sha(f) for f in [core/'memory_rom.c',core/'memory_rom.h',support/'harness.c',support/'minilib.c',support/'include/string.h',support/'verify.cjs',Path(__file__)]}}
    (out/'run.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run.check_returncode()
    test=[a.node,str(support/'verify.cjs'),str(out/'memory_rom.wasm'),str(a.roms.resolve()),str(a.cube.resolve()),str(out/'results.json')]
    result=subprocess.run(test,capture_output=True,text=True,encoding='utf-8')
    (out/'test.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    result.check_returncode();print(result.stdout)
if __name__=='__main__':main()
