"""在新第二级best后无损再分组，一次末级节点扫描争取max49或p99<3。"""
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
from run_channel_tail_nodes import digest,save
from certify_cinema_prefix_bound import key,rgb
from check_channel_arrival_nodes import compact_design
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--study',type=Path,required=True)
    p.add_argument('--accept',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖新末级试验')
    args.output.mkdir(parents=True);numba.set_num_threads(4);started=time.perf_counter()
    previous=json.loads((args.study/'run.json').read_text(encoding='utf-8'))
    for name,sha in previous['sources'].items():
        if digest(ROOT/name)!=sha:raise ValueError('原执行源已变')
    for value in previous['inputs'].values():
        if digest(value['path'])!=value['sha256']:raise ValueError('原完整支撑输入已变')
    best=args.study/'max_first/candidate';cube=args.accept/'candidate.rgb'
    manifest=json.loads((ROOT/'report/data/p16-cinema-second-nodes-v1/manifest.json').read_text(encoding='utf-8'))
    recorded=manifest['zip_members']
    for relative in ('joint-support.npz','max_first/after-hist.npy','max_first/candidate/model.npz',
        'max_first/candidate/candidate-base.slut','max_first/candidate/channel-frac.bin'):
        if digest(args.study/relative)!=recorded['results/cinema-second-nodes-v1/'+relative]['sha256']:
            raise ValueError('前阶段已发布支撑/候选原字节不符：'+relative)
    if digest(cube)!='143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e':raise ValueError('不是冻结max_first原始流')
    if digest(best/'stage2.slut')!='904e30a1c0f805175b0b9518949e4e96c9ff2a7e7980978ed8e90fd1282bd924':raise ValueError('第二级起点变更')
    if digest(best/'stage4.slut')!='5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386':raise ValueError('末级起点变更')
    plan=ROOT/'experiments/p16-cinema-post-second-last-v1.json'
    sources=[Path(__file__),plan,*[ROOT/name for name in previous['sources'] if name.endswith('.py')]]
    save(args.output/'run.json',{'previous_run_sha256':digest(args.study/'run.json'),'joint_support_sha256':digest(args.study/'joint-support.npz'),
        'baseline_cube_sha256':digest(cube),'stage2_sha256':digest(best/'stage2.slut'),'stage4_sha256':digest(best/'stage4.slut'),
        'sources':{path.relative_to(ROOT).as_posix():digest(path) for path in sources},'plan':json.loads(plan.read_text(encoding='utf-8')),
        'environment':study_provenance.environment_fingerprint(),'numba_threads':4,'test_type':'完整无损支撑再分组及末级拟合，无照片/native/性能'})
    with np.load(args.study/'joint-support.npz') as data:
        old_arrivals,old_gold,old_frequency,old_mass,old_source=[data[name] for name in ('arrivals','reference','frequency','mass','representative_source')]
    second=cc.from_sparse(io.load_sparse(best/'stage2.slut',competition=True))
    third=cc.from_sparse(io.load_sparse(Path(previous['inputs']['stage3']['path']),competition=True))
    original=cc.from_sparse(io.load_sparse(best/'stage4.slut',competition=True))
    reached=old_arrivals
    for model in (second,third):
        fresh=cc.predict(model,reached);np.testing.assert_array_equal(fresh,integer_oracle(model,reached));reached=fresh
    baseline=np.memmap(cube,np.uint8,'r',shape=(256**3,3));np.testing.assert_array_equal(cc.predict(original,reached),baseline[old_source])
    pairs,inverse=np.unique((key(reached).astype(np.uint64)<<24)|key(old_gold).astype(np.uint64),return_inverse=True)
    frequency=np.zeros(len(pairs),np.int64);mass=np.zeros(len(pairs),np.float64)
    source=np.full(len(pairs),np.iinfo(np.uint32).max,np.uint32)
    np.add.at(frequency,inverse,old_frequency);np.add.at(mass,inverse,old_mass);np.minimum.at(source,inverse,old_source)
    arrivals=rgb((pairs>>24).astype(np.uint32));gold=rgb((pairs&0xffffff).astype(np.uint32))
    assert frequency.sum()==256**3 and abs(float(mass.sum())-1)<1e-12
    np.savez_compressed(args.output/'joint-support.npz',arrivals=arrivals,reference=gold,frequency=frequency,mass=mass,representative_source=source)
    suffix=np.load(previous['inputs']['points']['path'],mmap_mode='r');output=cc.predict(original,arrivals)
    np.testing.assert_array_equal(output,baseline[source]);initial,square=an.measure(output,gold,suffix,frequency,mass,8,49)
    root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64));before_hist=np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64)
    np.testing.assert_array_equal(before_hist,np.load(args.study/'max_first/after-hist.npy'))
    np.save(args.output/'before-hist.npy',before_hist);before_metrics=hist_metrics(before_hist)
    indices,weights,active,colours=compact_design(original,arrivals);initial_nodes=original.nodes.reshape(-1,3)[active].copy()
    initial_acc,_=cj.accumulate(indices,weights,initial_nodes,gold);caps=np.maximum(49,square)
    np.testing.assert_array_equal(output,((initial_acc+io.ONE//2)>>io.Q).astype(np.uint8))
    directions=np.concatenate((cj.DIRECTIONS,mx.DIRECTIONS),axis=0);summaries={}
    save(args.output/'profile.json',{'joint_rows':len(pairs),'unique_arrivals':len(np.unique(pairs>>24)),'active_nodes':len(active),
        'design_bytes':indices.nbytes+weights.nbytes,'private_gain_bytes':4*9*78*len(active)*8,'initial_objectives':initial.tolist()})
    for mode,target in (('max_first',7),('p99_first',6)):
        folder=args.output/mode;folder.mkdir();nodes=initial_nodes.copy();acc=initial_acc.copy();current=original
        measured=initial.copy();records=[]
        for colour in range(8):
            change,bad,invalid=an.gains(indices,weights,acc,gold,suffix,frequency,mass,nodes,colours,colour,caps,root,4,8,49,directions,4)
            if invalid:raise AssertionError('末级支撑parity/cap错误')
            allowance=initial-measured;allowance[6:8]=0
            if np.any(allowance<-1e-7):raise AssertionError('不可预支预算')
            moves,predicted,accepted=priority.select(change,bad,colours,colour,directions,np.maximum(allowance,0),target)
            nodes=(nodes.astype(np.int32)+moves).astype(np.uint8);physical=original.nodes.copy();physical.reshape(-1,3)[active]=nodes
            current=cc.ChannelLut(original.grid,physical,original.idx,original.channel_frac)
            an.apply_accumulator(indices,weights,acc,moves);fresh=cc.predict(current,arrivals)
            np.testing.assert_array_equal(fresh,((acc+io.ONE//2)>>io.Q).astype(np.uint8));np.testing.assert_array_equal(fresh,integer_oracle(current,arrivals))
            after,squared=an.measure(fresh,gold,suffix,frequency,mass,8,49);error=float(np.max(np.abs(after-measured-predicted)))
            if error>1e-5 or np.any(after>initial+1e-5) or np.any(after[6:8]>measured[6:8]) or np.any(squared>caps):raise AssertionError('末级绝对预算错误')
            for entry in accepted:entry['physical_node']=int(active[entry['node']])
            entry={'colour':colour,'before':measured.tolist(),'after':after.tolist(),'gain_error':error,'max_squared':int(squared.max()),
                'changed_nodes':len(accepted),'moves':accepted,'seconds':time.perf_counter()-started}
            records.append(entry);save(folder/'progress.json',records);print({'mode':mode,**{k:v for k,v in entry.items() if k not in ('before','moves')}},flush=True)
            measured=after
        hist=np.bincount(squared,weights=frequency,minlength=len(root)).astype(np.int64);np.save(folder/'after-hist.npy',hist)
        after_metrics=hist_metrics(hist);candidate=folder/'candidate';candidate.mkdir()
        for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage2.slut'):shutil.copyfile(best/name,candidate/name)
        io.save_sparse(candidate/'stage4.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
        strict=after_metrics['max']<before_metrics['max'] or after_metrics['p99']<before_metrics['p99']
        eligible=bool(strict and all(after_metrics[k]<=before_metrics[k]+1e-12 for k in ('mean','rms','cvar_1pct')) and measured[1]<=initial[1]+1e-12 and measured[3]<=initial[3]+1e-12)
        summaries[mode]={'before':before_metrics,'after':after_metrics,'after_objectives':measured.tolist(),
            'changed_components':int(np.count_nonzero(current.nodes!=original.nodes)),'stage4_sha256':digest(candidate/'stage4.slut'),
            'eligible_for_independent_final_checks':eligible,'scope':'完整支撑拟合，新四级全域/native/百图/速度另验，不升级综合best。'}
        save(folder/'summary.json',summaries[mode])
    save(args.output/'summary.json',summaries)


if __name__=='__main__':main()
