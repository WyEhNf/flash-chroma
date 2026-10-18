"""共享cube、分输出几何下的一次8色26方向节点RGB联合精化。"""
from __future__ import annotations
import itertools
import time
import numpy as np
from numba import njit, prange
from . import channel_coordinates as cc, channel_global_nodes as cg, io

DIRECTIONS = np.asarray([v for v in itertools.product((-1, 0, 1), repeat=3) if any(v)], np.int32)


def parity(m):
    xyz = np.indices((m, m, m), dtype=np.int32).reshape(3, -1).T
    return ((xyz[:, 0] % 2)*4+(xyz[:, 1] % 2)*2+xyz[:, 2] % 2).astype(np.uint8)


@njit(cache=True, parallel=True)
def accumulate(indices, weights, nodes, targets):
    acc = np.empty((len(targets), 3), np.int32)
    squared = np.zeros(len(targets), np.int32)
    for p in prange(len(targets)):
        for c in range(3):
            value = 0
            for v in range(4): value += np.int64(weights[c, p, v])*np.int64(nodes[indices[c, p, v], c])
            acc[p, c] = value
            error = ((value+io.ONE//2) >> io.Q)-np.int64(targets[p, c])
            squared[p] += error*error
    return acc, squared


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, squared, targets, mass, caps, nodes, colours, colour, rho, parts):
    """每cube各parity仅一角；三路可能权重不同/为零，但正支撑节点必一致。"""
    size = len(nodes)
    changes = np.zeros((parts, 26, size), np.float64)
    forbidden = np.zeros((parts, 26, size), np.int64)
    legal = np.ones((26, size), np.uint8)
    invalid = np.zeros(parts, np.int64)
    for node in prange(size):
        for direction in range(26):
            for c in range(3):
                if not 0 <= np.int64(nodes[node, c])+DIRECTIONS[direction, c] <= 255:
                    legal[direction, node] = 0
    for part in prange(parts):
        component = np.empty((3, 3), np.int32)
        for p in range(len(targets)*part//parts, len(targets)*(part+1)//parts):
            node = -1
            for c in range(3):
                selected_weight, channel_node = 0, -1
                for v in range(4):
                    n, w = indices[c, p, v], weights[c, p, v]
                    if w > 0 and colours[n] == colour:
                        if channel_node >= 0: invalid[part] += 1
                        channel_node, selected_weight = n, w
                if channel_node >= 0:
                    if node >= 0 and node != channel_node: invalid[part] += 1
                    node = channel_node
                for step in range(3):
                    error = ((np.int64(acc[p, c])+(step-1)*selected_weight+io.ONE//2) >> io.Q)-np.int64(targets[p, c])
                    component[c, step] = error*error
            if node < 0: continue
            if component[0, 1]+component[1, 1]+component[2, 1] != squared[p]: invalid[part] += 1
            for direction in range(26):
                if not legal[direction, node]: continue
                d = DIRECTIONS[direction]
                d2 = component[0, d[0]+1]+component[1, d[1]+1]+component[2, d[2]+1]
                changes[part, direction, node] += mass[p]*(rho[d2]-rho[squared[p]])
                forbidden[part, direction, node] += int(d2 > caps[p])
    change, bad = changes.sum(axis=0), forbidden.sum(axis=0)
    for node in prange(size):
        for direction in range(26):
            if not legal[direction, node]:
                change[direction, node] = np.inf
                bad[direction, node] += 1
    return change, bad, invalid.sum()


@njit(cache=True)
def select(changes, forbidden, colours, colour):
    moves = np.zeros((changes.shape[1], 3), np.int32)
    predicted, count, joint = 0., 0, 0
    for node in range(changes.shape[1]):
        if colours[node] != colour: continue
        best, chosen = -1e-12, -1
        for direction in range(26):
            if not forbidden[direction, node] and changes[direction, node] < best:
                best, chosen = changes[direction, node], direction
        if chosen >= 0:
            moves[node] = DIRECTIONS[chosen]
            predicted += best; count += 1
            joint += int(np.count_nonzero(DIRECTIONS[chosen]) > 1)
    return moves, predicted, count, joint


@njit(cache=True, parallel=True)
def apply(indices, weights, acc, squared, targets, moves):
    for p in prange(len(targets)):
        d2 = 0
        for c in range(3):
            for v in range(4):
                acc[p, c] += np.int64(weights[c, p, v])*np.int64(moves[indices[c, p, v], c])
            error = ((np.int64(acc[p, c])+io.ONE//2) >> io.Q)-np.int64(targets[p, c])
            d2 += error*error
        squared[p] = d2


def propose(model, points, targets, mass, *, caps, parts=4, progress=None):
    """从3e5起点固定parity0..7恰好一次，不接其它失败提议。"""
    cc.validate(model)
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3 or not len(points)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(np.sum(mass))-1.) > 1e-10 or parts != 4
            or np.shape(caps) != (len(points),) or np.asarray(caps).dtype.kind not in 'iu'
            or np.any(caps < 0) or np.any(caps > 3*255**2)):
        raise ValueError('联合节点需要RGB8/质量1/逐色cap/4分片')
    started = time.perf_counter()
    indices, weights = cg.design(model, points)
    nodes = model.nodes.reshape(-1, 3).copy()
    acc, squared = accumulate(indices, weights, nodes, targets)
    if np.any(squared > caps): raise ValueError('3e5起点已经违反旧2dd cap')
    np.testing.assert_array_equal(((acc+io.ONE//2) >> io.Q).astype(np.uint8), cc.predict(model, points))
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    current = float(mass@rho[squared])
    report = {'before_weighted_objective': current, 'groups': [], 'directions': DIRECTIONS.tolist(),
        'parts': parts, 'requested_sweeps': 1, 'training_rows': len(points),
        'offline_design_bytes': indices.nbytes+weights.nbytes,
        'partial_buffers_bytes': parts*26*len(nodes)*16,
        'geometry_proof': '共享idx使三输出位于同一cube；8角parity互异，给定色各输出若有正支撑必是同一节点，三路weight可不同/为0。'}
    colours = parity(model.m)
    for colour in range(8):
        changes, forbidden, invalid = gains(indices, weights, acc, squared, targets, mass, caps,
            nodes, colours, colour, rho, parts)
        if invalid: raise AssertionError('shared cube的parity正支撑节点或当前d2缓存不一致')
        moves, predicted, changed, joint = select(changes, forbidden, colours, colour)
        apply(indices, weights, acc, squared, targets, moves)
        values = nodes.astype(np.int32)+moves
        if values.min() < 0 or values.max() > 255: raise AssertionError('联合节点越界')
        nodes = values.astype(np.uint8)
        measured = float(mass@rho[squared])
        bad = int(np.count_nonzero(squared > caps))
        if abs(measured-current-predicted) > 1e-10 or measured > current+1e-11 or bad:
            raise AssertionError('26方向联合收益/cap不一致')
        entry = {'colour': colour, 'changed_nodes': changed, 'joint_channel_moves': joint,
            'before_weighted_objective': current, 'after_weighted_objective': measured,
            'predicted_change': predicted, 'measured_change': measured-current,
            'prediction_error': abs(measured-current-predicted), 'geometry_errors': int(invalid),
            'cap_violations': bad, 'seconds': time.perf_counter()-started}
        current = measured; report['groups'].append(entry)
        if progress: progress(entry)
    candidate = cc.ChannelLut(model.grid.copy(), nodes.reshape(model.nodes.shape), model.idx.copy(), model.channel_frac.copy())
    checked_acc, checked_squared = accumulate(indices, weights, nodes, targets)
    fresh = cc.predict(candidate, points)
    if (not np.array_equal(acc, checked_acc) or not np.array_equal(squared, checked_squared)
            or not np.array_equal(((acc+io.ONE//2) >> io.Q).astype(np.uint8), fresh)
            or not np.array_equal(cg.squared_error(fresh, targets), squared)
            or np.any(squared > caps) or abs(float(mass@rho[squared])-current) > 1e-10):
        raise AssertionError('联合整扫fresh缓存/逐色cap不一致')
    report.update(after_weighted_objective=current,
        changed_node_components=int(np.count_nonzero(candidate.nodes != model.nodes)),
        changed_nodes=int(np.count_nonzero(np.any(candidate.nodes != model.nodes, axis=3))),
        joint_channel_moves=sum(row['joint_channel_moves'] for row in report['groups']),
        training_cap_violations=0, cache_recompute_mismatches=0,
        geometry_errors=0, seconds=time.perf_counter()-started,
        scope='固定一个节点RGB[-1,1]^3联合邻域，8色一次；不覆盖多节点联合，不称全局最优')
    return candidate, report
