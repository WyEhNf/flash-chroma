"""固定91d全部最劣点驱动的完整正支撑与cap40规模检查；不构造CP。"""
from __future__ import annotations
import argparse
import ast
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];CACHE=Path('F:/Hackathon/projects/16-lut-color')
sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from lutlab import channel_coordinates as cc,channel_component_box as component,channel_hotspot_support as hs,channel_capped_risk as risk,study_provenance
from run_channel_tail_nodes import digest,load_model
from run_cinema_first_hotspot import train_counts,TRAINING_PIXELS
from verify_channel_coordinates import integer_oracle
OUT=ROOT/'artifacts/cinema-current-all-max-support-v1'
PLAN=ROOT/'experiments/p16-cinema-current-all-max-support-v1.json'
FIRST=ROOT/'artifacts/cinema-current-feasible-cpsat-accept-v1/candidate'
FULL=ROOT/'artifacts/cinema-current-full-quality-v2'


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖全部最劣点规模证据：'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def verify(frozen):
    for name,expected in frozen['source_sha256'].items():assert digest(ROOT/name)==expected,name
    for spec in frozen['inputs'].values():assert digest(spec['path'])==spec['sha256'],spec['path']


def freeze():
    if OUT.exists():raise FileExistsError('不覆盖全部最劣点阶段')
    source_names=['scripts/screen_cinema_current_all_max.py','scripts/audit_cinema_current_all_max.py',
        'experiments/p16-cinema-current-all-max-support-v1.json','experiments/p16-cinema-current-all-max-support-proposal-v1.md',
        'scripts/check_cinema_current_outside_rank.py','experiments/p16-cinema-current-outside-rank-v1.json',
        'scripts/run_channel_tail_nodes.py','scripts/run_cinema_first_hotspot.py','scripts/verify_channel_coordinates.py',
        *['python/lutlab/'+n for n in ('channel_hotspot_support.py','channel_component_box.py','channel_capped_risk.py','channel_coordinates.py','interp.py','io.py','study_provenance.py')]]
    for name in source_names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
    paths={'first':FIRST/'model.npz','first_slut':FIRST/'candidate-base.slut','sidecar':FIRST/'channel-frac.bin',
        'stage2':FIRST/'stage2.slut','stage3':CACHE/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut','stage4':FIRST/'stage4.slut',
        'cube':FULL/'candidate.rgb','histograms':FULL/'histograms.npz','full_results':FULL/'results.json',
        'gold':CACHE/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
        'mass':CACHE/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy',
        'suffix':ROOT/'artifacts/cinema-first-hotspot-v1/suffix.npy',
        'old_screen':ROOT/'artifacts/cinema-max48-risk-upper-v1/screen.npz',
        'outside_rank':ROOT/'artifacts/cinema-current-outside-rank-v1/results.json'}
    expected={'first':'91d868d72e9eacc482fe26a8568dad4667f0d0ca9a24685432c6cf8991fd36d6',
        'first_slut':'07c9f25252132bb8509a183d97cc59457da5fcdbbe7d0d58618bd74e797b7c95',
        'cube':'728666cbc05f0cd2d9da112ce41a26117d67baee1511760d83df8f8cefe8ed98',
        'histograms':'fe50c015c3ac9f50daee007dccc38a1e09c196980675a23c8e92bd6d01551079',
        'stage2':'904e30a1c0f805175b0b9518949e4e96c9ff2a7e7980978ed8e90fd1282bd924',
        'stage3':'95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234',
        'stage4':'5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386',
        'gold':'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690',
        'mass':'1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e',
        'suffix':'0ced3cb5f1acad4ff15d392dfc52bf44af8e99807afc9b62ee7cb5625392a3d1'}
    identities={name:{'path':str(path),'sha256':digest(path)} for name,path in paths.items()}
    for name,sha in expected.items():assert identities[name]['sha256']==sha,name
    plan=json.loads(PLAN.read_text(encoding='utf-8'))
    save(OUT/'frozen.json',{'ast_pass':True,'source_sha256':{n:digest(ROOT/n) for n in source_names},'inputs':identities,
         'plan':plan,'environment':study_provenance.environment_fingerprint(),'test_type':'共享host完整支撑质量/规模，非性能','solver_calls':0})
    print({'frozen_sha256':digest(OUT/'frozen.json'),'sources':len(source_names),'inputs':len(paths)},flush=True)


def load_frozen():
    frozen=json.loads((OUT/'frozen.json').read_text(encoding='utf-8'));verify(frozen);return frozen


def contract():
    frozen=load_frozen()
    if (OUT/'contract.json').exists():raise FileExistsError('不覆盖有限合同')
    idx=np.tile((np.arange(256)>=128).astype(np.uint16),(3,1));base=np.where(np.arange(256)<128,np.arange(256)*512,(np.arange(256)-128)*65536//127).astype(np.uint32)
    frac=np.tile(base,(3,3,1))
    for c in range(3):
        for a in range(3):
            middle=(base>0)&(base<65536);frac[c,a,middle]=np.minimum(base[middle]+(3*c+a)*257,65535)
    nodes=((np.arange(81).reshape(3,3,3,3)*17)%256).astype(np.uint8);flat=nodes.reshape(-1,3)
    flat[0]=[0,1,254];flat[4]=[255,254,1];flat[13]=[1,0,255]
    model=cc.ChannelLut(np.tile([0.,128/255,1.],(3,1)).astype(np.float32),nodes,idx,frac)
    selected=np.array([0,4,13,26]);active=np.zeros((27,3),bool);active[selected]=True
    points=np.array(list(itertools.product((0,1,64,127,128,129,254,255),repeat=3)),np.uint8)
    np.testing.assert_array_equal(component.positive_hats(model,points,active),component.positive_tetra(model,points,active))
    i,w=hs.corners(model,points);values=nodes.reshape(-1,3).astype(np.int64);low,high=values.copy(),values.copy()
    low[selected]=np.maximum(values[selected]-2,0);high[selected]=np.minimum(values[selected]+2,255)
    for endpoint in (low,high):
        acc=np.sum(w.astype(np.uint64)*endpoint[i].astype(np.uint64),axis=1,dtype=np.uint64)
        observed=((acc+32768)>>16).astype(np.uint8)
        other=cc.ChannelLut(model.grid,endpoint.astype(np.uint8).reshape(nodes.shape),idx,frac)
        np.testing.assert_array_equal(integer_oracle(other,points),observed)
    lower=np.array([[0,0,0],[3,3,3],[0,0,0],[255,255,255],[7,8,9]],np.uint8)
    upper=np.array([[4,4,4],[7,7,7],[4,4,4],[255,255,255],[7,8,9]],np.uint8)
    gold=np.array([[6,6,6],[5,5,5],[255,255,255],[255,255,255],[0,0,0]],np.uint8)
    observed=risk.enumerate_stats(lower,upper,gold,lambda x:x,40);offsets,allowed=risk.collect_allowed(lower,upper,gold,lambda x:x,40)
    for j,(lo,hi,target) in enumerate(zip(lower,upper,gold)):
        states=list(itertools.product(*[range(int(a),int(b)+1) for a,b in zip(lo,hi)]));q=[sum((v-int(t))**2 for v,t in zip(row,target)) for row in states]
        safe=[list(row) for row,value in zip(states,q) if value<=40]
        assert [int(v[j]) for v in observed]==[min(q),max(q),len(q),len(safe),max((v for v in q if v<=40),default=-1)]
        assert allowed[offsets[j]:offsets[j+1]].tolist()==safe
    hist=hs.histogram(np.array([0,9,40]),np.array([0,2,1]),size=42);assert hist.sum()==3 and hist[0]==0 and hist[9]==2 and hist[40]==1
    save(OUT/'contract.json',{'pass':True,'frozen_sha256':digest(OUT/'frozen.json'),'positive_support_cases':len(points),
         'endpoint_integer_oracle_rows':2*len(points),'risk_boxes':len(lower),'clip_and_fixed_corners':True,'zero_training_mass':True,'solver_calls':0})
    print({'contract_pass':True,'points':len(points),'endpoints':2*len(points),'risk_boxes':len(lower)},flush=True)


def select():
    frozen=load_frozen();check=json.loads((OUT/'contract.json').read_text(encoding='utf-8'));assert check['pass'] and check['frozen_sha256']==digest(OUT/'frozen.json')
    if (OUT/'selection.npz').exists() or (OUT/'selection.json').exists():raise FileExistsError('不覆盖全部q41选择')
    inputs=frozen['inputs'];model=load_model(inputs['first']['path']);cube=np.memmap(inputs['cube']['path'],np.uint8,'r',shape=(1<<24,3));gold=np.load(inputs['gold']['path'],mmap_mode='r')
    hist=np.zeros(42,np.int64);pieces=[]
    for start in range(0,1<<24,65536):
        q=np.sum((cube[start:start+65536].astype(np.int32)-gold[start:start+65536].astype(np.int32))**2,axis=1,dtype=np.int32)
        assert int(q.max())<=41;hist+=hs.histogram(q,size=42);pieces.append(np.flatnonzero(q==41).astype(np.uint32)+start)
    hotspots=np.concatenate(pieces);assert len(hotspots)>0
    with np.load(inputs['histograms']['path']) as data:np.testing.assert_array_equal(hist,data['cube_candidate'][:42]);assert not np.any(data['cube_candidate'][42:])
    points=hs.rgb(hotspots);i,w,acc=hs.basis(model,points);chosen=[]
    for c in range(3):chosen.append(i[c][w[c]>0])
    touched=np.unique(np.concatenate(chosen));other_i,other_w=hs.corners(model,points)
    independently=np.unique(np.broadcast_to(other_i[:,:,None],other_w.shape)[other_w>0]);np.testing.assert_array_equal(touched,independently)
    with np.load(inputs['old_screen']['path']) as data:old=data['selected_nodes'].copy()
    assert len(old)==122;selected=np.union1d(old,touched);new=np.setdiff1d(touched,old)
    resource=frozen['plan']['资源门'];gate=len(selected)<=resource['maximum_selected_nodes']
    np.savez_compressed(OUT/'selection.npz',keys=hotspots,touched_nodes=touched,old_nodes=old,new_nodes=new,selected_nodes=selected,full_hist=hist)
    save(OUT/'selection.json',{'frozen_sha256':digest(OUT/'frozen.json'),'contract_sha256':digest(OUT/'contract.json'),
         'selection_sha256':digest(OUT/'selection.npz'),'all_q41_count':len(hotspots),'touched_nodes':len(touched),'new_nodes':len(new),
         'selected_nodes':len(selected),'node_gate_pass':bool(gate),'q41_selection_complete':True,'four_tetra_eight_hats_equal':True,'solver_calls':0})
    print({'q41':len(hotspots),'touched_nodes':len(touched),'new_nodes':len(new),'selected_nodes':len(selected),'node_gate':bool(gate)},flush=True)


def run():
    frozen=load_frozen();selection=json.loads((OUT/'selection.json').read_text(encoding='utf-8'))
    assert selection['frozen_sha256']==digest(OUT/'frozen.json') and selection['selection_sha256']==digest(OUT/'selection.npz')
    if (OUT/'run-input.json').exists():raise FileExistsError('不覆盖唯一完整规模普查')
    save(OUT/'run-input.json',{'frozen_sha256':digest(OUT/'frozen.json'),'selection_json_sha256':digest(OUT/'selection.json'),'selection_npz_sha256':digest(OUT/'selection.npz'),'solver_calls':0})
    if not selection['node_gate_pass']:
        save(OUT/'summary.json',{'within_gate':False,'stop':'selected_node_gate','selection':selection,'solver_calls':0});return
    inputs=frozen['inputs'];model=load_model(inputs['first']['path']);gates=frozen['plan']['资源门']
    with np.load(OUT/'selection.npz') as data:selected=data['selected_nodes'].copy();hotspots=data['keys'].copy()
    active=np.zeros((model.m**3,3),bool);active[selected]=True
    try:keys,geometry=component.complete_support(model,active,maximum_node_box_rows=gates['maximum_single_box_rows'])
    except MemoryError as error:
        save(OUT/'summary.json',{'within_gate':False,'stop':'single_node_box_gate','error':str(error),'solver_calls':0});return
    if len(keys)>gates['maximum_union_rows']:
        np.savez_compressed(OUT/'support-overflow.npz',keys=keys,selected_nodes=selected)
        save(OUT/'summary.json',{'within_gate':False,'stop':'support_row_gate','complete_support_rows':len(keys),'geometry':geometry,'solver_calls':0});return
    assert np.all(np.isin(hotspots,keys));points=hs.rgb(keys)
    cube=np.memmap(inputs['cube']['path'],np.uint8,'r',shape=(1<<24,3));gold_full=np.load(inputs['gold']['path'],mmap_mode='r');gold=gold_full[keys]
    suffix=np.load(inputs['suffix']['path'],mmap_mode='r');lookup=lambda rgb:suffix[hs.key(rgb)]
    nodes=model.nodes.reshape(-1,3).astype(np.int64);low,high=nodes.copy(),nodes.copy()
    low[selected]=np.maximum(nodes[selected]-2,0);high[selected]=np.minimum(nodes[selected]+2,255)
    lower=np.empty((len(keys),3),np.uint8);upper=lower.copy();original_first=lower.copy()
    max_acc=max_span=0
    for start in range(0,len(keys),65536):
        end=min(start+65536,len(keys));i,w=hs.corners(model,points[start:end]);weight=w.astype(np.uint64)
        a=np.sum(weight*low[i].astype(np.uint64),axis=1,dtype=np.uint64);b=np.sum(weight*high[i].astype(np.uint64),axis=1,dtype=np.uint64)
        assert np.all(a<=b) and np.all(b<=255*65536) and np.all(b-a<=4*65536)
        lower[start:end]=((a+32768)>>16).astype(np.uint8);upper[start:end]=((b+32768)>>16).astype(np.uint8)
        original_first[start:end]=integer_oracle(model,points[start:end])
        for endpoint,expected in ((low,lower[start:end]),(high,upper[start:end])):
            stage=cc.ChannelLut(model.grid,endpoint.astype(np.uint8).reshape(model.nodes.shape),model.idx,model.channel_frac)
            np.testing.assert_array_equal(integer_oracle(stage,points[start:end]),expected)
        max_acc=max(max_acc,int(b.max()));max_span=max(max_span,int((b-a).max()))
    np.testing.assert_array_equal(lookup(original_first),cube[keys]);original_q=np.sum((cube[keys].astype(np.int32)-gold.astype(np.int32))**2,axis=1,dtype=np.int32)
    mass=np.load(inputs['mass']['path'],mmap_mode='r');training,residual=train_counts(mass[keys],float(mass.sum(dtype=np.float64)))
    with np.load(inputs['histograms']['path']) as data:
        full=data['cube_candidate'][:42].copy();train=data['training60_candidate'][:42].copy()
    assert full.sum()==1<<24 and train.sum()==TRAINING_PIXELS
    outside=full-hs.histogram(original_q,size=42);outside_training=train-hs.histogram(original_q,training,size=42)
    assert np.all(outside>=0) and np.all(outside_training>=0) and not np.any(outside[41:]) and not np.any(outside_training[41:])
    state_count=np.prod(upper.astype(np.int16)-lower.astype(np.int16)+1,axis=1,dtype=np.int32)
    assert np.all(state_count<=gates['maximum_states_per_aabb']);total_states=int(state_count.sum(dtype=np.int64))
    np.savez_compressed(OUT/'aabb.npz',keys=keys,selected_nodes=selected,hotspot_keys=hotspots,lower_rgb=lower,upper_rgb=upper,
        original_first=original_first,original_squared=original_q,training_counts=training,outside_hist=outside,outside_training_hist=outside_training,
        gold=gold,state_count=state_count)
    if total_states>gates['maximum_total_aabb_states']:
        save(OUT/'summary.json',{'within_gate':False,'stop':'state_count_gate','aabb_states':total_states,'geometry':geometry,
            'aabb_sha256':digest(OUT/'aabb.npz'),'selected_physical_nodes':len(selected),'all_q41_count':len(hotspots),
            'complete_support_rows':len(keys),'maximum_states_per_aabb':int(state_count.max()),'all_q41_in_support':True,
            'outside_support_max_squared':int(np.flatnonzero(outside)[-1]),'outside_training_max_squared':int(np.flatnonzero(outside_training)[-1]),
            'affected_training_mass':int(training.sum()),'endpoint_integer_oracle_rows':2*len(keys),'state_queries':0,'solver_calls':0});return
    minimum,maximum,count,safe_count,safe_max=risk.enumerate_stats(lower,upper,gold,lookup,40)
    np.testing.assert_array_equal(count.astype(np.int32),state_count)
    dangerous=np.flatnonzero(maximum>40).astype(np.uint32);tuples=int(safe_count[dangerous].sum(dtype=np.int64));empty=int(np.count_nonzero(safe_count==0))
    gate=len(dangerous)<=gates['dangerous_points_max'] and tuples<=gates['safe_table_rows_max'] and empty==0
    stored={'keys':keys,'selected_nodes':selected,'hotspot_keys':hotspots,'original_first':original_first,'original_squared':original_q,
        'lower_rgb':lower,'upper_rgb':upper,'training_counts':training,'minimum_squared':minimum,'maximum_squared':maximum,
        'query_count':count,'safe_count':safe_count,'safe_maximum_squared':safe_max,'dangerous_rows':dangerous,
        'outside_hist':outside,'outside_training_hist':outside_training,'gold':gold}
    np.savez_compressed(OUT/'screen.npz',**stored)
    if gate:
        offsets,allowed=risk.collect_allowed(lower[dangerous],upper[dangerous],gold[dangerous],lookup,40)
        np.testing.assert_array_equal(np.diff(offsets),safe_count[dangerous]);assert int(offsets[-1])==tuples
        np.savez_compressed(OUT/'danger-allowed.npz',source_keys=keys[dangerous],offsets=offsets,allowed_rgb=allowed)
    result={'within_gate':bool(gate),'selected_physical_nodes':len(selected),'all_q41_count':len(hotspots),'complete_support_rows':len(keys),
        'geometry':geometry,'total_aabb_queries':total_states,'possibly_dangerous_rows':len(dangerous),'safe_rows':tuples,'zero_safe_rows':empty,
        'outside_support_max_squared':int(np.flatnonzero(outside)[-1]),'outside_training_max_squared':int(np.flatnonzero(outside_training)[-1]),
        'affected_training_mass':int(training.sum()),'training_frequency_residual':residual,'endpoint_integer_oracle_rows':2*len(keys),
        'maximum_endpoint_acc':max_acc,'maximum_unrounded_span':max_span,'payload_bytes':sum(v.nbytes for v in stored.values()),
        'all_q41_in_support':True,'solver_calls':0,'performance_calls':0,'stop':None if gate else 'empty_or_resource_gate',
        'scope':'唯一完整支撑cap40安全表示规模，不建CP，不保证共享可行/mean/p99或速度；任一空行或超门严格停止。'}
    verify(frozen);save(OUT/'summary.json',result)
    print({k:result[k] for k in ('within_gate','selected_physical_nodes','all_q41_count','complete_support_rows','total_aabb_queries','possibly_dangerous_rows','safe_rows','zero_safe_rows')},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['freeze','contract','select','run']);a=p.parse_args()
    {'freeze':freeze,'contract':contract,'select':select,'run':run}[a.mode]()
