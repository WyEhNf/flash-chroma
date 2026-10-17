"""固定整数管线的误差归因、离散敏感性和有界优化辅助。"""
from __future__ import annotations

import itertools
import numpy as np
from numba import njit, prange

from . import fit, interp, io
from .study_kernels import pixel

ROOT_DISTANCE = np.sqrt(np.arange(3 * 255 ** 2 + 1, dtype=np.float64))


@njit(cache=True, parallel=True)
def _unrounded(rgb, nodes, idx, frac, m):
    output = np.empty((len(rgb), 3), np.float64)
    for i in prange(len(rgb)):
        output[i] = pixel(nodes, idx, frac, m, int(rgb[i, 0]), int(rgb[i, 1]), int(rgb[i, 2]), 0)
    return output


@njit(cache=True, parallel=True)
def _map_chain(rgb, nodes, indices, fractions, m, kind):
    output = np.empty_like(rgb)
    for i in prange(len(rgb)):
        r, g, b = int(rgb[i, 0]), int(rgb[i, 1]), int(rgb[i, 2])
        for stage in range(len(nodes)):
            v = pixel(nodes[stage], indices[stage], fractions[stage], m, r, g, b, kind)
            r = min(255, max(0, int(np.floor(v[0] + .5))))
            g = min(255, max(0, int(np.floor(v[1] + .5))))
            b = min(255, max(0, int(np.floor(v[2] + .5))))
        output[i, 0], output[i, 1], output[i, 2] = r, g, b
    return output


class Operator:
    """缓存只读模型参数；每一级都按 RGB8 舍入，不保留浮点中间图。"""
    def __init__(self, models, kind=0):
        self.models, self.kind = models, kind
        if not models:
            return
        if len({model.m for model in models}) != 1:
            raise ValueError("本研究固定统一 m；不隐式处理混合尺寸")
        self.m = models[0].m
        self.nodes = np.stack([model.nodes.reshape(-1, 3).astype(np.float64) for model in models])
        self.indices = np.stack([model.tables()[0].astype(np.int32) for model in models])
        self.fractions = np.stack([model.tables()[1].astype(np.float64) / io.ONE for model in models])

    def __call__(self, rgb):
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        if not self.models:
            return rgb.copy()
        return _map_chain(rgb, self.nodes, self.indices, self.fractions, self.m, self.kind)


def source_apply(table, rgb):
    return table(rgb) if callable(table) else table[rgb[:, 0], rgb[:, 1], rgb[:, 2]]


def exact_chain(tables, rgb):
    out = rgb
    for table in tables:
        out = source_apply(table, out)
    return out


def histogram(prediction, target):
    error = prediction.astype(np.int32) - target.astype(np.int32)
    squared = np.sum(error * error, axis=1, dtype=np.int32)
    return np.bincount(squared, minlength=len(ROOT_DISTANCE)).astype(np.int64), squared


def hist_metrics(hist):
    n = int(hist.sum())
    if not n:
        raise ValueError("不能汇总空颜色集合")
    cumulative = np.cumsum(hist)
    rank = .99 * (n - 1)
    lo, hi = int(np.floor(rank)), int(np.ceil(rank))
    p_lo, p_hi = np.searchsorted(cumulative, [lo, hi], side="right")
    largest = int(np.flatnonzero(hist)[-1])
    count = max(1, int(np.ceil(n * .01)))
    remaining = count
    upper = 0.
    for d2 in np.flatnonzero(hist)[::-1]:
        take = min(remaining, int(hist[d2]))
        upper += take * ROOT_DISTANCE[d2]
        remaining -= take
        if not remaining:
            break
    return {"n": n, "mean": float(hist @ ROOT_DISTANCE / n),
            "rms": float(np.sqrt(hist @ np.arange(len(hist), dtype=np.int64) / n)),
            "p99": float(ROOT_DISTANCE[p_lo] + (rank - lo) * (ROOT_DISTANCE[p_hi] - ROOT_DISTANCE[p_lo])),
            "max": float(ROOT_DISTANCE[largest]), "cvar_1pct": upper / count,
            **{f"fraction_ge_{t}": float(hist[t*t:].sum() / n) for t in (1, 2, 3, 5)}}


def metrics(prediction, target):
    return hist_metrics(histogram(prediction, target)[0])


def vector_metrics(error):
    squared = np.sum(np.asarray(error, np.float64) ** 2, axis=1)
    distance = np.sqrt(squared)
    return {"mean": float(distance.mean()), "rms": float(np.sqrt(squared.mean())),
            "p99": float(np.percentile(distance, 99)), "max": float(distance.max())}


def stage_attribution(tables, models, points):
    reference, sparse = points.copy(), points.copy()
    target = exact_chain(tables, points)
    baseline = Operator(models)(points)
    baseline_stats = metrics(baseline, target)
    records = []
    for k, (table, model) in enumerate(zip(tables, models)):
        own = source_apply(table, sparse)
        next_reference = source_apply(table, reference)
        next_sparse = Operator([model])(sparse)
        local = next_sparse.astype(np.int32) - own.astype(np.int32)
        propagated = own.astype(np.int32) - next_reference.astype(np.int32)
        total = next_sparse.astype(np.int32) - next_reference.astype(np.int32)
        if not np.array_equal(local + propagated, total):
            raise AssertionError("误差向量分解不满足逐像素恒等式")
        replaced = Operator(models[k + 1:])(own)
        replacement_stats = metrics(replaced, target)
        records.append({"stage": k + 1, "input_drift": metrics(sparse, reference),
            "local_own_lut_error": metrics(next_sparse, own), "propagated_input_error": metrics(own, next_reference),
            "total_prefix_error": metrics(next_sparse, next_reference),
            "sse_local": float(np.mean(np.sum(local.astype(np.float64) ** 2, axis=1))),
            "sse_propagated": float(np.mean(np.sum(propagated.astype(np.float64) ** 2, axis=1))),
            "sse_interaction": float(2 * np.mean(np.sum(local.astype(np.float64) * propagated, axis=1))),
            "sse_total": float(np.mean(np.sum(total.astype(np.float64) ** 2, axis=1))),
            "replace_this_stage_exact": replacement_stats,
            "replacement_gain_mean": baseline_stats["mean"] - replacement_stats["mean"],
            "replacement_gain_cvar": baseline_stats["cvar_1pct"] - replacement_stats["cvar_1pct"]})
        reference, sparse = next_reference, next_sparse
    return {"baseline": baseline_stats, "stages": records,
            "scope": "固定输入颜色；单级替换收益含交互作用，不能相加为独立贡献"}


def suffix_sensitivity(tables, labels):
    """精确后缀对当前级输出 ±1 码值的响应；参考自身跳变单独量化。"""
    anchor = exact_chain(tables, labels)
    sensitivity = np.zeros(len(labels), np.float64)
    for axis, delta in itertools.product(range(3), (-1, 1)):
        changed = labels.copy()
        changed[:, axis] = np.clip(changed[:, axis].astype(np.int16) + delta, 0, 255)
        response = exact_chain(tables, changed).astype(np.int32) - anchor.astype(np.int32)
        sensitivity = np.maximum(sensitivity, np.linalg.norm(response, axis=1))
    return sensitivity


def neighbourhood(points, limit=None):
    parts = []
    for delta in itertools.product((-1, 0, 1), repeat=3):
        parts.append(np.clip(points.astype(np.int16) + delta, 0, 255).astype(np.uint8))
    result = np.unique(np.concatenate(parts), axis=0)
    return result if limit is None else result[:limit]


def promoted(candidate, baseline):
    keys = ("mean", "rms", "p99", "max")
    return (all(candidate[key] <= baseline[key] + 1e-12 for key in keys)
            and any(candidate[key] < baseline[key] - 1e-12 for key in keys))


def weighted_refit(table, model, points, weights, H, b, diagnostics):
    weights = np.asarray(weights, np.float64)
    weights = weights * (64 ** 3 / weights.sum())
    extra_H, transpose = fit._tetra_system(points, model.grid, weights)
    labels = source_apply(table, points).astype(np.float64)
    system, rhs = H + extra_H, b + transpose @ labels
    raw = fit.solve_spd(system, rhs, model.nodes.reshape(-1, 3).astype(np.float64),
                        diagnostics=diagnostics.setdefault("solver", {}))
    nodes = fit.quantize(fit.int_refine(raw, system, rhs)).reshape(model.nodes.shape)
    diagnostics.update(targets="本级原始完整LUT在相同输入上的RGB8标签", extra_weight_mass=float(weights.sum()),
                       sample_count=len(points), raw_node_components_outside_box=int(np.count_nonzero((raw < 0) | (raw > 255))))
    return io.SparseLut(model.grid, nodes)


def rounding_diagnostics(table, model, points, raw_nodes, tri_nodes):
    labels = source_apply(table, points).astype(np.float64)
    idx, frac = model.tables()
    indices, weights = interp.tetra_weights(points, idx, frac, model.m)
    def evaluate(nodes):
        return np.sum(weights[..., None] * np.asarray(nodes).reshape(-1, 3)[indices], axis=1)
    raw = evaluate(raw_nodes)
    clipped = evaluate(np.clip(raw_nodes, 0, 255))
    integer_nodes = evaluate(model.nodes)
    rounded = Operator([model])(points).astype(np.float64)
    geometry = np.empty((3, 256), np.float64)
    for a in range(3):
        cell = idx[a].astype(np.int32)
        geometry[a] = (np.arange(256) - model.grid[a, cell]) / (model.grid[a, cell+1] - model.grid[a, cell])
    geometric_output = _unrounded(points, model.nodes.reshape(-1, 3).astype(np.float64),
                                   idx.astype(np.int32), geometry, model.m)
    # 同一组整数节点，仅改变恢复算子；另有各自匹配的三线性 LS 对照。
    same_nodes_tri = Operator([model], kind=1)(points)
    matched_tri = Operator([io.SparseLut(model.grid, fit.quantize(tri_nodes).reshape(model.nodes.shape))], kind=1)(points)
    return {"raw_float_fit_error": vector_metrics(raw - labels),
            "clipped_float_fit_error": vector_metrics(clipped - labels),
            "clipping_change": vector_metrics(clipped - raw),
            "integer_node_refinement_change": vector_metrics(integer_nodes - clipped),
            "output_rounding_change": vector_metrics(rounded - integer_nodes),
            "q16_coordinate_change": vector_metrics(integer_nodes - geometric_output),
            "same_nodes_trilinear": metrics(same_nodes_tri, labels.astype(np.uint8)),
            "matched_trilinear_ls": metrics(matched_tri, labels.astype(np.uint8)),
            "scope": "同级同输入的诊断反事实；连续输出不作为合法四级中间值，范数不能直接相加"}


def hotspot_traces(tables, models, colours, selected):
    records = []
    for colour in colours[:8]:
        reference, sparse = colour[None].copy(), colour[None].copy()
        trace = []
        for table, model in zip(tables, models):
            own = source_apply(table, sparse)
            next_reference = source_apply(table, reference)
            next_sparse = Operator([model])(sparse)
            trace.append({"reference_input": reference[0].tolist(), "sparse_input": sparse[0].tolist(),
                "own_source_at_sparse_input": own[0].tolist(), "reference_output": next_reference[0].tolist(),
                "sparse_output": next_sparse[0].tolist()})
            reference, sparse = next_reference, next_sparse
        at = np.asarray(trace[selected]["sparse_input"], np.uint8)[None]
        nearby = neighbourhood(at)
        true_delta = source_apply(tables[selected], nearby).astype(np.int32) - source_apply(tables[selected], at).astype(np.int32)
        model_delta = Operator([models[selected]])(nearby).astype(np.int32) - Operator([models[selected]])(at).astype(np.int32)
        indices, weights = interp.tetra_index_weights_q(at, *models[selected].tables(), models[selected].m)
        records.append({"initial_rgb": colour.tolist(), "stages": trace,
            "selected_stage_neighbourhood": {"reference_jump": vector_metrics(true_delta),
                "model_jump": vector_metrics(model_delta), "response_difference": vector_metrics(model_delta-true_delta)},
            "selected_cell_vertices": indices[0].tolist(), "q16_weights": weights[0].tolist(),
            "stored_nodes": models[selected].nodes.reshape(-1, 3)[indices[0]].tolist()})
    return records
