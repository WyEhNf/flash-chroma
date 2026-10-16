"""完整域与照片等质量的有界节点拟合及分量整数目标比较。"""
from __future__ import annotations

import math
import numpy as np
import scipy.sparse as sp
from . import box, fit, interp, io, support_certificate


def photo_moments(model,points,targets):
    """保留重复像素频率；直接使用权威Q16整数表组装照片矩。"""
    if (points.dtype != np.uint8 or targets.dtype != np.uint8 or points.shape != targets.shape
            or points.ndim != 2 or points.shape[1] != 3 or not 0 < len(points) <= 1 << 20):
        raise ValueError("照片矩需要1至2^20个匹配RGB8样本")
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
    matrix = sp.csr_matrix((weights.astype(np.int64).ravel(),indices.ravel(),
        np.arange(0,4*len(points)+1,4,dtype=np.int32)),shape=(len(points),model.m**3))
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    # 每项非负，Hq<=P*2^32、bq<=P*65536*255，在本入口样本上界内不溢出。
    return (matrix.T @ matrix).tocsr(),matrix.T @ targets.astype(np.int64)


def equal_mass_system(H,b,Hq,bq,full_count,photo_count):
    """原生H/b含1/64标度；不能直接把它和照片求和，否则质量不等。"""
    if (not isinstance(full_count,int) or not isinstance(photo_count,int) or full_count <= 0 or photo_count <= 0
            or H.shape != Hq.shape or np.shape(b) != np.shape(bq) or b.shape != (H.shape[0],3)):
        raise ValueError("完整域/照片计数或矩形状无效")
    divisor = math.gcd(full_count,64*photo_count)
    a,c = 64*photo_count//divisor,full_count//divisor
    scale = 1 << (a+c-1).bit_length()
    alpha,beta = a/scale,c/scale
    system = (alpha*H+beta*(Hq.astype(np.float64)*2.**-32)).tocsr()
    rhs = alpha*b+beta*bq.astype(np.float64)*2.**-16
    return system,rhs,{"full_moment_scale":1/64,"full_count":full_count,"photo_count":photo_count,
        "full_coefficient": [a,scale],"photo_coefficient":[c,scale],
        "full_mass":alpha*full_count/64,"photo_mass":beta*photo_count,
        "scope":"两种测度等质量，连续三通道SSE；混合矩以float64求解，不冒称精确整数矩"}


def exact_change(H,b,Hq,bq,old,new,full_count,photo_count):
    """分别精确比较原生完整域与照片，再以Python整数交叉归约等质量目标。"""
    full = box.integer_sse_change_numerator(H,b,old,new)
    if Hq.dtype != np.int64 or bq.dtype != np.int64 or Hq.shape != H.shape or bq.shape != b.shape:
        raise ValueError("照片比较必须使用匹配的int64整数矩")
    largest_row = max(map(int,np.asarray(Hq.sum(axis=1)).ravel()))
    if largest_row*510+2*io.ONE*int(bq.max()) > np.iinfo(np.int64).max:
        raise OverflowError("照片整数矩超出安全行积范围")
    difference = (new.astype(np.int64)-old.astype(np.int64)).ravel()
    linear = (Hq @ (new.astype(np.int64)+old.astype(np.int64))-2*io.ONE*bq).ravel()
    photo = sum(int(difference[i])*int(linear[i]) for i in np.flatnonzero(difference))
    numerator = photo_count*full+full_count*photo
    return {"full_sse_change_numerator":str(full),"photo_sse_change_numerator":str(photo),
        "component_denominator_power":32,"equal_mass_change_numerator":str(numerator),
        "equal_mass_denominator":str(full_count*photo_count*(1 << 32)),
        "scope":"未舍入Q16插值的SSE均值之和；不保证最终RGB8 mean或尾部"}


def fit_equal_mass(table,model,points,H,b,*,full_count=256**3,diagnostics=None):
    """固定网格，不加隐藏先验；完整域正定支撑保证箱约束子问题可解。"""
    report = {} if diagnostics is None else diagnostics
    target = table(points) if callable(table) else table[points[:,0],points[:,1],points[:,2]]
    Hq,bq = photo_moments(model,points,target)
    system,rhs,mass = equal_mass_system(H,b,Hq,bq,full_count,len(points))
    support = support_certificate.certify(model.grid,*model.tables())
    lower_bound = support["hessian_eigenvalue_lower_bound"]
    if H.diagonal().min() < lower_bound:
        raise ValueError("完整域矩对角小于当前Q16设计的支撑证书下界")
    start = model.nodes.reshape(-1,3)
    continuous = box.solve_box(system,rhs,start,diagnostics=report.setdefault("solver",{}))
    candidate = fit.quantize(fit.int_refine(continuous,system,rhs)).reshape(-1,3)
    change = exact_change(H,b,Hq,bq,start,candidate,full_count,len(points))
    accepted = int(change["equal_mass_change_numerator"]) < 0
    report.update(mass=mass,integer_selection=change,accepted=accepted,lambda_prior=0.,support_certificate=support,
        continuous_gap_upper_bound=.5*report["solver"]["projected_gradient_l2_squared"]/(mass["full_coefficient"][0]/mass["full_coefficient"][1]*lower_bound),
        target_semantics="本级原完整LUT，逐样本RGB8标签；重复像素不去重，不用残差/复合标签",
        gap_scope="浮点KKT和完整域支撑下界的连续目标诊断，非RGB8精度证书")
    idx,frac = model.tables()
    return io.SparseLut(model.grid.copy(),(candidate if accepted else start).reshape(model.nodes.shape).copy(),idx.copy(),frac.copy())
