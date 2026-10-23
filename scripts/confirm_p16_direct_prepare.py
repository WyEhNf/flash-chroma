"""冻结后交错创建句柄，单独确认完整prepare边界；不重跑首轮稳态结果。"""
from __future__ import annotations
import argparse
import ctypes as ct
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
import hashlib
import numpy as np
from study_p16_direct_compile import setup,save,models,direct,info,env,digest

def worker(args,plan):
    libs,(paths,sides)=setup(args)
    assert {n:l.sha256 for n,l in libs.items()}==plan['libraries']
    assert {str(p):digest(p) for p in paths+[sides[0]]}==plan['inputs']
    rawpaths=(ct.c_char_p*4)(*(str(p).encode('utf-8') for p in paths))
    rawsides=(ct.c_char_p*4)(str(sides[0]).encode('utf-8'),None,None,None)
    order=plan['orders'][args.worker]
    records=[]
    for repeat in range(5):
        for name in order:
            handle=ct.c_void_p();error=ct.create_string_buffer(1024);lib=libs[name]
            start=time.perf_counter_ns()
            code=lib.dll.jshc_cc_create(rawpaths,rawsides,4,ct.byref(handle),error,len(error))
            elapsed=time.perf_counter_ns()-start
            if code:raise RuntimeError(error.value.decode('utf-8','replace'))
            try:
                # 不额外构造Python Chain，故Python侧的文件hash完全不落入计时。
                proxy=type('Proxy',(),{'library':lib,'handle':handle})()
                table_sha=None
                if repeat in (0,4):table_sha=hashlib.sha256(direct(proxy).tobytes()).hexdigest()
                if table_sha:assert table_sha==plan['direct_sha256']
                records.append({'repeat':repeat,'variant':name,'create_ns':elapsed,
                    'model_bytes':int(lib.dll.jshc_cc_model_bytes(handle)),'palette':info(proxy),'direct_sha256':table_sha})
                save(args.output/f'worker{args.worker}-partial.json',{'records':records,'order':order})
            finally:lib.dll.jshc_cc_destroy(handle)
    assert {str(p):digest(p) for p in paths+[sides[0]]}==plan['inputs']
    save(args.output/f'worker{args.worker}.json',{'records':records,'order':order,'environment':env()})

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--worker',type=int);args=p.parse_args()
    plan=json.loads(args.plan.read_text(encoding='utf-8'))
    args.data_root=Path(plan['data_root']);args.baseline=Path(plan['paths']['baseline']);args.candidate=Path(plan['paths']['candidate'])
    assert plan['orders']==[['baseline','candidate'],['candidate','baseline'],['candidate','baseline'],['baseline','candidate']]
    assert plan['gate']=={'median_ratio_max':0.75,'any_process_ratio_max':0.9,'repeats_per_variant_per_process':5}
    if args.worker is not None:return worker(args,plan)
    if args.output.exists():raise FileExistsError('保留已有证据，不覆盖或重试')
    args.output.mkdir(parents=True)
    save(args.output/'executed-plan.json',plan)
    for i in range(4):
        subprocess.run([sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--worker',str(i)],check=True)
    workers=[json.loads((args.output/f'worker{i}.json').read_text(encoding='utf-8')) for i in range(4)]
    pairs=[]
    for w in workers:
        durations={name:[r['create_ns']*1e-9 for r in w['records'] if r['variant']==name] for name in ('baseline','candidate')}
        ratio=statistics.median(durations['candidate'])/statistics.median(durations['baseline'])
        paired_ratios=[durations['candidate'][i]/durations['baseline'][i] for i in range(5)]
        pairs.append({'seconds':durations,'process_median_ratio':ratio,'pair_ratios':paired_ratios})
    ratios=[r['process_median_ratio'] for r in pairs]
    passed=statistics.median(ratios)<=0.75 and max(ratios)<=0.9
    save(args.output/'results.json',{'purpose':plan['purpose'],'passed_prepare_gate':passed,
        'processes':pairs,'median_ratio':statistics.median(ratios),'any_process_max':max(ratios),
        'timing_scope':plan['timing_scope'],'gate':plan['gate'],
        'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)],
        'limitations':'Windows宿主本地CPU，未锁频控温；仅prepare独立确认，不修复旧稳态控制失败或外推Skylake。'})
    print('准备确认：',passed,'进程比',ratios,'中位比',statistics.median(ratios))
if __name__=='__main__':main()
