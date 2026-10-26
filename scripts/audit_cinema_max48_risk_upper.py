"""逐点flatten独立复算全风险/安全最大值/CSR及公共上界，不求解CP。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import channel_hotspot_support as hs,channel_capped_risk as risk
from run_channel_tail_nodes import digest,save


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前完整风险上界独立审计')
    run=json.loads((args.stage/'run.json').read_text(encoding='utf-8'));summary=json.loads((args.stage/'summary.json').read_text(encoding='utf-8'))
    for name,h in run['source_sha256'].items():
        if digest(ROOT/name)!=h:raise ValueError('实际风险源已变')
    for spec in run['inputs'].values():
        if digest(spec['path'])!=spec['sha256']:raise ValueError('固定上界输入已变')
    with np.load(args.stage/'screen.npz') as data:v={k:data[k] for k in data.files}
    keys=v['keys'];gold=np.load(run['inputs']['gold']['path'],mmap_mode='r')[keys];suffix=np.load(run['inputs']['suffix']['path'],mmap_mode='r')
    rows=v['dangerous_rows'];danger_map=np.full(len(keys),-1,np.int32);danger_map[rows]=np.arange(len(rows),dtype=np.int32)
    offsets=allowed=None
    if summary['within_frozen_resource_gate']:
        with np.load(args.stage/'danger-allowed.npz') as data:
            np.testing.assert_array_equal(data['source_keys'],keys[rows]);offsets,allowed=data['offsets'],data['allowed_rgb']
    queries=max_chunk=0
    for start in range(0,len(keys),512):
        stop=min(start+512,len(keys));lower=v['lower_rgb'][start:stop].astype(np.int64);width=v['upper_rgb'][start:stop].astype(np.int64)-lower+1
        counts=np.prod(width,axis=1,dtype=np.int64);begins=np.r_[0,np.cumsum(counts,dtype=np.int64)]
        point=np.repeat(np.arange(stop-start),counts);local=np.arange(int(begins[-1]))-np.repeat(begins[:-1],counts)
        blue=local%width[point,2];rest=local//width[point,2]
        rgb=(lower[point]+np.column_stack((rest//width[point,1],rest%width[point,1],blue))).astype(np.uint8)
        error=suffix[hs.key(rgb)].astype(np.int32)-gold[start:stop][point].astype(np.int32);q=np.sum(error*error,axis=1,dtype=np.int32);safe=q<=47
        minimum=np.minimum.reduceat(q,begins[:-1]);maximum=np.maximum.reduceat(q,begins[:-1])
        safe_count=np.add.reduceat(safe.astype(np.int64),begins[:-1]);safe_max=np.maximum.reduceat(np.where(safe,q,-1),begins[:-1])
        for observed,label in ((minimum,'minimum_squared'),(maximum,'maximum_squared'),(counts,'query_count'),(safe_count,'safe_count'),(safe_max,'safe_maximum_squared')):
            np.testing.assert_array_equal(observed,v[label][start:stop])
        if offsets is not None:
            for j in np.flatnonzero(danger_map[start:stop]>=0):
                index=danger_map[start+j];expected=rgb[begins[j]:begins[j+1]][safe[begins[j]:begins[j+1]]]
                np.testing.assert_array_equal(expected,allowed[offsets[index]:offsets[index+1]])
        queries+=len(rgb);max_chunk=max(max_chunk,len(rgb))
    np.testing.assert_array_equal(rows,np.flatnonzero(v['maximum_squared']>47))
    empty=int(np.count_nonzero(v['safe_count']==0));triples=int(v['safe_count'][rows].sum(dtype=np.int64))
    gate=len(rows)<=8192 and triples<=1000000 and empty==0
    assert gate==summary['within_frozen_resource_gate'] and queries==summary['total_aabb_queries']
    cube=np.memmap(run['inputs']['cube']['path'],np.uint8,'r',shape=(1<<24,3))
    q0=np.sum((cube[keys].astype(np.int32)-gold.astype(np.int32))**2,axis=1,dtype=np.int32)
    np.testing.assert_array_equal(q0,v['original_squared'])
    np.testing.assert_array_equal(v['outside_hist'],v['baseline_current741_uniform'][:49]-hs.histogram(q0,size=49))
    np.testing.assert_array_equal(v['outside_training_hist'],v['baseline_current741_training'][:49]-hs.histogram(q0,v['training_counts'],size=49))
    if empty==0:
        worst=v['outside_hist']+hs.histogram(v['safe_maximum_squared'],size=49)
        train=v['outside_training_hist']+hs.histogram(v['safe_maximum_squared'],v['training_counts'],size=49)
        np.testing.assert_array_equal(worst,v['worst_safe_hist']);np.testing.assert_array_equal(train,v['worst_safe_training_hist'])
        for role in ('a399','best','current741'):
            assert risk.compare_histograms(worst,v['baseline_'+role+'_uniform'])==summary['comparisons'][role]['uniform']
            assert risk.compare_histograms(train,v['baseline_'+role+'_training'])==summary['comparisons'][role]['training']
    assert not run['cp_solver_called'] and not summary['cp_solver_called']
    save(args.output,{'pass':True,'source_sha256':digest(__file__),'summary_sha256':digest(args.stage/'summary.json'),'screen_sha256':digest(args.stage/'screen.npz'),
        'checked_source_rows':len(keys),'checked_rgb_queries':queries,'maximum_chunk_queries':max_chunk,'dangerous_rows':len(rows),'safe_tuples':triples,
        'within_resource_gate':gate,'scope':'独立逐点flatten复算全部状态、最大安全q与CSR；按固定外域和全频数重建六组上界及严格根证书，没有CP或共享模型可行结论。'})
    print({'pass':True,'rows':len(keys),'queries':queries,'within_gate':gate},flush=True)


if __name__=='__main__':main()
