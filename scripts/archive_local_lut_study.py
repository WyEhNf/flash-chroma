"""将已验证的本地研究按code/report归档，并生成两部分审核报告。"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import shutil
import statistics as stats

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIONS = {
    "sample_tetra": "均匀网格直接采样，四面体插值（4顶点）",
    "sample_tri": "均匀网格直接采样，三线性插值（8顶点）",
    "sample_nearest": "均匀网格直接采样，最近邻查询",
    "sample_hold": "均匀网格直接采样，单元下界零阶保持（255取上端点）",
    "sample_prism": "均匀网格直接采样，沿B轴拉伸的三角棱柱插值（6顶点）",
    "subpixel_tri": "按精确网格坐标重采样节点，三线性恢复",
    "subpixel_tetra": "按精确网格坐标重采样节点，四面体恢复",
    "box_tri": "Box局部平均构建节点，三线性恢复",
    "box_tetra": "Box局部平均构建节点，四面体恢复",
    "ls_tri_tri": "三线性基函数最小二乘拟合，三线性恢复",
    "ls_tri_tetra_mismatch": "三线性最小二乘拟合，改用四面体恢复；显式算子失配对照",
    "ls_tetra": "四面体最小二乘拟合，节点量化后四面体恢复",
    "ls_tetra_int": "四面体最小二乘加整数节点精化，四面体恢复",
    "jitter_tetra": "分层jitter采样拟合，四面体恢复",
    "curvature_int": "曲率驱动非均匀网格，四面体拟合加整数精化",
    "dp_jitter": "动态规划非均匀网格，分层jitter拟合及四面体恢复",
    "errorgrid_int": "误差驱动非均匀网格，四面体拟合加整数精化",
    "dp_boundary": "动态规划网格，边界补全采样拟合及四面体恢复",
    "dp_supported": "动态规划网格，补足所有节点数据支撑后拟合及四面体恢复",
    "tail_tetra": "尾部误差加权拟合加整数精化，四面体恢复",
    "irls_tetra": "迭代重加权最小二乘，关注较大残差，四面体恢复（来源代表子集）",
    "guarded_tetra": "带独立守护颜色集的Q16整数精化，四面体恢复（来源代表子集）",
}
FILES = {
    "python/lutlab/source_lut.py": "新增：解析CUBE、Hald TIFF、3DL，按明确轴序、裁剪和舍入政策生成黄金表。",
    "python/lutlab/study_kernels.py": "新增：Numba像素查询、五种插值、256³展开及精确色差直方图统计。",
    "python/lutlab/compatibility.py": "新增：组合配置、固定抽样、拟合缓存、候选选择、100图验证、计时与断点续跑。",
    "python/lutlab/study_chains.py": "新增：四级融合查询、逐级整数舍入、三组数值链及逐图指标。",
    "scripts/local_compatibility_pipeline.py": "新增：统一调度正确性、筛选、串行测速、四级、全色域、逐图导出、汇总和核验。",
    "scripts/study_worker.py": "新增：为Windows检查点文件占用注入有限重试，不改变数值算法。",
    "scripts/run_local_lut_study.py": "新增：早期简化启动入口；完整复现优先使用统一pipeline。",
    "scripts/check_full_cube_finalists.py": "新增：入围模型穷举全部16,777,216个RGB8输入。",
    "scripts/export_screen_per_image.py": "新增：导出所有配置的抽样逐图指标，核对与原筛选汇总一致。",
    "scripts/report_local_lut_study.py": "新增：原始汇总报告、最优候选CSV和两张科学图表。",
    "scripts/audit_local_lut_study.py": "新增：检查素材、代码、参考表、模型哈希及各结果表记录数量。",
    "scripts/archive_local_lut_study.py": "本次新增：整理code/report快照、配置指标汇总及本报告。",
    "tests/test_compatibility.py": "新增：源格式通道/轴序、既有Q16实现对照、三线性、棱柱、端点与统计测试。",
    "tests/test_chain_study.py": "新增：四级融合与逐级既有Q16实现一致性、独立误差统计测试。",
    "experiments/local-study-requirements.txt": "新增：本机独立研究环境的依赖版本。",
    "docs/local-lut-compatibility-workflow.md": "新增：复现命令、CI关系、范围、参考解释及已知限制。",
    "python/lutlab/fit.py": "既有依赖：各类节点拟合、整数精化、权重及非均匀网格实现。",
    "python/lutlab/interp.py": "既有依赖：独立插值实现与Q16正确性对照。",
    "python/lutlab/io.py": "既有依赖：稀疏LUT序列化、均匀网格及轴查表。",
    "python/lutlab/curve.py": "既有依赖：拟合与曲线相关辅助代码。",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def csv_write(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def med(values):
    return f"{stats.median(values):.4f}" if values else "未测"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "artifacts/local-lut-study/20261016")
    args = parser.parse_args()
    out = args.input.resolve()
    archive = out / "archive"
    code, report = archive / "code", archive / "report"
    data = report / "data"
    for directory in (code, data, report / "figures"):
        directory.mkdir(parents=True, exist_ok=True)
    audit = read(out / "audit.json")
    assert audit["status"] == "ok"
    reports = [read(p) for p in sorted((out / "luts").glob("*/result.json"))]
    meta = read(out / "run.json")
    images = read(ROOT / "assets/photos/manifest.json")
    luts = read(ROOT / "assets/LUT/manifest.json")
    chains = read(out / "chains.json")
    assert len(reports) == 68 and all(r["complete"] for r in reports)
    # 保留工作代码目录，仅复制不含缓存的源码快照。
    shutil.copytree(ROOT / "python/lutlab", code / "python/lutlab", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in FILES:
        destination = code / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    for name in ("assets/photos/manifest.json", "assets/LUT/manifest.json", ".github/workflows/correctness.yml"):
        destination = code / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    for path in out.iterdir():
        if path.is_file() and path.suffix in (".json", ".csv", ".log"):
            shutil.copy2(path, data / path.name)
        elif path.is_file() and path.suffix == ".png":
            shutil.copy2(path, report / "figures" / path.name)
    for folder in (out / "luts").iterdir():
        if folder.is_dir():
            target = data / "luts" / folder.name
            target.mkdir(parents=True, exist_ok=True)
            for path in folder.iterdir():
                if path.suffix in (".json", ".slut"):
                    shutil.copy2(path, target / path.name)
    raw_index = {"说明": "原始LUT与照片保留在仓库assets；黄金表缓存保留在原研究目录。路径相对仓库根目录，未重复复制。",
        "files": [{"path": e["path"], "sha256": e["sha256"]} for e in luts["assets"]]
        + [{"path": e["evaluation"]["path"], "sha256": e["evaluation"]["sha256"]} for e in images["images"]]
        + [{"path": str((out / "references" / (r["lut"]["sha256"][:12]+".npy")).relative_to(ROOT)).replace("\\", "/"),
            "sha256": r["reference_sha256"]} for r in reports]}
    (data / "external-data-index.json").write_text(json.dumps(raw_index, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    csv_write(data / "images.csv", [{"image": e["id"], "dataset": e["dataset"],
        "scene": e.get("suggested_scene", ""), "path": e["evaluation"]["path"],
        "sha256": e["evaluation"]["sha256"]} for e in images["images"]])
    csv_write(data / "luts.csv", [{"lut": e["path"], "source": e["source_id"], "format": e["format"], "sha256": e["sha256"]} for e in luts["assets"]])
    screen, full = defaultdict(list), defaultdict(list)
    full_rows = []
    best = []
    for r in reports:
        for row in r["screen"]:
            assert row["status"] == "ok"
            screen[(row["profile"], row["m"])].append(row)
        for row in r["full"]:
            assert row["status"] == "ok"
            full[(row["profile"], row["m"])].append(row)
            full_rows.append({"lut": r["lut"]["path"], "source": r["lut"]["source_id"],
                "profile": row["profile"], "m": row["m"], **row["quality"],
                "ms_per_image_median": row["median_ms_per_image"],
                "set_ms_1": row["set_ms"][0], "set_ms_2": row["set_ms"][1], "set_ms_3": row["set_ms"][2],
                "node_bytes": row["node_bytes"], "serialized_bytes": row["serialized_bytes"], "fit_s": row["fit_s"]})
        winner = min(r["full"], key=lambda v: v["quality"]["mean"])
        best.append((r, winner))
    csv_write(data / "full-results.csv", full_rows)
    summaries = []
    for (profile, m), rows in sorted(screen.items()):
        complete = full[(profile, m)]
        summaries.append({"profile": profile, "m": m, "description": DESCRIPTIONS[profile],
            "screen_luts": len(rows), "screen_mean_median": stats.median(r["quality"]["mean"] for r in rows),
            "screen_mean_worst_lut": max(r["quality"]["mean"] for r in rows),
            "full_luts": len(complete),
            "full_mean_median": stats.median(r["quality"]["mean"] for r in complete) if complete else "",
            "full_max_worst": max(r["quality"]["max"] for r in complete) if complete else "",
            "full_ms_per_image_median": stats.median(r["median_ms_per_image"] for r in complete) if complete else ""})
    csv_write(data / "algorithm-summary.csv", summaries)
    lines = ["# LUT与实际照片适配度检测报告", "", "日期：2026-10-16。状态：本地归档，未提交、推送或上传GitHub。", "",
        "## 1. 算法检测结果", "", "### 1.1 LUT、图片与检测范围", "",
        "- LUT共68个：Striped Purple 49、HDR2SDR 5、FilmSim 4、Christoph Wurst 3、Blender Filmic 7；格式为54个CUBE、7个Hald TIFF、7个3DL。文件名、来源、格式与SHA见[LUT清单](data/luts.csv)。",
        "- 照片共100张：Kodak 5、DPED 14、DIV2K 81；均为1024×768 RGB8，涵盖日常物体、人物、街景、自然及纹理。[图片清单](data/images.csv)逐张列出ID、来源、路径和SHA；原始授权随assets保留。",
        "- 20个基础配置分别覆盖68个LUT和17³/33³；IRLS、guarded各覆盖五个来源代表LUT和两档尺寸。合计22个配置名称、44个配置/尺寸组合、2740条LUT配置初筛记录；配置名称不等于独立算法数量。",
        "- 每配置在每张照片固定抽4096个像素（共409600）。按最低mean、最低max及33³采样四面体基线选择候选，去重后188条配置验证全部100张完整图片。全部2740条配置均有抽样逐图结果，只有入围188条有完整性能结果。",
        "- 另测三组四级数值链×10配置×两档尺寸，共60条；188个单级候选穷举完整256³ RGB8输入。", "",
        "### 1.2 精度与性能指标", "",
        "精度使用题目RGB欧氏距离 `sqrt(dR²+dG²+dB²)`，不是Lab色差。mean为平均距离，RMS为均方根距离，p99为每图99%分位数，max为最大像素距离；汇总中的worst_image_p99为最差单图p99。另保存误差≥1/2/3/5的像素比例。",
        "性能为预加载100图、预热后重复3次的映射耗时，含输出分配，不含PNG解码、JIT、拟合与误差统计。记录每图中位ms、100图三次原始ms、拟合秒数、节点/序列化字节及宿主RSS。拟合复用缓存，fit_s不代表独立冷启动总成本。",
        f"环境：{meta['platform']}；{meta['processor']}；Numba {meta['numba']} CPU四线程，BLAS单线程；Python {meta['python'].split()[0]}，NumPy {meta['numpy']}。基础提交 `{meta['git_commit']}`。",
        "正确性测试13项通过；原始研究最终核验通过，1788份不同模型校验一致。CMake缺失、g++启动DLL错误，未完成原有C++/CUDA门禁。本轮性能不能代表目标服务器的部署性能。",
        "源LUT按原网格三线性恢复，显式clip/round为RGB8黄金表，该定义可能有利于三线性候选；未知摄影色彩空间未推断。筛选与复核使用同一批照片，不是盲测。官方Threshold和聚合口径未知，不宣布官方达标。", "",
        "### 1.3 实际检测的算法简述与结果", "",
        "下表S17/S33为对应尺寸在已测LUT上的抽样mean中位数；完整N为两档尺寸入围条数，完整mean和ms为这些入围记录的中位数。不同算法入围的LUT集合不同，此表不能直接作公平速度排名；未测表示没有完整图测速。逐尺寸精确值见[算法汇总](data/algorithm-summary.csv)，逐LUT结果见[全部配置](data/compatibility.csv)。", "",
        "| 配置 | 算法简述 | S17 | S33 | 完整N | 完整mean | ms/图 |", "|---|---|---:|---:|---:|---:|---:|"]
    for profile, description in DESCRIPTIONS.items():
        complete = full[(profile,17)] + full[(profile,33)]
        lines.append(f"| `{profile}` | {description} | {med([r['quality']['mean'] for r in screen[(profile,17)]])} | {med([r['quality']['mean'] for r in screen[(profile,33)]])} | {len(complete)} | {med([r['quality']['mean'] for r in complete])} | {med([r['median_ms_per_image'] for r in complete])} |")
    lines += ["", "### 1.4 每个LUT的完整100图最优候选", "",
        "按已复核候选的mean选取；p99列为最差单图p99，max为100图所有像素最大值。平均误差低仍可能有较大局部误差。下表缩写仅去除文件扩展名，完整路径见[完整188条结果](data/full-results.csv)。", "",
        "| LUT（来源/名称） | 配置/尺寸 | mean | RMS | 最差p99 | max | ms/图 |", "|---|---|---:|---:|---:|---:|---:|"]
    for r, row in sorted(best, key=lambda pair: pair[0]["lut"]["path"]):
        q = row["quality"]
        lines.append(f"| {r['lut']['source_id']}/{Path(r['lut']['path']).stem} | `{row['profile']}/m{row['m']}` | {q['mean']:.4f} | {q['rms']:.4f} | {q['worst_image_p99']:.4f} | {q['max']:.4f} | {row['median_ms_per_image']:.4f} |")
    winners = Counter(row["profile"] for _,row in best)
    lines += ["", "已复核候选中最低mean的方案分布：" + "、".join(f"{p} {n}个LUT" for p,n in winners.most_common()) + "。没有一个配置在所有LUT上胜出。", "",
        "逐图查看：[完整图片18800条](data/per-image.csv)、[抽样图片274000条](data/screen-per-image.csv)。两张表可用LUT路径、profile、m和image关联，抽样值不等于完整图值。", "",
        "### 1.5 四级串联与全色域结果", "",
        "三组链使用不同的四张LUT，每级RGB8取整。它们是数值级联压力测试，未宣称摄影色彩域兼容。每组全部20条的算法/尺寸、mean、最差p99、max、时间见[四级结果](data/chains.csv)；具体四个LUT、逐图结果与三次计时见[链定义及原始结果](data/chains.json)。", "",
        "| 四级链 | 已测配置 | 最低mean候选 | mean | 最差p99 | max | ms/图 |", "|---|---:|---|---:|---:|---:|---:|"]
    for recipe in (1,2,3):
        rows = [r for r in chains["rows"] if r["recipe"] == recipe]
        row = min(rows, key=lambda r:r["mean"])
        lines.append(f"| {recipe} | {len(rows)} | `{row['profile']}/m{row['m']}` | {row['mean']:.4f} | {row['worst_image_p99']:.4f} | {row['max']:.4f} | {row['median_ms_per_image']:.4f} |")
    lines += ["", "[全色域结果](data/cube-finalists.csv)含188条单级候选的16,777,216种颜色精确统计；它覆盖照片未出现的颜色，但不能代替四级全色域证明。高阶样条、棱锥、神经网络、R25/R26原生全域拟合与C++/CUDA部署性能尚未纳入本轮实测。", "",
        "![全部LUT的抽样精度覆盖](figures/accuracy-heatmap.png)", "", "![入围方案精度与耗时](figures/full-accuracy-time.png)", "",
        "## 2. 已经开发的文件及作用", "", "### 2.1 code：源码快照", "",
        "下列路径均相对[code目录](../code/README.md)。新增研究代码保持原工作位置不变，归档内保留仓库相对路径；python/lutlab的其他既有模块随包复制，供依赖查阅。", "",
        "| 文件 | 作用 |", "|---|---|"]
    for name, description in FILES.items():
        lines.append(f"| [{name}](../code/{name}) | {description} |")
    lines += ["", "### 2.2 report：报告与证据文件", "", "| 文件 | 作用 |", "|---|---|",
        "| `report.md` | 本报告：检测范围、算法简述、精度/性能结果及文件作用。 |",
        "| `data/luts.csv`、`data/images.csv` | 68个LUT和100张照片的逐文件索引。 |",
        "| `data/algorithm-summary.csv` | 每种配置/尺寸的覆盖数量和精度、性能描述性汇总。 |",
        "| `data/full-results.csv` | 全部188个候选的完整精度、拟合、内存与三次原始计时。 |",
        "| `data/compatibility.csv` | 2740条初筛及188条完整记录，stage区分范围。 |",
        "| `data/per-image.csv`、`data/screen-per-image.csv` | 完整与抽样的逐LUT/逐配置/逐图片精度记录。 |",
        "| `data/best-per-lut.csv` | 每LUT最优候选、基线比较及全色域指标。 |",
        "| `data/chains.json`、`data/chains.csv` | 四级链配方、配置、逐图指标与原始性能。 |",
        "| `data/cube-finalists.json/csv` | 入围模型全256³颜色指标。 |",
        "| `data/luts/<哈希>/` | 各LUT配置参数、诊断、结果JSON及已生成SLUT模型；模型相对路径相对data目录。 |",
        "| `data/run.json`、`data/workflow-code-sha256.json` | 原始实验身份、环境及源码哈希。 |",
        "| `data/audit.json`、`data/*log` | 原始最终核验、正确性测试和阶段日志。 |",
        "| `data/external-data-index.json` | 未重复复制的原始素材及黄金表缓存位置和哈希。 |",
        "| `figures/` | 算法精度覆盖热力图及完整候选精度—耗时散点图。 |",
        "| `../archive-manifest.json` | 本次归档所有code/report文件的SHA-256和字节数。 |", "",
        "### 2.3 使用与复现", "",
        "归档供本地审核；不是独立发布包。原照片、LUT、授权和黄金表保留原位置，未重复复制大缓存。`code/`是源码快照，运行时应在原仓库根目录使用相同文件布局和研究依赖。", "",
        "```powershell", "python scripts/local_compatibility_pipeline.py --output artifacts/local-lut-study/20261016",
        "python scripts/archive_local_lut_study.py --input artifacts/local-lut-study/20261016", "```", "",
        "本次仅整理已有实测证据，没有重跑性能测试或修改冻结的数值算法。原始结果与原报告保留不变。", ""]
    (report / "report.md").write_text("\n".join(lines), encoding="utf-8")
    (code / "README.md").write_text("# 本地研究源码快照\n\n文件按仓库原相对路径保存。新增与既有文件职责见[报告第2部分](../report/report.md#2-已经开发的文件及作用)。\n\n复现须使用原仓库的assets及相同目录结构；本快照没有复制全部照片、LUT及黄金表缓存，不是独立运行环境。主入口为scripts/local_compatibility_pipeline.py，归档入口为scripts/archive_local_lut_study.py。\n", encoding="utf-8")
    entries = [{"path": str(p.relative_to(archive)).replace("\\", "/"), "bytes": p.stat().st_size, "sha256": digest(p)}
               for base in (code, report) for p in sorted(base.rglob("*")) if p.is_file()]
    (archive / "archive-manifest.json").write_text(json.dumps({"source_run": str(out.relative_to(ROOT)).replace("\\", "/"),
        "说明": "原实测未改动；本次归档的源码和报告文件哈希如下。", "files": entries}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for entry in entries:
        assert digest(archive / entry["path"]) == entry["sha256"]
    print(json.dumps({"archive": str(archive), "files": len(entries), "algorithms": len(DESCRIPTIONS),
        "algorithm_size_rows": len(summaries), "full_rows": len(full_rows), "bytes": sum(e["bytes"] for e in entries)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
