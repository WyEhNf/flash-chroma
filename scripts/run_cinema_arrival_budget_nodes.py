"""复用完整联合支撑，在固定best整体预算内消耗先前mean余额换取max下降。"""
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
from lutlab import channel_coordinates as cc,channel_joint_nodes as cj,channel_arrival_nodes as an
from lutlab import channel_arrival_budget_nodes as budget,io,study_provenance
from run_channel_tail_nodes import digest,save
from check_channel_arrival_nodes import compact_design
from accept_channel_coordinates import hist_metrics
from verify_channel_coordinates import integer_oracle


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖独立预算研究')
    args.output.mkdir(parents=True);numba.set_num_threads(4)
    previous=args.previous;run=json.loads((previous/'run.json').read_text(encoding='utf-8'))
    summary=json.loads((previous/'summary.json').read_text(encoding='utf-8'))
    for name in ('first','last','stage2','stage3','reference','points','mass','cube','contract'):
        item=run['inputs'][name]
        if digest(item['path'])!=item['sha256']:raise ValueError('前阶段完整支撑输入身份改变')
    for name,sha in run['sources'].items():
        if digest(ROOT/name)!=sha:raise ValueError('前阶段实际执行源已改变')
    candidate=previous/'candidate/stage4.slut'
    if digest(candidate)!=summary['stage4_sha256']:raise ValueError('中间候选身份改变')
    plan=ROOT/'experiments/p16-arrival-last-budget-v1.json'
    sources=[Path(__file__),ROOT/'python/lutlab/channel_arrival_budget_nodes.py',ROOT/'scripts/verify_channel_coordinates.py',plan]
    save(args.output/'run.json',{'previous_run_sha256':digest(previous/'run.json'),'previous_summary_sha256':digest(previous/'summary.json'),
        'joint_support_sha256':digest(previous/'joint-support.npz'),'starting_stage4_sha256':digest(candidate),
        'sources':{f.relative_to(ROOT).as_posix():digest(f) for f in sources},'previous_sources':run['sources'],
        'plan':json.loads(plan.read_text(encoding='utf-8')),'environment':study_provenance.environment_fingerprint(),
        'test_type':'固定完整域九预算的新单次末级拟合，无照片/运行时性能','numba_threads':4})
    with np.load(previous/'joint-support.npz') as data:
        arrivals,gold,frequency,mass=[data[name] for name in ('arrivals','reference','frequency','mass')]
    if frequency.dtype!=np.int64 or frequency.sum()!=256**3 or abs(float(mass.sum())-1)>1e-12:raise AssertionError('joint支持频数错误')
    suffix=np.load(run['inputs']['points']['path'],mmap_mode='r')
    baseline=cc.from_sparse(io.load_sparse(Path(run['inputs']['last']['path']),competition=True))
    current=cc.from_sparse(io.load_sparse(candidate,competition=True));original=current
    before_baseline,old_square=an.measure(cc.predict(baseline,arrivals),gold,suffix,frequency,mass,12,58)
    np.testing.assert_allclose(before_baseline,summary['before_objectives'],rtol=0,atol=1e-7)
    measured,square=an.measure(cc.predict(current,arrivals),gold,suffix,frequency,mass,12,58)
    np.testing.assert_allclose(measured,summary['after_objectives'],rtol=0,atol=1e-7)
    initial=measured.copy();caps=np.maximum(58,old_square)
    indices,weights,active,colours=compact_design(current,arrivals);nodes=current.nodes.reshape(-1,3)[active].copy()
    acc,_=cj.accumulate(indices,weights,nodes,gold);root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64))
    records=[];started=time.perf_counter()
    for colour in range(8):
        change,bad,invalid=an.gains(indices,weights,acc,gold,suffix,frequency,mass,nodes,colours,colour,caps,root,4,12,58,cj.DIRECTIONS,1)
        if invalid:raise AssertionError('预算阶段完整支撑几何/cap不符')
        allowance=before_baseline-measured;allowance[7]=0
        if np.any(allowance<-1e-7):raise AssertionError('尚未取得的预算不能预支')
        moves,predicted,accepted=budget.select(change,bad,colours,colour,cj.DIRECTIONS,np.maximum(allowance,0))
        nodes=(nodes.astype(np.int32)+moves).astype(np.uint8);physical=current.nodes.copy();physical.reshape(-1,3)[active]=nodes
        current=cc.ChannelLut(original.grid,physical,original.idx,original.channel_frac)
        an.apply_accumulator(indices,weights,acc,moves);fresh=cc.predict(current,arrivals)
        np.testing.assert_array_equal(fresh,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
        np.testing.assert_array_equal(fresh,integer_oracle(current,arrivals))
        after,square=an.measure(fresh,gold,suffix,frequency,mass,12,58);error=float(np.max(np.abs(after-measured-predicted)))
        if error>1e-5 or np.any(after>before_baseline+1e-5) or after[7]>measured[7] or np.any(square>caps):raise AssertionError('固定绝对预算/fresh/cap错误')
        for item in accepted:item['physical_node']=int(active[item['node']])
        entry={'colour':colour,'after':after.tolist(),'before':measured.tolist(),'available_budget':allowance.tolist(),
            'gain_error':error,'changed_nodes':len(accepted),'prior_budget_exchanges':sum(v['uses_prior_budget'] for v in accepted),
            'max_squared':int(square.max()),'moves':accepted,'seconds':time.perf_counter()-started}
        records.append(entry);save(args.output/'progress.json',records)
        print({k:v for k,v in entry.items() if k not in ('moves','before','available_budget')},flush=True);measured=after
    hist=np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64);np.save(args.output/'after-hist.npy',hist)
    after_metrics=hist_metrics(hist);before_metrics=summary['before']
    candidate_folder=args.output/'candidate';candidate_folder.mkdir()
    for name in ('model.npz','candidate-base.slut','channel-frac.bin'):shutil.copyfile(previous/'candidate'/name,candidate_folder/name)
    io.save_sparse(candidate_folder/'stage4.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
    strict=after_metrics['max']<before_metrics['max'] or after_metrics['p99']<before_metrics['p99']
    eligible=bool(strict and all(after_metrics[k]<=before_metrics[k]+1e-12 for k in ('mean','rms','cvar_1pct')) and measured[1]<=before_baseline[1]+1e-12)
    save(args.output/'summary.json',{'before_best':before_metrics,'after':after_metrics,'intermediate_start':summary['after'],
        'before_best_objectives':before_baseline.tolist(),'intermediate_objectives':initial.tolist(),'after_objectives':measured.tolist(),
        'stage4_sha256':digest(candidate_folder/'stage4.slut'),'eligible_for_independent_final_checks':eligible,
        'changed_components_from_intermediate':int(np.count_nonzero(current.nodes!=original.nodes)),
        'changed_components_from_best':int(np.count_nonzero(current.nodes!=baseline.nodes)),
        'joint_support_rows':len(arrivals),'active_nodes':len(active),'seconds':time.perf_counter()-started,
        'limits':'可消费前阶段已取得余额，不改前阶段原件；完整域新前向/独立四级/百图/native/速度尚未执行。'})


if __name__=='__main__':main()
