"""首级分输出Q16坐标：本级原表及固定稀疏后缀保持损失，整链参考只作硬cap。"""
from __future__ import annotations
import time
import numpy as np
from numba import njit, prange
from . import axis_calibration as ac, channel_coordinates as cc, exact_axis, io, monotone_axis


@njit(cache=True, parallel=True)
def measure(output, targets, terminal_targets, reference, caps, suffix, mass, rho, parts):
    losses, bad = np.zeros(parts), np.zeros(parts, np.int64)
    for part in prange(parts):
        for p in range(len(output)*part//parts, len(output)*(part+1)//parts):
            cost, d2 = ac._cost(np.int64(output[p, 0]), np.int64(output[p, 1]), np.int64(output[p, 2]),
                targets[p], terminal_targets[p], reference[p], suffix, rho, 1.)
            losses[part] += mass[p]*cost
            bad[part] += int(d2 > caps[p])
    return losses.sum(), bad.sum()


@njit(cache=True, parallel=True)
def chain_mismatches(output, suffix, expected):
    count = np.zeros(4, np.int64)
    for part in prange(4):
        for p in range(len(output)*part//4, len(output)*(part+1)//4):
            key = (np.int64(output[p, 0]) << 16) | (np.int64(output[p, 1]) << 8) | np.int64(output[p, 2])
            for c in range(3): count[part] += int(suffix[key, c] != expected[p, c])
    return count.sum()


@njit(cache=True, parallel=True)
def events(points, nodes, idx, frac, m, targets, terminal_targets, reference, caps, suffix,
           mass, rho, output, channel, axis, order, offsets):
    """当前其它两输出冻结；单输出每次真实整数事件后重算非线性后缀与cap。"""
    diff = np.zeros((256, io.ONE+1), np.float64)
    bdiff = np.zeros((256, io.ONE+1), np.int64)
    baseline, counts, invalid = np.zeros(256), np.zeros(256, np.int64), np.zeros(256, np.int64)
    for code in prange(256):
        start, stop = (offsets[code], offsets[code+1]) if len(order) else (0, 65536)
        for t in range(start, stop):
            p = order[t] if len(order) else ac._slab_index(axis, code, t)
            r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
            pr, pg, pb = np.int64(output[p, 0]), np.int64(output[p, 1]), np.int64(output[p, 2])
            cost, _ = ac._cost(pr, pg, pb, targets[p], terminal_targets[p], reference[p], suffix, rho, 1.)
            baseline[code] += mass[p]*cost
            if axis == 0: f0, f1 = frac[channel, 1, g], frac[channel, 2, b]
            elif axis == 1: f0, f1 = frac[channel, 0, r], frac[channel, 2, b]
            else: f0, f1 = frac[channel, 0, r], frac[channel, 1, g]
            a, b_other = min(f0, f1), max(f0, f1)
            f, previous_cost, previous_bad = 0, 0., 0
            while f <= io.ONE:
                end = min(io.ONE, a if f <= a else (b_other if f <= b_other else io.ONE))
                intercept, slope = exact_axis._line(nodes, idx, frac[channel], m, r, g, b, axis, f)
                intercept_c, slope_c = intercept[channel], slope[channel]
                while f <= end:
                    value = (intercept_c+slope_c*f)//io.ONE
                    vr, vg, vb = (value, pg, pb) if channel == 0 else ((pr, value, pb) if channel == 1 else (pr, pg, value))
                    cost, d2 = ac._cost(vr, vg, vb, targets[p], terminal_targets[p], reference[p], suffix, rho, 1.)
                    bad = int(d2 > caps[p])
                    diff[code, f] += mass[p]*(cost-previous_cost)
                    bdiff[code, f] += bad-previous_bad
                    previous_cost, previous_bad = cost, bad
                    counts[code] += 1
                    next_f = end+1
                    if slope_c > 0: next_f = min(next_f, -(-((value+1)*io.ONE-intercept_c)//slope_c))
                    elif slope_c < 0: next_f = min(next_f, (intercept_c-value*io.ONE)//(-slope_c)+1)
                    if next_f <= f:
                        invalid[code] += 1; f = io.ONE+1
                    else: f = next_f
    return diff, bdiff, baseline, counts, invalid


def propose(model, points, targets, terminal_targets, mass, *, reference, caps, suffix, baseline_stream,
            parts=4, progress=None):
    """R/G/B输出各R/G/B轴9块一次；标签始终独立T1与S(T1)。"""
    initial = cc.from_sparse(model)
    if (points.dtype != np.uint8 or points.shape != (256**3, 3)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or terminal_targets.dtype != np.uint8 or terminal_targets.shape != points.shape
            or reference.dtype != np.uint8 or reference.shape != points.shape
            or suffix.dtype != np.uint8 or suffix.shape != points.shape
            or np.shape(mass) != (len(points),) or np.any(mass < 0) or not np.all(np.isfinite(mass))
            or abs(float(mass.sum())-1.) > 1e-10 or parts != 4
            or np.shape(caps) != (len(points),) or np.asarray(caps).dtype.kind not in 'iu'
            or np.any(caps < 0) or np.any(caps > 3*255**2)
            or baseline_stream.dtype != np.uint8 or baseline_stream.shape != points.shape):
        raise ValueError('本轮需要完整规范RGB8、独立T1与S(T1)、同一固定后缀/原参考/caps/质量')
    for start in range(0, len(points), 1 << 18):
        rows = points[start:start+(1 << 18)].astype(np.int64)
        if not np.array_equal(rows@np.array([65536, 256, 1], np.int64), np.arange(start, start+len(rows))):
            raise ValueError('原RGB到首级行必须为规范恒等映射')
        value = targets[start:start+len(rows)].astype(np.int64)
        if not np.array_equal(terminal_targets[start:start+len(rows)], suffix[value@np.array([65536, 256, 1], np.int64)]):
            raise ValueError('后缀标签必须恰为S(T1)，不能混入精确整链reference')
    nodes, idx = initial.nodes.reshape(-1, 3), initial.idx
    frac = initial.channel_frac.astype(np.int64)
    output = cc._predict(points, nodes, idx, frac, model.m)
    error = output.astype(np.int32)-targets.astype(np.int32)
    squared = np.sum(error*error, axis=1, dtype=np.int32)
    del error
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    current, bad = measure(output, targets, terminal_targets, reference, caps, suffix, mass, rho, parts)
    if bad or chain_mismatches(output, suffix, baseline_stream):
        raise ValueError('三份复制首级不等价已验链或旧最佳chain不满足原cap')
    report = {'before_weighted_objective': float(current), 'blocks': [], 'parts': parts,
        'initial_chain_byte_mismatches': 0, 'initial_cap_violations': 0,
        'objective': 'rho(p-T1)+rho(S(p)-S(T1))，reference只进入cap',
        'representation': '实验NPZ共享节点/idx，每输出独立Q16 frac；坐标payload多6144字节，非SLUT v1或同速度声明'}
    started = time.perf_counter()
    for channel in range(3):
        for axis in range(3):
            diff, bdiff, baseline, counts, invalid = events(points, nodes, idx, frac, model.m, targets,
                terminal_targets, reference, caps, suffix, mass, rho, output, channel, axis,
                np.empty(0, np.int32), np.empty(0, np.int64))
            if np.any(invalid): raise AssertionError('首级单输出事件没有前进')
            losses, violations = np.cumsum(diff, axis=1), np.cumsum(bdiff, axis=1)
            del diff, bdiff
            if np.any(violations < 0): raise AssertionError('完整整链cap计数为负')
            old, rows = frac[channel, axis].copy(), np.arange(256)
            if (np.max(np.abs(losses[rows, old]-baseline)) > 1e-8
                    or abs(float(baseline.sum())-current) > 1e-8 or np.any(violations[rows, old])):
                raise AssertionError('事件起点与当前两项loss/整链cap不符')
            selected, predicted = monotone_axis.choose_axis(losses, violations, idx[axis], old)
            del losses, violations
            frac[channel, axis] = selected
            cc._refresh(points, nodes, idx, frac, model.m, targets, output, squared, channel)
            measured, bad = measure(output, targets, terminal_targets, reference, caps, suffix, mass, rho, parts)
            if (bad or abs(float(measured)-predicted) > 1e-8
                    or np.any(np.diff(idx[axis].astype(np.int64)*io.ONE+frac[channel, axis]) < 0)
                    or not np.array_equal(frac[channel, axis, [0, 255]], old[[0, 255]])):
                raise AssertionError('单通道DP应用后两项loss/cap/单调/端点不符')
            accepted = measured < current-1e-11
            if not accepted:
                frac[channel, axis] = old
                cc._refresh(points, nodes, idx, frac, model.m, targets, output, squared, channel)
            entry = {'channel': channel, 'axis': axis, 'accepted': bool(accepted),
                'before_weighted_objective': float(current), 'after_weighted_objective': float(measured) if accepted else float(current),
                'events': int(counts.sum()), 'changed_coordinates': int(np.count_nonzero(frac[channel, axis] != old)),
                'maximum_fraction_shift': int(np.max(np.abs(frac[channel, axis]-old))),
                'cap_violations': int(bad), 'prediction_error': abs(float(measured)-predicted), 'seconds': time.perf_counter()-started}
            if accepted: current = float(measured)
            report['blocks'].append(entry)
            if progress: progress(entry)
    fresh = cc._predict(points, nodes, idx, frac, model.m)
    difference = fresh.astype(np.int32)-targets.astype(np.int32)
    fresh_loss, bad = measure(fresh, targets, terminal_targets, reference, caps, suffix, mass, rho, parts)
    if (not np.array_equal(fresh, output) or not np.array_equal(np.sum(difference*difference, axis=1, dtype=np.int32), squared)
            or bad or abs(float(fresh_loss)-current) > 1e-8):
        raise AssertionError('9块结束fresh本级RGB/两项loss/整链cap缓存不符')
    candidate = cc.ChannelLut(initial.grid.copy(), initial.nodes.copy(), idx.copy(), frac.astype(np.uint32))
    cc.validate(candidate)
    report.update(after_weighted_objective=float(current), training_cap_violations=0,
        cache_recompute_mismatches=0, changed_coordinates=int(np.count_nonzero(frac != initial.channel_frac)),
        maximum_total_shift=int(np.max(np.abs(frac-initial.channel_frac.astype(np.int64)))),
        seconds=time.perf_counter()-started, scope='9块一次单调事件DP，非跨轴/输出全局最优，不是完整四级精度/原生验收')
    return candidate, report
