"""真实整数四级链上的尾部节点精化，分别保护全域和原训练质量的均值。"""
from __future__ import annotations

import numpy as np
from numba import njit, prange
from . import channel_joint_nodes as cj, channel_coordinates as cc, io


@njit(cache=True, inline='always')
def chain_square(r, g, b, suffix, target):
    value = suffix[(r << 16) | (g << 8) | b]
    result = 0
    for c in range(3):
        delta = np.int64(value[c])-np.int64(target[c])
        result += delta*delta
    return result


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, reference, suffix, mass, nodes, colours,
          colour, caps, root, parts, p99_sq=14, severe_sq=36):
    """八色各角互斥；每个方向统计完整支撑，不能只看高误差点。"""
    size = len(nodes)
    # mean、训练质量mean、RMS平方、训练质量RMS平方、p99超额、严重尾部、p99计数。
    private = np.zeros((parts, 7, 26, size), np.float64)
    bad = np.zeros((parts, 26, size), np.int64)
    invalid = np.zeros(parts, np.int64)
    legal = np.ones((26, size), np.uint8)
    for n in prange(size):
        for d in range(26):
            for c in range(3):
                if not 0 <= np.int64(nodes[n, c])+cj.DIRECTIONS[d, c] <= 255:
                    legal[d, n] = 0
    for part in prange(parts):
        value = np.empty((3, 3), np.int64)
        for p in range(len(reference)*part//parts, len(reference)*(part+1)//parts):
            node = -1
            for c in range(3):
                selected_weight, channel_node = 0, -1
                for v in range(4):
                    n, w = indices[c, p, v], weights[c, p, v]
                    if w > 0 and colours[n] == colour:
                        if channel_node >= 0:
                            invalid[part] += 1
                        selected_weight, channel_node = w, n
                if channel_node >= 0:
                    if node >= 0 and node != channel_node:
                        invalid[part] += 1
                    node = channel_node
                for step in range(3):
                    value[c, step] = (np.int64(acc[p, c])+(step-1)*selected_weight+io.ONE//2) >> io.Q
            if node < 0:
                continue
            old = chain_square(value[0, 1], value[1, 1], value[2, 1], suffix, reference[p])
            if old > caps[p]:
                invalid[part] += 1
            for d in range(26):
                if not legal[d, node]:
                    continue
                direction = cj.DIRECTIONS[d]
                new = chain_square(value[0, direction[0]+1], value[1, direction[1]+1], value[2, direction[2]+1], suffix, reference[p])
                distance = root[new]-root[old]
                square = new-old
                private[part, 0, d, node] += distance
                private[part, 1, d, node] += mass[p]*distance
                private[part, 2, d, node] += square
                private[part, 3, d, node] += mass[p]*square
                private[part, 4, d, node] += max(new-p99_sq, 0)-max(old-p99_sq, 0)
                private[part, 5, d, node] += max(new-severe_sq, 0)-max(old-severe_sq, 0)
                private[part, 6, d, node] += int(new > p99_sq)-int(old > p99_sq)
                bad[part, d, node] += int(new > caps[p])
    result = private.sum(axis=0)
    forbidden = bad.sum(axis=0)
    for n in prange(size):
        for d in range(26):
            if not legal[d, n]:
                forbidden[d, n] += 1
    return result, forbidden, invalid.sum()


def select(change, forbidden, colours, colour, mode):
    """只接受双mean/双RMS/p99计数不增，按冻结的尾部优先级选择。"""
    moves = np.zeros((len(colours), 3), np.int32)
    predicted = np.zeros(7, np.float64)
    accepted = []
    for n in np.flatnonzero(colours == colour):
        best, chosen = (0., 0., 0.), -1
        for d in range(26):
            v = change[:, d, n]
            if forbidden[d, n] or np.any(v[:4] > 1e-11) or v[6] > 0:
                continue
            score = (v[5], v[4], v[0]) if mode == 'severe_first' else (v[4], v[5], v[0])
            if score < best:
                best, chosen = score, d
        if chosen >= 0:
            moves[n] = cj.DIRECTIONS[chosen]
            predicted += change[:, chosen, n]
            accepted.append({'node': int(n), 'direction': int(chosen), 'deltas': change[:, chosen, n].tolist()})
    return moves, predicted, accepted


def measure(output, reference, suffix, mass, p99_sq=14, severe_sq=36):
    values = np.zeros(7, np.float64)
    squared = np.empty(len(output), np.int32)
    for start in range(0, len(output), 1 << 18):
        stop = min(start+(1 << 18), len(output))
        keys = output[start:stop].astype(np.int64)@np.array([65536, 256, 1], np.int64)
        delta = suffix[keys].astype(np.int32)-reference[start:stop].astype(np.int32)
        s = np.sum(delta*delta, axis=1, dtype=np.int32)
        squared[start:stop] = s
        distance = np.sqrt(s.astype(np.float64))
        w = mass[start:stop]
        values += [distance.sum(), w@distance, s.sum(), w@s,
                   np.maximum(s-p99_sq, 0).sum(), np.maximum(s-severe_sq, 0).sum(), np.count_nonzero(s > p99_sq)]
    return values, squared


def apply(model, indices, weights, acc, moves, reference):
    """沿用已验证的整数更新核；squared仅为该核的辅助量。"""
    scratch = np.empty(len(reference), np.int32)
    cj.apply(indices, weights, acc, scratch, reference, moves)
    nodes = model.nodes.astype(np.int32)+moves.reshape(model.nodes.shape)
    if nodes.min() < 0 or nodes.max() > 255:
        raise AssertionError('节点越界')
    return cc.ChannelLut(model.grid.copy(), nodes.astype(np.uint8), model.idx.copy(), model.channel_frac.copy())
