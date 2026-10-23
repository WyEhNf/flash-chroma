"""整数RGB球并集穷举给出固定前缀的最少训练超限数下界。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import study_provenance
from run_channel_tail_nodes import digest,save


OFFSETS=np.asarray([(r,g,b) for r in range(-3,4) for g in range(-3,4) for b in range(-3,4) if r*r+g*g+b*b<=11],np.int32)


def best_cover(gold,count,caps,baseline,maximum=255):
    values=[np.asarray(baseline,np.int32).reshape(1,3)]
    if np.any(count>0):values.append((gold[count>0,None,:].astype(np.int32)+OFFSETS[None,:,:]).reshape(-1,3))
    candidates=np.unique(np.concatenate(values),axis=0);candidates=candidates[np.all((candidates>=0)&(candidates<=maximum),axis=1)]
    delta=candidates[:,None,:]-gold[None,:,:].astype(np.int32);square=np.sum(delta*delta,axis=2,dtype=np.int32)
    legal=np.all(square<=caps[None,:],axis=1)
    if not np.any(legal):raise AssertionError('原起点应始终为可行见证')
    costs=(square[legal]>11)@count;slot=int(np.argmin(costs));witness=candidates[legal][slot]
    return int(costs[slot]),witness,int(legal.sum()),len(candidates)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖固定前缀训练下界')
    rng=np.random.default_rng(20261024044);all_output=np.asarray([(r,g,b) for r in range(8) for g in range(8) for b in range(8)],np.int32)
    for trial in range(64):
        gold=rng.integers(0,8,(1+trial%5,3),dtype=np.uint8);count=rng.integers(0,10,len(gold),dtype=np.int64)
        if trial%8==0:count[:]=0
        baseline=rng.integers(0,8,3,dtype=np.int32);caps=np.maximum(rng.integers(0,20,len(gold)),np.sum((baseline-gold.astype(np.int32))**2,axis=1))
        cost,witness,_,_=best_cover(gold,count,caps,baseline,7)
        squared=np.sum((all_output[:,None,:]-gold[None,:,:].astype(np.int32))**2,axis=2)
        expected=int(np.min((squared[np.all(squared<=caps[None,:],axis=1)]>11)@count))
        if cost!=expected or np.any(np.sum((witness-gold.astype(np.int32))**2,axis=1)>caps):raise AssertionError('8^3独立完整穷举不一致')
    probe_path=ROOT/'artifacts/cinema-training-tail-probe-v1.json';probe=json.loads(probe_path.read_text(encoding='utf-8'))
    support=Path(probe['inputs']['joint']['path']);cube_path=Path(probe['inputs']['cube']['path'])
    if digest(support)!=probe['inputs']['joint']['sha256'] or digest(cube_path)!=probe['inputs']['cube']['sha256']:raise ValueError('冻结起点不符')
    with np.load(support) as data:arrivals,gold,mass,source=[data[n] for n in ('arrivals','reference','mass','representative_source')]
    count=np.rint(mass*probe['training_pixels']).astype(np.int64)
    if np.max(np.abs(mass*probe['training_pixels']-count))>1e-6 or int(count.sum())!=probe['training_pixels']:raise AssertionError('训练整数频数不符')
    cube=np.memmap(cube_path,np.uint8,'r',shape=(256**3,3));output=cube[source]
    squared=np.sum((output.astype(np.int32)-gold.astype(np.int32))**2,axis=1,dtype=np.int32);caps=np.maximum(49,squared)
    if int(count@(squared>11))!=probe['squared_11_exceed_count']:raise AssertionError('原流训练计数不符')
    keys=arrivals.astype(np.int64)@np.array([65536,256,1],np.int64);records=[];bound=0
    for key in np.unique(keys):
        mask=keys==key;baseline=output[mask][0]
        np.testing.assert_array_equal(output[mask],np.broadcast_to(baseline,output[mask].shape))
        cost,witness,legal,candidates=best_cover(gold[mask],count[mask],caps[mask],baseline)
        bound+=cost;records.append({'arrival_key':int(key),'support_rows':int(mask.sum()),'training_pixels':int(count[mask].sum()),
            'baseline_above_11':int(count[mask]@(squared[mask]>11)),'minimum_above_11':cost,'witness':witness.tolist(),
            'candidate_count':candidates,'feasible_candidate_count':legal})
    total=probe['training_pixels'];impossible=100*bound>total
    save(args.output,{'source_sha256':digest(Path(__file__)),'plan_sha256':digest(ROOT/'experiments/p16-cinema-training-bound-v1.json'),
        'environment':study_provenance.environment_fingerprint(),'probe_sha256':digest(probe_path),
        'support_sha256':digest(support),'baseline_cube_sha256':digest(cube_path),'finite_exhaustive_cases':64,'finite_domain_outputs':512,
        'integer_ball_offsets':len(OFFSETS),'groups':len(records),'training_pixels':total,'minimum_above_11_lower_bound':bound,
        'minimum_exceed_fraction':bound/total,'fixed_prefix_target_11_impossible_under_caps':impossible,'records':records,
        'scope':'每arrival放松掉共享节点及全局均值后完整RGB整数覆盖的精确最优；总和仅为真实LUT的必要下界。未排除不等于可构造，无新拟合/native/百图/速度。'})
    print({'groups':len(records),'training_pixels':total,'minimum_above_11_lower_bound':bound,'minimum_exceed_fraction':bound/total,
        'fixed_prefix_target_11_impossible_under_caps':impossible},flush=True)


if __name__=='__main__':main()
