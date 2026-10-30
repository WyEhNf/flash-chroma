"""一次集中检验单调路径最优性和完整Q16事件，不代替真实精度终验。"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from numba import njit
from lutlab import axis_calibration as ac, exact_axis, interp, io, monotone_axis, study_provenance
from run_filmic_calibration import integer_oracle


@njit(cache=False)
def brute_events(points, nodes, idx, frac, targets, caps, mass, rho, axis, losses, violations):
    maximum, mismatch = 0., 0
    for f in range(io.ONE+1):
        value, bad = 0., 0
        for p in range(len(points)):
            rgb = ac._pixel(nodes, idx, frac, 17, int(points[p,0]), int(points[p,1]), int(points[p,2]), axis, f-frac[axis,128])
            squared = 0
            for c in range(3): squared += (rgb[c]-int(targets[p,c]))**2
            value += mass[p]*rho[squared];bad += int(squared > caps[p])
        maximum=max(maximum,abs(value-losses[f]));mismatch += bad != violations[f]
    return maximum,mismatch


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('不覆盖旧合同')
    args.output.mkdir(parents=True);numba.set_num_threads(4)
    rng=np.random.default_rng(2026101913);cases=0
    for _ in range(64):
        rows,width=int(rng.integers(2,6)),int(rng.integers(2,8))
        costs=rng.integers(0,17,(rows,width)).astype(np.float64)
        forbidden=rng.random((rows,width))<.3;original=np.sort(rng.integers(0,width,rows))
        path,value,displacement=monotone_axis.isotonic_path(costs,forbidden,original)
        feasible=[]
        for sequence in itertools.combinations_with_replacement(range(width),rows):
            if any(forbidden[i,f] for i,f in enumerate(sequence)):continue
            feasible.append((sum(costs[i,f] for i,f in enumerate(sequence)),sum(abs(f-original[i]) for i,f in enumerate(sequence))))
        if not feasible:assert not np.isfinite(value) and np.all(path==-1)
        else:
            optimum=min(feasible)
            assert (value,displacement)==optimum
            assert np.all(np.diff(path)>=0) and not np.any(forbidden[np.arange(rows),path])
        cases+=1
    costs=np.full((2,io.ONE+1),np.inf);forbidden=np.zeros(costs.shape,np.bool_)
    costs[0,15000]=4;costs[0,25000]=0;costs[1,26000]=0;costs[1,30000]=3
    path,value,_=monotone_axis.isotonic_path(costs,forbidden,np.array([10000,30000],np.int64))
    assert value==0 and path.tolist()==[25000,26000] and path[0]>20000
    # 全256码的同单元边界、端点固定、非单调idx及不可行端点拒绝。
    whole=np.full((256,io.ONE+1),np.inf);bad=np.zeros(whole.shape,np.int64)
    idx=np.minimum(np.arange(256)//16,15).astype(np.uint8)
    original=np.linspace(0,io.ONE,256).astype(np.int64)
    whole[np.arange(256),original]=0
    chosen,total=monotone_axis.choose_axis(whole,bad,idx,original)
    assert np.array_equal(chosen,original) and total==0
    bad[0,original[0]]=1
    try:monotone_axis.choose_axis(whole,bad,idx,original)
    except ValueError:pass
    else:raise AssertionError('冻结端点不能覆盖已有违规')
    del whole,bad
    grid=np.tile(np.linspace(0,255,17,dtype=np.float32),(3,1))
    model=io.SparseLut(grid,rng.integers(116,140,(17,17,17,3),dtype=np.uint8))
    idx,frac0=model.tables();frac=frac0.astype(np.int64)
    suffix=np.empty((256**3,3),np.uint8)
    for start in range(0,len(suffix),1<<18):
        k=np.arange(start,start+(1<<18),dtype=np.int64)
        suffix[start:start+len(k)]=np.column_stack((k>>16,(k>>8)&255,k&255)).astype(np.uint8)
    events=[]
    for axis in range(3):
        points=rng.integers(0,256,(17,3),dtype=np.uint8);points[:,axis]=128
        targets=rng.integers(118,138,points.shape,dtype=np.uint8)
        mass=rng.random(len(points));mass[:2]=0;mass/=mass.sum()
        caps=rng.integers(0,150,len(points),dtype=np.int32)
        root=np.sqrt(np.arange(3*255**2+1,dtype=np.float64));rho=root+.02*np.maximum(root-6.,0.)**2
        order=np.argsort(points[:,axis],kind='stable').astype(np.int64)
        offsets=np.r_[0,np.cumsum(np.bincount(points[:,axis],minlength=256))].astype(np.int64)
        diff,bdiff,base,count,invalid=exact_axis.events(points,model.nodes.reshape(-1,3),idx,frac,17,
            targets,targets,targets,caps,suffix,mass,rho,0.,axis,np.zeros(256,np.int64),
            np.full(256,io.ONE,np.int64),order,offsets,io.ONE+1)
        assert not np.any(invalid)
        losses,violations=np.cumsum(diff[128]),np.cumsum(bdiff[128])
        error,mismatch=brute_events(points,model.nodes.reshape(-1,3),idx,frac,targets,caps,mass,rho,axis,losses,violations)
        assert error<1e-8 and mismatch==0,(error,mismatch)
        assert np.count_nonzero(violations)>0
        for f in (0,1,1024,32768,65535,65536):
            new=frac0.copy();new[axis,128]=f
            candidate=io.SparseLut(grid,model.nodes,idx,new)
            np.testing.assert_array_equal(interp.apply_tetra_q16(candidate,points),integer_oracle(candidate,points))
        events.append({'axis':axis,'integer_states':io.ONE+1,'points':len(points),'maximum_cost_difference':error,
                       'cap_count_mismatches':mismatch,'events':int(count.sum())})
        del diff,bdiff
    files=['python/lutlab/monotone_axis.py','python/lutlab/exact_axis.py','python/lutlab/axis_calibration.py',
           'python/lutlab/io.py','python/lutlab/interp.py','python/lutlab/study_provenance.py',
           'scripts/verify_monotone_axis.py','scripts/run_filmic_calibration.py']
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in files:z.write(ROOT/name,name)
    result={'purpose':'64个独立穷举单调DP、静态边界反例、端点/不可行检查；三轴完整65537事件状态及独立u64 oracle',
        'environment':study_provenance.environment_fingerprint(),'numba_threads':numba.get_num_threads(),'seed':2026101913,
        'dp_cases':cases,'full_state_counterexample':path.tolist(),'events':events,
        'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
        'pass':True,'scope':'合成小输入实现合同，不是新真实LUT精度/百图/性能验证'}
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
