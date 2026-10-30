"""固定十一项预算单扫末级，训练尾部目标11，不使用百图重新拟合。"""
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
from lutlab import channel_arrival_nodes as an,channel_training_tail as tt,channel_coordinates as cc
from lutlab import channel_joint_nodes as cj,channel_max_nodes as mx,io,study_provenance
from check_channel_arrival_nodes import compact_design
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics
from run_channel_tail_nodes import save,digest


def training_metrics(square,count):
    hist=np.bincount(square,weights=count,minlength=3*255**2+1).astype(np.int64)
    total=int(hist.sum());cdf=hist.cumsum();rank=(99*total+99)//100
    p99sq=int(np.searchsorted(cdf,rank));position=(total-1)*.99;low=int(np.floor(position));high=int(np.ceil(position))
    lo=int(np.searchsorted(cdf,low+1));hi=int(np.searchsorted(cdf,high+1))
    return {'pixels':total,'cdf_p99_squared':p99sq,'linear_p99':float(np.sqrt(lo)+(position-low)*(np.sqrt(hi)-np.sqrt(lo))),
        'mean':float(count@np.sqrt(square.astype(np.float64))/total),'rms':float(np.sqrt(count@square/total)),
        'above_11_pixels':int(hist[12:].sum()),'maximum_squared':int(np.flatnonzero(hist)[-1])}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--probe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖原60图尾部单扫')
    contract=json.loads(args.contract.read_text(encoding='utf-8'));probe=json.loads(args.probe.read_text(encoding='utf-8'))
    if not contract['pass'] or not probe['fixed_target_11_applicable']:raise ValueError('有限合同或固定阈值适用性未通过')
    for name,sha in contract['sources'].items():
        if digest(ROOT/name)!=sha:raise ValueError('实际合同源已变化：'+name)
    if digest(ROOT/'scripts/probe_cinema_training_tail.py')!=probe['source_sha256']:raise ValueError('只读诊断源已变')
    proposal=ROOT/'experiments/p16-cinema-training-tail-proposal-v1.md'
    if digest(proposal)!=probe['proposal_sha256']:raise ValueError('预先提案已变')
    previous=ROOT/'artifacts/cinema-post-second-last-v1';post=json.loads((previous/'run.json').read_text(encoding='utf-8'))
    for name,sha in post['sources'].items():
        if digest(ROOT/name)!=sha:raise ValueError('前阶段实际执行源已变化：'+name)
    support=previous/'joint-support.npz'
    if digest(support)!=probe['inputs']['joint']['sha256']:raise ValueError('冻结联合支撑已变')
    study=ROOT/'artifacts/cinema-second-nodes-v1';prior=json.loads((study/'run.json').read_text(encoding='utf-8'))
    original_path=study/'max_first/candidate/stage4.slut'
    if digest(original_path)!='5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386':raise ValueError('不能用mean-only末级')
    cube=ROOT/'artifacts/cinema-second-accept-max_first-v1/candidate.rgb'
    if digest(cube)!=probe['inputs']['cube']['sha256']:raise ValueError('完整域起点已变')
    suffix_path=Path(prior['inputs']['points']['path'])
    if digest(suffix_path)!=prior['inputs']['points']['sha256']:raise ValueError('恒等后缀输入已变')
    plan=ROOT/'experiments/p16-cinema-training-tail-v1.json'
    sources={name:digest(ROOT/name) for name in set(post['sources'])|set(contract['sources'])|
        {'scripts/run_cinema_training_tail.py','scripts/probe_cinema_training_tail.py','experiments/p16-cinema-training-tail-v1.json','experiments/p16-cinema-training-tail-proposal-v1.md'}}
    args.output.mkdir(parents=True);numba.set_num_threads(4);started=time.perf_counter()
    save(args.output/'run.json',{'sources':sources,'contract_sha256':digest(args.contract),'probe_sha256':digest(args.probe),
        'support_sha256':digest(support),'baseline_cube_sha256':digest(cube),'original_last_sha256':digest(original_path),
        'suffix_sha256':digest(suffix_path),'plan':json.loads(plan.read_text(encoding='utf-8')),
        'environment':study_provenance.environment_fingerprint(),'numba_threads':4,'test_type':'完整无损支撑上的单次训练尾部拟合；未包含新的百图/native/性能'})
    with np.load(support) as data:arrivals,gold,frequency,mass,source=[data[n] for n in ('arrivals','reference','frequency','mass','representative_source')]
    if frequency.dtype!=np.int64 or int(frequency.sum())!=256**3 or abs(float(mass.sum())-1)>1e-12:raise AssertionError('完整支撑频数不守恒')
    total=60*1024*768;training=np.rint(mass*total).astype(np.int64)
    residual=float(np.max(np.abs(mass*total-training)))
    if residual>1e-6 or int(training.sum())!=total:raise AssertionError('原训练质量不能还原整数频数')
    suffix=np.load(suffix_path,mmap_mode='r');original=cc.from_sparse(io.load_sparse(original_path,competition=True))
    baseline=np.memmap(cube,np.uint8,'r',shape=(256**3,3));output=cc.predict(original,arrivals)
    np.testing.assert_array_equal(output,integer_oracle(original,arrivals));np.testing.assert_array_equal(output,baseline[source])
    initial,square=tt.measure(output,gold,suffix,frequency,mass,training,9,49,11)
    before_hist=np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64)
    np.testing.assert_array_equal(before_hist,np.load(study/'max_first/after-hist.npy'))
    before=hist_metrics(before_hist);before_train=training_metrics(square,training)
    if before_train['cdf_p99_squared']!=probe['generalized_cdf_p99_squared'] or abs(before_train['linear_p99']-probe['numpy_linear_equivalent_p99'])>1e-12 or before_train['above_11_pixels']!=probe['squared_11_exceed_count']:
        raise AssertionError('完整域原始流与压缩训练频数CDF不符')
    indices,weights,active,colours=compact_design(original,arrivals);nodes=original.nodes.reshape(-1,3)[active].copy()
    acc,_=cj.accumulate(indices,weights,nodes,gold);caps=np.maximum(49,square)
    np.testing.assert_array_equal(output,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
    root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64));directions=np.concatenate((cj.DIRECTIONS,mx.DIRECTIONS),axis=0)
    save(args.output/'profile.json',{'joint_rows':len(arrivals),'active_nodes':len(active),'training_pixels':total,
        'training_count_residual_max':residual,'design_bytes':indices.nbytes+weights.nbytes,'private_gain_bytes':4*11*78*len(active)*8,
        'initial_objectives':initial.tolist(),'before_uniform':before,'before_training':before_train})
    measured=initial.copy();records=[];current=original
    for colour in range(8):
        nine,bad,invalid=an.gains(indices,weights,acc,gold,suffix,frequency,mass,nodes,colours,colour,caps,root,4,9,49,directions,4)
        extra,invalid_extra=tt.training_gains(indices,weights,acc,gold,suffix,training,nodes,colours,colour,4,11,directions,4)
        if invalid or invalid_extra:raise AssertionError('完整支撑parity或原cap不符')
        allowance=initial-measured;allowance[[6,7,9]]=0
        if np.any(allowance<-1e-7):raise AssertionError('不允许预支预算')
        moves,predicted,accepted=tt.select(np.concatenate((nine,extra),axis=0),bad,colours,colour,directions,np.maximum(allowance,0))
        nodes=(nodes.astype(np.int32)+moves).astype(np.uint8);physical=original.nodes.copy();physical.reshape(-1,3)[active]=nodes
        current=cc.ChannelLut(original.grid,physical,original.idx,original.channel_frac);an.apply_accumulator(indices,weights,acc,moves)
        fresh=cc.predict(current,arrivals);np.testing.assert_array_equal(fresh,integer_oracle(current,arrivals))
        np.testing.assert_array_equal(fresh,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
        after,square=tt.measure(fresh,gold,suffix,frequency,mass,training,9,49,11);gain_error=float(np.max(np.abs(after-measured-predicted)))
        if gain_error>1e-5 or np.any(after>initial+1e-5) or np.any(after[[6,7,9]]>measured[[6,7,9]]) or np.any(square>caps):raise AssertionError('真实十一项预算或逐点cap失败')
        for entry in accepted:entry['physical_node']=int(active[entry['node']])
        record={'colour':colour,'before':measured.tolist(),'after':after.tolist(),'gain_error':gain_error,
            'training':training_metrics(square,training),'changed_nodes':len(accepted),'moves':accepted,'seconds':time.perf_counter()-started}
        records.append(record);save(args.output/'progress.json',records);print({k:v for k,v in record.items() if k not in ('before','moves')},flush=True);measured=after
    hist=np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64);np.save(args.output/'after-hist.npy',hist)
    after=hist_metrics(hist);after_train=training_metrics(square,training);candidate=args.output/'candidate';candidate.mkdir()
    for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage2.slut'):shutil.copyfile(study/'max_first/candidate'/name,candidate/name)
    io.save_sparse(candidate/'stage4.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
    strict=after_train['cdf_p99_squared']<before_train['cdf_p99_squared'] and after_train['linear_p99']<before_train['linear_p99']
    eligible=bool(strict and all(after[k]<=before[k]+1e-12 for k in ('mean','rms','p99','max','cvar_1pct')) and after_train['mean']<=before_train['mean']+1e-12 and after_train['rms']<=before_train['rms']+1e-12)
    summary={'before_uniform':before,'after_uniform':after,'before_training':before_train,'after_training':after_train,
        'after_objectives':measured.tolist(),'stage4_sha256':digest(candidate/'stage4.slut'),'changed_components':int(np.count_nonzero(current.nodes!=original.nodes)),
        'eligible_for_independent_final_checks':eligible,'scope':'只有训练尾部及绝对门通过才追加完整四级/native/100图。运行时速度、100图改善和正式阈值未由本拟合证明。'}
    save(args.output/'summary.json',summary);print(summary,flush=True)


if __name__=='__main__':main()
