"""汇总本地研究结果，输出中文报告、逐图CSV和科学绘图。"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import html
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab.compatibility import summarize

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args()
out = args.input.resolve()
summarize(out)
reports = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((out / "luts").glob("*/result.json"))]
meta = json.loads((out / "run.json").read_text(encoding="utf-8"))
progress = json.loads((out / "progress.json").read_text(encoding="utf-8"))
full = [(r, v) for r in reports for v in r["full"]]
screen = [(r, v) for r in reports for v in r["screen"]]
failures = [(r, v) for r, v in screen if v["status"] != "ok"]
chains = json.loads((out / "chains.json").read_text(encoding="utf-8")) if (out / "chains.json").exists() else {"rows": []}
cube = json.loads((out / "cube-finalists.json").read_text(encoding="utf-8")) if (out / "cube-finalists.json").exists() else {"rows": []}
cube_map = {(r["lut"],r["profile"],r["m"]):r for r in cube["rows"]}
if cube["rows"]:
    with (out / "cube-finalists.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, list(cube["rows"][0]))
        writer.writeheader()
        writer.writerows(cube["rows"])
with (out / "chains.csv").open("w", newline="", encoding="utf-8-sig") as stream:
    fields = ["recipe", "profile", "m", "status", "mean", "worst_image_mean", "worst_image_p99", "max", "median_ms_per_image", "node_bytes"]
    writer = csv.DictWriter(stream, fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(chains["rows"])
best_rows = []
for report in reports:
    valid = [r for r in report["full"] if r["status"] == "ok"]
    if valid:
        best = min(valid, key=lambda v: v["quality"]["mean"])
        baseline = next((v for v in valid if v["profile"] == "sample_tetra"), None)
        best_rows.append({"lut": report["lut"]["path"], "source": report["lut"]["source_id"],
            "profile": best["profile"], "m": best["m"], **best["quality"],
            "median_ms_per_image": best["median_ms_per_image"],
            "baseline_mean": baseline["quality"]["mean"] if baseline else None,
            "improvement_percent": 100*(1-best["quality"]["mean"]/baseline["quality"]["mean"]) if baseline and baseline["quality"]["mean"] else None})
        color = cube_map.get((report["lut"]["path"],best["profile"],best["m"]))
        best_rows[-1].update(cube_mean=color["mean"] if color else None,
                             cube_p99=color["p99"] if color else None, cube_max=color["max"] if color else None)
if best_rows:
    with (out / "best-per-lut.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, list(best_rows[0]))
        writer.writeheader()
        writer.writerows(best_rows)
algorithm_groups = defaultdict(list)
for report, row in screen:
    if row["status"] == "ok":
        algorithm_groups[(row["profile"], row["m"])].append(row["quality"]["mean"])
lines = ["# 本地LUT与图片适配度研究", "", "所有结果留在本地，未上传GitHub。", "",
    f"完成{progress['luts_finished']}个LUT，{progress['screen_rows']}条筛选配置，{progress['full_rows']}条完整100图复核，{progress['per_image_rows']}条逐图记录；失败配置{progress['failed_rows']}条。", "",
    "## 评测口径", "",
    "- 输入：68个外部LUT、100张1024×768 RGB8实际照片。源文件、图片、参考表及模型都有SHA-256。",
    "- 每个LUT在17³/33³两档上测试20种配置；五个来源各额外测试一张的IRLS及guarded变体。",
    "- 筛选：每张图固定4096个不放回随机像素，共409600像素/配置。筛选数据也参与候选选择，不能称盲测。",
    "- 每个LUT按筛选mean、筛选max及33³直接采样基线择优，去重后在全部100图的全部像素上复核；其他配置只有抽样结果。",
    "- 精度为RGB欧氏距离，不是Lab ΔE。p99按每图像素精确统计；汇总报告最差逐图p99，不将其称为全局p99。",
    "- NumPy/BLAS线程限制1；映射为Numba LLVM CPU四线程，预热后整组100图重复3次。包含输出分配，不含解码、JIT编译、拟合、参考烘焙和误差统计。",
    "- 筛选分三个进程并行，screen_probe_ms会受到资源竞争，只作流程诊断；正式全图测速在筛选全部完成后串行运行，不据筛选耗时宣布算法性能排名。",
    "- fit_s含实际求解，网格和相同节点模型在同一LUT内复用，不是每配置独立冷启动总耗时。宿主RSS是整个进程采样峰值，不是模型独占内存。",
    "- 单级结果不是赛题四级成绩。四级链另见chains.csv；每级整数舍入，链为明确列出的数值压力组合，不宣称未知源色彩空间匹配。",
    "- 本机未完成CMake/C++原有完整门禁：CMake未找到，CodeBlocks g++出现DLL启动错误。13项新测试检查源格式、Q16一致性、棱柱独立公式、分位数及四级融合；不替代原有C++/CUDA跨后端验收。",
    "- 参考表按源网格三线性解释并clip/round为256³ RGB8；3DL使用OCIO式位深推断与近恒等shaper政策。外部素材原本稀疏，参考插值结构可能偏向三线性候选。",
    "- 官方Threshold和聚合口径未知；文件中的ge_1/ge_2/ge_3/ge_5仅作阈值扫描，不宣布官方通过。",
    "- Windows文件占用导致两次检查点写入中断，保留失败日志后用有限IO重试恢复；重试只改变写入行为，不改变拟合/插值/误差定义。首轮测试的临时目录权限问题也已改用工作区临时目录解决。", "",
    "## 本机环境", "", f"- 平台：{meta['platform']}", f"- CPU：{meta['processor']}，逻辑{meta['logical_cpu_count']}核，物理{meta['physical_cpu_count']}核",
    f"- Python：{meta['python'].splitlines()[0]}；NumPy {meta['numpy']}；Numba {meta['numba']}",
    f"- 基础提交：`{meta['git_commit']}`；研究源码哈希见run.json。", "",
    "## 各来源完整100图最优候选", "", "这是对已复核候选的描述性汇总，未作独立盲测。", "",
    "| 来源 | LUT数 | mean中位数 | 最坏像素色差上界（本图片集） | 单图映射ms中位数 |", "|---|---:|---:|---:|---:|"]
for source in sorted({r["source"] for r in best_rows}):
    rows = [r for r in best_rows if r["source"] == source]
    lines.append(f"| {source} | {len(rows)} | {statistics.median(r['mean'] for r in rows):.6f} | {max(r['max'] for r in rows):.6f} | {statistics.median(r['median_ms_per_image'] for r in rows):.4f} |")
lines += ["", "## 候选选择观察", ""]
for (profile, size), count in Counter((r["profile"], r["m"]) for r in best_rows).most_common():
    lines.append(f"- `{profile}/m{size}`在{count}个LUT的已复核候选中获得最低mean。")
improvements = [r["improvement_percent"] for r in best_rows if r["improvement_percent"] is not None]
if improvements:
    lines.append(f"相对同LUT的33³直接采样四面体基线，mean降幅中位数为{statistics.median(improvements):.2f}%；这是同一照片集内选择后的结果，不能外推为新照片或新LUT上的保证。")
lines += ["", "## 抽样算法覆盖与精度", "", "此表每个配置只汇总成功执行的LUT，失败必须结合下节阅读；扩展配置只覆盖五张。", "",
          "| 配置 | m | 成功LUT数 | 抽样mean中位数 | 抽样mean最大值 |", "|---|---:|---:|---:|---:|"]
for (profile, size), values in sorted(algorithm_groups.items()):
    lines.append(f"| {profile} | {size} | {len(values)} | {statistics.median(values):.6f} | {max(values):.6f} |")
lines += ["", "## 未成功配置", ""]
if failures:
    for report, row in failures:
        lines.append(f"- {report['lut']['source_path']} / {row['profile']} / m{row['m']}：`{row['error']}`")
else:
    lines.append("本轮没有配置执行失败。")
lines += ["", "## 四级与全色域补充", "", f"四级数值链记录{len(chains['rows'])}条，其中成功{sum(r.get('status')=='ok' for r in chains['rows'])}条；入围单级模型全256³穷举{len(cube['rows'])}条。"]
if cube["rows"]:
    lines.append(f"入围模型全色mean范围{min(r['mean'] for r in cube['rows']):.6f}–{max(r['mean'] for r in cube['rows']):.6f}；全色最大误差范围{min(r['max'] for r in cube['rows']):.6f}–{max(r['max'] for r in cube['rows']):.6f}。这里同时含直接采样基线与择优候选，不是全部算法的范围。")
lines += ["", "## 文件入口", "", "- `compatibility.csv`：所有抽样与完整复核记录，stage字段区分范围。",
          "- `per-image.csv`：完整100图逐图mean/RMS/p99/max与阈值比例。",
          "- `screen-per-image.csv`：所有2740条配置×100张照片的抽样逐图指标；scope明确为screen_sample，不冒充完整图片成绩。",
          "- `best-per-lut.csv`：每张LUT完整复核后最优候选及33³采样基线。",
          "- `cube-finalists.json`、`cube-finalists.csv`：入围模型全部16,777,216颜色的精确统计。",
          "- `chains.json`、`chains.csv`：四级链定义、逐图精度、输出哈希与整组重复计时。",
          "- `luts/<源哈希>/result.json`：全部参数、求解诊断、失败与模型路径；`references/`：黄金表缓存。",
          "- `correctness-final.log`：13项正确性测试；`full.log`、`chains.log`：执行日志。",
          "- `audit.json`：全部素材、模型、代码哈希及各阶段记录数量的最终核验。", ""]

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
plt.rcParams["font.family"] = "Microsoft YaHei"
columns = sorted(algorithm_groups)
matrix = np.full((len(reports), len(columns)), np.nan)
for i, report in enumerate(reports):
    for row in report["screen"]:
        if row["status"] == "ok":
            matrix[i, columns.index((row["profile"],row["m"]))] = max(.001, row["quality"]["mean"])
fig, ax = plt.subplots(figsize=(18, 23))
plot = ax.imshow(matrix, aspect="auto", norm=LogNorm(.001, max(1., float(np.nanmax(matrix)))), cmap="viridis")
ax.set_xticks(range(len(columns)), [f"{p}\nm{m}" for p,m in columns], rotation=90, fontsize=7)
ax.set_yticks(range(len(reports)), [r["lut"]["source_id"]+"/"+Path(r["lut"]["path"]).stem[:24] for r in reports], fontsize=7)
ax.set_title("68张LUT × 稀疏化与插值配置：每图4096像素抽样平均RGB色差\n空格表示未运行或失败，完整统计见CSV")
fig.colorbar(plot, ax=ax, label="抽样平均RGB欧氏距离（对数色标）")
fig.tight_layout()
fig.savefig(out / "accuracy-heatmap.png", dpi=130)
plt.close(fig)
fig, ax = plt.subplots(figsize=(9,6))
for kernel in sorted({r["kernel"] for _,r in full}):
    data = [r for _,r in full if r["kernel"] == kernel]
    ax.scatter([r["median_ms_per_image"] for r in data], [r["quality"]["mean"] for r in data], label=kernel, alpha=.65, s=18)
ax.set_xlabel("完整100图中位映射时间 / 图（ms）")
ax.set_ylabel("完整100图mean RGB色差")
ax.set_title("仅含入围完整复核候选；不同LUT混合分布，不代表跨LUT胜负排名")
ax.legend()
fig.tight_layout()
fig.savefig(out / "full-accuracy-time.png", dpi=160)
plt.close(fig)
lines += ["![抽样精度覆盖](accuracy-heatmap.png)", "", "![完整复核精度与时间](full-accuracy-time.png)", ""]
(out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
files = [ROOT / "python/lutlab" / n for n in ("compatibility.py","source_lut.py","study_kernels.py","study_chains.py")]
files += [ROOT / "scripts/local_compatibility_pipeline.py", Path(__file__)]
files += [ROOT / "scripts/study_worker.py", ROOT / "scripts/check_full_cube_finalists.py", ROOT / "scripts/audit_local_lut_study.py",
          ROOT / "scripts/export_screen_per_image.py",
          ROOT / "tests/test_compatibility.py", ROOT / "tests/test_chain_study.py"]
(out / "workflow-code-sha256.json").write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, indent=2)+"\n", encoding="utf-8")
print(json.dumps(progress, ensure_ascii=False))
print(f"报告：{out / 'REPORT.md'}")
