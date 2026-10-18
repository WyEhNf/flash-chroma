"""一次集中检验舍入区间目标值/梯度，不涉及真实LUT精度。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import io, rounding_interval, study_provenance


def reference(indices, weights, targets, mass, nodes, radii, half_width=.49, epsilon=.05,
              tail_at=6., tail_weight=.02, cap_weight=4., parts=4):
    prediction = np.einsum('nv,nvc->nc', weights.astype(np.float64)/io.ONE, nodes[indices])
    error = prediction-targets
    outside = np.maximum(np.abs(error)-half_width, 0.)
    norm = np.sqrt(np.sum(error*error, axis=1)+epsilon**2)
    dead = np.sqrt(np.sum(outside*outside, axis=1)+epsilon**2)-epsilon
    loss = dead+tail_weight*np.maximum(norm-tail_at, 0.)**2+cap_weight*np.maximum(norm-radii, 0.)**2
    return float(mass@loss)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖旧合同')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101912)
    n, size = 521, 67
    indices = rng.integers(0, size-1, (n, 4), dtype=np.int32)
    cuts = np.sort(rng.integers(0, io.ONE+1, (n, 3), dtype=np.int32), axis=1)
    weights = np.diff(np.column_stack((np.zeros(n, np.int32), cuts, np.full(n, io.ONE, np.int32))),axis=1).astype(np.int32)
    nodes = rng.uniform(20, 235, (size, 3))
    prediction = np.einsum('nv,nvc->nc', weights.astype(np.float64)/io.ONE, nodes[indices])
    targets = np.clip(np.floor(prediction+rng.normal(0, 4, prediction.shape)+.5), 0, 255).astype(np.uint8)
    mass = rng.random(n);mass[:17] = 0;mass /= mass.sum()
    radii = rng.uniform(2, 10, n)
    settings = dict(half_width=.49, epsilon=.05, tail_at=6., tail_weight=.02, cap_weight=4., parts=4)
    value, gradient = rounding_interval.objective(indices,weights,targets,mass,nodes,radii,**settings)
    value_ref = reference(indices,weights,targets,mass,nodes,radii,**settings)
    assert abs(value-value_ref) < 1e-12
    assert np.array_equal(gradient[-1], np.zeros(3))
    numeric=[]
    for _ in range(12):
        direction = rng.normal(size=nodes.shape); direction /= np.linalg.norm(direction)
        step=1e-4
        estimate=(reference(indices,weights,targets,mass,nodes+step*direction,radii,**settings)-reference(indices,weights,targets,mass,nodes-step*direction,radii,**settings))/(2*step)
        analytic=float(np.sum(gradient*direction));numeric.append(abs(estimate-analytic))
    assert max(numeric) < 2e-7,max(numeric)
    one, grad_one = rounding_interval.objective(indices,weights,targets,mass,nodes,radii,**{**settings,'parts':1})
    assert abs(one-value)<1e-12 and np.max(np.abs(gradient-grad_one))<1e-12
    # 正确标签盒内部为零；区间外和软cap都有损失，符号对称。
    small_i=np.zeros((3,4),np.int32);small_w=np.zeros((3,4),np.int32);small_w[:,0]=io.ONE
    small_t=np.full((3,3),100,np.uint8);small_m=np.full(3,1/3);small_r=np.full(3,1e6)
    zero,gzero=rounding_interval.objective(small_i,small_w,small_t,small_m,np.full((1,3),100.48),small_r,**settings)
    assert zero==0 and np.all(gzero==0)
    positive,gpositive=rounding_interval.objective(small_i,small_w,small_t,small_m,np.full((1,3),100.8),small_r,**settings)
    negative,gnegative=rounding_interval.objective(small_i,small_w,small_t,small_m,np.full((1,3),99.2),small_r,**settings)
    assert positive>0 and abs(positive-negative)<1e-12 and np.max(np.abs(gpositive+gnegative))<1e-12
    files=['python/lutlab/rounding_interval.py','scripts/verify_rounding_interval.py']
    sha={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in files:z.write(ROOT/name,name)
    result={'purpose':'521行合成固定Q16设计的目标/方向梯度/归约/内部零损失；不测试真实LUT、拟合收益或原生运行时',
        'environment':study_provenance.environment_fingerprint(),'seed':2026101912,'numba_threads':numba.get_num_threads(),
        'value_abs_error':abs(value-value_ref),'directions':12,'maximum_gradient_abs_error':max(numeric),
        'parts_gradient_max_error':float(np.max(np.abs(gradient-grad_one))),'unsupported_gradient_zero':True,
        'interior_zero_and_signed_symmetry':True,'source_sha256':sha,'pass':True}
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
