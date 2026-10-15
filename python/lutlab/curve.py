"""Verified axis-separable LUTs and exact integer Q16 curve fitting.

This is an offline representation reduction only: fitted curves are expanded
back into the required m^3 RGB8 node table for the ordinary tetrahedral runtime.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .io import FULL_SHAPE, ONE, Q


def separable_channels(table: np.ndarray) -> list[tuple[int, np.ndarray]] | None:
    """Prove each channel depends on one input axis by checking every LUT byte."""
    if table.shape != FULL_SHAPE or table.dtype != np.uint8:
        raise ValueError("separability requires a complete RGB8 LUT")
    channels = []
    for channel in range(3):
        for axis in (channel, *(a for a in range(3) if a != channel)):
            selection = [0, 0, 0, channel]
            selection[axis] = slice(None)
            values = table[tuple(selection)].copy()
            verified = True
            for red in range(0, 256, 16):
                expected = (values[red:red + 16, None, None] if axis == 0 else
                            values[None, :, None] if axis == 1 else values[None, None, :])
                if not np.all(table[red:red + 16, ..., channel] == expected):
                    verified = False
                    break
            if verified:
                channels.append((axis, values))
                break
        else:
            return None
    return channels


@lru_cache(maxsize=32)
def _integer_solution(values_key: bytes, index_key: bytes, fraction_key: bytes,
                      m: int, max_node_value: int):
    values = np.frombuffer(values_key, dtype=np.uint8)
    index = np.frombuffer(index_key, dtype=np.uint8)
    fraction = np.frombuffer(fraction_key, dtype="<u4")
    domain = np.arange(max_node_value + 1, dtype=np.int32)
    left, right = domain[:, None], domain[None, :]
    maxima, squared = [], []
    # Each input belongs to exactly one cell, so all 256 errors enter once.
    for cell in range(m - 1):
        largest = np.zeros((len(domain), len(domain)), dtype=np.uint8)
        total = np.zeros_like(largest, dtype=np.uint32)
        for value in np.flatnonzero(index == cell):
            f = int(fraction[value])
            prediction = (left * (ONE - f) + right * f + ONE // 2) >> Q
            error = prediction - int(values[value])
            largest = np.maximum(largest, np.abs(error).astype(np.uint8))
            total += (error * error).astype(np.uint32)
        maxima.append(largest)
        squared.append(total)
    # First solve the bottleneck problem. Keeping a single lexicographic
    # (max,sum) pair per state would be incorrect when a later max hides it.
    bound = np.zeros(len(domain), dtype=np.uint16)
    for largest in maxima:
        bound = np.min(np.maximum(bound[:, None], largest), axis=0)
    optimum = int(bound.min())
    # Then solve additive squared error subject to that GLOBAL optimal bound.
    infinity = np.int64(1 << 60)
    cost = np.zeros(len(domain), dtype=np.int64)
    parents = np.empty((m - 1, len(domain)), dtype=np.int16)
    for cell, (largest, total) in enumerate(zip(maxima, squared)):
        trials = cost[:, None] + total
        trials[largest > optimum] = infinity
        parent = np.argmin(trials, axis=0)
        parents[cell] = parent
        cost = trials[parent, np.arange(len(domain))]
    last = int(np.argmin(cost))
    best_squared = int(cost[last])
    if best_squared >= infinity:
        raise RuntimeError("integer curve optimum has no feasible path")
    nodes = np.empty(m, dtype=np.uint8)
    nodes[-1] = last
    for cell in range(m - 2, -1, -1):
        last = int(parents[cell, last])
        nodes[cell] = last
    n = nodes.astype(np.int32)
    f = fraction.astype(np.int32)
    prediction = (n[index] * (ONE - f) + n[index.astype(np.int32) + 1] * f + ONE // 2) >> Q
    error = prediction - values.astype(np.int32)
    if int(np.max(abs(error))) != optimum or int(np.sum(error * error)) != best_squared:
        raise RuntimeError("integer curve backtrace disagrees with optimal objectives")
    return nodes.tobytes(), optimum, best_squared


def fit_integer_curve(values, index, fraction, m: int, *, max_node_value: int = 255):
    """Global minimax byte error, then minimum SSE at that bound, on a fixed axis.

    All 256 source values and every integer node value in [0,max_node_value]
    participate. The small-domain option supports independent exhaustive checks;
    production fitting uses the entire RGB8 domain.
    """
    values, index, fraction = map(np.asarray, (values, index, fraction))
    if (values.shape != (256,) or values.dtype != np.uint8 or index.shape != (256,)
            or index.dtype != np.uint8 or fraction.shape != (256,) or fraction.dtype.kind not in "iu"
            or not isinstance(m, (int, np.integer)) or isinstance(m, bool) or not 2 <= m <= 256
            or np.any(index > m - 2) or np.any(fraction < 0) or np.any(fraction > ONE)
            or not isinstance(max_node_value, int) or isinstance(max_node_value, bool)
            or not 0 <= max_node_value <= 255):
        raise ValueError("invalid RGB8 curve, Q16 axis table or integer node domain")
    payload, maximum, squared = _integer_solution(values.tobytes(), index.tobytes(),
        fraction.astype("<u4").tobytes(), int(m), max_node_value)
    return np.frombuffer(payload, dtype=np.uint8).copy(), {
        "algorithm": "two_pass_integer_dynamic_programming", "certified_inputs": 256,
        "objective": "minimum max absolute byte error, then minimum SSE at that global bound",
        "node_domain": [0, max_node_value], "max_abs_error": maximum, "squared_error_sum": squared,
        "scope": "this channel and fixed serialized Q16 axis; no final-chain guarantee"}
