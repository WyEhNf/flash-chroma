# 固定κ3两cell的完整质量证据

代理 `/root/tail`；操作者为当前会话用户。仅原3e5f的cell31725/31726使用mask1、κ3边界归零混合，节点/轴/其他cell保持不变；历史100图只验不调。本阶段是新插值表示研究，题面许可未知。

`run.json`绑定输入SHA、实际环境、冻结计划和数值源码SHA；`baseline-model.npz`和`candidate.json`使模型/表示可恢复。`cube.json`、`results.json`保留完整域与全部逐图指标，`photo-ratios.csv`列500项误差比，`photo-regressions.csv`无退化行。`faces.json`保存6,094,848真实分输出Q16面截面零差；`adjacency.json`保存全部50,135,040 RGB8相邻对及跨idx子集，包含局部跳变退化。

全域mean0.886672865143→0.886487398719、p99不变、max√1682→√1604，双mean保护通过。100图mean/RMS/CVaR各2好98平，p99全平、max1好99平。实际R/G轴原始输出最大相邻跳变分别12.1655→13.0384、39→41.0488；C0不能掩盖这些局部代价。

新鲜Numba完整16M逐色与独立uint64混合oracle一致，612修改支撑另逐色Python整数核Q32；100图新鲜Numba与完整流零差。完整50MB流留在artifacts，SHA为`f38217d6ab471f58cc794eee23ab02317f4df2d86b0a00eab4f520e2b4ba3875`。未实现原生/测性能/实测容量，不切默认。

`source.zip`是实际源码快照，`manifest.json`绑定10份原件及源码成员哈希。阶段说明与复现命令见[阶段文档](../../../docs/stages/2026-10-24-velvia-bubble-accept.md)。
