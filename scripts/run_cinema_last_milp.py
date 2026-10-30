"""一次冻结的局部整数规划，联合移动parity以尝试max²57→56。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
import warnings
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from scipy.optimize import milp
from lutlab import integer_last_milp as lm,channel_coordinates as cc,channel_arrival_nodes as an,io,study_provenance
from run_channel_tail_nodes import digest,save
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖实际局部MILP')
    args.output.mkdir(parents=True);numba.set_num_threads(4)
    prior=ROOT/'artifacts/cinema-arrival-last-budget-v1';support=ROOT/'artifacts/cinema-arrival-last-unit-v1/joint-support.npz'
    plan=ROOT/'experiments/p16-last-milp-v1.json';policy=json.loads(plan.read_text(encoding='utf-8'))
    stage=prior/'candidate/stage4.slut'
    if digest(stage)!=policy['baseline_stage4_sha256']:raise ValueError('不是当前新best末级')
    contract=json.loads(args.contract.read_text(encoding='utf-8'))
    if contract.get('pass') is not True:raise ValueError('缺少有限MILP合同')
    for name,value in contract['source_sha256'].items():
        if digest(ROOT/name)!=value:raise ValueError('合同执行源改变')
    previous=json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    prior_run=json.loads((prior/'run.json').read_text(encoding='utf-8'))
    if digest(support)!=prior_run['joint_support_sha256'] or previous['stage4_sha256']!=policy['baseline_stage4_sha256']:
        raise ValueError('joint支持或已验收模型身份改变')
    original_run=json.loads((ROOT/'artifacts/cinema-arrival-last-unit-v1/run.json').read_text(encoding='utf-8'))
    for name,value in original_run['sources'].items():
        if digest(ROOT/name)!=value:raise ValueError('完整joint执行源身份改变')
    source=[Path(__file__),ROOT/'python/lutlab/integer_last_milp.py',plan,ROOT/'scripts/check_integer_last_milp.py',
        ROOT/'python/lutlab/channel_arrival_nodes.py',ROOT/'scripts/verify_channel_coordinates.py']
    save(args.output/'run.json',{'plan':policy,'source_sha256':{f.relative_to(ROOT).as_posix():digest(f) for f in source},
        'input_sha256':{'stage4':digest(stage),'joint_support':digest(support),'baseline_summary':digest(prior/'summary.json'),
            'contract':digest(args.contract),'original_joint_run':digest(ROOT/'artifacts/cinema-arrival-last-unit-v1/run.json')},
        'prior_sources':original_run['sources'],'environment':study_provenance.environment_fingerprint(),
        'numba_threads':4,'solver_options':{'threads':1,'time_limit':20.,'node_limit':20000,'mip_rel_gap':0.},
        'scope':'完整加权支撑上的局部盒整数拟合；无照片/native/速度测试，浮点求解器状态不作形式全局证明'})
    with np.load(support) as data:arrivals,gold,frequency,mass=[data[n] for n in ('arrivals','reference','frequency','mass')]
    if frequency.sum()!=256**3 or abs(float(mass.sum())-1)>1e-12:raise AssertionError('完整联合频数错误')
    suffix_path=Path(original_run['inputs']['points']['path'])
    if digest(suffix_path)!=original_run['inputs']['points']['sha256']:raise ValueError('identity后缀不同')
    suffix=np.load(suffix_path,mmap_mode='r');model=cc.from_sparse(io.load_sparse(stage,competition=True))
    before,square=an.measure(integer_oracle(model,arrivals),gold,suffix,frequency,mass,12,56)
    baseline_metrics=hist_metrics(np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64))
    if square.max()!=57:raise AssertionError('当前baseline max不是57')
    baseline=np.asarray(previous['after_objectives'],np.float64)
    for k in (0,1,2,3,4,5,6,8):
        if abs(before[k]-baseline[k])>1e-7:raise AssertionError('已验收起点与实际联合支撑不一致')
    state=lm.build(model,arrivals,gold,frequency,mass,before,target_squared=56,node_radius=2)
    rounds=[];accepted=False;started=time.perf_counter()
    for iteration in range(4):
        with warnings.catch_warnings(record=True) as wr:
            result=milp(state['cost'],integrality=state['integrality'],bounds=state['bounds'],constraints=state['rows'].constraint(),
                options={'threads':1,'time_limit':20.,'node_limit':20000,'mip_rel_gap':0.})
        entry={'iteration':iteration,'status':int(result.status),'message':str(result.message),
            'mip_nodes':int(result.mip_node_count) if getattr(result,'mip_node_count',None) is not None else None,
            'mip_gap':float(result.mip_gap) if getattr(result,'mip_gap',None) is not None and np.isfinite(result.mip_gap) else None,
            'constraints':len(state['rows'].lo),'variables':state['rows'].nvar,'norm_cuts':len(state['seen']),
            'warnings':[str(w.message) for w in wr],'seconds':time.perf_counter()-started}
        if result.x is None:
            entry['outcome']='没有incumbent，按冻结预算停止';rounds.append(entry);save(args.output/'progress.json',rounds);break
        np.save(args.output/f'iteration-{iteration}-solver-x.npy',result.x)
        ids=state['block']['node'];values=np.rint(result.x[ids]).astype(np.int32)
        residual=float(np.max(np.abs(result.x[ids]-values)))
        if residual>1e-5 or np.any(values<0) or np.any(values>255):raise AssertionError('solver节点不是合法整数')
        nodes=model.nodes.copy();nodes.reshape(-1,3)[state['active']]=values.astype(np.uint8)
        candidate=cc.ChannelLut(model.grid,nodes,model.idx,model.channel_frac)
        unique_actual=integer_oracle(candidate,state['unique']);solver_y=np.rint(result.x[state['block']['output']]).astype(np.int32)
        mismatch=int(np.count_nonzero(unique_actual.astype(np.int32)!=solver_y))
        if mismatch:
            entry['outcome']='数值舍入不符，拒绝并停止';entry['solver_y_mismatches']=mismatch;rounds.append(entry);save(args.output/'progress.json',rounds);break
        actual=unique_actual[state['inverse']];measured,square=an.measure(actual,gold,suffix,frequency,mass,12,56)
        hist=np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64);quality=hist_metrics(hist)
        exact=bool(square.max()<=56 and all(quality[k]<=baseline_metrics[k]+1e-12 for k in ('mean','rms','p99','cvar_1pct'))
                   and measured[1]<=before[1]+1e-12 and measured[3]<=before[3]+1e-12 and measured[6]<=before[6])
        entry.update({'quality':quality,'objectives':measured.tolist(),'maximum_integer_residual':residual,
            'changed_components':int(np.count_nonzero(nodes!=model.nodes)),'exact_all_support_gate':exact})
        if exact:
            accepted=True;folder=args.output/'candidate';folder.mkdir()
            for name in ('model.npz','candidate-base.slut','channel-frac.bin'):shutil.copyfile(prior/'candidate'/name,folder/name)
            io.save_sparse(folder/'stage4.slut',io.SparseLut(candidate.grid,candidate.nodes,candidate.idx,candidate.channel_frac[0]));np.save(args.output/'after-hist.npy',hist)
            entry['stage4_sha256']=digest(folder/'stage4.slut');entry['outcome']='实际整数完整支撑过门，仍待独立四级/native/百图'
        else:
            delta=actual.astype(np.int32)-gold.astype(np.int32);true_norm=np.sqrt(np.sum(delta*delta,axis=1))
            underestimated=result.x[state['block']['norm']]<true_norm-1e-9
            added=sum(lm.add_norm_cut(state,int(i),delta[i]) for i in np.flatnonzero(underestimated))
            entry['added_norm_cuts']=added;entry['outcome']='真实指标未过，仅加合法范数支撑平面' if added else '没有新合法割，拒绝并停止'
        rounds.append(entry);save(args.output/'progress.json',rounds);print(entry,flush=True)
        if accepted or entry.get('added_norm_cuts',0)==0:break
    save(args.output/'summary.json',{'baseline':baseline_metrics,'accepted_for_independent_final_checks':accepted,'rounds':rounds,
        'seconds':time.perf_counter()-started,'limits':'仅±2局部盒与固定几何；超时/不可行不证明全模型无解；没有读取100图，没有native性能。'})


if __name__=='__main__':main()
