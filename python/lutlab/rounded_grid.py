"""在固定权威轴表上，按真实RGB8距离做有界加权8色精化。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit, prange

from . import interp, io


@njit(cache=True, parallel=True)
def _gains(indices, weights, acc, squared, targets, mass, nodes, colours, colour, channel, rho, cap, parts):
    """同色正支撑互斥；每个分片只写自己的节点收益与禁止位。"""
    size = len(nodes)
    gains = np.zeros((parts, 2, size), np.float64)
    forbidden = np.zeros((parts, 2, size), np.uint8)
    for part in prange(parts):
        for p in range(len(indices) * part // parts, len(indices) * (part + 1) // parts):
            for vertex in range(4):
                node = indices[p, vertex]
                weight = weights[p, vertex]
                if weight == 0 or colours[node] != colour:
                    continue
                old_error = ((acc[p, channel] + io.ONE // 2) >> io.Q) - int(targets[p, channel])
                old_squared = squared[p]
                for direction in range(2):
                    delta = 1 if direction == 0 else -1
                    value = int(nodes[node, channel]) + delta
                    if not 0 <= value <= 255:
                        forbidden[part, direction, node] = 1
                        continue
                    error = ((acc[p, channel] + delta * weight + io.ONE // 2) >> io.Q) - int(targets[p, channel])
                    next_squared = old_squared + error * error - old_error * old_error
                    if next_squared > cap:
                        forbidden[part, direction, node] = 1
                    gains[part, direction, node] += mass[p] * (rho[next_squared] - rho[old_squared])
                break
    return gains.sum(axis=0), forbidden.sum(axis=0)


@njit(cache=True, parallel=True)
def _apply(indices, weights, acc, squared, targets, colours, colour, channel, move):
    """输出通道依次更新；累加器完全用int32，绝不输出裁剪掩盖越界。"""
    for p in prange(len(indices)):
        for vertex in range(4):
            node = indices[p, vertex]
            weight = weights[p, vertex]
            if weight == 0 or colours[node] != colour:
                continue
            delta = move[node]
            if delta:
                before = ((acc[p, channel] + io.ONE // 2) >> io.Q) - int(targets[p, channel])
                acc[p, channel] += delta * weight
                after = ((acc[p, channel] + io.ONE // 2) >> io.Q) - int(targets[p, channel])
                squared[p] += after * after - before * before
            break


@njit(cache=True, parallel=True)
def _accumulate(indices, weights, nodes, targets):
    acc = np.empty((len(indices), 3), np.int32)
    squared = np.zeros(len(indices), np.int32)
    for p in prange(len(indices)):
        for channel in range(3):
            value = 0
            for vertex in range(4):
                value += int(weights[p, vertex]) * int(nodes[indices[p, vertex], channel])
            acc[p, channel] = value
            error = ((value + io.ONE // 2) >> io.Q) - int(targets[p, channel])
            squared[p] += error * error
    return acc, squared


def prepare(model, points, targets):
    """离线缓存固定设计；构造临时数组分块，固定I/W约8*N*4字节。"""
    indices, weights = np.empty((len(points), 4), np.int32), np.empty((len(points), 4), np.int32)
    for start in range(0, len(points), 1 << 18):
        i, w = interp.tetra_index_weights_q(points[start:start+(1 << 18)], *model.tables(), model.m)
        indices[start:start+len(i)], weights[start:start+len(i)] = i, w
    nodes = model.nodes.reshape(-1, 3).copy()
    acc, squared = _accumulate(indices, weights, nodes, targets)
    x, y, z = np.meshgrid(*(np.arange(model.m),) * 3, indexing='ij')
    colours = ((x % 2) * 4 + (y % 2) * 2 + z % 2).ravel().astype(np.uint8)
    return indices, weights, acc, squared, colours


def propose(model, points, targets, mass, *, sweeps=4, tail_at=6., tail_weight=.02,
            maximum_squared=3*255**2, parts=4, progress=None, envelope=None, extra_objective=None):
    """复用8色坐标下降，采用真实舍入目标；固定有限扫数后统一选型。"""
    io.validate_sparse(model, competition=True)
    if (np.asarray(points).dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3
            or np.asarray(targets).dtype != np.uint8 or targets.shape != points.shape or not len(points)
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(np.sum(mass)) - 1.) > 1e-10 or not 1 <= sweeps <= 16
            or not 1 <= parts <= 32 or not 0 <= maximum_squared <= 3*255**2
            or not np.isfinite(tail_at) or tail_at <= 0 or not np.isfinite(tail_weight) or tail_weight < 0):
        raise ValueError('整数精化需要合法RGB8、总质量1和有限预算/颜色上限')
    started = time.perf_counter()
    indices, weights, acc, squared, colours = prepare(model, points, targets)
    if envelope is not None:
        envelope.validate(points, acc)
    if extra_objective is not None:
        extra_objective.validate(targets)
    nodes = model.nodes.reshape(-1, 3).copy()
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root + tail_weight * np.maximum(root - tail_at, 0.)**2
    mass = np.ascontiguousarray(mass, dtype=np.float64)
    loss = float(mass @ rho[squared])
    if extra_objective is not None:
        loss += extra_objective.loss(acc, mass, rho)
    if int(squared.max()) > maximum_squared:
        raise ValueError('起点已经违反冻结完整域max上限')
    report = {'before_weighted_objective': loss, 'maximum_squared': maximum_squared, 'sweeps': [],
        'training_rows': len(points), 'design_cache_bytes': indices.nbytes + weights.nbytes,
        'objective': '真实Q16半向上RGB8距离+固定阈值以上二次惩罚；float64质量归约，不称无理数严格证书'}
    if envelope is not None:
        report['chain_envelope'] = envelope.metadata
    if extra_objective is not None:
        report['suffix_objective'] = extra_objective.metadata
    checkpoints = []
    stop = 'sweep_limit'
    for sweep in range(1, sweeps + 1):
        old = nodes.copy()
        changed = 0
        for colour in range(8):
            for channel in range(3):
                gain, forbidden = _gains(indices, weights, acc, squared, targets, mass, nodes,
                    colours, colour, channel, rho, maximum_squared, parts)
                if envelope is not None:
                    forbidden += envelope.forbidden(indices, weights, acc, colours, colour, channel, parts)
                if extra_objective is not None:
                    gain += extra_objective.gains(indices, weights, acc, mass, colours, colour, channel, rho, parts)
                gain[forbidden > 0] = np.inf
                gain[0, nodes[:, channel] == 255] = np.inf
                gain[1, nodes[:, channel] == 0] = np.inf
                move = np.where((gain[0] < -1e-12) & (gain[0] <= gain[1]), 1,
                    np.where(gain[1] < -1e-12, -1, 0)).astype(np.int32)
                move[colours != colour] = 0
                changed += int(np.count_nonzero(move))
                _apply(indices, weights, acc, squared, targets, colours, colour, channel, move)
                nodes[:, channel] = (nodes[:, channel].astype(np.int32) + move).astype(np.uint8)
        after = float(mass @ rho[squared])
        if extra_objective is not None:
            after += extra_objective.loss(acc, mass, rho)
        if envelope is not None:
            envelope.validate(points, acc)
        accepted = after < loss - 1e-11 and int(squared.max()) <= maximum_squared
        entry = {'sweep': sweep, 'changed_coordinates': changed, 'before_weighted_objective': loss,
                 'after_weighted_objective': after, 'accepted': bool(accepted), 'seconds': time.perf_counter()-started}
        report['sweeps'].append(entry)
        if progress:
            progress(entry)
        if not accepted:
            nodes = old
            stop = 'coordinate_stall' if changed == 0 else 'weighted_loss_or_cap_rollback'
            break
        loss = after
        idx, frac = model.tables()
        checkpoints.append((sweep, io.SparseLut(model.grid.copy(), nodes.reshape(model.nodes.shape).copy(), idx.copy(), frac.copy())))
    report.update(after_weighted_objective=loss, stop=stop, seconds=time.perf_counter()-started,
        accepted_sweeps=len(checkpoints), scope='固定轴有限±1邻域的加权提议，非RGB8全局最优；需独立选型与终验')
    if not checkpoints:
        idx, frac = model.tables()
        checkpoints.append((0, io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), frac.copy())))
    return checkpoints, report
