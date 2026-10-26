"""唯一122节点完整风险筛查及安全解公共指标的保守充分上界。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_component_box as support, channel_hotspot_support as hs, channel_capped_risk as risk, study_provenance
from run_channel_tail_nodes import digest,load_model,save
from run_cinema_first_hotspot import train_counts,TRAINING_PIXELS
from verify_channel_coordinates import integer_oracle


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True)
    p.add_argument('--contract',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前122节点完整风险上界普查')
    frozen=json.loads(args.frozen.read_text(encoding='utf-8'));contract=json.loads(args.contract.read_text(encoding='utf-8'))
    if not frozen['ast_pass'] or not contract['pass']:raise ValueError('先冻结源并通过有限合同')
    for sources in (frozen['source_sha256'],contract['source_sha256']):
        for name,expected in sources.items():
            if digest(ROOT/name)!=expected:raise ValueError('当前风险执行源已变：'+name)
    for spec in frozen['inputs'].values():
        if digest(spec['path'])!=spec['sha256']:raise ValueError('固定模型、直方图或数据已变')
    inputs=frozen['inputs'];model=load_model(inputs['first']['path'])
    box=json.loads((ROOT/'artifacts/cinema-max48-first-box-v1/results.json').read_text(encoding='utf-8'))
    with np.load(ROOT/'artifacts/cinema-max48-first-box-v1/replay.npz') as data:selected,hotspots=data['selected_nodes'],data['keys']
    if len(selected)!=122 or len(hotspots)!=145:raise ValueError('不是已验122节点/145热点')
    active=np.zeros((model.m**3,3),bool);active[selected]=True
    keys,geometry=support.complete_support(model,active)
    points=hs.rgb(keys);gold_full=np.load(inputs['gold']['path'],mmap_mode='r');gold=gold_full[keys]
    cube=np.memmap(inputs['cube']['path'],np.uint8,'r',shape=(1<<24,3))
    suffix=np.load(inputs['suffix']['path'],mmap_mode='r');lookup=lambda rgb:suffix[hs.key(rgb)]
    all_nodes=model.nodes.reshape(-1,3).astype(np.uint64);lo_nodes,hi_nodes=all_nodes.copy(),all_nodes.copy()
    lo_nodes[selected]=np.maximum(all_nodes[selected].astype(np.int64)-2,0).astype(np.uint64)
    hi_nodes[selected]=np.minimum(all_nodes[selected]+2,255)
    lower=np.empty((len(keys),3),np.uint8);upper=lower.copy();original_first=lower.copy();max_acc=max_span=0
    for start in range(0,len(keys),65536):
        end=min(start+65536,len(keys));i,w=hs.corners(model,points[start:end]);w=w.astype(np.uint64)
        a=np.sum(w*lo_nodes[i],axis=1,dtype=np.uint64);b=np.sum(w*hi_nodes[i],axis=1,dtype=np.uint64)
        if np.any(a>b) or np.any(b>255*65536) or np.any(b-a>4*65536):raise AssertionError('实际acc盒界失败')
        lower[start:end]=((a+32768)>>16).astype(np.uint8);upper[start:end]=((b+32768)>>16).astype(np.uint8)
        original_first[start:end]=integer_oracle(model,points[start:end]);max_acc=max(max_acc,int(b.max()));max_span=max(max_span,int((b-a).max()))
        for values,expected in ((lo_nodes,lower[start:end]),(hi_nodes,upper[start:end])):
            endpoint=cc.ChannelLut(model.grid,values.astype(np.uint8).reshape(model.nodes.shape),model.idx,model.channel_frac)
            np.testing.assert_array_equal(integer_oracle(endpoint,points[start:end]),expected)
    np.testing.assert_array_equal(lookup(original_first),cube[keys])
    original_squared=np.sum((cube[keys].astype(np.int32)-gold.astype(np.int32))**2,axis=1,dtype=np.int32)
    mass=np.load(inputs['mass']['path'],mmap_mode='r');training,_=train_counts(mass[keys],float(mass.sum(dtype=np.float64)))
    with np.load(inputs['histograms']['path']) as data:
        baselines={label:{'uniform':data['cube_'+role].copy(),'training':data['training60_'+role].copy()}
            for label,role in (('a399','a399'),('best','best'),('current741','candidate'))}
    current=baselines['current741'];hist=current['uniform'][:49].copy();train_hist=current['training'][:49].copy()
    if np.any(current['uniform'][49:]) or np.any(current['training'][49:]) or int(train_hist.sum())!=TRAINING_PIXELS:
        raise AssertionError('当前完整已验直方图不是max48/原60图')
    outside=hist-hs.histogram(original_squared,size=49);outside_training=train_hist-hs.histogram(original_squared,training,size=49)
    if np.any(outside<0) or np.any(outside_training<0) or outside[48] or outside_training[48]:raise AssertionError('完整正支撑未覆盖全部max48')
    minimum,maximum,count,safe_count,safe_max=risk.enumerate_stats(lower,upper,gold,lookup,47)
    dangerous=np.flatnonzero(maximum>47).astype(np.uint32);triples=int(safe_count[dangerous].sum(dtype=np.int64))
    empty=int(np.count_nonzero(safe_count==0));gate=len(dangerous)<=8192 and triples<=1000000 and empty==0
    if not np.all(np.isin(hotspots,keys[dangerous])):raise AssertionError('145热点未全部纳入危险集')
    args.output.mkdir(parents=True)
    stored={'keys':keys,'selected_nodes':selected,'original_first':original_first,'original_squared':original_squared,'training_counts':training,
        'lower_rgb':lower,'upper_rgb':upper,'minimum_squared':minimum,'maximum_squared':maximum,'query_count':count,
        'safe_count':safe_count,'safe_maximum_squared':safe_max,'dangerous_rows':dangerous,
        'outside_hist':outside,'outside_training_hist':outside_training}
    comparisons={};upper_defined=empty==0
    if upper_defined:
        worst=outside+hs.histogram(safe_max,size=49);worst_training=outside_training+hs.histogram(safe_max,training,size=49)
        stored.update(worst_safe_hist=worst,worst_safe_training_hist=worst_training)
        for label,values in baselines.items():
            comparisons[label]={'uniform':risk.compare_histograms(worst,values['uniform']),
                'training':risk.compare_histograms(worst_training,values['training'])}
    for label,values in baselines.items():
        stored['baseline_'+label+'_uniform']=values['uniform'];stored['baseline_'+label+'_training']=values['training']
    np.savez_compressed(args.output/'screen.npz',**stored)
    csr_payload=0
    if gate:
        offsets,allowed=risk.collect_allowed(lower[dangerous],upper[dangerous],gold[dangerous],lookup,47)
        np.testing.assert_array_equal(np.diff(offsets),safe_count[dangerous])
        if int(offsets[-1])!=triples:raise AssertionError('安全CSR不同于完整统计')
        np.savez_compressed(args.output/'danger-allowed.npz',source_keys=keys[dangerous],offsets=offsets,allowed_rgb=allowed)
        csr_payload=keys[dangerous].nbytes+offsets.nbytes+allowed.nbytes
    save(args.output/'run.json',{'inputs':inputs,'source_sha256':frozen['source_sha256'],'frozen_sha256':digest(args.frozen),
        'contract_sha256':digest(args.contract),'plan':frozen['plan'],'environment':study_provenance.environment_fingerprint(),'cp_solver_called':False})
    record={'complete_support_rows':len(keys),'geometry':geometry,'selected_physical_nodes':len(selected),'active_components':int(active.sum()),
        'total_aabb_queries':int(count.sum(dtype=np.int64)),'possibly_dangerous_rows':len(dangerous),'universally_safe_rows':int(np.count_nonzero(maximum<=47)),
        'safe_tuples_in_dangerous_rows':triples,'zero_safe_rows':empty,'within_frozen_resource_gate':bool(gate),
        'outside_support_max_squared':int(np.flatnonzero(outside)[-1]),'outside_training_max_squared':int(np.flatnonzero(outside_training)[-1]),
        'affected_training_mass':int(training.sum()),'upper_histogram_defined':upper_defined,'comparisons':comparisons,
        'independent_endpoint_rows':2*len(keys),'endpoint_mismatches':0,'maximum_endpoint_acc':max_acc,'maximum_unrounded_span':max_span,
        'saved_array_payload_bytes':sum(v.nbytes for v in stored.values()),'allowed_csr_payload_bytes':csr_payload,
        'cp_solver_called':False,'scope':'完整cap47风险与所有安全解的公共指标充分上界；上界不是可实现共享模型，不保护项不代表实际必退；超门STOP，不CP/拟合/性能。'}
    save(args.output/'summary.json',record)
    print({k:record[k] for k in ('complete_support_rows','total_aabb_queries','possibly_dangerous_rows','safe_tuples_in_dangerous_rows','zero_safe_rows','within_frozen_resource_gate')},flush=True)


if __name__=='__main__':main()
