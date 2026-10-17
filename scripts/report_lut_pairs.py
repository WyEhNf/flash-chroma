"""汇总本地双尺寸实验，生成审核报告和精简配对表，不自动上传。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab.paired_baselines import digest, summarize, write_table


def table(path):
    with path.open(encoding="utf-8-sig",newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key,value in row.items():
            if value:
                try:
                    row[key] = int(value) if key in ("m","reference_m","node_bytes","reference_node_bytes") else float(value)
                except ValueError:
                    pass
    return rows


def number(value):
    return "未定义" if value is None or value=="" else f"{float(value):.4f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT/"artifacts/lut-dual-baseline/20261017")
    args = parser.parse_args()
    out = args.input.resolve()
    progress = summarize(out)
    assert progress == {"luts":68,"screen_rows":2740,"full_rows":356,"baseline_rows":136,
                        "screen_complete":68,"full_complete":68}, progress
    meta = json.loads((out/"run.json").read_text(encoding="utf-8"))
    pairs = table(out/"full-size_pair.csv")
    screen = table(out/"screen-size_pair.csv")
    same = table(out/"full-same_size.csv")
    small = table(out/"full-small_vs_large_baseline.csv")
    full = table(out/"full-results.csv")
    bases = [r for r in pairs if r["profile"]=="sample_tetra"]
    assert len(pairs)==178 and len(screen)==1370 and len(bases)==68
    write_table(out/"baseline-pairs.csv",bases)
    groups = []
    for scope,data in (("full_100_images",pairs),("screen_4096_per_image",screen)):
        for profile in sorted({r["profile"] for r in data}):
            rows = [r for r in data if r["profile"]==profile]
            groups.append({"scope":scope,"profile":profile,"luts":len(rows),
                "m17_mean_median":statistics.median(r["reference_mean"] for r in rows),
                "m33_mean_median":statistics.median(r["mean"] for r in rows),
                "mean_reduction_percent_median":statistics.median(r["mean_reduction_percent"] for r in rows if r["mean_reduction_percent"]!="") if any(r["mean_reduction_percent"]!="" for r in rows) else None,
                "m33_mean_better":sum(r["mean_delta"]<0 for r in rows),
                "m33_mean_equal":sum(r["mean_delta"]==0 for r in rows),
                "m33_mean_worse":sum(r["mean_delta"]>0 for r in rows),
                "m17_time_median":statistics.median(r["reference_time"] for r in rows),
                "m33_time_median":statistics.median(r["time"] for r in rows),
                "m33_over_m17_time_ratio_median":statistics.median(r["time_ratio_candidate_over_reference"] for r in rows),
                "time_unit":rows[0]["time_unit"]})
    write_table(out/"method-summary.csv",groups)
    better = sum(r["mean_delta"]<0 for r in bases)
    equal = sum(r["mean_delta"]==0 for r in bases)
    worse = len(bases)-better-equal
    exact_smaller = [r for r in small if r["profile"]!="sample_tetra" and all(
        r[key]<=r["reference_"+key] for key in ("mean","rms","worst_image_p99","max"))]
    no_slower = [r for r in exact_smaller if r["time"]<=r["reference_time"]]
    reports = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((out/"luts").glob("*/result.json"))]
    environment = meta["identity"]["environment"]
    summary = {"baseline_m33_mean_better":better,"baseline_m33_mean_equal":equal,"baseline_m33_mean_worse":worse,
        "baseline_mean_reduction_percent_median":statistics.median(r["mean_reduction_percent"] for r in bases if r["mean_reduction_percent"]!=""),
        "baseline_m33_over_m17_time_ratio_median":statistics.median(r["time_ratio_candidate_over_reference"] for r in bases),
        "m17_methods_no_worse_than_m33_baseline_four_quality_metrics":len(exact_smaller),
        "and_no_slower_in_this_measurement":len(no_slower),
        "m17_vs_m33_method_cases":len([r for r in small if r["profile"]!="sample_tetra"]),
        "full_measurements":len(full),"screen_measurements":progress["screen_rows"]}
    (out/"findings.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write_table(out/"m17-matches-m33-baseline.csv",exact_smaller)
    lines = ["# LUT m17/m33双基线与配对精度性能报告", "", "状态：实验已完成，代码与结果保留本地，待用户审核后正式提交。计划通知为[Draft PR #38](https://github.com/WyEhNf/flash-chroma/pull/38)。", "",
        "## 1. 算法检测结果", "", "### 1.1 输入、模型与实验范围", "",
        "- 使用原68个LUT、100张1024×768 RGB8照片，源文件/照片/黄金表及1788份不同模型均先核SHA。复用原冻结节点与轴表，不重新拟合；原拟合耗时不冒充新测量。",
        "- 全部22种配置名称保留原覆盖：20种基础配置各68个LUT；IRLS/guarded各5个来源代表LUT。m17/m33共2740条固定样本测量，每图4096像素，固定旧seed20261016，误差与旧记录逐项核对。",
        "- 68个LUT的直接采样+Q16四面体基线均完整测m17与m33，共136条；原188条结果冻结178个LUT/方法组合，两档共356条完整100图记录，未按本轮结果重新选方法。其他配置只有抽样结果，不冒充完整图成绩。",
        "- 每个LUT/方法的两档相邻执行，方法顺序及先测哪一档由seed20261017冻结。每个模型预热后测三次；全部计时本轮串行新测，旧计时未混入。未控制操作系统全部后台负载，三次变异保留，不宣布统计显著加速。",
        "- 基线是sample_tetra/m17及sample_tetra/m33，不是自动取第一行；同尺寸、跨尺寸、跨尺寸跨方法分表。两档节点载荷14739与107811字节，比值约7.315；序列化大小另列。", "",
        "### 1.2 指标与环境", "",
        "精度为RGB码值欧氏mean/RMS、最差逐图p99、所有图片max及阈值比例；最差单图p99不是全体像素的全局p99。性能含输出分配，不含解码、JIT、拟合或质量统计。完整时间单位ms/图（100图整组中位时间除100），抽样时间单位ms/409600查询，二者禁止混算。三次原始整组耗时、最小/最大值及宿主RSS保留；RSS不是模型独占内存。",
        f"环境：{environment['platform']}；{environment['cpu_name']}；Python {environment['python'].split()[0]}；NumPy {environment['packages']['numpy']} / Numba {environment['packages']['numba']} / llvmlite {environment['packages']['llvmlite']}；Numba {environment['numba_threads']}线程，线程层{environment['numba_threading_layer']}；BLAS/MKL/OMP=1。源提交`{meta['git_commit']}`及未提交研究源SHA见run.json。",
        "本次24项定向正确性测试通过，覆盖两尺寸Q16、独立插值统计、四级回归、唯一基线、配对缺失/重复、零基线及环境变更拒绝。首次沙箱因禁止NTFS硬链接导致原有来源保护测试失败，保留日志；宿主运行同组24项全部通过，未改来源保护实现。",
        "本轮未重新编译或测量C++/AVX2/C99/CUDA，没有新四级拟合或实板性能。当前照片均已观察，不称盲测；参考是原网格三线性展开再clip/round的RGB8，可能有利于三线性；未知摄影色彩域保持未知。官方Threshold未定，不宣布通过。", "",
        "### 1.3 两条基线的完整100图对比", "",
        f"m33相对m17，mean改善{better}个LUT、持平{equal}个、退化{worse}个；逐LUT相对降幅的中位数为{summary['baseline_mean_reduction_percent_median']:.2f}%，时间比中位数为{summary['baseline_m33_over_m17_time_ratio_median']:.3f}。m33并不自动保证每个LUT误差更低。",
        "这里比较的是指定直接采样/Q16四面体方法的实测，不是两档网格容量的理论最优。节点增多也会改变采样与舍入位置；本轮没有对每个退化LUT逐一作因果分解。",
        "下表每行是同一LUT的直接采样四面体基线；p99/max等完整字段见[baseline-pairs.csv](baseline-pairs.csv)。负降幅表示m33更差。", "",
        "| LUT | m17 mean | m33 mean | 降幅% | m17 ms/图 | m33 ms/图 |", "|---|---:|---:|---:|---:|---:|"]
    for row in sorted(bases,key=lambda r:r["lut"]):
        lines.append(f"| {row['source']}/{Path(row['lut']).stem} | {row['reference_mean']:.5f} | {row['mean']:.5f} | {number(row['mean_reduction_percent'])} | {row['reference_time']:.4f} | {row['time']:.4f} |")
    lines += ["", "### 1.4 同方法跨尺寸：完整图片候选", "",
        "每行只汇总实际完整复核的方法/LUT集合；不同方法覆盖集合不同，不能横向把此表当成公平全数据集排名。同一行的两档严格配对。mean列分别为逐LUTmean中位数，时间比为逐LUT时间比中位数。", "",
        "| 配置 | LUT数 | m17 mean | m33 mean | 改善/持平/退化 | m33/m17时间比 |", "|---|---:|---:|---:|---|---:|"]
    for row in groups:
        if row["scope"]=="full_100_images":
            lines.append(f"| {row['profile']} | {row['luts']} | {row['m17_mean_median']:.5f} | {row['m33_mean_median']:.5f} | {row['m33_mean_better']}/{row['m33_mean_equal']}/{row['m33_mean_worse']} | {row['m33_over_m17_time_ratio_median']:.3f} |")
    lines += ["", "### 1.5 同尺寸方法收益及小模型对大基线", "",
        "[full-same_size.csv](full-same_size.csv)共356条：候选m17只对m17直接采样基线，m33只对m33基线。mean、RMS、最差p99、max均给出绝对差，mean另给相对降幅；零误差基线相对降幅留空，绝对差保留。",
        f"[full-small_vs_large_baseline.csv](full-small_vs_large_baseline.csv)含178条m17对m33基线的明确跨尺寸比较。110条非基线方法/LUT记录中，{len(exact_smaller)}条在mean/RMS/最差p99/max四项均不差于m33基线，其中{len(no_slower)}条在本次中位映射时间也不慢。该筛选是已见数据的描述，不等于新LUT或新照片的保证。命中明细见[m17-matches-m33-baseline.csv](m17-matches-m33-baseline.csv)。", "",
        "### 1.6 全部22种配置的抽样配对", "",
        "所有配置在同一批409600查询上串行重新计时，能够比较该固定查询批量；不得称为实际100张完整图片耗时。下面mean为固定样本误差，单元格时间单位ms/409600查询。完整逐LUT配对见[screen-size_pair.csv](screen-size_pair.csv)。", "",
        "| 配置 | LUT数 | m17 mean | m33 mean | m17 查询ms | m33 查询ms |", "|---|---:|---:|---:|---:|---:|"]
    for row in groups:
        if row["scope"]=="screen_4096_per_image":
            lines.append(f"| {row['profile']} | {row['luts']} | {row['m17_mean_median']:.5f} | {row['m33_mean_median']:.5f} | {row['m17_time_median']:.4f} | {row['m33_time_median']:.4f} |")
    lines += ["", "## 2. 文件作用与复现", "", "| 文件 | 作用 |", "|---|---|",
        "| `python/lutlab/paired_baselines.py` | 冻结配对计划、验证旧模型与参考、同环境重新测量、生成三类严格关联的配对表。 |",
        "| `scripts/run_lut_pairs.py` | 固定Numba四线程及BLAS/MKL/OMP单线程的启动入口。 |",
        "| `scripts/report_lut_pairs.py` | 生成本审核报告、基线/方法摘要和图表；不影响计时内核。 |",
        "| `scripts/audit_lut_pairs.py` | 独立核对输入/代码SHA、完整配对、CSV算式、旧结果全部质量字段及188个旧完整输出SHA。 |",
        "| `tests/test_paired_baselines.py` | 两档唯一基线、配对完整性、零分母、范围隔离及Q16独立对照。 |",
        "| `run.json`、`validated-inputs.json` | 新测量身份、代码/数据/环境、冻结覆盖及输入核验。 |",
        "| `full-results.csv`、`screen-results.csv` | 新实测原始指标、三次时间、模型和输出SHA。 |",
        "| `*-same_size.csv` | 同LUT同尺寸方法对直接采样基线。 |",
        "| `*-size_pair.csv` | 同LUT同方法m33对m17。 |",
        "| `*-small_vs_large_baseline.csv` | 同LUT的m17方法对m33直接采样基线。 |",
        "| `per-image.csv`、`luts/` | 本地保留的35600条完整逐图结果与逐LUT检查点，不全部上传。 |",
        "| `findings.json`、`method-summary.csv`、`baseline-pairs.csv` | 本轮描述性结论及精简汇总。 |", "",
        "已有本机冻结模型时，从仓库根目录执行：", "", "```powershell",
        "python scripts/run_lut_pairs.py --input artifacts/local-lut-study/20261016 --output artifacts/lut-dual-baseline/20261017",
        "python scripts/report_lut_pairs.py --input artifacts/lut-dual-baseline/20261017", "```", "",
        "新检出仓库不包含旧1788份模型及黄金表，不能直接假装复现此同字节测量；需恢复同SHA模型/参考，或用既有拟合工作流在新目录生成另一组输入并明确作为新实验。源码、环境、输入任一身份变化都拒绝复用当前输出，须指定新目录。",
        "本轮模型拟合来源为原20261016实验；本轮运行环境与耗时为全新记录，二者不能混写。完整旧实验、失败日志和本轮逐图证据保留本地。", ""]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"]="Microsoft YaHei"
    fig,axes=plt.subplots(1,2,figsize=(13,5))
    for source in sorted({r["source"] for r in bases}):
        data=[r for r in bases if r["source"]==source]
        axes[0].scatter([r["reference_mean"] for r in data],[r["mean"] for r in data],label=source,s=28,alpha=.8)
        axes[1].scatter([r["reference_time"] for r in data],[r["time"] for r in data],label=source,s=28,alpha=.8)
    for ax,title,xlabel,ylabel in [(axes[0],"两条基线：完整100图平均RGB误差","m17 mean","m33 mean"),
        (axes[1],"两条基线：完整100图中位映射时间","m17 ms/图","m33 ms/图")]:
        low=min(ax.get_xlim()[0],ax.get_ylim()[0]);high=max(ax.get_xlim()[1],ax.get_ylim()[1])
        ax.plot([low,high],[low,high],"--",color="gray",linewidth=1)
        ax.set(xlabel=xlabel,ylabel=ylabel,title=title);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/"baseline-pairs.png",dpi=150);plt.close(fig)
    lines += ["![双基线完整图片精度与时间](baseline-pairs.png)", ""]
    (out/"report.md").write_text("\n".join(lines),encoding="utf-8")
    code=[ROOT/p for p in ("python/lutlab/paired_baselines.py","scripts/run_lut_pairs.py","scripts/report_lut_pairs.py","scripts/audit_lut_pairs.py","tests/test_paired_baselines.py")]
    (out/"delivery-code-sha256.json").write_text(json.dumps({str(p.relative_to(ROOT)).replace("\\","/"):digest(p) for p in code},indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))
    print(out/"report.md")


if __name__=="__main__":
    main()
