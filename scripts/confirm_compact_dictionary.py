"""仅执行预冻结的一次字典确认，原bench同进程运行，原结果不覆盖，合并八worker取最劣。"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan_path=ROOT/'experiments/compact-dictionary-confirm-v1.json';plan=read(plan_path)
    for name,value in plan['files_sha256'].items():
        if sha(Path(name))!=value:raise AssertionError('冻结输入变化：'+name)
    for name,value in plan['source_sha256'].items():
        if sha(ROOT/name)!=value:raise AssertionError('冻结源变化：'+name)
    a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False);measurement=a.output/'measurement';bench=ROOT/'scripts/bench_compact_dictionary.py';argv=[str(bench),*plan['benchmark_arguments'],'--output',str(measurement)]
    save(a.output/'preflight.json',dict(plan_sha256=sha(plan_path),driver_sha256=sha(__file__),original_argv=argv,purpose=__doc__))
    previous=sys.argv;os.environ.update(plan['environment']);sys.argv=argv;capture=io.StringIO()
    try:
        with contextlib.redirect_stdout(capture):runpy.run_path(str(bench),run_name='__main__')
    finally:sys.argv=previous
    (a.output/'original-bench-stdout.txt').write_text(capture.getvalue(),encoding='utf-8');first=read(Path(plan['first_directory'])/'summary.json');second=read(measurement/'summary.json');rows=[]
    for old in first['ratios']:
        new=next(r for r in second['ratios'] if (r['label'],r['mode'],r['threads'])==(old['label'],old['mode'],old['threads']));key=old['mode']+'_'+str(old['threads']);raw=old['per_worker']+new['per_worker'];c1=first['controls'][key];c2=second['controls'][key];controls=[c1,c2];valid=[]
        for values,control in ((old['per_worker'],c1),(new['per_worker'],c2)):
            if 1/1.1<=control['median']<=1.1:valid.extend(value for value,aa in zip(values,control['ratios']) if .8<=aa<=1.25)
        rows.append(dict(label=old['label'],mode=old['mode'],threads=old['threads'],capacity=old['capacity'],accuracy_retention=1.0,all_eight_workers=raw,worst_raw=min(raw),median_raw=statistics.median(raw),worst_valid=min(valid) if valid else None,controls_both_pass=c1['pass_'] and c2['pass_'],stable_tiers={str(t):bool(c1['pass_'] and c2['pass_'] and min(raw)>=t/100) for t in (100,90,80,70,60,50)},valid_worker_below_50=any(x<.5 for x in valid)))
    selected=[r for r in rows if r['label']=='avx2_24'];save(a.output/'combined.json',dict(purpose=__doc__,plan_sha256=sha(plan_path),first_summary_sha256=sha(Path(plan['first_directory'])/'summary.json'),second_summary_sha256=sha(measurement/'summary.json'),rows=rows,controls=dict(first=first['controls'],second=second['controls']),stable_3byte_global_50=all(r['stable_tiers']['50'] for r in selected),revoke_3byte_global_50=any(r['valid_worker_below_50'] for r in selected),scope=plan['decision']))
    print(a.output/'combined.json')
if __name__=='__main__':main()
