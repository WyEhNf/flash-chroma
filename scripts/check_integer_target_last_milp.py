"""核对参数化p99约束边界与两有限已知可行模型，实际整数前向另验。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import warnings
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from scipy.optimize import milp
from lutlab import integer_target_last_milp as lm,channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle
from run_channel_tail_nodes import save,digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖参数化合同')
    model=cc.from_sparse(io.SparseLut(io.uniform_grid(17),np.zeros((17,17,17,3),np.uint8)))
    arrivals=np.asarray([[5,8,9],[11,13,17],[250,252,255]],np.uint8)
    gold=np.asarray([[3,0,0],[3,1,0],[7,0,0]],np.uint8);frequency=np.asarray([1,3,4],np.int64);mass=np.asarray([.1,.2,.7])
    output=integer_oracle(model,arrivals);square=np.sum((output.astype(np.int32)-gold.astype(np.int32))**2,axis=1)
    records=[]
    for p99 in (9,12):
        dist=np.sqrt(square);baseline=np.asarray([frequency@dist,mass@dist,frequency@square,mass@square,0,0,frequency@(square>p99),0,0],np.float64)
        state=lm.build(model,arrivals,gold,frequency,mass,baseline,p99_squared=p99,node_radius=1)
        rows=state['rows'];assert all(rows.hi[row]==p99 for row in state['outlier_rows'])
        assert all(rows.lo[row]==-np.sqrt(p99) for row in state['cvar_rows'])
        assert abs(rows.hi[state['excess_row']]-float(frequency@np.maximum(dist-np.sqrt(p99),0)))<1e-12
        with warnings.catch_warnings(record=True) as warnings_seen:
            result=milp(state['cost'],integrality=state['integrality'],bounds=state['bounds'],constraints=rows.constraint(),
                options={'threads':1,'time_limit':10.,'node_limit':1000,'mip_rel_gap':0.})
        if result.x is None:raise AssertionError('已知可行模型无incumbent')
        values=np.rint(result.x[state['block']['node']]).astype(np.uint8)
        assert np.max(np.abs(result.x[state['block']['node']]-values))<1e-5
        nodes=model.nodes.copy();nodes.reshape(-1,3)[state['active']]=values
        candidate=cc.ChannelLut(model.grid,nodes,model.idx,model.channel_frac)
        actual=integer_oracle(candidate,state['unique']);solver=np.rint(result.x[state['block']['output']]).astype(np.uint8)
        np.testing.assert_array_equal(actual,solver)
        d2=np.sum((actual[state['inverse']].astype(np.int32)-gold.astype(np.int32))**2,axis=1)
        assert d2.max()<=49 and frequency@(d2>p99)<=baseline[6]
        records.append({'p99_squared':p99,'status':int(result.status),'message':str(result.message),'actual_y_byte_mismatches':0,
            'warnings':[str(w.message) for w in warnings_seen]})
    rejected=0
    for target,p99,radius in ((9,9,2),(49,-1,2),(49,9,-1)):
        try:lm.build(model,arrivals,gold,frequency,mass,baseline,target_squared=target,p99_squared=p99,node_radius=radius)
        except ValueError:rejected+=1
        else:raise AssertionError('非法阈值被接受')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    save(args.output,{'pass':True,'finite_models':records,'reject_cases':rejected,
        'source_sha256':{path.relative_to(ROOT).as_posix():digest(path) for path in (Path(__file__),ROOT/'python/lutlab/integer_target_last_milp.py',ROOT/'python/lutlab/integer_last_milp.py',ROOT/'scripts/verify_channel_coordinates.py')},
        'scope':'参数9/12的outlier/固定阈值CVaR行边界及有限物理输出；旧half-up/平方/精确Cauchy合同保持原件，实际新全支撑及native另验。'})
    print({'pass':True,'finite_models':len(records),'rejects':rejected},flush=True)


if __name__=='__main__':main()
