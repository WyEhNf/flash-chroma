"""固定RGB8节点的单调可分离坐标校准；显式扩大插值函数族。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit, prange
from . import io


@njit(cache=True, inline='always')
def _pixel(nodes, idx, frac, m, r, g, b, axis, delta):
    base = (int(idx[0, r])*m+int(idx[1, g]))*m+int(idx[2, b])
    x = int(frac[0, r])+(delta if axis == 0 else 0)
    y = int(frac[1, g])+(delta if axis == 1 else 0)
    z = int(frac[2, b])+(delta if axis == 2 else 0)
    a, c, d = m*m, m, 1
    if x < y:
        x, y, a, c = y, x, c, a
    if y < z:
        y, z, c, d = z, y, d, c
    if x < y:
        x, y, a, c = y, x, c, a
    i0, i1, i2, i3 = base, base+a, base+a+c, base+m*m+m+1
    w0, w1, w2, w3 = io.ONE-x, x-y, y-z, z
    r_out = (w0*int(nodes[i0, 0])+w1*int(nodes[i1, 0])+w2*int(nodes[i2, 0])+w3*int(nodes[i3, 0])+io.ONE//2) >> io.Q
    g_out = (w0*int(nodes[i0, 1])+w1*int(nodes[i1, 1])+w2*int(nodes[i2, 1])+w3*int(nodes[i3, 1])+io.ONE//2) >> io.Q
    b_out = (w0*int(nodes[i0, 2])+w1*int(nodes[i1, 2])+w2*int(nodes[i2, 2])+w3*int(nodes[i3, 2])+io.ONE//2) >> io.Q
    return r_out, g_out, b_out


@njit(cache=True, inline='always')
def _slab_index(axis, code, t):
    if axis == 0:
        return (np.int64(code) << 16) | np.int64(t)
    if axis == 1:
        return ((np.int64(t) >> 8) << 16) | (np.int64(code) << 8) | (np.int64(t) & 255)
    return (np.int64(t) << 8) | np.int64(code)


@njit(cache=True, inline='always')
def _cost(r, g, b, target, terminal_target, reference, suffix, rho, suffix_weight):
    er, eg, eb = r-int(target[0]), g-int(target[1]), b-int(target[2])
    own = er*er+eg*eg+eb*eb
    final = suffix[(r << 16) | (g << 8) | b]
    er, eg, eb = int(final[0])-int(terminal_target[0]), int(final[1])-int(terminal_target[1]), int(final[2])-int(terminal_target[2])
    terminal = er*er+eg*eg+eb*eb
    er, eg, eb = int(final[0])-int(reference[0]), int(final[1])-int(reference[1]), int(final[2])-int(reference[2])
    return rho[own]+suffix_weight*rho[terminal], er*er+eg*eg+eb*eb


@njit(cache=True, parallel=True)
def _scores(points, nodes, idx, frac, m, targets, terminal_targets, reference, caps, suffix,
            mass, rho, suffix_weight, axis, deltas, order, offsets):
    """同轴码值切片互斥；跨轴调用必须串行并重算全部四面体分支。"""
    baseline = np.zeros(256, np.float64)
    gains = np.zeros((2, 256), np.float64)
    forbidden = np.zeros((2, 256), np.uint8)
    for code in prange(256):
        for direction in range(2):
            if deltas[direction, code] == 0:
                forbidden[direction, code] = 1
        start, stop = (offsets[code], offsets[code+1]) if len(order) else (0, 65536)
        for t in range(start, stop):
            if len(order):
                p = order[t]
            else:
                p = _slab_index(axis, code, t)
            r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
            pr, pg, pb = _pixel(nodes, idx, frac, m, r, g, b, axis, 0)
            before, _ = _cost(pr, pg, pb, targets[p], terminal_targets[p], reference[p], suffix, rho, suffix_weight)
            baseline[code] += mass[p]*before
            for direction in range(2):
                if forbidden[direction, code]:
                    continue
                pr, pg, pb = _pixel(nodes, idx, frac, m, r, g, b, axis, deltas[direction, code])
                after, squared = _cost(pr, pg, pb, targets[p], terminal_targets[p], reference[p], suffix, rho, suffix_weight)
                if squared > caps[p]:
                    forbidden[direction, code] = 1
                gains[direction, code] += mass[p]*(after-before)
    return baseline, gains, forbidden


@njit(cache=True, parallel=True)
def _measure(points, nodes, idx, frac, m, targets, terminal_targets, reference, caps,
             suffix, mass, rho, suffix_weight, parts):
    loss = np.zeros(parts, np.float64)
    violations = np.zeros(parts, np.int64)
    for part in prange(parts):
        for p in range(len(points)*part//parts, len(points)*(part+1)//parts):
            r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
            pr, pg, pb = _pixel(nodes, idx, frac, m, r, g, b, 0, 0)
            cost, squared = _cost(pr, pg, pb, targets[p], terminal_targets[p], reference[p], suffix, rho, suffix_weight)
            loss[part] += mass[p]*cost
            violations[part] += int(squared > caps[p])
    return loss.sum(), violations.sum()


def bounds(idx, frac, maximum_shift):
    """相邻静态中点隔开全部可选区间，保证同轴批量更新后仍单调。"""
    original = frac.astype(np.int64)
    coordinate = idx.astype(np.int64)*io.ONE+original
    if np.any(np.diff(coordinate, axis=1) < 0):
        raise ValueError('起点有效坐标必须单调')
    lower = np.maximum(0, original-maximum_shift)
    upper = np.minimum(io.ONE, original+maximum_shift)
    lower[:, 1:] = np.maximum(lower[:, 1:], (coordinate[:, :-1]+coordinate[:, 1:]+1)//2-idx[:, 1:].astype(np.int64)*io.ONE)
    upper[:, :-1] = np.minimum(upper[:, :-1], (coordinate[:, :-1]+coordinate[:, 1:])//2-idx[:, :-1].astype(np.int64)*io.ONE)
    lower[:, [0, 255]] = original[:, [0, 255]]
    upper[:, [0, 255]] = original[:, [0, 255]]
    if np.any(lower > original) or np.any(upper < original):
        raise ValueError('起点不在静态单调区间内')
    return lower, upper


def propose(model, points, targets, mass, *, envelope, extra_objective, steps, maximum_shift=4096,
            checkpoints=(4, 8, 12), parts=4, progress=None):
    """仅首级完整规范RGB8训练行；固定有限粗到细调节，不是全局最优。"""
    io.validate_sparse(model, competition=True)
    if (len(points) != 256**3 or points.dtype != np.uint8 or points.shape != (256**3, 3)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(np.sum(mass))-1.) > 1e-10 or not 1 <= maximum_shift <= io.ONE//8
            or len(envelope.suffix) != 256**3 or not np.array_equal(envelope.suffix, extra_objective.suffix)
            or not 1 <= parts <= 32 or not checkpoints or any(c not in range(1, len(steps)+1) for c in checkpoints)
            or not 1 <= len(steps) <= 16 or any(not isinstance(s, int) or isinstance(s, bool) or s <= 0 for s in steps)):
        raise ValueError('坐标校准需要完整首级RGB8测度、同一冻结后缀与有限预算')
    extra_objective.validate(targets)
    for start in range(0, len(points), 1 << 18):
        keys = points[start:start+(1 << 18)].astype(np.int64)@np.array([65536, 256, 1], np.int64)
        if not np.array_equal(keys, np.arange(start, start+len(keys))) or not np.array_equal(envelope.lookup[start:start+len(keys)], keys):
            raise ValueError('坐标校准要求原色到本级行的规范恒等映射')
    idx, original = model.tables()
    frac = original.astype(np.int64)
    lower, upper = bounds(idx, original, maximum_shift)
    nodes = model.nodes.reshape(-1, 3)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    common = (points, nodes, idx, frac, model.m, targets, extra_objective.targets,
              envelope.targets, envelope.caps, envelope.suffix, mass, rho, extra_objective.weight)
    started = time.perf_counter()
    initial, violating = _measure(*common, parts)
    if violating:
        raise ValueError('提议起点违反整链包络')
    report = {'before_weighted_objective': float(initial), 'maximum_fraction_shift': maximum_shift,
        'steps': steps, 'rounds': [], 'scope': '扩大单调可分离坐标函数族；相同节点/字节数不代表相同几何插值族，非全局最优'}
    saved = []
    current = float(initial)
    for number, step in enumerate(steps, 1):
        changes = 0
        for axis in range(3):
            deltas = np.stack((np.minimum(frac[axis]+step, upper[axis])-frac[axis],
                               np.maximum(frac[axis]-step, lower[axis])-frac[axis])).astype(np.int64)
            before, gain, forbidden = _scores(*common, axis, deltas, np.empty(0, np.int32), np.empty(0, np.int64))
            if abs(float(before.sum())-current) > 1e-8:
                raise AssertionError('上一轴批量收益与重新逐点目标不一致')
            gain[forbidden > 0] = np.inf
            direction = np.where((gain[0] < -1e-12) & (gain[0] <= gain[1]), 0,
                                 np.where(gain[1] < -1e-12, 1, -1))
            for code in np.flatnonzero(direction >= 0):
                d = direction[code]
                frac[axis, code] += deltas[d, code]
                current += float(gain[d, code])
                changes += 1
        measured, violating = _measure(*common, parts)
        if violating or measured > current+1e-8 or abs(float(measured)-current) > 1e-8:
            raise AssertionError('独立整扫重算违反目标或包络')
        current = float(measured)
        effective = idx.astype(np.int64)*io.ONE+frac
        if np.any(np.diff(effective, axis=1) < 0) or np.any(np.abs(frac-original.astype(np.int64)) > maximum_shift):
            raise AssertionError('校准轴表违反总偏移或单调性')
        entry = {'round': number, 'step': step, 'changed_coordinates': changes, 'weighted_objective': current,
                 'cap_violations': int(violating), 'seconds': time.perf_counter()-started}
        report['rounds'].append(entry)
        if progress:
            progress(entry)
        if number in checkpoints:
            saved.append((number, io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), frac.astype(np.uint32))))
    report.update(after_weighted_objective=current, seconds=time.perf_counter()-started)
    return saved, report
