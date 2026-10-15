"""One staged GPU parity batch and bounded, explicitly scoped GPU timing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from lutlab import data, interp, io, metrics
from phase_acceptance import verify_inputs


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def command(arguments):
    started = time.perf_counter()
    result = subprocess.run(list(map(str, arguments)), cwd=data.ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    record = {"command": list(map(str, arguments)), "returncode": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr,
              "process_wall_seconds": time.perf_counter() - started}
    if result.returncode:
        raise RuntimeError(json.dumps(record))
    record["result"] = json.loads(result.stdout) if result.stdout.strip() else None
    return record


def provenance(args):
    gpu = args.gpu.resolve()
    return {"platform": platform.platform(), "python": platform.python_version(),
            "gpu_executable": str(gpu), "gpu_executable_sha256": metrics.file_sha256(gpu),
            "gpu_capabilities": command([gpu, "info"]),
            "source_sha256": {str(path.relative_to(data.ROOT)): metrics.file_sha256(path)
                              for path in (data.ROOT / "gpu/main.cu", Path(__file__).resolve())}}


def controls(directory):
    directory.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026101518)
    paths = []
    for stage, m in enumerate((17, 18, 26, 33), 1):
        t = np.linspace(0, 1, m)
        grid = np.stack([255 * t ** 1.13, 255 * t, 255 * t ** .87])
        grid[:, 0], grid[:, -1] = 0, 255
        nodes = rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)
        path = directory / f"stage{stage}.slut"
        io.save_sparse(path, io.SparseLut(grid, nodes))
        paths.append(path)
    return paths


def parity(args):
    report = {**provenance(args), "scope": "GPU exact integer parity; independent CPU scalar full cube and Python Q16 tails",
              "cpu_executable": str(args.cpu.resolve()), "cpu_executable_sha256": metrics.file_sha256(args.cpu),
              "cases": []}
    real = data.ROOT / "artifacts/r17-algorithm/isp-0/baseline_m18"
    cases = [("frozen_isp0_m18", [real / f"stage{k}.slut" for k in range(1, 5)]),
             ("mixed_nonuniform_m17_18_26_33", controls(args.out / "mixed-control"))]
    for name, models in cases:
        cpu_output, gpu_output = args.out / f"{name}-cpu.raw", args.out / f"{name}-gpu.raw"
        record = {"name": name, "models": {str(path): metrics.file_sha256(path) for path in models}}
        record["cpu"] = command([args.cpu, "cube", "-o", cpu_output, "-k", "tetra_scalar", "-t", "4", *models])
        record["gpu"] = command([args.gpu, "cube", "-o", gpu_output, *models])
        record["cpu_output_sha256"] = metrics.file_sha256(cpu_output)
        record["gpu_output_sha256"] = metrics.file_sha256(gpu_output)
        record["bit_exact"] = cpu_output.stat().st_size == gpu_output.stat().st_size == io.FULL_NBYTES and record["cpu_output_sha256"] == record["gpu_output_sha256"]
        report["cases"].append(record)
        write(args.out / "correctness.json", report)
        if not record["bit_exact"]:
            raise RuntimeError(f"GPU full cube parity failed for {name}")
        print(f"[gpu-parity] {name}: all 16,777,216 RGB inputs exact", flush=True)
    models = cases[1][1]
    chain = [io.load_sparse(path) for path in models]
    report["tails"] = []
    for count in (1, 257, 4099):
        points = np.random.default_rng(count).integers(0, 256, (count, 3), dtype=np.uint8)
        points[0] = [255, 255, 255]
        if count > 1:
            points[1] = [0, 0, 0]
        truth = points.copy()
        for model in chain:
            truth = interp.apply_tetra_q16(model, truth)
        source, output = args.out / f"tail-{count}-input.raw", args.out / f"tail-{count}-output.raw"
        points.tofile(source)
        record = command([args.gpu, "pixels", "-i", source, "-o", output, *models])
        predicted = np.fromfile(output, dtype=np.uint8).reshape(-1, 3)
        exact = np.array_equal(predicted, truth)
        report["tails"].append({"count": count, "bit_exact": exact, "gpu": record,
                                 "output_sha256": metrics.file_sha256(output)})
        if not exact:
            write(args.out / "correctness.json", report)
            raise RuntimeError(f"GPU tail parity failed for count={count}")
    report["pass"] = True
    if metrics.file_sha256(args.gpu) != report["gpu_executable_sha256"] or metrics.file_sha256(args.cpu) != report["cpu_executable_sha256"]:
        raise RuntimeError("executable changed during parity")
    write(args.out / "correctness.json", report)
    print("[gpu-parity] independent Python tails exact", flush=True)


def benchmark(args):
    verify_inputs(args.inputs)
    models = [data.ROOT / "artifacts/r17-algorithm/isp-0/baseline_m18" / f"stage{k}.slut" for k in range(1, 5)]
    report = {**provenance(args), "scope": "frozen synthetic100; GPU batch throughput and per-image transfer mode measured separately",
              "input_manifest_sha256": metrics.file_sha256(args.inputs / "input-manifest.json"),
              "models": {str(path): metrics.file_sha256(path) for path in models}, "runs": []}
    for batch in args.batch_images:
        result = command([args.gpu, "bench", "-l", args.inputs / "bench.txt", "-r", args.reps,
                          "--batch-images", batch, "--block", args.block, *models])
        if result["result"]["images"] != 100:
            raise RuntimeError("GPU benchmark did not process all 100 images")
        report["runs"].append(result)
        write(args.out / "benchmark.json", report)
        value = result["result"]
        print(f"[gpu-bench] batch={batch}: transfer wall={value['set_transfer_wall_ms_p50']:.3f} ms/100; resident events={value['set_resident_event_ms_p50']:.3f} ms/100", flush=True)
    verify_inputs(args.inputs)
    for filename, digest in report["models"].items():
        if metrics.file_sha256(filename) != digest:
            raise RuntimeError("model changed during benchmark")
    if metrics.file_sha256(args.gpu) != report["gpu_executable_sha256"]:
        raise RuntimeError("GPU executable changed during benchmark")
    report["inputs_unchanged"] = True
    write(args.out / "benchmark.json", report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "bench"])
    parser.add_argument("--gpu", type=Path, default=data.ROOT / "artifacts/r18-gpu/build/jshc_gpu.exe")
    parser.add_argument("--cpu", type=Path, default=data.ROOT / "artifacts/r18-baseline/jshc-r17.exe")
    parser.add_argument("--out", type=Path, default=data.ROOT / "artifacts/r18-gpu")
    parser.add_argument("--inputs", type=Path, default=data.ROOT / "artifacts/r17-acceptance")
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--batch-images", type=int, nargs="+", default=[1, 100])
    parser.add_argument("--block", type=int, default=256)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    (parity if args.command == "check" else benchmark)(args)


if __name__ == "__main__":
    main()
