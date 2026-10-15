"""Reproducible OpenColorIO CPU baseline with four UINT8 stage boundaries.

OpenColorIO interpolates in float, so this is an industry comparison, not a
bit-exact replacement for the project's Q16 definition. Nonuniform coordinates
are represented by a separate 256-entry shaper in each of the four processors.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "artifacts/r18-tools/python"))
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
from lutlab import io, metrics


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def processors(models, interpolation):
    result = []
    for path in models:
        # Separate raw configs isolate the processor caches for the four
        # in-memory LUTs. Reusing one config produced a verified wrong-stage
        # cache hit with this wheel; the failed adapter evidence is retained.
        config = ocio.Config.CreateRaw()
        model = io.load_sparse(path, competition=True)
        indices, fractions = model.tables()
        # These are the serialized authoritative Q16 coordinates, not axes
        # reconstructed from float32 metadata.  OCIO subsequently uses float32.
        positions = (indices.astype(np.float64) + fractions / 65536.0) / (model.m - 1)
        shaper = ocio.Lut1DTransform(length=256)
        shaper.setData(np.ascontiguousarray(positions.T, dtype=np.float32))
        shaper.setInterpolation(ocio.INTERP_LINEAR)
        lut = ocio.Lut3DTransform(gridSize=model.m)
        lut.setData(np.ascontiguousarray(model.nodes.astype(np.float32) / 255.0))
        lut.setInterpolation(ocio.INTERP_TETRAHEDRAL if interpolation == "tetrahedral" else ocio.INTERP_LINEAR)
        group = ocio.GroupTransform([shaper, lut])
        result.append(config.getProcessor(group).getOptimizedCPUProcessor(
            ocio.BIT_DEPTH_UINT8, ocio.BIT_DEPTH_UINT8, ocio.OPTIMIZATION_LOSSLESS))
    return result


def apply(chain, pixels):
    for processor in chain:
        processor.applyRGB(pixels)


def describe(args):
    module_dir = Path(ocio.__file__).parent
    return {"scope": "four independent LUTs; UINT8 input/output at every OCIO stage; float32 interpolation",
            "ocio_version": ocio.__version__, "platform": platform.platform(),
            "python": sys.version, "numpy": np.__version__,
            "ocio_binaries": {str(p): metrics.file_sha256(p) for p in module_dir.rglob("*.pyd")},
            "optimization": "OPTIMIZATION_LOSSLESS", "interpolation": args.interpolation,
            "models": {str(p.resolve()): metrics.file_sha256(p) for p in args.models},
            "script_sha256": metrics.file_sha256(__file__)}


def histogram_stats(hist):
    count = int(hist.sum())
    cumulative = np.cumsum(hist)
    position = .99 * (count - 1)
    low, high = int(np.floor(position)), int(np.ceil(position))
    roots = np.sqrt(np.arange(len(hist), dtype=np.float64))
    a, b = np.searchsorted(cumulative, [low + 1, high + 1])
    return {"count": count, "mean": float(hist @ roots / count),
            "rms": float(np.sqrt(hist @ np.arange(len(hist), dtype=np.float64) / count)),
            "p99": float(roots[a] + (position - low) * (roots[b] - roots[a])),
            "max": float(roots[np.flatnonzero(hist)[-1]])}


def accuracy(args):
    report = describe(args)
    started = time.perf_counter()
    chain = processors(args.models, args.interpolation)
    report["processor_setup_seconds"] = time.perf_counter() - started
    binary = metrics.resolve_jshc(args.executable)
    report["native_executable"] = str(binary)
    report["native_sha256"] = metrics.file_sha256(binary)
    truth = io.load_full(args.truth, mmap=True).reshape(-1, 3) if args.truth else None
    report["truth_sha256"] = metrics.file_sha256(args.truth) if args.truth else None
    hist_diff = np.zeros(3 * 255**2 + 1, np.int64)
    hist_ocio, hist_native = hist_diff.copy(), hist_diff.copy()
    mismatch_pixels, mismatch_channels = 0, 0
    example_mismatches = []
    output_sha = hashlib.sha256()
    native_file = None
    try:
        with tempfile.TemporaryDirectory(prefix="r18-ocio-") as directory:
            path = Path(directory) / "native-cube.rgb"
            command = [str(binary), "cube", "--competition", "-k", "tetra_scalar", "-t", "4",
                       "-o", str(path), *map(str, args.models)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            if path.stat().st_size != 256**3 * 3:
                raise ValueError("native cube size mismatch")
            native_file = np.memmap(path, dtype=np.uint8, mode="r", shape=(256**3, 3))
            try:
                for begin in range(0, 256**3, 262144):
                    colors = np.arange(begin, min(begin + 262144, 256**3), dtype=np.uint32)
                    pixels = np.column_stack((colors >> 16, (colors >> 8) & 255, colors & 255)).astype(np.uint8)
                    apply(chain, pixels)
                    output_sha.update(pixels.tobytes())
                    reference = native_file[begin:begin + len(colors)]
                    diff = pixels.astype(np.int32) - reference.astype(np.int32)
                    squared = np.sum(diff * diff, axis=1)
                    hist_diff += np.bincount(squared, minlength=len(hist_diff))
                    mismatch_pixels += int(np.count_nonzero(squared))
                    mismatch_channels += int(np.count_nonzero(diff))
                    if len(example_mismatches) < 8:
                        for offset in np.flatnonzero(squared)[:8 - len(example_mismatches)]:
                            example_mismatches.append({"rgb_index": int(colors[offset]),
                                "ocio": pixels[offset].tolist(), "native": reference[offset].tolist()})
                    if truth is not None:
                        expected = truth[begin:begin + len(colors)].astype(np.int32)
                        for values, hist in ((pixels, hist_ocio), (reference, hist_native)):
                            delta = values.astype(np.int32) - expected
                            hist += np.bincount(np.sum(delta * delta, axis=1), minlength=len(hist))
            finally:
                native_file._mmap.close()
                native_file = None
    finally:
        if truth is not None:
            truth._mmap.close()
    report.update({"colors": 256**3, "mismatch_pixels": mismatch_pixels,
                   "mismatch_channels": mismatch_channels, "difference": histogram_stats(hist_diff),
                   "example_mismatches": example_mismatches, "output_sha256": output_sha.hexdigest(),
                   "ocio_vs_truth": histogram_stats(hist_ocio) if args.truth else None,
                   "native_vs_truth": histogram_stats(hist_native) if args.truth else None,
                   "elapsed_seconds": time.perf_counter() - started,
                   "bit_exact": mismatch_pixels == 0})
    for filename, expected in report["models"].items():
        if metrics.file_sha256(filename) != expected:
            raise RuntimeError("model changed during comparison")
    write_json(args.output, report)
    print(json.dumps(report, indent=2))


def bench(args):
    report = describe(args)
    paths = [Path(x.strip()) for x in args.images.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(paths) != 100 or len(set(paths)) != 100:
        raise ValueError("benchmark requires 100 distinct frozen frames")
    images = []
    for path in paths:
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise ValueError("expected 1024x768 RGB8")
            images.append(np.array(image))
    report["image_sha256"] = {str(p): metrics.file_sha256(p) for p in paths}
    report["list_sha256"] = metrics.file_sha256(args.images)
    started = time.perf_counter()
    chain = processors(args.models, args.interpolation)
    report["processor_setup_ms"] = (time.perf_counter() - started) * 1000
    cold = images[0].copy()
    started = time.perf_counter()
    apply(chain, cold)
    report["cold_apply_ms"] = (time.perf_counter() - started) * 1000
    report["runs"] = []
    # Each native apply releases the GIL. Per-worker reuse avoids allocating one
    # float image per stage or hiding a batch-sized duplicate in the comparison.
    def task(index, work):
        begin = time.perf_counter()
        np.copyto(work, images[index])
        copied = time.perf_counter()
        apply(chain, work)
        return (copied - begin) * 1000, (time.perf_counter() - copied) * 1000

    for workers in args.threads:
        buffers = [np.empty_like(images[0]) for _ in range(workers)]
        # Deterministic partitions, native per-image serial LUT processing.
        def partition(worker):
            return [task(i, buffers[worker]) for i in range(worker, len(images), workers)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for repetition in range(args.reps):
                begin = time.perf_counter()
                values = list(pool.map(partition, range(workers)))
                elapsed = (time.perf_counter() - begin) * 1000
                row = {"workers": workers, "repetition": repetition, "set_ms": elapsed,
                       "per_image_ms": elapsed / len(images), "worker_buffer_bytes": sum(x.nbytes for x in buffers),
                       "sum_worker_copy_ms": sum(t[0] for part in values for t in part),
                       "sum_worker_apply_ms": sum(t[1] for part in values for t in part)}
                report["runs"].append(row)
                print(json.dumps(row), flush=True)
    report["summary"] = [{"workers": workers,
        "median_set_ms": statistics.median(x["set_ms"] for x in report["runs"] if x["workers"] == workers)}
        for workers in args.threads]
    report["timing_scope"] = "host RGB8 to host RGB8: copy + four native OCIO UINT8 applies + Python task scheduling; decoded inputs resident; fitting/loading/encoding excluded"
    for filename, expected in {**report["models"], **report["image_sha256"]}.items():
        if metrics.file_sha256(filename) != expected:
            raise RuntimeError("input changed during comparison")
    write_json(args.output, report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["accuracy", "bench"])
    parser.add_argument("models", nargs=4, type=Path)
    parser.add_argument("--interpolation", choices=["tetrahedral", "trilinear"], default="tetrahedral")
    parser.add_argument("--truth", type=Path)
    parser.add_argument("--executable", type=Path, default=ROOT / "artifacts/r18-baseline/jshc-r17.exe")
    parser.add_argument("--images", type=Path, default=ROOT / "artifacts/r17-acceptance/bench.txt")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", nargs="+", type=int, default=[1, 4, 16])
    parser.add_argument("--reps", type=int, default=5)
    args = parser.parse_args()
    if args.reps < 1 or any(t < 1 for t in args.threads):
        parser.error("repetitions and workers must be positive")
    (accuracy if args.command == "accuracy" else bench)(args)


if __name__ == "__main__":
    main()
