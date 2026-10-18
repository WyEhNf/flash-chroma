"""固定节点，在既有单调边界内精确枚举Q16舍入事件，离散目标用float64归约。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit, prange
from . import axis_calibration as ac, io


@njit(cache=True, inline='always')
def _line(nodes, idx, frac, m, r, g, b, axis, f):
    base = (int(idx[0, r])*m+int(idx[1, g]))*m+int(idx[2, b])
    x = f if axis == 0 else int(frac[0, r])
    y = f if axis == 1 else int(frac[1, g])
    z = f if axis == 2 else int(frac[2, b])
    a, c, d = m*m, m, 1
    ax, ay, az = axis == 0, axis == 1, axis == 2
    if x < y:
        x, y, a, c, ax, ay = y, x, c, a, ay, ax
    if y < z:
        y, z, c, d, ay, az = z, y, d, c, az, ay
    if x < y:
        x, y, a, c, ax, ay = y, x, c, a, ay, ax
    i0, i1, i2, i3 = base, base+a, base+a+c, base+m*m+m+1
    left, right = (i0, i1) if ax else ((i1, i2) if ay else (i2, i3))
    slope = np.empty(3, np.int64)
    intercept = np.empty(3, np.int64)
    for channel in range(3):
        slope[channel] = int(nodes[right, channel])-int(nodes[left, channel])
        value = ((io.ONE-x)*int(nodes[i0, channel])+(x-y)*int(nodes[i1, channel])
                 +(y-z)*int(nodes[i2, channel])+z*int(nodes[i3, channel]))
        intercept[channel] = value-slope[channel]*f+io.ONE//2
    return intercept, slope


@njit(cache=True, inline='always')
def _next_event(f, end, intercept, slope, output):
    result = end+1
    for channel in range(3):
        b, c, y = slope[channel], intercept[channel], output[channel]
        if b > 0:
            threshold = -(-((y+1)*io.ONE-c)//b)
            result = min(result, threshold)
        elif b < 0:
            threshold = (c-y*io.ONE)//(-b)+1
            result = min(result, threshold)
    return result


@njit(cache=True, parallel=True)
def events(points, nodes, idx, frac, m, targets, terminal_targets, reference, caps, suffix,
           mass, rho, suffix_weight, axis, lower, upper, order, offsets, width):
    """每个输入只走真实输出变化事件；同轴码值各占一行，无并发写冲突。"""
    cost_diff = np.zeros((256, width), np.float64)
    violation_diff = np.zeros((256, width), np.int64)
    baseline = np.zeros(256, np.float64)
    event_count = np.zeros(256, np.int64)
    invalid_events = np.zeros(256, np.int64)
    for code in prange(256):
        lo, hi = int(lower[code]), int(upper[code])
        start, stop = (offsets[code], offsets[code+1]) if len(order) else (0, 65536)
        for t in range(start, stop):
            p = order[t] if len(order) else ac._slab_index(axis, code, t)
            r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
            rgb = ac._pixel(nodes, idx, frac, m, r, g, b, axis, 0)
            before, _ = ac._cost(rgb[0], rgb[1], rgb[2], targets[p], terminal_targets[p], reference[p], suffix, rho, suffix_weight)
            baseline[code] += mass[p]*before
            other = np.empty(2, np.int64)
            if axis == 0:
                other[0], other[1] = frac[1, g], frac[2, b]
            elif axis == 1:
                other[0], other[1] = frac[0, r], frac[2, b]
            else:
                other[0], other[1] = frac[0, r], frac[1, g]
            a, b_other = min(other[0], other[1]), max(other[0], other[1])
            f, previous_cost, previous_violation = lo, 0., 0
            while f <= hi:
                end = min(hi, a if f <= a else (b_other if f <= b_other else hi))
                intercept, slope = _line(nodes, idx, frac, m, r, g, b, axis, f)
                while f <= end:
                    output = (intercept+slope*f)//io.ONE
                    cost, squared = ac._cost(output[0], output[1], output[2], targets[p],
                        terminal_targets[p], reference[p], suffix, rho, suffix_weight)
                    violation = int(squared > caps[p])
                    cost_diff[code, f-lo] += mass[p]*(cost-previous_cost)
                    violation_diff[code, f-lo] += violation-previous_violation
                    previous_cost, previous_violation = cost, violation
                    event_count[code] += 1
                    next_f = _next_event(f, end, intercept, slope, output)
                    if next_f <= f:
                        invalid_events[code] += 1
                        f = hi+1
                    else:
                        f = next_f
    return cost_diff, violation_diff, baseline, event_count, invalid_events


def propose(model, points, targets, mass, *, envelope, extra_objective, anchor,
            sweeps=2, maximum_shift=4096, parts=4, progress=None):
    """固定两扫精确单坐标块下降；不同轴仍有非凸交互，不称全局最优。"""
    io.validate_sparse(model, competition=True)
    io.validate_sparse(anchor, competition=True)
    if (len(points) != 256**3 or points.shape != (256**3, 3) or points.dtype != np.uint8
            or targets.shape != points.shape or targets.dtype != np.uint8
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(np.sum(mass))-1.) > 1e-10 or sweeps not in (1, 2)
            or maximum_shift != 4096 or not 1 <= parts <= 32
            or len(envelope.suffix) != 256**3 or not np.array_equal(envelope.suffix, extra_objective.suffix)
            or model.m != anchor.m or not np.array_equal(model.grid, anchor.grid)
            or not np.array_equal(model.tables()[0], anchor.tables()[0])):
        raise ValueError('需要固定首级全域、同一后缀、原坐标锚点和预定有限预算')
    extra_objective.validate(targets)
    for start in range(0, len(points), 1 << 18):
        keys = points[start:start+(1 << 18)].astype(np.int64)@np.array([65536, 256, 1], np.int64)
        if not np.array_equal(keys, np.arange(start, start+len(keys))) or not np.array_equal(envelope.lookup[start:start+len(keys)], keys):
            raise ValueError('要求原色到本级行的规范恒等映射')
    idx, original = model.tables()
    frac = original.astype(np.int64)
    lower, upper = ac.bounds(*anchor.tables(), maximum_shift)
    if np.any(frac < lower) or np.any(frac > upper):
        raise ValueError('起点超出上一阶段原始坐标范围，不能隐式扩大')
    nodes = model.nodes.reshape(-1, 3)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    common = (points, nodes, idx, frac, model.m, targets, extra_objective.targets,
              envelope.targets, envelope.caps, envelope.suffix, mass, rho, extra_objective.weight)
    current, violations = ac._measure(*common, parts)
    if violations:
        raise ValueError('起点违反整链包络')
    report = {'before_weighted_objective': float(current), 'rounds': [], 'maximum_shift_from_anchor': maximum_shift,
        'objective': '同一本级原表及固定稀疏后缀标签；全部整数舍入事件，float64质量归约',
        'scope': '每轴每码值在同一静态区间内全枚举事件；轴间有限块下降，不证明联合全局最优'}
    report['chain_envelope'] = envelope.metadata
    saved, started = [], time.perf_counter()
    for sweep in range(1, sweeps+1):
        for axis in range(3):
            width = int(np.max(upper[axis]-lower[axis]))+1
            diff, forbidden_diff, baseline, counts, invalid = events(*common, axis, lower[axis], upper[axis],
                np.empty(0, np.int32), np.empty(0, np.int64), width)
            if np.any(invalid):
                raise AssertionError('舍入事件没有前进')
            losses = np.cumsum(diff, axis=1)
            forbidden = np.cumsum(forbidden_diff, axis=1)
            code = np.arange(256)
            old_index = frac[axis]-lower[axis]
            if (np.max(np.abs(losses[code, old_index]-baseline)) > 1e-8
                    or abs(float(baseline.sum())-current) > 1e-8
                    or np.any(forbidden[code, old_index])):
                raise AssertionError('事件表起点与独立逐点目标或包络不同')
            moved = 0
            for c in range(256):
                count = int(upper[axis, c]-lower[axis, c])+1
                values = losses[c, :count].copy()
                values[forbidden[c, :count] > 0] = np.inf
                minimum = float(values.min())
                if minimum < baseline[c]-1e-12:
                    choices = np.flatnonzero(values <= minimum+1e-12)
                    best = int(choices[np.argmin(np.abs(choices-old_index[c]))])
                    frac[axis, c] = lower[axis, c]+best
                    current += float(values[best]-baseline[c])
                    moved += 1
            measured, violations = ac._measure(*common, parts)
            if violations or abs(float(measured)-current) > 1e-8:
                raise AssertionError('精确切片批量应用后目标或包络不同')
            current = float(measured)
            if np.any(np.diff(idx.astype(np.int64)*io.ONE+frac, axis=1) < 0):
                raise AssertionError('静态区间批量结果不单调')
            row = {'sweep': sweep, 'axis': axis, 'changed_coordinates': moved,
                   'events': int(counts.sum()), 'weighted_objective': current,
                   'cap_violations': int(violations), 'seconds': time.perf_counter()-started}
            report['rounds'].append(row)
            if progress:
                progress(row)
        saved.append((sweep, io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), frac.astype(np.uint32))))
    report.update(after_weighted_objective=current, seconds=time.perf_counter()-started)
    return saved, report
