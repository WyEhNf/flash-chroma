"""新第二级固定后，联合移动末级全部parity，在固定预算内尝试max50→49。"""
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
from lutlab import integer_target_last_milp as lm,channel_coordinates as cc,channel_arrival_nodes as an,io,study_provenance
from run_channel_tail_nodes import digest,save
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖第二级之后的局部MILP')
    args.output.mkdir(parents=True);numba.set_num_threads(4)
    study=ROOT/'artifacts/cinema-second-nodes-v1';post=ROOT/'artifacts/cinema-post-second-last-v1'
    best=study/'max_first/candidate';stage=best/'stage4.slut';support=post/'joint-support.npz'
    plan=ROOT/'experiments/p16-cinema-second-milp-v1.json';policy=json.loads(plan.read_text(encoding='utf-8'))
    contract=json.loads(args.contract.read_text(encoding='utf-8'))
    if contract.get('pass') is not True:raise ValueError('缺少参数化有限合同')
    for name,sha in contract['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('参数化合同源码已变')
    original=json.loads((study/'run.json').read_text(encoding='utf-8'));postrun=json.loads((post/'run.json').read_text(encoding='utf-8'))
    for name,sha in {**original['sources'],**postrun['sources']}.items():
        if digest(ROOT/name)!=sha:raise ValueError('完整支撑执行源已变')
    if digest(stage)!='5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386':raise ValueError('末级起点不同')
    if digest(best/'stage2.slut')!='904e30a1c0f805175b0b9518949e4e96c9ff2a7e7980978ed8e90fd1282bd924':raise ValueError('第二级不同')
    sources=[Path(__file__),plan,ROOT/'python/lutlab/integer_target_last_milp.py',ROOT/'python/lutlab/integer_last_milp.py',
        ROOT/'scripts/check_integer_target_last_milp.py',ROOT/'scripts/verify_channel_coordinates.py',ROOT/'python/lutlab/channel_arrival_nodes.py']
    save(args.output/'run.json',{'plan':policy,'source_sha256':{path.relative_to(ROOT).as_posix():digest(path) for path in sources},
        'input_sha256':{'stage4':digest(stage),'stage2':digest(best/'stage2.slut'),'support':digest(support),'contract':digest(args.contract),
            'source_study_run':digest(study/'run.json'),'source_post_run':digest(post/'run.json')},
        'prior_sources':{**original['sources'],**postrun['sources']},'environment':study_provenance.environment_fingerprint(),
        'solver_options':{'threads':1,'time_limit':20.,'node_limit':20000,'mip_rel_gap':0.},
        'scope':'完整加权支撑的±2局部节点盒，浮点MILP非形式下界；未读百图/无native/速度'})
    with np.load(support) as data:arrivals,gold,frequency,mass=[data[name] for name in ('arrivals','reference','frequency','mass')]
    if len(arrivals)!=1219 or frequency.dtype!=np.int64 or frequency.sum()!=256**3 or abs(float(mass.sum())-1)>1e-12:raise AssertionError('完整再分组支撑不符')
    suffix_path=Path(original['inputs']['points']['path'])
    if digest(suffix_path)!=original['inputs']['points']['sha256']:raise ValueError('恒等后缀身份不符')
    suffix=np.load(suffix_path,mmap_mode='r');model=cc.from_sparse(io.load_sparse(stage,competition=True))
    before,square=an.measure(integer_oracle(model,arrivals),gold,suffix,frequency,mass,9,49)
    hist=np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64)
    np.testing.assert_array_equal(hist,np.load(post/'before-hist.npy'));baseline=hist_metrics(hist)
    if square.max()!=50 or baseline['p99']!=3:raise AssertionError('不是新第二级已验收起点')
    state=lm.build(model,arrivals,gold,frequency,mass,before,target_squared=49,node_radius=2,p99_squared=9)
    rounds=[];accepted=False;started=time.perf_counter()
    for iteration in range(4):
        with warnings.catch_warnings(record=True) as observed:
            result=milp(state['cost'],integrality=state['integrality'],bounds=state['bounds'],constraints=state['rows'].constraint(),
                options={'threads':1,'time_limit':20.,'node_limit':20000,'mip_rel_gap':0.})
        entry={'iteration':iteration,'status':int(result.status),'message':str(result.message),
            'mip_nodes':int(result.mip_node_count) if getattr(result,'mip_node_count',None) is not None else None,
            'mip_gap':float(result.mip_gap) if getattr(result,'mip_gap',None) is not None and np.isfinite(result.mip_gap) else None,
            'variables':state['rows'].nvar,'constraints':len(state['rows'].lo),'norm_cuts':len(state['seen']),
            'warnings':[str(w.message) for w in observed],'seconds':time.perf_counter()-started}
        if result.x is None:
            entry['outcome']='无incumbent，按冻结预算停止';rounds.append(entry);save(args.output/'progress.json',rounds);break
        np.save(args.output/f'iteration-{iteration}-solver-x.npy',result.x)
        values=np.rint(result.x[state['block']['node']]).astype(np.int32)
        residual=float(np.max(np.abs(result.x[state['block']['node']]-values)))
        if residual>1e-5 or np.any(values<0) or np.any(values>255):raise AssertionError('节点不是合法整数')
        nodes=model.nodes.copy();nodes.reshape(-1,3)[state['active']]=values.astype(np.uint8)
        candidate=cc.ChannelLut(model.grid,nodes,model.idx,model.channel_frac)
        actual_unique=integer_oracle(candidate,state['unique']);solver_y=np.rint(result.x[state['block']['output']]).astype(np.int32)
        mismatch=int(np.count_nonzero(actual_unique.astype(np.int32)!=solver_y))
        if mismatch:
            entry.update(outcome='真实half-up与solver输出不符，拒绝停止',solver_y_mismatches=mismatch)
            rounds.append(entry);save(args.output/'progress.json',rounds);break
        actual=actual_unique[state['inverse']];measured,square=an.measure(actual,gold,suffix,frequency,mass,9,49)
        hist=np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64);quality=hist_metrics(hist)
        exact=bool(square.max()<=49 and all(quality[key]<=baseline[key]+1e-12 for key in ('mean','rms','p99','cvar_1pct'))
            and measured[1]<=before[1]+1e-12 and measured[3]<=before[3]+1e-12 and measured[6]<=before[6])
        entry.update(quality=quality,objectives=measured.tolist(),maximum_integer_residual=residual,
            changed_components=int(np.count_nonzero(nodes!=model.nodes)),exact_all_support_gate=exact)
        if exact:
            accepted=True;folder=args.output/'candidate';folder.mkdir()
            for name in ('model.npz','candidate-base.slut','channel-frac.bin','stage2.slut'):shutil.copyfile(best/name,folder/name)
            io.save_sparse(folder/'stage4.slut',io.SparseLut(candidate.grid,candidate.nodes,candidate.idx,candidate.channel_frac[0]))
            np.save(args.output/'after-hist.npy',hist);entry.update(stage4_sha256=digest(folder/'stage4.slut'),outcome='真实完整支撑通过，仍待新四级/native/百图/速度')
        else:
            delta=actual.astype(np.int32)-gold.astype(np.int32);norm=np.sqrt(np.sum(delta*delta,axis=1))
            underestimated=result.x[state['block']['norm']]<norm-1e-9
            added=sum(lm.add_norm_cut(state,int(i),delta[i]) for i in np.flatnonzero(underestimated))
            entry.update(added_norm_cuts=added,outcome='仅追加合法范数支撑平面' if added else '无新割，按冻结协议停止')
        rounds.append(entry);save(args.output/'progress.json',rounds);print(entry,flush=True)
        if accepted or entry.get('added_norm_cuts',0)==0:break
    save(args.output/'summary.json',{'baseline':baseline,'accepted_for_independent_final_checks':accepted,'rounds':rounds,
        'seconds':time.perf_counter()-started,'limits':'固定前三级/±2盒，浮点求解器非形式全局证明；无照片/native/速度结果。'})


if __name__=='__main__':main()
