"""固定同一逻辑 CPU 复测，保留首次未固定亲和的全部记录。"""
from pathlib import Path
import datetime
import json
import os
import subprocess
import time
import psutil

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'artifacts/official-pr95-20261029'
parent=psutil.Process()
old=parent.cpu_affinity()
parent.cpu_affinity([0])
receipt={'started':datetime.datetime.now().isoformat(),'requested_affinity':[0],
         'parent_affinity':parent.cpu_affinity(),'psutil_version':psutil.__version__,'runs':[]}
env=os.environ.copy();env['PATH']='D:/codeblocks/MinGW/bin;'+env['PATH'];env['OMP_NUM_THREADS']='1'
try:
    for m in (17,33):
        env['FC_M']=str(m);env['FC_OUT']=f'artifacts/official-pr95-20261029/m{m}'
        cmd=['artifacts/official-pr95-20261029/official_adapter.exe','../../test/data','--extended']
        log=OUT/f'm{m}/extended-pinned.log';start=time.perf_counter()
        with log.open('wb') as f:
            child=subprocess.Popen(cmd,cwd=REPO,env=env,stdout=f,stderr=subprocess.STDOUT)
            affinity=psutil.Process(child.pid).cpu_affinity()
            assert affinity==[0], '子进程未继承预期亲和'
            rc=child.wait()
        row={'m':m,'command':cmd,'actual_child_affinity':affinity,'returncode':rc,'wall_seconds':time.perf_counter()-start,'log':str(log.relative_to(REPO))}
        receipt['runs'].append(row)
        (OUT/'run-pinned-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(row,ensure_ascii=False),flush=True)
        if rc:raise SystemExit(rc)
    receipt['completed']=True
    (OUT/'run-pinned-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
finally:
    parent.cpu_affinity(old)
