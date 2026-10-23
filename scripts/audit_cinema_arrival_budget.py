"""独立重算直方图/逐图对比与原生SHA；不冒充第二次逐PNG像素重放。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np


def metrics(hist):
    n=int(hist.sum());root=np.sqrt(np.arange(len(hist),dtype=np.float64));cdf=hist.cumsum()
    rank=.99*(n-1);lo=int(np.searchsorted(cdf,int(np.floor(rank)),side='right'))
    hi=int(np.searchsorted(cdf,int(np.ceil(rank)),side='right'))
    p99=root[lo]+(rank-np.floor(rank))*(root[hi]-root[lo])
    tail=max(1,(n+99)//100);remaining=tail;total=0.
    for square in np.flatnonzero(hist)[::-1]:
        taken=min(float(hist[square]),remaining);total+=taken*root[square];remaining-=taken
        if remaining<=0:break
    return {'n':n,'mean':float(hist@root/n),'rms':float(np.sqrt(hist@np.arange(len(hist),dtype=np.int64)/n)),
        'p99':float(p99),'max':float(root[np.flatnonzero(hist)[-1]]),'cvar_1pct':total/tail}


def compare(old,new):
    old={r['image']:r for r in old};new={r['image']:r for r in new};assert old.keys()==new.keys()
    answer={}
    for metric in ('mean','rms','p99','max','cvar_1pct'):
        better=equal=0;worse=[]
        for image in old:
            a,b=old[image][metric],new[image][metric]
            if b<a-1e-12:better+=1
            elif abs(b-a)<=1e-12:equal+=1
            else:worse.append({'image':image,'before':a,'after':b,'ratio':b/a if a else None})
        answer[metric]={'better':better,'equal':equal,'worse':len(worse),'worse_images':worse}
    return answer


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖独立审计')
    results=json.loads((ROOT/'artifacts/cinema-arrival-budget-accept-v1/results.json').read_text(encoding='utf-8'))
    study=json.loads((ROOT/'artifacts/cinema-arrival-last-budget-v1/summary.json').read_text(encoding='utf-8'))
    original_path=args.cache_root/'artifacts/cinema-current-anchor-accept-v1/results.json'
    original=json.loads(original_path.read_text(encoding='utf-8'))
    assert original['cube']['prediction_sha256']=='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
    new=results['variants']['candidate'];hist=np.load(ROOT/'artifacts/cinema-arrival-last-budget-v1/after-hist.npy')
    recomputed=metrics(hist)
    for k,v in recomputed.items():assert abs(v-new['cube'][k])<1e-11 and abs(v-study['after'][k])<1e-11
    assert new['passed_aggregate'] and new['full_native_byte_mismatches']==new['photo_native_byte_mismatches']==0
    cube=ROOT/'artifacts/cinema-arrival-budget-accept-v1/candidate.rgb'
    with cube.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
    assert all(new['sha256'][k]==sha for k in ('oracle','scalar','avx2'))
    comparisons={'versus_previous_best':compare(results['baseline_photos']['per_image'],new['photos']['per_image']),
        'versus_a399':compare(original['photos']['per_image'],new['photos']['per_image'])}
    for metric,values in comparisons['versus_previous_best'].items():
        assert all(values[k]==new['photos']['changes'][metric][k] for k in ('better','equal','worse'))
    for metric in ('mean','rms'):
        count=sum(r['n'] for r in new['photos']['per_image'])
        value=sum((r[metric]**(2 if metric=='rms' else 1))*r['n'] for r in new['photos']['per_image'])/count
        if metric=='rms':value=value**.5
        assert abs(value-new['photos'][metric])<1e-11
    output={'pass':True,'histogram_metrics':recomputed,'full_cube_sha256':sha,'full_reference_sha256':new['sha256']['reference'],
        'comparisons':comparisons,'original_cube':original['cube'],'original_results_sha256':hashlib.sha256(original_path.read_bytes()).hexdigest(),
        'original_photos_aggregate':{k:v for k,v in original['photos'].items() if k!='per_image'},
        'new_model_capacity_bytes':new['model_accounting_bytes'],'metric_convention':'p99沿用线性rank=.99(N−1)；cvar_1pct沿用最差ceil(N/100)个整数样本均值，不是分数尾质量定义。',
        'scope':'重算完整联合支撑直方图与100图JSON对比/mean/RMS汇总，未第二次逐PNG跑像素；native/独立四级正确性来自单独终验原件'}
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(output,ensure_ascii=False))


if __name__=='__main__':main()
