"""严格一次导出和三个fresh加一个前置合同进程，失败原样停止。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-alias-runtime-v1.json'
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=json.loads(PLAN.read_text(encoding='utf-8'))
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('预冻结源/输入不同，启动前STOP')
    a.output.mkdir(parents=True,exist_ok=False);rows=[];environment=os.environ.copy();environment.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OPENBLAS_NUM_THREADS='1')
    jobs=[('export',[str(ROOT/'scripts/export_page_alias.py'),'--output',str(a.output/'export')]),*[(mode,[str(ROOT/'scripts/page_alias_front.py'),'--mode',mode,'--output',str(a.output/mode)]) for mode in ('original','aligned','alias','contracts')]]
    for label,args in jobs:
        started=time.perf_counter();print('开始唯一前置：'+label,flush=True)
        result=subprocess.run([sys.executable,*args],cwd=ROOT,env=environment);elapsed=time.perf_counter()-started;rows.append(dict(label=label,returncode=result.returncode,process_wall_seconds=elapsed))
        (a.output/'run.json').write_text(json.dumps(dict(passed=False,plan_sha256=sha(PLAN),jobs=rows,scope='外部wall包括Python/imports/全部输入SHA/receipt及结果写入；非吞吐。'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if result.returncode:raise RuntimeError('唯一前置失败，原件保留STOP：'+label)
    receipts={mode:json.loads((a.output/mode/'results.json').read_text(encoding='utf-8')) for mode in ('original','aligned','alias','contracts')};export=json.loads((a.output/'export/export.json').read_text(encoding='utf-8'));total=export['outputs']['alias.bin']['bytes']+48+1056;saving=16779328-total
    if saving<(1<<20) or any(not value['passed'] for value in receipts.values()):raise AssertionError('实际backing或前置门失败')
    value=dict(passed=True,plan_sha256=sha(PLAN),jobs=rows,alias_backing=export['outputs']['alias.bin'],aligned_backing=export['outputs']['aligned.bin'],owner_bytes=48,model_bytes=1056,total_backing_plus_required_state=total,baseline_capacity=16779328,net_backing_saving=saving,ready_for_next_quality=True,scope='API/资源/格式前置全部通过后仍需另授完整域/百图；当前没有任何吞吐或独立物理RAM资格。')
    (a.output/'run.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(value,flush=True)
if __name__=='__main__':main()
