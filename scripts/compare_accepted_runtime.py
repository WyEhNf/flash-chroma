"""Seven paired CPU/CUDA mapping runs bound to one accepted 100-image result.

This small comparison reuses declared CPU/CUDA arms without rerunning the full
R19 configuration matrix. It never calls either arm the fastest on new models.
Each arm verifies every image output before timing. Host-to-host scopes are
kept consistent; resident GPU timing is not substituted for transfer-inclusive
latency. Accuracy gates are inherited explicitly from the accepted result.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")]
from lutlab import metrics, performance, runtime
from lutlab.entry import _write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--kernel", default="tetra_avx2_scalar_gather")
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    accepted_path, images, cpu, cuda = map(Path.resolve, (args.acceptance, args.images, args.cpu, args.cuda))
    accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
    if not (accepted.get("pass") and accepted.get("structural_contract_pass")
            and accepted.get("backend_cube_sha256_equal") and accepted.get("backend_images_sha256_equal")):
        raise RuntimeError("requires completed, locally passing CPU/CUDA acceptance")
    reference = accepted["backends"]["cpu"]
    models = [Path(path) for path in reference["runtime_command"][-4:]]
    expected = {**reference["model_sha256"], **reference["image_sha256"],
        **{row["path"]: row["sha256"] for row in accepted["sources"]},
        str(images): reference["image_list_sha256"], str(cpu): reference["executable_sha256"],
        str(cuda): accepted["backends"]["cuda"]["executable_sha256"]}
    for name, digest in expected.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError(f"accepted input/binary changed: {name}")
    files = [accepted_path, Path(__file__).resolve(), ROOT / "python/lutlab/runtime.py", ROOT / "python/lutlab/performance.py"]
    hashes = {**expected, **{str(path): metrics.file_sha256(path) for path in files}}
    environment = {"OMP_DYNAMIC": "FALSE", "OMP_PROC_BIND": "FALSE", "OMP_THREAD_LIMIT": "32",
                   "OMP_SCHEDULE": "STATIC", "JSHC_BLOCK_PIXELS": "4096", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    os.environ.update(environment)
    for name in ("OMP_PLACES", "GOMP_CPU_AFFINITY"):
        os.environ.pop(name, None)
    configurations = {"cpu": {"backend": "cpu", "executable": cpu, "kernel": args.kernel, "threads": args.threads, "batch": True},
                      "cuda": {"backend": "cuda", "executable": cuda, "threads": 0, "batch": 100}}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "input_and_source_sha256": hashes, "environment": environment, "pairs": 7, "reps_per_process": 3,
        "quality_result": str(accepted_path), "threshold_origin": accepted["threshold_origin"],
        "quality_metric": reference["metric"], "threshold_strict": reference["threshold_strict"],
        "official_score_available": accepted["official_score_available"],
        "timing_metric": "100 decoded ordinary-host RGB8 images to ordinary-host RGB8 output",
        "cpu_scope": "input working-copy plus in-place four-stage mapping; one batch team",
        "cuda_scope": "ordinary-to-pinned copy, H2D, fused4 mapping, D2H/wait, pinned-to-ordinary copy",
        "excluded": ["fit", "allocation", "model load", "decode", "encode", "checksum", "byte comparisons"],
        "configurations": {name: {key: str(value) if isinstance(value, Path) else value for key, value in config.items()}
                           for name, config in configurations.items()},
        "capabilities": {"cpu": runtime.capabilities("cpu", cpu), "cuda": runtime.capabilities("cuda", cuda)},
        "preflight": [], "runs": []}
    _write_report(args.output, report)
    with tempfile.TemporaryDirectory(prefix="accepted-preflight-") as directory:
        raw = Path(directory) / "output.rgb"
        for name, configuration in configurations.items():
            value = runtime.verify(models, images, competition=True, output=raw, **configuration)
            digest = metrics.file_sha256(raw)
            if raw.stat().st_size != 100 * 1024 * 768 * 3 or digest != reference["mapped_images_sha256"]:
                raise RuntimeError("declared mapping arm differs from accepted 100-image bytes")
            report["preflight"].append({"configuration": name, "runtime": value, "output_sha256": digest, "bit_exact": True})
            raw.unlink()
            _write_report(args.output, report)
    ratios = []
    for pair in range(7):
        order = ["cpu", "cuda"] if pair % 2 == 0 else ["cuda", "cpu"]
        values = {}
        for name in order:
            value = runtime.bench(models, images, reps=3, competition=True, **configurations[name])
            elapsed = value["set_ms_p50_rep"] if name == "cpu" else value["set_host_wall_ms_p50"]
            values[name] = elapsed
            if name == "cuda" and value["output_checksum_fnv1a64"] != reference["image_execution"]["runtime"]["output_checksum_fnv1a64"]:
                raise RuntimeError("CUDA timed output checksum differs from accepted images")
            report["runs"].append({"pair": pair, "order": order, "configuration": name,
                                   "host_to_host_ms": elapsed, "runtime": value})
            _write_report(args.output, report)
        ratios.append(values["cpu"] / values["cuda"])
        print(f"[mapping-paired] {pair + 1}/7 CPU={values['cpu']:.3f}, CUDA={values['cuda']:.3f} ms/100", flush=True)
    report["comparison"] = performance._paired_statistics(ratios, 2026101528)
    report["median_ms_per_100"] = {name: statistics.median(row["host_to_host_ms"] for row in report["runs"]
        if row["configuration"] == name) for name in configurations}
    for name, digest in hashes.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("accepted mapping input or binary changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True,
                  all_preflight_outputs_match_accepted_bytes=True)
    _write_report(args.output, report)
    print(json.dumps({key: report[key] for key in ("median_ms_per_100", "comparison")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
