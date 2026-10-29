"""顺序执行官方框架和扩展验证，记录命令、环境与全部退出码。"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import subprocess
import time
import winreg

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'artifacts/official-pr95-20261029'
env=os.environ.copy()
env['PATH']='D:/codeblocks/MinGW/bin;'+env['PATH']
env['OMP_NUM_THREADS']='1'
env['OPENBLAS_NUM_THREADS']='1'
try:
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as k:
        cpu=winreg.QueryValueEx(k,'ProcessorNameString')[0]
except OSError:
    cpu=platform.processor()
receipt={'started':datetime.datetime.now().isoformat(),'platform':platform.platform(),'cpu':cpu,
         'logical_cpus':os.cpu_count(),'compiler':subprocess.check_output(['D:/codeblocks/MinGW/bin/g++.exe','--version'],text=True),
         'flags':['-O2','-DNDEBUG','-std=c++17','-Wall','-Wextra'],
         'openmp':False,'threads':1,'affinity':'未固定','frequency':'未锁频','runs':[]}
exe='artifacts/official-pr95-20261029/official_adapter.exe'
receipt['exe_sha256']=hashlib.sha256((REPO/exe).read_bytes()).hexdigest()
for m in (17,33):
    env['FC_M']=str(m)
    env['FC_OUT']=f'artifacts/official-pr95-20261029/m{m}'
    for mode in ('official','extended'):
        cmd=[exe,'../../test/data']+(['--extended'] if mode=='extended' else [])
        log=OUT/f'm{m}/{mode}.log'
        print(f'开始 m={m} {mode}',flush=True)
        start=time.perf_counter()
        with log.open('wb') as f:
            result=subprocess.run(cmd,cwd=REPO,env=env,stdout=f,stderr=subprocess.STDOUT)
        row={'m':m,'mode':mode,'command':cmd,'env':{'FC_M':str(m),'FC_OUT':env['FC_OUT'],'OMP_NUM_THREADS':'1'},'log':str(log.relative_to(REPO)),
             'returncode':result.returncode,'wall_seconds':time.perf_counter()-start}
        receipt['runs'].append(row)
        (OUT/'run-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(row,ensure_ascii=False),flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
receipt['completed']=True
receipt['finished']=datetime.datetime.now().isoformat()
(OUT/'run-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
