"""Current-model OpenColorIO accuracy and seven AB/BA CPU performance pairs.

Both CPU arms use four workers on the same 100 decoded RGB8 frames. Four
independent UINT8 stage boundaries are retained. OCIO uses float32 interpolation
and a 256-entry geometry shaper, so output precision is measured, not assumed.
The public Python buffer adapter is a declared baseline, not OCIO's fastest
possible C++ or GPU integration. Setup, decode and allocation are outside timing.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")]
import numpy as np
from lutlab import io, metrics, performance, runtime
from lutlab.entry import _write_report
import industry_comparison as industry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    accepted_path, cpu, output = map(Path.resolve, (args.acceptance, args.cpu, args.output))
    output.mkdir(parents=True, exist_ok=True)
    accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
    if not accepted.get("pass") or not accepted.get("structural_contract_pass"):
        raise RuntimeError("requires completed local native acceptance")
    reference = accepted["backends"]["cpu"]
    models = list(map(Path, reference["model_sha256"]))
    images = ROOT / "artifacts/r17-acceptance/bench.txt"
    source = Path(accepted["sources"][0]["path"]).parent
    truth = source / "composite.lut256"
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_DYNAMIC="FALSE",
        OMP_PROC_BIND="FALSE", OMP_THREAD_LIMIT="32", OMP_SCHEDULE="STATIC", JSHC_BLOCK_PIXELS="4096")
    for name in ("OMP_PLACES", "GOMP_CPU_AFFINITY"):
        os.environ.pop(name, None)
    hashes = {**reference["model_sha256"], **accepted["images"], str(truth): accepted["reference_sha256"],
        str(images): accepted["image_list_sha256"], str(cpu): reference["executable_sha256"],
        str(accepted_path): metrics.file_sha256(accepted_path), str(Path(__file__)): metrics.file_sha256(__file__),
        str(ROOT / "scripts/industry_comparison.py"): metrics.file_sha256(ROOT / "scripts/industry_comparison.py")}
    for name, digest in hashes.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError(f"frozen input changed: {name}")
    report = {"scope": __doc__, "started_utc": datetime.now(timezone.utc).isoformat(),
        "input_and_source_sha256": hashes, "acceptance": str(accepted_path), "pairs": 7, "reps_per_process": 3,
        "official_score_available": False, "runs": [], "cpu_kernel": "tetra_avx2", "workers_per_arm": 4}
    target = output / "comparison.json"
    _write_report(target, report)
    command = [sys.executable, str(ROOT / "scripts/industry_comparison.py"), "accuracy", *map(str, models),
        "--truth", str(truth), "--executable", str(cpu), "--output", str(output / "accuracy.json")]
    checked = runtime._execute(command)
    (output / "accuracy.log").write_text(checked["stdout"] + checked["stderr"], encoding="utf-8")
    if checked["returncode"]:
        raise RuntimeError("OpenColorIO full-domain accuracy execution failed")
    accuracy = json.loads((output / "accuracy.json").read_text(encoding="utf-8"))
    for key in ("mean", "rms", "p99", "max"):
        if abs(accuracy["native_vs_truth"][key] - reference["cube"][key]) > 1e-12:
            raise RuntimeError("current native accuracy differs from accepted result")
    report.update(accuracy=accuracy, accuracy_process={k: v for k, v in checked.items() if k not in ("stdout", "stderr")})
    # Execute actual images separately from timing. Their metrics are not
    # inferred merely from synthetic uniform-cube frequency statistics.
    chain = industry.processors(models, "tetrahedral")
    composite = io.load_full(truth, mmap=True)
    image_results, image_sha = [], hashlib.sha256()
    for name in accepted["images"]:
        original = io.load_image(name)
        mapped = original.copy()
        industry.apply(chain, mapped)
        expected = io.apply_full(composite, original)
        delta = mapped.astype(np.int32) - expected.astype(np.int32)
        hist = np.bincount(np.sum(delta * delta, axis=-1).reshape(-1), minlength=3 * 255 ** 2 + 1)
        image_results.append({"image": name, **industry.histogram_stats(hist)})
        image_sha.update(mapped.tobytes())
    report["actual_images"] = {"count": len(image_results), "per_image": image_results,
        "output_sha256": image_sha.hexdigest(), "worst_mean": max(row["mean"] for row in image_results),
        "illustrative_mean_threshold": 2., "failed_images": sum(row["mean"] >= 2 for row in image_results)}
    _write_report(target, report)
    ratios = []
    for pair in range(7):
        order = ["ocio", "cpu"] if pair % 2 == 0 else ["cpu", "ocio"]
        measured = {}
        for arm in order:
            if arm == "cpu":
                value = runtime.bench(models, images, executable=cpu, kernel="tetra_avx2", threads=4,
                    reps=3, competition=True)
                elapsed = value["set_ms_p50_rep"]
            else:
                destination = output / f"ocio-pair-{pair}.json"
                command = [sys.executable, str(ROOT / "scripts/industry_comparison.py"), "bench", *map(str, models),
                    "--images", str(images), "--threads", "4", "--reps", "3", "--output", str(destination)]
                execution = runtime._execute(command)
                (output / f"ocio-pair-{pair}.log").write_text(execution["stdout"] + execution["stderr"], encoding="utf-8")
                if execution["returncode"]:
                    raise RuntimeError("OCIO timing process failed")
                value = {"benchmark": json.loads(destination.read_text(encoding="utf-8")),
                    "process": {k: v for k, v in execution.items() if k not in ("stdout", "stderr")}}
                elapsed = value["benchmark"]["summary"][0]["median_set_ms"]
            measured[arm] = elapsed
            report["runs"].append({"pair": pair, "order": order, "arm": arm, "host_to_host_ms": elapsed, "runtime": value})
            _write_report(target, report)
        ratios.append(measured["ocio"] / measured["cpu"])
        print(f"[industry] {pair + 1}/7 OCIO4={measured['ocio']:.3f} CPU4={measured['cpu']:.3f} ms/100", flush=True)
    report["comparison"] = performance._paired_statistics(ratios, 2026101529)
    report["median_ms_per_100"] = {arm: statistics.median(row["host_to_host_ms"] for row in report["runs"] if row["arm"] == arm)
                                   for arm in ("ocio", "cpu")}
    for name, digest in hashes.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("input changed during industry comparison")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True)
    _write_report(target, report)
    print(json.dumps({key: report[key] for key in ("median_ms_per_100", "comparison")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
