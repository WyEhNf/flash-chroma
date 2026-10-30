# 四项ID先行：单线程过三倍，四线程仍未过线

Agent：Codex；Operator：WyEhNf；Task：固定模型完整RGB8精度不下降，通用AVX2在本机相对修订23达到至少三倍吞吐；Status：In Progress。**整体目标尚未完成。** 本阶段65在同场四进程墙钟中，纯映射单线程配对中位比0.323628（吞吐3.0900倍），四线程比0.412157（吞吐2.4263倍）；真实分离输出单/四线程比0.275202/0.213119（3.6337/4.6922倍）。事前规定纯映射和真实输出两种接口的1/4线程都须至少三倍，因此四线程纯映射失败，不改变公共默认。

本阶段从[Draft PR #61](https://github.com/WyEhNf/flash-chroma/pull/61)的`1aac0f903c4829d6a1b05aa2dad78c82e52dd610`创建`codex/skylake-id-batch8-20261021`。64从已验40复制独立运行时，试图每8像素先发出8个随机精确ID表加载，再读取调色板；GCC实际宽循环每8像素产生多次ID栈写读，故在静态汇编阶段淘汰，**没有64的完整域或性能结果**。65复制64后把窗口缩为4像素，两个四项组分别用GPR编译器约束确保先发出ID读取；汇编首组4次ID加载早于首条调色板读取，宽循环不再出现按像素重复的ID栈写读。后续调色板、64像素NT输出、NTA输入、65536像素块维持40；模型、16MiB直表和23回退未改。64/65的源SHA分别在[构建计划](../../experiments/skylake-id-batch8-v1.json)与[65构建计划](../../experiments/skylake-id-batch4-v1.json)首次构建前冻结。

实际环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4；SIMD编译使用`-mavx2 -mtune=skylake -ffp-contract=off`，无AVX-512、PEXT、gather或fast-math。65独立Python标准库核验全部16,777,216种RGB8的表及整数oracle，参考/候选、单/四级、标量/AVX2请求1/4线程的12组原地与12组分离输出均逐字节一致；另有有限原地2208、分离/同址4416、保护页736、对齐1280及API拒绝44组通过。固定模型没有重新拟合，精度不下降。[验证身份单](../../experiments/skylake-id-batch4-validation-v1.json)在完整域通过后绑定其回执，[原始档案](../../report/data/skylake-id-batch-v1/README.md)保存源码、库与输出SHA。

65首次计数前[冻结同场PMU策略](../../experiments/skylake-id-batch4-pmu-v1.json)：1线程候选/40周期比≤0.95，4线程≤1.05，才运行墙钟。冻结100图各角色/线程一次预热、一次计数，全部running/enabled≥0.99，完整输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。

| 同场40→65 | 周期/像素 | 指令/像素 | 通用cache miss/像素 | 周期比 |
| --- | ---: | ---: | ---: | ---: |
| 1线程 | 3.23479→3.03694 | 5.40104→5.38543 | 0.10505→0.10124 | **0.938836** |
| 4线程合计 | 3.94043→3.89958 | 5.44306→5.43266 | 0.11481→0.11763 | **0.989633** |

65通过增量筛查后，在首次墙钟前[冻结四进程策略](../../experiments/skylake-id-batch4-quiet-perf-v1.json)：来宾CPU0/2/4/6绑定，父进程空闲前置检查，ABBA进程和线程顺序，每进程各角色/线程模式重复5轮，逐轮100图输出SHA核验；主门槛为四项配对中位耗时比各≤1/3，并检查最差进程回退和准备+首组。照片输入235,929,600字节，SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`。首次完整运行无重试，原始结果如下：

| 65/23同场四进程中位 | 1线程耗时比 | 1线程吞吐倍数 | 4线程耗时比 | 4线程吞吐倍数 |
| --- | ---: | ---: | ---: | ---: |
| 纯映射apply | 0.323628 | 3.0900 | **0.412157** | **2.4263** |
| 真实分离输出 | 0.275202 | 3.6337 | 0.213119 | 4.6922 |

四线程纯映射一项失败；旧copy+apply及准备时间完整列在原始结果，不能拿真实输出成功替代纯映射失败。此次23和65的绝对耗时均比旧40阶段明显缩短，旧40的2.6444/3.1200倍与本轮不能跨场直接相除或相乘。WSL虚拟PMU通用miss不指明具体缓存级，来宾vCPU绑定不保证宿主固定物理核；没有真实Skylake型号或实机计时。代码仅为可复核研究候选，官方派生表许可、内存预算与Threshold仍按[issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)待确认。本阶段保持Draft，不合并、不关闭事项。[归档](../../report/data/skylake-id-batch-v1/README.md)保存64汇编、65构建/完整域/PMU/四进程墙钟所有原件及SHA；新目录可依冻结策略依次执行`scripts/build_skylake_runtime.py`、`scripts/verify_skylake_id_batch4_linux.py`、`scripts/profile_skylake_id_batch4_pmu.py`和`scripts/bench_skylake_quiet_pinned_linux.py`，不得覆盖首次结果再挑选。
