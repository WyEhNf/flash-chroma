"""One serial CUDA allocation/parity qualification and seven paired comparisons.

Only benchmark buffer lifetimes and output validation changed. Frozen R22 CPU
cube/image SHA evidence is reused after binding every model, image and program.
Timing is ordinary decoded host RGB8 input to ordinary host output; no speedup
is presumed from reducing explicit CUDA image-allocation peak.
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
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cache, metrics, runtime
from lutlab.entry import _write_report
from lutlab.performance import _paired_statistics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=ROOT / "build-gpu/jshc_gpu.exe")
    parser.add_argument("--candidate", type=Path, default=ROOT / "build-r23-gpu/jshc_gpu.exe")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r23-gpu-memory")
    args = parser.parse_args()
    baseline, candidate, output = map(Path.resolve, (args.baseline, args.candidate, args.output))
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1")
    started = time.perf_counter()
    study_path = ROOT / "artifacts/r22-structured-v3/study.json"
    frozen = json.loads(study_path.read_text(encoding="utf-8"))
    if not frozen.get("structural_and_parity_pass"):
        raise RuntimeError("R22 must be complete before using its frozen CPU evidence")
    case = next(c for c in frozen["cases"] if (c["scenario"], c["m"]) == ("clip-7", 33))
    accuracy_path = Path(case["result"])
    if metrics.file_sha256(accuracy_path) != case["result_sha256"]:
        raise RuntimeError("frozen R22 accuracy evidence changed")
    accuracy = json.loads(accuracy_path.read_text(encoding="utf-8"))
    reference = accuracy["backends"]["cpu"]
    models = list(map(Path, case["models"]))
    images = ROOT / "artifacts/r17-acceptance/bench.txt"
    frozen_hashes = {**reference["model_sha256"], **reference["image_sha256"],
        str(images): reference["image_list_sha256"], str(baseline): accuracy["backends"]["cuda"]["executable_sha256"],
        reference["executable"]: reference["executable_sha256"]}
    for name, digest in frozen_hashes.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError(f"frozen input changed: {name}")
    programs = {"baseline": baseline, "candidate": candidate}
    capabilities = {name: runtime.capabilities("cuda", path) for name, path in programs.items()}
    for key in ("device", "device_id", "compute_major", "compute_minor", "cuda_driver_version", "global_memory_bytes"):
        if capabilities["baseline"][key] != capabilities["candidate"][key]:
            raise RuntimeError("old and new executables do not target the same GPU environment")
    if capabilities["candidate"]["benchmark_schema_version"] != 3:
        raise RuntimeError("candidate lacks the new memory/parity benchmark contract")
    new_build_path, old_build_path = candidate.parent / "build-manifest.json", baseline.parent / "build-manifest.json"
    new_build = json.loads(new_build_path.read_text(encoding="utf-8-sig"))
    old_build = json.loads(old_build_path.read_text(encoding="utf-8-sig"))
    for path, build in ((candidate, new_build), (baseline, old_build)):
        if metrics.file_sha256(path) != build["executable_sha256"]:
            raise RuntimeError("build manifest does not match executable")
    for name, digest in new_build["sources_sha256"].items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("candidate build source changed")
    snapshot = ROOT / "artifacts/r22-structured-v3/source-snapshot.zip"
    with zipfile.ZipFile(snapshot) as archive:
        old_cuda_sha = hashlib.sha256(archive.read("gpu/main.cu")).hexdigest()
    if old_build["sources_sha256"][str(ROOT / "gpu/main.cu")] != old_cuda_sha:
        raise RuntimeError("old CUDA source is not the frozen R22 implementation")
    sources = {f"python/lutlab/{name}": digest for name, digest in cache.source_fingerprint().items() if name != "pixi.lock"}
    sources.update({name: metrics.file_sha256(ROOT / name) for name in (
        "pixi.lock", "gpu/main.cu", "gpu/build-windows.ps1", "cpp/third_party/stb_image.h",
        "cpp/third_party/stb_image_write.h", "python/lutlab/runtime.py", "python/lutlab/performance.py",
        "python/lutlab/metrics.py", "scripts/r23_gpu_memory_study.py")})
    fixed_paths = [study_path, accuracy_path, snapshot, new_build_path, old_build_path, candidate, *map(Path, frozen_hashes)]
    fixed_hashes = {str(path): metrics.file_sha256(path) for path in fixed_paths}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "source_sha256": sources, "frozen_input_and_binary_sha256": fixed_hashes,
        "accuracy_reference": str(accuracy_path), "accuracy_recomputed": False,
        "official_score_available": False, "capabilities": capabilities,
        "build_manifests": {"baseline": old_build, "candidate": new_build},
        "predeclared_groups": [1, 7, 100], "pairs": 7, "reps_per_process": 3,
        "timing_metric": "set_host_wall_ms_p50; includes ordinary/pinned copies, H2D, four-stage kernel, D2H and wait",
        "timing_excludes": "fit, load, allocation, decode, encoding, checksum and byte comparison",
        "memory_metric": "peak explicit CUDA image allocation payload; excludes model, allocator/driver overhead and host memory",
        "preflight": [], "runs": []}
    target = output / "study.json"
    _write_report(target, report)
    for label, build in (("baseline", old_build), ("candidate", new_build)):
        _write_report(output / f"build-{label}.json", build)

    total_bytes = 100 * 1024 * 768 * 3
    def check_result(value, mode, group):
        if value["images"] != 100 or value["output_bytes"] != total_bytes:
            raise RuntimeError("benchmark did not process exactly 100 complete RGB8 images")
        if value["output_checksum_fnv1a64"] != reference["image_execution"]["runtime"]["output_checksum_fnv1a64"]:
            raise RuntimeError("timed result checksum differs from frozen CPU evidence")
        expected = 2 * total_bytes if mode == "candidate" else 2 * total_bytes + 2 * total_bytes * group // 100
        if value["image_device_buffers_bytes"] != expected:
            raise RuntimeError("explicit CUDA image memory does not match allocation lifetimes")
        if mode == "candidate":
            if not (value["all_timing_paths_output_bytes_equal"] and value["transfer_buffers_released_before_resident"]
                    and value["resident_output_checksum_fnv1a64"] == value["output_checksum_fnv1a64"]
                    and value["transfer_image_device_buffers_bytes"] == 2 * total_bytes * group // 100
                    and value["resident_image_device_buffers_bytes"] == 2 * total_bytes):
                raise RuntimeError("new timing branch parity or lifetime contract failed")

    with tempfile.TemporaryDirectory(prefix="r23-native-") as temporary:
        raw = Path(temporary) / "output.rgb"
        cube = runtime.cube(models, raw, backend="cuda", executable=candidate, competition=True)
        cube_sha = metrics.file_sha256(raw)
        if raw.stat().st_size != 256 ** 3 * 3 or cube_sha != reference["mapped_cube_sha256"]:
            raise RuntimeError("new CUDA full cube differs from frozen CPU output")
        report["full_cube"] = {"runtime": cube, "sha256": cube_sha, "frozen_cpu_byte_equivalence_pass": True}
        raw.unlink()
        for mode, group in [("baseline", 100), *(('candidate', g) for g in (1, 7, 100))]:
            value = runtime.bench(models, images, backend="cuda", executable=programs[mode], reps=1,
                                  batch=group, competition=True, output=raw)
            check_result(value, mode, group)
            digest = metrics.file_sha256(raw)
            if raw.stat().st_size != total_bytes or digest != reference["mapped_images_sha256"]:
                raise RuntimeError("100-image benchmark output differs from frozen CPU bytes")
            report["preflight"].append({"mode": mode, "group": group, "sha256": digest, "runtime": value,
                                         "frozen_cpu_byte_equivalence_pass": True})
            raw.unlink()
            _write_report(target, report)
            print(f"[preflight] {mode}/group{group}: cube-bound 100-image bytes equal; buffers={value['image_device_buffers_bytes']}", flush=True)

    for pair in range(7):
        order = ["baseline", "candidate"] if pair % 2 == 0 else ["candidate", "baseline"]
        for mode in order:
            value = runtime.bench(models, images, backend="cuda", executable=programs[mode], reps=3,
                                  batch=100, competition=True)
            check_result(value, mode, 100)
            report["runs"].append({"pair": pair, "order": order, "mode": mode, "runtime": value})
            _write_report(target, report)
        print(f"[paired] {pair + 1}/7 complete", flush=True)
    fields = ("set_host_wall_ms_p50", "set_transfer_wall_ms_p50", "set_resident_event_ms_p50")
    report["median_ms"] = {field: {mode: statistics.median(row["runtime"][field] for row in report["runs"]
        if row["mode"] == mode) for mode in programs} for field in fields}
    report["comparisons"] = {}
    for index, field in enumerate(fields):
        ratios = []
        for pair in range(7):
            values = {r["mode"]: r["runtime"][field] for r in report["runs"] if r["pair"] == pair}
            ratios.append(values["baseline"] / values["candidate"])
        report["comparisons"][field] = _paired_statistics(ratios, 2026101523 + index)
    for name, digest in {**fixed_hashes, **{str(ROOT / name): digest for name, digest in sources.items()}}.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError(f"study input or source changed: {name}")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
        explicit_image_device_peak_bytes={"baseline": 4 * total_bytes, "candidate": 2 * total_bytes},
        all_native_paths_parity_and_memory_pass=True)
    _write_report(target, report)
    print(json.dumps({"median_ms": report["median_ms"], "host_comparison": report["comparisons"][fields[0]]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
