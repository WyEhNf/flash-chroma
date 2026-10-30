"""本级原表标签在固定稀疏后缀下的输出保持损失，不使用精确整链标签。"""
from __future__ import annotations

import hashlib
import math
import numpy as np
from numba import njit, prange
from . import io
from .chain_envelope import _output


@njit(cache=True, parallel=True)
def _gains(indices, weights, acc, mass, targets, suffix, colours, colour, channel, rho, parts):
    gains = np.zeros((parts, 2, len(colours)), np.float64)
    for part in prange(parts):
        for p in range(len(indices)*part//parts, len(indices)*(part+1)//parts):
            for vertex in range(4):
                node, weight = indices[p, vertex], weights[p, vertex]
                if weight == 0 or colours[node] != colour:
                    continue
                r, g, b = _output(acc, p, channel, 0, suffix)
                er, eg, eb = r-int(targets[p, 0]), g-int(targets[p, 1]), b-int(targets[p, 2])
                old_squared = er*er+eg*eg+eb*eb
                for direction in range(2):
                    delta = 1 if direction == 0 else -1
                    r, g, b = _output(acc, p, channel, delta*weight, suffix)
                    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
                        continue
                    er, eg, eb = r-int(targets[p, 0]), g-int(targets[p, 1]), b-int(targets[p, 2])
                    squared = er*er+eg*eg+eb*eb
                    gains[part, direction, node] += mass[p]*(rho[squared]-rho[old_squared])
                break
    return gains.sum(axis=0)


class SuffixObjective:
    """训练标签始终为本级原表，固定后缀同时作用于预测和同一本级标签。"""
    def __init__(self, suffix, original_targets, weight=1.):
        self.suffix = np.asarray(suffix)
        self.original_targets = np.asarray(original_targets)
        self.weight = float(weight)
        if (self.suffix.dtype != np.uint8 or self.suffix.shape != (256**3, 3)
                or self.original_targets.dtype != np.uint8 or self.original_targets.ndim != 2
                or self.original_targets.shape[1] != 3 or not len(self.original_targets)
                or not np.isfinite(self.weight) or self.weight <= 0):
            raise ValueError('后缀损失需要完整RGB8缓存、本级RGB8标签及正权重')
        value = self.original_targets.astype(np.int64)
        self.targets = self.suffix[value@np.array([65536, 256, 1], np.int64)].copy()
        self.metadata = {'weight': self.weight, 'source_target_sha256': hashlib.sha256(self.original_targets.tobytes()).hexdigest(),
            'derived_target_sha256': hashlib.sha256(self.targets.tobytes()).hexdigest(),
            'formula': 'rho(pred-Tk(z))+weight*rho(S(pred)-S(Tk(z)))',
            'scope': 'S为固定稀疏后缀，目标仅来自本级Tk(z)，没有精确最终Y(x)或残差拟合标签'}

    def validate(self, targets):
        if not np.array_equal(targets, self.original_targets):
            raise ValueError('后缀损失的标签必须与本级原表标签一致')

    def loss(self, acc, mass, rho):
        terms = []
        for start in range(0, len(acc), 1 << 18):
            stop = min(start+(1 << 18), len(acc))
            output = ((acc[start:stop]+io.ONE//2) >> io.Q).astype(np.int64)
            transformed = self.suffix[output@np.array([65536, 256, 1], np.int64)]
            error = transformed.astype(np.int32)-self.targets[start:stop].astype(np.int32)
            squared = np.sum(error*error, axis=1, dtype=np.int32)
            terms.append(float(mass[start:stop]@rho[squared]))
        return self.weight*math.fsum(terms)

    def gains(self, indices, weights, acc, mass, colours, colour, channel, rho, parts):
        return self.weight*_gains(indices, weights, acc, mass, self.targets, self.suffix,
                                 colours, colour, channel, rho, parts)
