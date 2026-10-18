"""静态复算原始性能统计，归档一次完整准确性与实际四级运行成本。"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import zipfile
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def csv_file(path,rows):
    with Path(path).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]));writer.writeheader();writer.writerows(rows)
def delta(a,b):return 100*(1-b/a) if a else None

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖正式档案')
    accuracy=ROOT/'artifacts/cinema-current-anchor-accept-v1';bench=ROOT/'artifacts/cinema-current-anchor-runtime-v1'
    full=read(accuracy/'results.json');perf=read(bench/'results.json');plan=read(ROOT/'experiments/cinema-current-anchor-runtime-v1.json')
    audit=read(ROOT/'artifacts/cinema-current-anchor-evidence-audit-v1/results.json')
    if not full['acceptance']['accepted'] or full['acceptance']['failed'] or not audit['pass'] or not perf['pass']:raise ValueError('前置阶段未成功')
    workers=[]
    for i,h in enumerate(perf['worker_sha256']):
        p=bench/f'worker{i}.json'
        if digest(p)!=h:raise ValueError('原轮次SHA不同')
        w=read(p)
        if w['order']!=plan['orders'][i] or w['thread_order']!=plan['thread_orders'][i]:raise ValueError('实际配置顺序不同')
        if len(w['records'])!=4 or len(w['loaded_dependency_sources'])!=5:raise ValueError('配置或已载依赖不完整')
        workers.append(w)
    for threads in (1,4):
        records=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers]
        ratios=[statistics.median(r['candidate']['apply_seconds'])/statistics.median(r['baseline']['apply_seconds']) for r in records]
        reported=next(r for r in perf['paired'] if r['requested_threads']==threads)
        if any(abs(a-b)>1e-12 for a,b in zip(ratios,reported['process_ratios'])) or abs(statistics.median(ratios)-reported['median_ratio'])>1e-12:
            raise ValueError('原轮次配对比不同')
        for variant in ('baseline','candidate'):
            values=[statistics.median(r[variant]['apply_seconds'])*10 for r in records]
            reported=next(r for r in perf['summary'] if r['requested_threads']==threads and r['variant']==variant)
            if abs(statistics.median(values)-reported['median_apply_ms_per_image'])>1e-12:raise ValueError('性能单位或汇总不符')
    previous=read(ROOT/'artifacts/cinema-envelope-v1/full-results.json')
    earlier=read(ROOT/'artifacts/cinema-axis-calibration-v1/full-results.json')
    if previous['cube']['prediction_sha256']!=earlier['baseline']['cube']['prediction_sha256']:
        raise ValueError('历史PR16比较来源链路不符')
    if previous['cube']['reference_sha256']!=full['cube']['reference_sha256']:raise ValueError('历史参考范围不同')
    pr16=previous['baseline'];out.mkdir(parents=True)
    comparisons=[]
    for scope,new,old in [('cube',full['cube'],full['baseline']['cube']),('photos',full['photos'],full['baseline']['photos'])]:
        metrics=['mean','rms','p99','max','cvar_1pct'] if scope=='cube' else ['mean','rms','worst_image_p99','max','mean_image_cvar_1pct','merged_p99']
        for metric in metrics:comparisons.append({'scope':scope,'metric':metric,'baseline':old[metric],'candidate':new[metric],'reduction_pct':delta(old[metric],new[metric])})
    csv_file(out/'accuracy.csv',comparisons)
    csv_file(out/'performance.csv',[{k:r[k] for k in ['variant','requested_threads','median_apply_ms_per_image','median_copy_apply_ms_per_image','model_accounting_bytes','serialized_input_bytes']} for r in perf['summary']])
    old_by_id={r['image']:r for r in full['baseline']['photos']['per_image']};rows=[];regressions=[]
    for r in full['photos']['per_image']:
        old=old_by_id[r['image']];record={'image':r['image'],'group':r['group']}
        for metric in ('mean','rms','p99','max','cvar_1pct'):
            record['baseline_'+metric]=old[metric];record['candidate_'+metric]=r[metric]
            if r[metric]>old[metric]+1e-12:regressions.append({'image':r['image'],'group':r['group'],'metric':metric,'baseline':old[metric],'candidate':r[metric]})
        rows.append(record)
    csv_file(out/'per-image.csv',rows);csv_file(out/'regressions.csv',regressions)
    grouped=[]
    for name,group in full['groups'].items():
        for version in ('baseline','candidate'):
            v=group[version];grouped.append({'group':name,'variant':version,**{k:v[k] for k in ('n_images','mean','rms','worst_image_p99','max','mean_image_cvar_1pct')}})
    csv_file(out/'groups.csv',grouped)
    summary={'accuracy_accepted':True,'default_promoted':False,'changes_vs_af974':comparisons,'per_image_changes':full['per_image_changes'],
        'cumulative_vs_PR16':{'cube_mean_reduction_pct':delta(pr16['cube']['mean'],full['cube']['mean']),
            'cube_p99_reduction_pct':delta(pr16['cube']['p99'],full['cube']['p99']),
            'photos_mean_reduction_pct':delta(pr16['photos']['mean'],full['photos']['mean'])},
        'historical_PR16_source_sha256':digest(ROOT/'artifacts/cinema-envelope-v1/full-results.json'),
        'performance_paired':perf['paired'],'regressions':regressions,
        'native_byte_mismatches':full['native']['byte_mismatches'],'full_colour_cap_violations':full['cube']['cap_violations'],
        'candidate_npz_sha256':full['representation_sha256'],'cube_prediction_sha256':full['cube']['prediction_sha256'],
        'static_numeric_or_native_calls':0,'evidence_audit_sha256':digest(ROOT/'artifacts/cinema-current-anchor-evidence-audit-v1/results.json')}
    save(out/'summary.json',summary)
    for name,path in [('full-results.json',accuracy/'results.json'),('runtime-results.json',bench/'results.json'),
            ('post-review-audit.json',ROOT/'artifacts/cinema-current-anchor-evidence-audit-v1/results.json')]:shutil.copyfile(path,out/name)
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for folder in [accuracy,bench,ROOT/'artifacts/cinema-current-anchor-evidence-audit-v1']:
            for p in sorted(folder.iterdir()):
                if p.is_file() and p.suffix in ('.json','.npz','.zip','.log'):z.write(p,p.relative_to(ROOT).as_posix())
        for n in ['scripts/archive_cinema_current_anchor.py','experiments/cinema-current-anchor-accept-v1.json',
            'experiments/cinema-current-anchor-full-policy-v1.json','experiments/cinema-current-anchor-runtime-v1.json',
            'experiments/cinema-current-anchor-runtime-policy-v1.json']:z.write(ROOT/n,n)
    fit=read(ROOT/'experiments/cinema-current-anchor-v1.json')
    with zipfile.ZipFile(out/'models.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in [accuracy/'candidate-base.slut',accuracy/'channel-frac.bin',ROOT/'artifacts/cinema-current-anchor-v1/current-anchor-pipeline.npz',
                  *[ROOT/s['path'] for s in fit['suffix_models']],ROOT/fit['inputs']['initial']['path']]:z.write(p,p.relative_to(ROOT).as_posix())
    runtime=ROOT/'artifacts/channel-native-runtime-v3';build=read(runtime/'build.json')
    with zipfile.ZipFile(out/'runtime.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n,h in build['files'].items():
            if digest(runtime/n)!=h:raise ValueError('实测原生构建归档输入变化')
            z.write(runtime/n,(runtime/n).relative_to(ROOT).as_posix())
        z.write(runtime/'build.json',(runtime/'build.json').relative_to(ROOT).as_posix())
    save(out/'manifest.json',{'purpose':'唯一a399完整精度与实际四级运行代价，原始来源/模型/环境/尾部回退均保留',
        'files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps({'accuracy_accepted':True,'cumulative_vs_PR16':summary['cumulative_vs_PR16'],'regressions':regressions},ensure_ascii=False))

if __name__=='__main__':main()
