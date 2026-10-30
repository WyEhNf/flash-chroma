# 精确调色板编译：相对修订16的吞吐提升

Agent：Codex；Operator：WyEhNf；Task：在精度不变的前提下继续优化，直到相对当前已验修订16的吞吐至少提高50%；Status：Completed（本机固定模型研究与验证完成；以Draft交付，Skylake实机性能和官方适用性待验收）。

本机唯一一次冻结比较达到目标：修订22相对修订16，1线程apply吞吐提高 **84.99%**，4线程提高 **90.62%**；copy+apply分别提高 **79.46%/66.71%**。完整256³及100图输出逐字节相同。收益来自对当前稀疏链的无损预编译，不改变节点、坐标、舍入或拟合。四级句柄容量由1,800,836增至10,190,548字节，额外8,389,712字节；它是显式研究库，尚未替换公共默认。

本地开始于`e3975ea`，fetch后main仍为`b19c5a0`，已包含。参考直接使用PR #43中较快的[获证修订16](2026-10-20-skylake-domain-proof.md)，没有用早期无缓存版本代替。PR #44的五项静态停止完整保留；本阶段另起`codex/skylake-projection-20261020`，依赖其分支交付。提交以本阶段PR的实际头为准；所有数值还绑定下列源码、模型与二进制SHA。

## 原理与适用范围

先只读分析旧完整域输出及缓存：R、RG、RB投影的完整8像素包可用比例仅约4.6%–5.3%，没有进入新像素实现。精确游程的64项索引估算约9.49MB；随后采用固定8输入块的u32编码。完整最终输出有221种颜色，但运行时可直接取得的原后缀缓存含230种值（包括未使用槽的零值），因此实际构造器使用排序后的230项调色板，不能偷用已知完整输出流的221项。

类似[PNG indexed-colour](https://www.w3.org/TR/png/)的索引思想，调色板保存原始RGB值，不进行颜色量化。具体块编码是本阶段的精确部分求值：

1. 仅在四级链首级非共享、后三共享、完整域证书已通过、CPU/OS支持AVX2时尝试准备。原四个稀疏模型、原Q16/逐级RGB8和原后缀缓存继续保留。
2. 排序去重原缓存值，超过255项就直接保留修订16路径。本阶段固定拒绝样例实际6249项，已验证此分支。调色板ID 255专用于哨兵。
3. 构造器生成全部RGB8输入，调用当前原16路径得到标签；不读取完整源LUT、照片、旧cube预测或验收oracle。准备使用4线程，即使以后以1线程映射也如此。
4. 按`R<<16 | G<<8 | B`排序，每8个连续B码构成一个u32。低8位存块内最小调色板ID，后24位存八个3bit非负ID差。ID跨度大于7时写255哨兵，完整表固定2,097,152个u32，即8MiB。
5. 每次AVX2处理8个图像像素：先gather各自的块；全部可编码时，移位解码后再gather调色板并直接写回。任一lane为哨兵，整包内联执行原16计算。尾部和显式标量入口仍执行原四级整数路径。

实际1,962,299块可编码，占93.57%；134,853块回退。100图中任一lane回退的包占21.42%，这是事前剖面的描述，不是按照片选择范围或计时筛选参数。快包两次gather；回退包需先查块再执行原路径，不能把全部输入都称为两次gather。原型22仅这一个参数方案进入性能比较，没有扫描块宽、ID排序或缓存容量。

这不是任意LUT均有同等加速的算法保证。模型变化时重新建表，调色板过大、布局不符或证书不成立就回退；分配失败捕获`bad_alloc`并保留原路径，但未做分配失败注入。官方题面同时允许等价计算优化、要求每步在m³稀疏空间完成，因此派生颜色表/侧表的许可与预算必须由出题方确认，不能把本研究写成已获正式参赛资格。

## 性能结果与代价

环境为Windows11 26200 x64 / Ryzen9 8945HX（16核32线程），MinGW GCC15.2、Python3.12.14、NumPy1.26.4、Pillow10.4、psutil5.9。Release `-O3 -DNDEBUG`，仅AVX2翻译单元使用`-mavx2 -mtune=skylake -ffp-contract=off`；没有全局march、FMA、AVX512或fast-math。完整编译命令、实际加载库与依赖SHA在[档案](../../report/data/skylake-palette-v1/README.md)中。

冻结策略为四个串行新进程AB/BA/BA/AB，1/4线程顺序平衡，每配置5轮完整100图，共80轮。固定同L3域四个物理核的逻辑CPU0/2/4/6，未锁频控温。图片固定1024×768 RGB8，预载235,929,600字节，映射就地执行；计时不含IO、解码、拟合、分配及SHA。每次CABI repeats=1，在计时外核对该轮完整100图输出SHA。所有80轮保留，无重测、删轮或重排。

每进程先取5轮中位，再计算候选/参考，最后取四个配对比值的中位。下表绝对时间是各进程中位再取中位，仅便于理解；不能以两个绝对中位相除替代配对统计。

| 线程 | apply毫秒/图，16→22 | 配对耗时比 | 耗时下降 | 吞吐提高 | copy+apply配对耗时比／吞吐提高 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 5.81809→3.13744 | 0.540567 | 45.94% | 84.99% | 0.557230／79.46% |
| 4 | 1.63621→0.86902 | 0.524597 | 47.54% | 90.62% | 0.599850／66.71% |

预先门槛是两档apply和copy+apply中位比均≤2/3、任何apply进程比≤0.9、准备加首个已预热100图的copy+apply中位比≤1，全部通过。apply四个进程比：1线程0.55205/0.52756/0.53578/0.54535；4线程0.66127/0.49477/0.43176/0.55442。[标准库独立复算](../../report/data/skylake-palette-v1/audit/results.json)核对输入、实际修订16/22、库SHA、80轮输出、资源和配对公式，没有新增计时。

容量核算由真实句柄读取，包含原模型/侧表/表容量，不是RSS：

| 项目 | 修订16 | 修订22 |
| --- | ---: | ---: |
| 单级句柄 | 271,707 | 272,811 |
| 四级句柄 | 1,800,836 | 10,190,548 |
| 编译块表 | 0 | 8,388,608 |
| 新句柄元数据及256项调色板 | 0 | 1,104 |

构造期间RGB临时流、24bit反查、去重工作向量及新块表的容量合计76,239,872字节；该值包含最终8MiB表，不是进程峰值RSS，也没有包含调用者图像与整个解释器。构造结束释放临时流。原生单级也多1,104字节元数据，表未启用。

基准记录的句柄准备墙钟约由12.75–16.27ms增至69.80–97.88ms。**准备＋首个已预热100图copy+apply**配对中位：1线程0.661516、4线程0.921113。4线程四个进程分别为1.06206/1.05197/0.79026/0.74694，前两个更慢；不能称启动收益也达到50%。该派生指标把准备时间加到已预热首轮，不包含中间预热成本，因此也不是冷启动端到端或单图尾延迟。

## 精度、合同与可移植性

所有比较使用同一a399冻结链和原三后缀。没有重新拟合、改色差公式、放宽门槛或改变单级输出量化。

| 验证目的 | 实际覆盖与结果 |
| --- | --- |
| 原布局/非法输入合同 | 55组基础、6条非法侧表；55组后缀缓存、24,000合成槽，通过 |
| 完整域证书及诊断 | 8状态、24条失败不写；实际32³单元全部获证，通过 |
| 新编码独立重建 | 读取2,097,152词，独立旧oracle重建全部词、16,777,216颜色及所有哨兵；55种快/回退/混合/端点/长度配置、1,320次两库后端/偏移比较和8条诊断负例，零差 |
| 其他网格和正负斜率 | m17/18/25/33，48组×8,203像素的独立整数比较，零差 |
| 大调色板精确回退 | 6249项、完整域证书成立但不建表，18组×4,105像素、标量/AVX2及偏移哨兵，零差 |
| Windows实际完整输出 | 两库×单级/四级×标量1/AVX2请求4共8组完整256³，100张逐图及合并SHA全部相同 |
| Linux适配 | 同AMD的WSL2 Ubuntu / Linux6.18.33.2 / GCC15.2.0 / Python3.14.4标准库，528次有限比较及两库单级/四级×标量1、AVX2请求1/4共12组完整256³，零差；确认新编译表实际启用 |
| ISA及回退对象 | Win/Linux原16和4的AVX2对象在各自新构建中均与参考逐字节相同；新Win内核328条函数指令、零外部调用；仅AVX2，无高寄存器/FMA/AVX512 |

单级完整输出SHA为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`，四级为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，100图合并为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。

字节相同保证本阶段没有精度下降。既有模型的完整域RGB欧氏mean 0.981110596723、p99 3.74165738677、max约8.1240384及100图mean 0.810320558604继续适用；不是新拟合或CIEDE2000成绩，照片为已见数据，官方Threshold仍未知。

Windows首次完整验收已完成计算，却在销毁句柄后读取诊断时失败，没有生成成功回执；只修复验证器的生命周期，再做完整v2验收后才允许唯一性能实验。另一次大调色板补验在构造fixture时误用三轴grid，数值比较前失败，修复验证器后v2通过。两次失败的run、源ZIP和说明均保留；C++、模型、性能计划及已测二进制没有修改。validation-v1/v2/v3保留各次工具身份，不回写历史SHA。packed验证器曾将`__file__`绝对路径记入源清单，归档审计显式映射实际ZIP成员，不改旧回执。

## 复现与交付

主要实现为`experiments/skylake-palette-runtime`；构建、有限/完整验证、独立性能复算与归档审计分别位于`scripts/*skylake_palette*.py`。完整原始证据、小模型、源快照、对象/二进制及失败保存在[研究档案](../../report/data/skylake-palette-v1/README.md)。112份原始证据约5.4MB，不把235MB图片流及两个50MB完整域流放进Git；大流通过已有[服务器包](../../report/data/skylake-domain-server-v2/README.md)按SHA恢复。源ZIP按测量原字节恢复后构建，避免Git换行变更被误当成算法变化。

Linux本次实际命令如下，复现应选择新的输出目录：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-palette-v1.json --output artifacts/skylake-palette-linux-build-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
python3 scripts/verify_skylake_palette_linux.py --plan experiments/skylake-palette-v1.json --build artifacts/skylake-palette-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-palette-linux-full-v1 --affinity-cpus 0,2,4,6
```

Windows使用研究venv和`--compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator 'MinGW Makefiles'`构建。完整合同入口参数与输入SHA见各run.json；性能实际入口为`python scripts/bench_skylake_palette.py --policy experiments/skylake-palette-perf-v1.json --output artifacts/skylake-palette-perf-v1`，输出目录必须新建。该策略绑定本次Windows的构建与完整验收；移机不能改旧回执或直接套其SHA，应先在目标环境完成验证，再冻结新的构建身份、CPU集合与性能策略。

创建PR前检查全部38个PR、2个独立issue、2个Discussion与116组REST评论/review/行内记录，GraphQL线程0，分页完整。相对前轮最终刷新，相关意见无变化；PR #44正文新增第五项静态停止，头仍e3975ea。[协作回执](../../report/data/skylake-palette-v1/remote-check.json)记录完整快照与祖先关系：337a3dd基线/环境/内核绑定、876e15b8保护、397cc367相等mean修复均实际包含，公共相关实现未变，历史集成证据仍见[#37](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。[#42](https://github.com/WyEhNf/flash-chroma/pull/42)精度、[#43](https://github.com/WyEhNf/flash-chroma/pull/43)运行时、[#44](https://github.com/WyEhNf/flash-chroma/pull/44)失败研究分别保留，不乘算收益。

[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)的实现/模型误差区分继续落实；[#8](https://github.com/WyEhNf/flash-chroma/issues/8)接口迁移/实板、GUI #40仍独立待办。没有发现新增且未披露的相关阻塞意见；保持Draft，不合并、不关闭issue。归档独立审计已核对112个清单文件、13份源快照、711项源成员SHA，见[回执](../../report/data/skylake-palette-v1/archive-audit.json)。普通全仓CI不能替代这里的新实验库数值和性能证据。

实际Skylake性能未执行。AVX2指令边界与Linux构建/输出兼容已验证，但8MiB新表的缓存占用、gather的微码/GDS影响、NUMA与服务器频率可能改变收益。目标端需要固定真实SKU/OS/编译器/核集合和缓解状态，以相同模型分别测准备、apply、copy+apply和首组；本机85%/91%不能直接写成服务器收益。官方缓存/侧表许可、预算与Threshold继续待确认。
