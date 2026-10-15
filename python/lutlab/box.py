"""Box-constrained continuous LS and exact comparison of integer Q16 models.

The continuous problem is solved on a diagonally scaled, centred quadratic.
Only an explicitly checked feasible KKT point can be returned. Integer model
selection uses exact dyadic native moments, not subtraction of large float SSEs.
"""
from __future__ import annotations

import time

import numpy as np
import scipy.sparse as sp


class BoxConvergenceError(RuntimeError):
    def __init__(self, message, diagnostics):
        super().__init__(message)
        self.diagnostics = diagnostics


def solve_box(H, b, start=None, *, tol=1e-5, maxiter=500, ftol=1e-15, maxcor=10, diagnostics=None):
    """Minimise .5 sum(x*H*x)-sum(b*x), 0<=x<=255, for caller-proved SPD H.

    A library success flag is insufficient: feasibility, objective change and
    the independently recomputed scaled KKT residual must pass. No RGB output
    or global four-stage error guarantee follows from this continuous optimum.
    """
    from scipy.optimize import Bounds, minimize
    report = {} if diagnostics is None else diagnostics
    report.update(solver="centred_diagonal_lbfgsb", status="running", bounds=[0., 255.],
                  scaled_kkt_tolerance=tol, maxiter=maxiter, ftol=ftol, maxcor=maxcor,
                  optimizer_gtol=tol * .01, regularisation=0.)
    started = time.perf_counter()
    H = sp.csr_matrix(H, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    n = H.shape[0]
    x0 = np.zeros((n, 3)) if start is None else np.array(start, dtype=np.float64, copy=True, order="C")
    diagonal = H.diagonal()
    asymmetry = H - H.T if H.shape == (n, n) else None
    if (H.shape != (n, n) or b.shape != (n, 3) or x0.shape != (n, 3) or n == 0
            or not np.all(np.isfinite(H.data)) or not np.all(np.isfinite(b)) or not np.all(np.isfinite(x0))
            or np.any(diagonal <= 0) or np.any(x0 < 0) or np.any(x0 > 255)
            or (asymmetry is not None and asymmetry.nnz and np.max(abs(asymmetry.data)) > 1e-12 * max(1., np.max(abs(H.data))))
            or not np.isfinite(tol) or tol <= 0 or not np.isfinite(ftol) or ftol < 0
            or not isinstance(maxiter, int) or isinstance(maxiter, bool) or maxiter < 1
            or not isinstance(maxcor, int) or isinstance(maxcor, bool) or maxcor < 1):
        report["status"] = "invalid_input"
        raise BoxConvergenceError("invalid finite symmetric box-LS problem or feasible start", report)
    scale = np.sqrt(diagonal)[:, None]
    g0 = H @ x0 - b
    lower, upper = (-x0 * scale).ravel(), ((255. - x0) * scale).ravel()

    def quadratic(z):
        delta = z.reshape(n, 3) / scale
        product = H @ delta
        value = float(.5 * np.sum(delta * product) + np.sum(g0 * delta))
        gradient = ((product + g0) / scale).ravel()
        return value, gradient

    result = minimize(quadratic, np.zeros(n * 3), jac=True, method="L-BFGS-B", bounds=Bounds(lower, upper),
                      options={"gtol": tol * .01, "ftol": ftol, "maxiter": maxiter, "maxcor": maxcor, "maxls": 50})
    z = result.x
    # Only roundoff-distance bound snapping is permitted; a genuinely infeasible
    # optimisation result is rejected rather than repaired by a large clamp.
    tolerance = 32 * np.finfo(float).eps * np.maximum(abs(lower), abs(upper))
    z_feasible = bool(np.all(np.isfinite(z)) and np.all(z >= lower - tolerance) and np.all(z <= upper + tolerance))
    x = x0 + z.reshape(n, 3) / scale
    x.ravel()[z <= lower + tolerance] = 0.
    x.ravel()[z >= upper - tolerance] = 255.
    x = np.clip(x, 0., 255.)
    gradient = H @ x - b
    projected = gradient.copy()
    projected[((x == 0) & (gradient >= 0)) | ((x == 255) & (gradient <= 0))] = 0.
    scaled_inf = float(np.max(abs(projected / scale)))
    delta = x - x0
    change = float(.5 * np.sum(delta * (H @ delta)) + np.sum(g0 * delta))
    feasible = z_feasible and bool(np.all(np.isfinite(x)) and np.all(x >= 0) and np.all(x <= 255))
    converged = feasible and np.isfinite(change) and scaled_inf <= tol and change <= 1e-8
    report.update(optimizer_success=bool(result.success), optimizer_status=int(result.status),
        optimizer_message=str(result.message), iterations=int(result.nit), function_evaluations=int(result.nfev),
        feasible=feasible, scaled_projected_gradient_inf=scaled_inf,
        projected_gradient_l2_squared=float(np.sum(projected * projected)),
        projected_gradient_inf=float(np.max(abs(projected))), centred_objective_change=change,
        status="converged_by_kkt" if converged else "failed", solve_seconds=time.perf_counter() - started)
    if not converged:
        raise BoxConvergenceError(f"box LS failed feasibility/KKT check: scaled_inf={scaled_inf}, change={change}", report)
    return x


def integer_sse_change_numerator(H, b, baseline, candidate):
    """Exact full-domain unrounded SSE change numerator; denominator is 2^32.

    Requires the nonnegative native moments H=Hq/2^38 and b=bq/2^22.
    Row products fit signed int64 after explicit bounds checks; the final
    reduction uses Python integers because an SSE numerator can exceed uint64.
    """
    H = sp.csr_matrix(H)
    b, baseline, candidate = map(np.asarray, (b, baseline, candidate))
    n = H.shape[0]
    if (n == 0 or H.shape != (n, n) or b.shape != (n, 3) or baseline.shape != (n, 3) or candidate.shape != (n, 3)
            or baseline.dtype != np.uint8 or candidate.dtype != np.uint8):
        raise ValueError("integer SSE comparison requires matching RGB8 nodes and native moments")
    hq, bq = H.data * 2. ** 38, b * 2. ** 22
    exact_limit = 2 ** 53 - 1
    if (not np.all(np.isfinite(hq)) or not np.all(np.isfinite(bq)) or np.any(hq < 0) or np.any(bq < 0)
            or np.any(hq > exact_limit) or np.any(bq > exact_limit)
            or np.any(hq != np.rint(hq)) or np.any(bq != np.rint(bq))):
        raise ValueError("native integer moments are not exactly representable")
    # Generous headroom also absorbs float rounding in these conservative range
    # checks. The accepted row products are then evaluated entirely in int64.
    signed_limit = np.iinfo(np.int64).max
    max_row = float(np.max(np.asarray(H.sum(axis=1)))) * 2. ** 38
    if max_row * 510 > signed_limit / 2 or float(bq.max()) * 2 ** 17 > signed_limit / 2:
        raise ValueError("native moments exceed safe signed row-product range")
    raw = H.copy()
    raw.data = hq.astype(np.int64)
    raw_b = bq.astype(np.int64)
    old, new = baseline.astype(np.int64), candidate.astype(np.int64)
    difference = (new - old).ravel()
    linear = (raw @ (new + old) - raw_b * 2 ** 17).ravel()
    changed = np.flatnonzero(difference)
    return sum(int(difference[index]) * int(linear[index]) for index in changed)
