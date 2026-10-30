"""同一完整273节点支撑的独立±1缩域；真实端点与cap40唯一规模普查。"""
from __future__ import annotations
import argparse
import ast
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from lutlab import channel_coordinates as cc,channel_hotspot_support as hs,channel_capped_risk as risk,study_provenance
from run_channel_tail_nodes import digest,load_model
from verify_channel_coordinates import integer_oracle
OLD=ROOT/'artifacts/cinema-current-all-max-support-v1'
OUT=ROOT/'artifacts/cinema-current-all-max-unit-v1'
PLAN=ROOT/'experiments/p16-cinema-current-all-max-unit-v1.json'


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖±1独立缩域证据')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def verify(proof):
    for name,expected in proof['source_sha256'].items():assert digest(ROOT/name)==expected,name
    for name,expected in proof['inputs_sha256'].items():assert digest(name)==expected,name


def freeze():
    if OUT.exists():raise FileExistsError('不覆盖独立缩域阶段')
    old=json.loads((OLD/'frozen.json').read_text(encoding='utf-8'));audit=ROOT/'artifacts/cinema-current-all-max-support-independent-v1.json'
    independent=json.loads(audit.read_text(encoding='utf-8'));summary=json.loads((OLD/'summary.json').read_text(encoding='utf-8'))
    assert independent['pass'] and independent['summary_sha256']==digest(OLD/'summary.json')
    assert summary['stop']=='state_count_gate' and summary['state_queries']==0 and summary['complete_support_rows']==171271
    assert summary['selected_physical_nodes']==273 and summary['all_q41_count']==231 and summary['outside_support_max_squared']==38
    sources=dict(old['source_sha256'])
    for n in ['experiments/p16-cinema-current-all-max-unit-v1.json','scripts/screen_cinema_current_all_max_unit.py','scripts/audit_cinema_current_all_max_unit.py']:sources[n]=digest(ROOT/n)
    for n,expected in sources.items():
        assert digest(ROOT/n)==expected,n
        if n.endswith('.py'):ast.parse((ROOT/n).read_text(encoding='utf-8-sig'))
    inputs={v['path']:v['sha256'] for v in old['inputs'].values()}
    for p in [OLD/'frozen.json',OLD/'summary.json',OLD/'aabb.npz',OLD/'selection.json',OLD/'selection.npz',audit]:inputs[str(p)]=digest(p)
    for n,expected in inputs.items():assert digest(n)==expected,n
    save(OUT/'frozen.json',{'ast_pass':True,'source_sha256':sources,'inputs_sha256':inputs,'original_inputs':old['inputs'],
         'plan':json.loads(PLAN.read_text(encoding='utf-8')),'environment':study_provenance.environment_fingerprint(),
         'reused_complete_support_rows':171271,'reused_selected_nodes':273,'solver_calls':0,'performance_calls':0})
    print({'frozen_sha256':digest(OUT/'frozen.json'),'sources':len(sources),'inputs':len(inputs)},flush=True)


def load_frozen():
    proof=json.loads((OUT/'frozen.json').read_text(encoding='utf-8'));verify(proof);return proof


def contract():
    proof=load_frozen()
    if (OUT/'contract.json').exists():raise FileExistsError('不覆盖缩域有限合同')
    idx=np.tile((np.arange(256)>=128).astype(np.uint16),(3,1));base=np.where(np.arange(256)<128,np.arange(256)*512,(np.arange(256)-128)*65536//127).astype(np.uint32)
    frac=np.tile(base,(3,3,1))
    for c in range(3):
        for a in range(3):
            inside=(base>0)&(base<65536);frac[c,a,inside]=np.minimum(base[inside]+(3*c+a)*257,65535)
    nodes=((np.arange(81).reshape(3,3,3,3)*17)%256).astype(np.uint8);flat=nodes.reshape(-1,3)
    flat[0]=[0,1,254];flat[4]=[255,254,1];flat[13]=[1,0,255]
    model=cc.ChannelLut(np.tile([0.,128/255,1.],(3,1)).astype(np.float32),nodes,idx,frac)
    selected=np.array([0,4,13,26]);points=np.array(list(itertools.product((0,1,64,127,128,129,254,255),repeat=3)),np.uint8)
    i,w=hs.corners(model,points);v=nodes.reshape(-1,3).astype(np.int64);low,high=v.copy(),v.copy();low[selected]=np.maximum(v[selected]-1,0);high[selected]=np.minimum(v[selected]+1,255)
    lower=upper=None
    for label,end in [('lower',low),('upper',high)]:
        acc=np.sum(w.astype(np.uint64)*end[i].astype(np.uint64),axis=1,dtype=np.uint64);out=((acc+32768)>>16).astype(np.uint8)
        stage=cc.ChannelLut(model.grid,end.astype(np.uint8).reshape(nodes.shape),idx,frac);np.testing.assert_array_equal(integer_oracle(stage,points),out)
        if label=='lower':lower=out
        else:upper=out
    assert np.all(upper.astype(np.int16)-lower<=2)
    lo=np.array([[0,0,0],[3,3,3],[0,0,0],[255,255,255],[7,8,9]],np.uint8)
    hi=np.array([[2,2,2],[5,5,5],[2,2,2],[255,255,255],[7,8,9]],np.uint8)
    gold=np.array([[6,6,6],[5,5,5],[255,255,255],[255,255,255],[0,0,0]],np.uint8)
    observed=risk.enumerate_stats(lo,hi,gold,lambda x:x,40);offsets,allowed=risk.collect_allowed(lo,hi,gold,lambda x:x,40)
    for j,(a,b,t) in enumerate(zip(lo,hi,gold)):
        states=list(itertools.product(*[range(int(x),int(y)+1) for x,y in zip(a,b)]));q=[sum((x-int(y))**2 for x,y in zip(row,t)) for row in states]
        safe=[list(row) for row,n in zip(states,q) if n<=40]
        assert len(states)<=27 and [int(x[j]) for x in observed]==[min(q),max(q),len(q),len(safe),max((x for x in q if x<=40),default=-1)]
        assert allowed[offsets[j]:offsets[j+1]].tolist()==safe
    hist=hs.histogram(np.array([0,9,40]),np.array([0,2,1]),size=42);assert hist[0]==0 and hist.sum()==3
    save(OUT/'contract.json',{'pass':True,'frozen_sha256':digest(OUT/'frozen.json'),'integer_endpoint_rows':1024,'risk_boxes':5,
         'point_state_bound':27,'zero_training_mass':True,'fixed_corners_and_clip':True,'solver_calls':0})
    print({'contract_pass':True,'endpoints':1024,'risk_boxes':5,'state_bound':27},flush=True)


def run():
    proof=load_frozen();contract=json.loads((OUT/'contract.json').read_text(encoding='utf-8'));assert contract['pass'] and contract['frozen_sha256']==digest(OUT/'frozen.json')
    if (OUT/'run-input.json').exists():raise FileExistsError('不覆盖唯一±1真实规模普查')
    save(OUT/'run-input.json',{'frozen_sha256':digest(OUT/'frozen.json'),'contract_sha256':digest(OUT/'contract.json'),'solver_calls':0})
    inputs=proof['original_inputs'];model=load_model(inputs['first']['path']);gates=proof['plan']['资源门']
    with np.load(OLD/'aabb.npz') as data:base={n:data[n] for n in data.files if n not in ('lower_rgb','upper_rgb','state_count')}
    keys=base['keys'];selected=base['selected_nodes'];assert len(keys)==171271 and len(selected)==273 and len(base['hotspot_keys'])==231
    assert len(selected)<=gates['maximum_selected_nodes'] and len(keys)<=gates['maximum_union_rows']
    nodes=model.nodes.reshape(-1,3).astype(np.int64);low,high=nodes.copy(),nodes.copy();low[selected]=np.maximum(nodes[selected]-1,0);high[selected]=np.minimum(nodes[selected]+1,255)
    lower=np.empty((len(keys),3),np.uint8);upper=lower.copy();max_acc=max_span=0
    for begin in range(0,len(keys),65536):
        end=min(begin+65536,len(keys));points=hs.rgb(keys[begin:end]);i,w=hs.corners(model,points);weight=w.astype(np.uint64)
        a=np.sum(weight*low[i].astype(np.uint64),axis=1,dtype=np.uint64);b=np.sum(weight*high[i].astype(np.uint64),axis=1,dtype=np.uint64)
        assert np.all(a<=b) and np.all(b<=255*65536) and np.all(b-a<=2*65536)
        lower[begin:end]=((a+32768)>>16).astype(np.uint8);upper[begin:end]=((b+32768)>>16).astype(np.uint8)
        for values,expected in [(low,lower[begin:end]),(high,upper[begin:end])]:
            stage=cc.ChannelLut(model.grid,values.astype(np.uint8).reshape(model.nodes.shape),model.idx,model.channel_frac)
            np.testing.assert_array_equal(integer_oracle(stage,points),expected)
        max_acc=max(max_acc,int(b.max()));max_span=max(max_span,int((b-a).max()))
    count=np.prod(upper.astype(np.int16)-lower.astype(np.int16)+1,axis=1,dtype=np.int32);total=int(count.sum(dtype=np.int64))
    assert np.all(count<=27);np.savez_compressed(OUT/'aabb.npz',**base,lower_rgb=lower,upper_rgb=upper,state_count=count)
    common={'selected_physical_nodes':273,'complete_support_rows':171271,'all_q41_count':231,'aabb_states':total,
        'maximum_states_per_aabb':int(count.max()),'reused_full_support_certificate':True,'endpoint_integer_rows':342542,
        'maximum_endpoint_acc':max_acc,'maximum_unrounded_span':max_span,'aabb_sha256':digest(OUT/'aabb.npz'),
        'solver_calls':0,'performance_calls':0}
    if total>gates['maximum_total_aabb_states']:
        save(OUT/'summary.json',{**common,'within_gate':False,'stop':'state_count_gate','state_queries':0});return
    suffix=np.load(inputs['suffix']['path'],mmap_mode='r');lookup=lambda x:suffix[hs.key(x)]
    minimum,maximum,query,safe,safe_max=risk.enumerate_stats(lower,upper,base['gold'],lookup,40)
    np.testing.assert_array_equal(query.astype(np.int32),count);danger=np.flatnonzero(maximum>40).astype(np.uint32);triples=int(safe[danger].sum(dtype=np.int64));empty=int(np.count_nonzero(safe==0))
    gate=len(danger)<=gates['dangerous_points_max'] and triples<=gates['safe_table_rows_max'] and empty==0
    np.savez_compressed(OUT/'screen.npz',**base,lower_rgb=lower,upper_rgb=upper,minimum_squared=minimum,maximum_squared=maximum,
        query_count=query,safe_count=safe,safe_maximum_squared=safe_max,dangerous_rows=danger)
    if gate:
        offsets,allowed=risk.collect_allowed(lower[danger],upper[danger],base['gold'][danger],lookup,40)
        np.testing.assert_array_equal(np.diff(offsets),safe[danger]);assert int(offsets[-1])==triples
        np.savez_compressed(OUT/'danger-allowed.npz',source_keys=keys[danger],offsets=offsets,allowed_rgb=allowed)
    verify(proof)
    result={**common,'state_queries':total,'dangerous_rows':len(danger),'safe_rows':triples,'zero_safe_rows':empty,'within_gate':bool(gate),
        'stop':None if gate else 'empty_or_resource_gate','outside_max_squared':int(np.flatnonzero(base['outside_hist'])[-1]),
        'outside_training_max_squared':int(np.flatnonzero(base['outside_training_hist'])[-1]),'affected_training_mass':int(base['training_counts'].sum()),
        'scope':'独立±1缩域唯一完整安全规模，旧±2 STOP保持；门内也不是共享可行解，不CP或晋级。'}
    save(OUT/'summary.json',result);print(result,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['freeze','contract','run']);args=p.parse_args();{'freeze':freeze,'contract':contract,'run':run}[args.mode]()
