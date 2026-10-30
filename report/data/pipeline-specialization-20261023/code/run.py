"""冻结代码身份，先正确性、后两个串行独立计时进程；不自动重试。"""
from pathlib import Path
import subprocess,sys,json,hashlib
OUT=Path(__file__).resolve().parents[1]
lock=OUT/'run-lock.json'
if lock.exists():raise RuntimeError('已有运行记录，拒绝重复启动')
files=[OUT/'plan.json']+[OUT/'code'/name for name in ['kernels.py','study.py','run.py']]
lock.write_text(json.dumps(dict(files={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}),indent=2),encoding='utf8')
for name,args in [('verify',['verify']),('worker-0',['bench','--worker','0']),('worker-1',['bench','--worker','1'])]:
    print('开始',name,flush=True)
    with (OUT/(name+'.log')).open('wb') as log:
        subprocess.run([sys.executable,str(OUT/'code/study.py')]+args,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('完成',name,flush=True)
