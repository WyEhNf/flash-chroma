# Velvia 全局体对角线质量探针

[阶段报告](../../../docs/stages/2026-10-24-velvia-body-diagonals.md)解释几何、整数语义、完整测试覆盖和拒绝依据。`run.json`冻结当前 3e5f 最佳输入及四方向预算，`contract.json`为 17/33 八方向独立物理 u64/重参数化和互补方向验证，`results.json`保存完整域/百图合并与所有逐图统计。

mask1/2 的完整域 max 有下降，但 mean/p99 大幅退化；mask4 的 max 也恶化。三种新方向全部拒绝，未切换默认，未做原生或性能验收。反向 idx 不满足现有非降坐标合同，不能将研究核结果称作合法普通 SLUT 或已可移植模型。

`baseline-model.zip`是原最佳 NPZ，`source.zip`是实际测量源码，`archive-source.py`仅作静态归档；`manifest.json`含精简文件与全部完整流 SHA。四个完整 RGB 流只在本地 artifacts，不是新增模型查表；没有额外运行内存或速度结论。
