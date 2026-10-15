"""One serial study of unbiased, fully supported independent-LUT fitting.

Every integer grid vertex is observed once with weight 1/64. Exact boundary
colors and rejection-sampled remaining interior form a disjoint partition of
uniform RGB measure. Thus the unregularised data Hessian contains I/64, unlike
the previous boundary-only design. Runtime tables and Q16 kernels are unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cache, io, metrics, runtime
from lutlab.entry import _write_report
from r21_boundary_study import _accept, _comparison, _fit, _generate

CASES = [("isp-0", 18), ("clip-7", 17), ("clip-7", 18), ("clip-7", 33),
         ("warp-7", 18), ("isp-19", 18), ("clip-23", 18), ("film-11", 18), ("stress-13", 33),
         ("isp-29", 18), ("clip-31", 18)]


def _fit_record(models):
    path = models[0].parent / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return {"manifest": str(path), "manifest_sha256": metrics.file_sha256(path),
            "fit": manifest["fit"], "models": manifest["models"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r24-supported")
    args = parser.parse_args()
    cpu, cuda, output = args.cpu.resolve(), args.cuda.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      JSHC_BIN=str(cpu), JSHC_CUDA_BIN=str(cuda))
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    started = time.perf_counter()
    sources = {f"python/lutlab/{name}": digest for name, digest in cache.source_fingerprint().items()
               if name != "pixi.lock"}
    sources.update({name: metrics.file_sha256(ROOT / name) for name in (
        "pixi.lock", "python/lutlab/luts.py", "python/lutlab/validation.py", "python/lutlab/qualification.py",
        "scripts/r21_boundary_study.py", "scripts/r24_supported_study.py", "scripts/trace_acceptance_hotspots.py",
        "tests/test_fit_contract.py", "tests/test_cache_contract.py")})
    frozen_path = ROOT / "artifacts/r22-structured-v3/study.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if not frozen.get("structural_and_parity_pass"):
        raise RuntimeError("requires the completed R22 comparison")
    known = {(row["scenario"], row["m"]): row for row in frozen["cases"]}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "predeclared_cases": CASES, "new_full_lut_seeds": ["isp-29", "clip-31"],
        "method": "ls_tetra_supported", "settings_frozen_before_new_data_generation": True,
        "official_score_available": False, "source_sha256": sources,
        "frozen_baseline": {"path": str(frozen_path), "sha256": metrics.file_sha256(frozen_path)},
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
    for scenario, m in CASES:
        old = known.get((scenario, m))
        if old:
            baseline_path = Path(old["result"])
            if metrics.file_sha256(baseline_path) != old["result_sha256"]:
                raise RuntimeError("frozen baseline report changed")
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            source = Path(baseline["sources"][0]["path"]).parent
            old_models = list(map(Path, old["models"]))
            for name, digest in baseline["backends"]["cpu"]["model_sha256"].items():
                if metrics.file_sha256(name) != digest:
                    raise RuntimeError("frozen baseline model changed")
        else:
            source = output / "sources" / scenario
            _generate(source, scenario, sources["python/lutlab/luts.py"])
            old_models = _fit(source, scenario, m, "ls_tetra_structured", output, report["fit_executions"])
            baseline, baseline_path = _accept(old_models, source, scenario, m, "structured", output, cpu, cuda)
        baseline_fit = _fit_record(old_models)
        models = _fit(source, scenario, m, "ls_tetra_supported", output, report["fit_executions"])
        candidate_fit = _fit_record(models)
        routes = [s["structured"]["route"] for s in candidate_fit["fit"]["stage_info"]]
        for stage, (path, reference, info) in enumerate(zip(models, old_models, candidate_fit["fit"]["stage_info"]), 1):
            detail = info["structured"]
            if detail["route"] == "verified_axis_separable":
                if path.read_bytes() != reference.read_bytes():
                    raise RuntimeError("unchanged curve route changed frozen model bytes")
            else:
                ls = detail["least_squares"]
                if (ls["zero_diagonal_nodes"] != 0 or ls["minimum_diagonal"] < 1 / 64
                        or ls["full_grid_vertex_count"] != m ** 3 or ls["sample_weight_sum"] != 64 ** 3):
                    raise RuntimeError(f"supported-design invariant failed: {scenario}/m{m}/stage{stage}")
        candidate, candidate_path = _accept(models, source, scenario, m, "supported", output, cpu, cuda)
        comparison = _comparison(baseline, candidate)
        report["cases"].append({"scenario": scenario, "m": m, "new_lut_seed": old is None,
            "models": list(map(str, models)), "baseline_models": list(map(str, old_models)), "routes": routes,
            "result": str(candidate_path), "result_sha256": metrics.file_sha256(candidate_path),
            "baseline_result": str(baseline_path), "baseline_sha256": metrics.file_sha256(baseline_path),
            "candidate_fit": candidate_fit, "baseline_fit": baseline_fit, "comparison": comparison})
        _write_report(target, report)
        mean, maximum = comparison["cube"]["mean"], comparison["cube"]["max"]
        print(f"[supported] {scenario}/m{m}: mean {mean['baseline']:.6f}->{mean['candidate']:.6f}; "
              f"max {maximum['baseline']:.6f}->{maximum['candidate']:.6f}", flush=True)
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError(f"study source changed: {name}")
    for name, digest in report["executable_sha256"].items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("backend binary changed")
    if metrics.file_sha256(frozen_path) != report["frozen_baseline"]["sha256"]:
        raise RuntimeError("frozen baseline index changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                  structural_parity_and_support_pass=True)
    _write_report(target, report)


if __name__ == "__main__":
    main()
