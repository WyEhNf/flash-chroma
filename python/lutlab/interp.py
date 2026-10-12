"""Interpolation models mirroring the C++ kernels.

`tetra_weights` / `tri_weights` return, for each input colour, the flat node indices and
interpolation weights actually used at runtime (they use the Q16 fraction tables, so a
least-squares fit on these weights optimises exactly what the kernel computes, up to the
final rounding).
"""
from __future__ import annotations

import numpy as np

from .io import ONE, Q, SparseLut, axis_tables


def _prep(rgb: np.ndarray, idx: np.ndarray, frac: np.ndarray, m: int):
    r, g, b = (rgb[:, a].astype(np.intp) for a in range(3))
    sr, sg, sb = m * m, m, 1
    base = idx[0][r].astype(np.int64) * sr + idx[1][g].astype(np.int64) * sg + idx[2][b].astype(np.int64)
    fr = frac[0][r].astype(np.int64)
    fg = frac[1][g].astype(np.int64)
    fb = frac[2][b].astype(np.int64)
    return base, fr, fg, fb, (sr, sg, sb)


def tetra_index_weights_q(rgb: np.ndarray, idx, frac, m: int):
    """Flat node indices (N,4) and integer Q16 weights (N,4) of the tetra kernel."""
    base, fr, fg, fb, (sr, sg, sb) = _prep(rgb, idx, frac, m)
    F = np.stack([fr, fg, fb], 1)
    S = np.array([sr, sg, sb], np.int64)
    amax = np.argmax(F, 1)
    amin = np.argmin(F, 1)
    f1 = F.max(1)
    f3 = F.min(1)
    f2 = F.sum(1) - f1 - f3
    tot = sr + sg + sb
    I = np.stack([base, base + S[amax], base + tot - S[amin], base + tot], 1)
    W = np.stack([ONE - f1, f1 - f2, f2 - f3, f3], 1)
    return I, W


def tetra_weights(rgb: np.ndarray, idx, frac, m: int):
    I, W = tetra_index_weights_q(rgb, idx, frac, m)
    return I, W.astype(np.float64) / ONE


def tri_weights(rgb: np.ndarray, idx, frac, m: int):
    base, fr, fg, fb, (sr, sg, sb) = _prep(rgb, idx, frac, m)
    x, y, z = fr / ONE, fg / ONE, fb / ONE
    I, W = [], []
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                I.append(base + dr * sr + dg * sg + db * sb)
                W.append((x if dr else 1 - x) * (y if dg else 1 - y) * (z if db else 1 - z))
    return np.stack(I, 1), np.stack(W, 1)


def apply_tetra_q16(s: SparseLut, img: np.ndarray) -> np.ndarray:
    """Bit-exact mirror of jshc::tetra_scalar."""
    idx, frac = axis_tables(s.grid)
    flat = img.reshape(-1, 3)
    I, W = tetra_index_weights_q(flat, idx, frac, s.m)
    N = s.nodes.reshape(-1, 3).astype(np.int64)
    acc = (
        W[:, 0:1] * N[I[:, 0]]
        + W[:, 1:2] * N[I[:, 1]]
        + W[:, 2:3] * N[I[:, 2]]
        + W[:, 3:4] * N[I[:, 3]]
    )
    out = ((acc + (1 << (Q - 1))) >> Q).astype(np.uint8)
    return out.reshape(img.shape)


def eval_float(nodes: np.ndarray, grid: np.ndarray, rgb: np.ndarray, kernel: str) -> np.ndarray:
    """Unrounded interpolation of float nodes (for fitting diagnostics)."""
    idx, frac = axis_tables(grid)
    m = grid.shape[1]
    fn = tetra_weights if kernel == "tetra" else tri_weights
    I, W = fn(rgb, idx, frac, m)
    N = nodes.reshape(-1, 3)
    return np.einsum("nk,nkc->nc", W, N[I])
