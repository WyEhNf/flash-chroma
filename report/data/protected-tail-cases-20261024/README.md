# 普通四级与 Velvia 单级的完整支撑验证

[阶段报告](../../../docs/stages/2026-10-24-protected-tail-cases.md)列出起点、逐级 RGB8 语义、完整域/百图结果、逐图代价与尚未完成的速度门禁。

`cinema_shared` 与 `velvia` 分别包含冻结训练输入/策略、训练汇总、87 库的独立 uint64/标量/AVX2 完整域及百图验收、完整模型 ZIP。普通案例是 af974 共享坐标的四张 SLUT，无侧表；Velvia 是 3e5f 分输出坐标单级研究表示，不能互换许可或性能结论。

`summary.json`汇总两案；`regressions.csv`逐项保留所有回顾照片退化，尤其普通链 0877 mean 从 1.222872 增至 1.937969。两案 max 都未降，Velvia p99 也未降。没有默认切换，没有受控速度结论。

`fit-evidence.zip`保存各案唯一八批完整支撑训练记录；`source.zip`是本阶段实际执行源码快照；`manifest.json`保存源与证据 SHA。完整 50 MB RGB 流仅在本地 artifacts，未被当作稀疏模型；模型 ZIP 内也不包含完整真值/直表。

复现命令见阶段报告。`scripts/audit_tail_git_evidence.py`逐 Git blob 验 manifest，再独立验源码 ZIP 的原始字节，不重新运行像素或计时。
