"""Seven serial AB/BA pairs for exact assembly and complete four-LUT fitting.

Assembly: identical full-domain H,b from Python COO, native 1 thread, native
4 threads; coordinate generation and CSR conversion included, loading/hash
excluded. Complete fit: frozen R22 sampled structured versus R25 full-domain,
including first native-library use, DP grids, fitting and integer refinement.
Every process is fresh. Assembly matrices must match exactly; fitted models
must reproduce each method's own frozen bytes. All use clip-7/m33.
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
    import numpy as np
    import scipy.sparse as sp
    from lutlab import cascade, fit, io
    if Path(fit.__file__).resolve().parent != (args.package_root / "python/lutlab").resolve():
        raise RuntimeError("worker imported the wrong package")
    if args.worker.startswith("fit_"):
        tables = [io.load_full(args.source_dir / f"lut{k}.lut256") for k in range(1, 5)]
        method = "ls_tetra_structured" if args.worker == "fit_r22" else "ls_tetra_full"
        started = time.perf_counter()
        chain, info = cascade.fit_cascade_sequential(tables, 33, method, grid_mode="dp")
        seconds = time.perf_counter() - started
        hashes = []
        with tempfile.TemporaryDirectory(prefix="r25-model-bytes-") as directory:
            for stage, (model, reference) in enumerate(zip(chain, args.reference_models), 1):
                path = Path(directory) / f"stage{stage}.slut"
                io.save_sparse(path, model)
                payload = path.read_bytes()
                if payload != reference.read_bytes():
                    raise RuntimeError("fitting changed frozen model bytes")
                hashes.append(hashlib.sha256(payload).hexdigest())
        result = {"seconds": seconds, "fit_info": info, "model_sha256": hashes, "frozen_models_byte_equal": True}
    else:
        table = io.load_full(args.source_dir / "lut1.lut256")
        grid = io.load_sparse(args.grid_model).grid
        started = time.perf_counter()
        if args.worker == "assembly_coo":
            M = 33 ** 3
            H, b = sp.csr_matrix((M, M)), np.zeros((M, 3))
            points = np.empty((4 * 256 ** 2, 3), np.uint8)
            green, blue = np.indices((256, 256), dtype=np.uint8)
            points[:, 1], points[:, 2] = np.tile(green.ravel(), 4), np.tile(blue.ravel(), 4)
            for red in range(0, 256, 4):
                points[:, 0] = np.repeat(np.arange(red, red + 4, dtype=np.uint8), 256 ** 2)
                part, rhs = fit.normal_equations(points, table[red:red + 4].reshape(-1, 3),
                                                 np.full(len(points), 1 / 64), grid)
                H += part
                b += rhs
            detail = {"backend": "legacy_coo_full_domain_reference", "sample_count": 256 ** 3}
        else:
            from lutlab import fullfit
            threads = 1 if args.worker == "assembly_native1" else 4
            H, b, detail = fullfit.normal_equations(table, grid, threads)
        H.sum_duplicates()
        H.eliminate_zeros()
        H.sort_indices()
        seconds = time.perf_counter() - started
        digest = hashlib.sha256()
        for array, dtype in ((H.indptr, "<i8"), (H.indices, "<i8"), (H.data, "<f8"), (b, "<f8")):
            digest.update(memoryview(np.ascontiguousarray(array, dtype=dtype)))
        result = {"seconds": seconds, "canonical_system_sha256": digest.hexdigest(), "assembly": detail}
    print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("assembly_coo", "assembly_native1", "assembly_native4", "fit_r22", "fit_full"))
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--grid-model", type=Path)
    parser.add_argument("--reference-models", nargs=4, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r25-full/performance.json")
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    sys.path.insert(0, str(ROOT / "python"))
    from lutlab import fullfit, metrics, runtime
    from lutlab.entry import _write_report
    from lutlab.performance import _paired_statistics
    environment = {"OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                   "OMP_DYNAMIC": "FALSE", "OMP_THREAD_LIMIT": "32", "OMP_PROC_BIND": "FALSE"}
    for name in ("OMP_PLACES", "GOMP_CPU_AFFINITY"):
        os.environ.pop(name, None)
    os.environ.update(environment)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    study_path = ROOT / "artifacts/r25-full/study.json"
    study = json.loads(study_path.read_text(encoding="utf-8"))
    if not study.get("structural_parity_and_full_domain_pass"):
        raise RuntimeError("complete full-domain quality/oracle acceptance first")
    case = next(c for c in study["cases"] if (c["scenario"], c["m"]) == ("clip-7", 33))
    accuracy = json.loads(Path(case["result"]).read_text(encoding="utf-8"))
    source = Path(accuracy["sources"][0]["path"]).parent
    models = {"fit_r22": list(map(Path, case["baseline_models"])), "fit_full": list(map(Path, case["models"]))}
    baseline = output.parent / "frozen-r22"
    snapshot = ROOT / "artifacts/r22-structured-v3/source-snapshot.zip"
    old = json.loads((ROOT / "artifacts/r22-structured-v3/study.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(snapshot) as archive:
        for name in archive.namelist():
            if not name.startswith("python/lutlab/") or not name.endswith(".py"):
                continue
            destination = (baseline / name).resolve()
            if baseline.resolve() not in destination.parents:
                raise RuntimeError("frozen extraction escapes the package")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(name))
    for name, digest in old["source_sha256"].items():
        if name.startswith("python/lutlab/") and (baseline / name).is_file():
            if metrics.file_sha256(baseline / name) != digest:
                raise RuntimeError("R22 snapshot source mismatch")
    files = [study_path, Path(case["result"]), snapshot, Path(__file__).resolve(),
        *(source / f"lut{k}.lut256" for k in range(1, 5)), *(p for paths in models.values() for p in paths),
        *(ROOT / "python/lutlab").glob("*.py"), *(baseline / "python/lutlab").glob("*.py"),
        *(ROOT / name for name in fullfit.NATIVE_SOURCES), ROOT / "CMakeLists.txt", fullfit.resolve_library()]
    hashes = {str(path): metrics.file_sha256(path) for path in files}
    trainer = fullfit.trainer_fingerprint()
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "input_and_source_sha256": hashes, "trainer": trainer, "environment": environment,
        "cleared_environment": ["OMP_PLACES", "GOMP_CPU_AFFINITY"], "pairs": 7,
        "quality_gate": "see frozen R25 results; assembly speed is not final mapping throughput or an accuracy pass",
        "runs": []}
    canonical_sha = None
    for phase, modes in (("assembly", ["assembly_coo", "assembly_native1", "assembly_native4"]),
                         ("complete_fit", ["fit_r22", "fit_full"])):
        for pair in range(7):
            order = modes if pair % 2 == 0 else modes[::-1]
            for mode in order:
                package = baseline if mode == "fit_r22" else ROOT
                command = [sys.executable, str(Path(__file__).resolve()), "--worker", mode,
                    "--package-root", str(package), "--source-dir", str(source),
                    "--grid-model", str(models["fit_full"][0])]
                if mode.startswith("fit_"):
                    command += ["--reference-models", *map(str, models[mode])]
                process = runtime._execute(command)
                if process["returncode"]:
                    raise RuntimeError(process["stderr"])
                result = json.loads(process["stdout"])
                if phase == "assembly":
                    canonical_sha = canonical_sha or result["canonical_system_sha256"]
                    if result["canonical_system_sha256"] != canonical_sha:
                        raise RuntimeError("exact assembly matrices or rhs differ")
                report["runs"].append({"phase": phase, "pair": pair, "mode": mode, "order": order,
                                       "command": command, **process, "result": result})
                _write_report(output, report)
            print(f"[{phase}] pair {pair + 1}/7 complete", flush=True)
    all_modes = ("assembly_coo", "assembly_native1", "assembly_native4", "fit_r22", "fit_full")
    report["median_seconds"] = {mode: statistics.median(row["result"]["seconds"] for row in report["runs"]
        if row["mode"] == mode) for mode in all_modes}
    report["median_process_peak_working_set_bytes"] = {}
    for mode in all_modes:
        memory = [row["observed_peak_working_set_bytes"] for row in report["runs"]
                  if row["mode"] == mode and row["observed_peak_working_set_bytes"] is not None]
        report["median_process_peak_working_set_bytes"][mode] = statistics.median(memory) if memory else None
    report["comparisons"] = {}
    for index, (reference, candidate) in enumerate((("assembly_coo", "assembly_native1"),
        ("assembly_native1", "assembly_native4"), ("fit_r22", "fit_full"))):
        ratios = []
        for pair in range(7):
            values = {row["mode"]: row["result"]["seconds"] for row in report["runs"]
                      if row["pair"] == pair and row["mode"] in (reference, candidate)}
            ratios.append(values[reference] / values[candidate])
        report["comparisons"][f"{reference}_over_{candidate}"] = _paired_statistics(ratios, 2026101525 + index)
    for name, digest in hashes.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError(f"performance source/input changed: {name}")
    if fullfit.trainer_fingerprint() != trainer:
        raise RuntimeError("native trainer changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True,
        all_assembly_systems_byte_equivalent=True, all_fitted_models_match_own_frozen_bytes=True)
    _write_report(output, report)
    print(json.dumps({key: report[key] for key in ("median_seconds", "median_process_peak_working_set_bytes", "comparisons")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
