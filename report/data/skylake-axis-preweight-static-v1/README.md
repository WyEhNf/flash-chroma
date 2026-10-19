# 共享轴预计算的静态停止与后续结构剖面

[阶段说明](../../../docs/stages/2026-10-20-skylake-axis-preweight-static.md)解释可逆编码、真实环境、成本、未执行范围和下一方案。修订10只构建/反汇编/MCA，未加载或通过有限整数、完整域、百图输出、性能；不进入默认或已验服务器矩阵。

`analysis-results.json`保存两类完整优化循环：乘法44→38、gather不变，周期估计和吞吐下界反而变差。`analysis-decision.json`停止，不扫描变体。`analysis.zip`保留全部原始汇编、每处MCA及分析程序。`build-*`与`built-not-executed.zip`保存冻结源码、实际库/对象和参考字节相等证明。

`eligibility-and-proposal.json`是修正后的三个m33模型资格记录；`initial-invalid-grid-length.json`保留最初把3×m误读为边长3的无效草稿，其错误未进入模型或运行测试。静态计划绑定修正版本。

`skylake-cell-affine-*`、`skylake-uniform-suffix-*`和`skylake-structure-profile-v1-results.json`保留固定a399及已见100图的完整结构统计：整包局部仿射约8.88%，首级后整包同色约16.03%。后者方案只提出，修订11尚未实现。统计复用既有首级流，不是新内核正确性或时间收益，不进行独立精度宣称；源码和原始输入身份均保留。
