"""固定权威Q16表，一次8色节点RGB三通道联合整数邻域提议。"""
from __future__ import annotations

import hashlib
import itertools
import time
import numpy as np
from numba import njit, prange
from . import io, rounded_grid


DIRECTIONS = np.array([v for v in itertools.product((-1, 0, 1), repeat=3) if any(v)], np.int32)


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, squared, targets, mass, nodes, colours, colour, rho, caps, parts):
    """同色节点正支撑不交；一次评价26种RGB联合步，不组合单通道禁止位。"""
    size = len(nodes)
    change = np.zeros((parts, 26, size), np.float64)
    forbidden = np.zeros((parts, 26, size), np.int64)
    legal = np.ones((26, size), np.uint8)
    for node in prange(size):
        for direction in range(26):
            for channel in range(3):
                value = np.int64(nodes[node, channel])+DIRECTIONS[direction, channel]
                if value < 0 or value > 255:
                    legal[direction, node] = 0
    for part in prange(parts):
        component = np.empty((3, 3), np.int32)
        for p in range(len(indices)*part//parts, len(indices)*(part+1)//parts):
            for vertex in range(4):
                node, weight = int(indices[p, vertex]), int(weights[p, vertex])
                if weight == 0 or colours[node] != colour:
                    continue
                for channel in range(3):
                    for step in range(3):
                        error = ((acc[p, channel]+(step-1)*weight+io.ONE//2) >> io.Q)-int(targets[p, channel])
                        component[channel, step] = error*error
                for direction in range(26):
                    if not legal[direction, node]:
                        continue
                    d = DIRECTIONS[direction]
                    next_squared = component[0, d[0]+1]+component[1, d[1]+1]+component[2, d[2]+1]
                    forbidden[part, direction, node] += int(next_squared > caps[p])
                    change[part, direction, node] += mass[p]*(rho[next_squared]-rho[squared[p]])
                break
    result, count = change.sum(axis=0), forbidden.sum(axis=0)
    for node in prange(size):
        for direction in range(26):
            if not legal[direction, node]:
                result[direction, node] = np.inf
                count[direction, node] += 1
    return result, count


@njit(cache=True)
def select(change, forbidden, colours, colour):
    """每个节点至多一个联合步；固定方向次序破同值，空支撑节点不移动。"""
    moves = np.zeros((change.shape[1], 3), np.int32)
    predicted, changed, joint = 0., 0, 0
    for node in range(change.shape[1]):
        if colours[node] != colour:
            continue
        best, chosen = -1e-12, -1
        for direction in range(26):
            if forbidden[direction, node] == 0 and change[direction, node] < best:
                best, chosen = change[direction, node], direction
        if chosen >= 0:
            moves[node] = DIRECTIONS[chosen]
            predicted += best
            changed += 1
            joint += int(np.count_nonzero(DIRECTIONS[chosen]) > 1)
    return moves, predicted, changed, joint


@njit(cache=True, parallel=True)
def apply_moves(indices, weights, acc, squared, targets, moves):
    """一次累加全部顶点和三个通道，更新实际整数输出的距离平方。"""
    for p in prange(len(indices)):
        value_squared = 0
        for channel in range(3):
            for vertex in range(4):
                acc[p, channel] += int(weights[p, vertex])*int(moves[indices[p, vertex], channel])
            error = ((acc[p, channel]+io.ONE//2) >> io.Q)-int(targets[p, channel])
            value_squared += error*error
        squared[p] = value_squared


def propose(model, points, targets, mass, *, caps, sweeps=1, parts=4,
            tail_at=6., tail_weight=.02, progress=None):
    """固定一次26方向8色扫；仅优化本级原表，逐色cap与节点RGB8均是硬约束。"""
    io.validate_sparse(model, competition=True)
    points, targets, mass, raw_caps = map(np.asarray, (points, targets, mass, caps))
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3 or not len(points)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or mass.shape != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(mass.sum())-1.) > 1e-10
            or not isinstance(sweeps, int) or isinstance(sweeps, bool) or sweeps != 1
            or not isinstance(parts, int) or isinstance(parts, bool) or not 1 <= parts <= 32
            or raw_caps.dtype.kind not in 'iu' or raw_caps.shape not in ((), (len(points),))
            or np.any(raw_caps < 0) or np.any(raw_caps > 3*255**2)
            or not np.isfinite(tail_at) or tail_at <= 0 or not np.isfinite(tail_weight) or tail_weight < 0):
        raise ValueError('联合RGB提议需要合法RGB8/质量1/逐点整数cap；预算固定一次8色扫')
    caps = np.full(len(points), int(raw_caps), np.int32) if raw_caps.ndim == 0 else np.ascontiguousarray(raw_caps, dtype=np.int32)
    mass = np.ascontiguousarray(mass, dtype=np.float64)
    started = time.perf_counter()
    indices, weights, acc, squared, colours = rounded_grid.prepare(model, points, targets)
    if np.any(squared > caps):
        raise ValueError('起点已有逐点cap违规')
    nodes = model.nodes.reshape(-1, 3).copy()
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+tail_weight*np.maximum(root-tail_at, 0.)**2
    before = float(mass@rho[squared])
    predicted_total, changed_total, joint_total = 0., 0, 0
    report = {'before_weighted_objective': before, 'training_rows': len(points), 'groups': [],
        'directions': DIRECTIONS.tolist(), 'parts': parts, 'requested_sweeps': sweeps,
        'cap_sha256': hashlib.sha256(caps.astype('<i4', copy=False).tobytes()).hexdigest(),
        'design_cache_bytes': indices.nbytes+weights.nbytes,
        'partial_buffers_bytes': parts*26*len(nodes)*16,
        'objective': '本级原表RGB8欧氏距离+固定tail惩罚；浮点质量归约不是无理数严格证书'}
    for colour in range(8):
        change, forbidden = gains(indices, weights, acc, squared, targets, mass, nodes, colours,
                                   colour, rho, caps, parts)
        moves, predicted, changed, joint = select(change, forbidden, colours, colour)
        apply_moves(indices, weights, acc, squared, targets, moves)
        values = nodes.astype(np.int32)+moves
        if np.any(values < 0) or np.any(values > 255):
            raise AssertionError('联合提议越出RGB8节点范围')
        nodes = values.astype(np.uint8)
        predicted_total += predicted
        changed_total += changed
        joint_total += joint
        entry = {'colour': colour, 'changed_nodes': changed, 'joint_channel_moves': joint,
                 'predicted_objective_change': predicted}
        report['groups'].append(entry)
        if progress:
            progress(entry)
    check_acc, check_squared = rounded_grid._accumulate(indices, weights, nodes, targets)
    if not np.array_equal(acc, check_acc) or not np.array_equal(squared, check_squared):
        raise AssertionError('联合RGB增量缓存与重算不一致')
    if np.any(check_squared > caps):
        raise AssertionError('联合RGB最终违反逐点cap')
    after = float(mass@rho[check_squared])
    delta_error = abs((after-before)-predicted_total)
    if delta_error > 1e-10*max(1., abs(before), abs(after), abs(predicted_total)):
        raise AssertionError('联合RGB真实目标与预测收益不一致')
    accepted = after < before-1e-11
    candidate = io.SparseLut(model.grid.copy(), nodes.reshape(model.nodes.shape) if accepted else model.nodes.copy(),
                             *(a.copy() for a in model.tables()))
    io.validate_sparse(candidate, competition=True)
    report.update(after_weighted_objective=after if accepted else before, accepted_sweeps=int(accepted),
        changed_nodes=changed_total, joint_channel_moves=joint_total, objective_delta_error=delta_error,
        cap_violations=0, cache_recompute_mismatches=0, seconds=time.perf_counter()-started,
        scope='仅一个节点内三通道[-1,1]^3邻域，8色一次；不覆盖多节点联合，不称全局最优')
    return [(int(accepted), candidate)], report
