"""固定可分离RGB8节点与idx，解析校准单调Q16轴坐标；不扩大本轮边界。"""
from __future__ import annotations

import numpy as np
from . import io


def rounding_interval(left: int, right: int, target: int) -> tuple[int, int]:
    """返回half-up输出恰为target的整数frac闭区间，先限制到0..ONE。"""
    left, right, target = int(left), int(right), int(target)
    if not all(0 <= value <= 255 for value in (left, right, target)):
        raise ValueError("舍入区间仅接受RGB8节点和标签")
    slope = right-left
    if slope == 0:
        return (0, io.ONE) if left == target else (1, 0)
    lower = (target-left)*io.ONE-io.ONE//2
    upper = (target+1-left)*io.ONE-io.ONE//2-1
    if slope > 0:
        lo, hi = -((-lower)//slope), upper//slope
    else:
        lo, hi = -((upper)//(-slope)), (-lower)//(-slope)
    return max(0, lo), min(io.ONE, hi)


def diagonal_node_curves(model):
    """检查整个m³节点，拒绝近似可分离或通道置换的模型。"""
    io.validate_sparse(model, competition=True)
    curves = np.stack((model.nodes[:, 0, 0, 0], model.nodes[0, :, 0, 1],
                       model.nodes[0, 0, :, 2]), axis=1)
    for axis in range(3):
        shape = [1, 1, 1]
        shape[axis] = model.m
        if not np.array_equal(model.nodes[..., axis],
                              np.broadcast_to(curves[:, axis].reshape(shape), (model.m,)*3)):
            raise ValueError("本阶段只接受节点完整验证为同轴可分离的模型")
    return curves


def evaluate_curve(nodes, idx, fraction):
    n, i, f = (np.asarray(value, dtype=np.int64) for value in (nodes, idx, fraction))
    return ((n[i]*(io.ONE-f)+n[i+1]*f+io.ONE//2) >> io.Q).astype(np.uint8)


def static_bounds(idx, original, maximum_shift):
    """静态中点隔开相邻有效坐标区间，任意独立选择均非降；首尾固定。"""
    i, f = np.asarray(idx, np.int64), np.asarray(original, np.int64)
    q = i*io.ONE+f
    if np.any(np.diff(q, axis=1) < 0):
        raise ValueError("原有效坐标不单调")
    lower = np.maximum(0, f-maximum_shift)
    upper = np.minimum(io.ONE, f+maximum_shift)
    lower[:, 1:] = np.maximum(lower[:, 1:], (q[:, :-1]+q[:, 1:]+1)//2-i[:, 1:]*io.ONE)
    upper[:, :-1] = np.minimum(upper[:, :-1], (q[:, :-1]+q[:, 1:])//2-i[:, :-1]*io.ONE)
    lower[:, [0, 255]], upper[:, [0, 255]] = f[:, [0, 255]], f[:, [0, 255]]
    if (np.any(lower > f) or np.any(upper < f)
            or np.any((i*io.ONE+upper)[:, :-1] > (i*io.ONE+lower)[:, 1:])):
        raise AssertionError("静态边界没有包含原坐标或不能保证联合单调")
    return lower, upper


def calibrate(model, targets, *, maximum_shift=4096):
    """固定本轮约束下逐码最小绝对误差；不声称其他节点/网格族最优。"""
    source = np.asarray(targets)
    if (source.dtype != np.uint8 or source.shape != (256, 3)
            or not isinstance(maximum_shift, int) or isinstance(maximum_shift, bool)
            or not 0 <= maximum_shift <= io.ONE):
        raise ValueError("需要三条完整RGB8原表曲线和合法总偏移")
    nodes = diagonal_node_curves(model)
    idx, original = model.tables()
    lower, upper = static_bounds(idx, original, maximum_shift)
    wide_lower, wide_upper = static_bounds(idx, original, io.ONE)
    fraction = original.astype(np.int64).copy()
    rows, reasons = [], {}
    for axis in range(3):
        for code in range(256):
            index, before = int(idx[axis, code]), int(original[axis, code])
            a, b, target = int(nodes[index, axis]), int(nodes[index+1, axis]), int(source[code, axis])
            target_lo, target_hi = rounding_interval(a, b, target)
            lo, hi = int(lower[axis, code]), int(upper[axis, code])
            exact_lo, exact_hi = max(lo, target_lo), min(hi, target_hi)
            wide_lo = max(int(wide_lower[axis, code]), target_lo)
            wide_hi = min(int(wide_upper[axis, code]), target_hi)
            reason = None
            if target_lo > target_hi:
                reason = "fixed_nodes_or_cell_unreachable"
            elif wide_lo > wide_hi:
                reason = "fixed_endpoint" if code in (0, 255) else "static_midpoint"
            elif exact_lo > exact_hi:
                reason = "maximum_shift"
            necessary = None if wide_lo > wide_hi else max(wide_lo-before, before-wide_hi, 0)
            unconstrained_shift = (None if target_lo > target_hi else
                                   max(target_lo-before, before-target_hi, 0))
            # 合法fraction整数步进最多改变255/65536，输出不会跳过整数码值。
            out_lo = (a*(io.ONE-lo)+b*lo+io.ONE//2) >> io.Q
            out_hi = (a*(io.ONE-hi)+b*hi+io.ONE//2) >> io.Q
            reachable_target = min(max(target, min(out_lo, out_hi)), max(out_lo, out_hi))
            choice_lo, choice_hi = rounding_interval(a, b, reachable_target)
            choice_lo, choice_hi = max(lo, choice_lo), min(hi, choice_hi)
            if choice_lo > choice_hi:
                raise AssertionError("最接近可达码值却没有合法整数坐标")
            chosen = min(max(before, choice_lo), choice_hi)
            fraction[axis, code] = chosen
            after = (a*(io.ONE-chosen)+b*chosen+io.ONE//2) >> io.Q
            old_output = (a*(io.ONE-before)+b*before+io.ONE//2) >> io.Q
            if abs(after-target) > abs(old_output-target):
                raise AssertionError("区间内最小误差不应比原坐标差")
            if reason:
                reasons[reason] = reasons.get(reason, 0)+1
            rows.append({"axis": axis, "input": code, "cell": index, "left": a, "right": b,
                "target": target, "old_fraction": before, "fraction": chosen,
                "lower": lo, "upper": hi, "target_interval": [target_lo, target_hi],
                "exact_feasible": exact_lo <= exact_hi, "reason": reason,
                "minimum_shift_with_static_bounds": necessary,
                "minimum_shift_without_static_bounds": unconstrained_shift,
                "old_output": old_output, "output": after, "error": after-target})
    candidate = io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), fraction.astype(np.uint32))
    io.validate_sparse(candidate, competition=True)
    if np.any(np.diff(idx.astype(np.int64)*io.ONE+fraction, axis=1) < 0):
        raise AssertionError("最终有效坐标不单调")
    report = {"maximum_shift": maximum_shift, "code_count": 768,
        "changed_coordinates": int(np.count_nonzero(fraction != original)),
        "remaining_code_errors": sum(row["error"] != 0 for row in rows),
        "baseline_code_errors": sum(row["old_output"] != row["target"] for row in rows),
        "infeasible_reasons": reasons,
        "largest_actual_shift": int(np.abs(fraction-original.astype(np.int64)).max()),
        "all_exact": all(row["error"] == 0 for row in rows),
        "scope": "固定节点/idx、首尾、静态中点及总偏移的逐码最小误差；未改变或放宽约束；非其他网格/节点族最优",
        "rows": rows}
    return candidate, report


def cube_metrics(output_curves, source_curves):
    """独立轴误差直方图作卷积，解析得到完整RGB域统计，不映射三维模型。"""
    difference = np.asarray(output_curves, np.int64)-np.asarray(source_curves, np.int64)
    if difference.shape != (256, 3):
        raise ValueError("需要三条256码值曲线")
    hist = np.array([1], np.int64)
    for axis in range(3):
        values, counts = np.unique(difference[:, axis]**2, return_counts=True)
        updated = np.zeros(len(hist)+int(values[-1]), np.int64)
        for value, count in zip(values, counts):
            updated[int(value):int(value)+len(hist)] += hist*int(count)
        hist = updated
    n = int(hist.sum())
    if n != 256**3:
        raise AssertionError("解析完整域频数不守恒")
    root = np.sqrt(np.arange(len(hist), dtype=np.float64))
    cumulative = np.cumsum(hist)
    rank = .99*(n-1)
    lo, hi = int(np.floor(rank)), int(np.ceil(rank))
    lower, upper = root[np.searchsorted(cumulative, [lo, hi], side="right")]
    return {"n": n, "mean": float(hist@root/n),
        "rms": float(np.sqrt(hist@np.arange(len(hist), dtype=np.int64)/n)),
        "p99": float(lower+(rank-lo)*(upper-lower)),
        "max": float(root[np.flatnonzero(hist)[-1]])}


def exact_monotone(model, channels, maximum_shift=4096):
    """精确或明确回退：接受已完整验证的separable_channels结果，不重新猜测结构。

    输出通道可以置换、共享同一输入轴。先交所有通道的舍入区间，再求
    完整单调可行域；不修改节点/idx/grid/端点，不自动增加坐标偏移。
    调用者负责将channels绑定至其完整原表验证，三个曲线本身不能证明来源。
    """
    io.validate_sparse(model, competition=True)
    if (not isinstance(maximum_shift, int) or isinstance(maximum_shift, bool)
            or not 0 <= maximum_shift <= io.ONE):
        raise ValueError("最大总偏移必须为0..65536的整数")
    report = {"method": "exact_monotone_q16", "maximum_shift": maximum_shift,
              "feasible": False,
              "scope": "固定节点/idx/grid/端点和总偏移的精确单调坐标；仅原表完整验证的轴可分离结构；不可行返回None"}
    if channels is None:
        return None, {**report, "reason": "source_not_verified_axis_separable"}
    if len(channels) != 3:
        raise ValueError("需要三个已验证输出通道")
    parsed, curves = [], []
    for channel, item in enumerate(channels):
        if len(item) != 2:
            raise ValueError("每通道需要输入轴和256个RGB8标签")
        axis, values = item
        values = np.asarray(values)
        if (not isinstance(axis, (int, np.integer)) or isinstance(axis, (bool, np.bool_))
                or not 0 <= axis <= 2 or values.dtype != np.uint8 or values.shape != (256,)):
            raise ValueError("通道轴或原表曲线不合法")
        axis = int(axis)
        selection = [0, 0, 0, channel]
        selection[axis] = slice(None)
        node_curve = model.nodes[tuple(selection)].copy()
        shape = [1, 1, 1]
        shape[axis] = model.m
        if not np.array_equal(model.nodes[..., channel],
                              np.broadcast_to(node_curve.reshape(shape), (model.m,)*3)):
            return None, {**report, "reason": "node_tensor_mismatch", "channel": channel, "axis": axis}
        parsed.append((axis, values))
        curves.append(node_curve)
    report.update(channel_axes=[axis for axis, _ in parsed],
                  verified_node_values=int(model.nodes.size))
    idx, original = model.tables()
    original_fraction = original.astype(np.int64)
    q0 = idx.astype(np.int64)*io.ONE+original_fraction
    if np.any(np.diff(q0, axis=1) < 0):
        return None, {**report, "reason": "initial_coordinates_not_monotone"}
    raw_lower = np.zeros((3, 256), np.int64)
    raw_upper = np.full((3, 256), io.ONE, np.int64)
    individual = [[[] for _ in range(256)] for _ in range(3)]
    for channel, (axis, values) in enumerate(parsed):
        node_curve = curves[channel]
        for code in range(256):
            cell = int(idx[axis, code])
            lo, hi = rounding_interval(node_curve[cell], node_curve[cell+1], values[code])
            raw_lower[axis, code] = max(int(raw_lower[axis, code]), lo)
            raw_upper[axis, code] = min(int(raw_upper[axis, code]), hi)
            individual[axis][code].append({"channel": channel, "left": int(node_curve[cell]),
                "right": int(node_curve[cell+1]), "target": int(values[code]), "interval": [lo, hi]})
    lower = np.maximum(raw_lower, original_fraction-maximum_shift)
    upper = np.minimum(raw_upper, original_fraction+maximum_shift)
    # 首尾是交集，不能用赋值把已经无解的标签约束覆盖掉。
    lower[:, [0, 255]] = np.maximum(lower[:, [0, 255]], original_fraction[:, [0, 255]])
    upper[:, [0, 255]] = np.minimum(upper[:, [0, 255]], original_fraction[:, [0, 255]])
    failures = []
    for axis, code in np.argwhere(lower > upper):
        axis, code = int(axis), int(code)
        pieces = individual[axis][code]
        if any(lo > hi for lo, hi in (piece["interval"] for piece in pieces)):
            reason = "fixed_nodes_or_cell_unreachable"
        elif raw_lower[axis, code] > raw_upper[axis, code]:
            reason = "shared_axis_interval_conflict"
        elif code in (0, 255):
            reason = "frozen_endpoint"
        else:
            reason = "maximum_shift"
        failures.append({"axis": axis, "input": code, "reason": reason,
            "original_fraction": int(original_fraction[axis, code]),
            "fraction_interval": [int(lower[axis, code]), int(upper[axis, code])],
            "channel_constraints": pieces})
    if failures:
        return None, {**report, "reason": "pointwise_interval_empty", "failures": failures}
    low_q = idx.astype(np.int64)*io.ONE+lower
    high_q = idx.astype(np.int64)*io.ONE+upper
    prefix_lower = np.maximum.accumulate(low_q, axis=1)
    suffix_upper = np.minimum.accumulate(high_q[:, ::-1], axis=1)[:, ::-1]
    blockers = np.argwhere(prefix_lower > suffix_upper)
    if len(blockers):
        axis, code = map(int, blockers[0])
        left = int(np.argmax(low_q[axis, :code+1]))
        right = code+int(np.argmin(high_q[axis, code:]))
        return None, {**report, "reason": "monotonicity_conflict",
            "witness": {"axis": axis, "left_input": left, "left_minimum_q": int(low_q[axis, left]),
                        "right_input": right, "right_maximum_q": int(high_q[axis, right])},
            "pointwise_intervals_nonempty": True}
    # 三条序列q0、prefix_lower、suffix_upper均非降，逐点clamp仍非降。
    # 任意可行坐标必须在此域中，因此该解逐坐标距原坐标最近。
    q = np.minimum(np.maximum(q0, prefix_lower), suffix_upper)
    fraction = q-idx.astype(np.int64)*io.ONE
    if (np.any(np.diff(q, axis=1) < 0) or np.any(fraction < 0) or np.any(fraction > io.ONE)
            or np.any(np.abs(fraction-original_fraction) > maximum_shift)
            or not np.array_equal(fraction[:, [0, 255]], original_fraction[:, [0, 255]])):
        raise AssertionError("精确单调投影违反固定边界")
    for channel, (axis, values) in enumerate(parsed):
        predicted = evaluate_curve(curves[channel], idx[axis], fraction[axis])
        if not np.array_equal(predicted, values):
            raise AssertionError("精确单调投影没有兑现原表标签")
    candidate = io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), fraction.astype(np.uint32))
    io.validate_sparse(candidate, competition=True)
    report.update(feasible=True, reason=None, status="exact",
        changed_fractions=int(np.count_nonzero(fraction != original_fraction)),
        maximum_actual_shift=int(np.abs(fraction-original_fraction).max()),
        exact_channel_codes=3*256, endpoints_unchanged=True, effective_coordinates_monotone=True,
        selection="完整可行域内逐点最近原坐标；无近似成功或自动扩大偏移")
    return candidate, report
