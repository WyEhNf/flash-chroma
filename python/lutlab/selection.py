"""Select the fastest executable candidate that passes an explicit accuracy limit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from . import cli, data, metrics, validation
from .runlog import Run

# Each tuple couples its fitting basis to the actual interpolation kernel.
PROFILES = {
    "sample": ("seq", "sample", "uniform", "tetra_zig_simd"),
    "tetra": ("seq", "ls_tetra_int", "uniform", "tetra_zig_simd"),
    "tail": ("seq", "tail_tetra_int", "uniform", "tetra_zig_simd"),
    "errorgrid": ("seq", "ls_tetra_int", "error", "tetra_zig_simd"),
    "residual": ("residual", "ls_tetra_int", "uniform", "tetra_zig_simd"),
    "residual_tail": ("residual", "tail_tetra_int", "uniform", "tetra_zig_simd"),
    "trilinear": ("seq", "ls_tri", "uniform", "tri_float"),
    "composite": ("composite", "ls_tetra_int", "uniform", "tetra_zig_simd"),
}


def select(scenario: str, sizes: list[int], profiles: list[str], threshold: float,
           eval_list: Path, bench_list: Path, threads: int, reps: int,
           metric: str = "mean", allow_composite: bool = False,
           existing_only: bool = False, full_cube: bool = True) -> dict:
    if not sizes or any(not 17 <= m <= 33 for m in sizes):
        raise ValueError("all m values must be in [17,33]")
    if reps < 1:
        raise ValueError("reps must be positive")
    rows = []
    for m in sizes:
        for name in profiles:
            mode, method, grid, kernel = PROFILES[name]
            args = SimpleNamespace(scenario=scenario, m=m, method=method, mode=mode,
                                   grid=grid, adaptive=False)
            row = {"profile": name, "m": m, "mode": mode, "method": method,
                   "grid": grid, "kernel": kernel, "eligible": mode != "composite" or allow_composite}
            try:
                if existing_only:
                    paths = sorted(cli.model_dir(args).glob("stage*.slut"))
                    if len(paths) != (1 if mode == "composite" else 4):
                        row["status"] = "missing_model"
                        rows.append(row)
                        continue
                else:
                    paths = cli.model_paths(args)
                row["models"] = list(map(str, paths))
                accuracy = validation.validate(paths, data.scenario_dir(scenario) / "composite.lut256",
                                               eval_list, kernel=kernel, threads=threads,
                                               threshold=threshold, metric=metric, full_cube=full_cube)
                row["accuracy"] = accuracy
                row["status"] = "pass" if accuracy["pass"] else "fail_accuracy"
                if accuracy["pass"] and row["eligible"]:
                    row["bench"] = metrics.run_cpp_bench(paths, bench_list, kernel, threads, reps)
                elif accuracy["pass"]:
                    row["status"] = "ineligible_composite"
            except Exception as exc:
                row["status"] = "error"
                row["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(row)
            print(f"[select] {name} m={m}: {row['status']}", flush=True)
    passing = [x for x in rows if x.get("status") == "pass" and "bench" in x]
    winner = min(passing, key=lambda x: x["bench"]["set_ms_p50_rep"]) if passing else None
    return {"scenario": scenario, "threshold_strict": threshold, "metric": metric,
            "full_cube_checked": full_cube, "allow_composite": allow_composite,
            "winner": None if winner is None else {k: winner[k] for k in
                ("profile", "m", "mode", "method", "grid", "kernel", "models", "bench")},
            "candidates": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", default="isp-0")
    ap.add_argument("--m", type=int, nargs="+", default=[17, 25, 33])
    ap.add_argument("--profiles", nargs="+", choices=list(PROFILES), default=list(PROFILES))
    ap.add_argument("--threshold", required=True, type=float)
    ap.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
    ap.add_argument("--eval-list", type=Path, default=data.DATA / "eval.txt")
    ap.add_argument("--bench-list", type=Path, default=data.DATA / "bench.txt")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--allow-composite", action="store_true")
    ap.add_argument("--existing-only", action="store_true")
    ap.add_argument("--skip-cube", action="store_true")
    args = ap.parse_args(argv)
    with Run("select", vars(args)) as run:
        result = select(args.scenario, args.m, args.profiles, args.threshold, args.eval_list,
                        args.bench_list, args.threads, args.reps, args.metric,
                        args.allow_composite, args.existing_only, not args.skip_cube)
        run.path("selection.json").write_text(json.dumps(result, indent=2))
        run.metrics.update({"candidates": len(result["candidates"]), "winner": result["winner"] and
                            {k: result["winner"][k] for k in ("profile", "m", "mode")}})
        print(json.dumps({"winner": result["winner"],
                          "status": {f"{r['profile']}-m{r['m']}": r['status'] for r in result["candidates"]}}, indent=2))
    return 0 if result["winner"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
