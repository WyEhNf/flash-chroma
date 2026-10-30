# 坐标与节点局部性停止证据

[阶段说明](../../../docs/stages/2026-10-20-skylake-coordinate-locality.md)记录测试目的、实际Windows/AMD环境、全部资格条件与限制。本轮零新运行库、零原生像素/性能调用。

`coordinate-reuse-results.json`保存固定100图逐像素/八像素组的排序覆盖；67.89%逐像素不能替代34.09%整组覆盖。`endpoint-counterexamples.json`列出完整九表中两个不满足共享ONE条件的轴/码及全部三个错误数学展开值，未称为现有运行时bug。

`node-layout-results.json`保留仅首级节点的B连续/R连续访问行数，含全部逐图及16种自然对齐偏移；逐块只改善约1%，未达10%条件。行并集不是LRU、miss、PMU或时间。

`server-tuning-plan.json`、`server-tuning-results.json`及`server-tuning-complete.zip`保存一次两个对象编译、全部日志/反汇编/函数/循环清单；两对象逐字节相同，精确复现旧参考4。没有新库加载、MCA或性能比较。

`source-and-small-inputs.zip`保存原字节源码、冻结与归档脚本、原包含响应文件、固定模型/侧表/照片清单；不重复收录原235MB像素流。`decision.json`汇总四项拒绝依据与零新增运行调用，未修改历史失败、默认或服务器资格。
