# 时间性能优化：四个候选的阶段交付

Agent：Codex；Operator：WyEhNf；Task：以Skylake服务器为最终目标，在本机推进时间优化；Status：In Progress（首批四候选完成，服务器与规则验收继续待办，整体目标未结束）。

当前有一项明确的本机收益：对固定Cinema四级稀疏模型，用有容量上限的精确后缀缓存，1线程和4线程的apply耗时均下降约52%。输出保持逐字节一致，准备后容量增加约0.743MB。这个结果还不能当作Skylake成绩，也不能直接进入正式比赛默认：服务器尚未取得，题目是否允许新增这种派生缓存仍需确认。

## 这一阶段做了什么

先确认实际机器是Windows11 / Ryzen9 8945HX / 32GB，编译器为MinGW GCC15.2。AVX2翻译单元使用`-mavx2 -mtune=skylake -ffp-contract=off`，不把AVX512、FMA、fast-math或全局march作为前提；标量与CPU/OS检测仍保持通用指令。

四个候选按不同假设分别冻结、分别验收。没有通过反复计时筛好看的结果，也没有把失败的改动混进成功候选。

| 候选、提交与说明 | 1线程apply时间变化 | 4线程apply时间变化 | 结论 |
| --- | ---: | ---: | --- |
| [56位轴表打包](2026-10-20-skylake-packed.md)，`86a6722` | −2.67% | −1.10% | 未达门槛，且一个进程退化11.88%；不采用 |
| [精确16位乘加](2026-10-20-skylake-madd.md)，`3a23394` | +10.16% | +11.26% | 正确但更慢，不采用 |
| [精确binary32四权重](2026-10-20-skylake-float.md)，`67a332f` | +12.70% | +12.33% | 正确但更慢，不采用 |
| [有界精确后缀缓存](2026-10-20-skylake-suffix-cache.md)，`93b67cb` | −52.36% | −52.28% | 通过本机预设门槛，保留为显式研究候选 |

各行只与自己同一次构建的参考库比较，百分比取同进程配对比后再聚合；不跨阶段拼接绝对时间，也不与PR #42历史未绑核时间相除推导收益。

缓存用当前三个稀疏后缀逐级RGB8生成精确表，绝不使用完整源LUT代替稀疏链。范围由首级节点及固定2码余量决定，u32表上限1MiB，不使用照片调范围。8像素全部经过界限检查才查表，否则整包精确回退。实际表742400字节、准备后总容量1800836字节，原参考1058292字节；临时准备缓冲556800字节，创建后释放。这些是容量核算，不是RSS。

实际全色域和百图全部命中，不能外推到任意LUT。计时进程内建表约5.023..6.349ms，含加载/哈希的候选创建约10.602..14.238ms。“创建+首个已预热100图copy+apply”的配对比为1线程0.49067、4线程0.58313，明确计入准备成本，仍不是冷启动端到端或单图尾延迟。

## 验证分别证明什么

数值正确性与性能分开进行。四候选各有55组布局/长度合同与6条非法侧表拒绝，之后才对同一a399模型进行一次单级/四级完整256³及100图字节比较。缓存另有55组命中/回退合同、24000个合成槽和171056个实际合法槽的独立uint64核验、14544个非法槽隔离及只读ABI失败保护。

每个候选性能只执行一次固定方案：四个串行新进程AB/BA/BA/AB，1/4线程顺序平衡，每配置5轮完整100图；固定同L3域四个物理核的逻辑CPU0/2/4/6。原生apply与copy+apply分列，输入235929600字节预载，不含IO/解码/拟合/统计。没有锁频或控温。原始轮次、实际动态库/依赖SHA、亲和性、准备成本和失败门槛均归档。

缓存候选还完成Linux构建及运行：同一AMD主机的WSL2 Ubuntu / Linux6.18.33.2 / GCC15.2.0-16ubuntu1 / CMake4.2.3 / Python3.14.4。标准库验证入口无需NumPy/Numba，完成528个有限后端/偏移比较及两库单级/四级、标量1和AVX2请求1/4共12组完整色域字节比较。预期来自已核验的独立uint64/完整流；没有在Linux重算独立oracle或做照片性能，不能当成Skylake验收。

输出保持不变，因此复用PR #42的同输出误差结果，不重新拟合：完整色域RGB欧氏mean 0.981110596723、p99 3.74165738677、max约8.1240384；百图mean 0.810320558604。距离不是CIEDE2000，百图是已见数据，官方数据与Threshold仍未取得。

## 协作意见与交付边界

本次fetch后main仍`da5ed25`，PR #42头仍`59586f7`，均已被本分支包含。PR #42尚未合并，因此当前工作以`codex/joint-grid-precision-20261018`为base提出依赖草稿PR，避免重复显示其26个既有提交。提交不改写，未直接推主干，也不执行merge。

创建前通过REST/GraphQL逐页获取全部36个PR、2个独立issue、2个Discussion，以及110组评论/review/行内记录，相关审查线程为0，Discussion #4没有评论。阅读关联正文和完整意见，并在操作前刷新。原始快照和包含关系见[协作核对](../../report/data/skylake-runtime-delivery-v1/remote-check.json)。

| 原始记录 | 核对结果与本阶段处理 |
| --- | --- |
| [PR #9基线/环境两项P2](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[issue #7内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7) | 修复337a3dd为当前祖先；相关实现相对PR #42未改变，历史验证见[#37最终验收](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。本阶段每个构建/环境分别绑定，不复用旧计时冒充新环境 |
| [PR #27保护](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)、[PR #29相等mean](https://github.com/WyEhNf/flash-chroma/pull/29) | 876e15b8、397cc367实际包含；本阶段完全固定模型，以字节一致性保持所有既有精度与逐图代价，不放宽门槛 |
| [PR #41](https://github.com/WyEhNf/flash-chroma/pull/41)、[#39](https://github.com/WyEhNf/flash-chroma/pull/39) | 推进冻结模型后的运行成本比较；没有把其它机器或Numba时间拼成新加速比；两个PR继续独立 |
| [Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)、[#5素材意见](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072) | 区分实现正确性和模型误差，保存来源/哈希；没有新增全面压力扫描，四张创意LUT只证明数值串联，不称真实ISP或已验证色彩域兼容 |
| [issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)、[GUI #40](https://github.com/WyEhNf/flash-chroma/pull/40) | 公共接口迁移、实板资源与GUI仍独立待办；本阶段新库只在显式experiments入口运行，不代替这些验收 |

四份原始档案分别为[轴表](../../report/data/skylake-packed-v1/README.md)、[16位乘加](../../report/data/skylake-madd-v1/README.md)、[binary32](../../report/data/skylake-float-v1/README.md)、[精确缓存](../../report/data/skylake-suffix-cache-v1/README.md)。builder、有限合同、完整验收、平衡benchmark和归档入口统一复用；每阶段源码ZIP保留原始换行字节，跨系统复现不混淆Git文本归一化和SHA身份。

交付整理只执行档案/Git blob原字节、链接、语法和包含关系的静态检查，回执见[静态核对](../../report/data/skylake-runtime-delivery-v1/static-check.json)。没有借提交再跑像素核、拟合、单元或性能测试；静态结果不能替代全仓CI。AGENTS.md、默认模型、冠军、公共CLI/GUI/C99均未改。

## 接下来优先做什么

继续研究不新增派生查色表的热点优化，避免把比赛提速全部押在尚待许可的缓存上。先根据源码和汇编找出足够大的计算/读取成本，再冻结候选集中验证，有明确理由才做性能比较；不继续为前三个失败候选扫参数。

最终服务器需先记录具体Skylake型号、客户端或SP、操作系统、编译器、缓存/NUMA、微码与GDS状态，再用同一冻结模型完成正确性、1/4线程及完整100图比较，并披露准备、额外内存和计时范围。不关闭安全缓解，不把AMD/WSL结果写成服务器成绩。整体优化目标继续，当前PR保持Draft，官方格式/缓存许可、Threshold和服务器结果保持未完成。

## 后续三项检查与候选

PR #43初版提交后继续了三项独立研究，未对前四候选补计时：

| 后续对象 | 证据与结果 | 决定 |
| --- | --- | --- |
| [描述符快照](2026-10-20-skylake-snapshot.md)，`ec92b6f` | 指令减少7.39%，栈访存增加92.11%；MCA信号不一致 | 静态阶段停止，没有像素/正确性/性能测试 |
| [逐级遍历块](2026-10-20-skylake-stage-major.md)，`5414793` | 同模型完整字节一致，1/4线程apply配对中位下降6.10%/3.27%，但一个4线程进程退化8.63% | 按原稳健性门槛拒绝，`5d35f77`仅去除ZIP外重复MCA日志，原字节保留 |
| [首级/后缀只拆一次](2026-10-20-skylake-prefix-split.md)，`f9327d7` | 同模型完整字节一致，1线程下降4.34%，4线程配对中位增加0.33%，最差进程增加5.94% | 拒绝，停止融合切点、块大小和线程变体搜索 |

两个进入运行验证的后续候选仍各只有一次55组合同、完整256³/百图和四进程80轮次；模型/准备容量不变，保留全部失败和波动。MCA仅是静态潜力判断，不是Skylake实测，更不能覆盖4线程失败。首级拆分例子还显示聚合绝对时间中位之比与同进程配对比中位可给出不同方向，结论始终使用预定的后者。

更新PR前完整刷新37个PR、2个独立issue、2个Discussion及113组REST意见，并检查审查线程/分页，相关正文与意见的变化另存[后续核对](../../report/data/skylake-followup-delivery-v1/remote-check.json)；新增档案和Git blob/链接的静态回执见[后续静态检查](../../report/data/skylake-followup-delivery-v1/static-check.json)。初版`94f6a7b`的六项CI均成功，新头CI以实际检查结果为准，不能用初版状态替代。

另外检查普通四级路径，发现`cpp/src/lut_simd_avx2.cpp::chain_impl`已经显式展开四次共享插值，因此不重复实现或为相同假设再跑benchmark。接下来检查编译器生成的SIMD代码与寄存器分配，并准备可直接在最终服务器执行的冻结模型、环境记录和性能入口。目标服务器和官方许可仍未取得，整体目标继续，Draft不合并。
