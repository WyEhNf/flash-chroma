"""独立整数前向及显式重复训练像素核对新增两项尾部收益。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_training_tail as tt,channel_arrival_nodes as an,channel_coordinates as cc
from lutlab import channel_joint_nodes as cj,channel_max_nodes as mx,io,study_provenance
from check_channel_arrival_nodes import compact_design
from run_channel_tail_nodes import save,digest
from verify_channel_coordinates import integer_oracle


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖训练尾部有限合同')
    numba.set_num_threads(4);rng=np.random.default_rng(20261024031)
    directions=np.concatenate((cj.DIRECTIONS,mx.DIRECTIONS),axis=0)
    selector_cases=0
    for trial in range(256):
        colours=np.arange(16,dtype=np.int32)%8;colour=trial%8
        change=rng.integers(-8,9,(11,78,16)).astype(np.float64);change[:,0,:]=-rng.integers(0,5,(11,16))
        bad=(rng.random((78,16))<.2).astype(np.int64);allowance=rng.integers(0,20,11).astype(np.float64);allowance[[6,7,9]]=0
        moves,predicted,accepted=tt.select(change,bad,colours,colour,directions,allowance)
        independent=np.zeros(11);seen=set()
        for item in accepted:
            node,direction=item['node'],item['direction'];assert node not in seen and colours[node]==colour and bad[direction,node]==0
            seen.add(node);independent+=change[:,direction,node];np.testing.assert_array_equal(moves[node],directions[direction])
        np.testing.assert_array_equal(independent,predicted);assert np.all(independent<=allowance+1e-8)
        for node in set(range(16))-seen:assert not np.any(moves[node])
        selector_cases+=1
    # 固定构造：一个局部方向取得预算后允许另一个方向降低训练尾部。
    colours=np.zeros(2,np.int32);change=np.full((11,78,2),100.);bad=np.ones((78,2),np.int64)
    change[:,0,0]=-2;bad[0,0]=0;change[:,1,1]=1;change[[6,7],1,1]=0;change[9,1,1]=-3;bad[1,1]=0
    _,predicted,accepted=tt.select(change,bad,colours,0,directions,np.zeros(11))
    assert len(accepted)==2 and predicted[9]==-5 and np.all(predicted<=0) and any(v['uses_prior_budget'] for v in accepted)
    rejects=0
    for allowance in (np.zeros(10),-np.ones(11),np.full(11,np.nan)):
        try:tt.select(change,bad,colours,0,directions,allowance)
        except ValueError:rejects+=1
        else:raise AssertionError('非法预算被接受')
    suffix=np.empty((256**3,3),np.uint8)
    for start in range(0,len(suffix),1<<18):
        keys=np.arange(start,min(start+(1<<18),len(suffix)),dtype=np.uint32)
        suffix[start:start+len(keys)]=np.stack((keys>>16,(keys>>8)&255,keys&255),axis=1).astype(np.uint8)
    output=np.array([[3,1,1],[2,2,2],[7,0,0],[5,5,0]],np.uint8);reference=np.zeros_like(output)
    count=np.array([0,2,3,4],np.int64);frequency=np.ones(4,np.int64);mass=count/count.sum()
    measured,square=tt.measure(output,reference,suffix,frequency,mass,count,9,49,11)
    np.testing.assert_array_equal(square,[11,12,49,50]);expanded=np.repeat(np.arange(4),count)
    assert measured[9]==np.count_nonzero(square[expanded]>11) and measured[10]==np.maximum(square[expanded]-11,0).sum()
    records=[]
    for m in (17,33):
        sparse=io.SparseLut(io.uniform_grid(m),rng.integers(0,256,(m,m,m,3),dtype=np.uint8));sparse.nodes.reshape(-1,3)[0]=0;sparse.nodes.reshape(-1,3)[-1]=255
        model=cc.from_sparse(sparse)
        for channel in range(3):model.channel_frac[channel]=((model.channel_frac[channel].astype(np.uint64)*(20-channel))//20).astype(np.uint32)
        points=rng.integers(0,256,(192,3),dtype=np.uint8);points[:8]=np.asarray([[r,g,b] for r in (0,255) for g in (0,255) for b in (0,255)],np.uint8)
        original=integer_oracle(model,points);gold=np.clip(original.astype(np.int32)+rng.integers(-5,6,original.shape),0,255).astype(np.uint8)
        frequency=rng.integers(1,5,len(points),dtype=np.int64);training=rng.integers(0,5,len(points),dtype=np.int64);training[::3]=0;mass=training/training.sum()
        initial,squared=tt.measure(original,gold,suffix,frequency,mass,training,9,49,11);caps=np.maximum(49,squared)
        indices,weights,active,colours=compact_design(model,points);nodes=model.nodes.reshape(-1,3)[active];acc,_=cj.accumulate(indices,weights,nodes,gold)
        maximum=0.;probes=0;illegal=0
        for colour in range(8):
            nine,bad,invalid=an.gains(indices,weights,acc,gold,suffix,frequency,mass,nodes,colours,colour,caps,np.sqrt(np.arange(3*255**2+1)),4,9,49,directions,4)
            extra,invalid_extra=tt.training_gains(indices,weights,acc,gold,suffix,training,nodes,colours,colour,4,11,directions,4)
            assert invalid==0 and invalid_extra==0;changes=np.concatenate((nine,extra),axis=0)
            for node in np.flatnonzero(colours==colour)[:2]:
                for direction in range(78):
                    value=nodes[node].astype(np.int32)+directions[direction]
                    if np.any(value<0) or np.any(value>255):assert bad[direction,node]>0;illegal+=1;continue
                    physical=model.nodes.copy();physical.reshape(-1,3)[active[node]]=value
                    fresh=integer_oracle(cc.ChannelLut(model.grid,physical,model.idx,model.channel_frac),points)
                    after,actual=tt.measure(fresh,gold,suffix,frequency,mass,training,9,49,11)
                    maximum=max(maximum,float(np.max(np.abs(after-initial-changes[:,direction,node]))))
                    assert bad[direction,node]==int(frequency@(actual>caps));probes+=1
            moves,predicted,accepted=tt.select(changes,bad,colours,colour,directions,np.zeros(11))
            physical=model.nodes.copy();physical.reshape(-1,3)[active]=(nodes.astype(np.int32)+moves).astype(np.uint8)
            fresh=integer_oracle(cc.ChannelLut(model.grid,physical,model.idx,model.channel_frac),points)
            after,actual=tt.measure(fresh,gold,suffix,frequency,mass,training,9,49,11)
            maximum=max(maximum,float(np.max(np.abs(after-initial-predicted))));assert np.all(after<=initial+1e-8) and np.all(actual<=caps)
            repeated=np.repeat(np.arange(len(points)),training)
            assert after[9]==np.count_nonzero(actual[repeated]>11) and after[10]==np.maximum(actual[repeated]-11,0).sum()
        assert maximum<1e-8
        records.append({'m':m,'independent_legal_probes':probes,'illegal_node_directions':illegal,'maximum_gain_error':maximum,'expanded_training_pixels':int(training.sum())})
    sources=(Path(__file__),ROOT/'python/lutlab/channel_training_tail.py',ROOT/'python/lutlab/channel_arrival_nodes.py',ROOT/'scripts/check_channel_arrival_nodes.py',ROOT/'scripts/verify_channel_coordinates.py')
    save(args.output,{'pass':True,'environment':study_provenance.environment_fingerprint(),'sources':{p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        'selector_cases':selector_cases,'constructed_exchange_cases':1,'reject_cases':rejects,'threshold_squared':[11,12,49,50],'records':records,
        'scope':'有限几何/收益/重复计数/预算合同；不代替真实完整支撑和百图终验，也不作性能成绩'})
    print({'pass':True,'selector_cases':selector_cases,'records':records},flush=True)


if __name__=='__main__':main()
