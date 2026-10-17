"""Explicit independent four-LUT jitter fit with bounded CG continuation.

Usage: python -m lutlab.robust_fit --inputs T1 T2 T3 T4 --m 33 --model-dir models
This optional offline entry uses ordinary SLUT v1 Q16 models. It does not patch
the old fitter or modify any declared matrix. All effective policy/source bytes
are included in the immutable cache identity and checked again before publish.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import time

import numpy as np

from . import cache, cascade, fit, io, robust_solver

METHOD = "ls_tetra_jitter_continued"


def identity(input_paths, m, grid):
    policy = copy.deepcopy(robust_solver.POLICY)
    parameters = {"m": m, "mode": "seq", "method": METHOD, "grid": grid,
                  "interpolation_basis": "tetra_q16", "semantics": "independent", "n_stages": 4,
                  "residual_tail_beta": 0.0, "solver_policy": policy}
    value = cache.build_identity(input_paths, parameters)
    value["source_sha256"].update({name: cache.file_sha256(Path(__file__).parent / name)
                                    for name in ("robust_fit.py", "robust_solver.py")})
    value["algorithm_settings"] = cache.algorithm_settings({**parameters, "method": "ls_tetra_jitter"})
    value["algorithm_settings"]["least_squares"].update(solver=METHOD, continuation_policy=policy)
    return value


def fit_stage(table, m, grid, *, diagnostics):
    """Same jitter normal equations and integer refinement; alternate solver only."""
    started = time.perf_counter()
    seed = 0x533138
    points = fit.stratified_points(seed)
    targets = table[points[:, 0], points[:, 1], points[:, 2]]
    H, transpose = fit._stratified_system(np.ascontiguousarray(grid, np.float64).tobytes(), m, seed)
    b = transpose @ targets.astype(np.float64)
    x0 = fit.fit_ls_sep(table, grid, "hat").reshape(-1, 3)
    diagnostics.update(sample_scheme="one_jittered_point_per_4x4x4_block", sample_seed=seed, sample_count=len(points),
                       normal_equations_assembly="CSR design, sorted Hessian columns matching legacy COO")
    policy = robust_solver.POLICY
    x = robust_solver.solve_spd(H, b, x0, lam=policy["lambda"], tol=policy["rtol"],
        maxiter=policy["first_maxiter"], continuation_maxiter=policy["continuation_maxiter"],
        max_continuations=policy["max_continuations"], diagnostics=diagnostics.setdefault("solver", {}))
    nodes = fit.quantize(fit.int_refine(x.reshape(m, m, m, 3), H, b).reshape(m, m, m, 3))
    diagnostics["fit_s"] = time.perf_counter() - started
    return io.SparseLut(grid, nodes)


def fit_batch(input_paths, m, grid, model_dir):
    inputs = [Path(path).resolve() for path in input_paths]
    if len(inputs) != 4 or not 17 <= m <= 33 or grid not in ("uniform", "dp"):
        raise ValueError("requires four full original LUTs, m17..33, and uniform/dp grid")
    before = identity(inputs, m, grid)
    if (len({row["sha256"] for row in before["inputs"]}) != 4
            or any(row["bytes"] != io.FULL_NBYTES for row in before["inputs"])):
        raise ValueError("four distinct complete RGB8 source LUTs required")
    hit = cache.lookup(Path(model_dir), before)
    if hit is not None:
        if identity(inputs, m, grid) != before:
            raise RuntimeError("source or solver identity changed while validating cached models")
        return hit, True
    started = time.perf_counter()
    tables = [io.load_full(path) for path in inputs]
    if [cache.file_sha256(path) for path in inputs] != [row["sha256"] for row in before["inputs"]]:
        raise RuntimeError("source bytes changed while loading")
    chain = []
    info = []
    for table in tables:
        axis = cascade._grid_for(table, m, False, grid)
        diagnostics = {}
        chain.append(fit_stage(table, m, axis, diagnostics=diagnostics))
        info.append(diagnostics)
    if identity(inputs, m, grid) != before:
        raise RuntimeError("source, solver policy or fitting code changed; no models published")
    summary = {"fit_s": time.perf_counter() - started, "stage_s": [row["fit_s"] for row in info], "stage_info": info,
               "stage_semantics": "independent_lut_fits", "solver_policy": copy.deepcopy(robust_solver.POLICY),
               "timing_is_benchmark": False}
    return cache.publish(Path(model_dir), before, chain, summary), False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs=4, type=Path, required=True)
    parser.add_argument("--m", type=int, required=True, choices=range(17, 34))
    parser.add_argument("--grid", choices=("dp", "uniform"), default="dp")
    parser.add_argument("--model-dir", type=Path, required=True)
    args = parser.parse_args()
    entry, hit = fit_batch(args.inputs, args.m, args.grid, args.model_dir)
    print(json.dumps({"models": list(map(str, entry.paths)), "manifest": str(entry.directory / "manifest.json"),
                      "identity_sha256": entry.manifest["identity_sha256"], "cache_hit": hit, "method": METHOD,
                      "fit": entry.manifest["fit"]}))


if __name__ == "__main__":
    main()
