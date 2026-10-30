"""copy4唯一两步质量驱动：build先过机器码门，再手动授已批准quality，不补跑。"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from page_id16_copy4_common import ROOT,PLAN,checked_plan,sha,save
from study_memory_rom import read

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step',choices=('build','quality'),required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    plan=checked_plan()
    output=args.output.resolve()
    if args.step=='build':
        output.mkdir(parents=True,exist_ok=False)
        previous=[]
        command=[sys.executable,str(ROOT/'scripts/build_page_id16_copy4.py'),'--output',str(output/'build')]
    else:
        previous=read(output/'run.json')['jobs']
        if len(previous)!=1 or previous[0]['label']!='build' or previous[0]['returncode'] or not read(output/'build/machine-code-gate.json')['passed'] or (output/'quality').exists():raise AssertionError('唯一质量前置/原件不同')
        built=read(output/'build/build.json')
        if built['plan_sha256']!=sha(PLAN) or any(sha(output/'build'/name)!=value['sha256'] for name,value in built['outputs'].items()):raise AssertionError('实际新库/对象改变')
        command=[sys.executable,str(ROOT/'scripts/verify_page_id16_copy4.py'),'--rom',plan['page_rom'],'--build',str(output/'build'),'--output',str(output/'quality')]
    environment=os.environ.copy()
    environment.update(OMP_NUM_THREADS='4',OMP_DYNAMIC='FALSE',OPENBLAS_NUM_THREADS='1')
    started=time.perf_counter()
    value=subprocess.run(command,cwd=ROOT,env=environment,text=True,capture_output=True,encoding='utf-8',errors='replace')
    row=dict(label=args.step,command=command,returncode=value.returncode,wall_seconds=time.perf_counter()-started,stdout=value.stdout,stderr=value.stderr)
    jobs=previous+[row]
    save(output/'run.json',dict(plan_sha256=sha(PLAN),jobs=jobs,build_passed=jobs[0]['returncode']==0,passed=args.step=='quality' and value.returncode==0,scope='只一次build和一次质量；wall是流程观察，不是性能。首错误保留STOP，不覆盖目录或重采。'))
    print(dict(step=args.step,returncode=value.returncode,stdout=value.stdout[-3000:],stderr=value.stderr[-3000:]),flush=True)
    if value.returncode:raise RuntimeError('copy4唯一阶段失败STOP：'+args.step)

if __name__=='__main__':main()
