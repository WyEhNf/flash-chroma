"""固定分通道几何的单次全局盒节点提议与只撤销的逐色硬cap恢复。"""
from __future__ import annotations
import time
import numpy as np
from numba import njit, prange
from scipy.optimize import minimize
from . import channel_coordinates as cc, interp, io


def design(model, points):
    """三个输出分别缓存权威四面体设计，属于离线暂存。"""
    indices = np.empty((3, len(points), 4), np.int32)
    weights = np.empty_like(indices)
    for c in range(3):
        for start in range(0, len(points), 1 << 18):
            i, w = interp.tetra_index_weights_q(points[start:start+(1 << 18)], model.idx,
                model.channel_frac[c], model.m)
            indices[c, start:start+len(i)], weights[c, start:start+len(i)] = i, w
    return indices, weights


@njit(cache=True, parallel=True)
def loss_gradient(nodes, indices, weights, targets, mass, parts):
    """连续平滑RGB范数；私有分片梯度，避免共享节点的并发写。"""
    gradients = np.zeros((parts, len(nodes), 3), np.float64)
    losses = np.zeros(parts, np.float64)
    for part in prange(parts):
        error = np.empty(3, np.float64)
        for p in range(len(targets)*part//parts, len(targets)*(part+1)//parts):
            squared = .05**2
            for c in range(3):
                value = 0.
                for v in range(4):
                    value += (weights[c, p, v]/io.ONE)*nodes[indices[c, p, v], c]
                error[c] = value-float(targets[p, c])
                squared += error[c]*error[c]
            distance = np.sqrt(squared)
            tail = max(distance-6., 0.)
            losses[part] += mass[p]*(distance+.02*tail*tail)
            factor = mass[p]*(1.+.04*tail)/distance
            for c in range(3):
                for v in range(4):
                    gradients[part, indices[c, p, v], c] += factor*error[c]*(weights[c, p, v]/io.ONE)
    return losses.sum(), gradients.sum(axis=0)


@njit(cache=True, parallel=True)
def design_output(nodes, indices, weights):
    """训练设计上的整数重算，与末尾重新排序的独立前向核对。"""
    output = np.empty((indices.shape[1], 3), np.uint8)
    for p in prange(indices.shape[1]):
        for c in range(3):
            acc = 0
            for v in range(4):
                acc += np.int64(weights[c, p, v])*np.int64(nodes[indices[c, p, v], c])
            output[p, c] = (acc+io.ONE//2) >> io.Q
    return output


@njit(cache=True, parallel=True)
def veto_support(indices, weights, changed_nodes, original, violating_rows, parts):
    """标记违规色三输出所有正权重且确实变化的节点分量；不按质量忽略色。"""
    private = np.zeros((parts, len(original), 3), np.uint8)
    for part in prange(parts):
        for t in range(len(violating_rows)*part//parts, len(violating_rows)*(part+1)//parts):
            p = violating_rows[t]
            for c in range(3):
                for v in range(4):
                    node = indices[c, p, v]
                    if weights[c, p, v] > 0 and changed_nodes[node, c] != original[node, c]:
                        private[part, node, c] = 1
    return private.sum(axis=0) > 0


def squared_error(prediction, target):
    error = prediction.astype(np.int32)-target.astype(np.int32)
    return np.sum(error*error, axis=1, dtype=np.int32)


def integer_loss(squared, mass):
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    return float(mass@(root+.02*np.maximum(root-6., 0.)**2)[squared])


def veto(model, quantized, points, targets, caps, indices, weights, *, rounds=8, parts=4, progress=None):
    """最多8轮只恢复原值；不会引入新移动或扩大cap。"""
    if rounds != 8: raise ValueError('本阶段只接受冻结8轮veto上限')
    nodes, original = quantized.reshape(-1, 3).copy(), model.nodes.reshape(-1, 3)
    entries = []
    for iteration in range(1, rounds+1):
        current = cc.ChannelLut(model.grid, nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
        output = cc.predict(current, points)
        squared = squared_error(output, targets)
        bad = np.flatnonzero(squared > caps).astype(np.int64)
        if not len(bad): break
        before = nodes != original
        restore = veto_support(indices, weights, nodes, original, bad, parts)
        if np.any(restore & ~before) or not np.any(restore):
            raise AssertionError('cap恢复必须只撤销现有变化，且有违规时必须前进')
        nodes[restore] = original[restore]
        after = nodes != original
        if np.any(after & ~before) or np.count_nonzero(after) >= np.count_nonzero(before):
            raise AssertionError('veto没有严格减少变化分量')
        entry = {'round': iteration, 'violating_colours_before': len(bad),
            'reset_node_components': int(np.count_nonzero(restore)),
            'changed_components_after': int(np.count_nonzero(after))}
        entries.append(entry)
        if progress: progress(entry)
    candidate = cc.ChannelLut(model.grid.copy(), nodes.reshape(model.nodes.shape), model.idx.copy(), model.channel_frac.copy())
    output = design_output(nodes, indices, weights)
    squared = squared_error(output, targets)
    # 再次fresh核对，不能用上一轮恢复前的缓存作最终状态。
    fresh = cc.predict(candidate, points)
    if not np.array_equal(fresh, output) or not np.array_equal(squared_error(fresh, targets), squared):
        raise AssertionError('veto后的fresh RGB8输出与平方误差不符')
    report = {'maximum_rounds': rounds, 'rounds': entries, 'cap_violations_after': int(np.count_nonzero(squared > caps)),
        'changed_node_components_after': int(np.count_nonzero(nodes != original)),
        'cache_recompute_mismatches': 0}
    return candidate, squared, report


def propose(model, points, targets, mass, *, caps, parts=4, progress=None):
    """一次固定L-BFGS-B终点，再half-up与硬cap恢复，不追加拟合。"""
    cc.validate(model)
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3 or not len(points)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(float(np.sum(mass))-1.) > 1e-10 or parts != 4
            or np.shape(caps) != (len(points),) or np.asarray(caps).dtype.kind not in 'iu'
            or np.any(caps < 0) or np.any(caps > 3*255**2)):
        raise ValueError('全局节点需要RGB8/质量1/4分片/逐色整数cap')
    started = time.perf_counter()
    initial_squared = squared_error(cc.predict(model, points), targets)
    if np.any(initial_squared > caps): raise ValueError('3e5起点已经违反冻结旧2dd cap')
    initial_integer = integer_loss(initial_squared, mass)
    indices, weights = design(model, points)
    original = model.nodes.reshape(-1, 3).astype(np.float64)
    initial_continuous, _ = loss_gradient(original, indices, weights, targets, mass, parts)
    evaluations, history = [0], []
    def function(flat):
        loss, gradient = loss_gradient(flat.reshape(-1, 3), indices, weights, targets, mass, parts)
        evaluations[0] += 1
        if not np.isfinite(loss) or not np.all(np.isfinite(gradient)): raise ValueError('连续目标/梯度非有限')
        history.append({'evaluation': evaluations[0], 'unscaled_loss': float(loss),
            'unscaled_gradient_inf': float(np.max(np.abs(gradient))), 'seconds': time.perf_counter()-started})
        if progress and (evaluations[0] == 1 or evaluations[0] % 10 == 0): progress(history[-1])
        return loss*1e6, gradient.ravel()*1e6
    result = minimize(function, original.ravel(), method='L-BFGS-B', jac=True,
        bounds=[(0., 255.)]*original.size,
        options={'maxiter': 160, 'maxfun': 500, 'maxcor': 10, 'ftol': 1e-12, 'gtol': 1e-3})
    continuous = result.x.reshape(model.nodes.shape)
    if (not np.all(np.isfinite(continuous)) or np.any(continuous < 0) or np.any(continuous > 255)
            or result.nfev > 500):
        raise AssertionError('唯一连续终点不满足盒/预算')
    quantized = np.floor(continuous+.5).astype(np.uint8)
    candidate, squared, cap_report = veto(model, quantized, points, targets, caps, indices, weights,
        parts=parts, progress=progress)
    final_integer = integer_loss(squared, mass)
    failures = []
    if cap_report['cap_violations_after']: failures.append('training_colour_caps_after_8_veto')
    if not final_integer < initial_integer-1e-12: failures.append('training_integer_rho_strict_decrease')
    if (not np.array_equal(candidate.grid, model.grid) or not np.array_equal(candidate.idx, model.idx)
            or not np.array_equal(candidate.channel_frac, model.channel_frac)):
        raise AssertionError('全局节点阶段改变冻结几何')
    report = {'before_weighted_integer_rho': initial_integer, 'after_weighted_integer_rho': final_integer,
        'initial_continuous_surrogate': float(initial_continuous), 'final_continuous_surrogate': float(result.fun/1e6),
        'optimizer': {'success': bool(result.success), 'status': int(result.status), 'message': str(result.message),
            'iterations': int(result.nit), 'function_evaluations': int(result.nfev),
            'maximum_iterations': 160, 'maximum_function_evaluations': 500,
            'projected_gradient_termination_not_guaranteed_by_budget': not bool(result.success)},
        'evaluation_history': history, 'quantized_changed_components_before_veto': int(np.count_nonzero(quantized != model.nodes)),
        'maximum_quantized_shift_before_veto': int(np.max(np.abs(quantized.astype(np.int32)-model.nodes.astype(np.int32)))),
        'veto': cap_report, 'proposal_failures': failures, 'offline_design_bytes': indices.nbytes+weights.nbytes,
        'parts': parts, 'training_rows': len(points), 'seconds': time.perf_counter()-started,
        'scope': '一个连续盒终点half-up及最多8轮只撤销cap恢复；非RGB8/加权真实rho全局最优，无部署或终验结论'}
    return candidate, continuous, report
