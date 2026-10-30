"""实验表示：共享RGB8节点/idx，每个输出通道有独立Q16坐标；不是SLUT v1。"""
from __future__ import annotations

from dataclasses import dataclass
import time
import numpy as np
from numba import njit, prange
from . import axis_calibration as ac, exact_axis, io, monotone_axis


@dataclass
class ChannelLut:
    grid: np.ndarray
    nodes: np.ndarray
    idx: np.ndarray
    channel_frac: np.ndarray

    @property
    def m(self):
        return self.grid.shape[1]


def validate(model):
    if model.channel_frac.shape != (3, 3, 256) or model.channel_frac.dtype != np.uint32:
        raise ValueError('实验坐标必须为3输出×3轴×256码的uint32')
    for channel in range(3):
        io.validate_sparse(io.SparseLut(model.grid, model.nodes, model.idx, model.channel_frac[channel]), competition=True)
    if (np.any(np.diff(model.idx.astype(np.int64), axis=1) < 0)
            or np.any(np.diff(model.idx[None].astype(np.int64)*io.ONE+model.channel_frac, axis=2) < 0)):
        raise ValueError('此实验要求共享idx与各输出有效坐标非降')


def from_sparse(model):
    io.validate_sparse(model, competition=True)
    idx, frac = model.tables()
    result = ChannelLut(model.grid.copy(), model.nodes.copy(), idx.copy(), np.repeat(frac[None], 3, axis=0))
    validate(result)
    return result


@njit(cache=True, inline='always')
def _pixel(nodes, idx, frac, m, r, g, b, channel):
    base = (np.int64(idx[0, r])*m+np.int64(idx[1, g]))*m+np.int64(idx[2, b])
    x, y, z = np.int64(frac[channel, 0, r]), np.int64(frac[channel, 1, g]), np.int64(frac[channel, 2, b])
    a, c, d = m*m, m, 1
    if x < y: x, y, a, c = y, x, c, a
    if y < z: y, z, c, d = z, y, d, c
    if x < y: x, y, a, c = y, x, c, a
    v0, v1, v2, v3 = base, base+a, base+a+c, base+m*m+m+1
    value = ((io.ONE-x)*np.int64(nodes[v0, channel])+(x-y)*np.int64(nodes[v1, channel])
        +(y-z)*np.int64(nodes[v2, channel])+z*np.int64(nodes[v3, channel]))
    return (value+io.ONE//2) >> io.Q


@njit(cache=True, parallel=True)
def _predict(points, nodes, idx, frac, m):
    output = np.empty((len(points), 3), np.uint8)
    for p in prange(len(points)):
        for channel in range(3):
            output[p, channel] = _pixel(nodes, idx, frac, m, int(points[p, 0]), int(points[p, 1]), int(points[p, 2]), channel)
    return output


def predict(model, points):
    validate(model)
    if points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3:
        raise ValueError('实验前向需要N×3 RGB8')
    return _predict(points, model.nodes.reshape(-1, 3), model.idx, model.channel_frac, model.m)


@njit(cache=True, parallel=True)
def _refresh(points, nodes, idx, frac, m, targets, output, squared, channel):
    """只更新一个输出通道；其它两个通道及其误差保留当前缓存。"""
    for p in prange(len(points)):
        before = np.int64(output[p, channel])-np.int64(targets[p, channel])
        value = _pixel(nodes, idx, frac, m, int(points[p, 0]), int(points[p, 1]), int(points[p, 2]), channel)
        after = value-np.int64(targets[p, channel])
        squared[p] += after*after-before*before
        output[p, channel] = value


@njit(cache=True, parallel=True)
def events(points, nodes, idx, frac, m, targets, mass, caps, output, squared, rho,
           channel, axis, order, offsets):
    """固定其它输出通道，遍历当前通道的整数舍入事件；同轴slab互斥。"""
    costs = np.zeros((256, io.ONE+1), np.float64)
    violations = np.zeros((256, io.ONE+1), np.int64)
    baseline, counts, invalid = np.zeros(256), np.zeros(256, np.int64), np.zeros(256, np.int64)
    for code in prange(256):
        start, stop = (offsets[code], offsets[code+1]) if len(order) else (0, 65536)
        for t in range(start, stop):
            p = order[t] if len(order) else ac._slab_index(axis, code, t)
            r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
            old_error = np.int64(output[p, channel])-np.int64(targets[p, channel])
            other_squared = squared[p]-old_error*old_error
            baseline[code] += mass[p]*rho[squared[p]]
            if axis == 0:
                f0, f1 = frac[channel, 1, g], frac[channel, 2, b]
            elif axis == 1:
                f0, f1 = frac[channel, 0, r], frac[channel, 2, b]
            else:
                f0, f1 = frac[channel, 0, r], frac[channel, 1, g]
            a, b_other = min(f0, f1), max(f0, f1)
            f, previous_cost, previous_bad = 0, 0., 0
            while f <= io.ONE:
                end = min(io.ONE, a if f <= a else (b_other if f <= b_other else io.ONE))
                intercept, slope = exact_axis._line(nodes, idx, frac[channel], m, r, g, b, axis, f)
                intercept_c, slope_c = intercept[channel], slope[channel]
                while f <= end:
                    value = (intercept_c+slope_c*f)//io.ONE
                    error = value-np.int64(targets[p, channel])
                    d2 = other_squared+error*error
                    cost, bad = rho[d2], int(d2 > caps[p])
                    costs[code, f] += mass[p]*(cost-previous_cost)
                    violations[code, f] += bad-previous_bad
                    previous_cost, previous_bad = cost, bad
                    counts[code] += 1
                    next_f = end+1
                    if slope_c > 0:
                        next_f = min(next_f, -(-((value+1)*io.ONE-intercept_c)//slope_c))
                    elif slope_c < 0:
                        next_f = min(next_f, (intercept_c-value*io.ONE)//(-slope_c)+1)
                    if next_f <= f:
                        invalid[code] += 1
                        f = io.ONE+1
                    else:
                        f = next_f
    return costs, violations, baseline, counts, invalid


def propose(model, points, targets, mass, *, caps, parts=4, progress=None):
    """节点/idx固定，输出通道R/G/B各依次R/G/B轴一块，共9块一次，不追加扫数。"""
    initial = from_sparse(model)
    if (points.dtype != np.uint8 or points.shape != (256**3, 3) or targets.dtype != np.uint8
            or targets.shape != points.shape or mass.shape != (len(points),) or not np.all(np.isfinite(mass))
            or np.any(mass < 0) or abs(float(mass.sum())-1.) > 1e-10 or parts != 4
            or np.asarray(caps).dtype.kind not in 'iu' or np.shape(caps) != (len(points),)
            or np.any(caps < 0) or np.any(caps > 3*255**2)):
        raise ValueError('此冻结研究要求完整canonical RGB8域、质量1、逐色整数cap及4线程')
    for start in range(0, len(points), 1 << 18):
        block = points[start:start+(1 << 18)].astype(np.int64)
        if not np.array_equal(block@np.array([65536, 256, 1], np.int64), np.arange(start, start+len(block))):
            raise ValueError('训练行不是完整B最快RGB8')
    nodes, idx = initial.nodes.reshape(-1, 3), initial.idx
    frac = initial.channel_frac.astype(np.int64)
    output = _predict(points, nodes, idx, frac, model.m)
    difference = output.astype(np.int32)-targets.astype(np.int32)
    squared = np.sum(difference*difference, axis=1, dtype=np.int32)
    del difference
    if np.any(squared > caps):
        raise ValueError('三份复制的等价起点违反旧2dd逐色cap')
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    current = float(mass@rho[squared])
    report = {'before_weighted_objective': current, 'blocks': [], 'parts': parts,
        'representation': '实验NPZ；共享idx/节点，每输出通道独立3×256 Q16 frac；不属SLUT v1',
        'fraction_payload_bytes': int(frac.size*4), 'extra_fraction_payload_bytes': 2*3*256*4,
        'scope': '9块单轴真实RGB8目标单调DP；固定当前其它输出误差，不是联合全局最优或运行时验证'}
    started = time.perf_counter()
    for channel in range(3):
        for axis in range(3):
            diff, bdiff, baseline, counts, invalid = events(points, nodes, idx, frac, model.m,
                targets, mass, caps, output, squared, rho, channel, axis, np.empty(0, np.int32), np.empty(0, np.int64))
            if np.any(invalid):
                raise AssertionError('通道事件没有前进')
            costs, violations = np.cumsum(diff, axis=1), np.cumsum(bdiff, axis=1)
            del diff, bdiff
            if np.any(violations < 0):
                raise AssertionError('通道事件的cap计数为负')
            old, rows = frac[channel, axis].copy(), np.arange(256)
            if (np.max(np.abs(costs[rows, old]-baseline)) > 1e-8
                    or abs(float(baseline.sum())-current) > 1e-8 or np.any(violations[rows, old])):
                raise AssertionError('当前通道事件起点与当前整图缓存不符')
            selected, predicted = monotone_axis.choose_axis(costs, violations, idx[axis], old)
            del costs, violations
            frac[channel, axis] = selected
            _refresh(points, nodes, idx, frac, model.m, targets, output, squared, channel)
            measured = float(mass@rho[squared])
            bad = int(np.count_nonzero(squared > caps))
            if (bad or abs(measured-predicted) > 1e-8
                    or np.any(np.diff(idx[axis].astype(np.int64)*io.ONE+frac[channel, axis]) < 0)
                    or not np.array_equal(frac[channel, axis, [0, 255]], old[[0, 255]])):
                raise AssertionError('通道DP应用后目标/cap/单调/端点不符')
            accepted = measured < current-1e-11
            if not accepted:
                frac[channel, axis] = old
                _refresh(points, nodes, idx, frac, model.m, targets, output, squared, channel)
            entry = {'channel': channel, 'axis': axis, 'accepted': bool(accepted),
                'before_weighted_objective': current,
                'after_weighted_objective': measured if accepted else current,
                'events': int(counts.sum()), 'changed_coordinates': int(np.count_nonzero(frac[channel, axis] != old)),
                'maximum_fraction_shift': int(np.max(np.abs(frac[channel, axis]-old))), 'cap_violations': bad,
                'seconds': time.perf_counter()-started}
            if accepted: current = measured
            report['blocks'].append(entry)
            if progress: progress(entry)
    checked = _predict(points, nodes, idx, frac, model.m)
    checked_difference = checked.astype(np.int32)-targets.astype(np.int32)
    checked_squared = np.sum(checked_difference*checked_difference, axis=1, dtype=np.int32)
    if (not np.array_equal(checked, output) or not np.array_equal(checked_squared, squared)
            or np.any(checked_squared > caps) or abs(float(mass@rho[checked_squared])-current) > 1e-8):
        raise AssertionError('9块完成后重新计算训练缓存不一致')
    candidate = ChannelLut(initial.grid.copy(), initial.nodes.copy(), idx.copy(), frac.astype(np.uint32))
    validate(candidate)
    if not np.array_equal(candidate.nodes, model.nodes) or not np.array_equal(candidate.idx, model.tables()[0]):
        raise AssertionError('新表示不得改变节点或shared idx')
    report.update(after_weighted_objective=current, changed_coordinates=int(np.count_nonzero(frac != initial.channel_frac)),
        maximum_total_shift=int(np.max(np.abs(frac-initial.channel_frac.astype(np.int64)))),
        cache_recompute_mismatches=0, training_cap_violations=0, seconds=time.perf_counter()-started)
    return candidate, report
