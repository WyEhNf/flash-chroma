"""固定分输出通道几何，以一次24块真实RGB8坐标下降精化共享节点。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit, prange
from . import channel_coordinates as cc, interp, io


@njit(cache=True, parallel=True)
def accumulate(indices, weights, nodes, channel):
    """每通道凸四面体的Q16累加界为255*65536，int32足够。"""
    acc = np.empty(len(indices), np.int32)
    for p in prange(len(indices)):
        value = 0
        for v in range(4):
            value += int(weights[p, v])*int(nodes[indices[p, v], channel])
        acc[p] = value
    return acc


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, output, squared, targets, mass, caps,
          nodes, colours, colour, channel, rho, parts):
    """各分片私有归约；即使质量为零仍逐色核cap，同色正支撑至多一个。"""
    size = len(nodes)
    costs = np.zeros((parts, 2, size), np.float64)
    bad = np.zeros((parts, 2, size), np.int64)
    for part in prange(parts):
        for p in range(len(indices)*part//parts, len(indices)*(part+1)//parts):
            for v in range(4):
                node, weight = indices[p, v], weights[p, v]
                if weight == 0 or colours[node] != colour:
                    continue
                before = int(output[p, channel])-int(targets[p, channel])
                for direction in range(2):
                    delta = 1 if direction == 0 else -1
                    if not 0 <= int(nodes[node, channel])+delta <= 255:
                        continue
                    after = ((acc[p]+delta*weight+io.ONE//2) >> io.Q)-int(targets[p, channel])
                    d2 = squared[p]+after*after-before*before
                    costs[part, direction, node] += mass[p]*(rho[d2]-rho[squared[p]])
                    bad[part, direction, node] += int(d2 > caps[p])
                break
    return costs.sum(axis=0), bad.sum(axis=0)


@njit(cache=True, parallel=True)
def apply(indices, weights, acc, output, squared, targets, colours, colour, channel, move):
    """只更新当前输出；另两通道及其误差已经包含在当前d2中。"""
    for p in prange(len(indices)):
        for v in range(4):
            node, weight = indices[p, v], weights[p, v]
            if weight == 0 or colours[node] != colour:
                continue
            delta = move[node]
            if delta:
                before = int(output[p, channel])-int(targets[p, channel])
                acc[p] += delta*weight
                value = (acc[p]+io.ONE//2) >> io.Q
                after = value-int(targets[p, channel])
                squared[p] += after*after-before*before
                output[p, channel] = value
            break


def design(model, points, channel):
    """每次只缓存一个输出通道设计，三通道不能共用I/W。"""
    indices = np.empty((len(points), 4), np.int32)
    weights = np.empty_like(indices)
    for start in range(0, len(points), 1 << 18):
        i, w = interp.tetra_index_weights_q(points[start:start+(1 << 18)], model.idx,
            model.channel_frac[channel], model.m)
        indices[start:start+len(i)], weights[start:start+len(i)] = i, w
    return indices, weights


def parity(m):
    x, y, z = np.meshgrid(*(np.arange(m),)*3, indexing='ij')
    return ((x % 2)*4+(y % 2)*2+z % 2).ravel().astype(np.uint8)


def choose(costs, bad, nodes, colours, colour, channel):
    """节点边界全局禁止，不依赖该节点是否有训练支撑。"""
    costs = costs.copy()
    costs[bad > 0] = np.inf
    costs[0, nodes[:, channel] == 255] = np.inf
    costs[1, nodes[:, channel] == 0] = np.inf
    move = np.where((costs[0] < -1e-12) & (costs[0] <= costs[1]), 1,
        np.where(costs[1] < -1e-12, -1, 0)).astype(np.int32)
    move[colours != colour] = 0
    selected = np.flatnonzero(move)
    predicted = float(np.sum(costs[(move[selected] < 0).astype(np.intp), selected]))
    return move, predicted


def propose(model, points, targets, mass, *, caps, parts=4, tail_at=6., tail_weight=.02, progress=None):
    """只做R/G/B各8色一次；保持权威坐标与每级原表语义。"""
    cc.validate(model)
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3 or not len(points)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(np.sum(mass))-1.) > 1e-10 or parts != 4
            or np.shape(caps) != (len(points),) or np.asarray(caps).dtype.kind not in 'iu'
            or np.any(caps < 0) or np.any(caps > 3*255**2) or tail_at != 6. or tail_weight != .02):
        raise ValueError('此阶段仅接受RGB8/质量1/逐色cap/4分片及冻结rho')
    started = time.perf_counter()
    nodes = model.nodes.reshape(-1, 3).copy()
    output = cc.predict(model, points)
    difference = output.astype(np.int32)-targets.astype(np.int32)
    squared = np.sum(difference*difference, axis=1, dtype=np.int32)
    del difference
    if np.any(squared > caps): raise ValueError('冻结起点已经违反旧2dd cap')
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    current = float(mass@rho[squared])
    colours = parity(model.m)
    report = {'before_weighted_objective': current, 'blocks': [], 'parts': parts,
        'order': 'R/G/B各8种节点坐标parity，恰好24块各一次', 'training_rows': len(points),
        'single_channel_design_bytes': len(points)*4*8,
        'scope': '固定分通道坐标的RGB8节点有限±1邻域；非全局最优/完整精度或原生验收'}
    for channel in range(3):
        indices, weights = design(model, points, channel)
        acc = accumulate(indices, weights, nodes, channel)
        if not np.array_equal((acc+io.ONE//2) >> io.Q, output[:, channel]):
            raise AssertionError('当前通道设计与已有输出缓存不符')
        for colour in range(8):
            costs, bad = gains(indices, weights, acc, output, squared, targets, mass, caps,
                nodes, colours, colour, channel, rho, parts)
            move, delta = choose(costs, bad, nodes, colours, colour, channel)
            apply(indices, weights, acc, output, squared, targets, colours, colour, channel, move)
            nodes[:, channel] = (nodes[:, channel].astype(np.int32)+move).astype(np.uint8)
            measured = float(mass@rho[squared])
            violations = int(np.count_nonzero(squared > caps))
            if (violations or abs(measured-current-delta) > 1e-8 or measured > current+1e-10
                    or not np.array_equal((acc+io.ONE//2) >> io.Q, output[:, channel])):
                raise AssertionError('节点批量应用的预测收益/cap/累加器不符')
            entry = {'channel': channel, 'colour': colour, 'changed_nodes': int(np.count_nonzero(move)),
                'before_weighted_objective': current, 'after_weighted_objective': measured,
                'predicted_change': delta, 'measured_change': measured-current,
                'prediction_error': abs(measured-current-delta), 'cap_violations': violations,
                'seconds': time.perf_counter()-started}
            report['blocks'].append(entry)
            current = measured
            if progress: progress(entry)
        del indices, weights, acc
    candidate = cc.ChannelLut(model.grid.copy(), nodes.reshape(model.nodes.shape), model.idx.copy(), model.channel_frac.copy())
    cc.validate(candidate)
    checked = cc.predict(candidate, points)
    e = checked.astype(np.int32)-targets.astype(np.int32)
    checked_squared = np.sum(e*e, axis=1, dtype=np.int32)
    if (not np.array_equal(checked, output) or not np.array_equal(checked_squared, squared)
            or np.any(checked_squared > caps) or abs(float(mass@rho[checked_squared])-current) > 1e-8):
        raise AssertionError('24块结束后的fresh整RGB前向与缓存不符')
    report.update(after_weighted_objective=current,
        changed_node_components=int(np.count_nonzero(candidate.nodes != model.nodes)),
        maximum_node_shift=int(np.max(np.abs(candidate.nodes.astype(np.int32)-model.nodes.astype(np.int32)))),
        cache_recompute_mismatches=0, training_cap_violations=0, seconds=time.perf_counter()-started)
    return candidate, report
