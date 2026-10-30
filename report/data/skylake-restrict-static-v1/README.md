# 不重叠读取域候选的静态停止证据

[阶段说明](../../../docs/stages/2026-10-20-skylake-restrict-static.md)记录目的、算法前提、实际环境、全部两族结果与未执行范围。修订12仅构建/反汇编/MCA，未加载或调用候选，不进入默认或已验服务器包。

`analysis-results.json`和`analysis.zip`保留两条完整固定四级循环及全部原始汇编/MCA：指令575/570→529/519，含rsp操作数41/38→70/66，建模周期分别改善2.224%/5.477%，吞吐下界都略差。`decision.json`按测试前两族均至少3%的条件停止，不继续扫描别名变体。

`plan.json`、`proposal.json`及`build-*`保存方案、冻结源码和构建参数；`built-not-executed.zip`保存实际库及相关对象；`reference-object-proof.json`确认参考两个对象与历史修订5完全相同。新增域诊断、拒绝检查、可选辅助资源分支均未执行；预计四级新增568字节尚非运行核算。静态推导不替代正确性或Skylake实测。
