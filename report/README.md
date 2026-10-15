# 冻结报告与重建

本目录保存历史中文 Typst 探索报告、原始证据归档和生成表格。当前使用方法与构建入口见根目录 [README](../README.md)、[TOOLCHAIN](../TOOLCHAIN.md)；本报告中的历史分支名、默认后端和构建状态不再作为开发指南。

## 阅读与查证

- [R27 已测版本 PDF](../output/pdf/problem16-latest-tested-report.pdf)：较新的固定阶段技术评估。
- [历史探索报告](exploration.pdf)：由 `exploration.typ` 与 `chapters/` 组成的冻结报告。
- [数据索引](data/DATA_INDEX.md)：运行记录、逐图数据、最坏颜色与 SHA-256。
- [R17–R27 技术文档索引](../docs/README.md)。

这些报告描述特定代码、模型、数据与硬件。官方 LUT、阈值和服务器仍需按实际任务确认；历史“通过”与速度数字不能推断当前机器或正式比赛成绩。

## 编译历史 Typst 报告

已有 `generated/` 和 `data/` 随仓库保存。仅重新排版时，在项目根目录运行：

```bash
pixi install --locked --manifest-path report/pixi.toml
pixi run --locked --manifest-path report/pixi.toml compile
```

报告使用独立的 Typst 与 Noto CJK 字体环境，支持 Linux/Windows，不安装主数值环境或 macOS 包。任务固定 PDF 创建时间为 2026-10-13 00:00 UTC；不要把重编译误认为重新验证了实验数值。

## 重新生成历史表格和图片

`scripts/build_typst_data.py` 固定读取日志 ID `52e23c0b`、`37f9fba6`、`20bb8ce1`。需要先取得对应独立日志，见 [日志说明](../docs/LOGGING.md)，再运行：

```bash
pixi run --locked -e plots python scripts/build_typst_data.py
```

该命令会更新冻结报告的数据与图，并非日常测试步骤。开展新实验时应明确新记录与原报告的区别，不能把不同时期的数据拼成同一次测量。

## 其他历史生成器

`scripts/build_latest_tested_pdf.py` 依赖 ReportLab、原始 `artifacts/r27-step/` 证据和 Windows 等线字体绝对路径。它目前是历史机器上的生成脚本，未纳入 Linux 的一键报告构建；阅读仓库中的现成 PDF 不需要这些依赖。

`data/` 中的归档按原始字节与相对路径保存证据。大体积图像和 LUT 不全部随仓库分发；归档和文档不能替代缺失的实验输入。此次构建清理不重新生成 PDF，也不修改冻结数据或归档哈希。
