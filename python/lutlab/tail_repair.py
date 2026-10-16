"""颜色级整数上限与局部节点选择；只改变离线模型，不改变执行格式。"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from . import error_analysis as ea, interp, io


def clone(models):
    return [io.SparseLut(m.grid.copy(), m.nodes.copy(), *(a.copy() for a in m.tables())) for m in models]


def encode(points):
    return points.astype(np.int64) @ np.array([65536, 256, 1])


def decode(indices):
    return np.stack((indices >> 16, (indices >> 8) & 255, indices & 255), 1).astype(np.uint8)


def update_caps(caps, rgb, squared_limit):
    """相同颜色出现在多张图片时取最严上限，包含全部重复像素。"""
    if caps.shape != (256**3,) or caps.dtype != np.uint32 or not 0 <= squared_limit <= 3*255**2:
        raise ValueError("颜色上限表或RGB平方距离上限无效")
    indices = np.unique(encode(rgb))
    caps[indices] = np.minimum(caps[indices], squared_limit)


@dataclass(frozen=True, order=True)
class Move:
    stage: int
    node: int
    value: tuple[int, int, int]


class State:
    """缓存每级输入和四面体支撑；试探仅重新计算会经过被改节点的颜色。"""
    def __init__(self, models, points, truth, caps=None):
        self.models = models
        self.points, self.truth = points, truth
        self.caps = caps
        current = points
        self.inputs, self.indices, self.positive = [], [], []
        for model in models:
            self.inputs.append(current)
            indices, weights = interp.tetra_index_weights_q(current, *model.tables(), model.m)
            self.indices.append(indices)
            self.positive.append(weights > 0)
            current = ea.Operator([model])(current)
        self.prediction = current
        self.hist, self.squared = ea.histogram(current, truth)
        self.metrics = ea.hist_metrics(self.hist)

    def trial(self, move):
        rows = np.flatnonzero(np.any((self.indices[move.stage] == move.node) & self.positive[move.stage], axis=1))
        if not len(rows):
            return rows, np.empty((0, 3), np.uint8), np.empty(0, np.int32)
        node = self.models[move.stage].nodes.reshape(-1, 3)[move.node]
        old = node.copy()
        try:
            node[:] = move.value
            prediction = ea.Operator(self.models[move.stage:])(self.inputs[move.stage][rows])
        finally:
            node[:] = old
        error = prediction.astype(np.int32)-self.truth[rows].astype(np.int32)
        return rows, prediction, np.sum(error*error, axis=1, dtype=np.int32)

    def trial_metrics(self, rows, squared):
        hist = self.hist.copy()
        hist -= np.bincount(self.squared[rows], minlength=len(hist))
        hist += np.bincount(squared, minlength=len(hist))
        if np.any(hist < 0) or hist.sum() != len(self.points):
            raise AssertionError("局部替换的误差直方图不守恒")
        return ea.hist_metrics(hist)

    def loss(self, rows=None, squared=None):
        value = self.squared.copy()
        if rows is not None:
            value[rows] = squared
        excess = np.maximum(value.astype(np.int64)-self.caps.astype(np.int64), 0)
        return (int(excess.sum()), int(excess.max(initial=0)), int(np.count_nonzero(excess)))


def proposals(state, banks, focus_count):
    excess = np.maximum(state.squared.astype(np.int64)-state.caps.astype(np.int64), 0)
    focus = np.lexsort((np.arange(len(excess)), -excess))[:focus_count]
    focus = focus[excess[focus] > 0]
    result = set()
    for k, (indices, positive, bank) in enumerate(zip(state.indices, state.positive, banks)):
        nodes = np.unique(indices[focus][positive[focus]])
        for index in nodes:
            current = state.models[k].nodes.reshape(-1, 3)[index].astype(np.int32)
            for model in bank.values():
                alternative = model.nodes.reshape(-1, 3)[index].astype(np.int32)
                for numerator, denominator in ((1, 2), (1, 1)):
                    value = (current*(denominator-numerator)+alternative*numerator+denominator//2)//denominator
                    if np.array_equal(value, current):
                        continue
                    result.add(Move(k, int(index), tuple(map(int, value))))
                    for channel in range(3):
                        partial = current.copy()
                        partial[channel] = value[channel]
                        if not np.array_equal(partial, current):
                            result.add(Move(k, int(index), tuple(map(int, partial))))
    return sorted(result)


def repair(models, banks, hard, guards, limits, *, steps=32, focus_count=16):
    """有限局部搜索：先比较整数超限损失，再逐一核验固定保护门禁。

    保护上限由调用者在整个阶段开始前冻结，不能在约束分离轮次间累积放宽。
    节点值只从本级既有拟合候选及其一半混合值选择，不生成残差标签。
    """
    models = clone(models)
    log, generated, evaluated, rejected = [], 0, 0, {}
    stop = "step_limit"
    for iteration in range(steps):
        state = State(models, hard["points"], hard["truth"], hard["caps"])
        before = state.loss()
        if before[0] == 0:
            stop = "active_constraints_satisfied"
            break
        guard_states = {name: State(models, spec["points"], spec["truth"], spec.get("caps")) for name, spec in guards.items()}
        moves = proposals(state, banks, focus_count)
        generated += len(moves)
        ranked = []
        for move in moves:
            rows, _, squared = state.trial(move)
            evaluated += 1
            loss = state.loss(rows, squared)
            if loss < before:
                ranked.append((loss, move))
        accepted = None
        for loss, move in sorted(ranked):
            measurements = {}
            failures = []
            for name, sample in guard_states.items():
                rows, _, squared = sample.trial(move)
                if sample.caps is not None:
                    after_excess = np.maximum(squared.astype(np.int64)-sample.caps[rows].astype(np.int64), 0)
                    before_excess = np.maximum(sample.squared[rows].astype(np.int64)-sample.caps[rows].astype(np.int64), 0)
                    if np.any(after_excess > before_excess):
                        failures.append(name+".point_cap")
                        break
                measurements[name] = sample.trial_metrics(rows, squared)
                failures.extend(name+"."+key for key, bound in limits[name].items()
                                if measurements[name][key] > bound+1e-12)
                if failures:
                    break
            if failures:
                for key in failures:
                    rejected[key] = rejected.get(key, 0)+1
            else:
                accepted = (loss, move, measurements)
                break
        if accepted is None:
            stop = "no_guarded_improving_local_move"
            break
        loss, move, measurements = accepted
        node = models[move.stage].nodes.reshape(-1, 3)[move.node]
        previous = node.tolist()
        node[:] = move.value
        log.append({"step": iteration+1, "stage": move.stage+1, "node": move.node, "before_node": previous,
                    "after_node": list(move.value), "before_loss": before, "after_loss": loss, "guards": measurements,
                    "proposals": len(moves), "hard_improving_proposals": len(ranked)})
    return models, {"stop": stop, "accepted": log, "generated_moves": generated,
                    "hard_trials": evaluated, "guard_rejections": rejected}
