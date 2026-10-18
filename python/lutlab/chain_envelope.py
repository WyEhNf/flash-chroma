"""冻结前缀下的整链尾部硬约束；独立于本级原表拟合标签。"""
from __future__ import annotations

import numpy as np
from numba import njit, prange
from . import io


@njit(cache=True)
def _output(acc, row, channel, delta_weight, suffix):
    r = (acc[row, 0] + (delta_weight if channel == 0 else 0) + io.ONE//2) >> io.Q
    g = (acc[row, 1] + (delta_weight if channel == 1 else 0) + io.ONE//2) >> io.Q
    b = (acc[row, 2] + (delta_weight if channel == 2 else 0) + io.ONE//2) >> io.Q
    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        return r, g, b
    if len(suffix):
        value = suffix[(r << 16) | (g << 8) | b]
        return int(value[0]), int(value[1]), int(value[2])
    return r, g, b


@njit(cache=True, parallel=True)
def _forbidden(indices, weights, acc, lookup, targets, caps, colours, colour, channel, parts, suffix):
    """每个原始颜色独立保护；同色节点支撑互斥，故禁止位可合并。"""
    size = len(colours)
    flags = np.zeros((parts, 2, size), np.uint8)
    for part in prange(parts):
        for p in range(len(lookup)*part//parts, len(lookup)*(part+1)//parts):
            row = lookup[p]
            for vertex in range(4):
                node, weight = indices[row, vertex], weights[row, vertex]
                if weight == 0 or colours[node] != colour:
                    continue
                for direction in range(2):
                    delta = 1 if direction == 0 else -1
                    r, g, b = _output(acc, row, channel, delta*weight, suffix)
                    # 非法节点方向由拟合器另禁；这里避免其临时输出越界索引缓存。
                    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
                        flags[part, direction, node] = 1
                        continue
                    er, eg, eb = r-int(targets[p, 0]), g-int(targets[p, 1]), b-int(targets[p, 2])
                    if er*er + eg*eg + eb*eb > caps[p]:
                        flags[part, direction, node] = 1
                break
    return flags.sum(axis=0)


class ChainEnvelope:
    """同一末级输入可对应多个原始参考；逐个保留约束，不能按均值合并目标。"""
    def __init__(self, lookup, targets, caps, *, expected_arrivals=None, metadata=None, suffix=None):
        self.lookup = np.ascontiguousarray(lookup, dtype=np.int32)
        self.targets = np.ascontiguousarray(targets, dtype=np.uint8)
        self.caps = np.ascontiguousarray(caps, dtype=np.int32)
        self.expected_arrivals = expected_arrivals
        self.metadata = metadata or {}
        self.suffix = np.empty((0, 3), np.uint8) if suffix is None else np.asarray(suffix)
        if (np.asarray(lookup).dtype.kind not in 'iu' or np.any(np.asarray(lookup) != self.lookup)
                or np.asarray(targets).dtype != np.uint8 or self.targets.shape != (len(self.lookup), 3)
                or np.asarray(caps).dtype.kind not in 'iu' or np.any(np.asarray(caps) != self.caps)
                or self.caps.shape != (len(self.lookup),) or not len(self.lookup)
                or np.any(self.lookup < 0) or np.any(self.caps < 0) or np.any(self.caps > 3*255**2)):
            raise ValueError('整链包络需要合法行映射、RGB8参考和整数逐色上限')
        if self.suffix.dtype != np.uint8 or self.suffix.shape not in ((0, 3), (256**3, 3)):
            raise ValueError('固定后缀缓存必须覆盖完整RGB8输入，或为空恒等后缀')

    def validate(self, points, acc):
        if np.any(self.lookup >= len(points)):
            raise ValueError('整链到达映射超出本级训练行')
        maximum_excess = 0
        for start in range(0, len(self.lookup), 1 << 18):
            rows = self.lookup[start:start+(1 << 18)]
            if (self.expected_arrivals is not None
                    and not np.array_equal(points[rows], self.expected_arrivals[start:start+len(rows)])):
                raise ValueError('整链到达颜色和本级训练行映射不同')
            output = ((acc[rows] + io.ONE//2) >> io.Q)
            if len(self.suffix):
                keys = output.astype(np.int64)@np.array([65536, 256, 1], np.int64)
                output = self.suffix[keys].astype(np.int32)
            error = output-self.targets[start:start+len(rows)].astype(np.int32)
            squared = np.sum(error*error, axis=1, dtype=np.int32)
            maximum_excess = max(maximum_excess, int(np.max(squared-self.caps[start:start+len(rows)])))
        if maximum_excess > 0:
            raise ValueError('起点不满足冻结整链尾部包络')

    def forbidden(self, indices, weights, acc, colours, colour, channel, parts):
        return _forbidden(indices, weights, acc, self.lookup, self.targets, self.caps,
                          colours, colour, channel, parts, self.suffix)
