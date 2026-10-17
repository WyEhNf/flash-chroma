"""Nine AB/BA pairs for each predeclared structured-runtime comparison.

Three frozen real models represent mostly generic, mixed curve/vertex/generic,
and vertex/curve paths. All comparisons use one native binary, the same 100
images, 16 CPU threads and batch mode. Host copy plus four-stage mapping is
timed; first cold execution is retained separately. No pair is discarded. Do
not run while any known fitting controller/phase is active.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(1, str(ROOT))
sys.path.insert(2, str(ROOT / "artifacts/r18-tools/python"))
import numpy as np
from PIL import Image
from lutlab import casebook, corpus, performance, reportio, runtime
from scripts.r37_report_io import process_alive


def quiet(controller_path):
    controller = reportio.read_json(controller_path)
    if not controller.get("finished_utc") or any(row["status"] != "terminal" for row in controller["children"].values()):
        raise RuntimeError("the previous fitting controller is not terminal")
    if process_alive(controller["controller_pid"]):
        raise RuntimeError("the previous controller process remains live")
    for row in controller["children"].values():
        if process_alive(row["pid"]):
            raise RuntimeError("a known fitting process remains live")
    lease = ROOT / "artifacts/r29-matrix/phase-controller.lock"
    if lease.exists():
        raise RuntimeError("a canonical controller lease is still held")
    for lease in (ROOT / "artifacts/r36-extension").glob("*.lock"):
        if process_alive(reportio.read_json(lease)["pid"]):
            raise RuntimeError("an extension fitting phase remains live")
    return {"checked_controller_sha256": corpus.digest_file(controller_path),
            "known_controller_and_children_terminal": True, "canonical_lease_absent": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-controller", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "artifacts/r39-structured-performance"
    output.mkdir(exist_ok=True)
    target = output / "comparison.json"
    if target.exists():
        raise RuntimeError("preserve this epoch; do not rerun to select favorable samples")
    before_quiet = quiet(args.prior_controller.resolve())
    r35path = ROOT / "artifacts/r35-structured-runtime/stage.json"
    r35 = reportio.read_json(r35path)
    if not r35["pass"]:
        raise RuntimeError("requires a completed structured correctness stage")
    binary = ROOT / "build-r35-structured/jshc.exe"
    if corpus.digest_file(binary) != r35["builds"]["simd"]["binary_sha256"]:
        raise RuntimeError("validated native binary changed")
    for name, digest in r35["source_sha256"].items():
        if name.endswith((".cpp", ".hpp", ".c", ".h")) or name == "CMakeLists.txt":
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("compiled native source differs from the validated stage")
    selected = [next(row for row in r35["cases"] if row["name"] == name) for name in
                ("historical-clip-m17", "new-stress-m33", "new-bins17-m17")]
    listing = ROOT / "data/corpus-v1/benchmark100.txt"
    images = [Path(line) for line in listing.read_text(encoding="utf-8").splitlines() if line]
    if len(images) != 100:
        raise RuntimeError("requires the fixed 100-image cohort")
    tracked = [r35path, binary, listing, args.prior_controller.resolve(), *images]
    for row in selected:
        row["models"] = [casebook._path(path) for path in row["models"]]
        if [corpus.digest_file(path) for path in row["models"]] != row["model_sha256"]:
            raise RuntimeError("frozen model bytes changed")
        tracked.extend(row["models"])
    hashes = {str(path): corpus.digest_file(path) for path in tracked}
    if len({hashes[str(path)] for path in images}) != 100:
        raise RuntimeError("image contents are not unique")
    for path in images:
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise RuntimeError("wrong standard RGB8 frame")
    sources = ["scripts/r39_structured_performance.py", "scripts/r37_report_io.py", "python/lutlab/runtime.py",
               "python/lutlab/performance.py", "python/lutlab/reportio.py"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in sources}
    environment = {"OMP_DYNAMIC": "FALSE", "OMP_PROC_BIND": "FALSE", "OMP_THREAD_LIMIT": "32", "OMP_SCHEDULE": "STATIC",
                   "JSHC_BLOCK_PIXELS": "4096", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
    for name in ("OMP_PLACES", "GOMP_CPU_AFFINITY"):
        os.environ.pop(name, None)
    os.environ.update(environment)
    configs = {"gather16": "tetra_avx2_scalar_gather", "c99_16": "tetra_c99", "structured16": "tetra_structured_avx2"}
    comparisons = [(row["name"], a, b) for row in selected for a, b in
                   (("gather16", "c99_16"), ("gather16", "structured16"), ("c99_16", "structured16"))]
    rows_by_name = {row["name"]: row for row in selected}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": source_hashes, "input_and_binary_sha256": hashes, "quiet_before": before_quiet,
              "pairs": 9, "seed": 2026101639, "predeclared_comparisons": comparisons,
              "multiplicity_policy": "Holm correction across all nine two-sided sign tests with exact ties omitted, alpha=0.05; bootstrap CIs remain marginal 95%",
              "environment": environment, "configurations": configs, "cpu_capabilities": runtime.capabilities("cpu", binary),
              "timing_scope": "100 resident ordinary host images: copy plus four-stage mapping",
              "excluded": ["fitting", "image decode", "allocation", "model load", "encoding", "checksum"],
              "cold_scope": "first 100-image application, including lazy model/cache preparation, recorded separately; no input copy needed",
              "affinity": "OS scheduler, no pinning", "preflight": [], "runs": [], "comparisons": [],
              "official": False, "new_physical_mobile_measurement": False}
    reportio.write_report(target, report)
    with tempfile.TemporaryDirectory(prefix="r39-preflight-") as temporary:
        raw = Path(temporary) / "images.rgb"
        for row in selected:
            expected = None
            for name, kernel in configs.items():
                value = runtime.verify(row["models"], listing, executable=binary, kernel=kernel, threads=16,
                                       batch=True, competition=True, output=raw)
                digest = corpus.digest_file(raw)
                if raw.stat().st_size != 100 * 1024 * 768 * 3 or (expected is not None and digest != expected):
                    raise RuntimeError("benchmark configuration image bytes differ")
                expected = digest
                report["preflight"].append({"case": row["name"], "configuration": name, "output_sha256": digest,
                                            "native_runtime": value, "full_cube_proof": row["cube_sha256"]})
            reportio.write_report(target, report)
            print("[preflight] " + row["name"] + ": all 100 outputs agree for all three kernels", flush=True)
    rng = np.random.default_rng(report["seed"])
    for pair in range(report["pairs"]):
        for comparison_index in rng.permutation(len(comparisons)):
            case_name, a, b = comparisons[int(comparison_index)]
            order = [a, b] if (pair + int(comparison_index)) % 2 == 0 else [b, a]
            for name in order:
                value = runtime.bench(rows_by_name[case_name]["models"], listing, executable=binary, kernel=configs[name],
                                      threads=16, reps=1, batch=True, competition=True)
                elapsed = value["set_ms_p50_rep"]
                if not math.isfinite(elapsed) or elapsed <= 0:
                    raise RuntimeError("invalid set timing")
                report["runs"].append({"case": case_name, "comparison": [a, b], "pair": pair, "order": order,
                                       "configuration": name, "host_to_host_ms": elapsed, "runtime": value})
                reportio.write_report(target, report)
        print(f"[paired] round {pair+1}/9: all nine predeclared comparisons completed", flush=True)
    for index, (case_name, a, b) in enumerate(comparisons):
        values = [row for row in report["runs"] if row["case"] == case_name and row["comparison"] == [a, b]]
        ratios = []
        for pair in range(report["pairs"]):
            times = {row["configuration"]: row["host_to_host_ms"] for row in values if row["pair"] == pair}
            ratios.append(times[a] / times[b])
        report["comparisons"].append({"case": case_name, "reference": a, "candidate": b,
            "reference_median_ms": statistics.median(row["host_to_host_ms"] for row in values if row["configuration"] == a),
            "candidate_median_ms": statistics.median(row["host_to_host_ms"] for row in values if row["configuration"] == b),
            "reference_model_runtime_bytes": next(row["runtime"]["model_runtime_bytes"] for row in values if row["configuration"] == a),
            "candidate_model_runtime_bytes": next(row["runtime"]["model_runtime_bytes"] for row in values if row["configuration"] == b),
            **performance._paired_statistics(ratios, report["seed"] + index)})
    for comparison in report["comparisons"]:
        signs = [ratio > 1 for ratio in comparison["paired_ratios_reference_over_candidate"] if ratio != 1]
        n = len(signs)
        extreme = max(sum(signs), n - sum(signs))
        comparison["sign_test_non_tied_pairs"] = n
        comparison["two_sided_sign_test_p"] = min(1., 2 * sum(math.comb(n, k) for k in range(extreme, n + 1)) / 2**n) if n else 1.
    ordered = sorted(range(len(report["comparisons"])), key=lambda index: report["comparisons"][index]["two_sided_sign_test_p"])
    adjusted = 0.
    for rank, index in enumerate(ordered):
        comparison = report["comparisons"][index]
        adjusted = max(adjusted, min(1., (len(ordered) - rank) * comparison["two_sided_sign_test_p"]))
        comparison["two_sided_sign_test_holm_p"] = adjusted
        comparison["candidate_faster_holm_alpha_05"] = adjusted <= .05 and comparison["paired_speedup_median"] > 1
        comparison["reference_faster_holm_alpha_05"] = adjusted <= .05 and comparison["paired_speedup_median"] < 1
    report["cold_and_process_memory"] = []
    for row in selected:
        for name in configs:
            values = [value["runtime"] for value in report["runs"] if value["case"] == row["name"] and value["configuration"] == name]
            peaks = [value["observed_peak_working_set_bytes"] for value in values if value["observed_peak_working_set_bytes"] is not None]
            report["cold_and_process_memory"].append({"case": row["name"], "configuration": name,
                "cold_batch_ms_median": statistics.median(value["cold_batch_ms"] for value in values),
                "model_runtime_bytes": values[0]["model_runtime_bytes"],
                "process_peak_working_set_bytes_median": statistics.median(peaks) if peaks else None,
                "process_memory_scope": "whole native process; includes decoded image and work buffers, separate from model estimate"})
    for path, digest in hashes.items():
        if corpus.digest_file(Path(path)) != digest:
            raise RuntimeError("frozen input/binary changed")
    for name, digest in source_hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("comparison source changed")
    report["quiet_after"] = quiet(args.prior_controller.resolve())
    report.update(pass_=True, inputs_unchanged=True, finished_utc=datetime.now(timezone.utc).isoformat())
    report["pass"] = report.pop("pass_")
    reportio.write_report(target, report)
    print(json.dumps({"pass": True, "comparisons": report["comparisons"]}), flush=True)


if __name__ == "__main__":
    main()
