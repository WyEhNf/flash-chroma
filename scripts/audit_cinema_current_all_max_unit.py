"""独立核±1真实端点及全部安全状态，消费已认证完整支撑而不删点。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from screen_cinema_current_all_max_unit import OLD,OUT,load_frozen,save
from run_channel_tail_nodes import digest,load_model
from verify_channel_coordinates import integer_oracle
from lutlab import channel_hotspot_support as hs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖±1独立审计')
    proof=load_frozen();summary=json.loads((OUT/'summary.json').read_text(encoding='utf-8'));gates=proof['plan']['资源门'];inputs=proof['original_inputs']
    with np.load(OLD/'aabb.npz') as data:old={n:data[n] for n in data.files}
    with np.load(OUT/'aabb.npz') as data:arrays={n:data[n] for n in data.files}
    for n in old:
        if n not in ('lower_rgb','upper_rgb','state_count'):np.testing.assert_array_equal(old[n],arrays[n])
    keys=arrays['keys'];selected=arrays['selected_nodes'];assert len(keys)==171271 and len(selected)==273 and np.all(np.isin(arrays['hotspot_keys'],keys))
    model=load_model(inputs['first']['path']);nodes=model.nodes.reshape(-1,3).astype(np.int64);low,high=nodes.copy(),nodes.copy();low[selected]=np.maximum(nodes[selected]-1,0);high[selected]=np.minimum(nodes[selected]+1,255)
    for bound,values in [('lower_rgb',low),('upper_rgb',high)]:
        stage=type(model)(model.grid,values.astype(np.uint8).reshape(model.nodes.shape),model.idx,model.channel_frac)
        for start in range(0,len(keys),32768):np.testing.assert_array_equal(integer_oracle(stage,hs.rgb(keys[start:start+32768])),arrays[bound][start:start+32768])
    span=arrays['upper_rgb'].astype(np.int16)-arrays['lower_rgb'].astype(np.int16);count=(span[:,0]+1)*(span[:,1]+1)*(span[:,2]+1)
    assert np.all(span>=0) and np.all(span<=2);np.testing.assert_array_equal(count,arrays['state_count']);total=sum(int(v) for v in count);assert total==summary['aabb_states']
    result={'pass':True,'frozen_sha256':digest(OUT/'frozen.json'),'summary_sha256':digest(OUT/'summary.json'),'endpoint_integer_rows':342542,
        'support_rows':171271,'selected_nodes':273,'aabb_states':total,'stop':summary['stop'],'solver_calls':0}
    if summary['stop']=='state_count_gate':
        assert total>gates['maximum_total_aabb_states'] and summary['state_queries']==0 and not (OUT/'screen.npz').exists();save(args.output,result);print(result,flush=True);return
    assert total<=gates['maximum_total_aabb_states'];suffix=np.load(inputs['suffix']['path'],mmap_mode='r')
    with np.load(OUT/'screen.npz') as data:screen={n:data[n] for n in data.files}
    danger=[];triples=empty=0;kept_rows=[];kept_rgb=[]
    for begin in range(0,len(keys),4096):
        end=min(begin+4096,len(keys));rows=[];rgb=[]
        for offset in itertools.product(range(3),repeat=3):
            ids=np.flatnonzero(np.all(span[begin:end]>=offset,axis=1));rows.append(ids);rgb.append(arrays['lower_rgb'][begin:end][ids].astype(np.int16)+offset)
        rr=np.concatenate(rows);xx=np.concatenate(rgb).astype(np.uint8);addr=(xx[:,0].astype(np.uint32)<<16)|(xx[:,1].astype(np.uint32)<<8)|xx[:,2].astype(np.uint32)
        d=suffix[addr].astype(np.int32)-arrays['gold'][begin:end][rr].astype(np.int32);q=d[:,0]**2+d[:,1]**2+d[:,2]**2
        n=end-begin;mn=np.full(n,195076,np.int32);mx=np.zeros(n,np.int32);sm=np.full(n,-1,np.int32)
        np.minimum.at(mn,rr,q);np.maximum.at(mx,rr,q);good=q<=40;np.maximum.at(sm,rr[good],q[good]);safe=np.bincount(rr[good],minlength=n);queries=np.bincount(rr,minlength=n)
        for name,value in [('minimum_squared',mn),('maximum_squared',mx),('safe_maximum_squared',sm),('safe_count',safe),('query_count',queries)]:np.testing.assert_array_equal(value,screen[name][begin:end])
        ids=np.flatnonzero(mx>40);danger.extend((ids+begin).tolist());triples+=int(safe[ids].sum());empty+=int(np.count_nonzero(safe==0))
        if summary['within_gate']:
            take=good & (mx[rr]>40);kept_rows.append((rr[take]+begin).astype(np.uint32));kept_rgb.append(xx[take])
    np.testing.assert_array_equal(danger,screen['dangerous_rows']);assert len(danger)==summary['dangerous_rows'] and triples==summary['safe_rows'] and empty==summary['zero_safe_rows']
    gate=len(danger)<=gates['dangerous_points_max'] and triples<=gates['safe_table_rows_max'] and empty==0;assert gate==summary['within_gate']
    if gate:
        rr=np.concatenate(kept_rows);rgb=np.concatenate(kept_rgb);order=np.lexsort((hs.key(rgb),rr));rr,rgb=rr[order],rgb[order]
        with np.load(OUT/'danger-allowed.npz') as data:
            np.testing.assert_array_equal(keys[np.array(danger)],data['source_keys']);np.testing.assert_array_equal(rgb,data['allowed_rgb'])
            np.testing.assert_array_equal(np.bincount(np.searchsorted(danger,rr),minlength=len(danger)),np.diff(data['offsets']))
    result.update(independent_state_queries=total,dangerous_rows=len(danger),safe_rows=triples,zero_safe_rows=empty,within_gate=gate)
    save(args.output,result);print(result,flush=True)


if __name__=='__main__':main()
