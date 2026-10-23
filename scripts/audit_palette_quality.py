"""仅用冻结联合频数和palette独立复算质量/六档，不重新拟合或读取照片。"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import json
import numpy as np


def metrics(hist):
    n=int(hist.sum());bins=np.flatnonzero(hist);counts=hist[bins]
    roots=np.sqrt(bins.astype(np.float64))
    rank=99*(n-1);integer,fraction=divmod(rank,100)
    cumulative=np.cumsum(hist)
    low=int(np.searchsorted(cumulative,integer,side='right'))
    high=int(np.searchsorted(cumulative,integer+(fraction!=0),side='right'))
    remaining=tail_count=(n+99)//100;tail=0.
    for squared,count in zip(bins[::-1],counts[::-1]):
        take=min(remaining,int(count));tail+=take*math.sqrt(int(squared));remaining-=take
        if not remaining:break
    return dict(n=n,mean=float(np.dot(roots,counts)/n),rms=math.sqrt(float(np.dot(bins,counts))/n),
                p99=math.sqrt(low)+(fraction/100)*(math.sqrt(high)-math.sqrt(low)),max=math.sqrt(int(bins[-1])),cvar_1pct=tail/tail_count)


def check(expected,actual):
    for key in ['n','mean','rms','p99','max','cvar_1pct']:
        assert abs(expected[key]-actual[key])<1e-10,(key,expected[key],actual[key])


def ratio(old,new):
    return min(min(1.,old[key]/new[key]) if new[key] else 1. for key in ['mean','p99','max'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--input-profile',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('拒绝覆盖审计回执')
    rows=json.loads((args.profile/'results.json').read_text(encoding='utf-8'))['results']
    support=np.load(args.profile/'joint-support.npz');counted=0
    for row in rows:
        model=np.load(args.profile/(row['name']+'.npz'))
        decoded=model['palette'][model['mapping']].astype(np.int32)
        merged=np.zeros(3*255**2+1,np.int64)
        for index in [-1,*range(100)]:
            prefix='full' if index<0 else f'p{index:03d}'
            pairs=support[prefix+'_pairs'];counts=support[prefix+'_counts']
            ids=(pairs>>24).astype(np.intp)
            target=np.column_stack([pairs&255,(pairs>>8)&255,(pairs>>16)&255]).astype(np.int32)
            delta=decoded[ids]-target
            squared=delta[:,0]**2+delta[:,1]**2+delta[:,2]**2
            # 所有计数远低于2^53，浮点bincount的整数加法精确；与原add.at路径不同。
            hist=np.bincount(squared,weights=counts,minlength=3*255**2+1).astype(np.int64)
            actual=metrics(hist)
            assert actual['n']==(16777216 if index<0 else 786432)
            expected=row['metrics'] if index<0 else row['photos']['per_image'][index]
            check(expected,actual);counted+=1
            if index>=0:merged+=hist
        check(row['photos']['merged'],metrics(merged));counted+=1
        baseline=rows[0]
        minimum=min(ratio(baseline['metrics'],row['metrics']),ratio(baseline['photos']['merged'],row['photos']['merged']),
            *(ratio(old,new) for old,new in zip(baseline['photos']['per_image'],row['photos']['per_image'])))
        assert abs(minimum-row['minimum_retention'])<1e-12
        assert row['accuracy_tiers']==[tier for tier in [1.,.9,.8,.7,.6,.5] if minimum+1e-12>=tier]
    input_rows=json.loads((args.input_profile/'results.json').read_text(encoding='utf-8'))['results']
    histograms=np.load(args.input_profile/'histograms.npz')
    for row in input_rows:
        check(row['metrics'],metrics(histograms['full_'+row['name']]))
        check(row['photos']['merged'],metrics(histograms['photo_'+row['name']]))
        baseline=input_rows[0]
        minimum=min(ratio(baseline['metrics'],row['metrics']),ratio(baseline['photos']['merged'],row['photos']['merged']),
            *(ratio(old,new) for old,new in zip(baseline['photos']['per_image'],row['photos']['per_image'])))
        assert abs(minimum-row['minimum_retention'])<1e-12
        assert row['accuracy_tiers']==[tier for tier in [1.,.9,.8,.7,.6,.5] if minimum+1e-12>=tier]
    args.output.write_text(json.dumps(dict(passed=True,palette_metric_records=counted,input_aggregate_histograms=8,
        scope='palette九配置的完整域/100逐图/合并五项指标与六档独立复算；输入近邻四配置仅全域/合并直方图复算、逐图比值自洽，不冒充第二次逐图像素验收。'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('palette 918项质量记录、输入8直方图及全部六档复算通过')


if __name__=='__main__':main()
