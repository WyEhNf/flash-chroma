"""One frozen, reproducible comparison of independent four-LUT fitting methods.

Run from the repository root, for example:
  python scripts/q16_refinement_study.py --output artifacts/r17-algorithm

This is a sampled algorithm experiment. It saves full LUTs and both four-stage
models for a later native full-colour/100-image validation; its sample results
are not a substitute for that validation or an official threshold verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

# Small fitting systems must not spawn a host-wide BLAS team. Set before NumPy.
for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import fit, interp, io, luts


def legacy_int_refine(x_float, H, b, sweeps=4):
    """Frozen pre-change implementation, for exact equivalence and timing."""
    m = x_float.shape[0]
    x = np.clip(np.round(x_float.reshape(-1, 3)), 0, 255)
    ii, jj, kk = np.meshgrid(*(np.arange(m),) * 3, indexing="ij")
    colour = ((ii % 2) * 4 + (jj % 2) * 2 + kk % 2).ravel()
    d = H.diagonal()
    for _ in range(sweeps):
        changed = 0
        for col in range(8):
            selected = colour == col
            gradient = H @ x - b
            for delta in (1.0, -1.0):
                gain = delta * gradient[selected] + 0.5 * d[selected, None]
                ok = (gain < -1e-12) & (x[selected] + delta >= 0) & (x[selected] + delta <= 255)
                values = x[selected]
                values[ok] += delta
                x[selected] = values
                changed += int(ok.sum())
                gradient = H @ x - b
        if changed == 0:
            break
    return x


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def asset(path):
    return {"path": str(Path(path).resolve()), "sha256": sha(path), "bytes": Path(path).stat().st_size}


def evaluate(chain, points, target):
    pred = points
    for model in chain:
        pred = interp.apply_tetra_q16(model, pred)
    return fit._rgb_error_stats(pred, target)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "artifacts" / "r17-algorithm")
    ap.add_argument("--scenarios", nargs="+", default=["isp-0", "clip-7", "warp-7"])
    ap.add_argument("--m", type=int, nargs="+", default=[17, 18])
    ap.add_argument("--evaluation-points", type=int, default=1 << 18)
    args = ap.parse_args()
    if any(not 17 <= m <= 33 for m in args.m) or args.evaluation_points < 1:
        raise ValueError("require 17 <= m <= 33 and a positive evaluation sample size")
    args.output.mkdir(parents=True, exist_ok=True)
    seed = 20261015
    training = fit._cube_points(4)
    guard_seed = 0x513136
    guard = fit._q16_guard_points(4, seed=guard_seed)
    in_axis = np.zeros(256, dtype=bool)
    in_axis[np.unique(training[:, 0])] = True
    guard_keys = (guard[:, 0].astype(np.int32) << 16) | (guard[:, 1].astype(np.int32) << 8) | guard[:, 2]
    rng = np.random.default_rng(seed)
    point_parts, left = [], args.evaluation_points
    while left:
        draw = rng.integers(0, 256, (left + 4096, 3), dtype=np.uint8)
        key = (draw[:, 0].astype(np.int32) << 16) | (draw[:, 1].astype(np.int32) << 8) | draw[:, 2]
        draw = draw[~np.all(in_axis[draw], axis=1) & ~np.isin(key, guard_keys)][:left]
        point_parts.append(draw)
        left -= len(draw)
    points = np.concatenate(point_parts)
    boundaries = np.array([0, 1, 127, 128, 254, 255], np.uint8)
    edge_points = np.stack(np.meshgrid(boundaries, boundaries, boundaries, indexing="ij"), -1).reshape(-1, 3)
    result = {
        "scope": "independent four-stage Q16 pipeline; synthetic LUTs; frozen sampled accuracy",
        "official_threshold_known": False,
        "command": sys.argv, "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "scipy": scipy.__version__,
        "blas_thread_limit": 1, "training_points": len(training), "guard_points": len(guard),
        "guard_seed": guard_seed, "evaluation_points": len(points), "evaluation_seed": seed,
        "evaluation_disjoint_from_training_and_guard": True,
        "boundary_points_separate": len(edge_points),
        "evaluation_point_sha256": hashlib.sha256(points.tobytes()).hexdigest(),
        "code": {name: sha(ROOT / "python" / "lutlab" / name)
                 for name in ("fit.py", "cascade.py", "interp.py", "luts.py", "io.py")},
        "scenarios": [],
    }
    try:
        result["head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        result["head"] = None
    try:
        from threadpoolctl import threadpool_info
        result["threadpools"] = threadpool_info()
    except ImportError:
        result["threadpools"] = "threadpoolctl unavailable; process environment limit set before NumPy"

    all_start = time.perf_counter()
    for sid in args.scenarios:
        scenario_start = time.perf_counter()
        destination = args.output / sid
        destination.mkdir(parents=True, exist_ok=True)
        name, source_seed = luts.parse_scenario(sid)
        stages = luts.scenario(name, source_seed)
        tables = [luts.build_lut(stage) for stage in stages]
        row = {"scenario": sid, "source_seed": source_seed, "description": json.loads(luts.describe(stages)),
               "full_luts": [], "candidates": []}
        for stage_id, table in enumerate(tables, 1):
            path = destination / f"lut{stage_id}.lut256"
            io.save_full(path, table)
            row["full_luts"].append(asset(path))
        comp = io.compose(tables)
        comp_path = destination / "composite.lut256"
        io.save_full(comp_path, comp)
        row["composite"] = asset(comp_path)
        exact_final = io.apply_full(comp, points)
        exact_boundary = io.apply_full(comp, edge_points)
        del comp
        for m in args.m:
            grid = io.uniform_grid(m)
            baseline, candidate, detail = [], [], []
            for stage_id, table in enumerate(tables, 1):
                solver = {}
                start = time.perf_counter()
                x, H, b = fit.fit_ls_tetra(table, grid, diagnostics=solver)
                ls_s = time.perf_counter() - start
                start = time.perf_counter()
                original = legacy_int_refine(x, H, b)
                legacy_s = time.perf_counter() - start
                start = time.perf_counter()
                accelerated = fit.int_refine(x, H, b)
                accelerated_s = time.perf_counter() - start
                if not np.array_equal(original, accelerated):
                    raise AssertionError(f"legacy refinement changed: {sid}, m={m}, stage={stage_id}")
                incumbent = fit.quantize(accelerated.reshape(m, m, m, 3))
                diagnostic = {"guard_seed": guard_seed}
                refined = fit.q16_refine(incumbent, training, io.apply_full(table, training), grid,
                                        guard_points=guard, guard_targets=io.apply_full(table, guard),
                                        diagnostics=diagnostic)
                old = io.SparseLut(grid, incumbent)
                new = io.SparseLut(grid, refined)
                baseline.append(old)
                candidate.append(new)
                actual_training = fit._rgb_error_stats(interp.apply_tetra_q16(new, training),
                                                       io.apply_full(table, training))
                if actual_training != diagnostic["after"]["training"]:
                    raise AssertionError("Q16 refinement diagnostics disagree with runtime mirror")
                stage_detail = {"stage": stage_id, "solver": solver, "ls_s": ls_s,
                                "legacy_refine_s": legacy_s, "accelerated_refine_s": accelerated_s,
                                "legacy_nodes_bit_exact": True, "q16": diagnostic,
                                "heldout_baseline": evaluate([old], points, io.apply_full(table, points)),
                                "heldout_q16": evaluate([new], points, io.apply_full(table, points)),
                                "changed_node_channels": int(np.count_nonzero(incumbent != refined))}
                detail.append(stage_detail)
                for variant, model in (("baseline", old), ("q16", new)):
                    folder = destination / f"{variant}_m{m}"
                    folder.mkdir(exist_ok=True)
                    io.save_sparse(folder / f"stage{stage_id}.slut", model)
                print(json.dumps({"scenario": sid, "m": m, "stage": stage_id,
                                  "q16_sweeps_accepted": diagnostic["accepted_sweeps"],
                                  "stage_mean_before": stage_detail["heldout_baseline"]["mean"],
                                  "stage_mean_after": stage_detail["heldout_q16"]["mean"]}), flush=True)

            final_baseline = evaluate(baseline, points, exact_final)
            final_candidate = evaluate(candidate, points, exact_final)
            item = {"m": m, "stage_semantics": "four_independent_lut_fits", "stages": detail,
                    "heldout_four_stage_baseline": final_baseline,
                    "heldout_four_stage_q16": final_candidate,
                    "boundary_four_stage_baseline": evaluate(baseline, edge_points, exact_boundary),
                    "boundary_four_stage_q16": evaluate(candidate, edge_points, exact_boundary),
                    "heldout_four_stage_no_regression": all(final_candidate[key] <= final_baseline[key] + 1e-12
                                                               for key in ("mean", "rms", "p99", "max")),
                    "models": {variant: [asset(destination / f"{variant}_m{m}" / f"stage{k}.slut")
                                          for k in range(1, 5)] for variant in ("baseline", "q16")}}
            row["candidates"].append(item)
            print(json.dumps({"scenario": sid, "m": m, "four_stage_baseline": final_baseline,
                              "four_stage_q16": final_candidate}), flush=True)
        row["elapsed_s"] = time.perf_counter() - scenario_start
        result["scenarios"].append(row)
        result["elapsed_s"] = time.perf_counter() - all_start
        (args.output / "study.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        del tables
    print(json.dumps({"result": str((args.output / "study.json").resolve()),
                      "elapsed_s": result["elapsed_s"]}), flush=True)


if __name__ == "__main__":
    main()
