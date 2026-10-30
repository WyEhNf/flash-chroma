"""仅真实首解存在时一次完整支撑u64/Numba与公共best初门验解。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from lutlab import channel_coordinates as cc,channel_hotspot_support as hs,channel_capped_risk as risk,io,study_provenance
from run_channel_tail_nodes import load_model
from verify_channel_coordinates import integer_oracle
from cinema_current_cap40_identity import sha,verify,GATE
OUT=ROOT/'artifacts/cinema-current-cap40-cpsat-v1';ACCEPT=ROOT/'artifacts/cinema-current-cap40-cpsat-accept-v1'


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖新cap40验解')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.parse_args()
    if ACCEPT.exists():raise FileExistsError('不覆盖唯一完整cap40支撑验解')
    path=OUT/'problem.json';problem=json.loads(path.read_text(encoding='utf-8'));verify(problem);solution=json.loads((OUT/'solution.json').read_text(encoding='utf-8'))
    assert solution['problem_sha256']==sha(path) and solution['preflight_sha256']==sha(OUT/'preflight.json') and solution['source_sha256']==sha(ROOT/'scripts/run_cinema_current_cap40_solver.py')
    assert sha(solution['model_proto_path'])==solution['model_proto_sha256'] and not solution['objective_encoded']
    assert solution['feasible']==(solution['status'] in ('FEASIBLE','OPTIMAL'))
    if not solution['feasible']:
        save(ACCEPT/'summary.json',{'status':solution['status'],'feasible':False,'scope':'按唯一状态STOP，不创造候选或将UNKNOWN称无解。'});return
    values=solution['variables'];assert len(values)==12993 and all(type(v) is int for v in values)
    for v,domain in zip(values,problem['variables']):assert domain['lower']<=v<=domain['upper']
    for row in problem['rows']:
        raw=sum(c*values[i] for i,c in row['raw_terms']);reduced=sum(c*values[i] for i,c in row['terms'])
        assert row['raw_lower']<=raw<=row['raw_upper'] and row['lower']<=reduced<=row['upper']
    for point in problem['points']:assert [values[i] for i in point['z_indices']] in point['allowed_deltas']
    inputs=problem['original_inputs'];model=load_model(inputs['first']['path']);nodes=model.nodes.copy();flat=nodes.reshape(-1,3)
    for i,v in enumerate(problem['variables'][:819]):assert int(flat[v['physical_node'],v['channel']])==v['original_value'];flat[v['physical_node'],v['channel']]=v['original_value']+values[i]
    candidate=cc.ChannelLut(model.grid,nodes,model.idx,model.channel_frac)
    with np.load(problem['unit_screen']) as data:
        keys=data['keys'].copy();selected=data['selected_nodes'].copy();weights=data['training_counts'].copy();danger=data['dangerous_rows'].copy();hotspots=data['hotspot_keys'].copy()
        lower=data['lower_rgb'].copy();upper=data['upper_rgb'].copy();outside=data['outside_hist'].copy();outside_train=data['outside_training_hist'].copy();safe_max=data['safe_maximum_squared'].copy()
    assert (len(keys),len(selected),len(danger),len(hotspots),int(weights.sum()))==(171271,273,4058,231,3541732)
    fixed=np.ones(len(flat),bool);fixed[selected]=False;np.testing.assert_array_equal(flat[fixed],model.nodes.reshape(-1,3)[fixed])
    first=integer_oracle(candidate,hs.rgb(keys));np.testing.assert_array_equal(first,cc.predict(candidate,hs.rgb(keys)));assert np.all(first>=lower) and np.all(first<=upper)
    predicted=np.array([[p['original_rgb'][c]+values[p['z_indices'][c]] for c in range(3)] for p in problem['points']],np.uint8)
    np.testing.assert_array_equal(keys[danger],[p['source_key'] for p in problem['points']]);np.testing.assert_array_equal(first[danger],predicted)
    suffix=np.load(inputs['suffix']['path'],mmap_mode='r');gold=np.load(inputs['gold']['path'],mmap_mode='r');error=suffix[hs.key(first)].astype(np.int32)-gold[keys].astype(np.int32);q=np.sum(error*error,axis=1,dtype=np.int32)
    assert np.all(q<=safe_max) and int(q.max())<=40 and int(np.flatnonzero(outside)[-1])==38
    full=outside+hs.histogram(q,size=len(outside));train=outside_train+hs.histogram(q,weights,size=len(outside_train));assert int(full.sum())==1<<24 and int(train.sum())==47185920
    with np.load(inputs['old_screen']['path']) as data:baselines={label:{'uniform':data['baseline_'+label+'_uniform'].copy(),'training':data['baseline_'+label+'_training'].copy()} for label in ('a399','best','current741')}
    with np.load(inputs['histograms']['path']) as data:baselines['current91d']={'uniform':data['cube_candidate'].copy(),'training':data['training60_candidate'].copy()}
    comparisons={label:{'uniform':risk.compare_histograms(full,b['uniform']),'training':risk.compare_histograms(train,b['training'])} for label,b in baselines.items()}
    failures=[population+'_'+metric for population in ('uniform','training') for metric in ('mean','p99') if not comparisons['best'][population]['certificates'][metric]['automatically_protected']]
    uniform,training=hs.metrics(full),hs.metrics(train)
    if uniform['max_squared']>40:failures.append('global_max40')
    rows=np.searchsorted(keys,hotspots);np.testing.assert_array_equal(keys[rows],hotspots)
    folder=ACCEPT/'candidate';folder.mkdir(parents=True)
    with np.load(inputs['first']['path']) as data:content={k:data[k] for k in data.files}
    content['nodes']=nodes;np.savez_compressed(folder/'model.npz',**content);io.save_sparse(folder/'candidate-base.slut',io.SparseLut(candidate.grid,candidate.nodes,candidate.idx,candidate.channel_frac[0]))
    for name,filename in [('sidecar','channel-frac.bin'),('stage2','stage2.slut'),('stage4','stage4.slut')]:shutil.copyfile(inputs[name]['path'],folder/filename)
    np.savez_compressed(ACCEPT/'replay.npz',keys=keys,first_rgb=first,squared=q,training_counts=weights,after_hist=full,after_training_hist=train)
    save(ACCEPT/'summary.json',{'status':solution['status'],'feasible':True,'observed_node_l1':solution['observed_node_l1'],'fresh_support_rows':171271,
        'fresh_tables':4058,'fresh_hotspot_rows':231,'hotspots_max_squared':int(q[rows].max()),'u64_numba_mismatches':0,'after_uniform':uniform,
        'after_training':training,'comparisons':comparisons,'initial_gate':GATE,'failures':failures,'eligible_for_independent_final_checks':not failures,
        'candidate_npz_sha256':sha(folder/'model.npz'),'environment':study_provenance.environment_fingerprint(),
        'scope':'唯一共享首解完整支撑/固定外域/原60公共初门；未验完整native/100逐图或速度，不自动升级。'})
    print({'failures':failures,'uniform':uniform,'training':training},flush=True)


if __name__=='__main__':main()
