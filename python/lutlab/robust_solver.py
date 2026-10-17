"""Jacobi CG with bounded continuation and explicit true-residual checks.

The first solve has the same arithmetic and acceptance test as fit.solve_spd.
Only a finite exhausted first solve can continue from its current iterate. The
system, prior, tolerance and integer fitting objective never change. No partial
RGB solution is returned when any channel exhausts the declared total budget.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .fit import FitConvergenceError

POLICY = {"name": "jacobi_cg_bounded_continuation_v1", "lambda": 1e-4, "rtol": 1e-7,
          "first_maxiter": 300, "continuation_maxiter": 300, "max_continuations": 3,
          "initial_true_residual_limit": "max(10*rtol,1e-12), with scipy info=0; unchanged legacy rule",
          "continuation_true_residual_limit": "rtol, with scipy info=0",
          "warm_start": "previous finite iterate; restart CG recurrence on the same regularized SPD system",
          "failure": "raise before returning any partial RGB model"}


def solve_spd(H, b, x0=None, lam=1e-4, tol=1e-7, *, maxiter=300, continuation_maxiter=300,
              max_continuations=3, diagnostics=None):
    report = {} if diagnostics is None else diagnostics
    report.update(solver=POLICY["name"], lambda_=float(lam), rtol=float(tol), maxiter=int(maxiter),
                  continuation_maxiter=int(continuation_maxiter), max_continuations=int(max_continuations),
                  channels=[], status="running")
    report["lambda"] = report.pop("lambda_")
    n = H.shape[0]
    d = H.diagonal()
    D = d + 1.0
    if x0 is None:
        x0 = np.zeros((n, 3))
    if (H.shape != (n, n) or np.shape(b) != (n, 3) or np.shape(x0) != (n, 3)
            or not np.isfinite(lam) or lam <= 0 or not np.isfinite(tol) or tol <= 0
            or maxiter < 1 or continuation_maxiter < 1 or max_continuations < 0
            or not np.all(np.isfinite(H.data)) or not np.all(np.isfinite(b))
            or not np.all(np.isfinite(x0)) or np.any(d < 0)):
        report["status"] = "invalid_input"
        raise FitConvergenceError("invalid/non-finite regularized least-squares system", report)
    A = (H + sp.diags(lam * D)).tocsr()
    Pinv = sp.diags(1.0 / (d + lam * D))
    out = np.empty((n, 3))
    for channel in range(3):
        rhs = b[:, channel] + lam * D * x0[:, channel]
        initial = x0[:, channel]
        attempts = []
        for attempt in range(max_continuations + 1):
            iterations = 0
            def count_iteration(_):
                nonlocal iterations
                iterations += 1
            candidate, info = spla.cg(A, rhs, x0=initial, rtol=tol,
                maxiter=maxiter if attempt == 0 else continuation_maxiter, M=Pinv, callback=count_iteration)
            finite = bool(np.all(np.isfinite(candidate)))
            rhs_norm = float(np.linalg.norm(rhs))
            residual = float(np.linalg.norm(A @ candidate - rhs)) if finite else None
            relative = residual / max(rhs_norm, np.finfo(float).tiny) if finite else None
            limit = max(10 * tol, 1e-12) if attempt == 0 else tol
            converged = info == 0 and finite and relative <= limit
            attempts.append({"attempt": attempt, "info": int(info), "iterations": iterations,
                             "residual_l2": residual, "relative_residual": relative,
                             "finite": finite, "converged": bool(converged)})
            if converged:
                out[:, channel] = candidate
                break
            if not finite or info < 0 or attempt == max_continuations:
                report["channels"].append({"channel": channel, "attempts": attempts,
                    "iterations": sum(row["iterations"] for row in attempts), "converged": False})
                report["status"] = "failed"
                raise FitConvergenceError(f"bounded CG failed for channel {channel}: info={info}, relative_residual={relative}", report)
            initial = candidate
        report["channels"].append({"channel": channel, "attempts": attempts,
            "iterations": sum(row["iterations"] for row in attempts), "converged": True})
    report["status"] = "converged"
    return out
