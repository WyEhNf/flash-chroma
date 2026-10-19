# 按阶段遍历像素块的原始证据

同模型完整字节验证通过；1/4线程apply配对中位耗时下降6.1047%/3.2690%，但一个4线程进程退化8.6293%，违反预冻结稳健性门槛，**不采用**。准备后模型容量保持1058292字节，没有派生缓存；栈/RSS不在该容量中。[阶段说明](../../../docs/stages/2026-10-20-skylake-stage-major.md)列出目的、环境、方法和限制。

保留同次两库/依赖/核心、源码快照、55组合同与6条拒绝、单级/四级完整256³、100图输出身份、四进程80轮次及门槛复算。`assembly.zip`保存完整汇编，`build-static-mca.zip`保存提取的热循环与MCA完整输出；静态建模不代表实测周期。

复现使用`plan.json`/源码ZIP和对应build/contract/full/performance新目录，命令沿用`scripts/build_skylake_runtime.py`、`verify_skylake_packed.py`、`accept_skylake_runtime.py`、`bench_skylake_runtime.py`，输入模型复用PR #42。不得用另一阶段或另一系统的库/SHA替换记录，也不能把本机AMD结果当成Skylake或Linux成绩。没有因归档重跑数值或计时。
