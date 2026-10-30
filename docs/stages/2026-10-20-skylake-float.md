# 精确binary32四权重：保持字节一致，未获本机加速

Agent：Codex；Operator：WyEhNf；Task：Skylake时间优化的第三个独立候选；Status：Completed（负结果保留，整体优化继续）。

本候选将项目已有`channel_exact_float`的精确四权重思路适配分输出坐标，并显式采用平衡加法树。仍用原32位轴表、原节点/几何与逐级RGB8；不混入56位打包或16位乘加，不修改公共默认。

四个权重为`65536-high, high-middle, middle-low, low`，均为非负整数且总和65536。节点为RGB8，因此任意乘积及任意部分和≤16711680，加入32768后≤16744448，小于2²⁴。所有中间整数均能被binary32精确表示，最后`cvttps(sum+32768)>>16`严格复现Q16 half-up。这不适用于差分浮点表达式、更高位深或不合法的权重。

编译仅AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`，不启用FMA、fast-math或全局march；实际候选AVX2对象的FMA指令数为0。静态对象中整数乘法减少，但增加大量int/float转换；不能按指令条数推断速度。完全无侧表的链仍走原公共TetraAvx2，该候选只改变extended路径。

## 一次验证与性能比较

目的为算术字节等价及时间收益。环境：Windows11 26200 x64、Ryzen9 8945HX、32GB；Python3.12.14、NumPy1.26.4、Numba0.60.0；GCC15.2 Release `-O3 -DNDEBUG`、AVX2/OpenMP。Numba4、BLAS/MKL/OMP环境1；正确性标量1和AVX2请求1/4，性能固定同L3域物理核0/2/4/6。实际两主库、4个GCC依赖及SHA分别核验。

55组有限整数合同及6条非法侧表拒绝通过；冻结同一a399模型的单级/实际四级完整256³，两库标量1及AVX2请求4均与独立uint64/既有完整流逐字节一致；100图逐图和整组SHA复现。模型准备容量仍1058292字节，新拟合0次，精度不变。

性能在完整正确性通过后唯一执行：4个串行新进程AB/BA/BA/AB、1/4线程顺序平衡，每配置5轮完整100图。输入预载235929600字节，逐项预热核全部输出；apply和copy+apply分列，排除IO/解码/模型准备/统计。

| 请求线程 | apply配对比中位数 | 时间变化 | copy+apply配对比中位数 |
| --- | ---: | ---: | ---: |
| 1 | 1.127005480 | 增加12.7005% | 1.132827132 |
| 4 | 1.123300697 | 增加12.3301% | 1.117133286 |

预冻结门槛仍为两个线程数apply≤0.97、任一进程≤1.02、copy+apply≤1；未通过，不采用，不追加同候选计时或放宽门槛。每进程先取5轮中位、计算同进程比值后再取四进程中位，没有跨候选拼绝对时间。未锁频/控温，摊销不是单图延迟；AMD结果不能改称Skylake结果。

## 交付与下一步

源码在`experiments/skylake-float-runtime`，共用新候选CMake骨架`experiments/skylake-common.cmake`。输入计划和性能计划分别为`experiments/skylake-float-v1.json`、`skylake-float-perf-v1.json`。统一builder按计划项目/目标构建，检查ISA和浮点选项；其余验证入口与前两个候选相同，使用对应plan/build/contract/full/performance目录。目录拒绝覆盖，具体命令记录在归档run/build日志中。

实际源码、两库/依赖/核心、完整字节验收、80原轮次、汇编及门槛复算见[原始证据](../../report/data/skylake-float-v1/README.md)。Linux/Skylake尚未执行；已确认本机有WSL2 Ubuntu，可用于后续Linux构建和ABI核验，不能充当Skylake服务器。

三个指令级候选均不足以替换本机基线。接下来优先研究有界精确后缀缓存，尝试消除后三阶段重复计算，而不继续在这些失败候选上扫编译参数。任何缓存都须显式披露准备时间、额外内存和未命中回退；官方许可及服务器成绩仍待确认。
