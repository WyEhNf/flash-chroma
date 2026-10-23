"""完整联合频数压缩支撑上，固定当前最佳前三级，仅补末级±1单扫。"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc,channel_joint_nodes as cj,channel_arrival_nodes as an,io,study_provenance
from run_channel_tail_nodes import load_model,digest,save
from certify_cinema_prefix_bound import key,rgb
from check_channel_arrival_nodes import compact_design
from accept_channel_coordinates import hist_metrics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root',type=Path,required=True);parser.add_argument('--first-folder',type=Path,required=True)
    parser.add_argument('--cube',type=Path,required=True);parser.add_argument('--contract',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('不覆盖新支撑研究')
    args.output.mkdir(parents=True);cache=args.cache_root.resolve();numba.set_num_threads(4)
    plan=ROOT/'experiments/p16-arrival-last-unit-v1.json'
    paths={'first':args.first_folder/'model.npz','last':args.first_folder/'stage4.slut',
        'stage2':cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage2.slut',
        'stage3':cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut',
        'reference':cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
        'points':cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy',
        'mass':cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy','cube':args.cube,'contract':args.contract}
    expected={'first':'0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030',
        'last':'fcc15bc8147bc865e534644460ccda3e51f21e8979e21db2fa5bd7e574ffdb67',
        'stage2':'933a4311800dabfafdec534cc149c56aeb7043e5e57df8bef4dd174058b57650',
        'stage3':'95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234',
        'reference':'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690',
        'points':'fac03692667ab8d5220a4a09035b420d96037094c101b91011de303209ccaaea',
        'mass':'1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e',
        'cube':'150bd55ede2419b3ede748705adad388562137e3144de7aaebb929ee4f066c6a'}
    hashes={k:digest(v) for k,v in paths.items()}
    if any(hashes[k]!=v for k,v in expected.items()):raise ValueError('输入不属于已冻结当前最佳整链')
    import json
    contract=json.loads(args.contract.read_text(encoding='utf-8'))
    if contract.get('pass') is not True:raise ValueError('缺少独立有限合同')
    sources=[Path(__file__),plan,ROOT/'python/lutlab/channel_arrival_nodes.py',ROOT/'scripts/check_channel_arrival_nodes.py',
        ROOT/'scripts/certify_cinema_prefix_bound.py',ROOT/'scripts/run_channel_tail_nodes.py',ROOT/'python/lutlab/channel_coordinates.py',
        ROOT/'python/lutlab/channel_global_nodes.py',ROOT/'python/lutlab/channel_joint_nodes.py',ROOT/'python/lutlab/channel_tail_nodes.py',
        ROOT/'python/lutlab/io.py',ROOT/'python/lutlab/interp.py',ROOT/'scripts/accept_channel_coordinates.py']
    save(args.output/'run.json',{'inputs':{k:{'path':str(paths[k]),'sha256':v} for k,v in hashes.items()},
        'sources':{f.relative_to(ROOT).as_posix():digest(f) for f in sources},'plan':json.loads(plan.read_text(encoding='utf-8')),
        'environment':study_provenance.environment_fingerprint(),'numba_threads':4,
        'test_type':'全域联合频数无损压缩与拟合研究；原生/百图/速度另验'})
    first=load_model(paths['first']);prefix=[first]+[cc.from_sparse(io.load_sparse(paths[n],competition=True)) for n in ('stage2','stage3')]
    original=cc.from_sparse(io.load_sparse(paths['last'],competition=True))
    points=np.load(paths['points'],mmap_mode='r');reference=np.load(paths['reference'],mmap_mode='r')
    rawmass=np.load(paths['mass'],mmap_mode='r');baseline=np.memmap(paths['cube'],dtype=np.uint8,mode='r',shape=(256**3,3))
    if any(v.shape!=(256**3,3) or v.dtype!=np.uint8 for v in (points,reference)) or rawmass.shape!=(256**3,):
        raise ValueError('完整支撑或训练质量形状不符')
    totalmass=float(rawmass.sum(dtype=np.float64));root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64))
    groups={};hist=np.zeros(len(root),np.int64);train_distance=0.;started=time.perf_counter()
    for start in range(0,len(points),1<<18):
        stop=min(start+(1<<18),len(points));reached=points[start:stop]
        np.testing.assert_array_equal(key(reached),np.arange(start,stop,dtype=np.uint32))
        for model in prefix:reached=cc.predict(model,reached)
        np.testing.assert_array_equal(cc.predict(original,reached),baseline[start:stop])
        joint=(key(reached).astype(np.uint64)<<24)|key(reference[start:stop]).astype(np.uint64)
        unique,index,inverse,counts=np.unique(joint,return_index=True,return_inverse=True,return_counts=True)
        train=np.bincount(inverse,weights=rawmass[start:stop],minlength=len(unique))
        for pair,count,weight,representative in zip(unique,counts,train,index):
            value=groups.get(int(pair))
            if value is None:groups[int(pair)]=[int(count),float(weight),int(start+representative)]
            else:value[0]+=int(count);value[1]+=float(weight)
        delta=baseline[start:stop].astype(np.int32)-reference[start:stop].astype(np.int32)
        square=np.sum(delta*delta,axis=1,dtype=np.int32);hist+=np.bincount(square,minlength=len(root))
        train_distance+=float(np.asarray(rawmass[start:stop],np.float64)@root[square])/totalmass
        if stop%(1<<22)==0:print({'compressed':stop,'joint_pairs':len(groups),'seconds':time.perf_counter()-started},flush=True)
    pairs=np.asarray(sorted(groups),np.uint64);frequency=np.asarray([groups[int(k)][0] for k in pairs],np.int64)
    mass=np.asarray([groups[int(k)][1]/totalmass for k in pairs],np.float64)
    source=np.asarray([groups[int(k)][2] for k in pairs],np.uint32)
    arrivals=rgb((pairs>>24).astype(np.uint32));gold=rgb((pairs&0xffffff).astype(np.uint32))
    if frequency.sum()!=256**3 or abs(float(mass.sum())-1)>1e-12:raise AssertionError('联合频数未保留全部输入/训练质量')
    del groups
    np.savez_compressed(args.output/'joint-support.npz',arrivals=arrivals,reference=gold,frequency=frequency,mass=mass,representative_source=source)
    output=cc.predict(original,arrivals);initial,square=an.measure(output,gold,points,frequency,mass,12,58)
    compressed_hist=np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64)
    np.testing.assert_array_equal(hist,compressed_hist)
    if abs(initial[1]-train_distance)>1e-11:raise AssertionError('压缩训练mean不等于原完整输入')
    np.save(args.output/'before-hist.npy',hist)
    indices,weights,active,colours=compact_design(original,arrivals);nodes=original.nodes.reshape(-1,3)[active].copy()
    acc,_=cj.accumulate(indices,weights,nodes,gold)
    np.testing.assert_array_equal(output,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
    caps=np.maximum(58,square);measured=initial.copy();current=original;records=[]
    for colour in range(8):
        change,bad,invalid=an.gains(indices,weights,acc,gold,points,frequency,mass,nodes,colours,colour,caps,root,4,12,58,cj.DIRECTIONS,1)
        if invalid:raise AssertionError('完整联合支撑几何/cap错误')
        moves,predicted,accepted=an.select(change,bad,colours,colour,cj.DIRECTIONS)
        nodes=(nodes.astype(np.int32)+moves).astype(np.uint8);physical=current.nodes.copy();physical.reshape(-1,3)[active]=nodes
        current=cc.ChannelLut(original.grid,physical,original.idx,original.channel_frac)
        an.apply_accumulator(indices,weights,acc,moves);fresh=cc.predict(current,arrivals)
        np.testing.assert_array_equal(fresh,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
        after,square=an.measure(fresh,gold,points,frequency,mass,12,58)
        error=float(np.max(np.abs(after-measured-predicted)))
        if error>1e-5 or np.any(after>measured+1e-5) or np.any(square>caps):raise AssertionError('完整联合支撑fresh预算不符')
        for entry in accepted:entry['physical_node']=int(active[entry['node']])
        records.append({'colour':colour,'changed_nodes':len(accepted),'gain_error':error,'before':measured.tolist(),
            'after':after.tolist(),'max_squared':int(square.max()),'moves':accepted,'seconds':time.perf_counter()-started})
        save(args.output/'progress.json',records);print({k:v for k,v in records[-1].items() if k not in ('moves','before')},flush=True)
        measured=after
    afterhist=np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64);np.save(args.output/'after-hist.npy',afterhist)
    before_metrics,after_metrics=hist_metrics(hist),hist_metrics(afterhist)
    candidate=args.output/'candidate';candidate.mkdir()
    for name in ('model.npz','candidate-base.slut','channel-frac.bin'):shutil.copyfile(args.first_folder/name,candidate/name)
    io.save_sparse(candidate/'stage4.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
    strict=after_metrics['max']<before_metrics['max'] or after_metrics['p99']<before_metrics['p99']
    eligible=bool(strict and all(after_metrics[k]<=before_metrics[k]+1e-12 for k in ('mean','rms','cvar_1pct')) and measured[1]<=initial[1]+1e-12)
    save(args.output/'summary.json',{'before':before_metrics,'after':after_metrics,'before_objectives':initial.tolist(),
        'after_objectives':measured.tolist(),'joint_support_rows':len(pairs),'unique_arrivals':len(np.unique(pairs>>24)),
        'active_nodes':len(active),'all_physical_nodes':original.m**3,'geometry_bytes':indices.nbytes+weights.nbytes,
        'private_gain_bytes':4*9*26*len(active)*8,'changed_components':int(np.count_nonzero(current.nodes!=original.nodes)),
        'stage4_sha256':digest(candidate/'stage4.slut'),'training_mean_absolute_error':abs(initial[1]-train_distance),
        'eligible_for_independent_final_checks':eligible,'new_runtime_bytes':0,'seconds':time.perf_counter()-started,
        'limits':'联合频数完整覆盖，不是独立完整域新前向或原生正确性；百图未读取。只拟合末级，不含native速度。'})


if __name__=='__main__':main()
