"""Freeze problem 16 run evidence into an auditable, deterministic Typst report bundle."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
GENERATED = REPORT / "generated"
DATA = REPORT / "data"
RUNS = ROOT / "logs" / "runs"
SELECTION_ID = "52e23c0b"
PERF_SWEEP_ID = "37f9fba6"
PERF_REPEAT_ID = "20bb8ce1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_dir(run_id: str) -> Path:
    hits = list(RUNS.glob(f"*-{run_id}"))
    if len(hits) != 1:
        raise RuntimeError(f"expected one run directory for {run_id}, got {len(hits)}")
    return hits[0]


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def archive_exact(path: Path, files: list[Path]) -> None:
    """Save original bytes and relative paths with fixed tar/gzip metadata."""
    with path.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w") as tar:
            for src in sorted(files, key=lambda p: p.relative_to(ROOT).as_posix()):
                contents = src.read_bytes()
                info = tarfile.TarInfo(src.relative_to(ROOT).as_posix())
                info.size = len(contents)
                info.mode = 0o644
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(contents))


def fmt(x: object, digits: int = 3) -> str:
    return "—" if x is None else f"{float(x):.{digits}f}"


def build_plots(candidates: list[dict], perf_repeat: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    profiles = ["sample", "tetra", "tail", "errorgrid", "residual", "residual_tail", "trilinear", "composite"]
    sizes = [17, 25, 33]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    width = .24
    for j, m in enumerate(sizes):
        subset = {c["profile"]: c for c in candidates if c["m"] == m}
        vals = [subset[p]["accuracy"]["worst_image_metric"] for p in profiles]
        ax.bar(np.arange(len(profiles)) + (j - 1) * width, vals, width, label=f"m={m}")
    ax.axhline(2.0, color="#bb3943", linestyle="--", linewidth=1.5, label="local example limit 2.0")
    ax.set_xticks(np.arange(len(profiles)), profiles, rotation=27, ha="right")
    ax.set_ylabel("Worst image mean RGB distance")
    ax.set_title("isp-0: actual executable output, 29 evaluation images")
    ax.legend(ncols=4, fontsize=8)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(GENERATED / "current_accuracy.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4))
    for threads, color in [(4, "#2869a6"), (20, "#cf7456")]:
        rows = sorted((r for r in perf_repeat if r["threads"] == threads), key=lambda r: r["width"])
        ax.plot([r["width"] for r in rows], [r["set_ms_p50_rep"] for r in rows],
                marker="o", linewidth=2, label=f"{threads} threads", color=color)
    ax.set_xticks([8, 16])
    ax.set_xlabel("Zig vector lanes")
    ax.set_ylabel("100-image set median (ms)")
    ax.set_title("7 full-set repetitions; 4096-pixel blocks, dynamic scheduling")
    ax.grid(alpha=.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(GENERATED / "zig_width_repeat.png", dpi=180)
    plt.close(fig)


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    run_files = sorted(RUNS.glob("*/run.json"))
    if not run_files:
        raise RuntimeError("no independent run logs found")
    records = [json.loads(p.read_text()) for p in run_files]
    by_start = sorted(records, key=lambda r: r["start"])
    selection = json.loads((run_dir(SELECTION_ID) / "selection.json").read_text())
    candidates = selection["candidates"]
    if len(candidates) != 24:
        raise RuntimeError(f"expected 24 current candidates, found {len(candidates)}")
    sweep = json.loads((run_dir(PERF_SWEEP_ID) / "sweep.json").read_text())["rows"]
    repeat = json.loads((run_dir(PERF_REPEAT_ID) / "sweep.json").read_text())["rows"]
    route_data = json.loads((ROOT / "experiments" / "route_sweep.json").read_text())
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    log_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "logs", text=True).strip()

    candidate_rows = []
    image_rows = []
    hotspot_rows = []
    for c in candidates:
        a = c["accuracy"]
        b = c.get("bench", {})
        candidate_rows.append([c["m"], c["profile"], c["status"], c["mode"],
                               fmt(a["worst_image_metric"]), fmt(a["cube"]["mean"]),
                               fmt(a["cube"]["p99"]), fmt(a["cube"]["max"]),
                               fmt(b.get("set_ms_p50_rep")), fmt(b.get("set_ms_best_rep"))])
        for item in a["per_image"]:
            image_rows.append([c["m"], c["profile"], Path(item["image"]).name,
                               repr(item["mean"]), repr(item["rms"]), repr(item["p99"]),
                               repr(item["max"]), item["pass"]])
        for rank, spot in enumerate(a["cube"]["hotspots"], 1):
            hotspot_rows.append([c["m"], c["profile"], rank, *spot["rgb"], repr(spot["delta_e"])])
    write_csv(GENERATED / "candidate_results.csv",
              ["m", "路线", "本地门禁", "阶段模式", "最差图均值", "全色均值", "全色p99", "全色最大", "100图中位ms", "100图最佳ms"],
              candidate_rows)
    write_csv(DATA / "image_results.csv",
              ["m", "profile", "image", "mean", "rms", "p99", "max", "pass"], image_rows)
    write_csv(DATA / "cube_hotspots.csv",
              ["m", "profile", "rank", "R", "G", "B", "delta_e"], hotspot_rows)

    sweep_rows = [[r["threads"], r["width"], r["block_pixels"], r["schedule"],
                   fmt(r["set_ms_best_rep"])] for r in sweep]
    write_csv(GENERATED / "zig_sweep.csv", ["线程", "lane", "块", "调度", "100图最佳ms"], sweep_rows)
    write_csv(GENERATED / "zig_repeat.csv", ["线程", "lane", "100图最佳ms", "100图中位ms"],
              [[r["threads"], r["width"], fmt(r["set_ms_best_rep"]), fmt(r["set_ms_p50_rep"])] for r in repeat])

    scene_rows = []
    for scenario in sorted({r["scenario"] for r in route_data["lattice_routes"]}):
        for m in (17, 33):
            vals = {r["route"].split("_")[0]: r["mean_de"] for r in route_data["lattice_routes"]
                    if r["scenario"] == scenario and r["m"] == m}
            scene_rows.append([scenario, m, *[fmt(vals.get(k)) for k in ("R2", "R8", "R11", "R13")]])
    write_csv(GENERATED / "historic_scenarios.csv",
              ["场景", "m", "朴素R2", "整数LS R8", "残差R11", "复合R13"], scene_rows)

    history = subprocess.check_output(["git", "log", "--reverse", "--format=%h%x09%ad%x09%s", "--date=short"],
                                      cwd=ROOT, text=True).splitlines()
    write_csv(GENERATED / "git_history.csv", ["提交", "日期", "原始标题"],
              [line.split("\t", 2) for line in history])
    ledger_rows = []
    ledger_full = []
    for r in by_start:
        env = r.get("env", {})
        status = "OK" if r["status"] == "ok" else "FAIL"
        sha12 = env.get("commit", "")[:12]
        ledger_rows.append([r["start"][:16].replace("T", " "), r["id"], r["name"], status,
                            sha12, fmt(r["seconds"], 1)])
        ledger_full.append([r["start"], r["id"], r["name"], r["status"], r["seconds"],
                            env.get("commit", ""), env.get("branch", ""), env.get("dirty", ""),
                            r.get("dir", ""), json.dumps(r.get("params", {}), ensure_ascii=False, sort_keys=True)])
    write_csv(GENERATED / "ledger_print.csv", ["UTC 时间", "ID", "类型", "状态", "代码", "秒"], ledger_rows)
    write_csv(DATA / "ledger.csv", ["start", "id", "name", "status", "seconds", "code_commit", "branch", "dirty", "dir", "params_json"], ledger_full)

    all_run_files = sorted(p for p in RUNS.glob("*/*") if p.is_file())
    archive_exact(DATA / "run_records_exact.tar.gz", all_run_files)
    manifest_files = sorted((ROOT / "data").glob("manifest.json")) + sorted((ROOT / "data" / "scenarios").glob("*/meta.json"))
    if not manifest_files:
        raise RuntimeError("dataset manifests missing")
    archive_exact(DATA / "manifests_exact.tar.gz", manifest_files)
    archive_exact(DATA / "experiments_exact.tar.gz", sorted((ROOT / "experiments").glob("*.json")))

    build_plots(candidates, repeat)
    archive_names = ["run_records_exact.tar.gz", "manifests_exact.tar.gz", "experiments_exact.tar.gz",
                     "ledger.csv", "image_results.csv", "cube_hotspots.csv"]
    hashes = {name: sha(DATA / name) for name in archive_names}
    meta = {
        "source_git_commit": source_commit,
        "logs_git_commit": log_commit,
        "run_count": len(records),
        "failed_run_count": sum(r["status"] != "ok" for r in records),
        "candidate_count": len(candidates),
        "image_row_count": len(image_rows),
        "hotspot_row_count": len(hotspot_rows),
        "sweep_count": len(sweep),
        "historic_lattice_count": len(route_data["lattice_routes"]),
        "historic_non_lattice_count": len(route_data["non_lattice_routes"]),
        "historic_bench_count": len(route_data["cpp_benchmarks"]),
        "first_run_id": by_start[0]["id"],
        "last_run_id": by_start[-1]["id"],
        "selected_run_id": SELECTION_ID,
        "selection_winner": selection["winner"]["profile"],
        "selection_winner_m": selection["winner"]["m"],
        "selection_winner_p50_ms": selection["winner"]["bench"]["set_ms_p50_rep"],
        "artifact_sha256": hashes,
        "route_sweep_sha256": sha(ROOT / "experiments" / "route_sweep.json"),
    }
    (GENERATED / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    index = ["# 报告数据索引", "", f"由 `scripts/build_typst_data.py` 从 Git `{source_commit}` 和独立日志 `{log_commit}` 生成。",
             f"包含 {len(records)} 次运行、{len(candidates)} 个当前候选、{len(image_rows)} 条逐图结果；原始日志按字节归档，生成器不修改 `logs/`。",
             "", "| 文件 | SHA-256 |", "| --- | --- |"]
    index += [f"| `{name}` | `{digest}` |" for name, digest in hashes.items()]
    index += ["", "原始图像和完整 LUT 约 1.8 GiB，保留在被 Git 忽略的 `data/`；本归档只保存清单和实验记录。",
              "`run_records_exact.tar.gz` 包含运行目录中的 JSON、stdout、测试日志和代码差异；路径及字节不变。", ""]
    (DATA / "DATA_INDEX.md").write_text("\n".join(index))
    print(json.dumps({"runs": len(records), "candidates": len(candidates), "image_rows": len(image_rows),
                      "source_commit": source_commit, "archives": hashes}, indent=2))


if __name__ == "__main__":
    main()
