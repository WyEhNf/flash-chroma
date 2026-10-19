# 首级同色后缀快路的完整静态停止证据

[阶段说明](../../../docs/stages/2026-10-20-skylake-uniform-suffix-static.md)说明确定性原理、每级RGB8、实际Windows/AMD环境、全部路径及停止依据。候选修订11只构建/反汇编/MCA，未加载、没有新像素/正确性/性能结果。

`analysis-summary.json`及`decision.json`保留普通路径、216条同色排序路径的范围和固定16.03%剖面的潜力筛选。实际35-gather族普通包周期估计增加10.26%，最乐观混合仍增加约4.24%，不进入运行阶段。线性混合不是真实硬件性能，不把原九表族套上a399覆盖率。

`path-analysis.zip`保存全部436条路径的原始结果、每条MCA源/日志、完整汇编、分析源、初步清点及第一次入口假设拒绝。基本块反馈锚点覆盖所有简单环，不只取一个入口或较好排序。`initial-inspector-refusal.json`解释修正检查器而未改候选/重编译的过程。

`build-*`、`built-not-executed.zip`、`reference-object-proof.json`和`initial-design.json`保存计划、原字节源码、实际库/对象、参考与既有修订5相等证明及测试前实现决策。不新增颜色表或修改模型，不升级默认或已验服务器包；新内核若将来进入目标硬件仍需完整整数及性能验收。
