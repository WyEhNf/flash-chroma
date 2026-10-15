"""Seven serial AB/BA complete fits: R22 structured versus R24 supported.

Fixed stress-13/m33 exercises the stage with 63 formerly unsupported vertices.
The timer includes DP grids, full separability checks, curve solving, first-use
sampling/assembly, CG and integer refinement for all four LUTs. Imports, LUT
loading, serialization and verified model-cache lookup are excluded. Each run
uses a fresh process and must reproduce its own frozen model bytes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def worker(args):
    sys.path.insert(0, str(args.package_root / "python"))
    from lutlab import cascade, fit, io
    if Path(fit.__file__).resolve().parent != (args.package_root / "python/lutlab").resolve():
        raise RuntimeError("worker imported the wrong fitting package")
    tables = [io.load_full(args.source_dir / f"lut{k}.lut256") for k in range(1, 5)]
    started = time.perf_counter()
    chain, info = cascade.fit_cascade_sequential(tables, 33, args.method, grid_mode="dp")
    seconds = time.perf_counter() - started
    hashes = []
    with tempfile.TemporaryDirectory(prefix="r24-fit-bytes-") as directory:
        for stage, (model, reference) in enumerate(zip(chain, args.reference_models), 1):
            path = Path(directory) / f"stage{stage}.slut"
            io.save_sparse(path, model)
            payload = path.read_bytes()
            if payload != reference.read_bytes():
                raise RuntimeError("fit changed its frozen model bytes")
            hashes.append(hashlib.sha256(payload).hexdigest())
    print(json.dumps({"fit_seconds": seconds, "fit_info": info, "model_sha256": hashes,
                      "frozen_model_bytes_equal": True}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--method")
    parser.add_argument("--reference-models", nargs=4, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r24-supported/fit-comparison.json")
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    sys.path.insert(0, str(ROOT / "python"))
    from lutlab import metrics, runtime
    from lutlab.entry import _write_report
    from lutlab.performance import _paired_statistics
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    study_path = ROOT / "artifacts/r24-supported/study.json"
    study = json.loads(study_path.read_text(encoding="utf-8"))
    if not study.get("structural_parity_and_support_pass"):
        raise RuntimeError("run quality/support acceptance before this cost comparison")
    case = next(c for c in study["cases"] if (c["scenario"], c["m"]) == ("stress-13", 33))
    baseline = output.parent / "frozen-r22"
    snapshot = ROOT / "artifacts/r22-structured-v3/source-snapshot.zip"
    old_study = json.loads((ROOT / "artifacts/r22-structured-v3/study.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(snapshot) as archive:
        for name in archive.namelist():
            if not name.startswith("python/lutlab/") or not name.endswith(".py"):
                continue
            destination = (baseline / name).resolve()
            if baseline.resolve() not in destination.parents:
                raise RuntimeError("snapshot extraction escapes the frozen package")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(name))
    for name, digest in old_study["source_sha256"].items():
        if name.startswith("python/lutlab/") and (baseline / name).is_file():
            if metrics.file_sha256(baseline / name) != digest:
                raise RuntimeError("baseline does not match frozen R22 sources")
    models = {"r22_structured": list(map(Path, case["baseline_models"])),
              "r24_supported": list(map(Path, case["models"]))}
    packages = {"r22_structured": baseline, "r24_supported": ROOT}
    methods = {"r22_structured": "ls_tetra_structured", "r24_supported": "ls_tetra_supported"}
    result = json.loads(Path(case["result"]).read_text(encoding="utf-8"))
    source = Path(result["sources"][0]["path"]).parent
    files = [snapshot, study_path, Path(case["result"]), *(source / f"lut{k}.lut256" for k in range(1, 5)),
             *(p for paths in models.values() for p in paths), Path(__file__).resolve(),
             *(ROOT / "python/lutlab").glob("*.py"), *(baseline / "python/lutlab").glob("*.py")]
    hashes = {str(path): metrics.file_sha256(path) for path in files}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "input_and_source_sha256": hashes, "pairs": 7, "runs": [], "scenario": "stress-13", "m": 33,
        "quality_gate": "R24 full-cube and 100-image evidence; speed comparison cannot replace failed accuracy gates"}
    for pair in range(7):
        order = ["r22_structured", "r24_supported"] if pair % 2 == 0 else ["r24_supported", "r22_structured"]
        for mode in order:
            command = [sys.executable, str(Path(__file__).resolve()), "--worker", "--package-root", str(packages[mode]),
                       "--source-dir", str(source), "--method", methods[mode], "--reference-models", *map(str, models[mode])]
            process = runtime._execute(command)
            if process["returncode"]:
                raise RuntimeError(process["stderr"])
            report["runs"].append({"pair": pair, "mode": mode, "order": order, "command": command,
                                  **process, "result": json.loads(process["stdout"])})
            _write_report(output, report)
        print(f"[fit-paired] pair {pair + 1}/7 complete", flush=True)
    report["median_fit_seconds"] = {mode: statistics.median(row["result"]["fit_seconds"] for row in report["runs"]
        if row["mode"] == mode) for mode in methods}
    report["median_process_peak_working_set_bytes"] = {}
    for mode in methods:
        observations = [row["observed_peak_working_set_bytes"] for row in report["runs"]
                        if row["mode"] == mode and row["observed_peak_working_set_bytes"] is not None]
        report["median_process_peak_working_set_bytes"][mode] = statistics.median(observations) if observations else None
    ratios = []
    for pair in range(7):
        times = {row["mode"]: row["result"]["fit_seconds"] for row in report["runs"] if row["pair"] == pair}
        ratios.append(times["r22_structured"] / times["r24_supported"])
    report["comparison"] = _paired_statistics(ratios, 2026101524)
    for path, digest in hashes.items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError(f"comparison source or input changed: {path}")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True,
                  frozen_model_bytes_equal_all_runs=True)
    _write_report(output, report)
    print(json.dumps({key: report[key] for key in ("median_fit_seconds", "median_process_peak_working_set_bytes", "comparison")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
