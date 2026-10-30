"""在完整第一级联合支撑上各单扫第二级max/p99目标，固定当前最优其余级。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc,channel_joint_nodes as cj,channel_max_nodes as mx
from lutlab import channel_arrival_nodes as an,channel_arrival_priority as priority,io,study_provenance
from lutlab.integer_rgb_ball import intersection
from run_channel_tail_nodes import digest,save,load_model
from certify_cinema_prefix_bound import key,rgb
from check_channel_arrival_nodes import compact_design
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--best',type=Path,required=True)
    p.add_argument('--cube',type=Path,required=True);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖冻结第二级研究')
    args.output.mkdir(parents=True);cache=args.cache_root.resolve();numba.set_num_threads(4)
    plan=ROOT/'experiments/p16-cinema-second-nodes-v1.json'
    paths={'first':args.best/'model.npz','last':args.best/'stage4.slut',
        'stage2':cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage2.slut',
        'stage3':cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut',
        'reference':cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
        'points':cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy',
        'mass':cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy','cube':args.cube,'contract':args.contract}
    expected={'first':'0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030',
        'last':'5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386',
        'stage2':'933a4311800dabfafdec534cc149c56aeb7043e5e57df8bef4dd174058b57650',
        'stage3':'95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234',
        'reference':'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690',
        'points':'fac03692667ab8d5220a4a09035b420d96037094c101b91011de303209ccaaea',
        'mass':'1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e',
        'cube':'373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed'}
    hashes={k:digest(v) for k,v in paths.items()}
    if any(hashes[k]!=v for k,v in expected.items()):raise ValueError('起点不是冻结当前最佳')
    if json.loads(args.contract.read_text(encoding='utf-8')).get('pass') is not True:raise ValueError('缺少有限独立合同')
    sources=[Path(__file__),plan,ROOT/'scripts/check_cinema_second_nodes.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_arrival_priority.py','channel_arrival_nodes.py','integer_rgb_ball.py',
        'channel_coordinates.py','channel_joint_nodes.py','channel_max_nodes.py','channel_tail_nodes.py',
        'channel_global_nodes.py','io.py','interp.py','study_provenance.py')],
        *[ROOT/'scripts'/name for name in ('run_channel_tail_nodes.py','certify_cinema_prefix_bound.py',
        'check_channel_arrival_nodes.py','verify_channel_coordinates.py','accept_channel_coordinates.py')]]
    save(args.output/'run.json',{'inputs':{k:{'path':str(paths[k]),'sha256':v} for k,v in hashes.items()},
        'sources':{f.relative_to(ROOT).as_posix():digest(f) for f in sources},'plan':json.loads(plan.read_text(encoding='utf-8')),
        'environment':study_provenance.environment_fingerprint(),'numba_threads':4,
        'test_type':'固定完整域无损联合支撑及第二级拟合，无百图/运行时性能'})
    first=load_model(paths['first']);original=cc.from_sparse(io.load_sparse(paths['stage2'],competition=True))
    rest=[cc.from_sparse(io.load_sparse(paths[name],competition=True)) for name in ('stage3','last')]
    points=np.load(paths['points'],mmap_mode='r');gold_full=np.load(paths['reference'],mmap_mode='r')
    rawmass=np.load(paths['mass'],mmap_mode='r');baseline=np.memmap(paths['cube'],np.uint8,'r',shape=(256**3,3))
    if any(v.shape!=(256**3,3) or v.dtype!=np.uint8 for v in (points,gold_full)) or rawmass.shape!=(256**3,):
        raise ValueError('完整输入形状不符')
    started=time.perf_counter();suffix=np.empty_like(points);groups={};root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64))
    histogram=np.zeros(len(root),np.int64);training_mean=0.;totalmass=float(rawmass.sum(dtype=np.float64))
    for start in range(0,len(points),1<<18):
        stop=min(start+(1<<18),len(points));source=points[start:stop]
        np.testing.assert_array_equal(key(source),np.arange(start,stop,dtype=np.uint32))
        transformed=source
        for model in rest:transformed=cc.predict(model,transformed)
        suffix[start:stop]=transformed
        reached=cc.predict(first,source);predicted=cc.predict(original,reached)
        for model in rest:predicted=cc.predict(model,predicted)
        np.testing.assert_array_equal(predicted,baseline[start:stop])
        joint=(key(reached).astype(np.uint64)<<24)|key(gold_full[start:stop]).astype(np.uint64)
        unique,index,inverse,counts=np.unique(joint,return_index=True,return_inverse=True,return_counts=True)
        train=np.bincount(inverse,weights=rawmass[start:stop],minlength=len(unique))
        for pair,count,weight,representative in zip(unique,counts,train,index):
            value=groups.get(int(pair))
            if value is None:groups[int(pair)]=[int(count),float(weight),int(start+representative)]
            else:value[0]+=int(count);value[1]+=float(weight)
        delta=predicted.astype(np.int32)-gold_full[start:stop].astype(np.int32)
        squared=np.sum(delta*delta,axis=1,dtype=np.int32);histogram+=np.bincount(squared,minlength=len(root))
        training_mean+=float(np.asarray(rawmass[start:stop],np.float64)@root[squared])/totalmass
        if stop%(1<<22)==0:print({'compressed':stop,'joint_rows':len(groups),'seconds':time.perf_counter()-started},flush=True)
    probes=np.unique(np.r_[np.arange(0,256**3,65537),0,256**3-1]).astype(np.int64)
    independent=points[probes]
    for model in rest:independent=integer_oracle(model,independent)
    np.testing.assert_array_equal(independent,suffix[probes])
    pairs=np.asarray(sorted(groups),np.uint64);frequency=np.asarray([groups[int(k)][0] for k in pairs],np.int64)
    mass=np.asarray([groups[int(k)][1]/totalmass for k in pairs],np.float64)
    representative=np.asarray([groups[int(k)][2] for k in pairs],np.uint32);del groups
    arrivals=rgb((pairs>>24).astype(np.uint32));gold=rgb((pairs&0xffffff).astype(np.uint32))
    if frequency.sum()!=256**3 or abs(float(mass.sum())-1)>1e-12:raise AssertionError('完整支撑计数错误')
    np.savez_compressed(args.output/'joint-support.npz',arrivals=arrivals,reference=gold,frequency=frequency,mass=mass,representative_source=representative)
    output=cc.predict(original,arrivals);initial,square=an.measure(output,gold,suffix,frequency,mass,11,56)
    np.testing.assert_array_equal(histogram,np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64))
    if abs(initial[1]-training_mean)>1e-11:raise AssertionError('压缩原训练mean不符')
    np.save(args.output/'before-hist.npy',histogram);before_metrics=hist_metrics(histogram)
    certificates=[];arrived_codes=pairs>>24
    for arrived in np.unique(arrived_codes[square>56]):
        selected=arrived_codes==arrived
        certificates.append({'arrived':rgb(np.asarray([arrived],np.uint32))[0].tolist(),
            'gold_rows':int(selected.sum()),'result':intersection(gold[selected],56)})
    save(args.output/'first-prefix-balls.json',{'radius_squared':56,'groups':certificates,
        'scope':'仅旧57热组；任一不可行可证明固定第一级不能达到max56；全部可行不保证插值网络可实现。'})
    indices,weights,active,colours=compact_design(original,arrivals)
    original_nodes=original.nodes.reshape(-1,3)[active].copy();original_acc,_=cj.accumulate(indices,weights,original_nodes,gold)
    np.testing.assert_array_equal(output,((original_acc+io.ONE//2)>>io.Q).astype(np.uint8))
    caps=np.maximum(56,square);directions=np.concatenate((cj.DIRECTIONS,mx.DIRECTIONS),axis=0)
    save(args.output/'profile.json',{'joint_rows':len(pairs),'unique_arrivals':len(np.unique(arrived_codes)),
        'active_nodes':len(active),'all_nodes':original.m**3,'design_bytes':indices.nbytes+weights.nbytes,
        'private_gain_bytes':4*9*78*len(active)*8,'suffix_bytes':suffix.nbytes,'baseline_objectives':initial.tolist(),
        'baseline':before_metrics,'training_mean_error':abs(initial[1]-training_mean),'independent_suffix_probes':len(probes)})
    summaries={}
    for mode,target in (('max_first',7),('p99_first',6)):
        folder=args.output/mode;folder.mkdir();nodes=original_nodes.copy();acc=original_acc.copy()
        measured=initial.copy();current=original;records=[]
        for colour in range(8):
            change,bad,invalid=an.gains(indices,weights,acc,gold,suffix,frequency,mass,nodes,colours,colour,caps,root,4,11,56,directions,4)
            if invalid:raise AssertionError('完整联合支撑几何或cap不符')
            allowance=initial-measured;allowance[6:8]=0
            if np.any(allowance<-1e-7):raise AssertionError('不可预支未取得余额')
            moves,predicted,accepted=priority.select(change,bad,colours,colour,directions,np.maximum(allowance,0),target)
            nodes=(nodes.astype(np.int32)+moves).astype(np.uint8);physical=original.nodes.copy();physical.reshape(-1,3)[active]=nodes
            current=cc.ChannelLut(original.grid,physical,original.idx,original.channel_frac)
            an.apply_accumulator(indices,weights,acc,moves);fresh=cc.predict(current,arrivals)
            np.testing.assert_array_equal(fresh,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
            np.testing.assert_array_equal(fresh,integer_oracle(current,arrivals))
            after,squared=an.measure(fresh,gold,suffix,frequency,mass,11,56)
            error=float(np.max(np.abs(after-measured-predicted)))
            if error>1e-5 or np.any(after>initial+1e-5) or np.any(after[6:8]>measured[6:8]) or np.any(squared>caps):
                raise AssertionError('fresh与精确九预算不符')
            for entry in accepted:entry['physical_node']=int(active[entry['node']])
            record={'colour':colour,'before':measured.tolist(),'after':after.tolist(),'available_budget':allowance.tolist(),
                'gain_error':error,'max_squared':int(squared.max()),'changed_nodes':len(accepted),'moves':accepted,'seconds':time.perf_counter()-started}
            records.append(record);save(folder/'progress.json',records)
            print({'mode':mode,**{k:v for k,v in record.items() if k not in ('moves','before','available_budget')}},flush=True)
            measured=after
        afterhist=np.bincount(squared,weights=frequency,minlength=len(root)).astype(np.int64)
        np.save(folder/'after-hist.npy',afterhist);after_metrics=hist_metrics(afterhist)
        candidate=folder/'candidate';candidate.mkdir()
        for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage4.slut'):shutil.copyfile(args.best/name,candidate/name)
        io.save_sparse(candidate/'stage2.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
        strict=after_metrics['max']<before_metrics['max'] or after_metrics['p99']<before_metrics['p99']
        eligible=bool(strict and all(after_metrics[k]<=before_metrics[k]+1e-12 for k in ('mean','rms','cvar_1pct')) and
            measured[1]<=initial[1]+1e-12 and measured[3]<=initial[3]+1e-12)
        summaries[mode]={'before':before_metrics,'after':after_metrics,'before_objectives':initial.tolist(),'after_objectives':measured.tolist(),
            'stage2_sha256':digest(candidate/'stage2.slut'),'changed_components':int(np.count_nonzero(current.nodes!=original.nodes)),
            'eligible_for_independent_final_checks':eligible,'scope':'完整加权联合支撑；新四级全域、native、百图及速度尚未验收。'}
        save(folder/'summary.json',summaries[mode])
    save(args.output/'summary.json',summaries)


if __name__=='__main__':main()
