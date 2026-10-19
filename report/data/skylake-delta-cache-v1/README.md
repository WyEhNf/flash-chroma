# 已有缓存与同缓存加无损差值编码的直接比较

[阶段说明](../../../docs/stages/2026-10-20-skylake-delta-cache.md)解释参考选择、实现、环境、整数验证、性能波动和未完成项。参考已有缓存，候选只加入无损坐标差；不乘算此前独立百分比。

`cached-reference-object-check.json`及`reference-object-proof.zip`证明参考两个对象与早先已验缓存候选逐字节相同。`configuration-integrity.json`只读复核全部16个计时配置确实启用同容量缓存，候选布局为`[2,1,1,1]`。`assembly.zip`包含所有同形全命中循环、完整汇编/MCA日志、分析源与调用控制器，模拟不代表实测。

`contract-*`为55+6原合同；`layout-contract-*`为88组差值合同和32条诊断；`cache-contract-*`为77组组合交互及其绑定的前三份合同，包含原55组缓存、24000槽证明；新交互两库各25400合法槽独立uint64一致。`prior-cache-fixtures.zip`补存既有原缓存合同夹具，`cache-contract-fixtures.zip`为新交互夹具，不重新生成。`full-results.json`保留实际模型的完整色域、100图及171056槽、命中覆盖。

`performance-worker0..3.json`为唯一80轮原始结果；`performance-results.json`与`gate-recalculation.json`分别给出配对统计和不调用原生库的门槛复算。相对已有缓存，1/4线程apply耗时中位下降21.1454%/22.5320%，预设本机门槛通过。第一个进程参考明显更慢、准备+首组的一个四线程配对回退14.7968%，完整保留，不删样本或补计时。

源码/库/依赖/计划/实际配置按SHA绑定；模型复用PR42冻结模型。无重新拟合、默认变更或Skylake结果。现有服务器传输包针对此前无缓存差值实验，本档案不声称组合后端已完成Linux或服务器验收。
