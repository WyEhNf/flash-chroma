# 自由 cell 方向的收益与接缝限制

[阶段报告](../../../docs/stages/2026-10-24-velvia-cell-diagonals.md)解释局部可行性、冻结选择、完整域/百图改善与真实接缝退化。

`probe-results.json`含四方向内 max 下界及每项独立均值下界；`cell-statistics.npz`为完整32768 cell、四方向的五指标与max；`results.json`是唯一训练mean最优方向场的独立重算和百图验收。`regressions.csv`保留全部逐图退化，`error-ratios.csv`列旧/新具体误差比，不是官方得分。

`exact-faces.json`保存每面九点反例，`rgb8-boundaries.json`保存实际跨界相邻RGB8输入的完整跳变统计。聚合mean/p99/max改善，但17,954面采样不连续，面max跳32.0624，不能称作连续可用插值。没有原生或速度验收。

`cell-orientation.bin`为32768B实际byte数组，`baseline-model.zip`保持原3e5f节点/坐标；新表示仍需原分输出坐标侧表及未来新运行时。`source.zip`与manifest保存测量源码/全部证据SHA。完整RGB流仅本地离线证据。
