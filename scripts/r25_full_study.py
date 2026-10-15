"""Serial exact full-domain fitting study on the frozen eleven-case corpus.

General 3D stages use all 256^3 colours, integer Q16 moments, and the same DP
grid, prior, regularisation and integer refinement as the sampled methods.
Proved 1D stages retain their R22 integer-curve solution byte for byte. Both
R22 structured and R24 supported results remain comparison baselines.
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
from lutlab import cache, fullfit, metrics, runtime
from lutlab.entry import _write_report
from r21_boundary_study import _accept, _comparison, _fit
from r24_supported_study import _fit_record

CASES = [("isp-0", 18), ("clip-7", 17), ("clip-7", 18), ("clip-7", 33),
         ("warp-7", 18), ("isp-19", 18), ("clip-23", 18), ("film-11", 18), ("stress-13", 33),
         ("isp-29", 18), ("clip-31", 18)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r25-full")
    args = parser.parse_args()
    cpu, cuda, output = args.cpu.resolve(), args.cuda.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
        OMP_DYNAMIC="FALSE", OMP_THREAD_LIMIT="32", JSHC_BIN=str(cpu), JSHC_CUDA_BIN=str(cuda),
        JSHC_FULL_FIT_LIB=str(fullfit.resolve_library()))
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    started = time.perf_counter()
    sources = {f"python/lutlab/{name}": digest for name, digest in cache.source_fingerprint().items() if name != "pixi.lock"}
    sources.update({name: metrics.file_sha256(ROOT / name) for name in (
        "pixi.lock", "CMakeLists.txt", *fullfit.NATIVE_SOURCES, "python/lutlab/validation.py", "python/lutlab/qualification.py",
        "scripts/r21_boundary_study.py", "scripts/r24_supported_study.py", "scripts/r25_full_study.py",
        "tests/test_fullfit_contract.py", "tests/test_cache_contract.py")})
    old_path = ROOT / "artifacts/r24-supported/study.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    if not old.get("structural_parity_and_support_pass"):
        raise RuntimeError("requires the completed R24 corpus and comparison evidence")
    known = {(row["scenario"], row["m"]): row for row in old["cases"]}
    trainer = fullfit.trainer_fingerprint()
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "predeclared_cases": CASES, "new_data_generated": False, "method": "ls_tetra_full",
        "official_score_available": False, "source_sha256": sources, "trainer": trainer,
        "frozen_baseline": {"path": str(old_path), "sha256": metrics.file_sha256(old_path)},
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
        raise RuntimeError("full-domain independent oracle or Python acceptance failed")
    for scenario, m in CASES:
        previous = known[(scenario, m)]
        paths = {"r22": Path(previous["baseline_result"]), "r24": Path(previous["result"])}
        expected = {"r22": previous["baseline_sha256"], "r24": previous["result_sha256"]}
        baselines = {}
        for mode, path in paths.items():
            if metrics.file_sha256(path) != expected[mode]:
                raise RuntimeError("frozen accuracy baseline changed")
            value = json.loads(path.read_text(encoding="utf-8"))
            for name, digest in value["backends"]["cpu"]["model_sha256"].items():
                if metrics.file_sha256(name) != digest:
                    raise RuntimeError("frozen model changed")
            baselines[mode] = value
        source = Path(baselines["r22"]["sources"][0]["path"]).parent
        reference_models = list(map(Path, previous["baseline_models"]))
        models = _fit(source, scenario, m, "ls_tetra_full", output, report["fit_executions"])
        candidate_fit = _fit_record(models)
        routes = [stage["structured"]["route"] for stage in candidate_fit["fit"]["stage_info"]]
        for path, reference, stage in zip(models, reference_models, candidate_fit["fit"]["stage_info"]):
            detail = stage["structured"]
            if detail["route"] == "verified_axis_separable":
                if path.read_bytes() != reference.read_bytes():
                    raise RuntimeError("unchanged 1D route changed its frozen bytes")
            else:
                ls = detail["least_squares"]
                if (detail["route"] != "general_full_ls" or ls["sample_count"] != 256 ** 3
                        or ls["sample_weight_sum"] != 64 ** 3 or ls["zero_diagonal_nodes"] != 0
                        or ls["minimum_diagonal"] < 1 / 64 or ls["trainer"] != trainer):
                    raise RuntimeError("full-domain fitting contract failed")
        candidate, candidate_path = _accept(models, source, scenario, m, "full", output, cpu, cuda)
        compared = _comparison(baselines["r22"], candidate)
        report["cases"].append({"scenario": scenario, "m": m, "models": list(map(str, models)), "routes": routes,
            "baseline_models": list(map(str, reference_models)), "supported_models": previous["models"],
            "result": str(candidate_path), "result_sha256": metrics.file_sha256(candidate_path),
            "baseline_result": str(paths["r22"]), "baseline_sha256": expected["r22"],
            "supported_result": str(paths["r24"]), "supported_result_sha256": expected["r24"],
            "candidate_fit": candidate_fit, "comparison": compared,
            "versus_supported": _comparison(baselines["r24"], candidate)})
        _write_report(target, report)
        mean, maximum = compared["cube"]["mean"], compared["cube"]["max"]
        print(f"[full] {scenario}/m{m}: R22 mean {mean['baseline']:.6f}->{mean['candidate']:.6f}; "
              f"max {maximum['baseline']:.6f}->{maximum['candidate']:.6f}", flush=True)
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError(f"study source changed: {name}")
    for name, digest in report["executable_sha256"].items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("runtime executable changed")
    if fullfit.trainer_fingerprint() != trainer or metrics.file_sha256(old_path) != report["frozen_baseline"]["sha256"]:
        raise RuntimeError("native trainer or frozen corpus changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                  structural_parity_and_full_domain_pass=True)
    _write_report(target, report)


if __name__ == "__main__":
    main()
