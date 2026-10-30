# cap1600、双mean优先的独立失败记录

[阶段报告](../../../docs/stages/2026-10-24-velvia-mean-first.md)解释为何移除RMS硬约束仍不保证成功，以及真实原3e5f比较。

`run.json/summary.json`冻结单轮52提案和三预算；`fit-evidence.zip`保存完整支撑每批轨迹，manifest另记原progress SHA；`contract.json`含±1/2及0/255节点边界独立u64合同；`observations.json`为两个失败末节点额外分块研究前向的RMS/p99/CVaR，不是独立oracle终验。

mean仍比原3e5f高约1.32%，尽管RMS/max/CVaR改善、p99count守住，最终拒绝。没有照片/后拟合边界/native/performance、无默认升级，未改写旧五预算证据。`research-model.zip`只供研究复现；`source.zip`/manifest保存实际源与全部证据SHA。
