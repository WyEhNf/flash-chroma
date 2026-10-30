# 56位轴表候选的完整证据

本候选整数正确性通过，但未达本机预冻结性能门槛，未采用。环境、目的、方法与限制见[阶段说明](../../../docs/stages/2026-10-20-skylake-packed.md)。

- `plan.json`和各`*-run.json`绑定来源、参数及源码；`*-measured-source.zip`保持各执行阶段实际源码。
- `contract-results.json`为55组有限整数合同与6条非法输入拒绝；`full-results.json`为冻结a399模型的单级/四级完整256³和百图字节等价。精度复用同输出的PR42结果，不新增拟合。
- `performance-worker0..3.json`为四进程原轮次，`performance-results.json`为汇总，`gate-recalculation.json`独立复算并保留未达门槛结果。没有为归档重跑像素或计时。
- `build-topology.json`记录同L3域4个物理核的实际选择；`build-assembly-audit.json`是整个AVX2对象的静态计数，包含fallback和ABI保存，不是每像素周期。
- `binaries-and-core.zip`保留两主库、4个GCC依赖和同一静态核心；模型复用PR42中的`report/data/cinema-current-anchor-accept-v1/models.zip`，具体路径/SHA见计划。

`manifest.json`逐项记录原字节长度和SHA。未取得Skylake服务器结果；不得将AMD本机结果改名为服务器验收。
