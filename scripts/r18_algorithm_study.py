"""Frozen R18 algorithm comparison; reuses R17 full LUTs without altering them."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

for variable in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import fit, interp, io


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def asset(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}


def evaluate(chain, points, target):
    pred = points
    for model in chain:
        pred = interp.apply_tetra_q16(model, pred)
    return fit._rgb_error_stats(pred, target)


def key(points):
    return ((points[:, 0].astype(np.int32) << 16) | (points[:, 1].astype(np.int32) << 8)
            | points[:, 2])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=ROOT / "artifacts" / "r17-algorithm")
    ap.add_argument("--output", type=Path, default=ROOT / "artifacts" / "r18-algorithm")
    ap.add_argument("--scenarios", nargs="+", default=["isp-0", "clip-7", "warp-7"])
    ap.add_argument("--m", type=int, nargs="+", default=[17, 18])
    ap.add_argument("--evaluation-points", type=int, default=1 << 18)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source_record = json.loads((args.source / "study.json").read_text(encoding="utf-8"))
    regular = fit._cube_points(4)
    regular_guard = fit._q16_guard_points()
    jitter = fit.stratified_points()
    jitter_guard = fit.guard_points_excluding(jitter)
    excluded = np.concatenate([regular, regular_guard, jitter, jitter_guard])
    evaluation_seed = 2026101518
    points = fit.guard_points_excluding(excluded, args.evaluation_points, evaluation_seed)
    boundary_axis = np.array([0, 1, 127, 128, 254, 255], np.uint8)
    boundary = np.stack(np.meshgrid(*(boundary_axis,) * 3, indexing="ij"), -1).reshape(-1, 3)
    report = {"scope": "four independent uint8 LUTs, Q16 tetrahedral runtime mirror, synthetic source LUTs",
              "command": sys.argv, "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
              "platform": platform.platform(), "blas_threads": 1,
              "source_record": asset(args.source / "study.json"),
              "evaluation_seed": evaluation_seed, "evaluation_count": len(points),
              "evaluation_excludes_all_fitting_and_guard_points": True,
              "sample_sha256": {name: hashlib.sha256(values.tobytes()).hexdigest()
                                  for name, values in (("regular", regular), ("regular_guard", regular_guard),
                                                       ("jitter", jitter), ("jitter_guard", jitter_guard),
                                                       ("evaluation", points))},
              "code_sha256": {name: sha(ROOT / "python" / "lutlab" / name)
                                for name in ("fit.py", "cascade.py", "interp.py", "io.py")},
              "scenarios": []}
    beginning = time.perf_counter()
    for scene in args.scenarios:
        source_dir = args.source / scene
        source_meta = next(row for row in source_record["scenarios"] if row["scenario"] == scene)
        full_paths = [source_dir / f"lut{k}.lut256" for k in range(1, 5)]
        for path, expected in zip(full_paths, source_meta["full_luts"]):
            if sha(path) != expected["sha256"]:
                raise RuntimeError(f"source hash mismatch: {path}")
        tables = [io.load_full(path) for path in full_paths]
        composite_path = source_dir / "composite.lut256"
        composite = io.load_full(composite_path)
        target = io.apply_full(composite, points)
        boundary_target = io.apply_full(composite, boundary)
        del composite
        scene_record = {"scenario": scene, "full_luts": [asset(p) for p in full_paths],
                        "composite": asset(composite_path), "candidates": []}
        for m in args.m:
            uniform = io.uniform_grid(m)
            chains = {name: [] for name in ("sample_interp", "baseline", "guarded_base", "jitter",
                                           "jitter_guarded", "dp_jitter", "dp_guarded")}
            details = []
            for number, table in enumerate(tables, 1):
                start = time.perf_counter()
                stage = {"stage": number, "fitting": {}, "grid": {}}
                baseline = io.load_sparse(source_dir / f"baseline_m{m}" / f"stage{number}.slut")
                chains["baseline"].append(baseline)
                sample = io.SparseLut(uniform, fit.quantize(fit.fit_sample_interp(table, uniform)))
                chains["sample_interp"].append(sample)
                detail = {}
                guarded_base = fit.q16_refine_guarded(baseline.nodes, regular, io.apply_full(table, regular),
                                                       uniform, guard_points=regular_guard,
                                                       guard_targets=io.apply_full(table, regular_guard),
                                                       diagnostics=detail)
                stage["fitting"]["guarded_base"] = detail
                chains["guarded_base"].append(io.SparseLut(uniform, guarded_base))
                dp_grid = fit.adaptive_dp_grid(table, m, diagnostics=stage["grid"])
                for prefix, grid in (("jitter", uniform), ("dp", dp_grid)):
                    fit_start = time.perf_counter()
                    detail = {}
                    x, H, b = fit.fit_stratified_tetra(table, grid, diagnostics=detail)
                    nodes = fit.quantize(fit.int_refine(x, H, b).reshape(m, m, m, 3))
                    detail["fit_s"] = time.perf_counter() - fit_start
                    variant = "jitter" if prefix == "jitter" else "dp_jitter"
                    chains[variant].append(io.SparseLut(grid, nodes))
                    stage["fitting"][variant] = detail
                    refine = {}
                    refined = fit.q16_refine_guarded(nodes, jitter, io.apply_full(table, jitter), grid,
                                                     guard_points=jitter_guard,
                                                     guard_targets=io.apply_full(table, jitter_guard),
                                                     diagnostics=refine)
                    variant = "jitter_guarded" if prefix == "jitter" else "dp_guarded"
                    chains[variant].append(io.SparseLut(grid, refined))
                    stage["fitting"][variant] = refine
                stage["elapsed_s"] = time.perf_counter() - start
                stage["heldout"] = {name: evaluate([chain[-1]], points, io.apply_full(table, points))
                                     for name, chain in chains.items()}
                # Validate reported refinement metrics with the independent API.
                for name, training, guard in (("guarded_base", regular, regular_guard),
                                              ("jitter_guarded", jitter, jitter_guard), ("dp_guarded", jitter, jitter_guard)):
                    actual = {label: evaluate([chains[name][-1]], rgb, io.apply_full(table, rgb))
                              for label, rgb in (("training", training), ("guard", guard))}
                    if actual != stage["fitting"][name]["after"]:
                        raise AssertionError(f"Q16 diagnostic inconsistency: {scene}, {m}, {number}, {name}")
                details.append(stage)
                print(json.dumps({"scenario": scene, "m": m, "stage": number,
                                  "mean_by_method": {name: stat["mean"] for name, stat in stage["heldout"].items()},
                                  "elapsed_s": stage["elapsed_s"]}), flush=True)
            for name, chain in chains.items():
                directory = args.output / scene / f"{name}_m{m}"
                directory.mkdir(parents=True, exist_ok=True)
                for number, model in enumerate(chain, 1):
                    io.save_sparse(directory / f"stage{number}.slut", model)
                candidate = {"m": m, "method": name, "stage_semantics": "four_independent_lut_fits",
                              "heldout": evaluate(chain, points, target),
                              "boundary": evaluate(chain, boundary, boundary_target),
                              "models": [asset(directory / f"stage{k}.slut") for k in range(1, 5)]}
                scene_record["candidates"].append(candidate)
                print(json.dumps({"scenario": scene, "m": m, "method": name,
                                  "four_stage": candidate["heldout"]}), flush=True)
            scene_record.setdefault("stage_diagnostics", []).append({"m": m, "stages": details})
            report["elapsed_s"] = time.perf_counter() - beginning
            partial = dict(report, scenarios=[*report["scenarios"], scene_record])
            (args.output / "study.json").write_text(json.dumps(partial, indent=2), encoding="utf-8")
        report["scenarios"].append(scene_record)
        del tables
    report["elapsed_s"] = time.perf_counter() - beginning
    (args.output / "study.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"result": str((args.output / "study.json").resolve()), "elapsed_s": report["elapsed_s"]}), flush=True)


if __name__ == "__main__":
    main()
