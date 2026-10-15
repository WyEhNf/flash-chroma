"""Shared process adapter for the CPU and optional exact CUDA implementations.

The executable remains an explicit deployment choice. Selecting CUDA never falls
back to CPU, and device-only timings are never relabelled as host timings.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
BACKENDS = ("cpu", "cuda")


def _backend(value: str) -> str:
    if value not in BACKENDS:
        raise ValueError(f"backend must be one of {BACKENDS}, got {value!r}")
    return value


def resolve_backend(backend: str = "cpu", executable: str | Path | None = None) -> Path:
    """Resolve explicit path, backend-specific environment, then standard build."""
    _backend(backend)
    environment = "JSHC_BIN" if backend == "cpu" else "JSHC_CUDA_BIN"
    name = "jshc" if backend == "cpu" else "jshc_gpu"
    folder = "build" if backend == "cpu" else "build-gpu"
    suffix = ".exe" if os.name == "nt" else ""
    path = Path(executable or os.environ.get(environment) or ROOT / folder / (name + suffix)).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"{backend} executable not found: {path}; set {environment} or pass executable")
    return path


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class BackendError(RuntimeError):
    """A failed invocation with its command and captured diagnostics attached."""

    def __init__(self, message: str, record: dict):
        super().__init__(message)
        self.record = record


def _execute(command: list[str]) -> dict:
    """Capture pipes without deadlock, optionally observe the host process at 25 ms."""
    try:
        import psutil
    except ImportError:
        psutil = None
    started = time.perf_counter()
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace")
    observer = None
    if psutil is not None:
        try:
            observer = psutil.Process(process.pid)
        except psutil.Error:
            pass
    peak = None
    cpu_percent = None
    samples = 0
    memory_scope = None

    def sample() -> None:
        nonlocal peak, cpu_percent, samples, memory_scope
        if observer is None:
            return
        try:
            memory = observer.memory_info()
            value = getattr(memory, "peak_wset", memory.rss)
            peak = max(peak or 0, value)
            memory_scope = "OS peak working set" if hasattr(memory, "peak_wset") else "sampled resident set; short peaks may be missed"
            usage = observer.cpu_times()
            duration = time.perf_counter() - started
            if duration > 0:
                cpu_percent = 100 * (usage.user + usage.system) / duration
            samples += 1
        except psutil.Error:
            pass

    try:
        while True:
            sample()
            try:
                stdout, stderr = process.communicate(timeout=0.025)
                sample()
                break
            except subprocess.TimeoutExpired:
                continue
    except BaseException:
        process.kill()
        process.communicate()
        raise
    return {
        "returncode": process.returncode, "stdout": stdout, "stderr": stderr,
        "process_wall_seconds": time.perf_counter() - started,
        "observed_peak_working_set_bytes": peak, "host_cpu_percent": cpu_percent,
        "host_process_samples": samples,
        "host_memory_scope": memory_scope,
        "host_cpu_scope": "whole subprocess sampled CPU time; 100 percent is one logical CPU; excludes GPU utilization" if samples else None,
        "host_sampling_interval_ms": 25 if observer is not None else None,
    }


def _run(backend: str, executable: str | Path | None, arguments: list[str], models: list[Path] | None = None) -> dict:
    binary = resolve_backend(backend, executable)
    digest = _sha256(binary)
    model_hashes = {str(path): _sha256(path) for path in (models or [])}
    command = [str(binary), *arguments, *(str(path) for path in (models or []))]
    process = _execute(command)
    record = {
        "backend": backend, "executable": str(binary), "executable_sha256": digest,
        "models_sha256": model_hashes, "command": command,
        **process,
    }
    if process["returncode"]:
        raise BackendError(f"{backend} {arguments[0]} failed ({process['returncode']}): {process['stderr'].strip()}", record)
    try:
        result = json.loads(process["stdout"]) if process["stdout"].strip() else {}
    except json.JSONDecodeError as error:
        raise BackendError(f"{backend} returned invalid JSON: {error}", record) from error
    if not isinstance(result, dict):
        raise BackendError(f"{backend} returned a non-object JSON result", record)
    if _sha256(binary) != digest or any(_sha256(Path(path)) != value for path, value in model_hashes.items()):
        raise BackendError("executable or model changed during invocation", record)
    return {**result, **record}


def _models(paths: Iterable[str | Path], backend: str, competition: bool) -> list[Path]:
    result = [Path(path).resolve() for path in paths]
    if not result:
        raise ValueError("at least one sparse model is required")
    if (backend == "cuda" or competition) and len(result) != 4:
        raise ValueError("CUDA and competition mode require exactly four sparse stages")
    for path in result:
        if not path.is_file():
            raise FileNotFoundError(f"sparse model not found: {path}")
    return result


def _options(backend: str, kernel: str, threads: int, competition: bool, device: int, block: int) -> list[str]:
    _backend(backend)
    if threads < 0:
        raise ValueError("threads must be nonnegative")
    if backend == "cpu":
        if device != 0 or block != 256:
            raise ValueError("device and block are CUDA-only options")
        if kernel == "cuda_q16_fused4":
            raise ValueError("cuda_q16_fused4 requires backend='cuda'")
        result = ["-k", kernel, "-t", str(threads)]
    else:
        if kernel not in ("auto", "cuda_q16_fused4"):
            raise ValueError("CUDA supports only auto or cuda_q16_fused4")
        if threads != 0:
            raise ValueError("threads is a CPU-only option; use block for CUDA")
        if device < 0 or block < 32 or block > 1024 or block % 32:
            raise ValueError("CUDA device must be nonnegative and block a multiple of 32 in [32,1024]")
        result = ["--device", str(device), "--block", str(block)]
    if competition:
        result.append("--competition")
    return result


def _batch_options(backend: str, batch: bool | int) -> list[str]:
    size = 100 if batch is True else 1 if batch is False else batch
    if not isinstance(size, int) or not 1 <= size <= 100:
        raise ValueError("batch must be False/1, True/100, or a CUDA group size in [1,100]")
    if backend == "cpu":
        if size not in (1, 100):
            raise ValueError("CPU batch supports only 1 (per image) or 100 (one image set)")
        return ["--batch"] if size == 100 else []
    return ["--batch-images", str(size)]


def capabilities(backend: str = "cpu", executable: str | Path | None = None, *, device: int = 0) -> dict:
    """Query the actual executable/device, including native kernel availability."""
    _backend(backend)
    if device < 0 or (backend == "cpu" and device != 0):
        raise ValueError("device must be nonnegative and is CUDA-only")
    return _run(backend, executable, ["info", *(["--device", str(device)] if backend == "cuda" else [])])


def apply(models: Iterable[str | Path], input: str | Path, output: str | Path, *, backend: str = "cpu",
          executable: str | Path | None = None, kernel: str = "auto", threads: int = 0,
          competition: bool = False, device: int = 0, block: int = 256) -> dict:
    """Decode one image, apply the chain, and write a PNG (CUDA) or CPU-supported image."""
    arguments = ["apply", "-i", str(Path(input).resolve()), "-o", str(Path(output).resolve()),
                 *_options(backend, kernel, threads, competition, device, block)]
    return _run(backend, executable, arguments, _models(models, backend, competition))


def cube(models: Iterable[str | Path], output: str | Path, *, backend: str = "cpu",
         executable: str | Path | None = None, kernel: str = "auto", threads: int = 0,
         competition: bool = False, device: int = 0, block: int = 256) -> dict:
    """Write all 256^3 mapped RGB8 values, with B-fastest input-index ordering."""
    arguments = ["cube", "-o", str(Path(output).resolve()),
                 *_options(backend, kernel, threads, competition, device, block)]
    return _run(backend, executable, arguments, _models(models, backend, competition))


def bench(models: Iterable[str | Path], list_file: str | Path, *, backend: str = "cpu",
          executable: str | Path | None = None, kernel: str = "auto", threads: int = 0,
          reps: int = 5, batch: bool | int = False, competition: bool = False,
          device: int = 0, block: int = 256, write_dir: str | Path | None = None,
          output: str | Path | None = None) -> dict:
    """Return native timings without mixing host, pinned-transfer and resident scopes."""
    if reps < 1:
        raise ValueError("reps must be positive")
    arguments = ["bench", "-l", str(Path(list_file).resolve()), "-r", str(reps),
                 *_options(backend, kernel, threads, competition, device, block), *_batch_options(backend, batch)]
    if write_dir is not None:
        if backend != "cpu":
            raise ValueError("write_dir is CPU-only; use CUDA output for concatenated raw RGB")
        directory = Path(write_dir).resolve()
        directory.mkdir(parents=True, exist_ok=True)
        arguments.extend(["-w", str(directory)])
    if output is not None:
        if backend != "cuda":
            raise ValueError("bench output is CUDA-only; use verify(output=...) for both backends")
        arguments.extend(["-o", str(Path(output).resolve())])
    return _run(backend, executable, arguments, _models(models, backend, competition))


def verify(models: Iterable[str | Path], list_file: str | Path, *, backend: str = "cpu",
           executable: str | Path | None = None, kernel: str = "auto", threads: int = 0,
           batch: bool | int = False, competition: bool = False, device: int = 0,
           block: int = 256, output: str | Path | None = None) -> dict:
    """Map once, consume every output byte, and optionally write list-order raw RGB."""
    arguments = ["verify", "-l", str(Path(list_file).resolve()),
                 *_options(backend, kernel, threads, competition, device, block), *_batch_options(backend, batch)]
    if output is not None:
        arguments.extend(["-o", str(Path(output).resolve())])
    return _run(backend, executable, arguments, _models(models, backend, competition))
