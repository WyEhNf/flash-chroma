# 固定四级AVX2专门化：同一a399模型的后端验收

Agent：Codex；Operator：WyEhNf；状态：唯一候选构建、44组集中合同、完整native等价和固定性能门禁均通过；仅本地归档，未PR/push，默认不变。

本阶段只改变内核的编译期共享分派和四级循环展开。对照与候选均为a399首级+933a/95cb/932f后三模型、同一sidecar和原100张1024×768 RGB8；对照库7ceb30d…，候选库507b51a…。原v3、CMake、标量壳和核心未修改。没有新拟合、数据、权重或参数扫描，没有使用已失败reuse源码。

完整256³单级及实际四级的标量1/AVX2请求4与已验独立整数oracle流零差，100图输出SHA逐图一致。本阶段不重新选择精度，复用先前已完整验收的同一模型；精度证据见[原报告](../cinema-current-anchor-accept-v1/README.md)。模型只引用[原models.zip](../cinema-current-anchor-accept-v1/models.zip)，SHA `07bce54753726adfc707c1efea6bffb9ce6947f77f6b636d64372359cc530284`，本包不重复。

4个新进程串行AB/BA/BA/AB，线程顺序[1,4]/[4,1]/[1,4]/[4,1]，每配置5次完整100图，预加载235929600字节并逐配置预热/核SHA。apply与copy+apply分列，排除模型加载、文件IO、图像解码/编码和hash。两种比值都先算每进程5轮中位数之比，再取四进程比值中位数；不能用两端汇总中位数相除。

| 请求线程 | apply时间下降 | apply配对比 | copy+apply时间下降 | copy+apply配对比 |
|---|---:|---:|---:|---:|
| 1 | 10.704820% | 0.892951798503 | 10.541961% | 0.894580387217 |
| 4 | 7.764286% | 0.922357137578 | 6.974270% | 0.930257303044 |

原门槛为1/4线程apply配对比均≤0.97、任何进程≤1.02、copy+apply配对比≤1，全部通过，见`gate-audit.json`。`performance.csv`列绝对摊销统计和进程范围，`process-pairs.csv`列各进程配对中位数，`raw-rounds.csv`保留80个原轮次；全部原worker JSON/日志另在`evidence.zip`。这里时间下降率不是吞吐提升率。

环境：Windows11 26200 x64、Ryzen9 8945HX 16c32t/32GB，MinGW GCC15.2.0 Release -O3 -DNDEBUG、C++17/OpenMP；仅AVX2 TU带-mavx2，dispatcher保持baseline ISA；Python3.12.14/NumPy1.26.4/Pillow10.4。OMP_DYNAMIC=FALSE，BLAS/MKL/OMP环境1，原生显式请求1或4线程。新主DLL及共用4依赖的实际已载路径/SHA保存于run/worker；旧主DLL按冻结完整路径加载和SHA绑定，未额外枚举旧主模块路径。

`evidence.zip`收录构建、44合同、完整native及性能的全部run/results/worker轮次/日志和源码ZIP、冻结计划、合成合同输入；`binaries-and-core.zip`收录两主DLL、4依赖及实际链接静态核心，各有原始SHA。独立builder及其源码ZIP可复现本候选，不依赖修改公共CMake。`manifest.json`校验本包原字节，`commands.txt`区分历史测量命令与本次只读归档命令。归档脚本只重算旧回执，没有新native、像素、性能或拟合调用。

未锁频/控温/绑核，四进程范围不是置信区间；100图摊销ms/图不是单图延迟或尾延迟。上一阶段v3新表示相对af974约慢46%的结论仍只属于那组不同模型配对；本轮不能跨阶段用绝对耗时或乘比值推算相对af974的最终速度。没有后续硬件变体，未推广公共CLI/GUI/C99或默认，实验sidecar不是官方已认可格式。四张创意LUT只作数值串联，色彩域匹配未证明，无官方数据/Threshold或官方分数。
