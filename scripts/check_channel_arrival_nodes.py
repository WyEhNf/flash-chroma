"""独立uint64与显式重复支撑核对加权压缩设计的节点收益，不用于性能。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_arrival_nodes as an,channel_coordinates as cc,channel_global_nodes as cg
from lutlab import channel_joint_nodes as cj,channel_max_nodes as mx,io
from run_channel_tail_nodes import save
from verify_channel_coordinates import integer_oracle


def compact_design(model,points):
    indices,weights=cg.design(model,points)
    active=np.unique(indices[weights>0]);mapping=np.zeros(model.m**3,np.int32)
    mapping[active]=np.arange(len(active),dtype=np.int32)
    return mapping[indices],weights,active,cj.parity(model.m)[active]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖合同')
    numba.set_num_threads(4);rng=np.random.default_rng(20261024)
    suffix=np.empty((256**3,3),np.uint8)
    for start in range(0,len(suffix),1<<18):
        keys=np.arange(start,min(start+(1<<18),len(suffix)),dtype=np.int64)
        r,g,b=keys>>16,(keys>>8)&255,keys&255
        suffix[start:start+len(keys)]=np.column_stack(((r+g//8)%256,np.minimum(g+((b//32)%2)*3,255),b^((r//64)*3)))
    root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64));records=[]
    for m in (17,33):
        sparse=io.SparseLut(io.uniform_grid(m),rng.integers(0,256,(m,m,m,3),dtype=np.uint8))
        sparse.nodes.reshape(-1,3)[0]=0;sparse.nodes.reshape(-1,3)[-1]=255
        model=cc.from_sparse(sparse)
        for c in range(3):model.channel_frac[c]=((model.channel_frac[c].astype(np.uint64)*(20-c))//20).astype(np.uint32)
        points=rng.integers(0,256,(384,3),dtype=np.uint8)
        points[:8]=np.asarray([[r,g,b] for r in (0,255) for g in (0,255) for b in (0,255)],np.uint8)
        original=integer_oracle(model,points)
        keys=original.astype(np.int64)@np.array([65536,256,1],np.int64)
        reference=np.clip(suffix[keys].astype(np.int32)+rng.integers(-8,9,original.shape),0,255).astype(np.uint8)
        frequency=rng.integers(1,5,len(points),dtype=np.int64)
        mass=rng.random(len(points));mass[::3]=0;mass/=mass.sum()
        initial,square=an.measure(original,reference,suffix,frequency,mass,12,58);caps=np.maximum(58,square)
        indices,weights,active,colours=compact_design(model,points);nodes=model.nodes.reshape(-1,3)[active]
        acc,_=cj.accumulate(indices,weights,nodes,reference)
        np.testing.assert_array_equal(original,((acc+io.ONE//2)>>io.Q).astype(np.uint8))
        repeated=np.repeat(np.arange(len(points)),frequency)
        expanded,_=an.measure(original[repeated],reference[repeated],suffix,np.ones(len(repeated),np.int64),
            np.repeat(mass/frequency,frequency),12,58)
        np.testing.assert_allclose(initial,expanded,rtol=0,atol=1e-8)
        for directions,label in ((cj.DIRECTIONS,'unit26'),(mx.DIRECTIONS,'even52')):
            maximum_error=0.;probes=0;illegal=0
            selected_directions=range(len(directions))
            for colour in range(8):
                change,bad,invalid=an.gains(indices,weights,acc,reference,suffix,frequency,mass,nodes,colours,
                    colour,caps,root,4,12,58,directions,int(np.abs(directions).max()))
                if invalid:raise AssertionError('压缩几何不符合每parity唯一节点')
                possible=np.flatnonzero(colours==colour)[:2]
                for node in possible:
                    for direction in selected_directions:
                        values=nodes[node].astype(np.int32)+directions[direction]
                        if np.any(values<0) or np.any(values>255):
                            assert bad[direction,node]>0;illegal+=1;continue
                        proposed_nodes=model.nodes.copy();proposed_nodes.reshape(-1,3)[active[node]]=values
                        proposed=cc.ChannelLut(model.grid,proposed_nodes,model.idx,model.channel_frac)
                        fresh=integer_oracle(proposed,points)
                        measured,squared=an.measure(fresh,reference,suffix,frequency,mass,12,58)
                        error=float(np.max(np.abs(measured-initial-change[:,direction,node])))
                        maximum_error=max(maximum_error,error)
                        assert bad[direction,node]==int(frequency@(squared>caps))
                        probes+=1
                moves,predicted,accepted=an.select(change,bad,colours,colour,directions)
                assert np.all(predicted<=1e-8)
                proposed_nodes=model.nodes.copy();proposed_nodes.reshape(-1,3)[active]=(nodes.astype(np.int32)+moves).astype(np.uint8)
                proposed=cc.ChannelLut(model.grid,proposed_nodes,model.idx,model.channel_frac)
                fresh=integer_oracle(proposed,points);measured,squared=an.measure(fresh,reference,suffix,frequency,mass,12,58)
                maximum_error=max(maximum_error,float(np.max(np.abs(measured-initial-predicted))))
                update=acc.copy();an.apply_accumulator(indices,weights,update,moves)
                np.testing.assert_array_equal(fresh,((update+io.ONE//2)>>io.Q).astype(np.uint8))
                assert np.all(squared<=caps)
            if maximum_error>1e-8:raise AssertionError('加权完整收益不匹配独立oracle')
            records.append({'m':m,'directions':label,'points':len(points),'expanded_points':len(repeated),
                'active_nodes':len(active),'independent_legal_probes':probes,'illegal_node_directions':illegal,
                'maximum_gain_error':maximum_error,'byte_mismatches':0})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    save(args.output,{'pass':True,'records':records,'scope':'有限m17/33、26±1/52±2/4、0/255节点、非线性后缀、零训练质量、重复频数、紧凑节点映射、批量选择/acc更新；不代替实际全域验收'})
    print(records,flush=True)


if __name__=='__main__':main()
