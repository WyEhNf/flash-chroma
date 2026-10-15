"""Freeze and serially qualify boundary-complete LS on known and new LUT seeds.

The model uses four independent original LUT targets, with unchanged DP grids,
integer nodes and Q16 runtime semantics. New seeds are fixed before generation;
no fitting settings are selected from their outputs in this batch.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cache, cli, fit, interp, io, luts, metrics, qualification, runtime
from lutlab.entry import _write_report

CASES = [("isp-0", 18), ("clip-7", 17), ("clip-7", 18), ("clip-7", 33),
         ("warp-7", 18), ("isp-19", 18), ("clip-23", 18)]


def _generate(source, scenario, generator_sha):
    marker = source / "meta.json"
    if marker.exists():
        metadata = json.loads(marker.read_text(encoding="utf-8"))
        if metadata["generator_sha256"] != generator_sha or metadata["scenario"] != scenario:
            raise RuntimeError("existing generated source has a different identity")
        for name, digest in metadata["sha256"].items():
            if metrics.file_sha256(source / name) != digest:
                raise RuntimeError("existing generated source was modified")
        return metadata
    source.mkdir(parents=True, exist_ok=True)
    family, seed = luts.parse_scenario(scenario)
    stages = luts.scenario(family, seed)
    tables = []
    started = time.perf_counter()
    with np.errstate(all="ignore"):
        for index, stage in enumerate(stages, 1):
            table = luts.build_lut(stage)
            io.save_full(source / f"lut{index}.lut256", table)
            tables.append(table)
    io.save_full(source / "composite.lut256", io.compose(tables))
    metadata = {"scenario": scenario, "generator_sha256": generator_sha,
        "stages": json.loads(luts.describe(stages)), "build_seconds": time.perf_counter() - started,
        "sha256": {name: metrics.file_sha256(source / name) for name in [
            *(f"lut{k}.lut256" for k in range(1, 5)), "composite.lut256"]}}
    _write_report(marker, metadata)
    return metadata


def _fit(source, scenario, m, method, output, executions):
    namespace = output / "models" / scenario / f"{method}_m{m}"
    inputs = [source / f"lut{k}.lut256" for k in range(1, 5)]
    command = [sys.executable, "-m", "lutlab", "fit", "--scenario", scenario,
        "--inputs", *map(str, inputs), "--m", str(m), "--method", method, "--grid", "dp",
        "--model-dir", str(namespace)]
    process = runtime._execute(command)
    log = output / f"fit-{scenario}-m{m}-{method}.log"
    log.write_text(process["stdout"] + process["stderr"], encoding="utf-8")
    executions.append({"command": command, "log": str(log), "log_sha256": metrics.file_sha256(log),
                       **{key: value for key, value in process.items() if key not in ("stdout", "stderr")}})
    if process["returncode"]:
        raise RuntimeError(f"fit failed: {log}")
    parameters = SimpleNamespace(scenario=scenario, m=m, method=method, mode="seq", grid="dp",
        adaptive=False, inputs=inputs, model_dir=namespace, allow_composite=False, allow_residual=False)
    entry = cli.model_entry(parameters, existing_only=True)
    if entry is None:
        raise RuntimeError("public fitting entry did not publish a current verified batch")
    return entry.paths


def _accept(models, source, scenario, m, label, output, cpu, cuda):
    target = output / f"acceptance-{scenario}-m{m}-{label}.json"
    options = SimpleNamespace(models=models, full_luts=[source / f"lut{k}.lut256" for k in range(1, 5)],
        reference=source / "composite.lut256", images=ROOT / "artifacts/r17-acceptance/bench.txt",
        backend="both", cpu_executable=cpu, cuda_executable=cuda, kernel="tetra_avx2", threads=4,
        device=0, threshold=2., threshold_origin="illustrative", metric="mean", allow_declared_models=False,
        output=target)
    result = qualification.accept(options)
    if not (result["structural_contract_pass"] and result["backend_cube_sha256_equal"]
            and result["backend_images_sha256_equal"]):
        raise RuntimeError(f"structural or execution parity failed: {target}")
    return result, target


def _comparison(baseline, candidate):
    left, right = baseline["backends"]["cpu"], candidate["backends"]["cpu"]
    if baseline["sources"] != candidate["sources"] or baseline["images"] != candidate["images"]:
        raise RuntimeError("baseline and candidate do not use identical inputs")
    return {"cube": {key: {"baseline": left["cube"][key], "candidate": right["cube"][key],
                           "change": right["cube"][key] - left["cube"][key]}
                     for key in ("mean", "rms", "p99", "max")},
        "worst_image_mean": {"baseline": left["worst_image_metric"], "candidate": right["worst_image_metric"]},
        "image_improvements": {metric: sum(b[metric] < a[metric] for a, b in zip(left["per_image"], right["per_image"]))
                               for metric in ("mean", "p99", "max")},
        "image_regressions": {metric: sum(b[metric] > a[metric] for a, b in zip(left["per_image"], right["per_image"]))
                              for metric in ("mean", "p99", "max")},
        "local_mean_gate": {"baseline": baseline["pass"], "candidate": candidate["pass"]},
        "all_cube_metrics_nonregressing": all(right["cube"][key] <= left["cube"][key]
                                               for key in ("mean", "rms", "p99", "max"))}


def _baseline_support(models):
    model = io.load_sparse(models[1])  # clip-7 stage 2: the smooth-tone hotspot
    points = fit.stratified_points()
    I, W = interp.tetra_weights(points, *model.tables(), model.m)
    diagonal = np.bincount(I.ravel(), weights=(W * W).ravel(), minlength=model.m ** 3)
    coordinates = np.indices((model.m,) * 3).reshape(3, -1)
    boundary = np.any((coordinates == 0) | (coordinates == model.m - 1), axis=0)
    return {"stage": 2, "m": model.m, "sample_count": len(points),
        "sampled_boundary_colors": int(np.count_nonzero(np.any((points == 0) | (points == 255), axis=1))),
        "boundary_nodes": int(boundary.sum()), "zero_diagonal_nodes": int(np.count_nonzero(diagonal == 0)),
        "minimum_diagonal": float(diagonal.min()), "minimum_boundary_diagonal": float(diagonal[boundary].min()),
        "model_sha256": metrics.file_sha256(models[1]),
        "note": "diagonal support diagnostic only, not an estimate of the full matrix condition number"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r21-boundary")
    args = parser.parse_args()
    cpu, cuda, output = args.cpu.resolve(), args.cuda.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      JSHC_BIN=str(cpu), JSHC_CUDA_BIN=str(cuda))
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    started = time.perf_counter()
    sources = {f"python/lutlab/{name}": digest for name, digest in cache.source_fingerprint().items()
               if name != "pixi.lock"}
    sources.update({"pixi.lock": metrics.file_sha256(ROOT / "pixi.lock"),
        "python/lutlab/luts.py": metrics.file_sha256(ROOT / "python/lutlab/luts.py"),
        "python/lutlab/validation.py": metrics.file_sha256(ROOT / "python/lutlab/validation.py"),
        "python/lutlab/qualification.py": metrics.file_sha256(ROOT / "python/lutlab/qualification.py"),
        "scripts/r21_boundary_study.py": metrics.file_sha256(Path(__file__))})
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "predeclared_cases": CASES, "new_full_lut_seeds": ["isp-19", "clip-23"],
        "method": "ls_tetra_boundary", "settings_frozen_before_new_data_generation": True,
        "official_score_available": False, "source_sha256": sources,
        "executable_sha256": {str(path): metrics.file_sha256(path) for path in (cpu, cuda)},
        "fit_executions": [], "cases": []}
    target = output / "study.json"
    _write_report(target, report)
    check = runtime._execute([sys.executable, "-m", "pytest", "-q", "tests"])
    (output / "pytest.log").write_text(check["stdout"] + check["stderr"], encoding="utf-8")
    report["python_acceptance"] = {key: value for key, value in check.items() if key not in ("stdout", "stderr")}
    _write_report(target, report)
    print(check["stdout"], flush=True)
    if check["returncode"]:
        raise RuntimeError("Python acceptance failed")
    frozen = json.loads((ROOT / "artifacts/r20-validation/audit.json").read_text(encoding="utf-8"))
    known = {(row["scenario"], row["m"]): row for row in frozen["cases"]}
    for scenario, m in CASES:
        known_case = known.get((scenario, m))
        if known_case:
            baseline_path = Path(known_case["result"])
            if metrics.file_sha256(baseline_path) != known_case["result_sha256"]:
                raise RuntimeError("frozen baseline evidence changed")
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            source = Path(baseline["sources"][0]["path"]).parent
            baseline_models = list(map(Path, known_case["models"]))
            for path, digest in baseline["backends"]["cpu"]["model_sha256"].items():
                if metrics.file_sha256(path) != digest:
                    raise RuntimeError("frozen baseline model changed")
            if scenario == "clip-7" and m == 33:
                report["baseline_support_diagnostic"] = _baseline_support(baseline_models)
        else:
            source = output / "sources" / scenario
            _generate(source, scenario, sources["python/lutlab/luts.py"])
            baseline_models = _fit(source, scenario, m, "ls_tetra_jitter", output, report["fit_executions"])
            baseline, baseline_path = _accept(baseline_models, source, scenario, m, "jitter", output, cpu, cuda)
        models = _fit(source, scenario, m, "ls_tetra_boundary", output, report["fit_executions"])
        candidate, candidate_path = _accept(models, source, scenario, m, "boundary", output, cpu, cuda)
        comparison = _comparison(baseline, candidate)
        report["cases"].append({"scenario": scenario, "m": m, "new_lut_seed": known_case is None,
            "models": list(map(str, models)), "baseline_models": list(map(str, baseline_models)),
            "result": str(candidate_path), "result_sha256": metrics.file_sha256(candidate_path),
            "baseline_result": str(baseline_path), "baseline_sha256": metrics.file_sha256(baseline_path),
            "comparison": comparison})
        _write_report(target, report)
        mean, maximum = comparison["cube"]["mean"], comparison["cube"]["max"]
        print(f"[boundary] {scenario}/m{m}: mean {mean['baseline']:.6f}->{mean['candidate']:.6f}; "
              f"max {maximum['baseline']:.6f}->{maximum['candidate']:.6f}", flush=True)
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError(f"study source changed during execution: {name}")
    for name, digest in report["executable_sha256"].items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("backend binary changed during execution")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                  elapsed_seconds=time.perf_counter() - started, structural_and_parity_pass=True)
    _write_report(target, report)


if __name__ == "__main__":
    main()
