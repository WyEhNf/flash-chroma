"""只做完全相同九字节AABB的精确分组与计数，不导入后缀或模型。"""
from __future__ import annotations
import numpy as np


def row_keys(lower, upper, gold):
    arrays = (lower, upper, gold)
    if any(a.dtype != np.uint8 or a.ndim != 2 or a.shape[1] != 3 for a in arrays):
        raise ValueError('三个数组必须都是N×3 uint8')
    if lower.shape != upper.shape or lower.shape != gold.shape:
        raise ValueError('三个数组行数必须相等')
    span = upper.astype(np.int16) - lower.astype(np.int16)
    if np.any(span < 0) or np.any(span > 4):
        raise ValueError('RGB闭盒每轴必须1..5个值')
    return np.concatenate(arrays, axis=1)


def group_boxes(lower, upper, gold):
    keys = row_keys(lower, upper, gold)
    unique, representative, inverse, multiplicity = np.unique(
        keys, axis=0, return_index=True, return_inverse=True, return_counts=True)
    if len(keys) >= 1 << 32:
        raise OverflowError('本版完整inverse/代表仅支持uint32')
    span = upper.astype(np.int16) - lower.astype(np.int16)
    count = np.prod(span + 1, axis=1, dtype=np.int64)
    group_span = unique[:, 3:6].astype(np.int16) - unique[:, :3].astype(np.int16)
    group_count = np.prod(group_span + 1, axis=1, dtype=np.int64)
    np.testing.assert_array_equal(unique[inverse], keys)
    np.testing.assert_array_equal(keys[representative], unique)
    np.testing.assert_array_equal(count, group_count[inverse])
    np.testing.assert_array_equal(np.bincount(inverse, minlength=len(unique)), multiplicity)
    assert int(count.sum(dtype=np.int64)) == sum(int(a)*int(b) for a,b in zip(group_count, multiplicity))
    return dict(group_keys=unique, representative=representative.astype(np.uint32),
        inverse=inverse.astype(np.uint32), multiplicity=multiplicity.astype(np.uint32),
        group_state_count=group_count.astype(np.uint8), point_state_count=count.astype(np.uint8))


def geometry_totals(grouped, limit):
    if type(limit) is not int or limit < 0:
        raise ValueError('需要非负真整数门')
    logical = sum(int(v) for v in grouped['point_state_count'])
    query = sum(int(v) for v in grouped['group_state_count'])
    return dict(original_points=len(grouped['inverse']), groups=len(grouped['group_keys']),
        logical_point_states=logical, grouped_query_states=query,
        within_group_query_gate=query <= limit, query_limit=limit,
        maximum_group_states=max((int(v) for v in grouped['group_state_count']), default=0))
