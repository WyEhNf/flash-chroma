"""One serial qualification of exact separable-curve fitting and CSR regression.

Nine predeclared cases preserve every R21 counterexample and add two transform
families. Settings are frozen before generating film-11 and stress-13. A global
one-channel optimum never substitutes for native full-chain quality evidence.
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
         ("warp-7", 18), ("isp-19", 18), ("clip-23", 18), ("film-11", 18), ("stress-13", 33)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r22-structured-v3")
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
        "scripts/r21_boundary_study.py", "scripts/r22_structured_study.py", "scripts/r22_fit_comparison.py")})
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "predeclared_cases": CASES, "new_full_lut_seeds": ["film-11", "stress-13"],
        "method": "ls_tetra_structured", "settings_frozen_before_new_data_generation": True,
        "official_score_available": False, "source_sha256": sources,
        "executable_sha256": {str(path): metrics.file_sha256(path) for path in (cpu, cuda)},
        "fit_executions": [], "cases": [], "csr_legacy_regressions": []}
    target = output / "study.json"
    _write_report(target, report)
    check = runtime._execute([sys.executable, "-m", "pytest", "-q", "tests"])
    (output / "pytest.log").write_text(check["stdout"] + check["stderr"], encoding="utf-8")
    report["python_acceptance"] = {key: value for key, value in check.items() if key not in ("stdout", "stderr")}
    _write_report(target, report)
    print(check["stdout"], flush=True)
    if check["returncode"]:
        raise RuntimeError("Python acceptance failed")
    frozen = json.loads((ROOT / "artifacts/r21-boundary/study.json").read_text(encoding="utf-8"))
    known = {(row["scenario"], row["m"]): row for row in frozen["cases"]}
    for scenario, m in CASES:
        known_case = known.get((scenario, m))
        if known_case:
            boundary_path, jitter_path = map(Path, (known_case["result"], known_case["baseline_result"]))
            for path, expected in ((boundary_path, known_case["result_sha256"]), (jitter_path, known_case["baseline_sha256"])):
                if metrics.file_sha256(path) != expected:
                    raise RuntimeError("frozen comparison record changed")
            boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
            jitter = json.loads(jitter_path.read_text(encoding="utf-8"))
            source = Path(boundary["sources"][0]["path"]).parent
            old_jitter = list(map(Path, known_case["baseline_models"]))
            old_boundary = list(map(Path, known_case["models"]))
            for result in (boundary, jitter):
                for name, digest in result["backends"]["cpu"]["model_sha256"].items():
                    if metrics.file_sha256(name) != digest:
                        raise RuntimeError("frozen model changed")
        else:
            source = output / "sources" / scenario
            _generate(source, scenario, sources["python/lutlab/luts.py"])
        jitter_models = _fit(source, scenario, m, "ls_tetra_jitter", output, report["fit_executions"])
        if known_case:
            if any(a.read_bytes() != b.read_bytes() for a, b in zip(jitter_models, old_jitter)):
                raise RuntimeError(f"CSR assembly changed old jitter model bytes: {scenario}/m{m}")
            report["csr_legacy_regressions"].append({"scenario": scenario, "m": m,
                "all_four_models_byte_equal": True, "current_models": list(map(str, jitter_models)),
                "frozen_models": list(map(str, old_jitter))})
        else:
            jitter, jitter_path = _accept(jitter_models, source, scenario, m, "jitter", output, cpu, cuda)
            old_boundary = _fit(source, scenario, m, "ls_tetra_boundary", output, report["fit_executions"])
            boundary, boundary_path = _accept(old_boundary, source, scenario, m, "boundary", output, cpu, cuda)
        models = _fit(source, scenario, m, "ls_tetra_structured", output, report["fit_executions"])
        manifest = json.loads((models[0].parent / "manifest.json").read_text(encoding="utf-8"))
        routes = [stage["structured"]["route"] for stage in manifest["fit"]["stage_info"]]
        for stage, (model, reference, route) in enumerate(zip(models, old_boundary, routes), 1):
            if route == "general_boundary_ls" and model.read_bytes() != reference.read_bytes():
                raise RuntimeError(f"general fallback changed boundary model bytes: {scenario}/m{m}/stage{stage}")
        candidate, candidate_path = _accept(models, source, scenario, m, "structured", output, cpu, cuda)
        compared = _comparison(boundary, candidate)
        report["cases"].append({"scenario": scenario, "m": m, "new_lut_seed": known_case is None,
            "models": list(map(str, models)), "baseline_models": list(map(str, old_boundary)),
            "jitter_models": list(map(str, jitter_models)), "routes": routes,
            "result": str(candidate_path), "result_sha256": metrics.file_sha256(candidate_path),
            "baseline_result": str(boundary_path), "baseline_sha256": metrics.file_sha256(boundary_path),
            "jitter_result": str(jitter_path), "jitter_result_sha256": metrics.file_sha256(jitter_path),
            "comparison": compared, "versus_jitter": _comparison(jitter, candidate)})
        _write_report(target, report)
        mean, maximum = compared["cube"]["mean"], compared["cube"]["max"]
        print(f"[structured] {scenario}/m{m}: mean {mean['baseline']:.6f}->{mean['candidate']:.6f}; "
              f"max {maximum['baseline']:.6f}->{maximum['candidate']:.6f}; {routes}", flush=True)
    command = [sys.executable, str(ROOT / "scripts/r22_fit_comparison.py"),
               "--output", str(output / "fit-comparison.json")]
    comparison = runtime._execute(command)
    (output / "fit-comparison.log").write_text(comparison["stdout"] + comparison["stderr"], encoding="utf-8")
    report["performance_comparison"] = {"command": command, "returncode": comparison["returncode"],
                                       "log": str(output / "fit-comparison.log")}
    if comparison["returncode"]:
        _write_report(target, report)
        raise RuntimeError("paired full-fit comparison failed")
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError(f"study source changed: {name}")
    for name, digest in report["executable_sha256"].items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("backend binary changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                  structural_and_parity_pass=True, csr_legacy_byte_regression_pass=True)
    _write_report(target, report)


if __name__ == "__main__":
    main()
