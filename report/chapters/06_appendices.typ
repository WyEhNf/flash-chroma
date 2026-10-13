#import "../helpers.typ": meta, csvtable

= 原始数据附录与审计线索

正文引用的当前扫描固定为运行 #meta.selected_run_id，源提交 #meta.source_git_commit，独立日志提交 #meta.logs_git_commit。这两个提交的用途不同：前者确定生成报告时的代码，后者确定已冻结的运行记录。共有 #meta.run_count 次运行，失败 #meta.failed_run_count 次；其失败状态也收录，不将其改写成成功。`report/data/` 的归档保留原字节和相对路径，CSV 只是便于检索的派生视图。当前 24 候选产生 #meta.image_row_count 条逐图行、#meta.hotspot_row_count 条最坏颜色行。表格显示小数经过舍入；做阈值复核应使用原始 `selection.json`。

== 附录 A：当前 24 候选完整表

门禁为 `isp-0`、29 张图、每图平均 ΔE 严格小于本地示例值 2.0。`ineligible_composite` 表示数值精度合格但规则未确认，速度栏缺失；`fail_accuracy` 的速度栏同样缺失。完整浮点精度、29 张逐图结果、模型哈希和全色最坏 RGB 值分别在原始 `selection.json`、`image_results.csv` 与 `cube_hotspots.csv`。

#csvtable("generated/candidate_results.csv", (0.4fr, 1.0fr, 1.25fr, 0.75fr, 0.8fr, 0.8fr, 0.75fr, 0.75fr, 0.9fr, 0.8fr), size: 5.5pt, inset: 2.4pt)

== 附录 B：历史六场景的 10 图代理对照

`route_sweep.json` 按场景与 m 对比朴素四面体、整数最小二乘、四级残差和单级复合。它使用当时的 Python 代理、每场景 10 张图，不与附录 A 的当前门禁数值合并排名。单级复合仍有规则风险；`stress-0` 的误差高是当前算法族的重要能力边界。

#csvtable("generated/historic_scenarios.csv", (1.1fr, 0.45fr, 1fr, 1fr, 1fr, 1fr), size: 7pt)

== 附录 C：可移植 Zig 的完整 36 组扫描

本表来自 `37f9fba6`，每格是 100 张图、3 轮中的*最佳整组*毫秒，适合看候选范围而不宜做微小差异的最终排序。固定配置的 7 轮中位复测见正文图及 `generated/zig_repeat.csv`。默认内核后来改为 16 lane；这里宽度 8 和 16 使用当时的显式 ABI 符号。

#csvtable("generated/zig_sweep.csv", (0.8fr, 0.7fr, 1fr, 1.4fr, 1.4fr), size: 7pt)

== 附录 D：原始归档与 SHA-256

#table(
  columns: (2fr, 4fr),
  table.header([文件], [SHA-256]),
  [`run_records_exact.tar.gz`], [#text(size: 6pt)[#meta.artifact_sha256.at("run_records_exact.tar.gz")]],
  [`manifests_exact.tar.gz`], [#text(size: 6pt)[#meta.artifact_sha256.at("manifests_exact.tar.gz")]],
  [`experiments_exact.tar.gz`], [#text(size: 6pt)[#meta.artifact_sha256.at("experiments_exact.tar.gz")]],
  [`ledger.csv`], [#text(size: 6pt)[#meta.artifact_sha256.at("ledger.csv")]],
  [`image_results.csv`], [#text(size: 6pt)[#meta.artifact_sha256.at("image_results.csv")]],
  [`cube_hotspots.csv`], [#text(size: 6pt)[#meta.artifact_sha256.at("cube_hotspots.csv")]],
)

历史 `experiments/route_sweep.json` 的独立 SHA-256 是 #meta.route_sweep_sha256。精确归档不包含被 Git 忽略的约 1.8 GiB 图像/LUT，也不等于官方比赛数据。文档级路径说明见 `data/DATA_INDEX.md`。

== 附录 E：Git 探索时间线

保留原始提交标题以查找实现、失败、修复和门禁的出现时间。提交日期与运行 UTC 时间不是同一口径；报告文稿本身在数据基准提交之后完成。

#csvtable("generated/git_history.csv", (0.9fr, 0.9fr, 4.8fr), size: 6.5pt)

== 附录 F：全部独立运行台账

按运行 UTC 开始时间列出全部 #meta.run_count 条。此表包含一次审计后测试失败以及后来修复成功的记录。完整 `params_json`、分支、脏状态和代码 SHA 在 `data/ledger.csv`；原始 stdout、差异和指标在 `run_records_exact.tar.gz`。

#csvtable("generated/ledger_print.csv", (1.5fr, 0.85fr, 1.7fr, 0.55fr, 1.1fr, 0.45fr), size: 6pt, inset: 2.5pt)
