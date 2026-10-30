"""独立离线复算全部最劣点、安全状态及新资源门；不补充选择或拟合。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from screen_cinema_current_all_max import OUT,load_frozen,save
from run_channel_tail_nodes import digest,load_model
from run_cinema_first_hotspot import train_counts
from verify_channel_coordinates import integer_oracle
from lutlab import channel_hotspot_support as hs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖全部最劣点独立审计')
    frozen=load_frozen();inputs=frozen['inputs'];summary=json.loads((OUT/'summary.json').read_text(encoding='utf-8'));gates=frozen['plan']['资源门']
    selected_proof=json.loads((OUT/'selection.json').read_text(encoding='utf-8'));assert selected_proof['selection_sha256']==digest(OUT/'selection.npz')
    with np.load(OUT/'selection.npz') as data:hotspots=data['keys'].copy();selected=data['selected_nodes'].copy();touched=data['touched_nodes'].copy();new=data['new_nodes'].copy();old=data['old_nodes'].copy();full_hist=data['full_hist'].copy()
    model=load_model(inputs['first']['path']);points=hs.rgb(hotspots);indices,weights=hs.corners(model,points)
    independently=np.unique(np.broadcast_to(indices[:,:,None],weights.shape)[weights>0]);np.testing.assert_array_equal(independently,touched)
    np.testing.assert_array_equal(selected,np.union1d(old,touched));np.testing.assert_array_equal(new,np.setdiff1d(touched,old))
    cube=np.memmap(inputs['cube']['path'],np.uint8,'r',shape=(1<<24,3));gold_full=np.load(inputs['gold']['path'],mmap_mode='r');found=[];hist=np.zeros(42,np.int64)
    for start in range(0,1<<24,32768):
        d=cube[start:start+32768].astype(np.int32)-gold_full[start:start+32768].astype(np.int32);q=d[:,0]**2+d[:,1]**2+d[:,2]**2
        hist+=np.bincount(q,minlength=42);found.extend((np.nonzero(q==41)[0]+start).tolist())
    np.testing.assert_array_equal(found,hotspots);np.testing.assert_array_equal(hist,full_hist)
    assert selected_proof['all_q41_count']==len(hotspots) and summary['solver_calls']==0
    result={'pass':True,'frozen_sha256':digest(OUT/'frozen.json'),'summary_sha256':digest(OUT/'summary.json'),
        'all_q41_count':len(hotspots),'touched_nodes':len(touched),'new_nodes':len(new),'selected_nodes':len(selected),
        'full_cube_selection_independent_rows':1<<24,'solver_calls':0,'performance_calls':0,'stop':summary['stop']}
    if not (OUT/'aabb.npz').exists():
        assert not summary['within_gate'] and summary['stop'] in ('selected_node_gate','single_node_box_gate','support_row_gate')
        save(args.output,result);print(result,flush=True);return
    with np.load(OUT/'aabb.npz') as data:arrays={n:data[n] for n in data.files}
    keys=arrays['keys'];assert len(keys)==summary['complete_support_rows'] and np.all(np.diff(keys.astype(np.int64))>0)
    np.testing.assert_array_equal(selected,arrays['selected_nodes']);assert np.all(np.isin(hotspots,keys))
    nodes=model.nodes.reshape(-1,3).astype(np.int64);low,high=nodes.copy(),nodes.copy();low[selected]=np.maximum(nodes[selected]-2,0);high[selected]=np.minimum(nodes[selected]+2,255)
    for endpoint,bound in ((low,'lower_rgb'),(high,'upper_rgb')):
        stage=type(model)(model.grid,endpoint.astype(np.uint8).reshape(model.nodes.shape),model.idx,model.channel_frac)
        for begin in range(0,len(keys),32768):np.testing.assert_array_equal(integer_oracle(stage,hs.rgb(keys[begin:begin+32768])),arrays[bound][begin:begin+32768])
    suffix=np.load(inputs['suffix']['path'],mmap_mode='r');first=arrays['original_first'];address=(first[:,0].astype(np.uint32)<<16)|(first[:,1].astype(np.uint32)<<8)|first[:,2].astype(np.uint32)
    np.testing.assert_array_equal(suffix[address],cube[keys]);d=cube[keys].astype(np.int32)-gold_full[keys].astype(np.int32);q=d[:,0]**2+d[:,1]**2+d[:,2]**2
    np.testing.assert_array_equal(q,arrays['original_squared']);np.testing.assert_array_equal(gold_full[keys],arrays['gold'])
    mass=np.load(inputs['mass']['path'],mmap_mode='r');w,_=train_counts(mass[keys],float(mass.sum(dtype=np.float64)));np.testing.assert_array_equal(w,arrays['training_counts'])
    with np.load(inputs['histograms']['path']) as data:
        outside=data['cube_candidate'][:42]-np.bincount(q,minlength=42)
        outside_train=data['training60_candidate'][:42]-np.bincount(q,weights=w,minlength=42).astype(np.int64)
    np.testing.assert_array_equal(outside,arrays['outside_hist']);np.testing.assert_array_equal(outside_train,arrays['outside_training_hist'])
    assert min(outside)>=0 and min(outside_train)>=0 and not outside[41] and not outside_train[41]
    span=arrays['upper_rgb'].astype(np.int16)-arrays['lower_rgb'].astype(np.int16);count=(span[:,0]+1)*(span[:,1]+1)*(span[:,2]+1)
    np.testing.assert_array_equal(count,arrays['state_count']);total=sum(int(v) for v in count)
    result.update(complete_support_rows=len(keys),endpoint_integer_rows=2*len(keys),aabb_states=total,
        outside_max_squared=int(np.flatnonzero(outside)[-1]),outside_training_max_squared=int(np.flatnonzero(outside_train)[-1]))
    if summary['stop']=='state_count_gate':
        assert total>gates['maximum_total_aabb_states'] and summary['state_queries']==0 and not (OUT/'screen.npz').exists()
        save(args.output,result);print(result,flush=True);return
    assert total<=gates['maximum_total_aabb_states']
    with np.load(OUT/'screen.npz') as data:screen={n:data[n] for n in data.files}
    danger=[];safe_total=empty=0;csr_rows=[];csr_rgb=[]
    for begin in range(0,len(keys),4096):
        end=min(begin+4096,len(keys));rows=[];rgb=[]
        for offset in itertools.product(range(5),repeat=3):
            ids=np.flatnonzero(np.all(span[begin:end]>=offset,axis=1))
            rows.append(ids);rgb.append(arrays['lower_rgb'][begin:end][ids].astype(np.int16)+offset)
        rr=np.concatenate(rows);xx=np.concatenate(rgb).astype(np.uint8);address=(xx[:,0].astype(np.uint32)<<16)|(xx[:,1].astype(np.uint32)<<8)|xx[:,2].astype(np.uint32)
        d=suffix[address].astype(np.int32)-arrays['gold'][begin:end][rr].astype(np.int32);q=d[:,0]**2+d[:,1]**2+d[:,2]**2
        n=end-begin;mn=np.full(n,195076,np.int32);mx=np.zeros(n,np.int32);sm=np.full(n,-1,np.int32)
        np.minimum.at(mn,rr,q);np.maximum.at(mx,rr,q);good=q<=40;np.maximum.at(sm,rr[good],q[good])
        safe=np.bincount(rr[good],minlength=n);counts=np.bincount(rr,minlength=n)
        for name,value in [('minimum_squared',mn),('maximum_squared',mx),('safe_maximum_squared',sm),('safe_count',safe),('query_count',counts)]:
            np.testing.assert_array_equal(value,screen[name][begin:end])
        ids=np.flatnonzero(mx>40);danger.extend((ids+begin).tolist());safe_total+=int(safe[ids].sum());empty+=int(np.count_nonzero(safe==0))
        if summary['within_gate']:
            take=good & (mx[rr]>40);csr_rows.append((rr[take]+begin).astype(np.uint32));csr_rgb.append(xx[take])
    np.testing.assert_array_equal(danger,screen['dangerous_rows']);assert len(danger)==summary['possibly_dangerous_rows'] and safe_total==summary['safe_rows'] and empty==summary['zero_safe_rows']
    gate=len(danger)<=gates['dangerous_points_max'] and safe_total<=gates['safe_table_rows_max'] and empty==0
    assert gate==summary['within_gate']
    if gate:
        rows=np.concatenate(csr_rows);rgb=np.concatenate(csr_rgb);order=np.lexsort((hs.key(rgb),rows));rows,rgb=rows[order],rgb[order]
        with np.load(OUT/'danger-allowed.npz') as data:
            np.testing.assert_array_equal(keys[np.array(danger)],data['source_keys']);np.testing.assert_array_equal(rgb,data['allowed_rgb'])
            np.testing.assert_array_equal(np.bincount(np.searchsorted(danger,rows),minlength=len(danger)),np.diff(data['offsets']))
    result.update(independent_state_queries=total,dangerous_rows=len(danger),safe_rows=safe_total,zero_safe_rows=empty,within_gate=gate)
    save(args.output,result);print(result,flush=True)


if __name__=='__main__':main()
