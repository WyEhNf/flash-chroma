"""One serial audit of native image validation and clipping-capacity alternatives.

Keep the R19 evidence immutable. Reuse its six source-bound fitted models, then
fit only two predeclared clip-7 sizes (25 and 33) using the same DP/jitter method.
These are follow-up measurements on known data, not a new blind experiment.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cli, metrics, qualification, validation
from lutlab.entry import _write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r20-validation")
    args = parser.parse_args()
    cpu, cuda, output = args.cpu.resolve(), args.cuda.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      JSHC_BIN=str(cpu), JSHC_CUDA_BIN=str(cuda))
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    started = time.perf_counter()
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "serial validation correctness audit and predeclared capacity follow-up",
              "official_score_available": False,
              "accuracy_gate": "illustrative mean < 2 on every image and whole cube; not official",
              "blind_evaluation": False,
              "predeclared_additional_candidates": [{"scenario": "clip-7", "m": m,
                  "method": "ls_tetra_jitter", "grid": "dp"} for m in (25, 33)],
              "source_sha256": {str(path.relative_to(ROOT)): metrics.file_sha256(path) for path in [
                  ROOT / "python/lutlab/validation.py", ROOT / "python/lutlab/qualification.py",
                  ROOT / "python/lutlab/runtime.py", Path(__file__).resolve()]},
              "executable_sha256": {str(path): metrics.file_sha256(path) for path in (cpu, cuda)},
              "cases": []}
    target = output / "audit.json"
    command = [sys.executable, "-m", "pytest", "-q", "tests"]
    check = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (output / "pytest.log").write_text(check.stdout + check.stderr, encoding="utf-8")
    report["python_acceptance"] = {"command": command, "returncode": check.returncode,
        "log_sha256": metrics.file_sha256(output / "pytest.log")}
    _write_report(target, report)
    print(check.stdout, flush=True)
    check.check_returncode()

    frozen = json.loads((ROOT / "artifacts/r19-delivery/acceptance-suite.json").read_text(encoding="utf-8"))
    cases = frozen["cases"]
    if {(row["scenario"], row["m"]) for row in cases} != {
            (scenario, m) for scenario in ("isp-0", "clip-7", "warp-7") for m in (17, 18)} or len(cases) != 6:
        raise RuntimeError("R19 acceptance suite does not contain the six expected frozen cases")
    work = [(row, False) for row in cases]
    for m in (25, 33):
        work.append(({"scenario": "clip-7", "m": m}, True))
    for row, additional in work:
        scenario, m = row["scenario"], row["m"]
        source = ROOT / "artifacts/r17-algorithm" / scenario
        if additional:
            parameters = SimpleNamespace(scenario=scenario, m=m, method="ls_tetra_jitter", mode="seq",
                grid="dp", adaptive=False, inputs=[source / f"lut{k}.lut256" for k in range(1, 5)],
                model_dir=output / f"models/{scenario}/dp_jitter_m{m}", allow_composite=False, allow_residual=False)
            entry = cli.model_entry(parameters)
            row["models"] = list(map(str, entry.paths))
        options = SimpleNamespace(models=list(map(Path, row["models"])),
            full_luts=[source / f"lut{k}.lut256" for k in range(1, 5)],
            reference=source / "composite.lut256", images=ROOT / "artifacts/r17-acceptance/bench.txt",
            backend="both", cpu_executable=cpu, cuda_executable=cuda, kernel="tetra_avx2",
            threads=4, device=0, threshold=2., threshold_origin="illustrative", metric="mean",
            allow_declared_models=False, output=output / f"acceptance-{scenario}-m{m}.json")
        result = qualification.accept(options)
        if not (result["structural_contract_pass"] and result["backend_cube_sha256_equal"]
                and result["backend_images_sha256_equal"]):
            raise RuntimeError(f"native execution/provenance audit failed for {scenario}/m{m}")
        if not additional:
            old_path = Path(row["acceptance"])
            if metrics.file_sha256(old_path) != row["acceptance_sha256"]:
                raise RuntimeError("frozen R19 result was modified")
            old = json.loads(old_path.read_text(encoding="utf-8"))
            for backend in ("cpu", "cuda"):
                for field in ("cube", "per_image", "mapped_cube_sha256", "pass"):
                    if result["backends"][backend][field] != old["backends"][backend][field]:
                        raise RuntimeError(f"R19 quality changed: {scenario}/m{m}/{backend}/{field}")
        quality = result["backends"]["cpu"]
        report["cases"].append({"scenario": scenario, "m": m, "additional_candidate": additional,
            "models": row["models"], "result": str(options.output),
            "result_sha256": metrics.file_sha256(options.output),
            "native_images_and_cube_equal": True, "frozen_r19_quality_unchanged": True if not additional else None,
            "cube_mean": quality["cube"]["mean"], "cube_p99": quality["cube"]["p99"],
            "cube_max": quality["cube"]["max"], "worst_image_mean": quality["worst_image_metric"],
            "local_mean_gate_pass": result["pass"]})
        _write_report(target, report)
        print(f"[audit] {scenario}/m{m}: native images and cube agree, mean gate={result['pass']}", flush=True)

    # Exercise the new CUDA apply fallback for a one-frame validation set.
    first = report["cases"][0]
    full_listing = ROOT / "artifacts/r17-acceptance/bench.txt"
    first_line = next(line for line in full_listing.read_text(encoding="utf-8").splitlines() if line.strip())
    single = output / "single.txt"
    single.write_text(first_line + "\n", encoding="utf-8")
    single_result = validation.validate(list(map(Path, first["models"])),
        ROOT / "artifacts/r17-algorithm/isp-0/composite.lut256", single,
        kernel="auto", threads=0, threshold=2., metric="mean", full_cube=False,
        competition=True, backend="cuda", executable=cuda)
    if not single_result["image_execution_verified"] or single_result["image_execution"]["mode"] != "per_image_apply":
        raise RuntimeError("single-frame CUDA apply fallback was not verified")
    _write_report(output / "single-cuda.json", single_result)
    report["single_cuda_fallback_verified"] = True
    for path, digest in report["executable_sha256"].items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError("runtime binary changed during audit")
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["elapsed_seconds"] = time.perf_counter() - started
    report["correctness_audit_pass"] = True
    _write_report(target, report)


if __name__ == "__main__":
    main()
