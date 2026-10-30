"""只从冻结回执复算一次性能门禁并归档，无新的像素、拟合或测速。"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖档案')
    bench=ROOT/'artifacts/channel-native-benchmark-reuse-v1';result=read(bench/'results.json')
    plan=read(ROOT/'experiments/channel-native-benchmark-reuse-v1.json')
    policy=read(ROOT/'experiments/channel-runtime-reuse-policy-v1.json')
    if plan['orders']!=policy['performance']['process_orders'] or plan['thread_orders']!=policy['performance']['thread_orders']:
        raise ValueError('进程顺序不同于冻结政策')
    workers=[]
    for i,h in enumerate(result['worker_sha256']):
        path=bench/f'worker{i}.json'
        if digest(path)!=h:raise ValueError('原轮次SHA不同')
        w=read(path)
        if w['order']!=plan['orders'][i] or w['thread_order']!=plan['thread_orders'][i]:raise ValueError('实际顺序不同')
        if len(w['records'])!=6:raise ValueError('缺计时配置')
        for r in w['records']:
            if len(r['apply_seconds'])!=5 or len(r['copy_apply_seconds'])!=5:raise ValueError('实际轮次不同')
        workers.append(w)
    checks=[];failures=[]
    for threads in (1,4):
        records=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers]
        ratios=[statistics.median(r['candidate']['apply_seconds'])/statistics.median(r['baseline']['apply_seconds']) for r in records]
        paired=next(r for r in result['paired'] if r['requested_threads']==threads and r['denominator']=='baseline')
        if max(abs(a-b) for a,b in zip(ratios,paired['process_ratios']))>1e-12:raise ValueError('配对比复算不同')
        for variant in plan['variants']:
            raw=[statistics.median(r[variant]['apply_seconds'])*10 for r in records]
            summary=next(r for r in result['summary'] if r['requested_threads']==threads and r['variant']==variant)
            if abs(statistics.median(raw)-summary['median_apply_ms_per_image'])>1e-12:raise ValueError('绝对统计复算不同')
        total={v:statistics.median([statistics.median(r[v]['copy_apply_seconds']) for r in records]) for v in ('baseline','candidate')}
        if statistics.median(ratios)>.97:failures.append(f'threads{threads}.median_apply_ratio_0.97')
        if max(ratios)>1.02:failures.append(f'threads{threads}.all_process_ratio_1.02')
        if total['candidate']>total['baseline']:failures.append(f'threads{threads}.copy_apply_nonregression')
        checks.append({'requested_threads':threads,'process_ratios':ratios,'median_ratio':statistics.median(ratios),
            'copy_apply_median_ratio':total['candidate']/total['baseline']})
    contract=read(ROOT/'artifacts/channel-native-contract-reuse-v1/results.json')
    native=read(ROOT/'artifacts/channel-native-accept-reuse-v1/results.json')
    if not contract['pass'] or not native['pass'] or any(r['byte_mismatches'] for r in native['cube']) or native['photos']['byte_mismatches']:
        raise ValueError('正确性未通过')
    if contract['library_sha256']!=native['library_sha256'] or native['library_sha256']!=plan['inputs']['library']['sha256']:
        raise ValueError('实际库身份不同')
    out.mkdir(parents=True)
    save(out/'policy-audit.json',{'purpose':__doc__,'performance_accepted':not failures,'failures':failures,
        'paired_recomputed':checks,'raw_result_sha256':digest(bench/'results.json'),
        'native_pass':True,'concentrated_contract_pass':True,'additional_native_or_numeric_calls':0})
    with (out/'performance.csv').open('w',newline='',encoding='utf-8-sig') as f:
        keys=['variant','requested_threads','median_apply_ms_per_image','median_copy_apply_ms_per_image','model_accounting_bytes','serialized_input_bytes']
        writer=csv.DictWriter(f,keys);writer.writeheader()
        for r in result['summary']:writer.writerow({k:r[k] for k in keys})
    evidence_dirs=['channel-geometry-reuse-v1','channel-native-runtime-reuse-v1','channel-native-contract-reuse-v1',
        'channel-native-accept-reuse-v1','channel-native-benchmark-reuse-v1']
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in evidence_dirs:
            folder=ROOT/'artifacts'/name
            for p in sorted(folder.iterdir()):
                if p.is_file() and p.suffix in ('.json','.zip','.log'):z.write(p,p.relative_to(ROOT).as_posix())
        for p in [ROOT/'scripts/archive_channel_reuse.py',ROOT/'experiments/channel-native-accept-reuse-v1.json',
                  ROOT/'experiments/channel-native-benchmark-reuse-v1.json',ROOT/'experiments/channel-runtime-reuse-policy-v1.json']:
            z.write(p,p.relative_to(ROOT).as_posix())
    library=ROOT/plan['inputs']['library']['path'];old=ROOT/plan['inputs']['baseline_library']['path']
    build=read(ROOT/'artifacts/channel-native-runtime-reuse-v1/build.json')
    core=ROOT/'build-channel-research/libjshc_core.a'
    if digest(core)!=build['static_core_sha256']:raise ValueError('链接核心已变化')
    with zipfile.ZipFile(out/'binaries.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in [library,old,core,*[library.parent/n for n in build['binary_sha256'] if n!=library.name]]:
            z.write(p,p.relative_to(ROOT).as_posix())
    for name,path in [('benchmark-results.json',bench/'results.json'),('native-results.json',ROOT/'artifacts/channel-native-accept-reuse-v1/results.json'),
                      ('geometry-profile.json',ROOT/'artifacts/channel-geometry-reuse-v1/results.json')]:shutil.copyfile(path,out/name)
    save(out/'manifest.json',{'purpose':'未入围的唯一地址复用候选及一次性能门禁；模型/精度不变',
        'files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps({'performance_accepted':not failures,'failures':failures,'paired':checks},ensure_ascii=False))

if __name__=='__main__':main()
