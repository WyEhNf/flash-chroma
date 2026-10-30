"""由原始五轮秒数字面值用Decimal独立复算C7BK，既定门槛不变。"""
import argparse
from decimal import Decimal, localcontext
import json
from pathlib import Path

D=Decimal
TIERS=(100,90,80,70,60,50)
def load(raw):return json.loads(raw,parse_float=D)
def median(values):
    ordered=sorted(values);n=len(ordered)
    return ordered[n//2] if n%2 else (ordered[n//2-1]+ordered[n//2])/2
def close(left,right):
    if abs(left-right)>D('1e-15')*max(D(1),abs(left),abs(right)):
        raise AssertionError('Decimal与原序列化浮点不符')
def compute_raw(worker_raw,summary_raw):
    with localcontext() as context:
        context.prec=60
        workers=[load(raw) for raw in worker_raw];summary=load(summary_raw)
        if len(workers)!=4:raise AssertionError('四worker不完整')
        result=dict(purpose=__doc__,decimal_precision=60,controls={},modes={},six_tier_minimum_capacity={})
        for mode in ('inplace','outplace'):
            for threads in (1,4):
                key=f'{mode}_{threads}';aa=[];times=[]
                for index,worker in enumerate(workers):
                    selected={r['label']:r for r in worker['rows'] if r['mode']==mode and r['threads']==threads}
                    if len(selected)!=6:raise AssertionError('六角色不完整')
                    current={}
                    for label,row in selected.items():
                        if len(row['seconds'])!=5:raise AssertionError('原五轮不完整')
                        current[label]=median(row['seconds']);close(current[label],row['median_seconds'])
                    times.append(current)
                    control=next(c for c in worker['controls'] if c['mode']==mode and c['threads']==threads)
                    if len(control['seconds'])!=5:raise AssertionError('AA五轮不完整')
                    repeat=median(control['seconds']);ratio=repeat/current['ref80'];close(ratio,control['ratio'])
                    aa.append(dict(worker=index,primary_median_seconds=str(current['ref80']),repeat_median_seconds=str(repeat),ratio=str(ratio),individual_pass=D('.8')<=ratio<=D('1.25')))
                aa_values=[D(x['ratio']) for x in aa];aa_median=median(aa_values)
                valid=all(x['individual_pass'] for x in aa) and D(1)/D('1.1')<=aa_median<=D('1.1')
                old=summary['controls'][key]
                if old['pass_']!=valid:raise AssertionError('Decimal AA判定不同')
                close(aa_median,old['median'])
                result['controls'][key]=dict(workers=aa,median=str(aa_median),pass_=valid)
                rows=[r for r in summary['ratios'] if r['mode']==mode and r['threads']==threads];evaluated={}
                for row in rows:
                    ratios=[min(t['ref78'],t['ref80'])/t[row['label']] for t in times]
                    for actual,published in zip(ratios,row['per_worker'],strict=True):close(actual,published)
                    close(median(ratios),row['speed_retention']);worst=min(ratios)
                    evaluated[row['label']]=dict(capacity=row['capacity'],accuracy_retention='1',per_worker=[str(x) for x in ratios],worst=str(worst),worst_worker=ratios.index(worst),median=str(median(ratios)),eligible_speed_tiers=[tier for tier in TIERS if valid and worst>=D(tier)/100])
                result['modes'][key]=evaluated
                result['six_tier_minimum_capacity'][key]={}
                for tier in TIERS:
                    eligible=[r for r in rows if valid and D(evaluated[r['label']]['worst'])>=D(tier)/100]
                    selected=min(eligible,key=lambda r:r['capacity'],default=None)
                    existing=summary['tiers'][key][str(tier)]
                    if (selected is None)!=(existing is None) or (selected is not None and selected['label']!=existing['label']):raise AssertionError('Decimal六档选择不同')
                    result['six_tier_minimum_capacity'][key][str(tier)]=None if selected is None else dict(label=selected['label'],bytes=selected['capacity'])
        result['scope']='相同worker较快78/80作分母，最劣四worker；Decimal仅复算原件，不增加调用、不修复或删除失败。精度独立100%（八完整域/八百图输出身份）。'
        return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--perf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=compute_raw([(a.perf/f'worker-{i}/results.json').read_bytes() for i in range(4)],(a.perf/'summary.json').read_bytes())
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(a.output)
if __name__=='__main__':main()
