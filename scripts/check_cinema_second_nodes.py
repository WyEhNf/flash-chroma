"""独立重算目标选择器预算，并核对新11/56阈值的加权与重复样本等价。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import channel_arrival_nodes as an,channel_arrival_priority as priority,channel_joint_nodes as cj,channel_max_nodes as mx
from run_channel_tail_nodes import save,digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖有限合同')
    rng=np.random.default_rng(2026102417);directions=np.concatenate((cj.DIRECTIONS,mx.DIRECTIONS),axis=0)
    assert len(directions)==78 and len(np.unique(directions,axis=0))==78
    checks=0;exchanges=0;target_checks=0
    for trial in range(256):
        colours=np.arange(16,dtype=np.int32)%8;colour=trial%8
        change=rng.integers(-8,9,(9,78,16)).astype(np.float64)
        change[:,0,:]=-rng.integers(0,5,(9,16))
        bad=(rng.random((78,16))<.2).astype(np.int64)
        allowance=rng.integers(0,20,9).astype(np.float64);allowance[6:8]=0
        for target in (6,7):
            moves,predicted,accepted=priority.select(change,bad,colours,colour,directions,allowance,target)
            independent=np.zeros(9);seen=set()
            for item in accepted:
                node,direction=item['node'],item['direction']
                assert node not in seen and colours[node]==colour and bad[direction,node]==0
                seen.add(node);independent+=change[:,direction,node]
                np.testing.assert_array_equal(moves[node],directions[direction])
                exchanges+=int(item['uses_prior_budget'])
            for node in set(range(16))-seen:np.testing.assert_array_equal(moves[node],np.zeros(3))
            np.testing.assert_array_equal(independent,predicted)
            assert np.all(independent<=allowance+1e-8)
            assert np.all(independent[6:8]<=0);checks+=1
    # 构造仅有已取得余额才可接受的方向，独立断言两目标都执行预算交换。
    colours=np.zeros(2,np.int32);change=np.ones((9,78,2))*100;bad=np.ones((78,2),np.int64)
    for target in (6,7):
        change[:,0,0]=-2;bad[0,0]=0
        change[:,1,1]=1;change[6:8,1,1]=0;change[target,1,1]=-3;bad[1,1]=0
        moves,predicted,accepted=priority.select(change,bad,colours,0,directions,np.zeros(9),target)
        assert len(accepted)==2 and any(v['uses_prior_budget'] for v in accepted)
        assert predicted[target]==-5 and np.all(predicted<=0);target_checks+=1
    invalid=0
    for allowance,target in ((np.zeros(8),6),(-np.ones(9),6),(np.zeros(9),0)):
        try:priority.select(change,bad,colours,0,directions,allowance,target)
        except ValueError:invalid+=1
        else:raise AssertionError('非法预算/目标被接受')
    # RGB恒等后缀与显式重复样本独立计算，覆盖d²=11/12/56/57边界。
    suffix=np.empty((256**3,3),np.uint8)
    for start in range(0,len(suffix),1<<18):
        keys=np.arange(start,min(start+(1<<18),len(suffix)),dtype=np.uint32)
        suffix[start:start+len(keys)]=np.stack((keys>>16,(keys>>8)&255,keys&255),axis=1).astype(np.uint8)
    output=np.array([[5,1,1],[6,4,2],[7,2,2],[0,0,0],[255,255,255]],np.uint8)
    reference=np.array([[2,0,0],[0,0,0],[0,0,0],[1,2,3],[250,254,254]],np.uint8)
    frequency=np.array([1,2,3,4,5],np.int64);mass=np.array([0.,.1,.2,0.,.7])
    measured,square=an.measure(output,reference,suffix,frequency,mass,11,56)
    np.testing.assert_array_equal(square[:3],[11,56,57])
    expanded=np.repeat(np.arange(len(output)),frequency);squared=np.sum((output[expanded].astype(np.int64)-reference[expanded])**2,axis=1)
    distance=np.sqrt(squared.astype(np.float64));expanded_mass=np.repeat(mass/frequency,frequency)
    expected=np.asarray([distance.sum(),expanded_mass@distance,squared.sum(),expanded_mass@squared,
        np.maximum(squared-11,0).sum(),np.maximum(squared-36,0).sum(),np.count_nonzero(squared>11),
        np.count_nonzero(squared>56),np.maximum(squared-49,0).sum()],np.float64)
    np.testing.assert_allclose(measured,expected,rtol=0,atol=1e-12)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    save(args.output,{'pass':True,'random_selector_cases':checks,'observed_budget_exchanges':exchanges,
        'constructed_priority_checks':target_checks,'reject_cases':invalid,'weighted_threshold_rows':len(output),
        'expanded_rows':len(expanded),'weighted_error':float(np.max(np.abs(measured-expected))),
        'sources':{f.relative_to(ROOT).as_posix():digest(f) for f in (Path(__file__),ROOT/'python/lutlab/channel_arrival_priority.py')},
        'scope':'独立重算选择器的全部返回收益、预算、parity、方向与非法输入；11/56阈值显式重复支撑。收益几何复用已单独验收的an.gains，实际全域fresh/oracle另核。'})
    print({'pass':True,'selector_cases':checks,'constructed_cases':target_checks,'reject_cases':invalid},flush=True)


if __name__=='__main__':main()
