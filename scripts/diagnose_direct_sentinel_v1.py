"""隔离已失败256夹具的六后端/路径；只定位，不改原DLL或升级失败资格。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts')]
from check_direct_sentinel_native import BUILD,Library,sha,info,to,direct_table,palette
import numpy as np

OUT=ROOT/'artifacts/p16-direct-sentinel-diagnose-v1'
DLL_SHA='f54a505f128e515e165c9a13676d2f186939db7fefb7ea040d1aee2d15edd45a'

def child(case):
    dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(BUILD))]
    dll=BUILD/'libjshc_direct_sentinel.dll';assert sha(dll)==DLL_SHA
    directory=ROOT/'artifacts/p16-direct-sentinel-quality-v1/synthetic'
    models=[directory/'256-first.slut',*[directory/'256-tail.slut']*3]
    sides=[directory/'side.bin',None,None,None]
    library=Library(dll,DLL_SHA);kernel,threads,route=case.split(':');threads=int(threads)
    sample=np.concatenate((np.random.default_rng(2026102416).integers(0,256,(4096,3),dtype=np.uint8),np.array([[0,0,0],[255,255,255]],np.uint8)))
    with library.chain(models,sides) as chain:
        table=direct_table(chain).view(np.uint8);hot=palette(chain)
        state={'case':case,'info':info(chain),'table_sha256':hashlib.sha256(table).hexdigest(),'palette_sha256':hashlib.sha256(hot).hexdigest(),'id_counts':np.bincount(table[:-4],minlength=256).tolist(),'guard_zero':bool(np.all(table[-4:]==0))}
        print(json.dumps({'before_call':state}),flush=True)
        try:
            actual=chain.apply(sample.copy(),kernel=kernel,threads=threads) if route=='inplace' else to(chain,sample,kernel,threads)
        except Exception as error:
            print(json.dumps({'case':case,'exception_type':type(error).__name__,'error':str(error)}),flush=True);return 1
        print(json.dumps({'case':case,'output_sha256':hashlib.sha256(actual).hexdigest(),'exception':False}),flush=True)
    return 0

def parent():
    if OUT.exists():raise FileExistsError('不覆盖定位现场')
    frozen_path=ROOT/'artifacts/p16-direct-sentinel-quality-frozen-v1/frozen.json'
    frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    for name,expected in frozen['sources_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('原失败源身份变更')
    directory=ROOT/'artifacts/p16-direct-sentinel-quality-v1/synthetic'
    inputs=[directory/name for name in ('256-first.slut','256-tail.slut','side.bin')]
    OUT.mkdir(parents=True)
    protocol={'purpose':'六独立子进程定位原256合成夹具异常，不覆盖失败、不构建、不计时','checker_sha256':sha(__file__),'quality_frozen_sha256':sha(frozen_path),'dll_sha256':DLL_SHA,'inputs_sha256':{str(path):sha(path) for path in inputs},'cases':[f'{kernel}:{threads}:{route}' for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)] for route in ('inplace','to')],'performance_calls':0}
    (OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'checker.py').write_bytes(Path(__file__).read_bytes())
    env=os.environ.copy();env['PATH']='E:/mingw64/bin'+os.pathsep+env['PATH'];env['PYTHONIOENCODING']='utf-8'
    rows=[]
    for index,case in enumerate(protocol['cases']):
        result=subprocess.run([sys.executable,str(Path(__file__)),'--case',case],cwd=ROOT,env=env,capture_output=True,check=False)
        (OUT/f'{index}-stdout.txt').write_bytes(result.stdout);(OUT/f'{index}-stderr.txt').write_bytes(result.stderr)
        rows.append({'case':case,'returncode':result.returncode,'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()})
    (OUT/'results.json').write_text(json.dumps({'diagnosis_completed':True,'rows':rows,'performance_calls':0,'original_quality_passed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':rows,'performance_calls':0}))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case');args=parser.parse_args()
    if args.case:raise SystemExit(child(args.case))
    parent()

if __name__=='__main__':main()
