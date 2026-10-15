"""Balanced paired comparison with frozen inputs and host-to-host timing."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image

from . import data, io, metrics, runtime


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _same_bytes(first, second):
    if first.stat().st_size != second.stat().st_size:
        return False
    with first.open("rb") as a, second.open("rb") as b:
        while True:
            left, right = a.read(1 << 20), b.read(1 << 20)
            if left != right:
                return False
            if not left:
                return True


def _configurations(cpu, cuda, include_ocio):
    result = {
        "scalar_t4": dict(backend="cpu", executable=cpu, kernel="tetra_scalar", threads=4, batch=False),
        "avx2_t1": dict(backend="cpu", executable=cpu, kernel="tetra_avx2", threads=1, batch=False),
        "avx2_t4": dict(backend="cpu", executable=cpu, kernel="tetra_avx2", threads=4, batch=False),
        "avx2_batch_t4": dict(backend="cpu", executable=cpu, kernel="tetra_avx2", threads=4, batch=True),
        "gather_batch_t4": dict(backend="cpu", executable=cpu, kernel="tetra_avx2_scalar_gather", threads=4, batch=True),
        "gather_batch_t16": dict(backend="cpu", executable=cpu, kernel="tetra_avx2_scalar_gather", threads=16, batch=True),
    }
    pairs = [("scalar_t4", "avx2_t4"), ("avx2_t1", "avx2_t4"),
             ("avx2_t4", "avx2_batch_t4"), ("avx2_batch_t4", "gather_batch_t4"),
             ("gather_batch_t4", "gather_batch_t16")]
    if cuda is not None:
        result.update({
            "cuda_batch1": dict(backend="cuda", executable=cuda, kernel="cuda_q16_fused4", threads=0, batch=1),
            "cuda_batch100": dict(backend="cuda", executable=cuda, kernel="cuda_q16_fused4", threads=0, batch=100),
        })
        pairs += [("avx2_batch_t4", "cuda_batch100"), ("cuda_batch1", "cuda_batch100")]
    if include_ocio:
        result["ocio_t4"] = dict(backend="ocio", threads=4)
        pairs += [("ocio_t4", "avx2_t4")]
    return result, pairs


def _paired_statistics(ratios, seed):
    values = np.asarray(ratios, dtype=np.float64)
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, (10000, len(values)), replace=True)
    medians = np.median(samples, axis=1)
    faster = int(np.count_nonzero(values > 1))
    return {"paired_ratios_reference_over_candidate": values.tolist(),
            "paired_speedup_median": float(np.median(values)),
            "paired_median_bootstrap_95_ci": np.percentile(medians, [2.5, 97.5]).tolist(),
            "candidate_faster_pairs": faster, "pair_count": len(values),
            "one_sided_sign_test_p": sum(math.comb(len(values), k) for k in range(faster, len(values) + 1)) / 2 ** len(values),
            "inference_scope": "local paired samples only; bootstrap interval is not a guarantee on other inputs or machines"}


def compare(args):
    if args.pairs < 5:
        raise ValueError("strict comparison requires at least five pairs")
    optional_tools = data.ROOT / "artifacts/r18-tools/python"
    if optional_tools.is_dir():
        sys.path.insert(0, str(optional_tools))
    models = [p.resolve() for p in args.models]
    if len(models) != 4:
        raise ValueError("exactly four models are required")
    for path in models:
        io.load_sparse(path, competition=True)
    images = args.images.resolve()
    lines = [s.strip() for s in images.read_text(encoding="utf-8").splitlines() if s.strip()]
    image_paths = [Path(s) if Path(s).is_absolute() else data.ROOT / s for s in lines]
    if len(image_paths) != 100 or len(set(map(str, image_paths))) != 100:
        raise ValueError("strict benchmark requires 100 distinct image paths")
    for path in image_paths:
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise ValueError(f"expected 1024x768 RGB8: {path}")
    cpu = runtime.resolve_backend("cpu", args.cpu_executable)
    cuda = None if args.skip_cuda else runtime.resolve_backend("cuda", args.cuda_executable)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    configurations, comparisons = _configurations(cpu, cuda, not args.skip_ocio)
    cpu_info = runtime.capabilities("cpu", cpu)
    if not cpu_info.get("avx2") or not cpu_info.get("openmp_enabled"):
        raise ValueError("this fixed comparison matrix needs an AVX2/OpenMP build; portable acceptance is separate")
    files = [cpu, *models, images, *image_paths, *([cuda] if cuda else [])]
    hashes = {str(p): metrics.file_sha256(p) for p in files}
    environment = {"OMP_DYNAMIC": "FALSE", "OMP_PROC_BIND": "FALSE",
                   "OMP_THREAD_LIMIT": "32", "OMP_SCHEDULE": "STATIC", "JSHC_BLOCK_PIXELS": "4096",
                   "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    cleared_environment = ["OMP_PLACES", "GOMP_CPU_AFFINITY"]
    for key in cleared_environment:
        os.environ.pop(key, None)
    os.environ.update(environment)
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "protocol": "predeclared comparisons, seven or more alternating AB/BA pairs; comparison order shuffled within each round",
              "pairs_requested": args.pairs, "seed": args.seed,
              "timing_metric": "ordinary host RGB8 input to ordinary host RGB8 output; decoded inputs and allocations resident",
              "excluded": ["fitting", "model load", "image decode", "allocation", "output encoding", "checksum"],
              "cpu_scope": "whole-set ordinary host input copy plus in-place four-stage mapping",
              "cuda_scope": "ordinary host input to pinned copy + H2D + four-stage mapping + D2H + ordinary host output copy",
              "ocio_scope": "four UINT8 CPUProcessor stages through Python buffer API; copy and thread task scheduling included",
              "environment": environment, "cleared_environment": cleared_environment,
              "affinity": "OS scheduler; no thread pinning is claimed",
              "cpu_capabilities": cpu_info,
              "cuda_capabilities": runtime.capabilities("cuda", cuda) if cuda else None,
              "configurations": {k: {a: str(b) if isinstance(b, Path) else b for a, b in v.items()}
                                  for k, v in configurations.items()},
              "input_and_executable_sha256": hashes,
              "preflight": [], "runs": [], "comparisons": []}
    target = output / "comparison.json"
    _write(target, report)
    reference = output / "reference-output.rgb"
    # Output equality is a separate phase, avoiding checksum work inside the
    # timing loop and preserving the exact same immutable input for each run.
    for name, config in configurations.items():
        if config["backend"] == "ocio":
            continue
        raw = reference if name == "scalar_t4" else output / "candidate-output.rgb"
        value = runtime.verify(models, images, output=raw, competition=True, **config)
        if raw.stat().st_size != 100 * 1024 * 768 * 3:
            raise RuntimeError("incomplete preflight output")
        exact = name == "scalar_t4" or _same_bytes(reference, raw)
        report["preflight"].append({"configuration": name, "bit_exact": exact,
            "output_sha256": metrics.file_sha256(raw), "runtime": value})
        _write(target, report)
        if raw != reference:
            raw.unlink()
        if not exact:
            raise RuntimeError(f"preflight byte equality failed: {name}")
        print(f"[preflight] {name}: all 100 outputs byte-identical", flush=True)
    if not args.skip_ocio:
        # General float32 OCIO is allowed to differ by rounding. Its whole-cube
        # accuracy is measured separately and never described as exact by fiat.
        industry = data.ROOT / "scripts/industry_comparison.py"
        command = [sys.executable, str(industry), "accuracy", *map(str, models),
                   "--executable", str(cpu), "--output", str(output / "ocio-accuracy.json")]
        if args.reference:
            command += ["--truth", str(args.reference.resolve())]
        process = subprocess.run(command, cwd=data.ROOT, capture_output=True, text=True, encoding="utf-8")
        (output / "ocio-accuracy.log").write_text(process.stdout + process.stderr, encoding="utf-8")
        process.check_returncode()
        report["ocio_accuracy"] = json.loads((output / "ocio-accuracy.json").read_text(encoding="utf-8"))

    rng = np.random.default_rng(args.seed)
    for pair in range(args.pairs):
        for comparison_index in rng.permutation(len(comparisons)):
            a, b = comparisons[int(comparison_index)]
            order = [a, b] if (pair + int(comparison_index)) % 2 == 0 else [b, a]
            values = {}
            for name in order:
                config = configurations[name]
                if config["backend"] == "ocio":
                    destination = output / "ocio-current.json"
                    command = [sys.executable, str(data.ROOT / "scripts/industry_comparison.py"),
                        "bench", *map(str, models), "--images", str(images), "--output", str(destination),
                        "--threads", "4", "--reps", "1"]
                    start = time.perf_counter()
                    child = subprocess.run(command, cwd=data.ROOT, capture_output=True, text=True, encoding="utf-8")
                    child.check_returncode()
                    value = json.loads(destination.read_text(encoding="utf-8"))
                    value.update(command=command, process_wall_seconds=time.perf_counter() - start,
                                 stdout=child.stdout, stderr=child.stderr)
                    measured = value["summary"][0]["median_set_ms"]
                else:
                    value = runtime.bench(models, images, reps=1, competition=True, **config)
                    measured = value["set_ms_p50_rep"] if config["backend"] == "cpu" else value["set_host_wall_ms_p50"]
                if not math.isfinite(measured) or measured <= 0:
                    raise RuntimeError("invalid timing")
                row = {"comparison": [a, b], "pair": pair, "order": order,
                       "configuration": name, "host_to_host_ms": measured, "runtime": value}
                report["runs"].append(row)
                values[name] = measured
                _write(target, report)
            print(f"[paired] round={pair + 1} {a}/{b}: {values[a]:.3f}/{values[b]:.3f} ms", flush=True)
    for index, (a, b) in enumerate(comparisons):
        rows = [row for row in report["runs"] if row["comparison"] == [a, b]]
        ratios = []
        for pair in range(args.pairs):
            values = {row["configuration"]: row["host_to_host_ms"] for row in rows if row["pair"] == pair}
            ratios.append(values[a] / values[b])
        report["comparisons"].append({"reference": a, "candidate": b,
            "reference_median_ms": statistics.median(row["host_to_host_ms"] for row in rows if row["configuration"] == a),
            "candidate_median_ms": statistics.median(row["host_to_host_ms"] for row in rows if row["configuration"] == b),
            **_paired_statistics(ratios, args.seed + index)})
    for path, digest in hashes.items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError(f"input or executable changed during comparison: {path}")
    report["inputs_unchanged"] = True
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    _write(target, report)
    print(json.dumps(report["comparisons"], indent=2))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs=4, type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--cpu-executable", type=Path)
    parser.add_argument("--cuda-executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=7)
    parser.add_argument("--seed", type=int, default=2026101519)
    parser.add_argument("--skip-cuda", action="store_true")
    parser.add_argument("--skip-ocio", action="store_true")
    compare(parser.parse_args(argv))
    return 0
