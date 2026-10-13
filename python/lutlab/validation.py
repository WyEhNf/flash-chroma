"""Exact executable-output validation against the composed 256^3 reference LUT."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from . import data, io, metrics
from .runlog import Run


def _stats(pred: np.ndarray, truth: np.ndarray) -> tuple[dict, np.ndarray]:
    diff = pred.astype(np.int16) - truth.astype(np.int16)
    sq = np.sum(diff.astype(np.int32) ** 2, axis=-1).ravel()
    de = np.sqrt(sq.astype(np.float64))
    return {"mean": float(de.mean()), "rms": float(np.sqrt(sq.mean())),
            "p99": float(np.percentile(de, 99)), "max": float(de.max())}, sq


def validate(paths: list[Path], composite: Path, image_list: Path, *, kernel: str,
             threads: int, threshold: float, metric: str = "mean", full_cube: bool = True,
             top_k: int = 20) -> dict:
    """Pass requires every image metric strictly below threshold, using unrounded values."""
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and nonnegative")
    if metric not in ("mean", "p99", "max"):
        raise ValueError(metric)
    comp = io.load_full(composite, mmap=True)
    files = [Path(s) if Path(s).is_absolute() else data.ROOT / s
             for s in image_list.read_text().splitlines() if s.strip()]
    if not files:
        raise ValueError("empty image list")
    with tempfile.TemporaryDirectory(prefix="jshc-validate-") as tmp:
        raw = Path(tmp) / "cube.raw"
        subprocess.run([str(metrics.JSHC_BIN), "cube", "-o", str(raw), "-k", kernel,
                        "-t", str(threads), *map(str, paths)], check=True)
        if raw.stat().st_size != (1 << 24) * 3:
            raise ValueError("wrong cube output size")
        cube = np.memmap(raw, dtype=np.uint8, mode="r", shape=io.FULL_SHAPE)
        per_image = []
        for p in files:
            img = io.load_image(p)
            gt = io.apply_full(comp, img)
            pred = io.apply_full(cube, img)
            st, _ = _stats(pred, gt)
            per_image.append({"image": str(p), **st, "pass": bool(st[metric] < threshold)})
        result = {"kernel": kernel, "metric": metric, "threshold_strict": threshold,
                  "pass": all(x["pass"] for x in per_image), "n_images": len(files),
                  "failed_images": [x["image"] for x in per_image if not x["pass"]],
                  "worst_image_metric": max(x[metric] for x in per_image),
                  "per_image": per_image,
                  "model_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  "composite_sha256": hashlib.sha256(composite.read_bytes()).hexdigest()}
        if full_cube:
            hist = np.zeros(3 * 255 * 255 + 1, np.int64)
            hotspots: list[tuple[int, int, int, int]] = []
            for red in range(0, 256, 8):
                pred = cube[red:red + 8]
                gt = comp[red:red + 8]
                _, sq = _stats(pred, gt)
                hist += np.bincount(sq, minlength=len(hist))
                indices = np.argpartition(sq, -min(top_k, len(sq)))[-top_k:]
                for idx in indices:
                    r, rem = divmod(int(idx), 256 * 256)
                    g, b = divmod(rem, 256)
                    hotspots.append((int(sq[idx]), red + r, g, b))
                hotspots.sort(reverse=True)
                del hotspots[top_k:]
            cum = np.cumsum(hist)
            n = int(cum[-1])
            result["cube"] = {
                "n_colors": n, "mean": float(np.dot(np.sqrt(np.arange(len(hist))), hist) / n),
                "rms": float(np.sqrt(np.dot(np.arange(len(hist), dtype=np.float64), hist) / n)),
                "p99": float(np.sqrt(np.searchsorted(cum, np.ceil(.99 * n)))),
                "max": float(np.sqrt(np.flatnonzero(hist)[-1])),
                "hotspots": [{"rgb": [r, g, b], "delta_e": float(np.sqrt(sq))}
                             for sq, r, g, b in hotspots],
            }
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", default="isp-0")
    ap.add_argument("--eval-list", type=Path, default=data.DATA / "eval.txt")
    ap.add_argument("--kernel", default="tetra_zig_simd")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--threshold", type=float, required=True,
                    help="Explicit local/official limit; each image must be strictly below it")
    ap.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
    ap.add_argument("--skip-cube", action="store_true")
    ap.add_argument("models", nargs="+", type=Path)
    args = ap.parse_args(argv)
    with Run("validate", vars(args)) as run:
        result = validate(args.models, data.scenario_dir(args.scenario) / "composite.lut256",
                          args.eval_list, kernel=args.kernel, threads=args.threads,
                          threshold=args.threshold, metric=args.metric, full_cube=not args.skip_cube)
        run.metrics.update({k: v for k, v in result.items() if k not in ("per_image", "cube")})
        run.path("validation.json").write_text(json.dumps(result, indent=2))
        print(json.dumps({k: v for k, v in result.items() if k not in ("per_image", "model_sha256")}, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
