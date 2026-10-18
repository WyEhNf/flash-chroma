"""三维网格和RGB节点的联合连续提议；最终模型仍用Q16与RGB8验收。"""
from __future__ import annotations

import hashlib
import time

import numpy as np
from numba import njit, prange
from scipy.optimize import Bounds, minimize

from . import interp, io


@njit(cache=True, parallel=True)
def _objective(points, targets, mass, nodes, grid, epsilon, tail_at, tail_weight, parts):
    """显式分片私有梯度，避免共享节点上的并行写冲突。"""
    m = grid.shape[1]
    size = nodes.size + grid.size
    gradients = np.zeros((parts, size), np.float64)
    values = np.zeros(parts, np.float64)
    indices = np.empty((3, 256), np.int32)
    fractions = np.empty((3, 256), np.float64)
    widths = np.empty((3, 256), np.float64)
    for axis in range(3):
        cell = 0
        for x in range(256):
            while cell < m - 2 and x >= grid[axis, cell + 1]:
                cell += 1
            width = grid[axis, cell + 1] - grid[axis, cell]
            indices[axis, x] = cell
            fractions[axis, x] = (x - grid[axis, cell]) / width
            widths[axis, x] = width
    strides = (m * m, m, 1)
    for part in prange(parts):
        grad = gradients[part]
        cells = np.empty(3, np.int32)
        f = np.empty(3, np.float64)
        order = np.empty(3, np.int32)
        ids = np.empty(4, np.int32)
        w = np.empty(4, np.float64)
        error = np.empty(3, np.float64)
        for p in range(len(points) * part // parts, len(points) * (part + 1) // parts):
            for axis in range(3):
                x = int(points[p, axis])
                cells[axis] = indices[axis, x]
                f[axis] = fractions[axis, x]
                order[axis] = axis
            if f[order[0]] < f[order[1]]:
                order[0], order[1] = order[1], order[0]
            if f[order[1]] < f[order[2]]:
                order[1], order[2] = order[2], order[1]
            if f[order[0]] < f[order[1]]:
                order[0], order[1] = order[1], order[0]
            base = (cells[0] * m + cells[1]) * m + cells[2]
            ids[0] = base
            for j in range(3):
                ids[j + 1] = ids[j] + strides[order[j]]
            w[0], w[1] = 1. - f[order[0]], f[order[0]] - f[order[1]]
            w[2], w[3] = f[order[1]] - f[order[2]], f[order[2]]
            d2 = epsilon * epsilon
            for c in range(3):
                value = 0.
                for j in range(4):
                    value += w[j] * nodes[ids[j], c]
                error[c] = value - float(targets[p, c])
                d2 += error[c] * error[c]
            norm = np.sqrt(d2)
            excess = max(norm - tail_at, 0.)
            values[part] += mass[p] * (norm - epsilon + tail_weight * excess * excess)
            factor = mass[p] * (1. + 2. * tail_weight * excess) / norm
            for c in range(3):
                error[c] *= factor
                for j in range(4):
                    grad[3 * ids[j] + c] += w[j] * error[c]
            for j in range(3):
                axis = order[j]
                derivative = 0.
                for c in range(3):
                    derivative += error[c] * (nodes[ids[j + 1], c] - nodes[ids[j], c])
                x = int(points[p, axis])
                derivative /= widths[axis, x]
                offset = nodes.size + axis * m + cells[axis]
                grad[offset] -= (1. - f[axis]) * derivative
                grad[offset + 1] -= f[axis] * derivative
    return values.sum(), gradients.sum(axis=0)


def objective(points, targets, mass, nodes, grid, *, epsilon=.25, tail_at=6., tail_weight=.02, parts=4):
    """连续提议目标的值和解析梯度；不声称它等于舍入后的mean。"""
    return _objective(points, targets, mass, np.ascontiguousarray(nodes.reshape(-1, 3), dtype=np.float64),
                      np.ascontiguousarray(grid, dtype=np.float64), epsilon, tail_at, tail_weight, parts)


def quantized_model(nodes, grid, *, tables=None):
    """新网格先冻结float32，再生成权威表，避免存储坐标与运行时设计混杂。"""
    grid = np.asarray(grid, dtype=np.float32).astype(np.float64)
    nodes = np.clip(np.floor(np.asarray(nodes) + .5), 0, 255).astype(np.uint8)
    model = io.SparseLut(grid, nodes.reshape((grid.shape[1],) * 3 + (3,)))
    model.idx, model.frac = io.axis_tables(grid) if tables is None else tuple(v.copy() for v in tables)
    io.validate_sparse(model, competition=True)
    return model


def model_digest(model):
    """训练检查点的参数身份；序列化文件另记文件SHA。"""
    h = hashlib.sha256()
    for a in (model.grid.astype('<f4'), *model.tables(), model.nodes):
        h.update(a.tobytes())
    return h.hexdigest()


def grid_from_logits(logits, minimum_step=.5):
    """归一化正间隔覆盖0..255，允许全局重分配，端点与顺序由构造保证。"""
    logits = np.asarray(logits, dtype=np.float64)
    exponent = np.exp(logits - logits.max(axis=1, keepdims=True))
    shares = exponent / exponent.sum(axis=1, keepdims=True)
    free = 255. - minimum_step * logits.shape[1]
    if free <= 0:
        raise ValueError('最小步长不足以容纳网格')
    widths = minimum_step + free * shares
    grid = np.concatenate((np.zeros((3, 1)), np.cumsum(widths, axis=1)), axis=1)
    grid[:, -1] = 255.
    return grid


def spacing_gradient(grid_gradient, logits, minimum_step=.5):
    """网格位置梯度经归一化间隔的链式法则转换到logits。"""
    exponent = np.exp(logits - logits.max(axis=1, keepdims=True))
    shares = exponent / exponent.sum(axis=1, keepdims=True)
    cumulative = np.concatenate((np.zeros((3, 1)), np.cumsum(shares, axis=1)), axis=1)
    suffix = np.cumsum(grid_gradient[:, ::-1], axis=1)[:, ::-1][:, 1:]
    common = np.sum(grid_gradient * cumulative, axis=1, keepdims=True)
    return (255. - minimum_step * logits.shape[1]) * shares * (suffix - common)


def propose(model, points, targets, mass, *, move_grid, iterations=400, checkpoint_every=50,
            spacing_factor=4., minimum_step=.5, epsilon=.25, tail_at=6., tail_weight=.02, parts=4, progress=None):
    """固定预算的联合提议，保留全部预定检查点，之后统一做独立选型。"""
    points, targets = np.asarray(points), np.asarray(targets)
    mass = np.ascontiguousarray(mass, dtype=np.float64)
    if (points.dtype != np.uint8 or points.ndim != 2 or points.shape[1] != 3
            or targets.dtype != np.uint8 or targets.shape != points.shape or mass.shape != (len(points),)
            or not len(points) or not np.all(np.isfinite(mass)) or np.any(mass < 0)
            or abs(mass.sum() - 1.) > 1e-10 or not 0 < epsilon or tail_at <= 0 or tail_weight < 0
            or not 1 < spacing_factor or not 0 < minimum_step or iterations < 1 or checkpoint_every < 1 or not 1 <= parts <= 32):
        raise ValueError("联合拟合需要合法RGB8、总质量1及正的预算/平滑参数")
    io.validate_sparse(model, competition=True)
    initial_grid = np.array(model.grid, dtype=np.float64, copy=True)
    if not all(np.array_equal(a, b) for a, b in zip(io.axis_tables(initial_grid), model.tables())):
        raise ValueError("必须恢复与原权威表完全一致的离线小数网格，不能从float32偷偷重建")
    if np.any(initial_grid[:, 0] != 0) or np.any(initial_grid[:, -1] != 255):
        raise ValueError("本实验固定端点0/255")
    initial_nodes = model.nodes.reshape(-1, 3).astype(np.float64)
    # 按原设计的节点质量预条件，只影响优化坐标，不改变目标或加入先验。
    ids, w = interp.tetra_weights(points, *model.tables(), model.m)
    diagonal = np.bincount(ids.ravel(), weights=(mass[:, None] * w * w).ravel(), minlength=model.m**3)
    node_scale = np.repeat(np.clip(1. / np.sqrt(np.maximum(diagonal, 1e-8)), 10., 1000.), 3)
    gap = np.diff(initial_grid, axis=1)
    if np.any(gap <= minimum_step):
        raise ValueError('原网格间隔必须大于指定最小步长')
    initial_logits = np.log(gap - minimum_step)
    scale = np.concatenate((node_scale, np.ones(initial_logits.size)))
    initial = np.concatenate((initial_nodes.ravel(), initial_logits.ravel()))
    movement = np.log(spacing_factor) if move_grid else 0.
    lower = np.concatenate((np.zeros(initial_nodes.size), (initial_logits - movement).ravel()))
    upper = np.concatenate((np.full(initial_nodes.size, 255.), (initial_logits + movement).ravel()))
    bounds = Bounds((lower - initial) / scale, (upper - initial) / scale)
    evaluations, history, checkpoints = 0, [], []
    started = time.perf_counter()

    def physical(z):
        value = initial + z * scale
        logits = value[initial_nodes.size:].reshape(initial_logits.shape)
        grid = grid_from_logits(logits, minimum_step) if move_grid else initial_grid
        return value[:initial_nodes.size].reshape(-1, 3), grid

    def function(z):
        nonlocal evaluations
        nodes, grid = physical(z)
        value, gradient = objective(points, targets, mass, nodes, grid,
            epsilon=epsilon, tail_at=tail_at, tail_weight=tail_weight, parts=parts)
        evaluations += 1
        if not np.isfinite(value) or not np.all(np.isfinite(gradient)):
            raise FloatingPointError("联合拟合出现非有限目标/梯度")
        logits = (initial + z * scale)[initial_nodes.size:].reshape(initial_logits.shape)
        axis_gradient = spacing_gradient(gradient[initial_nodes.size:].reshape(initial_grid.shape), logits, minimum_step)
        if not move_grid:
            axis_gradient.fill(0.)
        transformed = np.concatenate((gradient[:initial_nodes.size], axis_gradient.ravel()))
        return value, transformed * scale

    def retain(z, iteration):
        nodes, grid = physical(z)
        # 固定轴对照必须保留原Q16表；只对确实改轴的方案生成新表。
        candidate = quantized_model(nodes, grid, tables=None if move_grid else model.tables())
        checkpoints.append((iteration, candidate))

    def callback(z):
        iteration = len(history) + 1
        value, gradient = function(z)
        history.append({"iteration": iteration, "continuous_objective": float(value),
                        "gradient_inf": float(np.max(abs(gradient))), "seconds": time.perf_counter() - started})
        if iteration % checkpoint_every == 0:
            retain(z, iteration)
            if progress:
                progress(history[-1])

    initial_value, _ = function(np.zeros_like(initial))
    result = minimize(function, np.zeros_like(initial), jac=True, method='L-BFGS-B', bounds=bounds,
        callback=callback, options={"maxiter": iterations, "maxcor": 15, "maxls": 40,
                                    "gtol": 1e-6, "ftol": 1e-12})
    retain(result.x, int(result.nit))
    nodes, grid = physical(result.x)
    if (not np.all(np.isfinite(result.x)) or np.any(nodes < -1e-8) or np.any(nodes > 255 + 1e-8)
            or np.any(np.diff(grid, axis=1) <= 0) or result.fun > initial_value + 1e-9):
        raise RuntimeError("联合提议未通过有限值、合法边界或目标非退化检查")
    distinct = {}
    for iteration, candidate in checkpoints:
        distinct.setdefault(model_digest(candidate), (iteration, candidate))
    report = {"move_grid": bool(move_grid), "initial_continuous_objective": float(initial_value),
        "final_continuous_objective": float(result.fun), "optimizer_success": bool(result.success),
        "optimizer_status": int(result.status), "iterations": int(result.nit), "function_evaluations": evaluations,
        "optimizer_message": str(result.message), "seconds": time.perf_counter() - started,
        "max_grid_displacement": float(np.max(abs(grid - initial_grid))), "history": history,
        "grid_parameterization": "归一化正间隔，端点0/255；log自由间隔相对初值有限箱，非固定节点位置小箱",
        "minimum_step": minimum_step, "unnormalized_spacing_factor_bound": spacing_factor,
        "unique_quantized_checkpoints": len(distinct), "prior": 0.,
        "scope": "有界非凸连续目标的有限预算提议；迭代上限不是收敛证书，需另验真实Q16/RGB8及完整域"}
    return list(distinct.values()), report
