"""全域局部重放与整数平方根均值证书；仅用于离线模型选择。"""
from __future__ import annotations

import hashlib
import itertools
import math
from functools import lru_cache

import numpy as np
from numba import njit

from . import error_analysis as ea, interp, tail_repair as tr


@lru_cache(maxsize=1)
def root_bounds():
    """L/2^24 <= sqrt(d²) <= U/2^24，平方检验完全使用Python整数。"""
    lower = np.array([math.isqrt(d << 48) for d in range(3*255**2+1)], np.int64)
    upper = lower + np.array([int(int(x)**2 != d << 48) for d,x in enumerate(lower)], np.int64)
    return lower, upper


def summary(hist):
    hist = np.asarray(hist)
    if hist.shape != (3*255**2+1,) or hist.dtype.kind not in "iu" or np.any(hist < 0):
        raise ValueError("证书需要非负整数RGB平方误差直方图")
    support = np.flatnonzero(hist)
    n = sum(int(hist[d]) for d in support)
    if not n:
        raise ValueError("证书不接受空颜色域")
    lo, hi = root_bounds()
    lower = sum(int(hist[d])*int(lo[d]) for d in support)
    upper = sum(int(hist[d])*int(hi[d]) for d in support)
    position, fraction = divmod(99*(n-1), 100)
    count, quantiles = 0, []
    for d in support:
        count += int(hist[d])
        if not quantiles and count > position:
            quantiles.append(int(d))
        if count > position + int(fraction > 0):
            quantiles.append(int(d))
            break
    return {"n": n, "precision_bits": 24, "sum_lower_q24": str(lower), "sum_upper_q24": str(upper),
        "mean_lower": lower/(n*(1 << 24)), "mean_upper": upper/(n*(1 << 24)),
        "sum_squared_error": str(sum(int(d)*int(hist[d]) for d in support)),
        "p99_squared_endpoints": quantiles, "p99_high_weight_percent": fraction,
        "max_squared_error": int(support[-1]), "histogram": [[int(d),int(hist[d])] for d in support]}


def certify(reference, candidate, numerator=1005, denominator=1000):
    """保守地证明mean预算与非增RMS/p99/max；相等分位端点直接比较。"""
    if (reference["n"] != candidate["n"] or not isinstance(numerator, int)
            or not isinstance(denominator, int) or denominator <= 0 or numerator < denominator):
        raise ValueError("全域证书颜色数或预算无效")
    failures = []
    if int(candidate["sum_upper_q24"])*denominator > int(reference["sum_lower_q24"])*numerator:
        failures.append("mean")
    if int(candidate["sum_squared_error"]) > int(reference["sum_squared_error"]):
        failures.append("rms")
    old, new = reference["p99_squared_endpoints"], candidate["p99_squared_endpoints"]
    if not all(a <= b for a,b in zip(new,old)):
        lo, hi = root_bounds()
        t = reference["p99_high_weight_percent"]
        if (100-t)*int(hi[new[0]])+t*int(hi[new[1]]) > (100-t)*int(lo[old[0]])+t*int(lo[old[1]]):
            failures.append("p99")
    if candidate["max_squared_error"] > reference["max_squared_error"]:
        failures.append("max")
    return {"accepted": not failures, "failed": failures, "mean_ratio": [numerator, denominator],
            "candidate": candidate, "scope": "已保存有限域直方图的整数上下界证书；输入覆盖与模型绑定另由全域执行核验"}


@njit(cache=True)
def cell_inverse(rgb, idx, m):
    """按输入立方体作稳定计数倒排，避免缓存每色四个顶点/权重。"""
    width = m-1
    counts = np.zeros(width**3, np.int64)
    for i in range(len(rgb)):
        key = (int(idx[0,rgb[i,0]])*width+int(idx[1,rgb[i,1]]))*width+int(idx[2,rgb[i,2]])
        counts[key] += 1
    offsets = np.empty(len(counts)+1, np.int64)
    offsets[0] = 0
    for i in range(len(counts)):
        offsets[i+1] = offsets[i]+counts[i]
    cursor = offsets[:-1].copy()
    positions = np.empty(len(rgb), np.int32)
    for i in range(len(rgb)):
        key = (int(idx[0,rgb[i,0]])*width+int(idx[1,rgb[i,1]]))*width+int(idx[2,rgb[i,2]])
        positions[cursor[key]] = i
        cursor[key] += 1
    return offsets, positions


def signature(models):
    h = hashlib.sha256()
    for model in models:
        h.update(model.m.to_bytes(4, "little"))
        h.update(model.nodes.tobytes())
        for table in model.tables():
            h.update(table.tobytes())
    return h.hexdigest()


class DomainGuard:
    """全颜色前缀、立方体倒排和误差直方图；保护参考在所有步之间固定。"""
    def __init__(self, models, points, truth, *, numerator=1005, denominator=1000, max_cache_bytes=1536 << 20):
        if points.dtype != np.uint8 or truth.dtype != np.uint8 or points.shape != truth.shape or points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("全域保护要求相同形状的RGB8颜色和参考")
        if not len(points) or len(points) > np.iinfo(np.int32).max:
            raise ValueError("倒排颜色数量必须在int32正范围内")
        estimate = len(points)*(7*len(models)+10)+2*len(ea.ROOT_DISTANCE)*8
        if estimate > max_cache_bytes:
            raise MemoryError("离线全域缓存估算超过冻结预算")
        self.truth, self.points = truth, points
        self.numerator, self.denominator = numerator, denominator
        self.inputs, self.inverse = [], []
        current = points
        for model in models:
            self.inputs.append(current)
            self.inverse.append(cell_inverse(current, model.tables()[0], model.m))
            current = ea.Operator([model])(current)
        self.prediction = current
        self.hist, self.squared = ea.histogram(current, truth)
        self.reference = summary(self.hist)
        self.model_signature = signature(models)
        self.records, self._pending = [], None
        self.cache_bytes = sum(a.nbytes for a in [truth, *self.inputs, self.prediction, self.squared, self.hist]
                               + [a for inverse in self.inverse for a in inverse])
        if self.cache_bytes > max_cache_bytes:
            raise MemoryError("离线全域缓存实际数组大小超过冻结预算")

    def affected(self, models, move):
        model = models[move.stage]
        m, width = model.m, model.m-1
        coordinates = (move.node//(m*m), (move.node//m)%m, move.node%m)
        offsets, positions = self.inverse[move.stage]
        parts = []
        choices = [[c for c in (value-1,value) if 0 <= c < width] for value in coordinates]
        for r,g,b in itertools.product(*choices):
            cell = (r*width+g)*width+b
            parts.append(positions[offsets[cell]:offsets[cell+1]])
        rows = np.concatenate(parts) if parts else np.empty(0,np.int32)
        indices, weights = interp.tetra_index_weights_q(self.inputs[move.stage][rows], *model.tables(), m)
        return rows[np.any((indices == move.node) & (weights > 0), axis=1)]

    def trial(self, models, move):
        if signature(models) != self.model_signature:
            raise ValueError("全域前缀与当前模型不同，拒绝使用陈旧倒排")
        rows = self.affected(models, move)
        node = models[move.stage].nodes.reshape(-1,3)[move.node]
        old = node.copy()
        updates = []
        current = self.inputs[move.stage][rows]
        try:
            node[:] = move.value
            for k in range(move.stage,len(models)):
                current = ea.Operator([models[k]])(current)
                if k+1 < len(models):
                    updates.append((k+1,current))
            expected_signature = signature(models)
        finally:
            node[:] = old
        delta = current.astype(np.int32)-self.truth[rows].astype(np.int32)
        squared = np.sum(delta*delta,axis=1,dtype=np.int32)
        hist = self.hist.copy()
        hist -= np.bincount(self.squared[rows],minlength=len(hist))
        hist += np.bincount(squared,minlength=len(hist))
        if np.any(hist < 0) or sum(map(int,hist)) != len(self.points):
            raise AssertionError("全域增量直方图不守恒")
        return {"rows": rows, "updates": updates, "prediction": current, "squared": squared,
                "hist": hist, "signature": expected_signature, "move": move}

    def consider(self, models, move):
        self._pending = None
        trial = self.trial(models,move)
        proof = certify(self.reference,summary(trial["hist"]),self.numerator,self.denominator)
        proof.update(stage=move.stage+1,node=move.node,value=list(move.value),
            affected_colours=len(trial["rows"]), changed_final_colours=int(np.count_nonzero(np.any(
                trial["prediction"] != self.prediction[trial["rows"]],axis=1))))
        self.records.append(proof)
        if proof["accepted"]:
            self._pending = trial
        return proof

    def commit(self, models, move):
        pending = self._pending
        if pending is None or pending["move"] != move or signature(models) != pending["signature"]:
            raise ValueError("全域试探回执与待提交模型不匹配")
        rows = pending["rows"]
        for stage,values in pending["updates"]:
            if not np.array_equal(self.inputs[stage][rows],values):
                self.inputs[stage][rows] = values
                self.inverse[stage] = cell_inverse(self.inputs[stage],models[stage].tables()[0],models[stage].m)
        self.prediction[rows] = pending["prediction"]
        self.squared[rows] = pending["squared"]
        self.hist = pending["hist"]
        if not np.array_equal(self.hist,np.bincount(self.squared,minlength=len(self.hist))):
            raise AssertionError("提交后全域直方图与逐色平方误差不同")
        self.model_signature = pending["signature"]
        self._pending = None

    def report(self):
        final = summary(self.hist)
        return {"reference": self.reference, "final": final,
            "certificate": certify(self.reference,final,self.numerator,self.denominator),
            "checks": self.records, "cache_array_bytes": self.cache_bytes,
            "model_signature": self.model_signature,
            "prediction_sha256": hashlib.sha256(self.prediction.tobytes()).hexdigest(),
            "reference_sha256": hashlib.sha256(self.truth.tobytes()).hexdigest()}
