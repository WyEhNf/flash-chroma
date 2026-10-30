# Filmic06：补偿整数节点的坐标误差

Agent：Codex；Operator：WyEhNf；本地阶段完成，未提交、推送或创建PR。

本阶段承接PR41的明确反例：Filmic06完全可分离，但固定几何轴和整数节点仍留下非零误差。先按同一3DL解释重建完整参考及17³/33³结构DP模型，三个历史SHA全部匹配，避免换弱基线。

新增separable_calibration.py解析每个码值的half-up精确Q16区间，在原frac±4096、静态相邻中点区间及固定首尾内选最小输出误差；RGB8节点、idx和float32网格字节不变。run_filmic_calibration.py提供独立prepare/accept入口，计划为experiments/filmic-calibration-v1.json，没有改通用拟合器或内核。

33³仅修改15个frac、最大偏移313，完整256³与100图的mean/RMS/p99/max全部为0。17³修改27个、最大偏移298，全域mean从0.114535154降至0.011691964，百图mean从0.125110668降至0.011658709，最差单图p99从1.414214降至1；所有逐图指标不退化，但全域p99/max未降。

17³剩下每轴input134：精确frac上限3640，静态下界3641。此结果只能证明本轮静态区间挡住精确值，不能称固定节点本身无解。后续直接单调阶段另立计划，不把其结果回写为本阶段成功。

测试目的为来源复现、解析整数契约与完整精度/执行一致性，非性能比较。Windows11 26200、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、Numba0.60.0；Numba4线程、BLAS/MKL/OMP=1，既有GCC15.2 Release程序各1线程。一次集中合同后，仅对两固定候选一次完整验收：四模型全域Numba/u64 oracle/闭式曲线相同，五个实际单级后端共20份完整流回执0差异；两个新模型额外AVX2映射百图核SHA。

[精简报告与证据](../../report/data/filmic-calibration-v1/README.md)包含模型、源快照、400条逐图记录和完整回执。large reference及像素流留在本地artifacts，SHA随归档。原始SLUT字节审计确认除frac外全部字节相同。

这是同源合同下严格可分离Filmic06的单级特例。坐标政策改变不等于Q16算术bug修复，也不代表一般三维LUT或四级链归零；官方数据/Threshold未知，不升级默认、不作性能或官方通过宣称。相关提交暂未创建，由根代理统一整合。
