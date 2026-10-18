"""固定节点/idx，以单元内完整Q16状态的单调DP提出坐标更新。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit
from . import axis_calibration as ac, exact_axis, io


@njit(cache=True)
def isotonic_path(costs, forbidden, original):
    """每行一个码值，状态非降；前缀最小值实现O(行数×状态数)DP。"""
    rows, width = costs.shape
    previous = np.full(width, np.inf, np.float64)
    displacement = np.full(width, np.int64(1 << 60), np.int64)
    back = np.full((rows, width), -1, np.int32)
    for f in range(width):
        if not forbidden[0, f] and np.isfinite(costs[0, f]):
            previous[f] = costs[0, f]
            displacement[f] = abs(f-original[0])
    for row in range(1, rows):
        current = np.full(width, np.inf, np.float64)
        distances = np.full(width, np.int64(1 << 60), np.int64)
        best, best_distance, best_index = np.inf, np.int64(1 << 60), -1
        for f in range(width):
            if previous[f] < best or (previous[f] == best and displacement[f] < best_distance):
                best, best_distance, best_index = previous[f], displacement[f], f
            if best_index >= 0 and not forbidden[row, f] and np.isfinite(costs[row, f]):
                current[f] = best+costs[row, f]
                distances[f] = best_distance+abs(f-original[row])
                back[row, f] = best_index
        previous, displacement = current, distances
    best, best_distance, last = np.inf, np.int64(1 << 60), -1
    for f in range(width):
        if previous[f] < best or (previous[f] == best and displacement[f] < best_distance):
            best, best_distance, last = previous[f], displacement[f], f
    path = np.full(rows, -1, np.int64)
    if last >= 0:
        path[-1] = last
        for row in range(rows-1, 0, -1):
            path[row-1] = back[row, path[row]]
    return path, best, best_distance


def choose_axis(costs, violations, idx, original):
    """idx递增的相邻单元自动有序；只需同一idx连续段内的联合单调约束。"""
    if (costs.shape != (256, io.ONE+1) or violations.shape != costs.shape
            or idx.shape != (256,) or original.shape != (256,)
            or np.any(np.diff(idx.astype(np.int64)) < 0)):
        raise ValueError('需要完整Q16状态、非降idx及256个原坐标')
    forbidden = violations > 0
    forbidden[0] = True; forbidden[0, original[0]] = violations[0, original[0]] > 0
    forbidden[-1] = True; forbidden[-1, original[-1]] = violations[-1, original[-1]] > 0
    output, predicted = original.copy(), 0.
    starts = np.r_[0, np.flatnonzero(np.diff(idx.astype(np.int64)))+1, 256]
    for start, stop in zip(starts[:-1], starts[1:]):
        path, value, _ = isotonic_path(costs[start:stop], forbidden[start:stop], original[start:stop])
        if not np.isfinite(value) or np.any(path < 0):
            raise ValueError('当前单元没有可行单调路径；原模型本应给出可行起点')
        output[start:stop] = path
        predicted += value
    return output, predicted


def propose(model, points, targets, mass, *, caps, parts=4, progress=None):
    """固定一轮R/G/B轴更新；整个单元可选，端点固定，不称跨轴全局最优。"""
    io.validate_sparse(model, competition=True)
    if (points.dtype != np.uint8 or points.shape != (256**3, 3)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or np.shape(mass) != (len(points),) or np.any(mass < 0) or not np.all(np.isfinite(mass))
            or abs(float(np.sum(mass))-1.) > 1e-10
            or np.asarray(caps).dtype.kind not in 'iu' or np.shape(caps) != (len(points),)
            or np.any(caps < 0) or np.any(caps > 3*255**2) or parts != 4):
        raise ValueError('本轮要求canonical完整RGB8、质量1、逐色cap及4分片')
    for start in range(0, len(points), 1 << 18):
        keys = points[start:start+(1 << 18)].astype(np.int64)@np.array([65536, 256, 1], np.int64)
        if not np.array_equal(keys, np.arange(start, start+len(keys))):
            raise ValueError('全域行不是B最快原色序')
    idx, original = model.tables()
    frac = original.astype(np.int64)
    if np.any(np.diff(idx.astype(np.int64), axis=1) < 0) or np.any(np.diff(idx.astype(np.int64)*io.ONE+frac, axis=1) < 0):
        raise ValueError('起点idx与有效坐标必须非降')
    nodes = model.nodes.reshape(-1, 3)
    distance = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = distance+.02*np.maximum(distance-6., 0.)**2
    # 恒等后缀只复用事件计算器；权重0使目标恰为本级原表rho，没有目标翻倍。
    common = (points, nodes, idx, frac, model.m, targets, targets, targets, caps, points, mass, rho, 0.)
    current, violating = ac._measure(*common, parts)
    if violating:
        raise ValueError('起点不满足旧锚定逐色cap')
    report = {'before_weighted_objective': float(current), 'rounds': [],
        'scope': '固定一轮跨轴块下降；每轴单元内完整Q16状态的单调DP；事件损失float64，非无理数/跨轴全局最优证书',
        'coordinate_policy': 'idx/grid/节点/端点固定；每码frac为0..65536，只有真实非降约束，无静态中点或总偏移限制'}
    started = time.perf_counter()
    for axis in range(3):
        diff, violation_diff, baseline, counts, invalid = exact_axis.events(*common, axis,
            np.zeros(256, np.int64), np.full(256, io.ONE, np.int64),
            np.empty(0, np.int32), np.empty(0, np.int64), io.ONE+1)
        if np.any(invalid):
            raise AssertionError('完整单元事件未前进')
        losses, violations = np.cumsum(diff, axis=1), np.cumsum(violation_diff, axis=1)
        if np.any(violations < 0):
            raise AssertionError('逐色违规计数不能为负')
        old = frac[axis].copy()
        rows = np.arange(256)
        if (np.max(np.abs(losses[rows, old]-baseline)) > 1e-8
                or abs(float(baseline.sum())-current) > 1e-8 or np.any(violations[rows, old])):
            raise AssertionError('完整状态起点不同于独立整域目标/cap')
        selected, predicted = choose_axis(losses, violations, idx[axis], old)
        frac[axis] = selected
        measured, violating = ac._measure(*common, parts)
        if (violating or abs(float(measured)-predicted) > 1e-8
                or np.any(np.diff(idx[axis].astype(np.int64)*io.ONE+frac[axis]) < 0)
                or not np.array_equal(frac[axis, [0, 255]], old[[0, 255]])):
            raise AssertionError('单调DP应用后的目标/cap/有序或端点不一致')
        accepted = measured < current-1e-11
        if not accepted:
            frac[axis] = old
        entry = {'axis': axis, 'before_weighted_objective': float(current),
            'after_weighted_objective': float(measured) if accepted else float(current),
            'accepted': bool(accepted), 'events': int(counts.sum()),
            'changed_coordinates': int(np.count_nonzero(frac[axis] != old)),
            'maximum_axis_shift': int(np.max(np.abs(frac[axis]-old))),
            'cap_violations': int(violating), 'seconds': time.perf_counter()-started}
        if accepted: current = float(measured)
        report['rounds'].append(entry)
        if progress: progress(entry)
        del diff, violation_diff, losses, violations
    candidate = io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), frac.astype(np.uint32))
    io.validate_sparse(candidate, competition=True)
    report.update(after_weighted_objective=float(current), seconds=time.perf_counter()-started,
        changed_coordinates=int(np.count_nonzero(frac != original)),
        maximum_total_shift=int(np.max(np.abs(frac-original.astype(np.int64)))))
    return [(1, candidate)], report
