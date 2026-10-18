"""冻结前缀下的整链尾部硬约束；独立于本级原表拟合标签。"""
from __future__ import annotations

import numpy as np
from numba import njit, prange
from . import io


@njit(cache=True, parallel=True)
def _forbidden(indices, weights, acc, lookup, targets, caps, colours, colour, channel, parts):
    """每个原始颜色独立保护；同色节点支撑互斥，故禁止位可合并。"""
    size = len(colours)
    flags = np.zeros((parts, 2, size), np.uint8)
    for part in prange(parts):
        for p in range(len(lookup)*part//parts, len(lookup)*(part+1)//parts):
            row = lookup[p]
            squared = 0
            for c in range(3):
                error = ((acc[row, c] + io.ONE//2) >> io.Q) - int(targets[p, c])
                squared += error*error
            old = ((acc[row, channel] + io.ONE//2) >> io.Q) - int(targets[p, channel])
            for vertex in range(4):
                node, weight = indices[row, vertex], weights[row, vertex]
                if weight == 0 or colours[node] != colour:
                    continue
                for direction in range(2):
                    delta = 1 if direction == 0 else -1
                    error = ((acc[row, channel] + delta*weight + io.ONE//2) >> io.Q) - int(targets[p, channel])
                    if squared + error*error - old*old > caps[p]:
                        flags[part, direction, node] = 1
                break
    return flags.sum(axis=0)


class ChainEnvelope:
    """同一末级输入可对应多个原始参考；逐个保留约束，不能按均值合并目标。"""
    def __init__(self, lookup, targets, caps, *, expected_arrivals=None, metadata=None):
        self.lookup = np.ascontiguousarray(lookup, dtype=np.int32)
        self.targets = np.ascontiguousarray(targets, dtype=np.uint8)
        self.caps = np.ascontiguousarray(caps, dtype=np.int32)
        self.expected_arrivals = expected_arrivals
        self.metadata = metadata or {}
        if (np.asarray(lookup).dtype.kind not in 'iu' or np.any(np.asarray(lookup) != self.lookup)
                or np.asarray(targets).dtype != np.uint8 or self.targets.shape != (len(self.lookup), 3)
                or np.asarray(caps).dtype.kind not in 'iu' or np.any(np.asarray(caps) != self.caps)
                or self.caps.shape != (len(self.lookup),) or not len(self.lookup)
                or np.any(self.lookup < 0) or np.any(self.caps < 0) or np.any(self.caps > 3*255**2)):
            raise ValueError('整链包络需要合法行映射、RGB8参考和整数逐色上限')

    def validate(self, points, acc):
        if np.any(self.lookup >= len(points)):
            raise ValueError('整链到达映射超出本级训练行')
        maximum_excess = 0
        for start in range(0, len(self.lookup), 1 << 18):
            rows = self.lookup[start:start+(1 << 18)]
            if (self.expected_arrivals is not None
                    and not np.array_equal(points[rows], self.expected_arrivals[start:start+len(rows)])):
                raise ValueError('整链到达颜色和本级训练行映射不同')
            error = ((acc[rows] + io.ONE//2) >> io.Q) - self.targets[start:start+len(rows)].astype(np.int32)
            squared = np.sum(error*error, axis=1, dtype=np.int32)
            maximum_excess = max(maximum_excess, int(np.max(squared-self.caps[start:start+len(rows)])))
        if maximum_excess > 0:
            raise ValueError('起点不满足冻结整链尾部包络')

    def forbidden(self, indices, weights, acc, colours, colour, channel, parts):
        return _forbidden(indices, weights, acc, self.lookup, self.targets, self.caps,
                          colours, colour, channel, parts)
