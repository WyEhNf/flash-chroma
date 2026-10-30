"""固定Q16设计上的相邻节点成对±1提议，仅优化本级原表标签。"""
from __future__ import annotations

import hashlib
import time
import numpy as np
from numba import njit, prange

from . import io, rounded_grid


def layout(m, offset):
    """两种预定2³节点块；同色块相隔四个节点，单元正支撑不相交。"""
    if offset not in (0, 1):
        raise ValueError('只支持预定的000/111块偏移')
    xyz = np.indices((m, m, m), dtype=np.int32).reshape(3, -1).T
    block_xyz = (xyz+offset)//2
    side = (m+offset+1)//2
    blocks = ((block_xyz[:, 0]*side+block_xyz[:, 1])*side+block_xyz[:, 2]).astype(np.int32)
    colours = ((block_xyz[:, 0] % 2)*4+(block_xyz[:, 1] % 2)*2+block_xyz[:, 2] % 2).astype(np.uint8)
    upper = np.full((m**3, 7), -1, np.int32)
    for bits in range(1, 8):
        delta = np.array((bits >> 2, (bits >> 1) & 1, bits & 1), np.int32)
        other = xyz+delta
        valid = np.all(other < m, axis=1) & np.all((other+offset)//2 == block_xyz, axis=1)
        upper[valid, bits-1] = (other[valid, 0]*m+other[valid, 1])*m+other[valid, 2]
    return blocks, colours, upper.ravel(), side**3


@njit(cache=True, parallel=True)
def _partials(indices, weights, acc, squared, targets, mass, nodes, blocks, colours,
              upper, colour, channel, rho, caps, parts, m):
    """单端全支撑之和，加共享像素的成对修正；违规次数必须有符号。"""
    size = len(nodes)
    node_gain = np.zeros((parts, 2, size), np.float64)
    node_count = np.zeros((parts, 2, size), np.int64)
    correction_gain = np.zeros((parts, 4, len(upper)), np.float64)
    correction_count = np.zeros((parts, 4, len(upper)), np.int64)
    invalid_geometry = np.zeros(parts, np.int64)
    for part in prange(parts):
        for p in range(len(indices)*part//parts, len(indices)*(part+1)//parts):
            old_error = ((acc[p, channel]+io.ONE//2) >> io.Q)-int(targets[p, channel])
            old_squared = squared[p]
            for v in range(4):
                a, wa = int(indices[p, v]), int(weights[p, v])
                if wa == 0 or colours[a] != colour:
                    continue
                for sign in range(2):
                    da = 1 if sign == 0 else -1
                    if not 0 <= np.int64(nodes[a, channel])+da <= 255:
                        continue
                    ea = ((acc[p, channel]+da*wa+io.ONE//2) >> io.Q)-int(targets[p, channel])
                    sa = old_squared+ea*ea-old_error*old_error
                    node_gain[part, sign, a] += mass[p]*(rho[sa]-rho[old_squared])
                    node_count[part, sign, a] += int(sa > caps[p])
                for w in range(v+1, 4):
                    b, wb = int(indices[p, w]), int(weights[p, w])
                    if wb == 0 or colours[b] != colour or blocks[a] != blocks[b]:
                        continue
                    # 正权重四面体顶点可比，但不依赖权重构造函数的数组顺序。
                    lo, hi = min(a, b), max(a, b)
                    dr = hi//(m*m)-lo//(m*m)
                    dg = (hi//m) % m-(lo//m) % m
                    db = hi % m-lo % m
                    if not (0 <= dr <= 1 and 0 <= dg <= 1 and 0 <= db <= 1 and dr+dg+db > 0):
                        invalid_geometry[part] += 1
                        continue
                    edge = lo*7+dr*4+dg*2+db-1
                    if upper[edge] != hi:
                        invalid_geometry[part] += 1
                        continue
                    wl, wh = (wa, wb) if a == lo else (wb, wa)
                    for direction in range(4):
                        dl = 1 if direction < 2 else -1
                        dh = 1 if direction % 2 == 0 else -1
                        if not (0 <= np.int64(nodes[lo, channel])+dl <= 255
                                and 0 <= np.int64(nodes[hi, channel])+dh <= 255):
                            continue
                        el = ((acc[p, channel]+dl*wl+io.ONE//2) >> io.Q)-int(targets[p, channel])
                        eh = ((acc[p, channel]+dh*wh+io.ONE//2) >> io.Q)-int(targets[p, channel])
                        ej = ((acc[p, channel]+dl*wl+dh*wh+io.ONE//2) >> io.Q)-int(targets[p, channel])
                        sl = old_squared+el*el-old_error*old_error
                        sh = old_squared+eh*eh-old_error*old_error
                        sj = old_squared+ej*ej-old_error*old_error
                        correction_gain[part, direction, edge] += mass[p]*(rho[sj]-rho[sl]-rho[sh]+rho[old_squared])
                        correction_count[part, direction, edge] += int(sj > caps[p])-int(sl > caps[p])-int(sh > caps[p])
    return node_gain, node_count, correction_gain, correction_count, invalid_geometry


@njit(cache=True, parallel=True)
def _finish(node_gain, node_count, correction_gain, correction_count, upper, colours, colour, nodes, channel):
    gains = np.full((4, len(upper)), np.inf, np.float64)
    counts = np.zeros((4, len(upper)), np.int64)
    for edge in prange(len(upper)):
        a, b = edge//7, int(upper[edge])
        if b < 0 or colours[a] != colour:
            continue
        for direction in range(4):
            da = 0 if direction < 2 else 1
            db = 0 if direction % 2 == 0 else 1
            if not (0 <= np.int64(nodes[a, channel])+(1 if da == 0 else -1) <= 255
                    and 0 <= np.int64(nodes[b, channel])+(1 if db == 0 else -1) <= 255):
                continue
            gain, count = 0., 0
            for part in range(len(node_gain)):
                gain += (node_gain[part, da, a]+node_gain[part, db, b]
                         +correction_gain[part, direction, edge])
                count += (node_count[part, da, a]+node_count[part, db, b]
                          +correction_count[part, direction, edge])
            gains[direction, edge], counts[direction, edge] = gain, count
    return gains, counts


def gains(indices, weights, acc, squared, targets, mass, nodes, geometry,
          colour, channel, rho, caps, parts=4):
    """返回真实组合损失变化及组合违规次数，不OR单端禁止位。"""
    blocks, colours, upper, _ = geometry
    m = round(len(nodes)**(1/3))
    arrays = _partials(indices, weights, acc, squared, targets, mass, nodes, blocks, colours,
                       upper, colour, channel, rho, caps, parts, m)
    if np.any(arrays[-1]):
        raise AssertionError('四面体正支撑端点不是当前块内相邻可比顶点')
    gain, counts = _finish(*arrays[:-1], upper, colours, colour, nodes, channel)
    if np.any(counts < 0):
        raise AssertionError('成对违规计数修正后不能为负')
    return gain, counts


@njit(cache=True)
def select(gain, counts, geometry_blocks, upper, block_count):
    """每个块只选一对，确定性按edge_id/方向打破相等收益。"""
    best = np.zeros(block_count, np.float64)
    edge_for = np.full(block_count, -1, np.int32)
    direction_for = np.zeros(block_count, np.int32)
    for edge in range(len(upper)):
        if upper[edge] < 0:
            continue
        block = geometry_blocks[edge//7]
        for direction in range(4):
            value = gain[direction, edge]
            if counts[direction, edge] == 0 and value < -1e-12 and value < best[block]:
                best[block], edge_for[block], direction_for[block] = value, edge, direction
    move = np.zeros(len(geometry_blocks), np.int32)
    predicted, pairs = 0., 0
    for block in range(block_count):
        edge = edge_for[block]
        if edge < 0:
            continue
        direction = direction_for[block]
        move[edge//7] = 1 if direction < 2 else -1
        move[upper[edge]] = 1 if direction % 2 == 0 else -1
        predicted += best[block]
        pairs += 1
    return move, predicted, pairs


@njit(cache=True, parallel=True)
def apply_moves(indices, weights, acc, squared, targets, channel, move):
    """一次累加四顶点所有改动，再更新真实舍入误差；不能遇单节点即break。"""
    for p in prange(len(indices)):
        change = 0
        for v in range(4):
            change += int(weights[p, v])*int(move[indices[p, v]])
        if change:
            before = ((acc[p, channel]+io.ONE//2) >> io.Q)-int(targets[p, channel])
            acc[p, channel] += change
            after = ((acc[p, channel]+io.ONE//2) >> io.Q)-int(targets[p, channel])
            squared[p] += after*after-before*before


def propose(model, points, targets, mass, *, caps, sweeps=1, parts=4,
            tail_at=6., tail_weight=.02, progress=None):
    """仅两种预定分块的一轮三通道配对提议，固定轴与独立本级RGB8标签。"""
    io.validate_sparse(model, competition=True)
    points, targets, mass = np.asarray(points), np.asarray(targets), np.asarray(mass)
    raw_caps = np.asarray(caps)
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3 or not len(points)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or mass.shape != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(mass.sum())-1.) > 1e-10
            or not isinstance(sweeps, int) or isinstance(sweeps, bool) or sweeps != 1
            or not isinstance(parts, int) or isinstance(parts, bool) or not 1 <= parts <= 32
            or raw_caps.dtype.kind not in 'iu' or raw_caps.shape not in ((), (len(points),))
            or np.any(raw_caps < 0) or np.any(raw_caps > 3*255**2)
            or not np.isfinite(tail_at) or tail_at <= 0 or not np.isfinite(tail_weight) or tail_weight < 0):
        raise ValueError('需要合法RGB8/质量1/逐点整数cap；本阶段固定一次配对扫')
    caps = np.full(len(points), int(raw_caps), np.int32) if raw_caps.ndim == 0 else np.ascontiguousarray(raw_caps, dtype=np.int32)
    mass = np.ascontiguousarray(mass, dtype=np.float64)
    started = time.perf_counter()
    indices, weights, acc, squared, _ = rounded_grid.prepare(model, points, targets)
    if np.any(squared > caps):
        raise ValueError('起点已经违反逐点cap，不能用重叠修正掩盖原有违规')
    nodes = model.nodes.reshape(-1, 3).copy()
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+tail_weight*np.maximum(root-tail_at, 0.)**2
    before = float(mass@rho[squared])
    report = {'training_rows': len(points), 'before_weighted_objective': before,
        'offsets': [[0, 0, 0], [1, 1, 1]], 'parts': parts, 'requested_sweeps': sweeps,
        'objective': '本级原表真实RGB距离+固定tail二次惩罚；所有行含零质量行均受各自cap限制',
        'cap_sha256': hashlib.sha256(caps.astype('<i4', copy=False).tobytes()).hexdigest(),
        'design_cache_bytes': indices.nbytes+weights.nbytes,
        'pair_working_buffer_bytes_upper_bound': parts*(2*len(nodes)+4*len(nodes)*7)*16+4*len(nodes)*7*16,
        'groups': []}
    predicted_total, pair_total = 0., 0
    for offset in (0, 1):
        geometry = layout(model.m, offset)
        blocks, _, upper, block_count = geometry
        for colour in range(8):
            for channel in range(3):
                gain, counts = gains(indices, weights, acc, squared, targets, mass, nodes, geometry,
                                      colour, channel, rho, caps, parts)
                move, predicted, pairs = select(gain, counts, blocks, upper, block_count)
                apply_moves(indices, weights, acc, squared, targets, channel, move)
                values = nodes[:, channel].astype(np.int32)+move
                if np.any(values < 0) or np.any(values > 255):
                    raise AssertionError('配对提议超出RGB8节点边界')
                nodes[:, channel] = values.astype(np.uint8)
                predicted_total += predicted
                pair_total += pairs
                entry = {'offset': offset, 'colour': colour, 'channel': channel,
                         'selected_pairs': pairs, 'predicted_objective_change': predicted}
                report['groups'].append(entry)
                if progress:
                    progress(entry)
    checked_acc, checked_squared = rounded_grid._accumulate(indices, weights, nodes, targets)
    if not np.array_equal(acc, checked_acc) or not np.array_equal(squared, checked_squared):
        raise AssertionError('整扫独立重算不同于配对增量缓存')
    if np.any(checked_squared > caps):
        raise AssertionError('成对选择后违反逐点硬cap')
    after = float(mass@rho[checked_squared])
    delta_error = abs((after-before)-predicted_total)
    if delta_error > 1e-10*max(1., abs(before), abs(after), abs(predicted_total)):
        raise AssertionError('整扫真实目标变化与组合预测收益不一致')
    accepted = after < before-1e-11
    idx, frac = model.tables()
    candidate = io.SparseLut(model.grid.copy(), nodes.reshape(model.nodes.shape).copy() if accepted else model.nodes.copy(),
                             idx.copy(), frac.copy())
    io.validate_sparse(candidate, competition=True)
    report.update(after_weighted_objective=after if accepted else before, accepted_sweeps=int(accepted),
        selected_pairs=pair_total, predicted_objective_change=predicted_total, objective_delta_error=delta_error,
        cache_recompute_mismatches=0, cap_violations=0, seconds=time.perf_counter()-started,
        stop='fixed_single_sweep' if accepted else 'no_significant_objective_improvement',
        scope='两种固定2³分块的相邻可比节点±1；不覆盖所有对角边、不称全局最优；浮点归约非无理数严格证书；需另行精度选型和终验')
    return [(1 if accepted else 0, candidate)], report
