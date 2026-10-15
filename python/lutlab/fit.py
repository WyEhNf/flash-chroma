"""Sparsification (fitting) methods: full 256^3 LUT -> m^3 lattice nodes.

Every method returns float nodes (m, m, m, 3); `quantize` turns them into the uint8
lattice required by the problem ("m*m*m 空间与原色彩空间变量类型一致").

Families
  naive      : sample (nearest integer sample), sample_interp (sub-pixel sample)
  classic    : box (cell averaging / low-pass)
  LS optimal : ls_sep (separable least squares for any tensor basis: hat=trilinear,
               bspline2, bspline3, lagrange3), ls_tetra (sparse LS on the exact tetra
               weights, optionally weighted), irls_tetra (Lp -> minimax), int_refine
               (integer-node descent on the unrounded LS objective), q16_refine
               (coordinate descent on the actual rounded RGB distance)
  lattice    : adaptive_grid (non-uniform knots, AdaInt-style, via per-axis curvature)
"""
from __future__ import annotations

import time
from functools import lru_cache

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .interp import apply_tetra_q16, tetra_index_weights_q, tetra_weights
from .io import ONE, Q, SparseLut, axis_tables, uniform_grid


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
def _cube_points(stride: int = 4) -> np.ndarray:
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


class FitConvergenceError(RuntimeError):
    """A failed solve must not replace an existing fitted model."""

    def __init__(self, message: str, diagnostics: dict):
        super().__init__(message)
        self.diagnostics = diagnostics


def solve_spd(H, b, x0=None, lam=1e-4, tol=1e-7, *, maxiter=300, diagnostics=None):
    """Solve the regularised system, recording and checking every CG result.

    (H + lam*D) x = b + lam*D*x0, D = diag(H)+1 keeps unsupported nodes at x0.
    Failure raises before a caller can publish a partially solved RGB model.
    """
    report = {} if diagnostics is None else diagnostics
    report.update({"solver": "jacobi_cg", "lambda": float(lam), "rtol": float(tol),
                   "maxiter": int(maxiter), "channels": [], "status": "running"})
    M = H.shape[0]
    d = H.diagonal()
    D = d + 1.0
    if x0 is None:
        x0 = np.zeros((M, 3))
    if (H.shape != (M, M) or np.shape(b) != (M, 3) or np.shape(x0) != (M, 3)
            or not np.isfinite(lam) or lam <= 0 or not np.isfinite(tol) or tol <= 0
            or maxiter < 1 or not np.all(np.isfinite(H.data))
            or not np.all(np.isfinite(b)) or not np.all(np.isfinite(x0))
            or np.any(d < 0)):
        report["status"] = "invalid_input"
        raise FitConvergenceError("invalid/non-finite regularised least-squares system", report)
    A = (H + sp.diags(lam * D)).tocsr()
    Pinv = sp.diags(1.0 / (d + lam * D))
    out = np.empty((M, 3))
    for c in range(3):
        rhs = b[:, c] + lam * D * x0[:, c]
        iterations = 0

        def count_iteration(_):
            nonlocal iterations
            iterations += 1

        out[:, c], info = spla.cg(A, rhs, x0=x0[:, c], rtol=tol, maxiter=maxiter,
                                  M=Pinv, callback=count_iteration)
        finite = bool(np.all(np.isfinite(out[:, c])))
        rhs_norm = float(np.linalg.norm(rhs))
        residual = float(np.linalg.norm(A @ out[:, c] - rhs)) if finite else None
        relative = residual / max(rhs_norm, np.finfo(float).tiny) if finite else None
        converged = info == 0 and finite and relative <= max(10 * tol, 1e-12)
        report["channels"].append({"channel": c, "info": int(info), "iterations": iterations,
                                   "residual_l2": residual, "relative_residual": relative,
                                   "finite": finite, "converged": bool(converged)})
        if not converged:
            report["status"] = "failed"
            raise FitConvergenceError(f"CG failed for channel {c}: info={info}, "
                                      f"relative_residual={relative}", report)
    report["status"] = "converged"
    return out


@lru_cache(maxsize=16)
def _full_cube_H(grid_key: bytes, m: int, stride: int):
    grid = np.frombuffer(grid_key).reshape(3, m)
    pts = _cube_points(stride)
    H, _ = normal_equations(pts, np.zeros((len(pts), 3), np.uint8), None, grid)
    return H


def fit_ls_tetra(T, grid, stride: int = 4, x0=None, lam=1e-4, *, diagnostics=None):
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
    return solve_spd(H, b, x0.reshape(-1, 3), lam,
                     diagnostics=diagnostics).reshape(m, m, m, 3), H, b


def fit_weighted_tetra(points, targets, weights, grid, x0, lam=1e-3, *, diagnostics=None):
    """Weighted LS (e.g. image histogram or stage-input distribution)."""
    H, b = normal_equations(points, targets, weights.astype(np.float64), grid)
    m = grid.shape[1]
    return solve_spd(H, b, x0.reshape(-1, 3), lam,
                     diagnostics=diagnostics).reshape(m, m, m, 3), H, b


def fit_irls_tetra(T, grid, p=6.0, iters=4, stride=4, x0=None, *, diagnostics=None):
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
        report = {}
        x = solve_spd(H, b, x, 1e-6, diagnostics=report)
        if diagnostics is not None:
            diagnostics.setdefault("iterations", []).append(report)
        err = np.linalg.norm(np.einsum("nk,nkc->nc", W, x[I]) - Y, axis=1)
        q = 2 + (p - 2) * (it + 1) / iters  # anneal the exponent
        w = np.maximum(err, 0.25) ** (q - 2)
        w /= w.mean()
    return x.reshape(m, m, m, 3)


def fit_tail_tetra(T, grid, stride=4, beta=2.0, *, diagnostics=None):
    """Reweight high-error cube samples after a first exact-kernel LS fit.

    Capped weights avoid fitting a tiny set of discontinuities at the expense of
    the entire cube. The final choice still belongs to the strict validator.
    """
    report = {} if diagnostics is None else diagnostics
    x0, _, _ = fit_ls_tetra(T, grid, stride=stride, diagnostics=report.setdefault("pilot", {}))
    pts = _cube_points(stride)
    v = np.round(np.linspace(0, 255, 256 // stride)).astype(np.intp)
    target = T[np.ix_(v, v, v)].reshape(-1, 3)
    idx, frac = axis_tables(grid)
    I, W = tetra_weights(pts, idx, frac, grid.shape[1])
    pred = np.einsum("nk,nkc->nc", W, x0.reshape(-1, 3)[I])
    err = np.linalg.norm(pred - target, axis=1)
    scale = max(float(np.percentile(err, 90)), 0.25)
    weights = np.minimum(1.0 + beta * (err / scale) ** 2, 16.0)
    x, H, b = fit_weighted_tetra(pts, target, weights, grid, x0,
                               diagnostics=report.setdefault("weighted", {}))
    return int_refine(x, H, b)


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
            # Same-colour off-diagonals are zero. A successful +1 move makes
            # the reverse -1 move non-improving, so both directions can be
            # decided from one gradient instead of three full sparse products.
            xs = x[sel]
            plus = (g[sel] + 0.5 * d[sel, None] < -1e-12) & (xs < 255)
            minus = (-g[sel] + 0.5 * d[sel, None] < -1e-12) & (xs > 0)
            xs += plus.astype(np.int8) - minus.astype(np.int8)
            x[sel] = xs
            changed += int(plus.sum() + minus.sum())
        if changed == 0:
            break
    return x


def _rgb_error_stats(pred: np.ndarray, target: np.ndarray) -> dict:
    error = pred.astype(np.int32) - target.astype(np.int32)
    squared = np.sum(error * error, axis=1)
    distance = np.sqrt(squared)
    return {"mean": float(distance.mean()), "rms": float(np.sqrt(squared.mean())),
            "p99": float(np.percentile(distance, 99)), "max": float(distance.max())}


def q16_refine(nodes: np.ndarray, points: np.ndarray, targets: np.ndarray, grid: np.ndarray,
               sweeps: int = 3, *, guard_points=None, guard_targets=None,
               diagnostics=None) -> np.ndarray:
    """Refine integer nodes using *rounded* RGB distance, preserving an incumbent.

    Each tetrahedron has at most one node of each index-parity colour. Thus,
    within a colour and output channel, ±1 proposals affect disjoint sets of
    samples: exact changes in sum ΔE can be binned per node and accepted in a
    batch. Output channels are processed sequentially because Euclidean RGB
    distance couples them. Integer accumulators include exactly the runtime
    Q16 weights and half-up rounding; no differentiable surrogate is accepted.

    A completed sweep is kept only if mean improves and sample RMS/p99/max do
    not worsen, both on fitting points and on optional independent guard
    points. Otherwise the entire sweep is rolled back and refinement stops.
    These are sampled safeguards, not an all-colour or four-stage guarantee.
    """
    m = grid.shape[1]
    if (np.size(nodes) != m ** 3 * 3 or np.asarray(nodes).dtype != np.uint8
            or np.asarray(points).dtype != np.uint8 or np.asarray(targets).dtype != np.uint8
            or np.shape(points) != np.shape(targets) or np.ndim(points) != 2
            or np.shape(points)[1] != 3 or len(points) == 0 or sweeps < 0):
        raise ValueError("q16_refine needs uint8 nodes and nonempty matching (N,3) RGB samples")
    if (guard_points is None) != (guard_targets is None):
        raise ValueError("guard_points and guard_targets must be supplied together")
    if guard_points is not None and (np.asarray(guard_points).dtype != np.uint8
            or np.asarray(guard_targets).dtype != np.uint8
            or np.shape(guard_points) != np.shape(guard_targets)
            or np.ndim(guard_points) != 2 or np.shape(guard_points)[1] != 3
            or len(guard_points) == 0):
        raise ValueError("guard data must be matching nonempty uint8 (N,3) RGB samples")

    started = time.perf_counter()
    report = {} if diagnostics is None else diagnostics
    report.update({"objective": "mean_rgb_euclidean_after_q16_half_up", "sweeps": [],
                   "training_points": len(points),
                   "guard_points": 0 if guard_points is None else len(guard_points),
                   "sample_guards": ["mean", "rms", "p99", "max"],
                   "acceptance_scope": "single_stage_sample_sets"})
    I, W = tetra_index_weights_q(points, *axis_tables(grid), m)
    x = nodes.reshape(-1, 3).astype(np.int32)
    y = targets.astype(np.int32)
    # 255 * 65536 fits in int32, as does the sum of three squared byte errors.
    acc = np.sum(W[..., None] * x[I], axis=1, dtype=np.int32)
    pred = (acc + ONE // 2) >> Q
    error = pred - y
    squared = np.sum(error * error, axis=1, dtype=np.int32)
    root = np.sqrt(np.arange(3 * 255 ** 2 + 1, dtype=np.float64))
    current = _rgb_error_stats(pred, y)
    guard_current = None
    if guard_points is not None:
        guard_current = _rgb_error_stats(apply_tetra_q16(
            SparseLut(grid, x.astype(np.uint8).reshape(m, m, m, 3)), guard_points), guard_targets)
    report["before"] = {"training": current.copy(), "guard": guard_current}

    ii, jj, kk = np.meshgrid(*(np.arange(m),) * 3, indexing="ij")
    colour = ((ii % 2) * 4 + (jj % 2) * 2 + kk % 2).ravel()
    # Retain only nonzero support. Every row appears at most once per colour,
    # even on tied fractions where runtime vertex choices are immaterial.
    support = []
    for c in range(8):
        row, vertex = np.nonzero((colour[I] == c) & (W > 0))
        support.append((row, I[row, vertex], W[row, vertex]))
    M = len(x)
    stop = "sweep_limit"
    for sweep in range(sweeps):
        previous_x = x.copy()
        changed = 0
        max_squared = int(squared.max())
        for row, node, weight in support:
            if not len(row):
                continue
            for channel in range(3):
                old_error = error[row, channel]
                old_squared = squared[row]
                old_distance = root[old_squared]
                changes = []
                for delta in (1, -1):
                    new_pred = np.clip((acc[row, channel] + delta * weight + ONE // 2) >> Q, 0, 255)
                    new_error = new_pred - y[row, channel]
                    new_squared = old_squared + new_error ** 2 - old_error ** 2
                    gain = np.bincount(node, weights=root[new_squared] - old_distance, minlength=M)
                    violates_max = np.bincount(node, weights=new_squared > max_squared, minlength=M) > 0
                    invalid = ((x[:, channel] + delta < 0) | (x[:, channel] + delta > 255)
                               | violates_max)
                    gain[invalid] = np.inf
                    changes.append(gain)
                plus, minus = changes
                move = np.where((plus < -1e-12) & (plus <= minus), 1,
                                np.where(minus < -1e-12, -1, 0)).astype(np.int32)
                changed += int(np.count_nonzero(move))
                x[:, channel] += move
                acc[row, channel] += move[node] * weight
                new_error = ((acc[row, channel] + ONE // 2) >> Q) - y[row, channel]
                squared[row] = old_squared + new_error ** 2 - old_error ** 2
                error[row, channel] = new_error
        if changed == 0:
            stop = "coordinate_optimum"
            break
        candidate = _rgb_error_stats((acc + ONE // 2) >> Q, y)
        guard_candidate = None
        if guard_points is not None:
            guard_candidate = _rgb_error_stats(apply_tetra_q16(
                SparseLut(grid, x.astype(np.uint8).reshape(m, m, m, 3)), guard_points), guard_targets)

        def no_regression(after, before):
            return all(after[key] <= before[key] + 1e-12 for key in ("mean", "rms", "p99", "max"))

        accepted = (candidate["mean"] < current["mean"] - 1e-12
                    and no_regression(candidate, current)
                    and (guard_current is None or no_regression(guard_candidate, guard_current)))
        report["sweeps"].append({"sweep": sweep + 1, "changed_coordinates": changed,
                                 "training": candidate, "guard": guard_candidate,
                                 "accepted": bool(accepted)})
        if not accepted:
            x = previous_x
            stop = "sample_guard_rollback"
            break
        current, guard_current = candidate, guard_candidate
    report.update({"after": {"training": current, "guard": guard_current},
                   "stop_reason": stop, "refine_s": round(time.perf_counter() - started, 6),
                   "accepted_sweeps": sum(s["accepted"] for s in report["sweeps"])})
    return x.astype(np.uint8).reshape(m, m, m, 3)


def _q16_guard_points(stride=4, count=1 << 16, seed=0x513136):
    """Fixed random guard inputs disjoint from the tensor fitting subgrid."""
    axis = np.round(np.linspace(0, 255, 256 // stride)).astype(np.uint8)
    if len(axis) == 256:
        return None  # full-cube fitting leaves no unseen input colours
    in_axis = np.zeros(256, dtype=bool)
    in_axis[axis] = True
    rng = np.random.default_rng(seed)
    parts, left = [], count
    while left:
        draw = rng.integers(0, 256, (left + 1024, 3), dtype=np.uint8)
        draw = draw[~np.all(in_axis[draw], axis=1)][:left]
        parts.append(draw)
        left -= len(draw)
    return np.concatenate(parts)


def fit_q16_tetra(T, grid, stride=4, sweeps=3, *, diagnostics=None):
    """Preserve the old LS integer model unless exact-Q16 sampled guards improve."""
    report = {} if diagnostics is None else diagnostics
    x, H, b = fit_ls_tetra(T, grid, stride=stride, diagnostics=report.setdefault("solver", {}))
    m = grid.shape[1]
    incumbent = quantize(int_refine(x, H, b).reshape(m, m, m, 3))
    points = _cube_points(stride)
    targets = T[points[:, 0], points[:, 1], points[:, 2]]
    # Fixed independent input colours, never an evaluation-image histogram.
    seed = 0x513136
    guard = _q16_guard_points(stride, seed=seed)
    guard_targets = None if guard is None else T[guard[:, 0], guard[:, 1], guard[:, 2]]
    detail = report.setdefault("q16_refine", {})
    detail["guard_seed"] = seed
    return q16_refine(incumbent, points, targets, grid, sweeps,
                      guard_points=guard, guard_targets=guard_targets, diagnostics=detail)


# R18 experimental paths are separate from the frozen R17 defaults.
@lru_cache(maxsize=2)
def stratified_points(seed: int = 0x533138) -> np.ndarray:
    """One fixed jittered colour per 4x4x4 input block, without image statistics."""
    cells = np.stack(np.meshgrid(*(np.arange(64, dtype=np.uint16) * 4,) * 3,
                                indexing="ij"), -1).reshape(-1, 3)
    offset = np.random.default_rng(seed).integers(0, 4, cells.shape, dtype=np.uint8)
    points = (cells + offset).astype(np.uint8)
    points.flags.writeable = False
    return points


def guard_points_excluding(points, count=1 << 16, seed=0x473138):
    """Reproducible guard colours disjoint from a supplied fitting point set."""
    def keys(p):
        return (p[:, 0].astype(np.int32) << 16) | (p[:, 1].astype(np.int32) << 8) | p[:, 2]

    excluded = np.unique(keys(points))
    if len(excluded) == 1 << 24:
        return None
    rng = np.random.default_rng(seed)
    parts, left = [], count
    while left:
        draw = rng.integers(0, 256, (left + 1024, 3), dtype=np.uint8)
        key = keys(draw)
        pos = np.searchsorted(excluded, key)
        present = (pos < len(excluded)) & (excluded[np.minimum(pos, len(excluded) - 1)] == key)
        draw = draw[~present][:left]
        parts.append(draw)
        left -= len(draw)
    return np.concatenate(parts)


@lru_cache(maxsize=4)
def _stratified_H(grid_key: bytes, m: int, seed: int):
    grid = np.frombuffer(grid_key).reshape(3, m)
    points = stratified_points(seed)
    H, _ = normal_equations(points, np.zeros((len(points), 3), np.uint8), None, grid)
    return H


def fit_stratified_tetra(T, grid, seed=0x533138, *, diagnostics=None):
    """Exact tetrahedral LS with equal-volume jittered, rather than tensor, samples."""
    points = stratified_points(seed)
    target = T[points[:, 0], points[:, 1], points[:, 2]]
    m = grid.shape[1]
    H = _stratified_H(np.ascontiguousarray(grid, np.float64).tobytes(), m, seed)
    I, W = tetra_weights(points, *axis_tables(grid), m)
    b = np.empty((m ** 3, 3))
    for channel in range(3):
        b[:, channel] = np.bincount(I.ravel(), weights=(W * target[:, channel, None]).ravel(),
                                    minlength=m ** 3)
    x0 = fit_ls_sep(T, grid, "hat").reshape(-1, 3)
    report = {} if diagnostics is None else diagnostics
    report.update({"sample_scheme": "one_jittered_point_per_4x4x4_block", "sample_seed": seed,
                   "sample_count": len(points)})
    x = solve_spd(H, b, x0, diagnostics=report.setdefault("solver", {}))
    return x.reshape(m, m, m, 3), H, b


def q16_refine_guarded(nodes, points, targets, grid, sweeps=3, *, guard_points=None,
                        guard_targets=None, diagnostics=None):
    """R18: accept local Q16 moves only when *both* sample sets cannot regress.

    Besides each set's sum ΔE and squared error, constrain counts above both
    order-statistic thresholds used by NumPy's linearly interpolated p99. This
    ensures p99 cannot increase, unlike constraining only one approximate tail
    threshold. Within one parity colour, sample supports remain disjoint.

    The guard is an optimisation/selection set, not unseen test data. No claim
    of full-cube or final-chain monotonicity follows from these local contracts.
    """
    m = grid.shape[1]
    if (np.asarray(nodes).dtype != np.uint8 or np.size(nodes) != m ** 3 * 3
            or sweeps < 0 or len(points) == 0):
        raise ValueError("invalid guarded Q16 refinement inputs")
    if (guard_points is None) != (guard_targets is None):
        raise ValueError("guard points and targets must be supplied together")
    started = time.perf_counter()
    x = nodes.reshape(-1, 3).astype(np.int32)
    M = len(x)
    root = np.sqrt(np.arange(3 * 255 ** 2 + 1, dtype=np.float64))
    ii, jj, kk = np.meshgrid(*(np.arange(m),) * 3, indexing="ij")
    colours = ((ii % 2) * 4 + (jj % 2) * 2 + kk % 2).ravel()
    idx, frac = axis_tables(grid)
    states = []
    for name, rgb, target in (("training", points, targets), ("guard", guard_points, guard_targets)):
        if rgb is None:
            continue
        if (np.asarray(rgb).dtype != np.uint8 or np.asarray(target).dtype != np.uint8
                or np.shape(rgb) != np.shape(target) or np.ndim(rgb) != 2
                or np.shape(rgb)[1] != 3 or not len(rgb)):
            raise ValueError("guarded Q16 refinement requires matching uint8 (N,3) samples")
        I, W = tetra_index_weights_q(rgb, idx, frac, m)
        acc = np.sum(W[..., None] * x[I], axis=1, dtype=np.int32)
        y = target.astype(np.int32)
        error = ((acc + ONE // 2) >> Q) - y
        squared = np.sum(error * error, axis=1, dtype=np.int32)
        support = []
        for colour in range(8):
            row, vertex = np.nonzero((colours[I] == colour) & (W > 0))
            support.append((row, I[row, vertex], W[row, vertex]))
        states.append({"name": name, "y": y, "acc": acc, "error": error, "squared": squared,
                       "support": support})

    def statistics():
        return {s["name"]: _rgb_error_stats((s["acc"] + ONE // 2) >> Q, s["y"]) for s in states}

    report = {} if diagnostics is None else diagnostics
    before = statistics()
    report.update({"objective": "joint_actual_q16_rgb_distance", "sample_guards": ["mean", "rms", "p99", "max"],
                   "acceptance": "per_node_on_each_sample_set", "before": before,
                   "training_points": len(points), "guard_points": 0 if guard_points is None else len(guard_points),
                   "sweeps": []})
    current = before
    stop = "sweep_limit"
    for sweep in range(sweeps):
        previous = x.copy()
        changed = 0
        for state in states:
            squared = state["squared"]
            rank = .99 * (len(squared) - 1)
            order = [int(np.floor(rank)), int(np.ceil(rank))]
            state["tail_limits"] = np.unique(np.partition(squared, order)[order])
            state["max_limit"] = int(squared.max())
        for colour in range(8):
            for channel in range(3):
                gains = []
                for delta in (1, -1):
                    allowed = (x[:, channel] + delta >= 0) & (x[:, channel] + delta <= 255)
                    total_gain = np.zeros(M)
                    for state in states:
                        row, node, weight = state["support"][colour]
                        if not len(row):
                            continue
                        old_squared = state["squared"][row]
                        old_error = state["error"][row, channel]
                        trial = np.clip((state["acc"][row, channel] + delta * weight + ONE // 2) >> Q, 0, 255)
                        new_error = trial - state["y"][row, channel]
                        new_squared = old_squared + new_error ** 2 - old_error ** 2
                        gain = np.bincount(node, weights=root[new_squared] - root[old_squared], minlength=M)
                        squared_gain = np.bincount(node, weights=new_squared - old_squared, minlength=M)
                        too_large = np.bincount(node, weights=new_squared > state["max_limit"], minlength=M)
                        allowed &= (gain <= 1e-12) & (squared_gain <= 0) & (too_large == 0)
                        for limit in state["tail_limits"]:
                            crossing = ((new_squared > limit).astype(np.int8)
                                        - (old_squared > limit).astype(np.int8))
                            allowed &= np.bincount(node, weights=crossing, minlength=M) <= 0
                        total_gain += gain
                    total_gain[~allowed] = np.inf
                    gains.append(total_gain)
                plus, minus = gains
                move = np.where((plus < -1e-12) & (plus <= minus), 1,
                                np.where(minus < -1e-12, -1, 0)).astype(np.int32)
                changed += int(np.count_nonzero(move))
                x[:, channel] += move
                for state in states:
                    row, node, weight = state["support"][colour]
                    old_error = state["error"][row, channel]
                    state["acc"][row, channel] += move[node] * weight
                    new_error = ((state["acc"][row, channel] + ONE // 2) >> Q) - state["y"][row, channel]
                    state["squared"][row] += new_error ** 2 - old_error ** 2
                    state["error"][row, channel] = new_error
        if changed == 0:
            stop = "constrained_coordinate_optimum"
            break
        candidate = statistics()
        accepted = all(candidate[name][metric] <= current[name][metric] + 1e-12
                       for name in current for metric in ("mean", "rms", "p99", "max"))
        report["sweeps"].append({"sweep": sweep + 1, "changed_coordinates": changed,
                                 "statistics": candidate, "accepted": bool(accepted)})
        if not accepted:
            # Defensive protection against a future implementation regression.
            x = previous
            stop = "contract_rollback"
            break
        current = candidate
    report.update({"after": current, "stop_reason": stop,
                   "accepted_sweeps": sum(row["accepted"] for row in report["sweeps"]),
                   "refine_s": time.perf_counter() - started})
    return x.astype(np.uint8).reshape(m, m, m, 3)


def fit_guarded_tetra(T, grid, sweeps=3, *, diagnostics=None):
    """Optional jittered LS plus locally constrained, true-Q16 integer refinement."""
    report = {} if diagnostics is None else diagnostics
    x, H, b = fit_stratified_tetra(T, grid, diagnostics=report.setdefault("least_squares", {}))
    m = grid.shape[1]
    nodes = quantize(int_refine(x, H, b).reshape(m, m, m, 3))
    points = stratified_points()
    guard = guard_points_excluding(points)
    target = T[points[:, 0], points[:, 1], points[:, 2]]
    guard_target = T[guard[:, 0], guard[:, 1], guard[:, 2]]
    return q16_refine_guarded(nodes, points, target, grid, sweeps, guard_points=guard,
                              guard_targets=guard_target, diagnostics=report.setdefault("q16_refine", {}))


# ================================================================ adaptive grid
def adaptive_dp_grid(T: np.ndarray, m: int, probes: int = 24, *, diagnostics=None) -> np.ndarray:
    """Choose integer knots by dynamic programming on exact axiswise chord SSE.

    For one axis, regard all sampled perpendicular colours and output channels
    as a vector-valued curve Y[x]. A 256x256 Gram matrix plus two prefix sums
    evaluates every segment's linear-interpolation SSE without looping over
    its interior colours. DP then chooses m endpoints, with fixed 0/255 and
    spacing in [2, ceil(2*255/(m-1))]. The spacing penalty breaks near-affine
    ties towards uniform intervals; this is an axiswise surrogate, not the
    final tetrahedral or quantised objective.
    """
    if not 17 <= m <= 33 or not 2 <= probes <= 256:
        raise ValueError("DP grid requires 17<=m<=33 and 2<=probes<=256")
    started = time.perf_counter()
    report = {} if diagnostics is None else diagnostics
    grid = np.empty((3, m), np.float64)
    perpendicular = np.round(np.linspace(0, 255, probes)).astype(np.intp)
    ideal = 255.0 / (m - 1)
    max_step = int(np.ceil(2 * ideal))
    report.update({"method": "axis_chord_sse_dynamic_programming", "perpendicular_probes": probes,
                   "minimum_step": 2, "maximum_step": max_step, "axes": []})
    for axis in range(3):
        coords = [perpendicular, perpendicular, perpendicular]
        coords[axis] = np.arange(256)
        Y = np.moveaxis(T[np.ix_(*coords)], axis, 0).reshape(256, -1).astype(np.float64)
        Y -= Y.mean(axis=0)  # interpolation error is invariant to a constant shift
        gram = (Y @ Y.T) / Y.shape[1]
        prefix = np.pad(np.cumsum(gram, axis=1), ((0, 0), (1, 0)))
        weighted = np.pad(np.cumsum(gram * np.arange(256)[None], axis=1), ((0, 0), (1, 0)))
        diag = gram.diagonal()
        norm_prefix = np.r_[0.0, np.cumsum(diag)]
        cost = np.full((256, 256), np.inf)
        for a in range(254):
            b = np.arange(a + 2, min(a + max_step, 255) + 1)
            width = b - a
            # Include both endpoints; their residuals are exactly zero.
            sum_a = prefix[a, b + 1] - prefix[a, a]
            xsum_a = weighted[a, b + 1] - weighted[a, a]
            sum_b = prefix[b, b + 1] - prefix[b, a]
            xsum_b = weighted[b, b + 1] - weighted[b, a]
            cross = 2 * (b * sum_a - xsum_a + xsum_b - a * sum_b) / width
            square_coeff = (width + 1) * (2 * width + 1) / (6.0 * width)
            mixed_coeff = (width + 1) * (width - 1) / (6.0 * width)
            pred_norm = square_coeff * (diag[a] + diag[b]) + 2 * mixed_coeff * gram[a, b]
            cost[a, b] = np.maximum(norm_prefix[b + 1] - norm_prefix[a] - cross + pred_norm, 0)
        dp = np.full((m, 256), np.inf)
        parent = np.full((m, 256), -1, np.int16)
        dp[0, 0] = 0
        for segments in range(1, m):
            for end in range(2 * segments, min(255, max_step * segments) + 1):
                start = np.arange(max(2 * (segments - 1), end - max_step), end - 1)
                value = dp[segments - 1, start] + cost[start, end] + 1e-6 * (end - start - ideal) ** 2
                best = int(np.argmin(value))
                dp[segments, end] = value[best]
                parent[segments, end] = start[best]
        if not np.isfinite(dp[m - 1, 255]):
            raise RuntimeError("no feasible DP grid under spacing constraints")
        grid[axis, -1] = 255
        end = 255
        for segments in range(m - 1, 0, -1):
            end = int(parent[segments, end])
            grid[axis, segments - 1] = end
        knot = grid[axis].astype(np.intp)
        uniform = np.round(np.linspace(0, 255, m)).astype(np.intp)
        report["axes"].append({"axis": axis, "knots": knot.tolist(),
                                "selected_chord_sse": float(cost[knot[:-1], knot[1:]].sum()),
                                "rounded_uniform_chord_sse": float(cost[uniform[:-1], uniform[1:]].sum())})
    report["grid_s"] = time.perf_counter() - started
    return grid


def adaptive_grid(T: np.ndarray, m: int, alpha: float = 0.5, expo: float = 0.4) -> np.ndarray:
    """Per-axis knot placement equidistributing |d2 T/dx2|^expo (mixed with uniform)."""
    grid = np.empty((3, m))
    for a in range(3):
        sl = [slice(None, None, 4), slice(None, None, 4), slice(None, None, 4), slice(None)]
        sl[a] = slice(None)
        sub = T[tuple(sl)].astype(np.float32)
        d2 = np.abs(np.diff(sub, n=2, axis=a))
        other = tuple(i for i in range(4) if i != a)
        prof = d2.mean(axis=other)
        prof = np.concatenate([[prof[0]], prof, [prof[-1]]])  # back to 256
        dens = prof ** expo
        dens = alpha * dens / (dens.mean() + 1e-8) + (1 - alpha)
        cdf = np.concatenate([[0], np.cumsum((dens[1:] + dens[:-1]) / 2)])
        cdf /= cdf[-1]
        grid[a] = np.interp(np.linspace(0, 1, m), cdf, np.arange(256.0))
        grid[a][0], grid[a][-1] = 0.0, 255.0
        # enforce a minimum spacing so every cell keeps some support
        for i in range(1, m):
            grid[a][i] = max(grid[a][i], grid[a][i - 1] + 2.0)
        grid[a] = np.minimum(grid[a], 255.0 - 2.0 * (m - 1 - np.arange(m)))
    return grid


def adaptive_error_grid(T: np.ndarray, m: int, alpha: float = 0.5) -> np.ndarray:
    """Place knots using held-out error of a pilot uniform tetrahedral fit."""
    pilot_grid = uniform_grid(m)
    pilot = fit_sample(T, pilot_grid)
    pts = _cube_points(8)
    v = np.round(np.linspace(0, 255, 32)).astype(np.intp)
    target = T[np.ix_(v, v, v)].reshape(-1, 3)
    I, W = tetra_weights(pts, *axis_tables(pilot_grid), m)
    pred = np.einsum("nk,nkc->nc", W, pilot.reshape(-1, 3)[I])
    err = np.linalg.norm(pred - target, axis=1).reshape(32, 32, 32)
    grid = np.empty((3, m))
    for axis in range(3):
        prof = err.mean(axis=tuple(a for a in range(3) if a != axis))
        density = 1.0 - alpha + alpha * (prof + 0.25) / (prof.mean() + 0.25)
        cdf = np.r_[0.0, np.cumsum((density[1:] + density[:-1]) / 2)]
        cdf /= cdf[-1]
        grid[axis] = np.interp(np.linspace(0, 1, m), cdf, v.astype(float))
        grid[axis, 0], grid[axis, -1] = 0.0, 255.0
        for j in range(1, m):
            grid[axis, j] = max(grid[axis, j], grid[axis, j - 1] + 2)
        grid[axis] = np.minimum(grid[axis], 255 - 2 * (m - 1 - np.arange(m)))
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
        x, _, _ = fit_ls_tetra(T, grid, diagnostics=info.setdefault("solver", {}))
    elif method == "ls_tetra_int":
        x, H, b = fit_ls_tetra(T, grid, diagnostics=info.setdefault("solver", {}))
        x = int_refine(x, H, b)
    elif method == "ls_tetra_q16":
        x = fit_q16_tetra(T, grid, diagnostics=info)
    elif method == "ls_tetra_jitter":
        x, H, b = fit_stratified_tetra(T, grid, diagnostics=info.setdefault("least_squares", {}))
        x = int_refine(x, H, b)
    elif method == "ls_tetra_guarded":
        x = fit_guarded_tetra(T, grid, diagnostics=info)
    elif method == "irls_tetra":
        x = fit_irls_tetra(T, grid, diagnostics=info.setdefault("solver", {}))
    elif method == "tail_tetra_int":
        x = fit_tail_tetra(T, grid, diagnostics=info.setdefault("solver", {}))
    else:
        raise KeyError(method)
    info["fit_s"] = round(time.perf_counter() - t0, 3)
    return quantize(x.reshape(m, m, m, 3)), grid, info
