"""逐节点分量窄域与重新构造的完整Q16正支撑，不复用旧输入筛选。"""
from __future__ import annotations
import numpy as np
from . import channel_hotspot_support as hs


def domains(original, witness):
    for name in ('grid', 'idx', 'channel_frac'):
        np.testing.assert_array_equal(getattr(original, name), getattr(witness, name))
    if original.nodes.shape != witness.nodes.shape: raise ValueError('见证节点形状不同')
    delta = witness.nodes.reshape(-1, 3).astype(np.int64)-original.nodes.reshape(-1, 3).astype(np.int64)
    if np.any(np.abs(delta) > 2): raise ValueError('见证不在原±2域')
    lower, upper = np.minimum(delta, 0), np.maximum(delta, 0)
    return lower, upper, delta != 0


def positive_hats(model, points, active):
    indices, weights = hs.corners(model, points)
    return np.any((weights > 0)&active[indices], axis=(1, 2))


def positive_tetra(model, points, active):
    indices, weights, _ = hs.basis(model, points)
    result = np.zeros(len(points), bool)
    for channel in range(3): result |= np.any((weights[channel] > 0)&active[indices[channel], channel], axis=1)
    return result


def complete_support(model, active, maximum_node_box_rows=65536, full_domain=True):
    pieces = []; candidate_rows = 0; physical = np.flatnonzero(np.any(active, axis=1))
    for node in physical:
        points = hs.box(model, int(node), maximum_node_box_rows); candidate_rows += len(points)
        indices, weights = hs.corners(model, points)
        selected_weight = np.where((indices == node)[:, :, None], weights, 0)
        mask = np.any((selected_weight > 0)&active[node][None, None, :], axis=(1, 2))
        pieces.append(hs.key(points[mask]))
    keys = np.unique(np.concatenate(pieces)) if pieces else np.empty(0, np.uint32)
    checked = 0
    if full_domain:
        for start in range(0, 1 << 24, 65536):
            block = np.arange(start, start+65536, dtype=np.uint32)
            independently = positive_tetra(model, hs.rgb(block), active)
            lo, hi = np.searchsorted(keys, [start, start+65536]); expected = np.zeros(len(block), bool)
            expected[(keys[lo:hi]-start).astype(np.int64)] = True
            np.testing.assert_array_equal(independently, expected); checked += len(block)
    return keys, {'physical_nodes': len(physical), 'active_components': int(active.sum()),
        'local_geometry_candidate_rows': candidate_rows, 'full_domain_independent_rows': checked,
        'support_rows': len(keys), 'support_mismatches': 0, 'construction_uses_old70571_filter': False}


def endpoint_rgb(model, points, lower, upper):
    indices, weights = hs.corners(model, points); weight = weights.astype(np.uint64)
    nodes = model.nodes.reshape(-1, 3).astype(np.int64)
    low_nodes, high_nodes = nodes+lower, nodes+upper
    if np.any(low_nodes < 0) or np.any(high_nodes > 255): raise ValueError('窄域越RGB8边界')
    low_acc = np.sum(weight*low_nodes[indices].astype(np.uint64), axis=1, dtype=np.uint64)
    high_acc = np.sum(weight*high_nodes[indices].astype(np.uint64), axis=1, dtype=np.uint64)
    if np.any(low_acc > high_acc) or np.any(high_acc-low_acc > 2*65536): raise AssertionError('窄域端点/宽度不符')
    return ((low_acc+32768)>>16).astype(np.uint8), ((high_acc+32768)>>16).astype(np.uint8), low_acc, high_acc
