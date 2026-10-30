"""穷举整数RGB球交；盒外坐标距离已大于目标半径，不能遗漏可行点。"""
from __future__ import annotations
import math
import numpy as np


def intersection(reference, radius_squared):
    reference = np.asarray(reference)
    if reference.dtype != np.uint8 or reference.ndim != 2 or reference.shape[1] != 3 or len(reference) == 0:
        raise ValueError('需要非空N×3 RGB8参考集合')
    if not isinstance(radius_squared, int) or not 0 <= radius_squared <= 3*255**2:
        raise ValueError('需要合法整数平方半径')
    radius = math.isqrt(radius_squared)
    wide = reference.astype(np.int32)
    lo = np.maximum(0, wide.max(axis=0)-radius)
    hi = np.minimum(255, wide.min(axis=0)+radius)
    count = int(np.prod(np.maximum(hi-lo+1, 0), dtype=np.int64))
    tested = 0
    for r in range(int(lo[0]), int(hi[0])+1):
        for g in range(int(lo[1]), int(hi[1])+1):
            for b in range(int(lo[2]), int(hi[2])+1):
                tested += 1
                delta = wide-np.array([r, g, b], np.int32)
                if np.all(np.sum(delta*delta, axis=1, dtype=np.int32) <= radius_squared):
                    return {'feasible': True, 'witness': [r, g, b], 'lo': lo.tolist(), 'hi': hi.tolist(),
                            'box_size': count, 'tested': tested}
    return {'feasible': False, 'witness': None, 'lo': lo.tolist(), 'hi': hi.tolist(),
            'box_size': count, 'tested': tested}
