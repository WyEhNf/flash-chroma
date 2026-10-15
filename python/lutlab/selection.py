"""Report measured accuracy/speed/memory tradeoffs under an explicit local limit."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from types import SimpleNamespace

from . import cli, data, io, metrics, validation
from .runlog import Run

# Each profile couples the fitting basis to the interpolation actually executed.
PROFILES = {
    "sample": ("seq", "sample", "uniform", "auto"),
    "tetra": ("seq", "ls_tetra_int", "uniform", "auto"),
    "tetra_q16": ("seq", "ls_tetra_q16", "uniform", "auto"),
    "q16": ("seq", "ls_tetra_q16", "uniform", "auto"),
    "tail": ("seq", "tail_tetra_int", "uniform", "auto"),
    "errorgrid": ("seq", "ls_tetra_int", "error", "auto"),
    "dp_jitter": ("seq", "ls_tetra_jitter", "dp", "auto"),
    "dp_boundary": ("seq", "ls_tetra_boundary", "dp", "auto"),
    "dp_structured": ("seq", "ls_tetra_structured", "dp", "auto"),
    "dp_supported": ("seq", "ls_tetra_supported", "dp", "auto"),
    "dp_full": ("seq", "ls_tetra_full", "dp", "auto"),
    "dp_full_box": ("seq", "ls_tetra_full_box", "dp", "auto"),
    "adaptive_full": ("seq", "adaptive_full", "dp", "auto"),
    "dp_guarded": ("seq", "ls_tetra_guarded", "dp", "auto"),
    "residual": ("residual", "ls_tetra_int", "uniform", "auto"),
    "residual_tail": ("residual", "tail_tetra_int", "uniform", "auto"),
    "trilinear": ("seq", "ls_tri", "uniform", "tri_float"),
    "composite": ("composite", "ls_tetra_int", "uniform", "auto"),
}
# R18 improves mean error in the staged study but does not guarantee lower
# worst-case error. Every candidate still passes the requested tail constraint.
# Guarded fitting is explicit: its single-stage guard is not a cascade guarantee.
DEFAULT_PROFILES = ["sample", "tetra", "q16", "errorgrid", "dp_jitter"]


def _quality(accuracy: dict) -> dict:
    images = accuracy["per_image"]
    return {"mean_image_delta_e": sum(image["mean"] for image in images) / len(images),
            "worst_image_mean": max(image["mean"] for image in images),
            "worst_image_p99": max(image["p99"] for image in images),
            "max_image_delta_e": max(image["max"] for image in images),
            "cube_mean": accuracy.get("cube", {}).get("mean"),
            "cube_p99": accuracy.get("cube", {}).get("p99"),
            "cube_max": accuracy.get("cube", {}).get("max")}


def pareto_front(rows: list[dict], objectives: list[str]) -> list[dict]:
    """Return non-dominated measured candidates; every named objective is minimized."""
    return [row for row in rows if not any(
        other is not row
        and all(other["objectives"][key] <= row["objectives"][key] for key in objectives)
        and any(other["objectives"][key] < row["objectives"][key] for key in objectives)
        for other in rows)]


def _summary(row: dict | None) -> dict | None:
    if row is None:
        return None
    fields = ("id", "profile", "m", "mode", "method", "grid", "kernel", "models", "manifest",
              "eligibility", "quality", "memory", "fit_s", "objectives", "bench")
    return {key: row[key] for key in fields if key in row}


def _recommendations(rows: list[dict]) -> dict:
    if not rows:
        return {"speed": None, "accuracy": None, "tail": None, "memory": None,
                "conservative_baseline": None}
    baseline = [row for row in rows if row["profile"] == "tetra"]
    tail_key = "cube_max" if all(row["quality"]["cube_max"] is not None for row in rows) else "max_image_delta_e"
    return {
        "speed": _summary(min(rows, key=lambda row: row["objectives"]["set_ms_p50_rep"])),
        "accuracy": _summary(min(rows, key=lambda row: row["quality"]["mean_image_delta_e"])),
        "tail": _summary(min(rows, key=lambda row: row["quality"][tail_key])),
        "memory": _summary(min(rows, key=lambda row: row["objectives"]["model_bytes"])),
        "conservative_baseline": _summary(min(baseline, key=lambda row: (
            row["quality"][tail_key], row["quality"]["mean_image_delta_e"])) if baseline else None),
    }


def select(scenario: str, sizes: list[int], profiles: list[str], threshold: float,
           eval_list: Path, bench_list: Path, threads: int, reps: int,
           metric: str = "mean", allow_composite: bool = False,
           existing_only: bool = False, full_cube: bool = True, *,
           allow_residual: bool = False, constraint_scope: str = "images",
           executable: str | Path | None = None) -> dict:
    if not sizes or any(not isinstance(m, int) or isinstance(m, bool) or not 17 <= m <= 33 for m in sizes):
        raise ValueError("all m values must be integers in [17,33]")
    if not profiles or any(name not in PROFILES for name in profiles):
        raise ValueError("at least one known profile is required")
    if reps < 1 or threads < 0:
        raise ValueError("reps must be positive and threads nonnegative")
    if not math.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and nonnegative")
    if metric not in ("mean", "p99", "max") or constraint_scope not in ("images", "cube", "both"):
        raise ValueError("invalid metric or constraint scope")
    if not full_cube and constraint_scope != "images":
        raise ValueError("cube constraints require full_cube=True")
    # Fail before fitting if a usable runtime was not supplied.
    binary = metrics.resolve_jshc(executable)
    # A valid model identity cannot make a stale composite file a valid oracle.
    scenario_provenance = data.verify_scenario(scenario)
    rows = []
    for m in dict.fromkeys(sizes):
        for name in dict.fromkeys(profiles):
            mode, method, grid, kernel = PROFILES[name]
            semantics = "independent" if mode == "seq" else mode
            research_allowed = mode == "seq" or (allow_composite if mode == "composite" else allow_residual)
            args = SimpleNamespace(scenario=scenario, m=m, method=method, mode=mode,
                                   grid=grid, adaptive=False, allow_composite=allow_composite,
                                   allow_residual=allow_residual)
            row = {"id": f"{name}-m{m}", "profile": name, "m": m, "mode": mode,
                   "method": method, "grid": grid, "kernel": kernel,
                   "eligibility": "conservative_independent" if mode == "seq" else "research_only",
                   "eligible": mode == "seq", "research_allowed": research_allowed}
            try:
                if not research_allowed:
                    row["status"] = f"ineligible_{mode}"
                    row["reason"] = f"requires explicit --allow-{mode}; no official acceptance is implied"
                else:
                    entry = cli.model_entry(args, existing_only=existing_only)
                    if entry is None:
                        row["status"] = "missing_verified_model"
                    else:
                        paths = entry.paths
                        row["models"] = list(map(str, paths))
                        row["manifest"] = str(entry.directory / "manifest.json")
                        row["fit_s"] = entry.manifest.get("fit", {}).get("fit_s")
                        row["memory"] = {
                            "serialized_model_bytes": sum(path.stat().st_size for path in paths),
                            "node_payload_bytes": sum(io.load_sparse(path).nodes.nbytes for path in paths),
                        }
                        accuracy = validation.validate(paths, data.scenario_dir(scenario) / "composite.lut256",
                            eval_list, kernel=kernel, threads=threads, threshold=threshold,
                            metric=metric, full_cube=full_cube, executable=binary,
                            constraint_scope=constraint_scope, competition=mode == "seq", semantics=semantics)
                        row["accuracy"] = accuracy
                        row["quality"] = _quality(accuracy)
                        row["eligible"] = mode == "seq" and accuracy["submission_contract_pass"]
                        if not accuracy["pass"]:
                            row["status"] = "fail_accuracy"
                        else:
                            row["bench"] = metrics.run_cpp_bench(paths, bench_list, kernel, threads, reps,
                                                                  executable=binary)
                            runtime_bytes = row["bench"].get("model_runtime_bytes")
                            if runtime_bytes is not None:
                                row["memory"]["model_runtime_bytes"] = runtime_bytes
                            row["memory"]["kernel_block_scratch_bytes_per_worker"] = row["bench"].get("kernel_block_scratch_bytes_per_worker")
                            row["memory"]["preloaded_image_bytes"] = row["bench"].get("preloaded_image_bytes")
                            row["memory"]["scope"] = "runtime-reported model objects and vector capacities; images, thread scratch, allocator and process RSS excluded"
                            row["status"] = "pass" if row["eligible"] else "research_pass"
            except Exception as exc:
                row["status"] = "error"
                row["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(row)
            print(f"[select] {name} m={m}: {row['status']}", flush=True)
    passing = [row for row in rows if row.get("status") in ("pass", "research_pass") and "bench" in row]
    runtime_available = bool(passing) and all("model_runtime_bytes" in row["memory"] for row in passing)
    memory_basis = "model_runtime_bytes" if runtime_available else "serialized_model_bytes"
    objectives = ["mean_image_delta_e", "set_ms_p50_rep", "model_bytes"]
    for row in passing:
        row["objectives"] = {"mean_image_delta_e": row["quality"]["mean_image_delta_e"],
                             "set_ms_p50_rep": row["bench"]["set_ms_p50_rep"],
                             "model_bytes": row["memory"][memory_basis]}
    baseline = [row for row in passing if row["eligible"]]
    research = [row for row in passing if not row["eligible"]]
    recommendations = _recommendations(baseline)
    return {"scenario": scenario, "scenario_provenance": scenario_provenance,
            "threshold_strict": threshold, "metric": metric,
            "constraint_scope": constraint_scope, "full_cube_requested": full_cube,
            "allow_composite": allow_composite, "allow_residual": allow_residual,
            "pareto_objectives": objectives, "memory_objective_basis": memory_basis,
            "pareto": [_summary(row) for row in pareto_front(baseline, objectives)],
            "research_pareto": [_summary(row) for row in pareto_front(research, objectives)],
            "recommendations": recommendations, "research_recommendations": _recommendations(research),
            "winner": recommendations["speed"],
            "selection_policy": "winner is the speed recommendation among conservative independent candidates; no total score is inferred",
            "baseline_policy": "among passing independent uniform tetra fits, minimize measured cube max (or image max), then mean image Delta E; grid size is not a quality proxy",
            "quality_scope": "unweighted average of per-image mean RGB Delta E; cube statistics and constraints are reported separately",
            "fit_cost_scope": "recorded fitting wall seconds from each verified model manifest; excluded from runtime benchmark",
            "timing_caution": "single sequential sweep, no paired noise significance claim; retain Pareto alternatives",
            "candidates": rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="isp-0")
    parser.add_argument("--m", type=int, nargs="+", default=[17, 25, 33])
    parser.add_argument("--profiles", nargs="+", choices=list(PROFILES), default=DEFAULT_PROFILES,
                        help="candidate fits; dp_guarded is opt-in and retains all accuracy checks")
    parser.add_argument("--threshold", required=True, type=float)
    parser.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
    parser.add_argument("--constraint-scope", choices=["images", "cube", "both"], default="images")
    parser.add_argument("--eval-list", type=Path, default=data.DATA / "eval.txt")
    parser.add_argument("--bench-list", type=Path, default=data.DATA / "bench.txt")
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--allow-composite", action="store_true")
    parser.add_argument("--allow-residual", action="store_true")
    parser.add_argument("--existing-only", action="store_true")
    parser.add_argument("--skip-cube", action="store_true")
    parser.add_argument("--executable", type=Path)
    args = parser.parse_args(argv)
    with Run("select", vars(args), commit_logs=False) as run:
        result = select(args.scenario, args.m, args.profiles, args.threshold, args.eval_list,
            args.bench_list, args.threads, args.reps, args.metric, args.allow_composite,
            args.existing_only, not args.skip_cube, allow_residual=args.allow_residual,
            constraint_scope=args.constraint_scope, executable=args.executable)
        run.path("selection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        run.metrics.update({"candidates": len(result["candidates"]), "winner": result["winner"] and
                           {key: result["winner"][key] for key in ("profile", "m", "mode")}})
        print(json.dumps({"recommendations": result["recommendations"],
                          "research_recommendations": result["research_recommendations"],
                          "status": {row["id"]: row["status"] for row in result["candidates"]}}, indent=2))
    return 0 if result["winner"] or result["research_recommendations"]["speed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
