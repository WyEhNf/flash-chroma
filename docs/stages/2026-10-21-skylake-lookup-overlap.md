# 查表等待诊断与输入输出固定组合

**相对修订23的整体三倍吞吐目标尚未完成。** 本阶段在既有40的16MiB无损ID表路径上确认本机照片输入的加载等待，再对已分别改善单线程计数的50向量输入和57输出预排做唯一固定组合59。59逐字节正确，但单线程周期退化，未过事前冻结的增量筛查；没有新增整轮墙钟成绩。最新有效整轮仍是[PR #50](https://github.com/WyEhNf/flash-chroma/pull/50)的40：纯映射1/4线程相对23为2.6444/3.1200倍，真实输出3.3066/4.3069倍。不能将不同实验的局部收益相乘。

分支`codex/skylake-lookup-overlap-20261021`依赖[PR #54](https://github.com/WyEhNf/flash-chroma/pull/54)的`b157a68e12b5e7a72aa6db0816d6165f24ec8a12`。本阶段仅新增研究库、冻结策略和诊断入口；原23、公共默认、模型、只读`AGENTS.md`未改。

## 诊断与设计

先冻结[诊断策略](../../experiments/skylake-lookup-diagnostic-v1.json)，在一次非像素探针确认六个Zen4原始事件的计数比例均为1后，对同一40对象分别处理真实100图原地、固定灰色原地、真实100图分离输出，各预热一次、计数一次。照片原地的最老加载未完成等待为2.24429周期/像素，占计数周期62.858%；固定灰色为0.08363周期/像素、6.218%；照片分离输出为2.58271周期/像素、64.477%。三者指令均约5.4/像素。照片原地的generic缓存miss为0.10741/像素，固定灰色为0.00018。它支持本机真实照片存在显著访存等待，但不同输入的周期不可用作相对23的吞吐比，也不证明具体缓存级、平均延迟或Skylake行为。原始事件定义采用[Linux v6.18 Zen4事件表](https://github.com/torvalds/linux/tree/v6.18/tools/perf/pmu-events/arch/x86/amdzen4)；WSL虚拟PMU未由宿主校准。

另外只读扫描已冻结照片的64像素窗口，R低表平均涉及49.4153条64字节线，B低排列为49.7014；所以未启动B低候选。这是地址集合统计，不是硬件miss计数。旧54已向量化，虽降低generic miss却使单线程周期增加约24%；不在“首次向量化”错误前提下组合54和57。59只组合50的精确24字节AVX2输入展开与57按输出位置预排的三条NT合并，保留40的ID表、GPR ID/调色板加载、NTA、64像素读后写192字节、65536像素工作块、SFENCE及普通尾部。独立审阅还发现4096个逻辑4KiB ID页中3082页内容唯一，但页别名会破坏当前2MiB THP且不减少逻辑页数量；无性能依据启动实现。

## 验证与结果

实际环境是Ryzen9 8945HX、Windows11宿主上的WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库。Release AVX2 TU为`-mavx2 -mtune=skylake -ffp-contract=off`，无AVX512、native、fast-math、PEXT或gather。绑定来宾vCPU0/2/4/6；它们不保证对应固定宿主物理核。没有实际Skylake、锁频或宿主独占验证。

59静态检查原23/16/4回退对象与参考逐字节相同，像素对象无外部调用、PEXT、gather或AVX512。独立解码16,777,216个ID；两库×单/四级×标量/AVX2请求1/4线程的原地12组、分离输出12组完整RGB8 API配置全部与独立整数输出逐字节相同，差异和哨兵越界均为0。另通过2208个有限原地、4416个分离输出/别名、736个保护页、1280个目标对齐和44个API拒绝检查。物理表SHA仍为`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`，四级输出SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`；固定模型的精度不下降。未重新拟合，也不声称相对官方LUT零误差。

在首次59计数前冻结同场40的周期筛查：1线程候选/40≤0.95且4线程≤1.05，才进入整轮墙钟。100图输入235,929,600字节，SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`；各配置各一次预热、一次计数，输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。逐TID计数运行比例≥0.99，句柄16MiB表实际完全大页覆盖。

| 同场40→59 | 周期/像素 | 指令/像素 | 周期比 |
| --- | ---: | ---: | ---: |
| 1线程 | 3.05874→3.25798 | 5.40104→4.77587 | 1.06514 |
| 4线程 | 4.04262→4.00643 | 5.43965→4.82716 | 0.99105 |

1线程失败；减少约11.6%指令没有换来周期收益。按策略停止，不做完整墙钟、重计挑选或3倍宣称。4线程轻微改善仅为本次计数结果。诊断、布局扫描、构建、汇编、完整域、四项计数原件及二进制见[归档](../../report/data/skylake-lookup-overlap-v1/README.md)；[独立离线复核](../../report/data/skylake-lookup-overlap-v1/independent-audit.json)通过35份原始文件SHA与全部门槛。

[协作记录](../../report/data/skylake-lookup-overlap-v1/remote-check.json)完整读取50个PR、2个独立issue、2个Discussion、152组REST意见及0个审查线程，分页完整。与前阶段已读记录比较，旧正文、状态、头SHA、base SHA和评论/review均无变化；新增#54为本阶段依赖，#55/#56分别是其他模型精度和插值研究，均无新增评论或review。本分支包含main `b19c5a0`、#7/#9的`337a3dd`、#27的`876e15b8`、#29的`397cc367`及#54头。历史修复依其既有验证，不冒充本阶段重测。创建Draft前仍须再次完整刷新，若有新增意见则重新核对。

复现需从归档的`measured-source.zip`恢复原字节、使用同SHA模型和输入，在新输出目录依次调用`scripts/build_skylake_runtime.py`、`scripts/inspect_skylake_vectorpack.py`、`scripts/verify_skylake_vectorpack_linux.py`、`scripts/profile_skylake_vectorpack_pmu.py`；完整命令参数由各脚本`--help`和冻结策略给出。不得覆盖既有输出后冒充首次计数。当前库仅为可复核研究候选，目标Skylake应重新编译并验证；官方派生表许可、内存预算、Threshold及实板表现仍以[issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)跟踪。整体目标继续active，本阶段保持Draft，不合并或关闭事项。
