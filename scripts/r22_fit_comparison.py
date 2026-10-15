"""Seven paired full four-LUT fits: frozen R21 jitter LS versus current CSR.

Only in-memory four-stage DP+jitter fitting is timed. Input loading, imports,
model serialization and hash checks are excluded. Each sample is a fresh process
and includes first-use design-matrix construction, not model-cache lookup.
"""
from __future__ import annotations

import argparse
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
    from lutlab import cascade, io
    tables = [io.load_full(args.source_dir / f"lut{k}.lut256") for k in range(1, 5)]
    started = time.perf_counter()
    chain, info = cascade.fit_cascade_sequential(tables, 33, "ls_tetra_jitter", grid_mode="dp")
    seconds = time.perf_counter() - started
    hashes = []
    with tempfile.TemporaryDirectory(prefix="r22-fit-output-") as directory:
        for stage, (model, reference) in enumerate(zip(chain, args.reference_models), 1):
            path = Path(directory) / f"stage{stage}.slut"
            io.save_sparse(path, model)
            payload = path.read_bytes()
            if payload != reference.read_bytes():
                raise RuntimeError("full fit changed frozen model bytes")
            hashes.append(hashlib.sha256(payload).hexdigest())
    print(json.dumps({"fit_seconds": seconds, "fit_info": info, "model_sha256": hashes,
                      "frozen_model_bytes_equal": True}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--reference-models", nargs=4, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r22-structured-v3/fit-comparison.json")
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
    baseline = output.parent / "frozen-r21"
    snapshot = ROOT / "artifacts/r21-boundary/source-snapshot.zip"
    old_study = json.loads((ROOT / "artifacts/r21-boundary/study.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(snapshot) as archive:
        for name in archive.namelist():
            if not name.startswith("python/lutlab/") or not name.endswith(".py"):
                continue
            destination = (baseline / name).resolve()
            if baseline.resolve() not in destination.parents:
                raise RuntimeError("snapshot path escapes the frozen package")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(name))
    for name, digest in old_study["source_sha256"].items():
        if name.startswith("python/lutlab/") and (baseline / name).is_file():
            if metrics.file_sha256(baseline / name) != digest:
                raise RuntimeError("frozen package does not match R21 source evidence")
    row = next(case for case in old_study["cases"] if case["scenario"] == "clip-7" and case["m"] == 33)
    models = list(map(Path, row["baseline_models"]))
    source = ROOT / "artifacts/r17-algorithm/clip-7"
    files = [snapshot, *(source / f"lut{k}.lut256" for k in range(1, 5)), *models,
             ROOT / "python/lutlab/fit.py", Path(__file__).resolve()]
    hashes = {str(path): metrics.file_sha256(path) for path in files}
    report = {"scope": __doc__, "input_sha256": hashes, "pairs": 7, "runs": [],
              "baseline_package_source": "R21 source snapshot, verified against frozen source hashes"}
    for pair in range(7):
        order = ["r21_coo", "current_csr"] if pair % 2 == 0 else ["current_csr", "r21_coo"]
        for mode in order:
            package = baseline if mode == "r21_coo" else ROOT
            command = [sys.executable, str(Path(__file__).resolve()), "--worker", "--package-root", str(package),
                       "--source-dir", str(source), "--reference-models", *map(str, models)]
            process = runtime._execute(command)
            if process["returncode"]:
                raise RuntimeError(process["stderr"])
            report["runs"].append({"pair": pair, "mode": mode, "order": order, "command": command,
                                  **process, "result": json.loads(process["stdout"])})
            _write_report(output, report)
        print(f"[fit-paired] pair {pair + 1}/7 complete", flush=True)
    modes = ("r21_coo", "current_csr")
    ratios = []
    for pair in range(7):
        times = {row["mode"]: row["result"]["fit_seconds"] for row in report["runs"] if row["pair"] == pair}
        ratios.append(times[modes[0]] / times[modes[1]])
    report["median_fit_seconds"] = {mode: statistics.median(row["result"]["fit_seconds"]
        for row in report["runs"] if row["mode"] == mode) for mode in modes}
    report["median_process_peak_working_set_bytes"] = {}
    for mode in modes:
        observations = [row["observed_peak_working_set_bytes"] for row in report["runs"]
                        if row["mode"] == mode and row["observed_peak_working_set_bytes"] is not None]
        report["median_process_peak_working_set_bytes"][mode] = statistics.median(observations) if observations else None
    report["comparison"] = _paired_statistics(ratios, 2026101522)
    for path, digest in hashes.items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError("fit comparison input or source changed")
    report["inputs_unchanged"] = True
    report["frozen_model_bytes_equal_all_runs"] = True
    _write_report(output, report)
    print(json.dumps({key: report[key] for key in ("median_fit_seconds",
        "median_process_peak_working_set_bytes", "comparison")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
