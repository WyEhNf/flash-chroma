"""Build the Chinese latest-tested report solely from frozen stage evidence."""
from __future__ import annotations

import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
    PageBreak, Spacer, Table, TableStyle, KeepTogether, Flowable)
from reportlab.graphics.shapes import Drawing, Line, Rect, String, PolyLine, Circle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report/latest"
ART = ROOT / "artifacts/r27-step"
NAVY = colors.HexColor("#153044")
TEAL = colors.HexColor("#087F8C")
GRAY = colors.HexColor("#526371")
LIGHT = colors.HexColor("#EEF4F6")
RED = colors.HexColor("#A74338")
GOLD = colors.HexColor("#B47822")
WIDTH, HEIGHT = A4
CONTENT = WIDTH - 88


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def f(value, digits=4):
    return f"{value:.{digits}f}"


def mib(value):
    return f(value / 1024 ** 2, 2)


class Report(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "H1":
            text = flowable.getPlainText()
            key = f"section-{self.page}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=0)


def page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(1.5)
    canvas.line(44, HEIGHT - 34, WIDTH - 44, HEIGHT - 34)
    canvas.setFillColor(GRAY)
    canvas.setFont("Body", 8)
    canvas.drawString(44, HEIGHT - 26, "第16题 · 极速焕彩 / 最新已测版本 R27")
    canvas.drawRightString(WIDTH - 44, HEIGHT - 26, "2026-10-15")
    canvas.setStrokeColor(colors.HexColor("#CDD9DF"))
    canvas.setLineWidth(.5)
    canvas.line(44, 36, WIDTH - 44, 36)
    canvas.setFillColor(GRAY)
    canvas.drawString(44, 23, "本地数据结论；官方数据、阈值及服务器仍待发布")
    canvas.drawRightString(WIDTH - 44, 23, str(doc.page))
    canvas.restoreState()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont("Body", "C:/Windows/Fonts/Deng.ttf"))
    pdfmetrics.registerFont(TTFont("Strong", "C:/Windows/Fonts/Dengb.ttf"))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Strong", italic="Body", boldItalic="Strong")
    rl_config.warnOnMissingFontGlyphs = 1
    styles = {
        "body": ParagraphStyle("BodyText", fontName="Body", fontSize=10, leading=16,
            textColor=NAVY, spaceAfter=8, wordWrap="CJK", rightIndent=6),
        "small": ParagraphStyle("Small", fontName="Body", fontSize=8.2, leading=12.5,
            textColor=GRAY, spaceAfter=6, wordWrap="CJK", rightIndent=6),
        "h1": ParagraphStyle("H1", fontName="Strong", fontSize=20, leading=27,
            textColor=NAVY, spaceAfter=17, wordWrap="CJK"),
        "subtitle": ParagraphStyle("Subtitle", fontName="Strong", fontSize=17, leading=25,
            textColor=NAVY, spaceAfter=17, wordWrap="CJK"),
        "h2": ParagraphStyle("H2", fontName="Strong", fontSize=12, leading=18,
            textColor=TEAL, spaceBefore=11, spaceAfter=7, keepWithNext=True, wordWrap="CJK"),
        "cell": ParagraphStyle("Cell", fontName="Body", fontSize=8.5, leading=12.5,
            textColor=NAVY, wordWrap="CJK"),
        "head": ParagraphStyle("Head", fontName="Strong", fontSize=8.5, leading=12,
            textColor=colors.white, wordWrap="CJK"),
    }
    story = []

    def p(text, kind="body"):
        return Paragraph(text, styles[kind])

    def add(text, kind="body"):
        story.append(p(text, kind))

    def heading(text):
        add(text, "h2")

    def section(text):
        if story:
            story.append(PageBreak())
        add(text, "h1")

    def table(rows, widths, small=False):
        cells = [[p(str(value), "head" if index == 0 else ("small" if small else "cell"))
                  for value in row] for index, row in enumerate(rows)]
        t = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LINEBELOW", (0, 0), (-1, 0), .6, TEAL),
        ]))
        story.append(t)
        story.append(Spacer(1, 9))

    def bars(items, xmax, axis_label, width=CONTENT, height=180):
        drawing = Drawing(width, height)
        left, right, top, bottom = 115, 68, 27, 30
        usable = width - left - right
        for j in range(5):
            x = left + usable * j / 4
            drawing.add(Line(x, bottom, x, height - top, strokeColor=colors.HexColor("#DCE5EA"), strokeWidth=.5))
            drawing.add(String(x, bottom - 15, f(xmax * j / 4, 1), fontName="Body", fontSize=8,
                fillColor=GRAY, textAnchor="middle"))
        row_height = (height - top - bottom) / len(items)
        for index, (label, value, color) in enumerate(items):
            y = height - top - row_height * (index + .5)
            drawing.add(String(left - 10, y - 3, label, fontName="Body", fontSize=9,
                fillColor=NAVY, textAnchor="end"))
            drawing.add(Rect(left, y - 7, usable * value / xmax, 14, fillColor=color, strokeColor=None))
            drawing.add(String(left + usable * value / xmax + 6, y - 3, f(value, 3),
                fontName="Body", fontSize=8.5, fillColor=NAVY))
        drawing.add(String(left, 1, axis_label, fontName="Body", fontSize=8, fillColor=GRAY))
        return drawing

    def paired_plot(old, new):
        width, height = CONTENT, 218
        d = Drawing(width, height)
        left, bottom, right, top = 45, 34, 15, 22
        w, h, ymax = width - left - right, height - bottom - top, 7.
        for tick in range(8):
            y = bottom + h * tick / ymax
            d.add(Line(left, y, width - right, y, strokeColor=colors.HexColor("#DCE5EA"), strokeWidth=.4))
            d.add(String(left - 10, y - 3, str(tick), fontName="Body", fontSize=8, textAnchor="end", fillColor=GRAY))
        for values, color, label in ((old, GOLD, "R25"), (new, TEAL, "R27")):
            coordinates = []
            for i, value in enumerate(values):
                coordinates.extend((left + w * i / 99, bottom + h * value / ymax))
            d.add(PolyLine(coordinates, strokeColor=color, strokeWidth=1.2))
            d.add(String(width - (85 if label == "R25" else 40), height - 12,
                label, fontName="Strong", fontSize=9, fillColor=color))
        d.add(String(left, 10, "图片索引 0-99；纵轴为该图平均 RGB ΔE", fontName="Body", fontSize=8.5, fillColor=GRAY))
        return d

    study = read(ART / "study.json")
    mapping = read(ART / "mapping-comparison.json")
    industry = read(ART / "industry/comparison.json")
    if not study.get("structural_parity_partition_and_palette_pass") or not mapping.get("inputs_unchanged") or not industry.get("inputs_unchanged"):
        raise RuntimeError("report requires all completed successful stages")
    for filename, digest in study["source_sha256"].items():
        if sha(ROOT / filename) != digest:
            raise RuntimeError(f"frozen algorithm changed: {filename}")
    for evidence in (mapping, industry):
        for filename, digest in evidence["input_and_source_sha256"].items():
            if sha(filename) != digest:
                raise RuntimeError(f"comparison input changed: {filename}")
    cases = study["cases"]
    stress_case = next(c for c in cases if c["scenario"] == "stress-13")
    accepted = read(stress_case["result"])
    prior = read(stress_case["baseline_result"])
    native = accepted["backends"]["cpu"]
    native_old = prior["backends"]["cpu"]
    cube, old_cube = native["cube"], native_old["cube"]
    cpu_ms, gpu_ms = mapping["median_ms_per_100"]["cpu"], mapping["median_ms_per_100"]["cuda"]
    industry_ms = industry["median_ms_per_100"]
    quality = industry["accuracy"]
    total_pass = sum(c["comparison"]["local_mean_gate"]["candidate"] for c in cases)
    chosen = {}
    for c in cases:
        if c["scenario"] not in chosen or c["comparison"]["worst_image_mean"]["candidate"] < chosen[c["scenario"]]["comparison"]["worst_image_mean"]["candidate"]:
            chosen[c["scenario"]] = c
    reductions = 100 * (1 - cube["mean"] / old_cube["mean"])
    peak_cpu = statistics.median(row["runtime"]["observed_peak_working_set_bytes"] for row in mapping["runs"] if row["configuration"] == "cpu")
    peak_gpu_host = statistics.median(row["runtime"]["observed_peak_working_set_bytes"] for row in mapping["runs"] if row["configuration"] == "cuda")
    gpu_run = next(row["runtime"] for row in mapping["runs"] if row["configuration"] == "cuda")
    cpu_run = next(row["runtime"] for row in mapping["runs"] if row["configuration"] == "cpu")
    fit_seconds = stress_case["candidate_fit"]["fit"]["fit_s"]

    # 1. Executive page.
    add("最新已完成测试版本", "small")
    story.append(Spacer(1, 24))
    add("第16题 · 极速焕彩", "h1")
    add("正确性、精度、性能与开源先进方案对比", "subtitle")
    add("R27 阶段技术评估报告 · 2026年10月15日", "body")
    story.append(Spacer(1, 18))
    table([
        ["当前实测结论", "结果"],
        ["压力场景全色域平均 ΔE", f"{f(old_cube['mean'])} → {f(cube['mean'])}，下降 {f(reductions, 2)}%"],
        ["100 张图，CPU / CUDA", f"{f(cpu_ms, 3)} / {f(gpu_ms, 3)} ms；分别约 {f(cpu_ms/100, 4)} / {f(gpu_ms/100, 4)} ms/图"],
        ["同模型开源 CPU 基线", f"相对 OCIO 2.6 四工作线程接入路径，配对加速中位数 {f(industry['comparison']['paired_speedup_median'], 2)} 倍"],
        ["本地精度示例门槛", f"固定配置 {total_pass}/13 组通过；每个源选择已测合法 m 后，9/9 个源通过"],
    ], [185, CONTENT - 185])
    heading("报告结论的边界")
    add("当前版本具有完整的本地正确性证据，R27 显著修复了压力家族的平均色差。它仍不能被认定为官方通过，也不能被认定为全行业 SOTA：官方数据、Threshold、判定粒度和统一服务器尚未取得；开源论文的图像增强任务与本题的给定四 LUT 逼近任务存在差异。")
    add("压力模型的最大 RGB ΔE 仍为 38.4187；如果正式规则要求逐像素误差低于 2，本版本会失败。已测速度是批处理吞吐均值，不是单张冷启动延迟。", "body")
    add("版本定位：C++17 CPU 主线 + 可选 CUDA；新增 adaptive_full 仅显式启用，尚未替换默认候选。代码基点 de4571d；R20-R27 为未提交的本地工作区成果，依靠源码与输入 SHA256 冻结。", "small")

    # 2. Requirements.
    section("01 题目要求与覆盖状态")
    add("依据用户提供的题面截图及仓库 PROBLEM.md。精度使用题面 RGB 欧氏距离，ΔE = sqrt((R1-R2)²+(G1-G2)²+(B1-B2)²)，没有换用 Lab/CIEDE2000。")
    table([
        ["要求 / 指标", "当前测试结果与口径", "状态"],
        ["输入 1024×768、RGB、8-bit", "100 个不同文件；实际原生解码并验证，拒绝 16-bit、错误通道及尺寸", "已覆盖"],
        ["4 个完整 256³ 整型 LUT", "RGB8 项目适配格式，每张 50,331,648 字节；4 张源哈希各异", "已覆盖*"],
        ["17 ≤ m ≤ 33", "真实案例 m=17/18/33；耦合控制另含 m=25；非法尺寸拒绝", "已覆盖"],
        ["输出 m³ 整型节点", "4 张普通 RGB8 稀疏表，每级独立；文件及 manifest 检查", "已覆盖"],
        ["所在晶体定位与插值", "非均匀整数轴；几何 Q16 或已证明的零阶保持选择", "已覆盖"],
        ["四次独立映射、整数中间值", "每级使用其自身原始 LUT 标签；四级逐次 RGB8 输出", "已覆盖"],
        ["精度硬门槛 ΔE < Threshold", "全色域与逐图 mean/RMS/p99/max 均报告；示例采用严格 mean<2", "官方待定"],
        ["100 张图四级平均耗时", "7 对 AB/BA，每进程 3 次；CPU、CUDA 及 OCIO 同输入", "本机已测"],
        ["指定服务器 / i7-14700 示例", "当前为 AMD 8945HX + RTX 5070 Laptop；不是指定 Intel 机器", "尚未覆盖"],
        ["内存与压缩", "节点、文件、运行时模型、工作集、显式 GPU 缓冲分项报告", "本机已测"],
        ["移植与工程落地", "C++17 独立构建、可选后端；OFF 配置完成真实拟合对照", "部分覆盖"],
    ], [116, 329, CONTENT - 445], small=True)
    add("* 题面只明确 LUT 为整型，未明确节点位深、容器和字节序。当前 RGB8 适配正确性不能替代正式格式适配。I/O 和稀疏化是否计时也尚未明确。", "small")

    # 3. Method and environment.
    section("02 算法、架构与测试环境")
    table([
        ["项目", "已确认环境"],
        ["CPU / 操作系统", "AMD Ryzen 9 8945HX，16 核 / 32 逻辑线程，Windows x64；AVX2 与操作系统寄存器状态支持已核验"],
        ["GPU", f"{escape(str(mapping['capabilities']['cuda']['device']))}；计算能力 12.0；显存约 8 GiB"],
        ["编译与依赖", "C++17 / MinGW GCC 15.2；CUDA Toolkit 13.2 / MSVC 14.44；Python + NumPy/SciPy；OpenColorIO 2.6.0"],
        ["并行政策", "实验串行运行；只在单个任务内部使用 OpenMP/CUDA。CPU 性能分别声明 4 或 16 工作者"],
    ], [112, CONTENT - 112])
    heading("R27 的三级选择")
    add("第一步检查完整 LUT 的相邻切片。若每轴常值区间的全部边界可以容纳在 m 个节点中，就构造精确零阶保持模型；这也适用于三个轴相互耦合的分段常量变换。")
    add("第二步利用已证明的前缀输出超集，将其全部分量取值纳入下一级网格。节点依旧只采样该级原始 LUT，并对整个超集直接查表核对。否则回退至 R25 的精确全色域法方程拟合。")
    add("压力源的四级路线：R25 曲线拟合 → 精确阶梯量化 → 可达节点精确布点 → R25 三维拟合。第二级覆盖全部 RGB8 输入， 第三级的保证仅覆盖前缀输出超集；它不吸收前级误差。")
    heading("没有改变的运行时合同")
    add("每一级仍保存 m³ 个 RGB8 节点，通过原有 SLUT v1 权威轴表定位并执行整数四面体权重；每级立即舍入到 RGB8。零阶保持的权重为 0 或 65536，明确不同于几何距离比例。没有增加运行时稠密 LUT、神经网络、复合表或图像相关残差。")
    add("C++/CUDA 像素算术本轮未修改。新入口 fit_model 保留自定义轴表；旧的仅节点返回接口明确拒绝 adaptive_full，避免调用者丢弃插值政策。缓存绑定方法、源 LUT、源码、拟合默认值和原生训练库指纹。", "small")

    # 4. Protocol.
    section("03 阶段正确性与实验方法")
    table([
        ["证据", "范围", "结果"],
        ["Python 合同", "本轮集中一次，15 项；原生算子未改，不重复其昂贵 COO oracle", "全部通过"],
        ["独立三维耦合控制", "四个不同完整 LUT；m=17/18/25/33；CPU、CUDA 各穷举 16,777,216 个输入", "与完整四表串联逐字节一致"],
        ["13 组固定模型配置", "全部经统一 fit CLI 重新拟合，回退级核对冻结 R25 完整文件字节", "52 个级中仅压力源两级变化"],
        ["未变化的 12 组", "48 张模型字节不变；原始 LUT、复合真值、图片、清单和执行文件哈希逐项核验", "复用 R25 真实 CPU/CUDA 验收"],
        ["变化的压力组", "CPU、CUDA 各全色域穷举 + 100 张标准图实际执行", "两个后端的色域和图像 SHA 均相同"],
        ["计时实现的预检", "CPU gather16 / CUDA batch100，实际 235,929,600 字节图像输出", "与已验收结果逐字节相同"],
        ["拒绝控制", "连续变化源、缺失集合证明、超节点预算、非法集合、节点接口丢权重", "均按预期拒绝精确声明"],
    ], [112, 275, CONTENT - 387], small=True)
    add("复用不是重新执行：12 组原有证据的输入与模型完全相同，因此没有为生成报告重跑全部像素。新路线另有完整三维耦合控制，避免仅验证可分离函数。阶段耗时约 " + f(study["elapsed_seconds"], 2) + " 秒（含集中合同检查、13 组拟合和必要的验收）。", "body")
    heading("性能统计")
    add("每个配对交替 AB/BA；每个独立进程运行 3 次，以其批次耗时中位数形成一个观测。报告 7 对比值的中位数、固定种子 10,000 次配对重采样的 95% 区间与胜出对数。比值中位数通常不等于两个边际中位数之比。")
    add("图片使用同一组 100 个本地生成/冻结文件。9 个不同源配置仍主要来自模拟变换家族；stress 的种子不改变其固定变换，不能当作多个独立随机压力样本。所有数据均不代表官方测试分布。", "small")

    # 5. All current accuracy.
    section("04 全部已测配置的精度结果")
    add("下表为当前 R27 结果。门槛列要求全部 100 张图的 mean<2 且全色域 mean<2；这是示例规则，不能替代官方判定。全色域每组包含 16,777,216 个输入颜色。")
    rows = [["源 / m", "mean", "RMS", "p99", "max", "最差图 mean", "示例"]]
    csvrows = []
    for c in cases:
        a = read(c["result"])
        value = a["backends"]["cpu"]
        q = value["cube"]
        rows.append([f"{c['scenario']} / {c['m']}", f(q["mean"]), f(q["rms"]), f(q["p99"], 3),
            f(q["max"], 3), f(value["worst_image_metric"]), "通过" if c["comparison"]["local_mean_gate"]["candidate"] else "失败"])
        csvrows.append({"scenario": c["scenario"], "m": c["m"], **{k: q[k] for k in ("mean", "rms", "p99", "max")},
            "worst_image_mean": value["worst_image_metric"], "illustrative_mean_gate": c["comparison"]["local_mean_gate"]["candidate"],
            "execution_evidence": c["execution_evidence"], "result_sha256": c["result_sha256"]})
    table(rows, [105, 60, 60, 55, 55, 105, CONTENT - 440])
    heading("固定 m 与容量选择必须分别报告")
    add(f"固定配置为 {total_pass}/13 组通过。clip-7/m17、clip-23/m18 和 clip-31/m18 仍失败，不能隐去。选用已测更大网格后，9 个不同源均存在一个通过示例门槛的合法配置；该选择已使用这些样本，不是独立泛化验证。")
    add("13 组均不能满足全色域 max<2。m 从 18 增至 33 时，四表节点数据从 69,984 增至 431,244 字节；精度提升伴随明确的容量成本。", "small")

    # 6. Stress focus.
    section("05 压力场景：主要改善与剩余误差")
    story.append(bars([("R25 全色 mean", old_cube["mean"], GOLD), ("R27 全色 mean", cube["mean"], TEAL)], 4.5,
        "同一 stress-13/m33，RGB ΔE；越低越好", height=140))
    table([
        ["指标", "R25", "R27", "变化"],
        ["全色 mean", f(old_cube["mean"]), f(cube["mean"]), f"下降 {f(reductions, 2)}%"],
        ["全色 p99 / max", f"{f(old_cube['p99'], 3)} / {f(old_cube['max'], 3)}", f"{f(cube['p99'], 3)} / {f(cube['max'], 3)}", "均降低"],
        ["100 图最差 mean", f(native_old["worst_image_metric"]), f(native["worst_image_metric"]), "示例门槛由失败转通过"],
    ], [130, 106, 106, CONTENT - 342])
    story.append(paired_plot([v["mean"] for v in native_old["per_image"]], [v["mean"] for v in native["per_image"]]))
    add("100 张图的 mean 全部改善；但逐图 p99 有 39 张上升、max 有 23 张上升。不能把全色域四项同时改善写成所有图片每个指标都改善。", "small")
    add(f"全色域中仍有 {cube['pixels_at_or_above_threshold']:,} 个颜色（约 {100*cube['pixels_at_or_above_threshold']/256**3:.3f}%）的 ΔE≥2。最坏输入示例为 RGB(96,27,10)，误差 38.4187；下一步应追踪前级逼近在量化边界附近造成的跨阶跃差异。", "small")

    # 7. Speed.
    section("06 当前模型的严格性能比较")
    table([
        ["运行配置", "100 图中位 ms", "均摊 ms/图", "均摊吞吐 图/s"],
        ["CPU AVX2 gather，16线程、batch", f(cpu_ms, 3), f(cpu_ms/100, 4), f(100000/cpu_ms, 1)],
        ["CUDA，batch100，普通主机到普通主机", f(gpu_ms, 3), f(gpu_ms/100, 4), f(100000/gpu_ms, 1)],
        ["CPU AVX2，4线程、逐图", f(industry_ms["cpu"], 3), f(industry_ms["cpu"]/100, 4), f(100000/industry_ms["cpu"], 1)],
        ["OpenColorIO，4工作线程、Python buffer", f(industry_ms["ocio"], 3), f(industry_ms["ocio"]/100, 4), f(100000/industry_ms["ocio"], 1)],
    ], [220, 95, 95, CONTENT - 410])
    stat = mapping["comparison"]
    add(f"CPU16/CUDA 的配对加速比中位数为 {f(stat['paired_speedup_median'], 3)}，95% 区间 [{f(stat['paired_median_bootstrap_95_ci'][0], 3)}, {f(stat['paired_median_bootstrap_95_ci'][1], 3)}]；CUDA 在 7/7 对更快，单侧符号检验 p=0.0078125。该比较同时改变硬件和并行方式，不能归因于某一条 CUDA 指令。")
    heading("计时边界")
    add("CPU 包含输入复制与四级映射。CUDA 包含普通主机到锁页区复制、H2D、四级融合 kernel、D2H/等待及复制回普通主机。两者均排除分配、拟合、模型载入、图片解码、PNG 编码和校验。CUDA 驻留 kernel 中位约 " + f(statistics.median(r["runtime"]["set_resident_event_ms_p50"] for r in mapping["runs"] if r["configuration"] == "cuda"), 3) + " ms/100，另列诊断，不替代含传输主结果。")
    heading("离线稀疏化与端到端范围")
    add(f"R27 压力组四张表的单次记录 fit_s={f(fit_seconds, 3)} 秒，包含网格选择和拟合，不含源文件加载与发布；没有据单次记录宣称拟合加速。R25 的独立 7 对对照显示，全色域原生法方程单线程较 Python COO 快 55.47 倍，但这只对应组装阶段。")
    add("本轮 bench 进程墙时中位约 CPU 0.543 秒、CUDA 1.530 秒，包含解码、预热和多轮测量，不能用作一批单次端到端延迟。PNG 编码、官方 I/O 和稀疏化是否纳入赛题耗时尚待明确。题面 Intel 上的 1.5 秒/图示例也不是本机成绩的直接评分阈值。", "small")

    # 8. OpenColorIO.
    section("07 OpenColorIO 2.6 同口径实测")
    add("OpenColorIO 是 ASWF 的成熟开源颜色管理框架；官方 2.6 发布信息已核验 [外1]。本轮用相同四表节点和权威轴坐标构建 shaper + 3D LUT，保持四个 UINT8 阶段边界；OCIO 内部仍采用 float32 插值。")
    table([
        ["指标（当前压力源）", "本实现 Q16", "OpenColorIO 2.6"],
        ["全色 mean / RMS", f"{f(cube['mean'])} / {f(cube['rms'])}", f"{f(quality['ocio_vs_truth']['mean'])} / {f(quality['ocio_vs_truth']['rms'])}"],
        ["全色 p99 / max", f"{f(cube['p99'], 3)} / {f(cube['max'], 3)}", f"{f(quality['ocio_vs_truth']['p99'], 3)} / {f(quality['ocio_vs_truth']['max'], 3)}"],
        ["100 图最差 mean / 失败数", f"{f(native['worst_image_metric'])} / 0", f"{f(industry['actual_images']['worst_mean'])} / {industry['actual_images']['failed_images']}"],
        ["4工作线程，ms/100 图", f(industry_ms["cpu"], 3), f(industry_ms["ocio"], 3)],
        ["进程峰值工作集中位 MiB", mib(statistics.median(r["runtime"]["observed_peak_working_set_bytes"] for r in industry["runs"] if r["arm"]=="cpu")), mib(statistics.median(r["runtime"]["process"]["observed_peak_working_set_bytes"] for r in industry["runs"] if r["arm"]=="ocio"))],
        ["对本项目 Q16 的逐字节等价", "CPU/CUDA 相同", f"{quality['mismatch_pixels']:,}/{256**3:,} 个输入不同"],
    ], [200, 145, CONTENT - 345])
    stat = industry["comparison"]
    add(f"OCIO4/CPU4 配对加速比中位数 {f(stat['paired_speedup_median'], 3)}，95% 区间 [{f(stat['paired_median_bootstrap_95_ci'][0], 3)}, {f(stat['paired_median_bootstrap_95_ci'][1], 3)}]，7/7 对 CPU 更快。区间仅表达本机这 7 对样本的不确定性。")
    add("OCIO 在本例的平均误差略低，不能宣称本实现在精度上全面超过 OCIO。两个路径优化的是同样的节点表示，但算术不同，故速度比较是明确的工程接入路径比较，不是对严格相同输出定义的框架竞速。")
    add("OCIO 的 Python 线程分派、逐图输入复制及 buffer 调用成本均包含在计时中；未测试其直接 C++ 集成或 GPU processor，也未为 OCIO 扫描全部配置。工作集包含 Python、动态库和输入图片；不等于纯插值算子的内存。四线程比较采用相同工作者数，但没有声称等资源隔离或全系统独占。", "small")

    # 9. Literature/SOTA.
    section("08 开源先进方案 / SOTA 的可比性")
    add("本次核对优先采用官方仓库、论文和文档 [外1-5]。没有发现可直接搬用的公开排名同时满足本题给定四 LUT、每级整数、m≤33、100 张指定图片和相同机器。因此不使用“全球 SOTA”作为已证结论。")
    table([
        ["方案", "技术与公开状态", "可比较的指标 / 结论"],
        ["本项目 R27", "给定 LUT 的离线逼近；整数阶段；C++17/AVX2/CUDA", "本地 RGB ΔE、100 图吞吐、模型字节、工作集有实测；正式分数未知"],
        ["OpenColorIO 2.6 [外1-2]", "成熟开源颜色管理；支持四面体插值", "本轮同模型 CPU 实测；精度略优，当前接入耗时较长；不能外推所有配置"],
        ["AdaInt，CVPR 2022 [外3]", "作者公开 PyTorch/CUDA；学习非均匀 LUT 采样区间", "与自适应网格思路相关；其照片增强真值和训练目标不同，未在本题重训或复测"],
        ["SVDLUT，ICCV 2025 [外4-5]", "作者公开实现；低维 LUT + SVD + 空间特征融合", "与压缩及缓存优化相关；其模型参数量不等于本题四表存储，PSNR/Lab ΔE不可直接换算"],
    ], [102, 190, CONTENT - 292])
    heading("文献原值：仅为背景，不能计算跨任务加速比")
    table([
        ["SVDLUT 论文 Table 3，FiveK 480p", "参数量", "PSNR", "SSIM", "Lab ΔE", "GPU ms"],
        ["AdaInt（该论文对照）", "619.7K", "25.49", "0.926", "7.47", "1.29"],
        ["SVDLUT", "160.5K", "25.76", "0.931", "7.26", "1.37"],
    ], [198, 70, 58, 58, 65, CONTENT - 449], small=True)
    add("以上为作者论文在 Tesla V100 上的图像增强结果 [外4]，不是本机复测。其 Lab 色差、感知指标、神经网络生成 LUT 与分辨率均不同，不能拿 7.26 与本题 RGB 0.3767 比大小，也不能将 1.37 ms 与本报告批量均摊 0.6776 ms 计算领先倍数。", "small")
    add("截至本报告检索日还可见 LoopLUT（2026-09 预印本）[外6]，聚焦区域级增强；本轮未验证其公开代码与本题兼容性，故不将其列为已复现的开源基线。", "small")

    # 10. Memory.
    section("09 内存、压缩与可落地性")
    table([
        ["内存口径", "当前实测 / 精确计数", "解释"],
        ["4 张完整 RGB8 LUT", "201,326,592 B = 192 MiB", "离线输入；运行时不装载完整表"],
        ["4 张 m33 节点 payload", "431,244 B = 0.411 MiB", f"较完整节点约 {f(201326592/431244, 2)} 倍缩小"],
        ["4 个 SLUT v1 文件", "448,252 B = 0.427 MiB", "含头、网格与权威轴表；不能只报节点"],
        ["CPU 准备后模型", f"{cpu_run['model_runtime_bytes']:,} B = {mib(cpu_run['model_runtime_bytes'])} MiB", "含节点展开与运行时辅助表"],
        ["GPU 模型 device allocation", f"{gpu_run['model_device_bytes']:,} B = {mib(gpu_run['model_device_bytes'])} MiB", "按当前运行时精确计数"],
        ["CPU16 batch 图像", "输入225 MiB + 工作副本225 MiB", "batch 吞吐模式；非单张最小内存"],
        ["CUDA 显式图像缓冲峰值", "450 MiB", "输入/输出两份，传输与驻留缓冲分时复用"],
        ["CPU16 / CUDA 主机峰值工作集", f"{mib(peak_cpu)} / {mib(peak_gpu_host)} MiB", "7 次进程 OS peak 的中位数，含框架、图像等"],
    ], [172, 170, CONTENT - 342], small=True)
    add("显式 GPU 缓冲计数不等于 nvidia-smi 设备总占用或峰值显存；后者含驱动/上下文，本轮未做可靠采样。主机 CPU 百分比为整个子进程采样 CPU 时间，100% 对应一个逻辑 CPU，既不是映射阶段利用率也不是 GPU 利用率。")
    heading("工程优势与实际缺口")
    add("运行时可使用独立 C++17 构建，Python 仅承担离线拟合与验证；CUDA、Zig/Rust 等后端按需启用。全色域训练动态库使用稳定 C ABI，并完成 OpenMP/AVX2 关闭配置在真实矩阵上的一致性验证。缓存原子发布与源码/数据哈希降低混用模型风险。")
    add("尚未覆盖 ARM/NEON、Android/iOS、真实嵌入式功耗、跨编译器性能和正式 Intel 服务器。R27 仍需离线扫描完整 LUT；嵌入式部署应在资源充足的主机离线生成模型，采用单图/小批缓冲，不能把本报告 450 MiB 批次模式直接当作端侧最低内存。", "small")

    # 11. Scoring.
    section("10 三个评分项的证据化评估")
    table([
        ["官方分项", "当前可证明的竞争力", "未满足的计分前提 / 评估"],
        ["A 正确性与精度\n40 分", "输入合同、四级整数执行、CPU/CUDA 一致性完整；9 个源存在通过本地 mean<2 的合法 m", "官方阈值和粒度未知；3 个固定配置仍失败；max 仍高。不能认领40分。正式数据到位后优先复验"],
        ["B 执行速度\n40 分", "100 图批量：CPU16 86.864 ms、CUDA 67.757 ms；当前 OCIO4 路径7/7配对较慢", "未在统一服务器测试，没有各队最短耗时和官方计时边界，不能认领满分或按比例算出确定分数"],
        ["C 架构与算法创新\n20 分", "精确阶梯识别、可达网格、全色域整数组装、SIMD/CUDA、可选依赖与可复现证据", "具备较强工程证据；ARM/移动端、功耗和官方工程评审未做，无法客观转换为具体分数"],
    ], [92, 202, CONTENT - 294])
    heading("当前判断")
    add("A 项的主要风险已经从压力家族平均误差过高，转为未知官方口径与剩余离群误差。若官方偏向整图平均，本地证据较有利；若采用严格像素最大值，本地结果仍明确不足。")
    add("B 项具备本机吞吐优势，但最优后端必须随目标硬件重新确定。本报告没有据 CUDA 驻留 kernel 或 AMD 成绩为 Intel 服务器估分。")
    add("C 项具有可审查的算法与代码实现，并有依赖关闭配置的功能证据；实现的新意和架构可行性有支撑，最终评分仍属于评委判断。")
    add("因此本报告不给出臆测的总分或“预计满分”。这不是把未测项目记成零分，而是区分已完成测试、示例达标和官方计分三种不同事实。", "body")

    # 12. Reproduction.
    section("11 复现、冻结版本与待办")
    add("工作目录：F:/Hackathon/projects/16-lut-color。Git 基点 de4571d6a17cdc5e1dca0076217ff11d4f568c33；报告使用未提交的 R27 源码快照，不依赖分支名称识别模型。")
    table([
        ["证据文件（相对仓库根）", "作用"],
        ["artifacts/r27-step/study.json", "13组拟合、路由证明、复用边界、全色域与图片验收"],
        ["artifacts/r27-step/mapping-comparison.json", "7对CPU16/CUDA含传输性能、预检字节及主机工作集"],
        ["artifacts/r27-step/industry/comparison.json", "OCIO全色精度、100图实际输出和7对4线程性能"],
        ["report/data/r27/r27-evidence.zip", "可审阅的源码/JSON/日志/SLUT归档；不含大体积原始图像与完整LUT"],
        ["report/latest/latest-tested-accuracy.csv", "本报告13行精度数据，保持原始浮点数"],
    ], [300, CONTENT - 300], small=True)
    heading("当前执行文件指纹（SHA256 前16位）")
    table([["组件", "指纹"],
        ["CPU jshc.exe", accepted["backends"]["cpu"]["executable_sha256"][:16]],
        ["CUDA jshc_gpu.exe", accepted["backends"]["cuda"]["executable_sha256"][:16]],
        ["原生全色域训练库 ABI 1", study["trainer"]["library_sha256"][:16]],
        ["R27 step.py", study["source_sha256"]["python/lutlab/step.py"][:16]],
    ], [220, CONTENT - 220])
    add("拟合入口：python -m lutlab fit --scenario stress-13 --inputs <四张完整LUT> --m 33 --method adaptive_full --grid dp。先配置 PYTHONPATH=python;artifacts/r18-tools/python，以及 JSHC_FULL_FIT_LIB 指向 build-fit/libjshc_full_fit.dll。", "small")
    add("统一验收入口为 python -m lutlab accept，性能复现脚本为 scripts/compare_accepted_runtime.py 和 scripts/r27_industry_study.py。运行时与输入必须符合记录的 SHA256；移植或更改输入后，应另存结果并重测，不能沿用原分数。", "small")
    heading("下一阶段")
    add("先处理量化边界附近的最大误差，并保持四级独立语义；收到官方数据后确认 LUT 格式、Threshold 粒度与计时边界，在统一服务器复验全部图片。后续硬件优化应保持同一模型输出，先集中正确性阶段，再做少量预声明的性能配对。")

    # 13. References and traceability.
    section("12 数据来源与参考资料")
    add("本地数据优先于摘要取值。所有最新数值从 JSON 读取，PDF 生成不触发新的数值测试。外部信息核查日期：2026-10-15；只把可直接支持相关事实的官方文档、作者仓库与论文作为依据。", "small")
    refs = [
        ("外1", "OpenColorIO 2.6 官方发布说明", "https://opencolorio.readthedocs.io/en/v2.6.0/releases/ocio_2_6.html"),
        ("外2", "OpenColorIO 2.6 插值枚举与 API", "https://opencolorio.readthedocs.io/en/v2.6.0/api/enums.html"),
        ("外3", "AdaInt，CVPR 2022；作者源码", "https://github.com/ImCharlesY/AdaInt"),
        ("外4", "SVDLUT 作者论文 v1：Table 3/7 与实验设置", "https://arxiv.org/html/2508.16121v1"),
        ("外5", "SVDLUT 作者官方实现，ICCV 2025", "https://github.com/WontaeaeKim/SVDLUT"),
        ("外6", "LoopLUT，2026-09-27 预印本", "https://arxiv.org/abs/2609.33593"),
    ]
    for identifier, title, url in refs:
        add(f"[{identifier}] <b>{escape(title)}</b><br/><link href='{escape(url)}' color='#087F8C'>{escape(url)}</link>", "small")
    heading("本地证据链")
    add("题面：PROBLEM.md 与用户截图。R20 修复实际图像执行验收；R22 证明可分离曲线；R23 缩短 CUDA bench 缓冲寿命；R25 引入全色域整数法方程及容量测试；R26 箱约束方法多数案例回归，未替换主线；R27 对阶梯与可达节点作精确处理。历史结果均按阶段归档，没有用未经复验的旧模型速度充当 R27 成绩。", "small")
    manifests = [("R27 研究", ART / "study.json"), ("CPU/CUDA 配对", ART / "mapping-comparison.json"),
        ("OCIO 配对", ART / "industry/comparison.json")]
    for label, path in manifests:
        add(f"{label} SHA256：<br/>{sha(path)}", "small")
    add("报告中 B、KiB、MiB、GiB 按二进制换算；ms 为毫秒。所有置信区间限于本机配对样本。官方正确性、评分与行业排名仍未判定。", "small")

    output = OUT / "problem16-latest-tested-report.pdf"
    doc = Report(str(output), pagesize=A4, leftMargin=44, rightMargin=44, topMargin=58, bottomMargin=51,
        title="第16题 极速焕彩：最新已测 R27 技术报告", author="项目技术评估", subject="精度、性能、内存、评分与开源方案对比")
    doc.addPageTemplates(PageTemplate(id="main", frames=[Frame(44, 51, CONTENT, HEIGHT - 109,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=page))
    doc.build(story)
    with (OUT / "latest-tested-accuracy.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(csvrows[0]))
        writer.writeheader()
        writer.writerows(csvrows)
    manifest = {"pdf": str(output), "bytes": output.stat().st_size, "sha256": sha(output),
        "evidence_sha256": {str(path.relative_to(ROOT)): sha(path) for _, path in manifests},
        "source": str(Path(__file__).relative_to(ROOT)), "source_sha256": sha(__file__),
        "official_score_available": False, "version": "R27", "pages_expected": 13}
    (OUT / "report-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
