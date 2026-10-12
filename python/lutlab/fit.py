"""Sparsification (fitting) methods: full 256^3 LUT -> m^3 lattice nodes.

Every method returns float nodes (m, m, m, 3); `quantize` turns them into the uint8
lattice required by the problem ("m*m*m 空间与原色彩空间变量类型一致").

Families
  naive      : sample (nearest integer sample), sample_interp (sub-pixel sample)
  classic    : box (cell averaging / low-pass)
  LS optimal : ls_sep (separable least squares for any tensor basis: hat=trilinear,
               bspline2, bspline3, lagrange3), ls_tetra (sparse LS on the exact tetra
               weights, optionally weighted), irls_tetra (Lp -> minimax), int_refine
               (integer-aware coordinate descent after rounding)
  lattice    : adaptive_grid (non-uniform knots, AdaInt-style, via per-axis curvature)
"""
from __future__ import annotations

import time
from functools import lru_cache

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .interp import tetra_weights
from .io import ONE, axis_tables, uniform_grid


# ================================================================ separable machinery
def contract(T: np.ndarray, Mr: np.ndarray, Mg: np.ndarray, Mb: np.ndarray) -> np.ndarray:
    """out[i,j,k,c] = sum_{r,g,b} Mr[i,r] Mg[j,g] Mb[k,b] T[r,g,b,c]  (float32)."""
    X = np.tensordot(Mr.astype(np.float32), T.astype(np.float32), axes=(1, 0))  # (i,g,b,c)
    X = np.tensordot(Mg.astype(np.float32), X, axes=(1, 1))                      # (j,i,b,c)
    X = np.tensordot(Mb.astype(np.float32), X, axes=(1, 2))                      # (k,j,i,c)
    return np.ascontiguousarray(X.transpose(2, 1, 0, 3))


def basis_matrix(grid_axis: np.ndarray, kind: str) -> np.ndarray:
    """B (256, m): value at input x = sum_i B[x,i] node_i along one axis."""
    m = len(grid_axis)
    B = np.zeros((256, m))
    x = np.arange(256)
    if kind == "hat":  # exactly what the Q16 kernels use
        idx, frac = axis_tables(np.stack([grid_axis] * 3))
        f = frac[0] / ONE
        B[x, idx[0]] = 1 - f
        B[x, idx[0].astype(int) + 1] += f
        return B
    h = 255.0 / (m - 1)
    t = x / h
    if kind in ("bspline2", "bspline3"):
        def b2(u):
            u = np.abs(u)
            return np.where(u < 0.5, 0.75 - u ** 2, np.where(u < 1.5, 0.5 * (1.5 - u) ** 2, 0))

        def b3(u):
            u = np.abs(u)
            return np.where(u < 1, 2 / 3 - u ** 2 + u ** 3 / 2, np.where(u < 2, (2 - u) ** 3 / 6, 0))
        fn = b2 if kind == "bspline2" else b3
        for i in range(m):
            B[:, i] = fn(t - i)
        return B
    if kind == "lagrange3":
        for xi in range(256):
            i = min(int(t[xi]), m - 2)
            s = min(max(i - 1, 0), m - 4)
            nodes = np.arange(s, s + 4)
            for a in nodes:
                w = 1.0
                for b in nodes:
                    if b != a:
                        w *= (t[xi] - b) / (a - b)
                B[xi, a] = w
        return B
    raise KeyError(kind)


def fit_ls_sep(T: np.ndarray, grid: np.ndarray, kind: str = "hat") -> np.ndarray:
    P = [np.linalg.pinv(basis_matrix(grid[a], kind)) for a in range(3)]
    return contract(T, *P)


def synth_sep(X: np.ndarray, grid: np.ndarray, kind: str) -> np.ndarray:
    """Evaluate a separable model on all 2^24 colours -> float (256,256,256,3)."""
    B = [basis_matrix(grid[a], kind) for a in range(3)]
    return contract(X, *B)


# ================================================================ naive / classic
def fit_sample(T, grid):
    i = [np.clip(np.round(grid[a]).astype(int), 0, 255) for a in range(3)]
    return T[np.ix_(i[0], i[1], i[2])].astype(np.float32)


def fit_sample_interp(T, grid):
    M = []
    for a in range(3):
        g = np.clip(grid[a], 0, 255)
        lo = np.floor(g).astype(int).clip(0, 254)
        f = g - lo
        A = np.zeros((len(g), 256))
        A[np.arange(len(g)), lo] = 1 - f
        A[np.arange(len(g)), lo + 1] += f
        M.append(A)
    return contract(T, *M)


def fit_box(T, grid):
    M = []
    x = np.arange(256)
    for a in range(3):
        g = grid[a]
        edges = np.concatenate([[-np.inf], (g[1:] + g[:-1]) / 2, [np.inf]])
        A = ((x[None, :] >= edges[:-1, None]) & (x[None, :] < edges[1:, None])).astype(float)
        empty = A.sum(1) == 0
        A[empty, np.clip(np.round(g[empty]).astype(int), 0, 255)] = 1
        M.append(A / A.sum(1, keepdims=True))
    return contract(T, *M)


# ================================================================ sparse LS (tetra)
def _cube_points(stride: int = 2) -> np.ndarray:
    v = np.round(np.linspace(0, 255, 256 // stride)).astype(np.uint8)
    return np.stack(np.meshgrid(v, v, v, indexing="ij"), -1).reshape(-1, 3)


def normal_equations(points, targets, weights, grid, chunk=1 << 20):
    """H = A^T W A (sparse), b = A^T W y for the tetra kernel."""
    idx, frac = axis_tables(grid)
    m = grid.shape[1]
    M = m ** 3
    H = sp.csr_matrix((M, M))
    b = np.zeros((M, 3))
    for s in range(0, len(points), chunk):
        P = points[s:s + chunk]
        I, W = tetra_weights(P, idx, frac, m)
        w = np.ones(len(P)) if weights is None else weights[s:s + chunk]
        Ww = W * w[:, None]
        rows = np.repeat(I, 4, axis=1).ravel()
        cols = np.tile(I, (1, 4)).ravel()
        vals = (Ww[:, :, None] * W[:, None, :]).ravel()
        H = H + sp.coo_matrix((vals, (rows, cols)), shape=(M, M)).tocsr()
        Y = targets[s:s + chunk].astype(np.float64)
        for c in range(3):
            b[:, c] += np.bincount(I.ravel(), weights=(Ww * Y[:, c:c + 1]).ravel(), minlength=M)
    return H, b


def solve_spd(H, b, x0=None, lam=1e-6, tol=1e-8):
    """(H + lam*D) x = b + lam*D*x0, D = diag(H)+1 keeps unsupported nodes at x0."""
    M = H.shape[0]
    d = H.diagonal()
    D = d + 1.0
    if x0 is None:
        x0 = np.zeros((M, 3))
    A = (H + sp.diags(lam * D)).tocsr()
    Pinv = sp.diags(1.0 / (d + lam * D))
    out = np.empty((M, 3))
    for c in range(3):
        rhs = b[:, c] + lam * D * x0[:, c]
        out[:, c], info = spla.cg(A, rhs, x0=x0[:, c], rtol=tol, maxiter=500, M=Pinv)
    return out


@lru_cache(maxsize=16)
def _full_cube_H(grid_key: bytes, m: int, stride: int):
    grid = np.frombuffer(grid_key).reshape(3, m)
    pts = _cube_points(stride)
    H, _ = normal_equations(pts, np.zeros((len(pts), 3), np.uint8), None, grid)
    return H


def fit_ls_tetra(T, grid, stride: int = 2, x0=None, lam=1e-6):
    """Uniform-weight LS over the RGB cube (H depends only on the grid -> cached)."""
    m = grid.shape[1]
    H = _full_cube_H(np.ascontiguousarray(grid, np.float64).tobytes(), m, stride)
    pts = _cube_points(stride)
    v = np.round(np.linspace(0, 255, 256 // stride)).astype(np.intp)
    Y = T[np.ix_(v, v, v)].reshape(-1, 3)
    idx, frac = axis_tables(grid)
    M = m ** 3
    b = np.zeros((M, 3))
    for s in range(0, len(pts), 1 << 21):
        I, W = tetra_weights(pts[s:s + (1 << 21)], idx, frac, m)
        Yc = Y[s:s + (1 << 21)].astype(np.float64)
        for c in range(3):
            b[:, c] += np.bincount(I.ravel(), weights=(W * Yc[:, c:c + 1]).ravel(), minlength=M)
    if x0 is None:
        x0 = fit_ls_sep(T, grid, "hat").reshape(-1, 3)
    return solve_spd(H, b, x0.reshape(-1, 3), lam).reshape(m, m, m, 3), H, b


def fit_weighted_tetra(points, targets, weights, grid, x0, lam=1e-3):
    """Weighted LS (e.g. image histogram or stage-input distribution)."""
    H, b = normal_equations(points, targets, weights.astype(np.float64), grid)
    m = grid.shape[1]
    return solve_spd(H, b, x0.reshape(-1, 3), lam).reshape(m, m, m, 3), H, b


def fit_irls_tetra(T, grid, p=6.0, iters=4, stride=4, x0=None):
    """Iteratively reweighted LS approximating the L_p (-> L_inf) norm of the error."""
    m = grid.shape[1]
    pts = _cube_points(stride)
    v = np.round(np.linspace(0, 255, 256 // stride)).astype(np.intp)
    Y = T[np.ix_(v, v, v)].reshape(-1, 3).astype(np.float64)
    idx, frac = axis_tables(grid)
    I, W = tetra_weights(pts, idx, frac, m)
    x = (fit_ls_sep(T, grid, "hat") if x0 is None else x0).reshape(-1, 3).astype(np.float64)
    w = np.ones(len(pts))
    for it in range(iters):
        H, b = normal_equations(pts, Y, w, grid)
        x = solve_spd(H, b, x, 1e-6)
        err = np.linalg.norm(np.einsum("nk,nkc->nc", W, x[I]) - Y, axis=1)
        q = 2 + (p - 2) * (it + 1) / iters  # anneal the exponent
        w = np.maximum(err, 0.25) ** (q - 2)
        w /= w.mean()
    return x.reshape(m, m, m, 3)


# ================================================================ integer refinement
def int_refine(x_float: np.ndarray, H, b, sweeps: int = 4) -> np.ndarray:
    """Coordinate descent on the integer lattice for 0.5*x^T H x - b^T x.

    Nodes are 8-coloured by index parity so that same-colour nodes never share a
    tetrahedron (H_jk = 0) and can be updated simultaneously.
    """
    m = round(x_float.shape[0] ** (1 / 3)) if x_float.ndim == 2 else x_float.shape[0]
    x = np.clip(np.round(x_float.reshape(-1, 3)), 0, 255)
    ii, jj, kk = np.meshgrid(*(np.arange(m),) * 3, indexing="ij")
    color = ((ii % 2) * 4 + (jj % 2) * 2 + (kk % 2)).ravel()
    d = H.diagonal()
    for _ in range(sweeps):
        changed = 0
        for col in range(8):
            sel = color == col
            g = H @ x - b                       # gradient of 0.5 x^T H x - b^T x
            for delta in (1.0, -1.0):
                gain = delta * g[sel] + 0.5 * d[sel, None]   # objective change
                ok = (gain < -1e-12) & (x[sel] + delta >= 0) & (x[sel] + delta <= 255)
                xs = x[sel]
                xs[ok] += delta
                x[sel] = xs
                changed += int(ok.sum())
                g = H @ x - b
        if changed == 0:
            break
    return x


# ================================================================ adaptive grid
def adaptive_grid(T: np.ndarray, m: int, alpha: float = 0.5, expo: float = 0.4) -> np.ndarray:
    """Per-axis knot placement equidistributing |d2 T/dx2|^expo (mixed with uniform)."""
    Tf = T.astype(np.float32)
    grid = np.empty((3, m))
    for a in range(3):
        d2 = np.abs(np.diff(Tf, n=2, axis=a))
        other = tuple(i for i in range(4) if i != a)
        prof = d2.mean(axis=other)
        prof = np.concatenate([[prof[0]], prof, [prof[-1]]])  # back to 256
        dens = prof ** expo
        dens = alpha * dens / dens.mean() + (1 - alpha)
        cdf = np.concatenate([[0], np.cumsum((dens[1:] + dens[:-1]) / 2)])
        cdf /= cdf[-1]
        grid[a] = np.interp(np.linspace(0, 1, m), cdf, np.arange(256.0))
        grid[a][0], grid[a][-1] = 0.0, 255.0
        # enforce a minimum spacing so every cell keeps some support
        for i in range(1, m):
            grid[a][i] = max(grid[a][i], grid[a][i - 1] + 2.0)
        grid[a] = np.minimum(grid[a], 255.0 - 2.0 * (m - 1 - np.arange(m)))
    return grid


# ================================================================ helpers
def quantize(x: np.ndarray) -> np.ndarray:
    return np.clip(np.floor(np.asarray(x, np.float64) + 0.5), 0, 255).astype(np.uint8)


def fit(T: np.ndarray, m: int, method: str, grid: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, dict]:
    """Dispatch by name. Returns (uint8 nodes, grid, info)."""
    t0 = time.perf_counter()
    grid = uniform_grid(m) if grid is None else grid
    info: dict = {}
    if method == "sample":
        x = fit_sample(T, grid)
    elif method == "sample_interp":
        x = fit_sample_interp(T, grid)
    elif method == "box":
        x = fit_box(T, grid)
    elif method == "ls_tri":
        x = fit_ls_sep(T, grid, "hat")
    elif method == "ls_tetra":
        x, _, _ = fit_ls_tetra(T, grid)
    elif method == "ls_tetra_int":
        x, H, b = fit_ls_tetra(T, grid)
        x = int_refine(x, H, b)
    elif method == "irls_tetra":
        x = fit_irls_tetra(T, grid)
    else:
        raise KeyError(method)
    info["fit_s"] = round(time.perf_counter() - t0, 3)
    return quantize(x.reshape(m, m, m, 3)), grid, info
