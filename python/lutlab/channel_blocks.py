"""冻结分通道坐标，按2³节点块整体±1跨越整数舍入台阶。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit, prange
from . import channel_coordinates as cc, interp, io


def layout(m):
    """固定000原点分块；同奇偶色的不同块不会共享任何正权重像素。"""
    xyz = np.indices((m, m, m), dtype=np.int32).reshape(3, -1).T
    b = xyz//2
    side = (m+1)//2
    blocks = ((b[:, 0]*side+b[:, 1])*side+b[:, 2]).astype(np.int32)
    colours = ((b[:, 0]%2)*4+(b[:, 1]%2)*2+b[:, 2]%2).astype(np.uint8)
    return blocks, colours, side**3


def design(model, points, channel):
    """逐输出构造四面体；不借用另一输出的几何。"""
    indices = np.empty((len(points), 4), np.int32)
    weights = np.empty_like(indices)
    for start in range(0, len(points), 1 << 18):
        i, w = interp.tetra_index_weights_q(points[start:start+(1 << 18)], model.idx,
                                           model.channel_frac[channel], model.m)
        indices[start:start+len(i)], weights[start:start+len(i)] = i, w
    return indices, weights


@njit(cache=True, parallel=True)
def accumulate(indices, weights, nodes):
    acc = np.empty(len(indices), np.int32)
    for p in prange(len(indices)):
        value = 0
        for v in range(4):
            value += np.int64(weights[p, v])*np.int64(nodes[indices[p, v]])
        acc[p] = value
    return acc


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, squared, target, mass, caps, blocks, colours,
          colour, block_count, rho, parts):
    """先合并同块全部顶点权重，再计算一次真实RGB8变化，不能相加单节点收益。"""
    changes = np.zeros((parts, 2, block_count), np.float64)
    forbidden = np.zeros((parts, 2, block_count), np.int64)
    geometry_errors = np.zeros(parts, np.int64)
    for part in prange(parts):
        for p in range(len(indices)*part//parts, len(indices)*(part+1)//parts):
            block, combined = -1, 0
            for v in range(4):
                node, weight = indices[p, v], weights[p, v]
                if weight and colours[node] == colour:
                    if block >= 0 and blocks[node] != block:
                        geometry_errors[part] += 1
                    block = blocks[node]
                    combined += weight
            if block < 0:
                continue
            before = ((np.int64(acc[p])+io.ONE//2) >> io.Q)-np.int64(target[p])
            for direction in range(2):
                sign = 1 if direction == 0 else -1
                after = ((np.int64(acc[p])+sign*combined+io.ONE//2) >> io.Q)-np.int64(target[p])
                d2 = np.int64(squared[p])+after*after-before*before
                # 越界节点方向由调用者整体禁止；rho表在这里仍须安全索引。
                if d2 < 0 or d2 >= len(rho):
                    forbidden[part, direction, block] += 1
                else:
                    forbidden[part, direction, block] += int(d2 > caps[p])
                    changes[part, direction, block] += mass[p]*(rho[d2]-rho[squared[p]])
    return changes.sum(axis=0), forbidden.sum(axis=0), geometry_errors.sum()


def select(changes, forbidden, nodes, blocks, colours, colour, block_count):
    """整块所有节点均须合法；没有负收益的块保持原字节。"""
    valid = np.ones((2, block_count), np.bool_)
    np.logical_and.at(valid[0], blocks, nodes < 255)
    np.logical_and.at(valid[1], blocks, nodes > 0)
    choices = np.where(valid & (forbidden == 0), changes, np.inf)
    move = np.where((choices[0] < -1e-12) & (choices[0] <= choices[1]), 1,
                    np.where(choices[1] < -1e-12, -1, 0)).astype(np.int32)
    block_colours = np.zeros(block_count, np.uint8)
    block_colours[blocks] = colours
    move[block_colours != colour] = 0
    active = np.flatnonzero(move)
    predicted = float(sum(changes[int(move[b] < 0), b] for b in active))
    return move, predicted, len(active)


@njit(cache=True, parallel=True)
def apply(indices, weights, acc, squared, target, move, blocks):
    for p in prange(len(indices)):
        delta = 0
        for v in range(4):
            delta += np.int64(weights[p, v])*np.int64(move[blocks[indices[p, v]]])
        if delta:
            before = ((np.int64(acc[p])+io.ONE//2) >> io.Q)-np.int64(target[p])
            acc[p] += delta
            after = ((np.int64(acc[p])+io.ONE//2) >> io.Q)-np.int64(target[p])
            squared[p] += after*after-before*before


def propose(model, points, targets, mass, *, caps, parts=4, progress=None):
    """固定000分块，R/G/B各8块色一次；保持原坐标、节点数、运行时与标签。"""
    cc.validate(model)
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3
            or targets.dtype != np.uint8 or targets.shape != points.shape or not len(points)
            or mass.shape != (len(points),) or np.any(~np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(mass.sum())-1.) > 1e-10 or parts != 4
            or np.asarray(caps).dtype.kind not in 'iu' or np.shape(caps) != (len(points),)
            or np.any(caps < 0) or np.any(caps > 3*255**2)):
        raise ValueError('块精化需要匹配RGB8、质量1、逐色整数cap与4分片')
    started = time.perf_counter()
    nodes = model.nodes.reshape(-1, 3).copy()
    output = cc.predict(model, points)
    difference = output.astype(np.int32)-targets.astype(np.int32)
    squared = np.sum(difference*difference, axis=1, dtype=np.int32)
    del difference
    if np.any(squared > caps): raise ValueError('起点已有逐色cap违规')
    roots = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = roots+.02*np.maximum(roots-6., 0.)**2
    before = current = float(mass@rho[squared])
    blocks, colours, block_count = layout(model.m)
    report = {'before_weighted_objective': before, 'groups': [], 'parts': parts,
              'offset': [0, 0, 0], 'scope': '2³节点块同通道同号±1；非任意多节点或全局最优'}
    for channel in range(3):
        indices, weights = design(model, points, channel)
        acc = accumulate(indices, weights, nodes[:, channel])
        if not np.array_equal(((acc+io.ONE//2) >> io.Q).astype(np.uint8), output[:, channel]):
            raise AssertionError('本通道设计与当前输出不同')
        for colour in range(8):
            change, forbidden, invalid = gains(indices, weights, acc, squared, targets[:, channel],
                mass, caps, blocks, colours, colour, block_count, rho, parts)
            if invalid: raise AssertionError('同色不同块共享正支撑')
            move, predicted, count = select(change, forbidden, nodes[:, channel], blocks, colours, colour, block_count)
            apply(indices, weights, acc, squared, targets[:, channel], move, blocks)
            values = nodes[:, channel].astype(np.int32)+move[blocks]
            if np.any(values < 0) or np.any(values > 255): raise AssertionError('块移动节点越界')
            nodes[:, channel] = values.astype(np.uint8)
            measured = float(mass@rho[squared])
            if abs(measured-current-predicted) > 1e-10 or measured > current+1e-11 or np.any(squared > caps):
                raise AssertionError('块收益/硬cap不符')
            entry = {'channel': channel, 'colour': colour, 'changed_blocks': count,
                     'changed_node_values': int(np.count_nonzero(move[blocks])),
                     'predicted_change': predicted, 'weighted_objective': measured,
                     'elapsed_seconds': time.perf_counter()-started}
            report['groups'].append(entry)
            if progress: progress(entry)
            current = measured
        output[:, channel] = ((acc+io.ONE//2) >> io.Q).astype(np.uint8)
        if not np.array_equal(acc, accumulate(indices, weights, nodes[:, channel])):
            raise AssertionError('本通道累加缓存与重新计算不同')
        del indices, weights, acc
    candidate = cc.ChannelLut(model.grid.copy(), nodes.reshape(model.nodes.shape),
                              model.idx.copy(), model.channel_frac.copy())
    fresh = cc.predict(candidate, points)
    error = fresh.astype(np.int32)-targets.astype(np.int32)
    d2 = np.sum(error*error, axis=1, dtype=np.int32)
    if not np.array_equal(fresh, output) or not np.array_equal(d2, squared) or np.any(d2 > caps):
        raise AssertionError('整扫fresh前向/平方误差/逐色cap不符')
    cc.validate(candidate)
    report.update(after_weighted_objective=current, changed_node_values=int(np.count_nonzero(nodes != model.nodes.reshape(-1, 3))),
                  training_cap_violations=0, cache_recompute_mismatches=0, seconds=time.perf_counter()-started)
    return candidate, report
