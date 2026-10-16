"""可断点续跑的本地LUT×图片×算法适配度研究，结果不自动上传。"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import contextlib
from datetime import datetime, timezone
import hashlib
import io as textio
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import threading
import time
import traceback

import numpy as np
import numba
from PIL import Image
import psutil
from llvmlite import binding as llvm

from . import fit, interp, io, source_lut, study_kernels as kernels
from . import study_provenance

ROOT = Path(__file__).resolve().parents[2]
KINDS = {"tetra": 0, "tri": 1, "nearest": 2, "hold": 3, "prism": 4}
PROFILES = {
    **{f"sample_{k}": ("sample", "uniform", k) for k in KINDS},
    "subpixel_tri": ("sample_interp", "uniform", "tri"),
    "subpixel_tetra": ("sample_interp", "uniform", "tetra"),
    "box_tri": ("box", "uniform", "tri"),
    "box_tetra": ("box", "uniform", "tetra"),
    "ls_tri_tri": ("ls_tri", "uniform", "tri"),
    "ls_tri_tetra_mismatch": ("ls_tri", "uniform", "tetra"),
    "ls_tetra": ("ls_tetra", "uniform", "tetra"),
    "ls_tetra_int": ("ls_tetra_int", "uniform", "tetra"),
    "jitter_tetra": ("ls_tetra_jitter", "uniform", "tetra"),
    "curvature_int": ("ls_tetra_int", "curvature", "tetra"),
    "dp_jitter": ("ls_tetra_jitter", "dp", "tetra"),
    "errorgrid_int": ("ls_tetra_int", "error", "tetra"),
    "dp_boundary": ("ls_tetra_boundary", "dp", "tetra"),
    "dp_supported": ("ls_tetra_supported", "dp", "tetra"),
    "tail_tetra": ("tail_tetra_int", "uniform", "tetra"),
}
SLOW_PROFILES = {"irls_tetra": ("irls_tetra", "uniform", "tetra"),
                 "guarded_tetra": ("ls_tetra_guarded", "uniform", "tetra")}
METRICS = ["mean", "rms", "p99", "max", "fraction_ge_1", "fraction_ge_2", "fraction_ge_3", "fraction_ge_5"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + f".{os.getpid()}.partial")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str) + "\n", encoding="utf-8")
    temp.replace(path)


def model_args(model):
    idx, frac = model.tables()
    return (np.ascontiguousarray(model.nodes.reshape(-1, 3), dtype=np.float64),
            idx.astype(np.int32), frac.astype(np.float64) / io.ONE, model.m)


def quality(summary):
    return {"mean": float(summary[:, 0].mean()), "rms": float(np.sqrt(np.mean(summary[:, 1] ** 2))),
            "worst_image_mean": float(summary[:, 0].max()), "worst_image_p99": float(summary[:, 2].max()),
            "max": float(summary[:, 3].max()), "fraction_ge_2": float(summary[:, 5].mean())}


class PeakRSS:
    """采样整个宿主进程RSS；不将其解释为模型独占内存。"""
    def __enter__(self):
        self.stop = threading.Event()
        self.peak = psutil.Process().memory_info().rss
        def monitor():
            while not self.stop.wait(.05):
                self.peak = max(self.peak, psutil.Process().memory_info().rss)
        self.thread = threading.Thread(target=monitor, daemon=True)
        self.thread.start()
        return self
    def __exit__(self, *_):
        self.peak = max(self.peak, psutil.Process().memory_info().rss)
        self.stop.set()
        self.thread.join()


def environment(args):
    files = [ROOT / "python/lutlab" / name for name in
             ("compatibility.py", "source_lut.py", "study_kernels.py", "fit.py", "interp.py", "io.py", "curve.py", "study_provenance.py")]
    fingerprint = {str(p.relative_to(ROOT)): digest(p) for p in files}
    numpy_config = textio.StringIO()
    with contextlib.redirect_stdout(numpy_config):
        np.__config__.show()
    execution_environment = study_provenance.environment_fingerprint()
    execution_environment.update(numpy_build=numpy_config.getvalue(),
        llvm_cpu_name=llvm.get_host_cpu_name(), llvm_cpu_features=llvm.get_host_cpu_features().flatten(),
        numba_threads=numba.get_num_threads(), numba_threading_layer=numba.threading_layer())
    identity = {"schema": 2, "environment": execution_environment,
                "source_sha256": fingerprint, "lut_manifest": digest(ROOT / "assets/LUT/manifest.json"),
                "image_manifest": digest(ROOT / "assets/photos/manifest.json"), "sizes": args.sizes,
                "screen_pixels_per_image": args.screen_pixels, "threads": args.threads,
                "reps": args.reps, "extended": args.extended, "profiles": PROFILES}
    return {"identity": identity, "identity_sha256": study_provenance.identity_digest(identity),
            "created_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
            "platform": platform.platform(), "processor": platform.processor(),
            "logical_cpu_count": psutil.cpu_count(), "physical_cpu_count": psutil.cpu_count(logical=False),
            "ram_bytes": psutil.virtual_memory().total, "numba": numba.__version__, "numpy": np.__version__,
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "backend": "Numba LLVM CPU，固定线程数；与现有C++/CUDA历史时间不可直接比较",
            "timing_scope": "解码和源烘焙/拟合独立计时；图像映射包含输出分配，不含解码、编译、质量统计；输入已预加载",
            "gate": "无官方Threshold；只报告RGB欧氏mean/RMS/p99/max及阈值扫描，不宣布官方通过",
            "source_reference": "按素材原网格三线性解释，再clip/round为完整RGB8黄金表；未知摄影色彩域保持未知",
            "native_build_status": "本研究入口不自动执行原生门禁；以对应阶段实际记录为准",
            "deferred": ["C++/CUDA部署性能", "R25/R26原生全域库", "MLP/SIREN", "高阶样条", "棱锥插值"]}


def run(args):
    numba.set_num_threads(args.threads)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    meta = environment(args)
    previous = out / "run.json"
    study_provenance.claim_run(previous, meta)
    image_manifest = json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))
    image_rows = image_manifest["images"]
    images = []
    for row in image_rows:
        path = ROOT / row["evaluation"]["path"]
        if digest(path) != row["evaluation"]["sha256"]:
            raise ValueError(f"图片哈希变化：{path}")
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise ValueError("图片不满足RGB8尺寸要求")
            images.append(np.asarray(image).reshape(-1, 3))
    images = np.stack(images)
    positions = np.random.default_rng(20261016).choice(images.shape[1], args.screen_pixels, replace=False)
    screening = np.ascontiguousarray(images[:, positions])
    entries = json.loads((ROOT / "assets/LUT/manifest.json").read_text(encoding="utf-8"))["assets"]
    extended_ids = set()
    seen = set()
    for entry in entries:
        if entry["source_id"] not in seen:
            extended_ids.add(entry["sha256"][:12])
            seen.add(entry["source_id"])
    if args.limit:
        entries = entries[:args.limit]
    entries = entries[args.shard::args.shards]
    # JIT预热单独完成，不放入任何性能成绩。
    dummy = io.SparseLut(io.uniform_grid(17), np.zeros((17, 17, 17, 3), np.uint8))
    da = model_args(dummy)
    kernels.map_pixels(screening.reshape(-1, 3)[:32], *da, 0)
    kernels.image_metrics(screening[:, :1], np.zeros((256 ** 3, 3), np.uint8), *da, 0)
    kernels.expand_cube(*da, 1)
    flat_images = images.reshape(-1, 3)
    source_seen = set()
    for index, entry in enumerate(entries):
        identifier = entry["sha256"][:12]
        folder = out / "luts" / identifier
        folder.mkdir(parents=True, exist_ok=True)
        result_path = folder / "result.json"
        existing = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
        if existing and (existing.get("complete") or (args.phase == "screen" and existing.get("screen_complete"))):
            source_seen.add(entry["source_id"])
            print(f"[{index+1}/{len(entries)}] 复用 {identifier}", flush=True)
            continue
        report = existing if existing and existing.get("screen_complete") else {"lut": entry, "run_identity": meta["identity_sha256"], "screen": [], "full": [],
                  "complete": False, "status": "running"}
        write_json(result_path, report)
        source_path = ROOT / entry["path"]
        if digest(source_path) != entry["sha256"]:
            raise ValueError("源LUT哈希变化")
        started = time.perf_counter()
        cache = out / "references" / f"{identifier}.npy"
        cache_meta = cache.with_suffix(".json")
        reference_id = {"source": entry["sha256"], "adapter": digest(Path(source_lut.__file__)),
                        "kernels": digest(Path(kernels.__file__))}
        if cache.exists() and cache_meta.exists() and json.loads(cache_meta.read_text(encoding="utf-8"))["identity"] == reference_id:
            table = np.load(cache, mmap_mode="r")
            policy = json.loads(cache_meta.read_text(encoding="utf-8"))["policy"]
        else:
            table, policy = source_lut.bake_source(source_path, entry)
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, table)
            write_json(cache_meta, {"identity": reference_id, "policy": policy, "sha256": digest(cache)})
        report.update(source_prepare_s=time.perf_counter()-started, reference_policy=policy,
                      reference_sha256=digest(cache))
        truth = np.ascontiguousarray(table.reshape(-1, 3))
        profiles = dict(PROFILES)
        if args.extended and identifier in extended_ids:
            profiles.update(SLOW_PROFILES)
        if report.get("screen_complete"):
            profiles = {}
        source_seen.add(entry["source_id"])
        fitted, grids = {}, {}
        with PeakRSS() as memory:
            for m in args.sizes:
                for profile, (method, grid_mode, kernel) in profiles.items():
                    row = {"profile": profile, "m": m, "method": method, "grid": grid_mode, "kernel": kernel,
                           "scope": "screen_sample", "pixels_per_image": args.screen_pixels}
                    try:
                        key = (method, grid_mode, m)
                        if key not in fitted:
                            fit_started = time.perf_counter()
                            grid_key = (grid_mode, m)
                            if grid_key not in grids:
                                grids[grid_key] = (fit.adaptive_grid(table, m) if grid_mode == "curvature" else
                                    fit.adaptive_error_grid(table, m) if grid_mode == "error" else
                                    fit.adaptive_dp_grid(table, m) if grid_mode == "dp" else io.uniform_grid(m))
                            grid = grids[grid_key]
                            nodes, grid, diagnostics = fit.fit(table, m, method, grid=grid)
                            model = io.SparseLut(grid, nodes)
                            path = folder / f"{method}-{grid_mode}-m{m}.slut"
                            io.save_sparse(path, model)
                            fitted[key] = (model, path, time.perf_counter()-fit_started, diagnostics)
                        model, path, fit_s, diagnostics = fitted[key]
                        arguments = model_args(model)
                        summary = kernels.image_metrics(screening, truth, *arguments, KINDS[kernel])
                        # 只对相同采样点测筛选吞吐，不外推为整张图片耗时。
                        timings = []
                        probe = screening.reshape(-1, 3)
                        for _ in range(3):
                            t0 = time.perf_counter()
                            output = kernels.map_pixels(probe, *arguments, KINDS[kernel])
                            timings.append((time.perf_counter()-t0)*1000)
                        row.update(status="ok", quality=quality(summary), fit_s=fit_s,
                                   model=str(path.relative_to(out)), model_sha256=digest(path),
                                   node_bytes=model.nodes.nbytes, serialized_bytes=path.stat().st_size,
                                   screen_probe_ms=timings, diagnostics=diagnostics)
                    except Exception as error:
                        row.update(status="failed", error=repr(error), traceback=traceback.format_exc())
                    report["screen"].append(row)
                    write_json(result_path, report)
            report["host_process_sampled_peak_rss_bytes"] = memory.peak
        report.update(screen_complete=True, status="screened")
        write_json(result_path, report)
        valid = [row for row in report["screen"] if row["status"] == "ok"]
        if args.phase == "screen":
            print(f"[{index+1}/{len(entries)}] {identifier} 已筛选{len(report['screen'])}项，成功{len(valid)}项", flush=True)
            continue
        if not valid:
            report.update(status="failed", complete=True)
            write_json(result_path, report)
            continue
        picks = [min(valid, key=lambda row: row["quality"]["mean"]),
                 min(valid, key=lambda row: row["quality"]["max"])]
        baseline = next((row for row in valid if row["profile"] == "sample_tetra" and row["m"] == max(args.sizes)), None)
        if baseline:
            picks.append(baseline)
        picked = {(row["profile"], row["m"]) for row in report["full"]}
        for row in picks:
            key = (row["profile"], row["m"])
            if key in picked:
                continue
            picked.add(key)
            full = {k: row[k] for k in ("profile", "m", "method", "grid", "kernel", "model", "model_sha256", "fit_s", "node_bytes", "serialized_bytes")}
            model = io.load_sparse(out / row["model"])
            arguments = model_args(model)
            with PeakRSS() as memory:
                summary = kernels.image_metrics(images, truth, *arguments, KINDS[row["kernel"]])
                per_image = [{"image": image_rows[j]["id"], **{name: float(summary[j, k]) for k, name in enumerate(METRICS)}} for j in range(len(images))]
                # 实际映射输出逐图统计，与独立质量内核对照后再计时。
                check = kernels.map_pixels(images[0], *arguments, KINDS[row["kernel"]])
                original = images[0].astype(np.int32)
                expected = truth[(original[:, 0] * 256 + original[:, 1]) * 256 + original[:, 2]]
                distance = np.linalg.norm(check.astype(np.int32)-expected.astype(np.int32), axis=1)
                if abs(distance.mean()-summary[0, 0]) > 1e-10 or abs(np.percentile(distance, 99)-summary[0, 2]) > 1e-10:
                    raise RuntimeError("独立逐像素误差对照失败")
                kernels.map_pixels(flat_images[:1024], *arguments, KINDS[row["kernel"]])
                times = []
                for _ in range(args.reps):
                    started = time.perf_counter()
                    mapped = kernels.map_pixels(flat_images, *arguments, KINDS[row["kernel"]])
                    times.append((time.perf_counter()-started)*1000)
                full.update(scope="full_100_images", quality=quality(summary), per_image=per_image,
                            set_ms=times, median_ms_per_image=statistics.median(times)/len(images),
                            host_process_sampled_peak_rss_bytes=memory.peak,
                            output_sha256=hashlib.sha256(mapped.tobytes()).hexdigest(),
                            status="ok", image_count=len(images), pixels_per_image=images.shape[1])
            report["full"].append(full)
            write_json(result_path, report)
        report.update(complete=True, status="ok", finished_utc=datetime.now(timezone.utc).isoformat())
        write_json(result_path, report)
        print(f"[{index+1}/{len(entries)}] {identifier} 完成{len(valid)}项筛选、{len(report['full'])}项100图验证；最佳mean={min(r['quality']['mean'] for r in report['full']):.5f}", flush=True)
        summarize(out)
    if args.shards == 1:
        summarize(out)


def summarize(out):
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((out / "luts").glob("*/result.json"))]
    rows, per_image = [], []
    for report in reports:
        for stage in ("screen", "full"):
            for record in report[stage]:
                row = {"lut": report["lut"]["path"], "source": report["lut"]["source_id"], "stage": stage,
                       **{k: record.get(k) for k in ("profile", "m", "method", "grid", "kernel", "status", "fit_s", "node_bytes", "serialized_bytes", "median_ms_per_image", "error")},
                       **record.get("quality", {})}
                rows.append(row)
                if stage == "full":
                    for image in record.get("per_image", []):
                        per_image.append({"lut": row["lut"], "profile": row["profile"], "m": row["m"], **image})
    for name, table in (("compatibility.csv", rows), ("per-image.csv", per_image)):
        if table:
            fields = list(dict.fromkeys(key for row in table for key in row))
            with (out / name).open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.DictWriter(stream, fields)
                writer.writeheader()
                writer.writerows(table)
    write_json(out / "progress.json", {"luts_finished": sum(r.get("complete", False) for r in reports),
               "screen_rows": sum(len(r["screen"]) for r in reports), "full_rows": sum(len(r["full"]) for r in reports),
               "failed_rows": sum(row["status"] != "ok" for row in rows), "per_image_rows": len(per_image)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/local-lut-study/20261016")
    parser.add_argument("--sizes", type=int, nargs="+", default=[17, 33])
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--screen-pixels", type=int, default=4096)
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--extended", action="store_true")
    parser.add_argument("--phase", choices=("all", "screen", "full"), default="all")
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if any(not 17 <= m <= 33 for m in args.sizes) or args.reps < 1 or not 1 <= args.screen_pixels <= 1024*768 or not 0 <= args.shard < args.shards:
        raise ValueError("尺寸、采样数量或重复次数非法")
    if args.summarize:
        summarize(args.output)
    else:
        run(args)


if __name__ == "__main__":
    main()
