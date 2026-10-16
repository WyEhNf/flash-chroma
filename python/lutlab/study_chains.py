"""复用单级研究模型，显式测量四级整数映射的数值级联。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import time

import numba
from numba import njit, prange
import numpy as np
from PIL import Image

from . import io
from .study_kernels import pixel
from .compatibility import ROOT, KINDS, PeakRSS, digest, model_args, write_json


@njit(cache=True, parallel=True)
def map_chain(rgb, nodes, indices, fractions, m, kind):
    output = np.empty_like(rgb)
    for i in prange(len(rgb)):
        r, g, b = int(rgb[i, 0]), int(rgb[i, 1]), int(rgb[i, 2])
        for stage in range(4):
            value = pixel(nodes[stage], indices[stage], fractions[stage], m, r, g, b, kind)
            r = min(255, max(0, int(np.floor(value[0] + .5))))
            g = min(255, max(0, int(np.floor(value[1] + .5))))
            b = min(255, max(0, int(np.floor(value[2] + .5))))
        output[i, 0], output[i, 1], output[i, 2] = r, g, b
    return output


@njit(cache=True, parallel=True)
def compare_images(prediction, truth):
    output = np.empty((len(prediction), 4), np.float64)
    for image in prange(len(prediction)):
        hist = np.zeros(195076, np.int64)
        for p in range(prediction.shape[1]):
            d2 = 0
            for c in range(3):
                delta = int(prediction[image, p, c]) - int(truth[image, p, c])
                d2 += delta * delta
            hist[d2] += 1
        n = prediction.shape[1]
        rank = .99 * (n - 1)
        lo, hi = int(np.floor(rank)), int(np.ceil(rank))
        cumulative, total, squared, low, high, maximum = 0, 0., 0., 0., 0., 0.
        for d2 in range(len(hist)):
            count = hist[d2]
            if count:
                value = np.sqrt(d2)
                if cumulative <= lo < cumulative + count:
                    low = value
                if cumulative <= hi < cumulative + count:
                    high = value
                cumulative += count
                total += count * value
                squared += count * d2
                maximum = value
        output[image, 0] = total / n
        output[image, 1] = np.sqrt(squared / n)
        output[image, 2] = low + (rank-lo)*(high-low)
        output[image, 3] = maximum
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "artifacts/local-lut-study/20261016")
    parser.add_argument("--reps", type=int, default=3)
    args = parser.parse_args()
    numba.set_num_threads(4)
    out = args.input.resolve()
    reports = [json.loads(p.read_text(encoding="utf-8")) for p in (out / "luts").glob("*/result.json")]
    image_rows = json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]
    frames = []
    for row in image_rows:
        path = ROOT / row["evaluation"]["path"]
        if digest(path) != row["evaluation"]["sha256"]:
            raise ValueError("图片哈希发生变化")
        with Image.open(path) as image:
            frames.append(np.asarray(image).reshape(-1, 3))
    images = np.stack(frames)
    # 只构造创意LUT的明确数值链；源色彩域未声明，不能称为推荐摄影管线。
    creative = sorted([r for r in reports if r["lut"]["source_id"] == "stripedpurple"], key=lambda r: r["lut"]["path"])
    recipes = [creative[start:start+4] for start in (0, 11, 30)]
    profiles = ["sample_tri", "sample_tetra", "subpixel_tetra", "ls_tri_tri", "ls_tetra_int",
                "jitter_tetra", "curvature_int", "dp_jitter", "dp_supported", "tail_tetra"]
    results = {"semantics": "四张不同完整LUT独立拟合，逐级RGB8取整；数值级联压力实验，不证明源色彩空间匹配",
               "backend": "Numba LLVM CPU四级融合、4线程", "reps": args.reps,
               "source_code_sha256": digest(Path(__file__)), "parent_run": digest(out / "run.json"), "rows": []}
    for recipe_index, recipe in enumerate(recipes):
        if len(recipe) != 4:
            continue
        truth = images.reshape(-1, 3).copy()
        refs = []
        for report in recipe:
            identifier = report["lut"]["sha256"][:12]
            table = np.load(out / "references" / f"{identifier}.npy", mmap_mode="r")
            refs.append(identifier)
            truth = table[truth[:, 0], truth[:, 1], truth[:, 2]]
        truth = truth.reshape(images.shape)
        for size in (17, 33):
            for profile in profiles:
                records = [next((r for r in report["screen"] if r["profile"] == profile and r["m"] == size and r["status"] == "ok"), None) for report in recipe]
                row = {"recipe": recipe_index+1, "luts": [r["lut"]["path"] for r in recipe], "profile": profile, "m": size}
                if any(r is None for r in records):
                    row.update(status="skipped", reason="某级模型未成功生成")
                    results["rows"].append(row)
                    continue
                models = []
                for record in records:
                    path = out / record["model"]
                    if digest(path) != record["model_sha256"]:
                        raise ValueError("模型哈希发生变化")
                    models.append(io.load_sparse(path))
                parameters = [model_args(m) for m in models]
                nodes = np.stack([p[0] for p in parameters])
                indices = np.stack([p[1] for p in parameters])
                fractions = np.stack([p[2] for p in parameters])
                kind = KINDS[records[0]["kernel"]]
                flat = images.reshape(-1, 3)
                mapped_probe = map_chain(flat[:16384], nodes, indices, fractions, size, kind)
                oracle = flat[:16384].copy()
                from . import study_kernels
                for parameters_stage in parameters:
                    oracle = study_kernels.map_pixels(oracle, *parameters_stage, kind)
                if not np.array_equal(mapped_probe, oracle):
                    raise RuntimeError("四级融合与逐级独立执行不一致")
                with PeakRSS() as memory:
                    times = []
                    for _ in range(args.reps):
                        started = time.perf_counter()
                        mapped = map_chain(flat, nodes, indices, fractions, size, kind)
                        times.append((time.perf_counter()-started)*1000)
                    summary = compare_images(mapped.reshape(images.shape), truth)
                    row.update(status="ok", set_ms=times, median_ms_per_image=statistics.median(times)/len(images),
                               mean=float(summary[:, 0].mean()), worst_image_mean=float(summary[:, 0].max()),
                               worst_image_p99=float(summary[:, 2].max()), max=float(summary[:, 3].max()),
                               node_bytes=sum(m.nodes.nbytes for m in models),
                               host_process_sampled_peak_rss_bytes=memory.peak,
                               output_sha256=hashlib.sha256(mapped.tobytes()).hexdigest(),
                               per_image=[{"image": image_rows[i]["id"], **{k: float(summary[i,j]) for j,k in enumerate(("mean","rms","p99","max"))}} for i in range(len(images))])
                results["rows"].append(row)
                write_json(out / "chains.json", results)
                print(f"四级链{recipe_index+1} {profile}/m{size}: mean={row['mean']:.5f}, {row['median_ms_per_image']:.3f}ms/图", flush=True)
    write_json(out / "chains.json", results)


if __name__ == "__main__":
    main()
