"""不调用拟合或原验收统计函数，从原始完整RGB流独立复算直方图与指标。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def metrics(hist):
    total=int(hist.sum());cdf=np.cumsum(hist,dtype=np.int64);position=.99*(total-1)
    lower=int(math.floor(position));upper=int(math.ceil(position))
    a=int(np.searchsorted(cdf,lower,side='right'));b=int(np.searchsorted(cdf,upper,side='right'))
    tail=(total+99)//100;remaining=tail;tail_sum=[]
    for squared in range(len(hist)-1,-1,-1):
        taken=min(remaining,int(hist[squared]));tail_sum.append(taken*math.sqrt(squared));remaining-=taken
        if remaining==0:break
    result={'n':total,'mean':math.fsum(int(count)*math.sqrt(sq) for sq,count in enumerate(hist) if count)/total,
        'rms':math.sqrt(sum(sq*int(count) for sq,count in enumerate(hist))/total),
        'p99':math.sqrt(a)+(position-lower)*(math.sqrt(b)-math.sqrt(a)),
        'max':math.sqrt(int(np.flatnonzero(hist)[-1])),'cvar_1pct':math.fsum(tail_sum)/tail}
    for threshold in (1,2,3,5):result['fraction_ge_'+str(threshold)]=int(hist[threshold**2:].sum())/total
    return result


def check_metrics(actual,reported):
    for key,value in actual.items():
        if abs(value-reported[key])>1e-12:raise AssertionError('独立指标不符：'+key)


def histogram(path,gold):
    output=np.memmap(path,np.uint8,'r',shape=(256**3,3));hist=np.zeros(3*255**2+1,np.int64)
    for start in range(0,len(output),1<<18):
        delta=output[start:start+(1<<18)].astype(np.int32)-gold[start:start+(1<<18)].astype(np.int32)
        square=np.sum(delta*delta,axis=1,dtype=np.int32);hist+=np.bincount(square,minlength=len(hist))
    return hist


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--study',type=Path,required=True)
    p.add_argument('--accept-root',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--reference',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖独立审计')
    if digest(args.baseline)!='373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed':raise ValueError('基线不符')
    if digest(args.reference)!='ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690':raise ValueError('真值不符')
    gold=np.load(args.reference,mmap_mode='r');old_hist=histogram(args.baseline,gold);old_metrics=metrics(old_hist)
    np.testing.assert_array_equal(old_hist,np.load(args.study/'before-hist.npy'))
    summaries=json.loads((args.study/'summary.json').read_text(encoding='utf-8'));records={}
    for mode in ('max_first','p99_first'):
        folder=args.accept_root/('cinema-second-accept-'+mode+'-v1');result=json.loads((folder/'results.json').read_text(encoding='utf-8'))
        hist=histogram(folder/'candidate.rgb',gold);actual=metrics(hist)
        np.testing.assert_array_equal(hist,np.load(args.study/mode/'after-hist.npy'))
        check_metrics(actual,result['cube']);check_metrics(actual,summaries[mode]['after']);check_metrics(old_metrics,result['baseline'])
        raw_sha=digest(folder/'candidate.rgb')
        for name in ('oracle','scalar','avx2'):
            if result['sha256'][name]!=raw_sha:raise AssertionError('原生/独立oracle完整流身份不符')
        photo=result['photos'];old_photo=result['baseline_photos'];rows=photo['per_image'];old_rows=old_photo['per_image']
        if len(rows)!=100 or len(old_rows)!=100 or len({r['image'] for r in rows})!=100:raise AssertionError('照片集合不完整')
        for collection,aggregate in ((rows,photo),(old_rows,old_photo)):
            n=sum(row['n'] for row in collection)
            if n!=aggregate['n']:raise AssertionError('逐图像素数和不符')
            if abs(math.fsum(row['n']*row['mean'] for row in collection)/n-aggregate['mean'])>1e-12:raise AssertionError('逐图mean合计不符')
            if abs(math.sqrt(math.fsum(row['n']*row['rms']**2 for row in collection)/n)-aggregate['rms'])>1e-12:raise AssertionError('逐图RMS合计不符')
            if max(row['max'] for row in collection)!=aggregate['max']:raise AssertionError('逐图max合计不符')
        changes={}
        for key in ('mean','rms','p99','max','cvar_1pct'):
            pairs=list(zip(old_rows,rows))
            if any(a['image']!=b['image'] for a,b in pairs):raise AssertionError('逐图顺序不符')
            better=sum(b[key]<a[key]-1e-12 for a,b in pairs);worse=sum(b[key]>a[key]+1e-12 for a,b in pairs)
            changes[key]={'better':better,'worse':worse,'same':100-better-worse,
                'worst_ratio':max((b[key]/a[key] if a[key] else (1. if b[key]==0 else math.inf)) for a,b in pairs)}
        records[mode]={'cube':actual,'candidate_sha256':raw_sha,'raw_hist_equals_complete_weighted_support':True,
            'full_native_and_oracle_sha_passed':True,'photo_aggregate_matches_rows':True,'photo_changes':changes,
            'passed_aggregate':result['passed_aggregate']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'pass':True,'baseline':old_metrics,'records':records,'source_sha256':digest(Path(__file__)),
        'scope':'原始全域重算，独立math.fsum/整数CDF/top-ceil(n/100)CVaR，逐图mean/RMS/max合计及变化；未重新解码照片/native或测速度。'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'records':records},flush=True)


if __name__=='__main__':main()
