# 有界拟合与四级联合选择证据

阶段方案和数值源代码先冻结于 `58fb26d`，完整说明见[阶段报告](../../../docs/stages/2026-10-17-joint-box-objective.md)。本目录保留新的独立研究身份，不改写上阶段证据或冠军。

- `plan.json`、`run.json`：冻结计划、原始运行身份、实际CPU/系统/依赖/线程/源码/二进制指纹。
- `results.json`、`fit-diagnostics.csv`：三个案例的完整指标、收敛/KKT、连续有界目标与IRLS诊断；不把连续目标当成RGB8精度证明。
- `candidate-guard.csv`：264个组合的选择指标、退化字段及是否入选；全部测度门禁拒绝了两个单级的新候选，Cinema选中四级联合方案。
- `case-summary.csv`：完整色域与100图摘要，显式区分复用基线和本轮实际展开的赢家。
- `photos-per-image.csv`、`photo-split-summary.csv`：600条逐图及18条60/20/20分组摘要。照片全部曾被历史研究观察，审计仅不参与本轮训练/选择，不称盲测。
- `photo-max-counterexamples.json`：四张训练图的max回归、RGB与字节哈希、像素位置和逐级轨迹；没有只公布总体收益。
- `native-parity.json`：3条本轮Cinema全色域原生回执、7条历史同字节基线回执。原始 `results.json` 中 `reused_baseline` 字段保留完整旧回执列表；本文件只筛选其中 `variant=baseline` 的实际复用项，不将旧候选算成本轮验收。
- `models-and-selection.zip`、`archive-index.json`：41个成员，含32个SLUT模型及9个案例JSON；逐文件SHA-256可核对。模型继续采用SLUT v1、m33、原始Q16轴表。
- `photo-partition.json`、`sample-hashes.json`：固定分组、每张训练/选择照片采样索引哈希、颜色输入哈希。
- `guard-measures.png`：选择集两个mean的散点图；图中不显示的尾部约束同样参与选择，不能只凭散点判定通过。
- `contract.log`、`experiment.log`、`integrity.json`：3项针对性合同、单批原始日志、来源及归档完整性。NumPy可选PyYAML警告保留原样。

Cinema全色域mean/max从2.022233/9.848858降至1.282465/9.273618，100图mean从1.759132降至1.037166；四张图的单图max上升。Lomo/Velvia保留基线，不宣称解决全部尾部或官方达标。未做性能扫描、硬件优化或默认方法替换。

## 复现与模型使用

拟合命令、实际环境和已知限制见阶段报告。研究入口从上一阶段忽略目录比对原始基线SLUT；如果只检出仓库，可按 `report/data/chain-error-v1/archive-index.json` 核对上一阶段ZIP，提取各case的 `baseline-stage*.slut` 至 `artifacts/chain-error-study-v1/<case>/`。该步骤只恢复已版本化的模型字节，不需要恢复完整旧RGB输出或重跑旧100图。数值缓存可以重新构造，环境变化必须使用新输出目录；当前实验严格复用旧程序身份，其他程序需先重新建立基线正确性证据。

无需重新拟合即可检查、使用本轮Cinema赢家：从ZIP提取 `cinema-chain2/selected-stage1.slut` 至 `selected-stage4.slut`，按此顺序交给已有 `lutlab.runtime.apply` 或 `cube`。换用其他合法构建时，可以用 `runtime.cube` 重新产生完整流，与本目录记录的输出SHA `a0831ed4be35753bdf3c48ae11fff2f2bd355f7c77b8673a7fa042a940a658e8` 比较；新的执行环境和二进制回执另存，不冒充本轮测试。

归档结果由 `scripts/report_joint_box_study.py` 从冻结输出整理。重新生成报告会核对所有实测源文件的原始字节，源文件不同则拒绝；若在Git提交后换行转换导致历史依赖字节不同，应使用对应测量源及新身份，不能改写本目录旧run。

Agent：Codex

Operator：WyEhNf

Task：联合优化与误差分析证据

Status：阶段归档完成，候选待审查
