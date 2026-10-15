"""Validate executable output with explicit image and whole-cube threshold scopes."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from . import data, io, metrics, runtime
from .runlog import Run


def _squared_error(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    diff = pred.astype(np.int32) - truth.astype(np.int32)
    return np.sum(diff * diff, axis=-1, dtype=np.int32).ravel()


def _stats(pred: np.ndarray, truth: np.ndarray) -> tuple[dict, np.ndarray]:
    sq = _squared_error(pred, truth)
    de = np.sqrt(sq.astype(np.float64))
    return {"mean": float(de.mean()), "rms": float(np.sqrt(sq.mean())),
            "p99": float(np.percentile(de, 99)), "max": float(de.max())}, sq


@contextmanager
def _mapped_full(path: Path):
    # Close before TemporaryDirectory removes cube.raw, also on Windows/error paths.
    if path.stat().st_size != (1 << 24) * 3:
        raise ValueError(f"wrong full LUT size: {path}")
    mapped = io.load_full(path, mmap=True)
    try:
        yield mapped
    finally:
        mapped._mmap.close()


def _cube_stats(cube, comp, top_k: int, threshold: float) -> dict:
    # Exact integer histogram: no per-block floating-point percentile/sort needed.
    hist = np.zeros(3 * 255 * 255 + 1, np.int64)
    hotspots: list[tuple[int, int, int, int]] = []
    for red in range(0, 256, 8):
        sq = _squared_error(cube[red:red + 8], comp[red:red + 8])
        hist += np.bincount(sq, minlength=len(hist))
        if top_k:
            k = min(top_k, len(sq))
            for index in np.argpartition(sq, len(sq) - k)[-k:]:
                r, rem = divmod(int(index), 256 * 256)
                g, b = divmod(rem, 256)
                hotspots.append((int(sq[index]), red + r, g, b))
            hotspots.sort(reverse=True)
            del hotspots[top_k:]
    cum = np.cumsum(hist)
    n = int(cum[-1])
    de = np.sqrt(np.arange(len(hist), dtype=np.float64))
    # Match np.percentile's linear interpolation convention used for image p99.
    rank = .99 * (n - 1)
    lo, hi = int(np.floor(rank)), int(np.ceil(rank))
    low = de[np.searchsorted(cum, lo + 1)]
    high = de[np.searchsorted(cum, hi + 1)]
    return {"n_colors": n, "mean": float(np.dot(de, hist) / n),
            "rms": float(np.sqrt(np.dot(np.arange(len(hist), dtype=np.float64), hist) / n)),
            "p99": float(low + (high - low) * (rank - lo)),
            "max": float(de[np.flatnonzero(hist)[-1]]),
            "pixels_at_or_above_threshold": int(hist[de >= threshold].sum()),
            "hotspots": [{"rgb": [r, g, b], "delta_e": float(np.sqrt(sq))}
                         for sq, r, g, b in hotspots]}


def validate(paths: list[Path], composite: Path, image_list: Path, *, kernel: str,
             threads: int, threshold: float, metric: str = "mean", full_cube: bool = True,
             top_k: int = 20, executable: str | Path | None = None,
             constraint_scope: str = "images", competition: bool = False,
             semantics: str = "independent", backend: str = "cpu",
             device: int = 0, block: int = 256) -> dict:
    """Pass describes the selected local contract, never an official score.

    Only cube max bounds every pixel for a fixed LUT chain. Cube mean/p99 do not
    imply an arbitrary-image bound. No constraint scope is silently upgraded.
    """
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and nonnegative")
    if metric not in ("mean", "p99", "max"):
        raise ValueError(metric)
    if constraint_scope not in ("images", "cube", "both"):
        raise ValueError(constraint_scope)
    if semantics not in ("independent", "residual", "composite"):
        raise ValueError(semantics)
    if threads < 0 or top_k < 0:
        raise ValueError("threads and top_k must be nonnegative")
    if not full_cube and constraint_scope != "images":
        raise ValueError("cube constraints require full_cube=True")
    paths = [Path(p).resolve() for p in paths]
    if not paths:
        raise ValueError("no sparse models")
    sizes = [io.load_sparse(p).m for p in paths]
    model_contract = io.inspect_submission_contract(paths, semantics=semantics)
    sparse_contract = model_contract["pass"]
    if competition and (not sparse_contract or semantics != "independent"):
        raise ValueError("competition mode requires four independent integer LUTs with 17 <= m <= 33")
    files = [Path(s.strip()) if Path(s.strip()).is_absolute() else data.ROOT / s.strip()
             for s in Path(image_list).read_text().splitlines() if s.strip()]
    if not files:
        raise ValueError("empty image list")
    image_specs = []
    for path in files:
        with Image.open(path) as im:
            ok = im.mode == "RGB" and im.size == (1024, 768)
            image_specs.append(ok)
            if competition and not ok:
                raise ValueError(f"competition image must be 1024x768 RGB8: {path}")
    binary = runtime.resolve_backend(backend, executable)
    tracked = [binary, Path(composite).resolve(), Path(image_list).resolve(), *paths, *files]
    hashes_before = {path: metrics.file_sha256(path) for path in tracked}
    with tempfile.TemporaryDirectory(prefix="jshc-validate-") as tmp:
        raw = Path(tmp) / "cube.raw"
        execution = runtime.cube(paths, raw, backend=backend, executable=binary,
                                 kernel=kernel, threads=threads, competition=competition,
                                 device=device, block=block)
        with _mapped_full(raw) as cube, _mapped_full(Path(composite)) as comp:
            per_image = []
            for path in files:
                img = io.load_image(path)
                st, sq = _stats(io.apply_full(cube, img), io.apply_full(comp, img))
                per_image.append({"image": str(path), **st,
                                  "pixels_at_or_above_threshold": int(np.count_nonzero(
                                      np.sqrt(sq.astype(np.float64)) >= threshold)),
                                  "pass": bool(st[metric] < threshold)})
            image_pass = all(row["pass"] for row in per_image)
            contract_pass = sparse_contract and semantics == "independent" and all(image_specs)
            result = {"kernel": kernel, "backend": backend, "metric": metric, "threshold_strict": threshold,
                      "constraint_scope": constraint_scope, "semantics": semantics,
                      "competition_mode": competition, "stages": len(paths), "sizes": sizes,
                      "model_contract": model_contract,
                      "image_set_pass": image_pass, "cube_stats_computed": full_cube,
                      "cube_constraint_pass": None, "submission_contract_pass": contract_pass,
                      "submission_contract_note": "local conservative format/declared semantics only; official threshold and format are not supplied",
                      "n_images": len(files),
                      "failed_images": [row["image"] for row in per_image if not row["pass"]],
                      "worst_image_metric": max(row[metric] for row in per_image),
                      "per_image": per_image,
                      "image_list_sha256": hashes_before[Path(image_list).resolve()],
                      "image_sha256": {str(path): hashes_before[path] for path in files},
                      "model_sha256": {str(p): hashes_before[p] for p in paths},
                      "composite_sha256": hashes_before[Path(composite).resolve()],
                      "executable": str(binary), "executable_sha256": hashes_before[binary]}
            result["runtime_command"] = execution["command"]
            result["mapped_cube_sha256"] = metrics.file_sha256(raw)
            if full_cube:
                result["cube"] = _cube_stats(cube, comp, top_k, threshold)
                result["cube_constraint_pass"] = bool(result["cube"][metric] < threshold)
            selected_pass = image_pass if constraint_scope == "images" else result["cube_constraint_pass"]
            if constraint_scope == "both":
                selected_pass = selected_pass and image_pass
            result["pass"] = bool(selected_pass and (contract_pass or not competition))
    for path, expected in hashes_before.items():
        if metrics.file_sha256(path) != expected:
            raise RuntimeError(f"validation input changed during execution: {path}")
    result["inputs_unchanged"] = True
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", default="isp-0")
    ap.add_argument("--eval-list", type=Path, default=data.DATA / "eval.txt")
    ap.add_argument("--kernel", default="auto")
    ap.add_argument("--executable", type=Path)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--threshold", type=float, required=True)
    ap.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
    ap.add_argument("--constraint-scope", choices=["images", "cube", "both"], default="images")
    ap.add_argument("--competition", action="store_true")
    ap.add_argument("--semantics", choices=["independent", "residual", "composite"], default="independent")
    ap.add_argument("--skip-cube", action="store_true")
    ap.add_argument("models", nargs="+", type=Path)
    args = ap.parse_args(argv)
    with Run("validate", vars(args), commit_logs=False) as run:
        result = validate(args.models, data.scenario_dir(args.scenario) / "composite.lut256",
                          args.eval_list, kernel=args.kernel, threads=args.threads,
                          threshold=args.threshold, metric=args.metric, full_cube=not args.skip_cube,
                          executable=args.executable, constraint_scope=args.constraint_scope,
                          competition=args.competition, semantics=args.semantics)
        run.metrics.update({k: v for k, v in result.items() if k not in ("per_image", "cube")})
        run.path("validation.json").write_text(json.dumps(result, indent=2))
        print(json.dumps({k: v for k, v in result.items() if k not in ("per_image", "model_sha256")}, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
