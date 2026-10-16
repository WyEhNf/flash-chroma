"""固定候选库的四级联合选择；离线研究，不改变逐级RGB8运行时。"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from . import box, error_analysis as ea, fit, interp, io


def design(points, model):
    """直接使用权威idx/frac组装四面体设计，不从float32坐标重建。"""
    indices, weights = interp.tetra_weights(points, *model.tables(), model.m)
    matrix = sp.csr_matrix((weights.ravel(), indices.ravel(),
        np.arange(0, 4 * len(points) + 1, 4, dtype=np.int32)), shape=(len(points), model.m ** 3))
    matrix.eliminate_zeros()
    return matrix


def fit_bank(table, model, uniform_points, photo_points, *, mass=.5, lam=1e-4,
             epsilon=.5, irls_rounds=3, diagnostics=None):
    """本级原表标签：混合测度的裁剪CG、箱约束LS与平滑RGB范数IRLS。

    所有候选保留同一网格。固定正对角先验保证每次箱约束子问题严格凸；
    IRLS仅优化本级连续目标，最终四级指标仍由独立的联合选择集判定。
    """
    if not 0 < mass < 1 or lam <= 0 or epsilon <= 0 or irls_rounds < 1:
        raise ValueError("混合比例、正则项、平滑参数和轮数必须有效")
    if not len(uniform_points) or not len(photo_points):
        raise ValueError("均匀颜色与照片训练颜色均不能为空")
    report = {} if diagnostics is None else diagnostics
    points = np.concatenate((uniform_points, photo_points))
    target = ea.source_apply(table, points).astype(np.float64)
    matrix = design(points, model)
    n = len(uniform_points)
    weights = np.concatenate((np.full(n, 1-mass), np.full(len(photo_points), mass*n/len(photo_points))))
    start = model.nodes.reshape(-1, 3).astype(np.float64)

    def moments(w):
        transpose = matrix.multiply(w[:, None]).T.tocsr()
        return (transpose @ matrix).tocsr(), transpose @ target

    normal, rhs = moments(weights)
    prior = lam * (normal.diagonal() + 1.)
    system, regular_rhs = normal + sp.diags(prior), rhs + prior[:, None] * start
    raw = fit.solve_spd(normal, rhs, start, lam=lam, diagnostics=report.setdefault("clipped_solver", {}))
    bounded = box.solve_box(system, regular_rhs, np.clip(raw, 0, 255),
                            diagnostics=report.setdefault("box_solver", {}))
    # 两个整数候选在完全相同的正则化二次式上精化，隔离求解后裁剪的影响。
    values = {"mixed_clip": fit.int_refine(raw, system, regular_rhs),
              "mixed_box": fit.int_refine(bounded, system, regular_rhs)}

    def objective(x):
        residual = matrix @ x - target
        return float(weights @ np.sqrt(np.sum(residual * residual, axis=1) + epsilon**2)
                     + .5 * np.sum(prior[:, None] * (x-start)**2))

    current = bounded
    records = []
    for iteration in range(irls_rounds):
        residual = matrix @ current - target
        effective = weights / np.sqrt(np.sum(residual*residual, axis=1) + epsilon**2)
        hessian, linear = moments(effective)
        hessian = hessian + sp.diags(prior)
        linear += prior[:, None] * start
        info = {}
        candidate = box.solve_box(hessian, linear, current, diagnostics=info)
        before, after = objective(current), objective(candidate)
        if after > before + 1e-8 * max(1., abs(before)):
            raise ArithmeticError("IRLS连续平滑范数目标增大，拒绝发布候选")
        records.append({"iteration": iteration+1, "before": before, "after": after, "solver": info})
        current = candidate
    values["mixed_mean"] = fit.int_refine(current, hessian, linear)
    difference = bounded - np.clip(raw, 0, 255)
    gradient = system @ np.clip(raw, 0, 255) - regular_rhs
    report.update(target_semantics="本级原始完整LUT在本级相同输入上的RGB8值；无残差或复合标签",
        uniform_count=n, photo_count=len(photo_points), photo_mass=mass, total_mass=float(weights.sum()),
        lambda_prior=lam, prior_min=float(prior.min()), irls_epsilon=epsilon, irls=records,
        raw_components_outside_box=int(np.count_nonzero((raw < 0) | (raw > 255))),
        box_components_outside_box=int(np.count_nonzero((bounded < 0) | (bounded > 255))),
        continuous_box_vs_clamped_change=float(.5*np.sum(difference*(system@difference)) + np.sum(gradient*difference)),
        continuous_objective_scope="同一混合测度、正则化、单级、未舍入目标；不保证RGB8或四级指标",
        quantized_continuous_changes={name: float(.5*np.sum((x-start)*(system@(x+start)))
            - np.sum(regular_rhs*(x-start))) for name, x in values.items()})
    idx, frac = model.tables()
    return {name: io.SparseLut(model.grid.copy(), fit.quantize(x).reshape(model.nodes.shape),
                             idx.copy(), frac.copy()) for name, x in values.items()}


def measure(prediction, target, *, group_size=None):
    result = ea.metrics(prediction, target)
    if group_size is not None:
        if len(prediction) % group_size:
            raise ValueError("每张照片的选择像素数必须相同且完整")
        per_image = [ea.metrics(prediction[i:i+group_size], target[i:i+group_size])
                     for i in range(0, len(prediction), group_size)]
        result.update(worst_image_mean=max(r["mean"] for r in per_image),
                      worst_image_p99=max(r["p99"] for r in per_image))
    return result


def choose(records, baseline_key, measures=("uniform", "photo", "hotspot")):
    """多测度非退化门禁；按最差相对mean选择，固定元组打破完全平局。"""
    baseline = next(row for row in records if row["key"] == baseline_key)
    eligible = []
    for row in records:
        failures = []
        strict = False
        for name in measures:
            old, new = baseline["metrics"][name], row["metrics"][name]
            keys = ("mean", "rms", "p99", "max") + (("worst_image_mean", "worst_image_p99") if name == "photo" else ())
            for key in keys:
                if new[key] > old[key] + 1e-12:
                    failures.append(name+"."+key)
                strict |= new[key] < old[key] - 1e-12
        if not failures and (strict or row["key"] == baseline_key):
            eligible.append(row)
    def score(row):
        ratios = [row["metrics"][name]["mean"] / max(baseline["metrics"][name]["mean"], 1e-12)
                  for name in measures if name != "hotspot"]
        return (max(ratios), sum(ratios), sum(row["metrics"][name]["rms"] for name in measures),
                sum(i != j for i, j in zip(row["key"], baseline_key)), tuple(row["key"]))
    return {"winner": min(eligible, key=score)["key"], "eligible": [row["key"] for row in eligible],
            "measures": list(measures), "score": "最大相对mean、相对mean之和、RMS之和、改动级数、元组"}


def enumerate_bank(banks, sample_sets):
    """有限候选库精确枚举，复用公共前缀；全部末级输出仍逐级RGB8取整。"""
    operators = [{name: ea.Operator([model]) for name, model in stage.items()} for stage in banks]
    records = []
    def walk(stage, prefix, current):
        if stage == len(banks):
            records.append({"key": list(prefix), "metrics": {
                name: measure(current[name], spec["truth"], group_size=spec.get("group_size"))
                for name, spec in sample_sets.items()}})
            return
        for name, operator in operators[stage].items():
            walk(stage+1, prefix+(name,), {key: operator(value) for key, value in current.items()})
    walk(0, (), {name: spec["points"] for name, spec in sample_sets.items()})
    if len(records) != int(np.prod([len(stage) for stage in banks])):
        raise AssertionError("联合枚举记录数与候选库不符")
    return records
