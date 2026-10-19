# 首级/后缀单边界拆分的原始证据

完整字节一致；1线程apply中位耗时下降4.3414%，4线程配对中位增加0.3322%、最差进程增加5.9418%，预冻结性能门槛失败，**不采用**。模型容量仍1058292字节，没有派生表。[阶段说明](../../../docs/stages/2026-10-20-skylake-prefix-split.md)列出目的、环境、统计口径与限制。

档案保留冻结源码/计划、同次两库/依赖/核心、55组合同与6条拒绝、单级/四级完整256³、100图逐图身份、四进程80轮次与门槛复算。`assembly.zip`为完整objdump，`build-static-mca.zip`为提取热循环和MCA原始输出；日志只在ZIP内保存以保留原始行尾空格，模拟不替代硬件时间。

复现使用源码ZIP保留的原始字节及新build/contract/full/performance目录，统一入口为`scripts/build_skylake_runtime.py`、`verify_skylake_packed.py`、`accept_skylake_runtime.py`、`bench_skylake_runtime.py`，分别绑定本阶段计划与构建身份。输入复用PR #42冻结模型，不恢复旧计时冒充新环境；本机AMD结果不代表Skylake、Linux或官方通过。
