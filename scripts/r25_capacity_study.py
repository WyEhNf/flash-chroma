"""A separate legal-capacity check, not a fixed-size algorithm comparison.

The two R24 clipping failures at m18 are evaluated at m33 with the already
frozen R25 full-domain algorithm. The m18 and m33 results use identical source
LUTs and images. No new parameters, grids or source data are tuned here.
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
from lutlab import cache, fullfit, metrics
from lutlab.entry import _write_report
from r21_boundary_study import _accept, _comparison, _fit
from r24_supported_study import _fit_record

CASES = [("clip-23", 18, 33), ("clip-31", 18, 33)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r25-full/capacity")
    args = parser.parse_args()
    cpu, cuda, output = args.cpu.resolve(), args.cuda.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
        OMP_DYNAMIC="FALSE", OMP_THREAD_LIMIT="32", JSHC_BIN=str(cpu), JSHC_CUDA_BIN=str(cuda),
        JSHC_FULL_FIT_LIB=str(fullfit.resolve_library()))
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    started = time.perf_counter()
    prior_path = ROOT / "artifacts/r25-full/study.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    if not prior.get("structural_parity_and_full_domain_pass"):
        raise RuntimeError("complete R25 fixed-capacity comparison first")
    if fullfit.trainer_fingerprint() != prior["trainer"]:
        raise RuntimeError("capacity study must use the identical frozen trainer")
    sources = {name: metrics.file_sha256(ROOT / name) for name in prior["source_sha256"]}
    if sources != prior["source_sha256"]:
        raise RuntimeError("fixed-capacity fitting source changed")
    sources["scripts/r25_capacity_study.py"] = metrics.file_sha256(Path(__file__))
    known = {(c["scenario"], c["m"]): c for c in prior["cases"]}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "source_sha256": sources, "predeclared_cases": CASES, "trainer": prior["trainer"],
        "fixed_capacity_reference": {"path": str(prior_path), "sha256": metrics.file_sha256(prior_path)},
        "executable_sha256": {str(p): metrics.file_sha256(p) for p in (cpu, cuda)},
        "official_score_available": False, "fit_executions": [], "cases": []}
    target = output / "study.json"
    _write_report(target, report)
    for scenario, old_m, new_m in CASES:
        old = known[(scenario, old_m)]
        path = Path(old["result"])
        if metrics.file_sha256(path) != old["result_sha256"]:
            raise RuntimeError("frozen m18 accuracy result changed")
        baseline = json.loads(path.read_text(encoding="utf-8"))
        source = Path(baseline["sources"][0]["path"]).parent
        models = _fit(source, scenario, new_m, "ls_tetra_full", output, report["fit_executions"])
        candidate, candidate_path = _accept(models, source, scenario, new_m, "full", output, cpu, cuda)
        comparison = _comparison(baseline, candidate)
        report["cases"].append({"scenario": scenario, "baseline_m": old_m, "candidate_m": new_m,
            "models": list(map(str, models)), "baseline_models": old["models"],
            "result": str(candidate_path), "result_sha256": metrics.file_sha256(candidate_path),
            "baseline_result": str(path), "baseline_sha256": old["result_sha256"],
            "candidate_fit": _fit_record(models), "comparison": comparison,
            "node_payload_bytes": {"baseline": 4 * old_m ** 3 * 3, "candidate": 4 * new_m ** 3 * 3},
            "serialized_model_bytes": {"baseline": sum(Path(p).stat().st_size for p in old["models"]),
                                       "candidate": sum(p.stat().st_size for p in models)}})
        _write_report(target, report)
        print(f"[capacity] {scenario}/m{old_m}->m{new_m}: gate "
              f"{baseline['pass']}->{candidate['pass']}; worst_image_mean={candidate['backends']['cpu']['worst_image_metric']:.6f}", flush=True)
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError("capacity source changed")
    for name, digest in report["executable_sha256"].items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("capacity runtime changed")
    if fullfit.trainer_fingerprint() != prior["trainer"] or metrics.file_sha256(prior_path) != report["fixed_capacity_reference"]["sha256"]:
        raise RuntimeError("capacity trainer or reference changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                  structural_parity_and_capacity_pass=True)
    _write_report(target, report)


if __name__ == "__main__":
    main()
