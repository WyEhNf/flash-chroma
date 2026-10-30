"""整数舍入/平方分段线性与有限MILP的独立物理输出合同。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
import warnings
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from scipy.optimize import milp
from lutlab import integer_last_milp as lm,channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle
from run_channel_tail_nodes import save,digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖整数规划合同')
    count=0
    for base in (0,1,127,254):
        acc=base*65536+np.arange(65536,dtype=np.int64);y=(acc+32768)//65536
        residual=acc-65536*y
        assert np.all((residual>=-32768)&(residual<=32767))
        for wrong in (y-1,y+1):
            residual=acc-65536*wrong;assert not np.any((residual>=-32768)&(residual<=32767))
        count+=len(acc)
    for d in range(-7,8):assert max((2*k+1)*d-k*(k+1) for k in range(-8,8))==d*d
    directions=[v for v in itertools.product((-1,0,1),repeat=3) if any(v)];normal_cases=0
    for delta in itertools.product(range(-7,8),repeat=3):
        for vector in directions:
            dot=sum(a*b for a,b in zip(delta,vector))
            if dot>0:assert dot*dot<=sum(a*a for a in delta)*sum(b*b for b in vector)
            normal_cases+=1
    model=cc.from_sparse(io.SparseLut(io.uniform_grid(17),np.zeros((17,17,17,3),np.uint8)))
    arrivals=np.asarray([[5,8,9],[11,13,17],[250,252,255]],np.uint8)
    reference=np.asarray([[0,1,1],[1,0,0],[0,0,1]],np.uint8);frequency=np.asarray([1,3,4],np.int64);mass=np.asarray([.1,.2,.7])
    old=integer_oracle(model,arrivals);delta=old.astype(np.int32)-reference.astype(np.int32);square=np.sum(delta*delta,axis=1);dist=np.sqrt(square)
    baseline=np.asarray([frequency@dist,mass@dist,frequency@square,mass@square,0,0,frequency@(square>12),0,0],np.float64)
    state=lm.build(model,arrivals,reference,frequency,mass,baseline)
    with warnings.catch_warnings(record=True) as warning_records:
        result=milp(state['cost'],integrality=state['integrality'],bounds=state['bounds'],constraints=state['rows'].constraint(),
            options={'time_limit':10.,'node_limit':1000,'threads':1,'mip_rel_gap':0.})
    if result.x is None:raise AssertionError('已知可行有限夹具没有incumbent')
    ids=state['block']['node'];values=np.rint(result.x[ids]).astype(np.uint8)
    assert np.max(np.abs(result.x[ids]-values))<1e-5
    nodes=model.nodes.copy();nodes.reshape(-1,3)[state['active']]=values
    candidate=cc.ChannelLut(model.grid,nodes,model.idx,model.channel_frac)
    actual=integer_oracle(candidate,state['unique']);proposed=np.rint(result.x[state['block']['output']]).astype(np.uint8)
    np.testing.assert_array_equal(actual,proposed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    save(args.output,{'pass':True,'rounding_cases':count,'squared_integer_values':15,'exact_cauchy_cases':normal_cases,
        'finite_milp_status':int(result.status),'finite_milp_message':str(result.message),'finite_milp_actual_bytes_mismatch':0,
        'forwarded_option_warnings':[str(w.message) for w in warning_records],
        'source_sha256':{f.relative_to(ROOT).as_posix():digest(f) for f in (Path(__file__),ROOT/'python/lutlab/integer_last_milp.py',ROOT/'scripts/verify_channel_coordinates.py')},
        'scope':'有限约束合同与精确Python整数不等式；不证明实际模型可行/全局最优或native性能。'})
    print({'pass':True,'rounding_cases':count,'finite_status':int(result.status),'cauchy_cases':normal_cases},flush=True)


if __name__=='__main__':main()
