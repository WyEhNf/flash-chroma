# 固定m33网格误差研究证据

阶段报告：[网格位置与拟合误差](../../../docs/stages/2026-10-17-tail-grid.md)。数值执行Git为`eb854e1`，两例×三方案共一次集中批次，6个新模型完整验收；2个历史基线从PR13同字节证据复用。没有重选赢家、更换默认或开展性能扫描。

- `plan.json`：执行前冻结计划；`environment.json`：实际Windows/Python/依赖/CPU/线程、完整拟合库及运行时SHA。
- `results.json`：完整256³/100图、390152边界色、top128、旧三点证书、局部舍入前/后输出、拟合KKT与矩阵行审计。
- `case-summary.csv`：8条汇总；`photos-per-image.csv`：800条逐图，600新执行、200复用。
- `photo-regressions.json`：分别相对历史和整数对照的逐图改善/持平/退化，以及各指标最大退化图。
- `native-parity.json`：六模型各标量/AVX2完整流与独立整数oracle一致，12回执。未在C99四级CLI或实板运行这些单级模型。
- `new-hotspot-certificates.json`：后验固定半径1/2/4/8三点必要下界；包含全部检查，未反馈拟合，0不等于可精确表示。
- `models-grid-and-costs.zip`、`archive-index.json`：8个SLUT、实际整数/历史浮点网格、三轴完整切线及整数弦代价、DP决策、冻结模型诊断，共30成员。
- `measured-source.zip`、`source-provenance.json`：17文件实测原字节，逐一绑定run身份，另记归档器SHA；`experiment.log`保留实际控制台。
- `counterexample-lines.png`：从已保存完整流绘制旧反例切线，已目视检查；`integrity.json`保存生成时所有证据哈希与数量。README及后续CI说明不冒充原数值输出。

复现见阶段报告。入口拒绝已有输出；归档器需同名旁置`.log`。可从ZIP恢复模型核查，不需要把约300MB完整输出流提交到Git；重建全流须使用锁定源素材和执行源码。完整表与流暂存在本地忽略缓存，路径保留于来源记录。

所有误差均为RGB欧氏码值距离。完整色域、边界、逐图、最差单图p99分别命名，不能混用；官方数据/Threshold未知。新网格减少部分尾部，却使照片mean普遍退化，全部失败事实保留，不能称总体通过、SOTA或未知LUT泛化。

Agent：Codex

Operator：WyEhNf

Task：固定容量网格位置与拟合目标的误差归因

Status：集中实验及归档完成，研究候选未替换默认，Draft待审查
