# 六十四像素ID先行查表：精度保持，性能回退

Agent：Codex；Operator：WyEhNf；Task：在完整RGB8精度不下降的前提下，相对修订23达到至少三倍吞吐；Status：In Progress。**整体目标尚未完成。** 最新有效整轮墙钟仍是[修订40的Draft PR #50](https://github.com/WyEhNf/flash-chroma/pull/50)：纯映射单/四线程为2.6444/3.1200倍，真实输出为3.3066/4.3069倍。本阶段63未过事前增量筛查，不能产生新的墙钟或三倍声明。

本阶段从[Draft PR #60](https://github.com/WyEhNf/flash-chroma/pull/60)的`d209c7ad0159c808215ef8cb9d7b4fe1efb77ff2`创建`codex/skylake-deferred-palette-20261021`，复制已验40为独立实验运行时，仅将AVX2宽循环改为先连续取64个精确表ID到栈上64字节，再查230项调色板并沿原40路径打包输出。`std::atomic_signal_fence`只保证编译器保留两阶段顺序，不执行硬件栅栏。意图是提高随机ID加载的并行度；原四级模型、16MiB表、NT输出、NTA输入、65536像素工作块、公共默认和23回退未改。[构建冻结计划](../../experiments/skylake-deferred-palette-v1.json)在首次构建前记录69份源码SHA；[计数策略](../../experiments/skylake-deferred-palette-pmu-v1.json)在首次计数前冻结同场40的1线程≤0.95、4线程≤1.05周期比条件。

实际环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4。Release AVX2翻译单元使用`-mavx2 -mtune=skylake -ffp-contract=off`；未使用AVX-512或fast-math。独立Python标准库核验全部16,777,216种RGB8的表与整数oracle，参考/候选、单/四级、标量/AVX2请求1/4线程的12组原地和12组分离输出均逐字节一致。有限原地2208、分离输出及别名4416、保护页736、目标对齐1280、API拒绝44组全部通过。模型没有重新拟合，固定模型输出精度不下降。

同场40/63各线程配置只预热一次、计数一次，使用冻结100张1024×768照片，输入SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，完整输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。全部计数未复用硬件计数器，记录运行比例为1。结果如下：

| 同场40→63 | 周期/像素 | 指令/像素 | 通用cache miss/像素 | 周期比 |
| --- | ---: | ---: | ---: | ---: |
| 1线程 | 3.17054→4.55847 | 5.40104→7.08711 | 0.10110→0.11085 | **1.437760** |
| 4线程合计 | 3.99033→5.87931 | 5.44474→7.14222 | 0.12300→0.14018 | **1.473390** |

两项均失败；额外的暂存、重读和顺序约束没有转化为访存收益。遵守冻结策略，不重测63挑选数值，也不执行整轮墙钟。[原始档案](../../report/data/skylake-deferred-palette-v1/README.md)保存构建、源码ZIP、完整域和计数原件及SHA清单；在新输出目录可依次运行`scripts/build_skylake_runtime.py`、`scripts/verify_skylake_deferred_palette_linux.py`与`scripts/profile_skylake_deferred_palette_pmu.py`复核。

本机WSL虚拟PMU事件不是精确L3指标，来宾vCPU固定不保证宿主物理核固定；真实Skylake尚无实测。内存预算、官方派生表许可、官方Threshold仍按[issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)待确认。本分支只交付Draft研究，不改默认、不合并、不关闭事项。
