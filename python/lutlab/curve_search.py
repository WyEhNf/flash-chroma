"""Exact full-RGB error histograms for proven diagonal integer curve chains.

The proof obligation is stronger than separability: channel c must depend only
on input c. Shared axes or channel permutations must not be treated as three
independent error variables. No interpolation, rounding or input colour is
sampled after the complete source/node proof has passed.
"""
from __future__ import annotations

import numpy as np

from . import io

HISTOGRAM_SIZE = 3 * 255 ** 2 + 1
ROOTS = np.sqrt(np.arange(HISTOGRAM_SIZE, dtype=np.float64))


def target_curves(table):
    if table.shape != io.FULL_SHAPE or table.dtype != np.uint8:
        raise ValueError("target must be the complete RGB8 cube")
    points = np.arange(256)
    curves = np.asarray(table[points, points, points]).copy()
    for red in range(0, 256, 8):
        block = table[red:red+8]
        expected = (curves[red:red+8, 0, None, None], curves[None, :, None, 1], curves[None, None, :, 2])
        for channel in range(3):
            if not np.all(block[..., channel] == expected[channel]):
                raise ValueError("complete target is not diagonal-separable")
    return curves


def model_curves(model):
    io.validate_sparse(model, competition=True)
    m = model.m
    nodes = (model.nodes[:, 0, 0, 0], model.nodes[0, :, 0, 1], model.nodes[0, 0, :, 2])
    idx, frac = model.tables()
    curves = np.empty((256, 3), dtype=np.uint8)
    for channel, values in enumerate(nodes):
        shape = [1, 1, 1]
        shape[channel] = m
        if not np.all(model.nodes[..., channel] == values.reshape(shape)):
            raise ValueError("complete stored node array is not diagonal-separable")
        indices = idx[channel].astype(np.intp)
        fractions = frac[channel].astype(np.int64)
        lower = values[indices].astype(np.int64)
        upper = values[indices + 1].astype(np.int64)
        # Tetrahedral Q16 telescopes to this expression when all channel-c
        # vertices depend only on axis c; rounding is retained at every stage.
        curves[:, channel] = ((lower * io.ONE + (upper - lower) * fractions + io.ONE // 2) >> io.Q).astype(np.uint8)
    return curves


def compose(curves):
    out = np.repeat(np.arange(256, dtype=np.uint8)[:, None], 3, axis=1)
    for table in curves:
        if table.shape != (256, 3) or table.dtype != np.uint8:
            raise ValueError("invalid complete integer channel curves")
        out = np.stack([table[out[:, channel], channel] for channel in range(3)], axis=1)
    return out


def error_histogram(predicted, target):
    squared = (predicted.astype(np.int32) - target.astype(np.int32)) ** 2
    histogram = np.array([1], dtype=np.int64)
    for channel in range(3):
        counts = np.bincount(squared[:, channel]).astype(np.int64)
        histogram = np.convolve(histogram, counts)
    # Every factor sums to 256; all coefficients and partial sums are <=2^24,
    # so integer convolution cannot overflow int64. Independence follows from
    # the complete diagonal source/model proofs, not an image distribution.
    if int(histogram.sum()) != 256 ** 3 or np.any(histogram < 0) or len(histogram) > HISTOGRAM_SIZE:
        raise RuntimeError("invalid exact RGB histogram")
    return np.pad(histogram, (0, HISTOGRAM_SIZE - len(histogram)))


def statistics(histogram, threshold=2.):
    if histogram.shape != (HISTOGRAM_SIZE,) or histogram.dtype != np.int64 or int(histogram.sum()) != 256 ** 3:
        raise ValueError("requires the complete exact RGB histogram")
    n = int(histogram.sum())
    cumulative = np.cumsum(histogram)
    rank = .99 * (n - 1)
    lo, hi = int(np.floor(rank)), int(np.ceil(rank))
    low, high = ROOTS[np.searchsorted(cumulative, [lo + 1, hi + 1])]
    return {"n_colors": n, "mean": float(np.dot(ROOTS, histogram) / n),
            "rms": float(np.sqrt(np.dot(np.arange(HISTOGRAM_SIZE, dtype=np.float64), histogram) / n)),
            "p99": float(low + (high - low) * (rank - lo)), "max": float(ROOTS[np.flatnonzero(histogram)[-1]]),
            "pixels_at_or_above_threshold": int(histogram[ROOTS >= threshold].sum())}


def pareto(rows):
    names = ("mean", "max", "node_payload_bytes")
    return [row for row in rows if not any(all(other[name] <= row[name] for name in names)
            and any(other[name] < row[name] for name in names) for other in rows)]
