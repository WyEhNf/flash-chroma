"""Dataset construction: test images (1024x768 RGB) and LUT scenarios."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

from . import io, luts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
W, H = 1024, 768
KODAK_URL = "https://r0k.us/graphics/kodak/kodak/kodim{:02d}.png"


def _fetch_kodak(dst: Path, allow_synthetic_only: bool = False) -> list[Path]:
    dst.mkdir(parents=True, exist_ok=True)
    out = []
    for i in range(1, 25):
        p = dst / f"kodim{i:02d}.png"
        if not p.exists():
            try:
                with urllib.request.urlopen(KODAK_URL.format(i), timeout=30) as r:
                    p.write_bytes(r.read())
            except Exception as e:
                if allow_synthetic_only:
                    print(f"[data] Kodak download failed ({e}); explicit synthetic-only mode")
                    return []
                raise RuntimeError(f"Kodak image {i} unavailable; rerun with --allow-synthetic-only to opt in") from e
        out.append(p)
    return out


def _to_frame(img: Image.Image) -> Image.Image:
    if img.height > img.width:
        img = img.rotate(90, expand=True)
    return img.convert("RGB").resize((W, H), Image.LANCZOS)


def _synthetic(rng) -> dict[str, np.ndarray]:
    imgs = {}
    # (1) lattice sweep of the RGB cube: worst case, every region of the LUT is hit
    s = 92
    v = np.round(np.linspace(0, 255, s)).astype(np.uint8)
    cube = np.stack(np.meshgrid(v, v, v, indexing="ij"), -1).reshape(-1, 3)
    flat = np.full((W * H, 3), 128, np.uint8)
    flat[: len(cube)] = cube
    imgs["syn_cube"] = flat.reshape(H, W, 3)
    # (2) hue x lightness sweep with smooth saturation ramp
    hh, ll = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    sat = np.clip(1.2 - ll * 0.4, 0, 1)
    rgb = np.clip(np.abs(((hh[..., None] * 6 + np.array([0, 4, 2])) % 6) - 3) - 1, 0, 1)
    img = ll[..., None] * (1 - sat[..., None] + sat[..., None] * rgb)
    imgs["syn_huesweep"] = np.round(img * 255).astype(np.uint8)
    # (3) uniform noise (no spatial structure, every colour equally likely)
    imgs["syn_noise"] = rng.integers(0, 256, (H, W, 3), dtype=np.uint8)
    # (4) skin / sky / foliage gradients with sensor-like noise
    t = np.linspace(0, 1, W)[None, :, None]
    bands = [np.array([224, 172, 140]), np.array([110, 160, 220]), np.array([70, 120, 50])]
    rows = []
    for c in bands:
        base = c * (0.35 + 0.75 * t)
        rows.append(np.repeat(base, H // 3, axis=0))
    img = np.concatenate(rows, 0)[:H] + rng.normal(0, 4, (H, W, 3))
    imgs["syn_memory_colors"] = np.clip(img, 0, 255).astype(np.uint8)
    # (5) near-neutral greys + dark/bright extremes (where clipping kinks live)
    g = np.linspace(0, 255, W)[None, :, None] + rng.normal(0, 3, (H, 1, 3))
    imgs["syn_neutrals"] = np.clip(np.broadcast_to(g, (H, W, 3)), 0, 255).astype(np.uint8)
    return imgs


def build_images(seed: int = 0, allow_synthetic_only: bool = False) -> dict:
    rng = np.random.default_rng(seed)
    raw = _fetch_kodak(DATA / "raw" / "kodak", allow_synthetic_only)
    if len(raw) != 24 and not allow_synthetic_only:
        raise RuntimeError(f"expected 24 Kodak images, found {len(raw)}")
    eval_dir, bench_dir = DATA / "images" / "eval", DATA / "images" / "bench"
    eval_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)
    photos = []
    for p in raw:
        frame = _to_frame(Image.open(p))
        frame.save(eval_dir / p.name, compress_level=1)
        photos.append(np.asarray(frame))
    for name, arr in _synthetic(rng).items():
        Image.fromarray(arr).save(eval_dir / f"{name}.png", compress_level=1)
    # bench: 100 photo-like frames (crops / flips / exposure changes of the photos)
    srcs = photos if photos else [np.asarray(Image.open(p)) for p in sorted(eval_dir.glob("syn_*.png"))]
    for i in range(100):
        a = srcs[i % len(srcs)]
        if i >= len(srcs):
            scale = rng.uniform(0.55, 0.95)
            ch, cw = int(H * scale), int(W * scale)
            y0, x0 = rng.integers(0, H - ch + 1), rng.integers(0, W - cw + 1)
            im = Image.fromarray(a[y0:y0 + ch, x0:x0 + cw]).resize((W, H), Image.LANCZOS)
            arr = np.asarray(im).astype(np.float32)
            arr = arr * rng.uniform(0.75, 1.25) + rng.normal(0, rng.uniform(0, 3), arr.shape)
            if rng.random() < 0.5:
                arr = arr[:, ::-1]
            a = np.clip(arr, 0, 255).astype(np.uint8)
        Image.fromarray(a).save(bench_dir / f"bench_{i:03d}.png", compress_level=1)
    lists = {}
    for name, d in [("eval", eval_dir), ("bench", bench_dir)]:
        files = sorted(p.relative_to(ROOT).as_posix() for p in d.glob("*.png"))
        (DATA / f"{name}.txt").write_text("\n".join(files) + "\n")
        lists[name] = len(files)
    manifest = {
        "seed": seed, "source_mode": "kodak+synthetic" if len(raw) == 24 else "synthetic-only",
        "width": W, "height": H, "lists": lists,
        "sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [*raw, *sorted(eval_dir.glob("*.png")), *sorted(bench_dir.glob("*.png")),
                             DATA / "eval.txt", DATA / "bench.txt"]},
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return lists


def verify_images(require_kodak: bool = True) -> dict:
    manifest = json.loads((DATA / "manifest.json").read_text())
    if require_kodak and manifest["source_mode"] != "kodak+synthetic":
        raise ValueError("dataset is synthetic-only; full Kodak set required")
    for rel, expected in manifest["sha256"].items():
        p = ROOT / rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError(f"missing or modified dataset file: {rel}")
    for name, expected in (("eval", 29), ("bench", 100)):
        paths = [ROOT / line for line in (DATA / f"{name}.txt").read_text().splitlines() if line]
        if len(paths) != expected and require_kodak:
            raise ValueError(f"{name}: expected {expected} images, found {len(paths)}")
        for p in paths:
            with Image.open(p) as im:
                if im.size != (W, H) or im.mode != "RGB":
                    raise ValueError(f"unexpected image format: {p}")
    return {"source_mode": manifest["source_mode"], "lists": manifest["lists"],
            "files_hashed": len(manifest["sha256"])}


def scenario_dir(sid: str) -> Path:
    return DATA / "scenarios" / sid


def build_scenario(sid: str, force: bool = False) -> dict:
    d = scenario_dir(sid)
    meta_p = d / "meta.json"
    if meta_p.exists() and not force:
        return json.loads(meta_p.read_text())
    d.mkdir(parents=True, exist_ok=True)
    name, seed = luts.parse_scenario(sid)
    stages = luts.scenario(name, seed)
    t0 = time.time()
    tables = []
    with np.errstate(all="ignore"):
        for k, st in enumerate(stages, 1):
            L = luts.build_lut(st)
            io.save_full(d / f"lut{k}.lut256", L)
            tables.append(L)
    comp = io.compose(tables)
    io.save_full(d / "composite.lut256", comp)
    meta = {
        "id": sid, "stages": json.loads(luts.describe(stages)),
        "sha256": {f"lut{k}": hashlib.sha256(t.tobytes()).hexdigest()[:16] for k, t in enumerate(tables, 1)},
        "build_s": round(time.time() - t0, 2),
    }
    meta_p.write_text(json.dumps(meta, indent=1))
    return meta
