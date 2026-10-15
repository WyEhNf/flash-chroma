"""Bounded phase acceptance: frozen synthetic inputs and alternating whole-set timing.

No model selection or parameter sweep happens here. Supply the four frozen models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time

import numpy as np
from PIL import Image

from lutlab import data, metrics, validation


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def prepare(out: Path):
    rng = np.random.default_rng(20261015)
    images = data._synthetic(rng)
    directory = out / "inputs"
    directory.mkdir(parents=True, exist_ok=True)
    evaluation = []
    for name, array in images.items():
        path = directory / f"{name}.png"
        Image.fromarray(array).save(path, compress_level=1)
        evaluation.append(path.resolve())
    benchmark = []
    bases = list(images.values())
    for index in range(100):
        # 100 reproducible RGB8 frames; no natural-photo quality claim is implied.
        frame = np.roll(bases[index % len(bases)], (index * 13, index * 17), axis=(0, 1))
        if index % 2:
            frame = frame[:, ::-1]
        scale = 192 + (index * 19) % 97
        frame = np.clip((frame.astype(np.uint32) * scale + 128) // 256, 0, 255).astype(np.uint8)
        path = directory / f"bench-{index:03d}.ppm"
        Image.fromarray(frame).save(path)
        benchmark.append(path.resolve())
    for name, paths in (("eval", evaluation), ("bench", benchmark)):
        (out / f"{name}.txt").write_text("\n".join(map(str, paths)) + "\n", encoding="utf-8")
    manifest = {"seed": 20261015, "source": "synthetic-only; five families, 100 derived frames",
                "size": [1024, 768], "channels": "RGB8", "evaluation_images": len(evaluation),
                "benchmark_images": len(benchmark),
                "generator_sha256": metrics.file_sha256(__file__),
                "lists": {name: metrics.file_sha256(out / f"{name}.txt") for name in ("eval", "bench")},
                "files": {str(path): metrics.file_sha256(path) for path in evaluation + benchmark}}
    write_json(out / "input-manifest.json", manifest)
    print(json.dumps({"prepared": str(out), "eval": len(evaluation), "bench": len(benchmark)}))


def verify_inputs(out: Path):
    manifest = json.loads((out / "input-manifest.json").read_text())
    for name, count in (("eval", 5), ("bench", 100)):
        listing = out / f"{name}.txt"
        if metrics.file_sha256(listing) != manifest["lists"][name]:
            raise ValueError(f"frozen input list changed: {listing}")
        files = [line.strip() for line in listing.read_text().splitlines() if line.strip()]
        if len(files) != count or len(set(files)) != count:
            raise ValueError(f"expected {count} distinct {name} images")
        if any(filename not in manifest["files"] for filename in files):
            raise ValueError(f"unfrozen path in {listing}")
    for filename, expected in manifest["files"].items():
        if metrics.file_sha256(filename) != expected:
            raise ValueError(f"frozen input changed: {filename}")
    return manifest


def measured_run(command, cwd):
    try:
        import psutil
    except ImportError:
        psutil = None
    if psutil:
        psutil.cpu_percent()
    started = time.perf_counter()
    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    peak = 0
    monitor = psutil.Process(process.pid) if psutil else None
    while process.poll() is None:
        if monitor:
            try:
                memory = monitor.memory_info()
                peak = max(peak, memory.rss, getattr(memory, "peak_wset", 0))
            except psutil.Error:
                pass
        time.sleep(.025)
    stdout, stderr = process.communicate()
    row = {"command": command, "returncode": process.returncode, "stdout": stdout, "stderr": stderr,
           "process_wall_seconds": time.perf_counter() - started,
           "observed_peak_working_set_bytes": peak or None,
           "host_cpu_percent_during_process": psutil.cpu_percent() if psutil else None}
    if process.returncode == 0:
        row["result"] = json.loads(stdout)
    return row


def benchmark(args):
    binary = metrics.resolve_jshc(args.executable)
    info = json.loads(subprocess.check_output([str(binary), "info"], text=True))
    if "tetra_avx2" not in info["available_kernels"]:
        raise RuntimeError("AVX2 benchmark requires confirmed compiled and executable support")
    models = [path.resolve() for path in args.models]
    if len(models) != 4:
        raise ValueError("benchmark requires four frozen independent models")
    verify_inputs(args.out)
    report = {"scope": "same-build scalar vs AVX2; synthetic100; no inference about official hardware",
              "platform": platform.platform(), "python": platform.python_version(),
              "executable": str(binary), "executable_sha256": metrics.file_sha256(binary),
              "capabilities": info, "input_manifest_sha256": metrics.file_sha256(args.out / "input-manifest.json"),
              "models": {str(path): metrics.file_sha256(path) for path in models},
              "environment": {key: os.environ.get(key) for key in
                              ("OMP_NUM_THREADS", "OMP_SCHEDULE", "JSHC_BLOCK_PIXELS")}, "runs": []}
    for threads in args.threads:
        for pair in range(args.pairs):
            order = ["tetra_scalar", "tetra_avx2"]
            if pair % 2:
                order.reverse()
            for kernel in order:
                command = [str(binary), "bench", "--competition", "-l", str((args.out / "bench.txt").resolve()),
                           "-k", kernel, "-t", str(threads), "-r", "1", *map(str, models)]
                row = measured_run(command, data.ROOT)
                row.update({"pair": pair, "kernel": kernel, "threads": threads})
                report["runs"].append(row)
                write_json(args.out / "benchmark.json", report)
                if row["returncode"]:
                    raise RuntimeError(row["stderr"])
                if row["result"]["images"] != 100:
                    raise ValueError("benchmark did not execute all 100 images")
                print(f"threads={threads} pair={pair} {kernel}: {row['result']['set_ms_p50_rep']:.3f} ms/100", flush=True)
    summaries = []
    for threads in args.threads:
        rows = [r for r in report["runs"] if r["threads"] == threads]
        medians = {kernel: statistics.median(r["result"]["set_ms_p50_rep"] for r in rows if r["kernel"] == kernel)
                   for kernel in ("tetra_scalar", "tetra_avx2")}
        ratios = []
        for pair in range(args.pairs):
            times = {r["kernel"]: r["result"]["set_ms_p50_rep"] for r in rows if r["pair"] == pair}
            ratios.append(times["tetra_scalar"] / times["tetra_avx2"])
        summaries.append({"threads": threads, "set_ms_medians": medians,
                          "paired_speedup": ratios, "paired_speedup_median": statistics.median(ratios),
                          "avx2_ms_per_image": medians["tetra_avx2"] / 100,
                          "all_pairs_faster": all(ratio > 1 for ratio in ratios)})
    report["summary"] = summaries
    for filename, expected in report["models"].items():
        if metrics.file_sha256(filename) != expected:
            raise RuntimeError(f"benchmark model changed during execution: {filename}")
    if metrics.file_sha256(binary) != report["executable_sha256"]:
        raise RuntimeError("benchmark executable changed during execution")
    verify_inputs(args.out)
    report["inputs_unchanged"] = True
    write_json(args.out / "benchmark.json", report)
    print(json.dumps(summaries, indent=2))


def accuracy(args):
    """Predeclared four-model batch, chosen after the separate sampled study."""
    source = data.ROOT / "artifacts" / "r17-algorithm"
    verify_inputs(args.out)
    report = {"scope": "actual executable, all 2^24 RGB colours and five synthetic RGB8 images",
              "threshold_note": "2.0 mean Delta E is an illustrative local threshold, not official",
              "sampled_study_sha256": metrics.file_sha256(source / "study.json"),
              "input_manifest_sha256": metrics.file_sha256(args.out / "input-manifest.json"), "results": []}
    for scenario, variant in (("clip-7", "baseline_m17"), ("clip-7", "q16_m17"),
                              ("isp-0", "baseline_m17"), ("isp-0", "baseline_m18")):
        models = [source / scenario / variant / f"stage{stage}.slut" for stage in range(1, 5)]
        result = validation.validate(models, source / scenario / "composite.lut256", args.out / "eval.txt",
            kernel="auto", threads=4, threshold=2.0, metric="mean", full_cube=True,
            executable=args.executable, competition=True, constraint_scope="both", semantics="independent")
        report["results"].append({"scenario": scenario, "variant": variant, "validation": result})
        write_json(args.out / "accuracy.json", report)
        print(json.dumps({"scenario": scenario, "variant": variant, "mean": result["cube"]["mean"],
                          "p99": result["cube"]["p99"], "max": result["cube"]["max"],
                          "worst_image_mean": result["worst_image_metric"], "local_pass": result["pass"]}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "accuracy", "bench"])
    parser.add_argument("--out", type=Path, default=data.ROOT / "artifacts" / "r17-acceptance")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--threads", nargs="+", type=int, default=[1, 4])
    parser.add_argument("--pairs", type=int, default=5)
    parser.add_argument("models", type=Path, nargs="*")
    args = parser.parse_args()
    if args.pairs < 1 or any(threads < 1 for threads in args.threads):
        parser.error("pairs and threads must be positive")
    if args.command == "prepare":
        prepare(args.out)
    elif args.command == "accuracy":
        accuracy(args)
    else:
        benchmark(args)


if __name__ == "__main__":
    main()
