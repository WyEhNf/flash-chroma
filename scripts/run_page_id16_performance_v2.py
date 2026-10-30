"""仅执行冻结v2双阶段四fresh/1232调用及6RSS一次，保留所有失效，不补跑。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-id16-performance-v2.json'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output=args.output.resolve()
    plan=json.loads(PLAN.read_text(encoding='utf-8'))
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('正式启动前源/输入改变STOP')
    args.output.mkdir(parents=True,exist_ok=False)
    rows=[]
    environment=os.environ.copy()
    environment.update(OMP_NUM_THREADS='4',OMP_DYNAMIC='FALSE',OPENBLAS_NUM_THREADS='1')
    jobs=[('worker'+str(index),['--worker',str(index)]) for index in range(4)]+[('rss-'+role,['--rss',role]) for role in plan['roles']]
    for label,arguments in jobs:
        command=[sys.executable,str(ROOT/'scripts/bench_page_id16_v2.py'),*arguments,'--output',str(args.output/label)]
        print('开始唯一P4双阶段正式进程：'+label,flush=True)
        started=time.perf_counter()
        value=subprocess.run(command,cwd=ROOT,env=environment,text=True,capture_output=True)
        rows.append(dict(label=label,command=command,returncode=value.returncode,wall_seconds=time.perf_counter()-started,stdout=value.stdout,stderr=value.stderr))
        (args.output/'driver.json').write_text(json.dumps(dict(plan_sha256=sha(PLAN),passed=False,jobs=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(dict(label=label,returncode=value.returncode,stdout=value.stdout[-1000:],stderr=value.stderr[-2000:]),flush=True)
        if value.returncode:raise RuntimeError('唯一正式进程失败STOP：'+label)
    (args.output/'driver.json').write_text(json.dumps(dict(plan_sha256=sha(PLAN),passed=True,jobs=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(dict(passed=True,workers=4,calls=1232,rss_processes=6),flush=True)

if __name__=='__main__':main()
