"""CLI for data, traceable model fitting, evaluation, and benchmarking."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from . import cache, cascade, data, interp, io, luts, metrics
from .runlog import Run
from .axisbins import PROFILES as BIN_PROFILES

METHODS = ("sample", "sample_interp", "box", "ls_tri", "ls_tetra", "ls_tetra_int",
           "ls_tetra_q16", "ls_tetra_jitter", "ls_tetra_boundary", "ls_tetra_structured", "ls_tetra_supported", "ls_tetra_calibrated", "ls_tetra_full", "ls_tetra_full_box",
           "ls_tetra_guarded", "irls_tetra", "tail_tetra_int", "adaptive_full", *BIN_PROFILES)
GRIDS = ("uniform", "curvature", "error", "dp")


def fit_parameters(args) -> dict:
    if not isinstance(args.m, int) or isinstance(args.m, bool) or not 17 <= args.m <= 33:
        raise ValueError("competition model grid size m must be in [17,33]")
    if args.mode not in ("seq", "residual", "composite") or args.method not in METHODS:
        raise ValueError("unsupported fitting mode or method")
    if args.mode == "residual" and args.method not in ("ls_tetra_int", "tail_tetra_int"):
        raise ValueError("residual fitting supports ls_tetra_int and tail_tetra_int only")
    if args.method == "adaptive_full" and args.mode != "seq":
        raise ValueError("adaptive_full supports four independent sequential stages only")
    if args.method == 'ls_tetra_calibrated' and args.mode != 'seq':
        raise ValueError('解析坐标校准仅支持四张独立原表的seq模式')
    if args.method in BIN_PROFILES and args.mode!="seq":
        raise ValueError("bin/prefix candidates require four independent sequential stages")
    grid = getattr(args, "grid", None) or ("curvature" if getattr(args, "adaptive", False) else "uniform")
    if grid not in GRIDS:
        raise ValueError(f"unknown grid mode: {grid}")
    if args.method in ("ls_tetra_supported", "ls_tetra_calibrated", "ls_tetra_full", "ls_tetra_full_box", "adaptive_full", *BIN_PROFILES) and grid != "dp":
        raise ValueError(f"{args.method} requires --grid dp for exact integer vertex observations")
    if getattr(args, "adaptive", False) and grid != "curvature":
        raise ValueError("--adaptive conflicts with a non-curvature --grid")
    return {"m": args.m, "mode": args.mode, "method": args.method, "grid": grid,
            "interpolation_basis": "trilinear_float" if args.method == "ls_tri" else "tetra_q16",
            "semantics": {"seq": "independent", "residual": "residual", "composite": "composite"}[args.mode],
            "n_stages": 1 if args.mode == "composite" else 4,
            "residual_tail_beta": 1.0 if args.mode == "residual" and args.method == "tail_tetra_int" else 0.0}


def _check_research_permission(args) -> None:
    for mode in ("residual", "composite"):
        if args.mode == mode and not getattr(args, f"allow_{mode}", False):
            raise ValueError(f"{mode} is a research mode; explicitly pass --allow-{mode}")


def model_dir(args) -> Path:
    """Readable namespace; only verified batches below it are reusable models."""
    parameters = fit_parameters(args)
    if getattr(args, "model_dir", None) is not None:
        return Path(args.model_dir)
    variant = f"{args.mode}_{args.method}_m{args.m}"
    if parameters["grid"] == "error":
        variant += "_errorgrid"
    elif parameters["grid"] == "curvature":
        variant += "_adaptive"
    elif parameters["grid"] == "dp":
        variant += "_dpgrid"
    return data.DATA / "models" / args.scenario / variant


def _source_paths(args, *, create: bool) -> list[Path]:
    supplied = getattr(args, "inputs", None)
    if supplied is not None:
        if len(supplied) != 4:
            raise ValueError("--inputs requires exactly four full LUT files, in stage order")
        paths = [Path(path) for path in supplied]
    else:
        directory = data.scenario_dir(args.scenario)
        paths = [directory / f"lut{k}.lut256" for k in range(1, 5)]
        if create and not any(path.exists() for path in paths) and not (directory / "meta.json").exists():
            data.build_scenario(args.scenario)
    for path in paths:
        if path.stat().st_size != io.FULL_NBYTES:
            raise ValueError(f"incorrect source LUT size: {path}")
    return paths


def model_entry(args, *, existing_only: bool = False) -> cache.Entry | None:
    _check_research_permission(args)
    parameters = fit_parameters(args)
    sources = _source_paths(args, create=not existing_only)
    identity = cache.build_identity(sources, parameters)
    entry = cache.lookup(model_dir(args), identity)
    if entry is not None or existing_only:
        return entry
    return cmd_fit(args, identity=identity)


def model_paths(args) -> list[Path]:
    entry = model_entry(args)
    if entry is None:
        raise RuntimeError("fitter did not publish a verified model batch")
    return entry.paths


def cmd_gen_data(args):
    with Run("gen-data", {"scenarios": args.scenarios, "seed": args.seed}, commit_logs=False) as run:
        lists = data.build_images(seed=args.seed, allow_synthetic_only=args.allow_synthetic_only)
        for scenario in args.scenarios:
            metadata = data.build_scenario(scenario, force=args.force)
            print(f"[gen-data] scenario {scenario} ready (build_s={metadata['build_s']}s)")
        run.metrics.update({"image_lists": lists, "n_scenarios": len(args.scenarios)})


def cmd_fit(args, *, identity: dict | None = None) -> cache.Entry:
    _check_research_permission(args)
    parameters = fit_parameters(args)
    sources = _source_paths(args, create=True)
    identity = identity or cache.build_identity(sources, parameters)
    if entry := cache.lookup(model_dir(args), identity):
        print(f"[fit] verified cache hit: {entry.directory}")
        return entry
    with Run("fit", {"scenario": args.scenario, **parameters}, commit_logs=False) as run:
        tables = [io.load_full(path) for path in sources]
        # Check fitted bytes, rather than trusting an earlier file hash.
        for table, record in zip(tables, identity["inputs"]):
            if hashlib.sha256(memoryview(np.ascontiguousarray(table))).hexdigest() != record["sha256"]:
                raise RuntimeError("source LUT changed while loading; no model published")
        grid = parameters["grid"]
        try:
            if args.mode == "seq":
                chain, info = cascade.fit_cascade_sequential(tables, args.m, args.method, grid_mode=grid)
            elif args.mode == "residual":
                chain, info = cascade.fit_cascade_residual(tables, args.m,
                    tail_beta=parameters["residual_tail_beta"], grid_mode=grid)
            else:
                chain, info = cascade.fit_composite_single(tables, args.m, args.method, grid_mode=grid)
        except Exception as exc:
            if hasattr(exc, "diagnostics"):
                run.metrics["solver_failure"] = exc.diagnostics
            raise
        # Reject a mixed source/code version if files changed while fitting.
        if cache.build_identity(sources, parameters) != identity:
            raise RuntimeError("input, solver, or fitting code changed during fit; no model published")
        entry = cache.publish(model_dir(args), identity, chain, info)
        run.metrics.update(info | {"slut_paths": list(map(str, entry.paths)), "n_stages": len(chain),
                                   "manifest": str(entry.directory / "manifest.json"),
                                   "identity_sha256": entry.manifest["identity_sha256"]})
        print(json.dumps(run.metrics, indent=2))
    return entry


def cmd_evaluate(args):
    if args.method == "ls_tri":
        raise ValueError("ls_tri requires its actual tri_float backend; use lutlab.validation or selection")
    with Run("evaluate", {"scenario": args.scenario, **fit_parameters(args)}, commit_logs=False) as run:
        entry = model_entry(args)
        if entry is None:
            raise RuntimeError("fitter did not publish a verified model batch")
        sluts = [io.load_sparse(path, competition=True) for path in entry.paths]
        if getattr(args, "inputs", None) is not None:
            tables = [io.load_full(path) for path in _source_paths(args, create=False)]
            hashes = [hashlib.sha256(memoryview(np.ascontiguousarray(table))).hexdigest() for table in tables]
            if hashes != [record["sha256"] for record in entry.manifest["identity"]["inputs"]]:
                raise RuntimeError("source LUT changed after fitting; evaluation rejected")
            composite = io.compose(tables)
            run.metrics["scenario"] = {"source": "explicit_full_luts", "sha256": hashes}
            del tables
        else:
            run.metrics["scenario"] = data.verify_scenario(args.scenario)
            composite = io.load_full(data.scenario_dir(args.scenario) / "composite.lut256")

        def predict(image):
            for model in sluts:
                image = interp.apply_tetra_q16(model, image)
            return image

        image_list = [data.ROOT / line.strip() for line in (data.DATA / "eval.txt").read_text().splitlines()
                      if line.strip()]
        evaluation = metrics.eval_images(predict, composite, image_list)
        summary = {key: value for key, value in evaluation.items() if key != "per_image"}
        run.metrics.update(summary)
        run.path("eval_detail.json").write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))


def cmd_bench(args):
    kernel = "tri_float" if args.method == "ls_tri" and args.kernel == "auto" else args.kernel
    with Run("bench", {"scenario": args.scenario, **fit_parameters(args),
                       "kernel": kernel, "threads": args.threads}, commit_logs=False) as run:
        benchmark = metrics.run_cpp_bench(model_paths(args), data.DATA / "bench.txt", kernel=kernel,
            threads=args.threads, reps=args.reps, executable=args.executable)
        run.metrics.update(benchmark)
        print(json.dumps(benchmark, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lutlab")
    commands = parser.add_subparsers(dest="cmd", required=True)
    generate = commands.add_parser("gen-data")
    generate.add_argument("--scenarios", nargs="+", default=luts.DEFAULT_SCENARIOS)
    generate.add_argument("--seed", type=int, default=0)
    generate.add_argument("--force", action="store_true")
    generate.add_argument("--allow-synthetic-only", action="store_true")
    for name in ("fit", "evaluate", "bench"):
        command = commands.add_parser(name)
        command.add_argument("--scenario", default="isp-0")
        command.add_argument("--inputs", nargs=4, type=Path, metavar=("LUT1", "LUT2", "LUT3", "LUT4"),
                             help="four raw 256^3 RGB8 LUTs in stage order; overrides scenario source files")
        command.add_argument("--model-dir", type=Path,
                             help="immutable model-batch namespace; input contents determine cache identity")
        command.add_argument("--m", type=int, choices=range(17, 34), default=33)
        command.add_argument("--method", choices=METHODS, default="ls_tetra_int")
        command.add_argument("--mode", choices=["seq", "residual", "composite"], default="seq")
        command.add_argument("--adaptive", action="store_true")
        command.add_argument("--grid", choices=GRIDS, default=None)
        command.add_argument("--allow-composite", action="store_true", help="enable research with one composed stage")
        command.add_argument("--allow-residual", action="store_true", help="enable research with cross-stage residual fitting")
        if name == "bench":
            command.add_argument("--kernel", default="auto")
            command.add_argument("--threads", type=int, default=0)
            command.add_argument("--reps", type=int, default=5)
            command.add_argument("--executable", type=Path)
    args = parser.parse_args(argv)
    {"gen-data": cmd_gen_data, "fit": cmd_fit, "evaluate": cmd_evaluate, "bench": cmd_bench}[args.cmd](args)


if __name__ == "__main__":
    main(sys.argv[1:])
