"""从相同已验收起点最多四次坐标扫描，检验训练尾部目标是否可达。"""
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
from run_cinema_training_tail import training_metrics


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖有界训练尾部重复扫描')
    art=ROOT/'artifacts';previous=json.loads((art/'cinema-training-tail-v1/run.json').read_text(encoding='utf-8'))
    for name,sha in previous['sources'].items():
        if digest(ROOT/name)!=sha:raise ValueError('原单扫执行源已变：'+name)
    contract_path=art/'cinema-training-tail-contract-v1.json';probe_path=art/'cinema-training-tail-probe-v1.json'
    if digest(contract_path)!=previous['contract_sha256'] or digest(probe_path)!=previous['probe_sha256']:raise ValueError('旧合同/独立诊断原件不符')
    contract=json.loads(contract_path.read_text(encoding='utf-8'));probe=json.loads(probe_path.read_text(encoding='utf-8'))
    if not contract['pass'] or not probe['fixed_target_11_applicable']:raise ValueError('有限合同或固定目标不通过')
    support=Path(probe['inputs']['joint']['path']);cube_path=Path(probe['inputs']['cube']['path'])
    if digest(support)!=previous['support_sha256'] or digest(cube_path)!=previous['baseline_cube_sha256']:raise ValueError('完整起点支撑或原流已变')
    study=art/'cinema-second-nodes-v1';original_folder=study/'max_first/candidate';last=original_folder/'stage4.slut'
    if digest(last)!=previous['original_last_sha256']:raise ValueError('不得使用未验收新末级作起点')
    prior=json.loads((study/'run.json').read_text(encoding='utf-8'));suffix_path=Path(prior['inputs']['points']['path'])
    if digest(suffix_path)!=previous['suffix_sha256']:raise ValueError('恒等后缀不符')
    plan_path=ROOT/'experiments/p16-cinema-training-cycles-v1.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
    sources={**previous['sources'],'scripts/run_cinema_training_cycles.py':digest(Path(__file__)),
        'experiments/p16-cinema-training-cycles-v1.json':digest(plan_path)}
    args.output.mkdir(parents=True);numba.set_num_threads(4);started=time.perf_counter()
    save(args.output/'run.json',{'sources':sources,'inherited_single_sweep_run_sha256':digest(art/'cinema-training-tail-v1/run.json'),
        'contract_sha256':digest(contract_path),'probe_sha256':digest(probe_path),'support_sha256':digest(support),
        'baseline_cube_sha256':digest(cube_path),'original_last_sha256':digest(last),'suffix_sha256':digest(suffix_path),
        'plan':plan,'environment':study_provenance.environment_fingerprint(),'numba_threads':4,
        'test_type':'同一起点的最多四次完整支撑训练尾部拟合，不是新的原生/百图/速度验收'})
    with np.load(support) as data:arrivals,gold,frequency,mass,source=[data[n] for n in ('arrivals','reference','frequency','mass','representative_source')]
    total=60*1024*768;training=np.rint(mass*total).astype(np.int64)
    if frequency.dtype!=np.int64 or int(frequency.sum())!=256**3 or np.max(np.abs(mass*total-training))>1e-6 or int(training.sum())!=total:raise AssertionError('整数频数不符')
    original=cc.from_sparse(io.load_sparse(last,competition=True));suffix=np.load(suffix_path,mmap_mode='r')
    baseline=np.memmap(cube_path,np.uint8,'r',shape=(256**3,3));output=cc.predict(original,arrivals)
    np.testing.assert_array_equal(output,integer_oracle(original,arrivals));np.testing.assert_array_equal(output,baseline[source])
    initial,square=tt.measure(output,gold,suffix,frequency,mass,training,9,49,11)
    before_hist=np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64)
    np.testing.assert_array_equal(before_hist,np.load(study/'max_first/after-hist.npy'))
    before=hist_metrics(before_hist);before_train=training_metrics(square,training)
    indices,weights,active,colours=compact_design(original,arrivals);nodes=original.nodes.reshape(-1,3)[active].copy()
    acc,_=cj.accumulate(indices,weights,nodes,gold);caps=np.maximum(49,square);root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64))
    np.testing.assert_array_equal(output,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
    directions=np.concatenate((cj.DIRECTIONS,mx.DIRECTIONS),axis=0);measured=initial.copy();records=[];sweeps=[]
    stop_reason='达到预注册最多四扫次';eligible=False;current=original
    for sweep in range(4):
        sweep_start=measured.copy()
        for colour in range(8):
            nine,bad,invalid=an.gains(indices,weights,acc,gold,suffix,frequency,mass,nodes,colours,colour,caps,root,4,9,49,directions,4)
            extra,invalid_extra=tt.training_gains(indices,weights,acc,gold,suffix,training,nodes,colours,colour,4,11,directions,4)
            if invalid or invalid_extra:raise AssertionError('parity或原cap错误')
            allowance=initial-measured;allowance[[6,7,9]]=0
            if np.any(allowance<-1e-7):raise AssertionError('不能预支原起点余额')
            moves,predicted,accepted=tt.select(np.concatenate((nine,extra),axis=0),bad,colours,colour,directions,np.maximum(allowance,0))
            nodes=(nodes.astype(np.int32)+moves).astype(np.uint8);physical=original.nodes.copy();physical.reshape(-1,3)[active]=nodes
            current=cc.ChannelLut(original.grid,physical,original.idx,original.channel_frac);an.apply_accumulator(indices,weights,acc,moves)
            fresh=cc.predict(current,arrivals);np.testing.assert_array_equal(fresh,integer_oracle(current,arrivals))
            np.testing.assert_array_equal(fresh,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
            after,square=tt.measure(fresh,gold,suffix,frequency,mass,training,9,49,11);error=float(np.max(np.abs(after-measured-predicted)))
            if error>1e-5 or np.any(after>initial+1e-5) or np.any(after[[6,7,9]]>measured[[6,7,9]]) or np.any(square>caps):raise AssertionError('独立十一项/cap/收益失败')
            for entry in accepted:entry['physical_node']=int(active[entry['node']])
            records.append({'sweep':sweep,'colour':colour,'before':measured.tolist(),'after':after.tolist(),'gain_error':error,
                'moves':accepted,'seconds':time.perf_counter()-started});save(args.output/'progress.json',records);measured=after
        hist=np.bincount(square,weights=frequency,minlength=len(root)).astype(np.int64);after=hist_metrics(hist);after_train=training_metrics(square,training)
        strict=after_train['cdf_p99_squared']<before_train['cdf_p99_squared'] and after_train['linear_p99']<before_train['linear_p99']
        eligible=bool(strict and all(after[k]<=before[k]+1e-12 for k in ('mean','rms','p99','max','cvar_1pct')) and after_train['mean']<=before_train['mean']+1e-12 and after_train['rms']<=before_train['rms']+1e-12)
        folder=args.output/f'sweep-{sweep+1}';folder.mkdir();np.save(folder/'after-hist.npy',hist)
        io.save_sparse(folder/'stage4.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
        entry={'sweep':sweep+1,'uniform':after,'training':after_train,'after_objectives':measured.tolist(),
            'changed_components':int(np.count_nonzero(current.nodes!=original.nodes)),'stage4_sha256':digest(folder/'stage4.slut'),
            'eligible_for_independent_final_checks':eligible};sweeps.append(entry);save(args.output/'sweeps.json',sweeps);print(entry,flush=True)
        if eligible:stop_reason='达到原定训练严格门与全部非退化预算';break
        if measured[9]>=sweep_start[9]:stop_reason='完整扫次训练超限计数未严格减少，按预注册停止';break
    candidate=args.output/'candidate';candidate.mkdir()
    for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage2.slut'):shutil.copyfile(original_folder/name,candidate/name)
    io.save_sparse(candidate/'stage4.slut',io.SparseLut(current.grid,current.nodes,current.idx,current.channel_frac[0]))
    summary={'before_uniform':before,'before_training':before_train,'after_uniform':after,'after_training':after_train,
        'sweeps_executed':len(sweeps),'batches_executed':len(records),'stop_reason':stop_reason,
        'stage4_sha256':digest(candidate/'stage4.slut'),'changed_components':int(np.count_nonzero(current.nodes!=original.nodes)),
        'eligible_for_independent_final_checks':eligible,'scope':'全部扫次保留；未通过训练严格门不追加原生/百图/速度。旧单扫失败不变。'}
    save(args.output/'summary.json',summary);print(summary,flush=True)


if __name__=='__main__':main()
