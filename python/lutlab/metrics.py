"""Evaluation metrics (exact ΔE as defined in PROBLEM.md) and C++ benchmark wrapper."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from . import io

ROOT = Path(__file__).resolve().parents[2]
JSHC_BIN = ROOT / "build" / "jshc"


def delta_e_map(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Per-pixel Euclidean RGB distance: sqrt((R1-R2)^2 + (G1-G2)^2 + (B1-B2)^2)."""
    diff = pred.astype(np.float32) - target.astype(np.float32)
    return np.sqrt(np.sum(diff * diff, axis=-1))


def summarize_delta_e(de: np.ndarray) -> dict[str, float]:
    flat = de.ravel()
    return {
        "mean": round(float(np.mean(flat)), 4),
        "rms": round(float(np.sqrt(np.mean(flat * flat))), 4),
        "p95": round(float(np.percentile(flat, 95)), 4),
        "p99": round(float(np.percentile(flat, 99)), 4),
        "max": round(float(np.max(flat)), 4),
    }


def eval_images(
    pred_fn,
    comp_lut: np.ndarray,
    image_paths: list[str | Path],
) -> dict:
    """Evaluate a prediction callable `pred_fn(img) -> img_out` against `comp_lut` over a
    list of images."""
    means, p95s, p99s, maxs = [], [], [], []
    per_image = {}
    for p in image_paths:
        img = io.load_image(p)
        gt = io.apply_full(comp_lut, img)
        pred = pred_fn(img)
        de = delta_e_map(pred, gt)
        st = summarize_delta_e(de)
        per_image[Path(p).stem] = st
        means.append(st["mean"])
        p95s.append(st["p95"])
        p99s.append(st["p99"])
        maxs.append(st["max"])
    return {
        "n_images": len(image_paths),
        "mean_de": round(float(np.mean(means)), 4),
        "worst_img_mean_de": round(float(np.max(means)), 4),
        "mean_p95_de": round(float(np.mean(p95s)), 4),
        "mean_p99_de": round(float(np.mean(p99s)), 4),
        "max_pixel_de": round(float(np.max(maxs)), 4),
        "pass_rate_mean_le_1_0": round(float(np.mean(np.array(means) <= 1.0)), 4),
        "pass_rate_mean_le_2_0": round(float(np.mean(np.array(means) <= 2.0)), 4),
        "pass_rate_p99_le_3_0": round(float(np.mean(np.array(p99s) <= 3.0)), 4),
        "per_image": per_image,
    }


def run_cpp_bench(
    slut_paths: list[str | Path],
    list_file: str | Path,
    kernel: str = "tetra_zig_simd",
    threads: int = 0,
    reps: int = 5,
    write_dir: str | Path | None = None,
) -> dict:
    cmd = [
        str(JSHC_BIN),
        "bench",
        "-l",
        str(list_file),
        "-k",
        kernel,
        "-t",
        str(threads),
        "-r",
        str(reps),
    ]
    if write_dir is not None:
        Path(write_dir).mkdir(parents=True, exist_ok=True)
        cmd += ["-w", str(write_dir)]
    cmd += [str(p) for p in slut_paths]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(res.stdout.strip())
