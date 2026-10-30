"""单次串行导出/构建/完整质量，任何失败保留原件STOP，不运行吞吐。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-id16-runtime-v1.json'
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();plan=json.loads(PLAN.read_text(encoding='utf-8'))
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('启动前冻结源/原件不同')
    a.output.mkdir(parents=True,exist_ok=False);jobs=[('export',['scripts/export_page_id16.py','--output',str(a.output/'rom')]),('build',['scripts/build_page_id16.py','--output',str(a.output/'build')]),('quality',['scripts/verify_page_id16.py','--rom',str(a.output/'rom/page-id16.bin'),'--build',str(a.output/'build'),'--output',str(a.output/'quality')])];environment=os.environ.copy();environment.update(OMP_NUM_THREADS='4',OMP_DYNAMIC='FALSE',OPENBLAS_NUM_THREADS='1');rows=[]
    for label,args in jobs:
        print('开始单版P4质量：'+label,flush=True);started=time.perf_counter();value=subprocess.run([sys.executable,*args],cwd=ROOT,env=environment,text=True,capture_output=True);elapsed=time.perf_counter()-started;row=dict(label=label,command=[sys.executable,*args],returncode=value.returncode,stdout=value.stdout,stderr=value.stderr,wall_seconds=elapsed);rows.append(row)
        result=dict(passed=False,plan_sha256=sha(PLAN),jobs=rows,scope='只质量，任何失败原样STOP；wall为执行环境观察，不给速度档。');(a.output/'run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(label=label,returncode=value.returncode,stdout=value.stdout[-1200:],stderr=value.stderr[-2500:]),flush=True)
        if value.returncode:raise RuntimeError('唯一P4'+label+'失败，保留原件，不修后重采')
    quality=json.loads((a.output/'quality/results.json').read_text(encoding='utf-8'));result.update(passed=bool(quality['passed']),actual_rom_bytes=quality['actual_rom_bytes'],actual_model_bytes=quality['actual_model_bytes'],actual_capacity=quality['actual_capacity'],net_saving=quality['net_saving'],ready_for_performance_proposal=True);(a.output/'run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print({key:result[key] for key in ('passed','actual_rom_bytes','actual_model_bytes','actual_capacity','net_saving')},flush=True)
if __name__=='__main__':main()
