"""精确验证不可区分原色对，以整数距离给固定前缀的max下界。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc,io
from lutlab.integer_rgb_ball import intersection
from run_channel_tail_nodes import digest,save,load_model
from check_cinema_prefix_certificate import python_pixel


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖精确原色对证书')
    prior=ROOT/'artifacts/cinema-arrival-last-budget-v1';joint=ROOT/'artifacts/cinema-arrival-last-unit-v1/joint-support.npz'
    run=json.loads((ROOT/'artifacts/cinema-arrival-last-unit-v1/run.json').read_text(encoding='utf-8'))
    parent=json.loads((prior/'run.json').read_text(encoding='utf-8'));plan=ROOT/'experiments/p16-arrival-pair-bound-v1.json'
    if digest(joint)!=parent['joint_support_sha256']:raise ValueError('完整联合支撑不同')
    for name in ('first','stage2','stage3','reference'):
        if digest(run['inputs'][name]['path'])!=run['inputs'][name]['sha256']:raise ValueError('前缀/参考身份不同')
    reference=np.load(run['inputs']['reference']['path'],mmap_mode='r')
    prefix=[load_model(Path(run['inputs']['first']['path']))]+[cc.from_sparse(io.load_sparse(Path(run['inputs'][name]['path']),competition=True)) for name in ('stage2','stage3')]
    last_path=prior/'candidate/stage4.slut'
    if digest(last_path)!='5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386':raise ValueError('末级不是已验收新best')
    last=cc.from_sparse(io.load_sparse(last_path,competition=True))
    with np.load(joint) as data:arrivals,gold,frequency,source=[data[n] for n in ('arrivals','reference','frequency','representative_source')]
    if frequency.dtype!=np.int64 or frequency.sum()!=256**3:raise AssertionError('不是完整联合频数')
    prediction=np.asarray([python_pixel(last,point.tolist()) for point in arrivals],np.uint8)
    delta=prediction.astype(np.int32)-gold.astype(np.int32);square=np.sum(delta*delta,axis=1)
    if square.max()!=57:raise AssertionError('联合支撑max不是57')
    codes=(arrivals[:,0].astype(np.uint32)<<16)|(arrivals[:,1].astype(np.uint32)<<8)|arrivals[:,2]
    groups=[];certificates=[]
    for code in np.unique(codes[square==57]):
        selected=np.flatnonzero(codes==code);ball=intersection(gold[selected],56)
        groups.append({'arrived_rgb':arrivals[selected[0]].tolist(),'reference_rgb':gold[selected].tolist(),
            'source_rgb_codes':source[selected].tolist(),'target_ball':ball})
        for a,b in itertools.combinations(selected,2):
            ga,gb=gold[a].tolist(),gold[b].tolist();distance=sum((ga[c]-gb[c])**2 for c in range(3))
            if distance<=4*56:continue
            sources=[int(source[a]),int(source[b])];targets=[ga,gb];trace=[]
            values=[[s>>16,(s>>8)&255,s&255] for s in sources]
            for stage,model in enumerate(prefix,1):
                values=[python_pixel(model,v) for v in values]
                trace.append({'stages':stage,'outputs':values,'equal':values[0]==values[1]})
            if not trace[-1]['equal'] or values[0]!=arrivals[a].tolist():raise AssertionError('原色对未在被检前缀相同')
            for s,g in zip(sources,targets):
                if reference[s].tolist()!=g:raise AssertionError('原色对gold与冻结独立参考不符')
            current=prediction[a].tolist()
            if max(sum((current[c]-g[c])**2 for c in range(3)) for g in targets)>57:raise AssertionError('当前输出不能达到57见证')
            lower=(distance+3)//4
            if lower!=57:raise AssertionError('原色对下界与已验收57不符')
            certificates.append({'source_rgb_codes':sources,'source_rgb':[[s>>16,(s>>8)&255,s&255] for s in sources],
                'reference_rgb':targets,'reference_pair_squared_distance':distance,'four_times_target':224,
                'earliest_equal_prefix':next(v['stages'] for v in trace if v['equal']),'prefix_trace':trace,
                'max_squared_integer_lower_bound':lower,'current_output':current})
            break
    earliest=min((v['earliest_equal_prefix'] for v in certificates),default=None)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    save(args.output,{'plan':json.loads(plan.read_text(encoding='utf-8')),'hot_joint_groups':groups,'pair_certificates':certificates,
        'earliest_fixed_prefix_with_proven_lower_bound':earliest,'fixed_prefix_max_squared_lower_bound':57 if earliest is not None else None,
        'proof':'对任意输出y，||a−b||²≤2(||a−y||²+||b−y||²)≤4 max(d²)。同前缀必同输出；当pair d²>224时不能两者都≤56。RGB8平方误差是整数，因此max²≥57。',
        'source_sha256':{f.relative_to(ROOT).as_posix():digest(f) for f in (Path(__file__),plan,ROOT/'scripts/check_cinema_prefix_certificate.py',ROOT/'python/lutlab/integer_rgb_ball.py')},
        'input_sha256':{'joint_support':digest(joint),'previous_budget_run':digest(prior/'run.json'),'stage4':digest(last_path),
            **{name:run['inputs'][name]['sha256'] for name in ('first','stage2','stage3','reference')}},
        'scope':'少量精确见证足以给固定前缀下界，完整max57上界引用此前独立全域验收。未新跑全部RGB/native/照片；不能扩展为可改变首级的模型族全局最优。'})
    print({'hot_groups':len(groups),'pair_certificates':len(certificates),'earliest_fixed_prefix':earliest,'lower_bound_squared':57 if earliest is not None else None},flush=True)


if __name__=='__main__':main()
