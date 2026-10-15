# 极速焕彩：中文 Typst 探索报告

最新已完成测试版本另见[R27技术评估PDF](../output/pdf/problem16-latest-tested-report.pdf)，覆盖题目指标、三个评分项、OpenColorIO实测与开源论文对照。它由`scripts/build_latest_tested_pdf.py`读取已冻结的R27 JSON生成；依赖ReportLab及Windows等线字体，不会触发数值重测。数据与指纹在`output/pdf/`，可恢复证据见[data/r27](data/r27/README.md)。下文是保留的历史探索报告说明。

主文件为 `exploration.typ`，交付 PDF 为 `exploration.pdf`。正文从题面和首个 Git 提交讲起，按阶段记录算法、失败路线、工程审计、当前 24 候选严格门禁、Zig 性能调参、选题判断和团队复现流程。`generated/` 包含由日志生成的 Typst 表格与图；`data/` 包含原始运行记录归档、数据清单归档、逐图 CSV、最坏颜色 CSV 和完整台账。

这是基于 `codex/zig-default-pixi` 分支和独立实验日志冻结的报告，随 Codeberg 默认 `main` 一起提供阅读。`main` 保留较早的实现；需要复现实验或更新数值时先切到该实验分支，并取回 `experiment-logs` 日志分支。

在项目根目录、代码与独立日志固定后运行：

```bash
pixi run python scripts/build_typst_data.py
pixi run --manifest-path report/pixi.toml compile
pdfinfo report/exploration.pdf
```

报告专用 `report/pixi.toml` 安装 Typst 和 Noto CJK 字体，不改变算法环境。生成器固定读取本轮主扫描 `52e23c0b`、36 组 Zig 扫描 `37f9fba6` 和 7 轮复测 `20bb8ce1`；若开展新一轮官方实验，须修改脚本中的固定运行 ID 并重新生成报告，避免混淆口径。
编译任务固定 PDF 创建时间为 2026-10-13 00:00 UTC，以便重复编译时得到相同文件哈希。

`data/run_records_exact.tar.gz` 按原始字节和相对路径保存本地 `logs/runs/` 的 JSON、stdout、测试日志和差异；`data/manifests_exact.tar.gz` 保存清单，`data/experiments_exact.tar.gz` 保存历史实验 JSON。约 1.8 GiB 的图像和 LUT 本体仍由主仓库忽略，报告不复制。原始数据索引和 SHA-256 见 `data/DATA_INDEX.md`。
