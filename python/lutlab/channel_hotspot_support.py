"""首级物理节点的完整正支撑与独立八角解析权重；不进行拟合。"""
from __future__ import annotations
import itertools
import math
import numpy as np
from . import interp, io


DIRECTIONS = np.array([v for scale in (1, 2) for v in itertools.product((-scale, 0, scale), repeat=3)
                       if v != (0, 0, 0)], dtype=np.int32)


def key(points):
    return ((points[:, 0].astype(np.uint32) << 16) |
            (points[:, 1].astype(np.uint32) << 8) | points[:, 2].astype(np.uint32))


def rgb(keys):
    keys = np.asarray(keys, np.uint32)
    return np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)


def basis(model, points):
    """主要提案设计沿用权威四面体权重；结果为有符号64位累加。"""
    indices, weights = [], []
    acc = np.empty((len(points), 3), np.int64)
    nodes = model.nodes.reshape(-1, 3).astype(np.int64)
    for channel in range(3):
        i, w = interp.tetra_index_weights_q(points, model.idx, model.channel_frac[channel], model.m)
        indices.append(i); weights.append(w)
        acc[:, channel] = np.sum(w.astype(np.int64)*nodes[i, channel], axis=1, dtype=np.int64)
    return np.asarray(indices), np.asarray(weights), acc


def corners(model, points):
    """用八角帽函数计算权重，不调用四面体排序/索引实现。"""
    base = ((model.idx[0, points[:, 0]].astype(np.int64)*model.m +
             model.idx[1, points[:, 1]])*model.m + model.idx[2, points[:, 2]])
    offsets = np.array([0, 1, model.m, model.m+1, model.m**2,
                        model.m**2+1, model.m**2+model.m, model.m**2+model.m+1], np.int64)
    weights = np.empty((len(points), 8, 3), np.int32)
    for channel in range(3):
        x, y, z = [model.channel_frac[channel, axis, points[:, axis]].astype(np.int32) for axis in range(3)]
        weights[:, 0, channel] = io.ONE-np.maximum(np.maximum(x, y), z)
        weights[:, 7, channel] = np.minimum(np.minimum(x, y), z)
        weights[:, 4, channel] = np.maximum(x-np.maximum(y, z), 0)
        weights[:, 2, channel] = np.maximum(y-np.maximum(x, z), 0)
        weights[:, 1, channel] = np.maximum(z-np.maximum(x, y), 0)
        weights[:, 6, channel] = np.maximum(np.minimum(x, y)-z, 0)
        weights[:, 5, channel] = np.maximum(np.minimum(x, z)-y, 0)
        weights[:, 3, channel] = np.maximum(np.minimum(y, z)-x, 0)
    if np.any(weights < 0) or np.any(weights.sum(axis=1, dtype=np.int64) != io.ONE):
        raise AssertionError('八角权重非负/分区守恒失败')
    return base[:, None]+offsets, weights


def box(model, physical_node, maximum_rows):
    """节点在三个共享idx轴的全部两侧编码盒，含0和末端节点。"""
    coordinate = np.unravel_index(int(physical_node), (model.m,)*3)
    axes = [np.flatnonzero((model.idx[a] == coordinate[a]) |
                          (model.idx[a].astype(np.int64) == coordinate[a]-1)).astype(np.uint8)
            for a in range(3)]
    rows = math.prod(len(a) for a in axes)
    if rows > maximum_rows:
        raise MemoryError('单节点完整编码盒超过冻结资源界')
    return np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1, 3)


def support(model, physical_node, maximum_rows):
    points = box(model, physical_node, maximum_rows)
    indices, weights, acc = basis(model, points)
    node_weight = np.sum(np.where(indices == physical_node, weights, 0), axis=2).T
    positive = np.any(node_weight > 0, axis=1)
    independent_i, independent_w = corners(model, points)
    independent_weight = np.sum(np.where((independent_i == physical_node)[:, :, None], independent_w, 0), axis=1)
    np.testing.assert_array_equal(node_weight, independent_weight)
    independent_acc = np.sum(independent_w.astype(np.int64)*model.nodes.reshape(-1, 3)[independent_i], axis=1)
    np.testing.assert_array_equal(acc, independent_acc)
    return points[positive], acc[positive], node_weight[positive]


def histogram(square, count=None, size=51):
    if count is None:
        return np.bincount(square, minlength=size).astype(np.int64)
    result = np.bincount(square, weights=count, minlength=size)
    if np.any(result != np.rint(result)) or result.sum() > 2**53:
        raise AssertionError('整数频数的直方图精确累加界失败')
    return result.astype(np.int64)


def metrics(hist):
    hist = np.asarray(hist, np.int64)
    total = int(hist.sum())
    if total <= 0 or np.any(hist < 0):
        raise ValueError('精确完整直方图需要非负计数与正总数')
    cumulative = hist.cumsum()
    # 用整数分数表达NumPy linear的99%位置，避免大计数浮点排位。
    position = 99*(total-1)
    lo_rank, remainder = divmod(position, 100)
    hi_rank = lo_rank + int(remainder != 0)
    lo, hi = np.searchsorted(cumulative, [lo_rank, hi_rank], side='right')
    tail_count = (total+99)//100
    remaining, terms = tail_count, []
    for d2 in np.flatnonzero(hist)[::-1]:
        take = min(remaining, int(hist[d2])); terms.append(take*math.sqrt(int(d2))); remaining -= take
        if not remaining:
            break
    return {'n': total, 'mean': math.fsum(int(v)*math.sqrt(i) for i, v in enumerate(hist))/total,
            'rms': math.sqrt(sum(int(v)*i for i, v in enumerate(hist))/total),
            'p99': math.sqrt(int(lo))+(remainder/100)*(math.sqrt(int(hi))-math.sqrt(int(lo))),
            'max_squared': int(np.flatnonzero(hist)[-1]), 'cvar_1pct': math.fsum(terms)/tail_count}
