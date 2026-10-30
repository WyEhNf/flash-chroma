"""跨越整数平台的±2/±4节点提议，并在整批内交换均值预算。"""
from __future__ import annotations
import numpy as np
from numba import njit, prange
from . import channel_joint_nodes as cj, channel_tail_nodes as tail, io

DIRECTIONS = np.concatenate((2*cj.DIRECTIONS, 4*cj.DIRECTIONS), axis=0)


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, reference, suffix, mass, nodes, colours, colour, caps, root, parts):
    size = len(nodes)
    private = np.zeros((parts, 9, 52, size), np.float64)
    bad = np.zeros((parts, 52, size), np.int64)
    invalid = np.zeros(parts, np.int64)
    legal = np.ones((52, size), np.uint8)
    for n in prange(size):
        for d in range(52):
            for c in range(3):
                if not 0 <= np.int64(nodes[n, c])+DIRECTIONS[d, c] <= 255:
                    legal[d, n] = 0
    for part in prange(parts):
        value = np.empty((3, 5), np.int64)
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
                for step in range(5):
                    value[c, step] = (np.int64(acc[p, c])+2*(step-2)*selected_weight+io.ONE//2) >> io.Q
            if node < 0:
                continue
            old = tail.chain_square(value[0, 2], value[1, 2], value[2, 2], suffix, reference[p])
            if old > caps[p]:
                invalid[part] += 1
            for d in range(52):
                if not legal[d, node]:
                    continue
                direction = DIRECTIONS[d]
                new = tail.chain_square(value[0, direction[0]//2+2], value[1, direction[1]//2+2],
                    value[2, direction[2]//2+2], suffix, reference[p])
                distance, square = root[new]-root[old], new-old
                private[part, 0, d, node] += distance
                private[part, 1, d, node] += mass[p]*distance
                private[part, 2, d, node] += square
                private[part, 3, d, node] += mass[p]*square
                private[part, 4, d, node] += max(new-12, 0)-max(old-12, 0)
                private[part, 5, d, node] += max(new-36, 0)-max(old-36, 0)
                private[part, 6, d, node] += int(new > 12)-int(old > 12)
                private[part, 7, d, node] += int(new > 65)-int(old > 65)
                private[part, 8, d, node] += max(new-49, 0)-max(old-49, 0)
                bad[part, d, node] += int(new > caps[p])
    result, forbidden = private.sum(axis=0), bad.sum(axis=0)
    for n in prange(size):
        for d in range(52):
            if not legal[d, n]:
                forbidden[d, n] += 1
    return result, forbidden, invalid.sum()


def select(change, bad, colours, colour):
    """先取得严格局部mean收益，再以整批预算换取原max计数下降。"""
    chosen = np.full(len(colours), -1, np.int32)
    predicted = np.zeros(9)
    nodes = np.flatnonzero(colours == colour)
    for n in nodes:
        best = (0., 0., 0.)
        for d in range(52):
            v = change[:, d, n]
            if bad[d, n] or np.any(v[:4] > 1e-11) or np.any(v[4:] > 1e-11):
                continue
            score = (v[0], v[7], v[4])
            if score < best:
                chosen[n], best = d, score
        if chosen[n] >= 0:
            predicted += change[:, chosen[n], n]
    baseline_choice = chosen.copy()
    candidates = []
    for n in nodes:
        old = np.zeros(9) if chosen[n] < 0 else change[:, chosen[n], n]
        for d in range(52):
            if not bad[d, n] and change[7, d, n] < old[7]:
                candidates.append((change[7, d, n]-old[7], change[8, d, n]-old[8], change[0, d, n]-old[0], int(n), d))
    candidates.sort()
    for _, _, _, n, d in candidates:
        old = np.zeros(9) if chosen[n] < 0 else change[:, chosen[n], n]
        new = change[:, d, n]
        if new[7] >= old[7]:
            continue
        tentative = predicted+new-old
        # 每批两种mean、两种RMS、p99超额/计数、严重尾部均不可借下一批还账。
        if np.all(tentative <= 1e-9):
            chosen[n], predicted = d, tentative
    moves = np.zeros((len(colours), 3), np.int32)
    accepted = []
    for n in np.flatnonzero(chosen >= 0):
        moves[n] = DIRECTIONS[chosen[n]]
        accepted.append({'node': int(n), 'direction': int(chosen[n]),
                         'budget_exchange': bool(chosen[n] != baseline_choice[n]),
                         'deltas': change[:, chosen[n], n].tolist()})
    return moves, predicted, accepted


def measure(output, reference, suffix, mass):
    values, squared = tail.measure(output, reference, suffix, mass)
    values[4] = np.maximum(squared-12, 0).sum()
    values[6] = np.count_nonzero(squared > 12)
    return np.r_[values, np.count_nonzero(squared > 65), np.maximum(squared-49, 0).sum()], squared
