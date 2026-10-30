"""固定Q16设计的舍入区间连续提议；部署模型仍为RGB8节点。"""
from __future__ import annotations

import time
import numpy as np
from numba import njit, prange
from scipy.optimize import minimize
from . import io, rounded_grid


@njit(cache=True, parallel=True)
def objective(indices, weights, targets, mass, nodes, radii, half_width, epsilon,
              tail_at, tail_weight, cap_weight, parts):
    """正确RGB8标签的内部区间无主损失，软尾部/软cap不能替代整数硬验收。"""
    gradients = np.zeros((parts, len(nodes), 3), np.float64)
    values = np.zeros(parts, np.float64)
    for part in prange(parts):
        error, excess = np.empty(3, np.float64), np.empty(3, np.float64)
        for p in range(len(indices)*part//parts, len(indices)*(part+1)//parts):
            squared, outside_squared = epsilon*epsilon, epsilon*epsilon
            for channel in range(3):
                value = 0.
                for vertex in range(4):
                    value += weights[p, vertex]*nodes[indices[p, vertex], channel]/io.ONE
                e = value-float(targets[p, channel])
                u = max(abs(e)-half_width, 0.)
                error[channel], excess[channel] = e, u if e >= 0 else -u
                squared += e*e
                outside_squared += u*u
            distance, outside = np.sqrt(squared), np.sqrt(outside_squared)
            tail = max(distance-tail_at, 0.)
            cap = max(distance-radii[p], 0.)
            values[part] += mass[p]*(outside-epsilon+tail_weight*tail*tail+cap_weight*cap*cap)
            factor = (2*tail_weight*tail+2*cap_weight*cap)/distance
            for channel in range(3):
                derivative = mass[p]*(excess[channel]/outside+factor*error[channel])
                for vertex in range(4):
                    gradients[part, indices[p, vertex], channel] += weights[p, vertex]*derivative/io.ONE
    return values.sum(), gradients.sum(axis=0)


def propose(model, points, targets, mass, *, caps, iterations=240, parts=4, progress=None):
    """固定240次上限、±4节点盒与两个终态混合比例；不自动搜索权重或预算。"""
    io.validate_sparse(model, competition=True)
    if (np.asarray(points).dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3
            or np.asarray(targets).dtype != np.uint8 or targets.shape != points.shape
            or np.shape(mass) != (len(points),) or not np.all(np.isfinite(mass))
            or np.any(mass < 0) or abs(float(np.sum(mass))-1.) > 1e-10
            or np.asarray(caps).dtype.kind not in 'iu' or np.shape(caps) != (len(points),)
            or np.any(caps < 0) or np.any(caps > 3*255**2)
            or iterations != 240 or parts != 4):
        raise ValueError('本研究固定240迭代、4分片、合法RGB8/归一质量及逐色整数cap')
    started = time.perf_counter()
    indices, weights, _, initial_squared, _ = rounded_grid.prepare(model, points, targets)
    if np.any(initial_squared > caps):
        raise ValueError('起点违反冻结硬cap')
    initial = model.nodes.reshape(-1, 3).astype(np.float64)
    # 连续节点量化与最终输出舍入每通道合计最多1码值；仅解释软目标的保守半径。
    # 优化没有严格满足此半径的保证，最终逐色整数cap仍必须逐点检查。
    radii = np.maximum(np.sqrt(caps.astype(np.float64))-np.sqrt(3.), 0.)
    settings = dict(half_width=.49, epsilon=.05, tail_at=6., tail_weight=.02, cap_weight=4., parts=parts)
    evaluations, callbacks, history = 0, 0, []
    def fun(vector):
        nonlocal evaluations
        value, gradient = objective(indices, weights, targets, mass, vector.reshape(-1, 3), radii, **settings)
        evaluations += 1
        return value*1e6, gradient.ravel()*1e6
    before, _ = fun(initial.ravel())
    def callback(vector):
        nonlocal callbacks
        callbacks += 1
        if callbacks % 40 == 0:
            entry = {'iteration': callbacks, 'evaluations': evaluations, 'seconds': time.perf_counter()-started}
            history.append(entry)
            if progress:
                progress(entry)
    result = minimize(fun, initial.ravel(), jac=True, method='L-BFGS-B',
        bounds=list(zip(np.maximum(initial.ravel()-4., 0.), np.minimum(initial.ravel()+4., 255.))),
        options={'maxiter': iterations, 'maxfun': 1000, 'maxcor': 10, 'ftol': 1e-12, 'gtol': 1e-3}, callback=callback)
    after, _ = fun(result.x)
    report = {'before_objective': before/1e6, 'after_objective': after/1e6,
        'settings': settings, 'maximum_node_shift': 4., 'iterations': int(result.nit),
        'evaluations': evaluations, 'solver_success': bool(result.success), 'solver_message': str(result.message),
        'progress': history, 'candidates': {}, 'training_rows': len(points),
        'scope': '固定设计的连续舍入区间目标；非真实RGB mean；最终RGB8量化及硬cap另查，不能以软惩罚称严格可行'}
    checkpoints = []
    idx, frac = model.tables()
    for number, alpha in enumerate((.5, 1.), 1):
        continuous = initial+alpha*(result.x.reshape(-1, 3)-initial)
        nodes = np.clip(np.floor(continuous+.5), 0, 255).astype(np.uint8)
        _, squared = rounded_grid._accumulate(indices, weights, nodes, targets)
        violations = int(np.count_nonzero(squared > caps))
        candidate = io.SparseLut(model.grid.copy(), nodes.reshape(model.nodes.shape), idx.copy(), frac.copy())
        io.validate_sparse(candidate, competition=True)
        checkpoints.append((number, candidate))
        report['candidates'][str(number)] = {'alpha': alpha, 'cap_violations': violations,
            'changed_node_channels': int(np.count_nonzero(nodes != initial)),
            'maximum_squared': int(squared.max())}
    report['seconds'] = time.perf_counter()-started
    return checkpoints, report
