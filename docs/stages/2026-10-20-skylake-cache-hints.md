# 修订38—42：精确缓存访问与300%吞吐研究

Agent：Codex；Operator：WyEhNf；Task：精度不降、当前吞吐达到300%；Status：In Progress。

本阶段的新输出接口已有单项超过3倍的本机结果，整体目标仍未完成。40真实source→destination接口的1/4线程配对吞吐为修订23的3.0559倍／3.8973倍，41为3.0942倍／4.3711倍；相同候选的纯映射尚未同时达到3倍。所有候选的`accepted_on_this_host=false`。公共模型、默认实现和已验23保持原样。

本阶段基于`acaf2b2fea95151a7b35e2d5158b6e236d2d47fd`，衔接[上一阶段](2026-10-20-skylake-load-packing.md)与[Draft PR #48](https://github.com/WyEhNf/flash-chroma/pull/48)。本阶段提交号由交付元数据记录；具体源、构建、动态库与计时源码的完整SHA均在[证据目录](../../report/data/skylake-cache-hints-v1/README.md)，不以分支名代替测量身份。

## 本阶段改动及取舍

| 修订 | 主要实现目录 | 固定研究变更 | 处理结论 |
| --- | --- | --- | --- |
| 38 | `experiments/skylake-sourcehint-runtime` | 在37上只增加输入NTA提示；初始最多1024字节，每64像素前瞻1024字节，覆盖未来192字节 | 保留直接证据，没有扫描距离 |
| 39 | `experiments/skylake-tablehint-runtime` | 独立从37出发，对下一组64像素的全部ID地址做T0预取；不叠加38输入提示 | 指令及周期增加，停止该固定全量预取方案 |
| 40 | `experiments/skylake-batchspan-runtime` | 在38上将运行时块从4096扩大为65536像素，摊薄对齐前缀、NTA启动和SFENCE | 新接口两种线程数均超过3倍，纯映射继续研究 |
| 41 | `experiments/skylake-skew-runtime` | 独立从38出发，地址`h=c^(c>>10)`，逆变换`c=h^(h>>10)^(h>>20)` | 四线程墙钟比值较低，但计数未支持稳定周期收益，暂不与40拼接 |
| 42 | `experiments/skylake-wordload-runtime` | 在40上，以8MiB原23主词的普通GPR加载替换16MiB字节索引；精确向量解码后读取原例外池及调色板 | 容量减少，解码与例外成本过高，停止扩展 |

38—41使用16MiB精确u8 ID表及原230项调色板，句柄计量28,046,644字节；42新主词为8MiB，句柄19,658,036字节；参考23为11,269,404字节。42保留原主词副本用于既有诊断和回退，没有宣称句柄仅8MiB。所有表只由原四个稀疏模型及逐级RGB8规则构造，构造器不读取照片、完整源LUT或gold流；模型磁盘格式不变。

41只是可逆地址排列。独立位段解码核验全部16M颜色，缓存行号映射也逐项核对为双射，2MiB页分组不变。[几何检查](../../report/data/skylake-cache-hints-v1/skylake-skew-geometry-v1/results.json)显示，在常规低位组索引模型中，固定R/G、遍历B的256条访问可分散到更多私有缓存组。这是地址模型分析；实际CPU可能有索引哈希，不能把该模型当作缓存未命中实测。

各版本继续按64字节对齐输出，先读完64像素再写192字节，使用完整缓存行的AVX2非临时存储；在普通尾部、返回及OpenMP barrier前SFENCE。输入额外读取和提示地址均限制在当前线程块内。40/42的65536块会减少小图像的可并行块数，其性能结论只覆盖本次固定输入；没有小图性能保证。其他形状继续精确回退。

## 实际环境和判定口径

实际为Ryzen9 8945HX、Windows11宿主、WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库。原生共享库为Release，AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`，未使用FMA、AVX512、native或fast-math。用户确认服务器型号未知，按通用AVX2继续。没有实际Skylake验证，没有锁频控温；不能从本机结果承诺服务器同幅提速。

四个串行新进程按AB/BA/BA/AB比较，每进程两种线程数、每配置5轮，每轮100张固定1024×768 RGB8图。主线程固定CPU0；`OMP_PLACES={0},{2},{4},{6}`、`OMP_PROC_BIND=TRUE`、`OMP_DYNAMIC=FALSE`；逐TID允许CPU和团队顺序在前后均核验。运行时大页必须在实际`smaps`中完整覆盖，提示成功本身不足以通过。

每个候选分别对同场23计算四个“候选进程中位耗时／参考进程中位耗时”，再取四个比值的中位数。下表均为耗时比，越低越好；吞吐倍数为该比值的倒数，不能把不同实验收益相乘，也不能跨Windows/Linux比较绝对时间。

| 修订 | 纯映射1线程 | 纯映射4线程 | 旧copy+apply 1线程 | 旧copy+apply 4线程 | 真实输出1线程 | 真实输出4线程 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 38 | 0.378885 | 0.518298 | 0.482725 | 0.727589 | 0.337585 | 0.274046 |
| 39 | 0.472094 | 0.619661 | 0.551275 | 0.798212 | 0.415127 | 0.357446 |
| 40 | 0.376115 | 0.495106 | 0.468043 | 0.713520 | 0.327236 | 0.256586 |
| 41 | 0.391372 | 0.455721 | 0.519638 | 0.757071 | 0.323185 | 0.228775 |
| 42 | 0.665148 | 0.710210 | 0.732678 | 0.851817 | 0.552173 | 0.343712 |

40纯映射吞吐2.6588倍／2.0198倍，41为2.5551倍／2.1943倍。40的全部四个进程在两种线程数的新输出比值均≤1/3；41单线程进程比值为0.43465、0.32629、0.30741、0.32008，波动较大，不隐藏第一个进程。全部原始轮次见对应`worker*.json`。

真实输出计时包括实际公开API的验证、映射、对齐、尾部、fence及线程工作；参考23适配器为真实memcpy+旧apply。旧copy+apply、剔除copy的纯apply另列。文件IO、解码、分配和SHA在计时外，每轮完整输出SHA与源/哨兵核验均通过。准备为4线程原生构造；准备加首组100图使用首次已预热测量，不标作冷启动。五版准备加首组的配对比值分别为0.6672/0.9229、0.6912/0.9050、0.6383/0.8611、0.7130/0.8967、0.6929/0.6651。

固定门槛仍要求纯apply及真实输出的1/4线程中位比≤1/3，任一进程纯apply比≤0.9，准备加首组中位比≤1。仅真实输出达标不改变整体状态。旧接口3倍也没有实现。

## 正确性与失败保留

每版对新表独立解码全部16,777,216种颜色，另做12组in-place及12组真实输出完整色域比较：两库、单级/四级、标量1线程和AVX2请求1/4线程。四级gold SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，单级为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`，均逐字节一致。性能100图输出均为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。

| 修订 | 有限in-place比较 | 有限输出/别名比较 | 保护页比较 | 64种目标对齐比较 |
| --- | ---: | ---: | ---: | ---: |
| 38 | 1824 | 3648 | 608 | 1280 |
| 39 | 1536 | 3072 | 512 | 1280 |
| 40 | 2208 | 4416 | 736 | 1280 |
| 41 | 1824 | 3648 | 608 | 1280 |
| 42 v2 | 2208 | 4416 | 736 | 1280 |

每版另有44条新API拒绝检查及9条直表诊断拒绝。40/42完整域每次输入262144像素，覆盖四个65536工作块，并增加65536/131072两侧边界，避免“请求4线程实际只有一个块”的覆盖缺口。静态实汇编均无外部调用，原三个回退对象与同场参考逐字节相同；独立TU禁止超AVX2指令。

42首次验证v1在最后的句柄容量断言失败：验证器沿用`24+2**24`，实际新表为`24+2**23`。该运行没有通过回执，不计入已通过次数。保留原验证源、run、测量源码快照及[failure-note](../../report/data/skylake-cache-hints-v1/skylake-wordload-linux-full-v1/failure-note.json)，以新文件`verify_skylake_wordload_fixed_linux.py`及validation-v2只修正结束断言，在full-v2重新完整验收。库及模型未变；首次性能在v2通过后才运行。没有覆盖旧目录、复测性能择优或丢弃不利轮次。

当前固定模型在完整RGB8输出上完全一致，所以已有误差不下降；没有重新拟合。历史误差口径为RGB欧氏距离，非CIEDE2000；照片已见，不是盲测。其他网格全面矩阵、分配失败注入、MSVC、其他操作系统及实际Skylake均未新增验证。

## 计数器研究与环境限制

五次配对画像均单次预热、单次计数，每版1/4线程共4个配置，不生成墙钟成绩。每个参与TID独立读取用户态cycles/instructions/generic cache events；20项画像运行比例≥0.99，逐项SHA与绑定通过。少量ct/启停和OpenMP结束自旋包含在计数内，不能作为精确内核指令延迟。

| 同场配对 | 1线程周期／像素（参考→候选） | 4线程周期／像素（参考→候选） | 判断范围 |
| --- | --- | --- | --- |
| 37→38 | 7.2701→6.5919 | 8.0735→6.8119 | 本次周期降低；4线程generic miss并未降低 |
| 37→39 | 6.7533→7.5752 | 6.0975→8.1255 | T0全量预取额外指令未抵消成本 |
| 38→40 | 6.3579→5.9748 | 6.4200→6.1627 | 块内固定成本摊薄得到一次计数支持 |
| 38→41 | 3.7867→3.7885 | 4.5402→5.0050 | 额外约3条指令／像素，未支持周期收益 |
| 40→42 | 5.6191→8.7878 | 5.9375→8.2663 | 较小表未抵消解码成本 |

不同画像中参考周期明显不同，不能跨行相除作速度结论。[只读PMU映射](../../report/data/skylake-cache-hints-v1/pmu-mapping/results.json)记录cache-references为event0x60/umask0xff、cache-misses为event0x64/umask0x09、max_precise=0、perf_event_paranoid=2；这些是本机Zen4虚拟环境映射，不标作Skylake或精确L3未命中。

本轮发现C盘空闲为0，WSL提示不能创建交换盘；当时约14GB可用内存、SwapTotal=0、memory PSI为0，F盘约80GB可用。[原始环境记录](../../report/data/skylake-cache-hints-v1/host-space/results.json)保留此限制。没有删除用户文件、调整WSL配置、提升perf权限、停用安全缓解或改系统大页策略。所有构建和测量输出落在F盘。

[Intel优化手册15.16.4及图15-12](https://cdrdv2-public.intel.com/814198/248966-Optimization-Reference-Manual-V1-049.pdf)说明Skylake的硬件/软件gather取舍与缓存局部性有关，因此普通加载的本机优势必须在目标服务器复核；[GDS说明](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/gather-data-sampling.html)也提示缓解会影响gather延迟。本任务没有调整缓解。泛化事件语义边界见[perf_event_open](https://man7.org/linux/man-pages/man2/perf_event_open.2.html)，大页建议边界见[Linux文档](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)。

## 审计、复现与交付

[独立复算](../../report/data/skylake-cache-hints-v1/performance-audit.json)核对五次完整ABBA比较，共400轮旧模式和400轮真实输出，身份、全色域、源SHA、线程、大页、每轮输出及配对算式均通过。档案含194份原始文件、8,343,421字节，21份测量源码ZIP共1583项源成员、95项二进制成员；[档案核对](../../report/data/skylake-cache-hints-v1/archive-check.json)逐项SHA、ZIP及库身份通过。上述194份清单不包含之后新增的README、静态交付和操作前刷新元数据。

例：在仓库根目录、输入已按计划恢复且输出目录尚不存在时，运行如下命令。其他版本将`wordload`换为相应名称；42明确使用fixed验证器和full-v2，旧v1保留。

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-wordload-v1.json --output artifacts/skylake-wordload-linux-build-v1
python3 scripts/verify_skylake_wordload_fixed_linux.py --plan experiments/skylake-wordload-v1.json --build artifacts/skylake-wordload-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-wordload-linux-full-v2 --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_wordload_pinned_linux.py --policy experiments/skylake-wordload-linux-perf-v1.json --output artifacts/skylake-wordload-linux-perf-v1
python3 scripts/profile_skylake_wordload_pmu.py --policy experiments/skylake-wordload-pmu-v1.json --output artifacts/skylake-wordload-pmu-v1
python3 scripts/audit_skylake_cache_hints.py --output artifacts/skylake-cache-hints-delivery-v1/performance-audit.json
```

这些是原始冻结路径，不能直接在已有目录重跑覆盖。新的环境或构建须创建独立计划/输出并保留新SHA；不要修改历史计划来使哈希通过。235MB照片和两个50MB完整域流按计划同SHA恢复，模型来自已有`report/data/skylake-palette-v1/fixed-models.zip`；本档案不重复打包大流。构造及冻结验证生成器在证据ZIP中，恢复到原路径后可检查生成过程。

创建PR前已完整检查42个PR、2个独立issue、2个Discussion、128组REST意见、0条审查线程，分页完整；与上一阶段全部已读意见比较未变化，新增#48完整正文已读。相关修复337a3dd（#7/#9基线和绑定）、876e15b8（#27保护）、397cc367（#29相等mean）及依赖acaf2b2均为当前祖先。[协作检查](../../report/data/skylake-cache-hints-v1/remote-check.json)保留原链接、处理状态和未解决事项；操作前还会刷新逐项比较两份快照，覆盖新#48的正文/头/base及全部意见。

仍未解决：3倍整体门槛、派生表官方许可与内存预算、Threshold、实际Skylake速度、issue #8接口/实板及GUI #40事项。保持Draft，不合并、不关闭事项。下一阶段优先研究纯映射的访存与输出路径，以新候选直接对23验证；停止全量T0预取和本版主词解码扩展，不把画像周期或新接口单项达标写成整体完成。
