"""原环境独立u64重放当前完整安全解，按已冻结373a公共mean/p99初门验收。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from lutlab import channel_coordinates as cc,channel_hotspot_support as hs,channel_capped_risk as risk,io,study_provenance
from run_channel_tail_nodes import load_model
from verify_channel_coordinates import integer_oracle
from cinema_current_safe_identity import GATE,sha,verify_frozen


def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True);p.add_argument('--solution',type=Path,required=True)
    p.add_argument('--preflight',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前安全解唯一全支撑验收')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));solution=json.loads(args.solution.read_text(encoding='utf-8'));verify_frozen(problem)
    if solution['problem_sha256']!=sha(args.problem) or solution['preflight_sha256']!=sha(args.preflight) or solution['source_sha256']!=sha(ROOT/'scripts/solve_cinema_current_safe_cpsat.py'):
        raise ValueError('解或预检身份不符')
    preflight=json.loads(args.preflight.read_text(encoding='utf-8'))
    if not preflight['pass'] or solution['model_proto_sha256']!=preflight['model_proto_sha256'] or sha(solution['model_proto_path'])!=solution['model_proto_sha256']:raise ValueError('实际PB不等于预检')
    args.output.mkdir(parents=True)
    if not solution['feasible']:
        save(args.output/'summary.json',{'status':solution['status'],'feasible':False,'eligible_for_independent_final_checks':False,
            'scope':'没有incumbent，按唯一协议STOP；UNKNOWN非无解。'});return
    values=solution['variables'];n=problem['n_node_variables']
    if len(values)!=len(problem['variables']) or any(type(v) is not int for v in values):raise ValueError('不是完整真整数解')
    for value,domain in zip(values,problem['variables']):
        if not domain['lower']<=value<=domain['upper']:raise AssertionError('实际解超域')
    if solution['abs_variables']!=[abs(v) for v in values[:n]] or solution['l1_objective_integer']!=sum(abs(v) for v in values[:n]):raise AssertionError('L1整数值不符')
    for row in problem['rows']:
        raw=sum(c*values[i] for i,c in row['raw_terms']);reduced=sum(c*values[i] for i,c in row['terms'])
        if not row['raw_lower']<=raw<=row['raw_upper'] or not row['lower']<=reduced<=row['upper']:raise AssertionError('违反原始或gcd舍入约束')
    for point in problem['points']:
        if [values[i] for i in point['z_indices']] not in point['allowed_deltas']:raise AssertionError('违反完整危险安全表')
    inputs=problem['inputs'];model=load_model(inputs['first']['path']);nodes=model.nodes.copy();flat=nodes.reshape(-1,3)
    for i,meta in enumerate(problem['variables'][:n]):
        if int(flat[meta['physical_node'],meta['channel']])!=meta['original_value']:raise AssertionError('实际节点原值不符')
        flat[meta['physical_node'],meta['channel']]=meta['original_value']+values[i]
    candidate=cc.ChannelLut(model.grid,nodes,model.idx,model.channel_frac)
    with np.load(problem['source_inputs']['screen']['path']) as data:
        keys=data['keys'].copy();selected=data['selected_nodes'].copy();weights=data['training_counts'].copy();danger=data['dangerous_rows'].copy()
        lower=data['lower_rgb'].copy();upper=data['upper_rgb'].copy();outside=data['outside_hist'].copy();outside_train=data['outside_training_hist'].copy()
        safe_max=data['safe_maximum_squared'].copy();baseline={label:{'uniform':data['baseline_'+label+'_uniform'].copy(),'training':data['baseline_'+label+'_training'].copy()}
            for label in ('a399','best','current741')}
    fixed=np.ones(len(flat),bool);fixed[selected]=False;np.testing.assert_array_equal(flat[fixed],model.nodes.reshape(-1,3)[fixed])
    actual_selected=sorted({v['physical_node'] for v in problem['variables'][:n]});np.testing.assert_array_equal(actual_selected,selected)
    if len(keys)!=80751 or len(danger)!=4985 or int(weights.sum())!=901853:raise ValueError('完整支撑或训练质量不符')
    first=integer_oracle(candidate,hs.rgb(keys));np.testing.assert_array_equal(cc.predict(candidate,hs.rgb(keys)),first)
    if np.any(first<lower) or np.any(first>upper):raise AssertionError('实际首级输出超已证AABB')
    predicted=np.array([[p['original_rgb'][c]+values[p['z_indices'][c]] for c in range(3)] for p in problem['points']],np.uint8)
    np.testing.assert_array_equal(keys[danger],np.array([p['source_key'] for p in problem['points']]))
    np.testing.assert_array_equal(first[danger],predicted)
    suffix=np.load(inputs['suffix']['path'],mmap_mode='r');gold=np.load(inputs['gold']['path'],mmap_mode='r')
    error=suffix[hs.key(first)].astype(np.int32)-gold[keys].astype(np.int32);square=np.sum(error*error,axis=1,dtype=np.int32)
    if np.any(square>safe_max) or square.max()>43 or int(np.flatnonzero(outside)[-1])>41:raise AssertionError('实际共享解违反安全充分上界')
    after_hist=outside+hs.histogram(square,size=len(outside));after_train=outside_train+hs.histogram(square,weights,size=len(outside_train))
    if int(after_hist.sum())!=1<<24 or int(after_train.sum())!=47185920:raise AssertionError('固定外域拼接质量失败')
    comparisons={label:{'uniform':risk.compare_histograms(after_hist,base['uniform']),'training':risk.compare_histograms(after_train,base['training'])} for label,base in baseline.items()}
    failures=[]
    for population in ('uniform','training'):
        for metric in ('mean','p99'):
            if not comparisons['best'][population]['certificates'][metric]['automatically_protected']:failures.append(population+'_'+metric)
    actual_uniform=hs.metrics(after_hist);actual_training=hs.metrics(after_train)
    if actual_uniform['max_squared']>GATE['global_max_squared_upper']:failures.append('global_max43')
    with np.load(inputs['box_replay']['path']) as data:hotspots=data['keys'].copy()
    rows=np.searchsorted(keys,hotspots);np.testing.assert_array_equal(keys[rows],hotspots)
    if len(hotspots)!=145:raise AssertionError('当前145热点不符')
    folder=args.output/'candidate';folder.mkdir()
    with np.load(inputs['first']['path']) as data:content={name:data[name] for name in data.files}
    content['nodes']=nodes;np.savez_compressed(folder/'model.npz',**content)
    io.save_sparse(folder/'candidate-base.slut',io.SparseLut(candidate.grid,candidate.nodes,candidate.idx,candidate.channel_frac[0]))
    for name,filename in (('sidecar','channel-frac.bin'),('stage2','stage2.slut'),('stage4','stage4.slut')):shutil.copyfile(inputs[name]['path'],folder/filename)
    np.savez_compressed(args.output/'replay.npz',keys=keys,first_rgb=first,squared=square,training_counts=weights,
        after_hist=after_hist,after_training_hist=after_train)
    save(args.output/'summary.json',{'status':solution['status'],'feasible':True,'l1_objective_integer':solution['l1_objective_integer'],
        'fresh_support_rows':len(keys),'fresh_danger_rows':len(danger),'fresh_hotspot_rows':len(rows),'hotspots145_max_squared':int(square[rows].max()),
        'support_max_squared':int(square.max()),'outside_support_max_squared':int(np.flatnonzero(outside)[-1]),'u64_numba_mismatches':0,
        'after_uniform':actual_uniform,'after_training':actual_training,'three_denominator_comparisons':comparisons,'initial_gate':GATE,
        'failures':failures,'candidate_npz_sha256':sha(folder/'model.npz'),'eligible_for_independent_final_checks':not failures,
        'environment':study_provenance.environment_fingerprint(),
        'scope':'唯一incumbent的145/4985/80751真实整数重放与公共best初门；RMS/CVaR和相对741退化全量披露，未完成native/100图/速度资格。'})
    print({'failures':failures,'uniform':actual_uniform,'training':actual_training},flush=True)


if __name__=='__main__':main()
