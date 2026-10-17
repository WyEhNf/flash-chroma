"""固定单元的局部最小最大拟合、整数最小修改，以及与求解器无关的必要误差证书。"""
import math
import numpy as np
from scipy.optimize import Bounds,LinearConstraint,linprog,milp
from . import interp,io


def combination_bound(model,points,targets,multipliers):
    points,targets = np.asarray(points),np.asarray(targets)
    if (points.ndim != 2 or points.shape[1:] != (3,) or targets.shape != points.shape or points.dtype != np.uint8 or targets.dtype != np.uint8
            or len(multipliers) != len(points) or any(type(x) is not int for x in multipliers) or not any(multipliers)):
        raise ValueError("整数证书需要RGB8输入/参考及等长的非零整数乘子")
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
    terms = {}
    for ids,row,multiplier in zip(indices,weights,multipliers):
        for node,w in zip(ids,row):terms[int(node)] = terms.get(int(node),0)+multiplier*int(w)
    terms = {n:c for n,c in terms.items() if c}
    norm = sum(abs(x) for x in multipliers)
    low = 255*sum(min(0,c) for c in terms.values())
    high = 255*sum(max(0,c) for c in terms.values())
    target = [65536*sum(k*int(t[c]) for k,t in zip(multipliers,targets)) for c in range(3)]
    # 三通道分别应用箱约束及half-up舍入的保守1/2余量，再利用误差整数性向上取整。
    margins = [max(low-t,t-high)-32768*norm for t in target]
    bounds = [max(0,-(-m//(65536*norm))) for m in margins]
    selected = [i for i,k in enumerate(multipliers) if k]
    return {"points":points[selected].tolist(),"targets":targets[selected].tolist(),"multipliers":[str(multipliers[i]) for i in selected],
        "node_coefficients":[[n,str(c)] for n,c in sorted(terms.items())],"coefficient_l1":str(norm),
        "target_q16":list(map(str,target)),"node_range_q16":[str(low),str(high)],"rounding_allowance_q16":str(32768*norm),
        "channel_lower_bounds":bounds,"rgb_l2_max_lower_bound":max(bounds),
        "scope":"固定权威idx/frac及Q16四面体、任意合法RGB8节点的必要误差；乘子由数值求解提议，结论仅依赖整数证书；不涵盖其他网格/恢复或最终四级"}


def design(model,points):
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
    nodes = np.unique(indices[weights > 0])
    matrix = np.zeros((len(points),len(nodes)),np.int64)
    for row,(ids,ws) in enumerate(zip(indices,weights)):
        for node,w in zip(ids,ws):
            if w:matrix[row,np.searchsorted(nodes,node)] += int(w)
    return nodes,matrix


def changed(model,nodes,values,channel=2):
    idx,frac = model.tables()
    result = io.SparseLut(model.grid.copy(),model.nodes.copy(),idx.copy(),frac.copy())
    result.nodes.reshape(-1,3)[nodes,channel] = values
    return result


def relaxed_minimax(model,points,targets,*,dual_scale=1000000):
    nodes,matrix = design(model,points)
    a = matrix/65536.
    n = len(points)
    objective = np.r_[np.zeros(len(nodes)),1.]
    constraints = np.vstack((np.column_stack((a,-np.ones(n))),np.column_stack((-a,-np.ones(n)))))
    result = linprog(objective,A_ub=constraints,b_ub=np.r_[targets[:,2].astype(float),-targets[:,2].astype(float)],
        bounds=[(0,255)]*len(nodes)+[(0,None)],method="highs")
    if not result.success:raise RuntimeError("局部连续最小最大求解未成功："+result.message)
    dual = result.ineqlin.marginals[:n]-result.ineqlin.marginals[n:]
    scale = float(np.max(np.abs(dual)))
    multipliers = [int(x) for x in np.rint(dual/scale*dual_scale)] if scale else [1]+[0]*(n-1)
    divisor = math.gcd(*multipliers)
    multipliers = [k//divisor for k in multipliers]
    certificate = combination_bound(model,points,targets,multipliers)
    candidate = changed(model,nodes,np.floor(result.x[:-1]+.5).astype(np.uint8))
    return candidate,{"channel":"B","continuous_objective":float(result.fun),"iterations":int(result.nit),
        "node_ids":nodes.tolist(),"continuous_nodes":result.x[:-1].tolist(),"certificate":certificate,
        "scope":"连续B通道局部最小最大解仅用于产生整数见证和证书；不把求解器浮点最优标记当作必要下界"}


def minimum_change(model,points,targets,*,rgb_max,max_delta,time_limit=60,channel=2):
    if type(rgb_max) is not int or rgb_max < 0 or type(max_delta) is not int or not 0 <= max_delta <= 255:
        raise ValueError("局部RGB上限与修改范围必须为合法整数")
    if type(channel) is not int or channel not in (0,1,2):raise ValueError("主改通道必须为R/G/B之一")
    nodes,matrix = design(model,points)
    count = len(nodes)
    current = model.nodes.reshape(-1,3)[nodes,channel].astype(float)
    prediction = interp.apply_tetra_q16(model,points).astype(np.int32)
    other = [c for c in range(3) if c != channel]
    rg = np.sum((prediction[:,other]-targets[:,other].astype(np.int32))**2,axis=1)
    remaining = rgb_max**2-rg
    if np.any(remaining < 0):return None,{"success":False,"reason":"其余固定通道本身已经超出RGB目标"}
    allowance = np.array([math.isqrt(int(v)) for v in remaining])
    lower = np.maximum(0,targets[:,channel].astype(int)-allowance)*65536-32768
    upper = (np.minimum(255,targets[:,channel].astype(int)+allowance)+1)*65536-32769
    # 输出为floor((整数累加+32768)/65536)，上界减1保留严格端点，不能写成连续闭区间近似。
    a = np.vstack((np.column_stack((matrix,np.zeros_like(matrix))),np.column_stack((np.eye(count),-np.eye(count))),
        np.column_stack((-np.eye(count),-np.eye(count)))))
    constraints = LinearConstraint(a,np.r_[lower,np.full(2*count,-np.inf)],np.r_[upper,current,-current])
    result = milp(np.r_[np.zeros(count),np.ones(count)],integrality=np.r_[np.ones(count),np.zeros(count)],
        bounds=Bounds(np.r_[np.maximum(0,current-max_delta),np.zeros(count)],np.r_[np.minimum(255,current+max_delta),np.full(count,max_delta)]),
        constraints=constraints,options={"time_limit":time_limit,"mip_rel_gap":0.})
    info = {"success":bool(result.success),"status":int(result.status),"solver_message":result.message,"rgb_max":rgb_max,"max_delta":max_delta,"channel":channel,
        "scope":"只求固定单元内选定通道整数节点的最小L1修改；尚未满足照片/完整域保护，实际Q16输出必须重放"}
    if not result.success:return None,info
    values = np.rint(result.x[:count])
    if np.max(np.abs(values-result.x[:count])) > 1e-5:raise ValueError("MILP返回的节点不满足整数契约")
    candidate = changed(model,nodes,values.astype(np.uint8),channel)
    squared = np.sum((interp.apply_tetra_q16(candidate,points).astype(np.int32)-targets)**2,axis=1)
    if np.any(squared > rgb_max**2):raise AssertionError("MILP候选真实Q16输出未满足RGB上限")
    info.update(node_ids=nodes.tolist(),l1_change=int(np.sum(np.abs(values-current))),mip_gap=float(result.mip_gap))
    return candidate,info
