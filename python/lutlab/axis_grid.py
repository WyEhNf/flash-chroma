"""边界/热点切线的RGB8弦误差与两遍最小最大网格DP。"""
from __future__ import annotations

import hashlib
import itertools
import numpy as np

from . import interp, io

INF = 1 << 60


def axis_curves(table, axis, hotspots, *, anchors=9, hot_lines=32):
    """同时保留0/255边界，并按冻结热点及其±1垂直邻域补充切线。"""
    if axis not in (0,1,2) or not 2 <= anchors <= 256 or hot_lines < 0:
        raise ValueError("切线轴或采样参数无效")
    perpendicular = [a for a in range(3) if a != axis]
    levels = np.rint(np.linspace(0,255,anchors)).astype(np.uint8)
    pairs = list(itertools.product(map(int,levels),repeat=2))
    seen, added = set(pairs), 0
    offsets = [(0,0)] + [d for d in itertools.product((-1,0,1),repeat=2) if d != (0,0)]
    for colour in hotspots:
        for dr,dg in offsets:
            pair = tuple(int(np.clip(int(colour[a])+d,0,255)) for a,d in zip(perpendicular,(dr,dg)))
            if pair not in seen and added < hot_lines:
                pairs.append(pair)
                seen.add(pair)
                added += 1
    points = np.empty((256,len(pairs),3),np.uint8)
    points[:,:,axis] = np.arange(256,dtype=np.uint8)[:,None]
    for index,a in enumerate(perpendicular):
        points[:,:,a] = np.array(pairs,np.uint8)[None,:,index]
    flat = points.reshape(-1,3)
    values = table(flat) if callable(table) else table[flat[:,0],flat[:,1],flat[:,2]]
    values = np.asarray(values,dtype=np.uint8).reshape(points.shape)
    return values,{"axis":axis,"perpendicular_axes":perpendicular,"line_pairs":[list(p) for p in pairs],
        "anchor_lines":anchors**2,"hot_lines":added,"rgb_bytes_sha256":hashlib.sha256(values.tobytes()).hexdigest(),
        "scope":"完整参考的指定1D切线，包含端点；不是全部3D色域误差"}


def chord_costs(curves, *, min_step=1, max_step=16):
    """所有候选弦使用Q16权重和RGB8舍入，max/SSE均为精确整数。"""
    curves = np.asarray(curves)
    n = len(curves)
    if curves.dtype != np.uint8 or curves.ndim != 3 or curves.shape[2] != 3 or not curves.shape[1] or not 1 <= min_step <= max_step < n:
        raise ValueError("弦代价需要uint8 (轴长度,切线数,3)及有效步长")
    worst = np.full((n,n),INF,np.int64)
    sse = np.full((n,n),INF,np.int64)
    for start in range(n-1):
        for end in range(start+min_step,min(n,start+max_step+1)):
            width = end-start
            offset = np.arange(width+1,dtype=np.int64)
            fraction = (offset*io.ONE*2+width)//(2*width)
            a,b = curves[start].astype(np.int64),curves[end].astype(np.int64)
            prediction = ((io.ONE-fraction[:,None,None])*a+fraction[:,None,None]*b+io.ONE//2) >> io.Q
            delta = prediction-curves[start:end+1].astype(np.int64)
            squared = np.sum(delta*delta,axis=2)
            worst[start,end],sse[start,end] = int(squared.max()),int(squared.sum())
    return worst,sse


def choose_knots(worst,sse,m,*,min_step=1,max_step=16,objective="minimax"):
    """先求最小瓶颈，再在该瓶颈下优化SSE；不能用单遍词典序代替。"""
    worst,sse = np.asarray(worst),np.asarray(sse)
    n = len(worst)
    if (worst.shape != (n,n) or sse.shape != (n,n) or worst.dtype.kind not in "iu" or sse.dtype.kind not in "iu"
            or not 2 <= m <= n or not 1 <= min_step <= max_step < n or objective not in ("minimax","sse")):
        raise ValueError("网格DP形状、整数代价或参数无效")
    bottleneck = np.full((m,n),INF,np.int64)
    bottleneck[0,0] = 0
    for k in range(1,m):
        for end in range(k*min_step,min(n-1,k*max_step)+1):
            for start in range(max((k-1)*min_step,end-max_step),end-min_step+1):
                value = max(int(bottleneck[k-1,start]),int(worst[start,end]))
                if value < bottleneck[k,end]:
                    bottleneck[k,end] = value
    optimum = int(bottleneck[m-1,n-1])
    if optimum >= INF:
        raise ValueError("节点数和步长约束下不存在覆盖路径")
    threshold = optimum if objective == "minimax" else INF-1
    loss,penalty = np.full((m,n),INF,np.int64),np.full((m,n),INF,np.int64)
    parent = np.full((m,n),-1,np.int32)
    loss[0,0],penalty[0,0] = 0,0
    for k in range(1,m):
        for end in range(k*min_step,min(n-1,k*max_step)+1):
            best = None
            for start in range(max((k-1)*min_step,end-max_step),end-min_step+1):
                if loss[k-1,start] >= INF or worst[start,end] > threshold or sse[start,end] >= INF:
                    continue
                value = (int(loss[k-1,start])+int(sse[start,end]),
                         int(penalty[k-1,start])+(end*(m-1)-(n-1)*k)**2,start)
                if best is None or value < best:
                    best = value
            if best is not None:
                loss[k,end],penalty[k,end],parent[k,end] = best
    if parent[m-1,n-1] < 0:
        raise ArithmeticError("瓶颈可行但第二遍DP没有找到路径")
    knots = [n-1]
    for k in range(m-1,0,-1):
        knots.append(int(parent[k,knots[-1]]))
    knots.reverse()
    selected_worst = max(int(worst[a,b]) for a,b in zip(knots[:-1],knots[1:]))
    # 独立的布尔可达检查：最优瓶颈再减1时不应存在同节点数覆盖路径。
    reachable = np.zeros((m,n),bool)
    reachable[0,0] = True
    for k in range(1,m):
        for end in range(k*min_step,min(n-1,k*max_step)+1):
            reachable[k,end] = any(reachable[k-1,start] and worst[start,end] < optimum
                for start in range(max((k-1)*min_step,end-max_step),end-min_step+1))
    if reachable[m-1,n-1]:
        raise AssertionError("最小瓶颈被更低阈值的可达路径推翻")
    return np.asarray(knots,np.float64),{"objective":objective,"knots":knots,"minimax_squared_optimum":optimum,
        "selected_worst_squared":selected_worst,"selected_sse":int(loss[m-1,n-1]),
        "tie_penalty":int(penalty[m-1,n-1]),"strictly_lower_bottleneck_reachable":False,
        "min_step":min_step,"max_step":max_step,
        "scope":"给定切线/合法整数弦代价上的全路径DP；不证明拟合后3D模型全局最优"}


def audit_normal_rows(table,grid,H,b,*,row_count=4):
    """用独立局部RGB笛卡尔支撑核对完整域原生H/b，覆盖最窄节点区。"""
    m = grid.shape[1]
    idx,frac = io.axis_tables(grid)
    choices = []
    for axis in range(3):
        narrow = int(np.argmin(np.diff(grid[axis])))
        coordinates = [m//2]*3
        coordinates[axis] = narrow+1
        choices.append(tuple(coordinates))
    choices.append((0,0,0))
    records = []
    for coordinates in list(dict.fromkeys(choices))[:row_count]:
        node = (coordinates[0]*m+coordinates[1])*m+coordinates[2]
        axes = [np.flatnonzero((idx[a] == c-1)|(idx[a] == c)).astype(np.uint8) for a,c in enumerate(coordinates)]
        points = np.stack(np.meshgrid(*axes,indexing="ij"),-1).reshape(-1,3)
        indices,weights = interp.tetra_weights(points,idx,frac,m)
        own = np.sum(np.where(indices == node,weights,0.),axis=1)
        row = np.bincount(indices.ravel(),weights=(weights*own[:,None]/64).ravel(),minlength=m**3)
        targets = table[points[:,0],points[:,1],points[:,2]].astype(np.float64)
        rhs = np.sum(own[:,None]*targets/64,axis=0)
        if not np.array_equal(row,H.getrow(node).toarray()[0]) or not np.array_equal(rhs,b[node]):
            raise AssertionError("完整域原生矩阵行与独立局部支撑组装不同")
        records.append({"node":node,"coordinates":list(coordinates),"support_box_colours":len(points),
            "positive_support_colours":int(np.count_nonzero(own)),"normal_row_max_difference":0.,"rhs_max_difference":0.})
    return records
