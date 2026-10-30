"""首级整数AABB的固定offset枚举；只输出完整安全/危险统计。"""
from __future__ import annotations
import itertools
import numpy as np
from . import channel_hotspot_support as hs


def enumerate_stats(lower, upper, gold, lookup):
    if (lower.shape != upper.shape or lower.shape != gold.shape or lower.dtype != np.uint8 or
            upper.dtype != np.uint8 or np.any(upper < lower) or np.any(upper.astype(np.int16)-lower > 4)):
        raise ValueError('需要RGB8且每轴不超过5项的有序AABB')
    minimum = np.full(len(lower), 3*255**2+1, np.int32)
    maximum = np.zeros(len(lower), np.int32); count = np.zeros(len(lower), np.uint8); safe = np.zeros(len(lower), np.uint8)
    span = upper.astype(np.int16)-lower
    for offset in itertools.product(range(5), repeat=3):
        use = np.all(span >= np.array(offset, np.int16), axis=1); rows = np.flatnonzero(use)
        if not len(rows): continue
        rgb = (lower[rows].astype(np.int16)+offset).astype(np.uint8)
        output = lookup(rgb); delta = output.astype(np.int32)-gold[rows].astype(np.int32)
        square = np.sum(delta*delta, axis=1, dtype=np.int32)
        minimum[rows] = np.minimum(minimum[rows], square); maximum[rows] = np.maximum(maximum[rows], square)
        count[rows] += 1; safe[rows] += (square <= 49).astype(np.uint8)
    expected = np.prod(span+1, axis=1, dtype=np.int32)
    np.testing.assert_array_equal(count.astype(np.int32), expected)
    return minimum, maximum, count, safe


def collect_allowed(lower, upper, gold, lookup):
    rows_parts, rgb_parts = [], []; span = upper.astype(np.int16)-lower
    for offset in itertools.product(range(5), repeat=3):
        rows = np.flatnonzero(np.all(span >= np.array(offset, np.int16), axis=1))
        if not len(rows): continue
        rgb = (lower[rows].astype(np.int16)+offset).astype(np.uint8)
        delta = lookup(rgb).astype(np.int32)-gold[rows].astype(np.int32)
        good = np.sum(delta*delta, axis=1, dtype=np.int32) <= 49
        rows_parts.append(rows[good].astype(np.uint32)); rgb_parts.append(rgb[good])
    rows = np.concatenate(rows_parts) if rows_parts else np.empty(0, np.uint32)
    rgb = np.concatenate(rgb_parts) if rgb_parts else np.empty((0, 3), np.uint8)
    order = np.lexsort((hs.key(rgb), rows)); rows, rgb = rows[order], rgb[order]
    counts = np.bincount(rows, minlength=len(lower)); offsets = np.r_[0, np.cumsum(counts, dtype=np.int64)]
    return offsets, rgb
