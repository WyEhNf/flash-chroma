# 四线程逐TID访存诊断

Agent：Codex /root；Operator：WyEhNf；Task：保持完整RGB8精度、通用AVX2、相对23三倍吞吐；Status：In Progress。**整体三倍目标尚未完成。** 本阶段没有新优化修订或吞吐成绩，只补齐已验65的单/四线程事件诊断，避免把原地/分离输出的倍数差或单线程等待直接外推为四线程根因。

从Draft [PR #67](https://github.com/WyEhNf/flash-chroma/pull/67)头`aeffda0e1b869e3f3651275429e223879571f145`创建`codex/skylake-four-thread-diagnostic-20261021`。既有40诊断只测单线程；新[冻结策略](../../experiments/skylake-four-thread-diagnostic-v1.json)绑定原65库、构建、完整域结果、模型、照片、驱动及新脚本SHA。65库SHA仍`37b8ef8a22805f9bebb701d6a16f5c14cc31219280033e5f70eae7d236936cb8`，没有重编译或改变默认。

固定顺序为照片原地1/4线程、固定灰色原地4/1线程、照片分离输出1/4线程。每项一次完整预热和一次公开API计数，共6次预热、6次计数，**原生墙钟验收调用0**，不扫描、不重复挑选。单一句柄，100图共78643200像素；灰色固定(128,128,128)，只改变诊断输入，没有内容特判内核。

实际Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu / Linux6.18.33.2 / GCC15.2库 / Python3.14.4标准库，原65 Release AVX2使用`-mavx2 -mtune=skylake -ffp-contract=off`。先等待来宾空闲和PID1年龄条件，绑定来宾CPU0/2/4/6并核验实际团队、TID单CPU集合。原16MiB VMA恰好同容量、2MiB对齐且全部THP覆盖，所有案例前后均通过。没有宿主独占、锁频、控温或目标Skylake实测。

六事件沿用[Linux v6.18 Zen4事件表](https://github.com/torvalds/linux/tree/v6.18/tools/perf/pmu-events/arch/x86/amdzen4)：cycles、instructions、l2_request_misses、oldest_not_complete、oldest_load_not_complete、load_dispatch。CPU family25/model97检查通过。按每TID独立打开六事件pinned组，排除kernel/hypervisor；主TID最后enable、最先disable。全部24组原始读取字节先落盘，再核验running/enabled≥0.99、事件包含关系和输出，不用诊断失败前丢失的数据补成成功。

| 输入与接口 | 线程 | 参与TID合计周期/像素 | 指令/像素 | L2请求miss/像素 | 最老加载未完成周期比例 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 照片原地 | 1 | 3.048125 | 5.378356 | 0.106666 | 54.50% |
| 照片原地 | 4 | 3.977356 | 5.429631 | 0.119758 | 60.80% |
| 固定灰色原地 | 4 | 2.768861 | 5.399074 | 0.000474 | 14.27% |
| 固定灰色原地 | 1 | 1.301282 | 5.378328 | 0.000179 | 4.24% |
| 照片分离输出 | 1 | 3.465883 | 5.394281 | 0.122487 | 60.07% |
| 照片分离输出 | 4 | 4.993917 | 5.454090 | 0.139694 | 67.72% |

照片原地四个参与TID的名义周期/像素为3.996/3.941/4.003/3.969，加载等待比例57.8%/62.7%/57.9%/64.9%；灰色四线程周期/像素2.775/2.668/2.821/2.812，加载等待13.0%—15.5%。未见单个线程独占全部周期的现象，但没有逐线程像素循环内部计时，不能据总周期接近断言工作量或barrier开销完全均衡。

四线程每TID名义19660800像素由原65连续`schedule(static)`的1200个65536像素块均分推定；1线程只把CPU0的调用线程归为参与者，另三个已创建的TID计数全部保留、单列旁观总量，不混入参与汇总。计数窗口包含OpenMP分派、barrier、收尾自旋和少量ct/启停，不能从最老加载等待比例直接求平均延迟或未完成请求数。虚拟PMU未由宿主校准，Zen4事件不能标为Skylake指标。

本次结果支持照片路径存在显著加载等待；灰色在四线程下也有较高周期成本，说明不能只用表miss解释所有成本。它不证明具体缓存级、NT写、带宽、频率或收尾哪项是根因，不能拿照片/灰色周期相除当作候选提速，更不能重评旧失败或宣布三倍。后续选择实质改动仍须完整精度及受控直接23验收。

12次调用完整输出SHA均符合冻结预期，源及前后保护区未变。照片输入235929600字节SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。本阶段未重做完整色域或拟合；完整域精度沿用相同SHA的65原证据。计数正确、照片正确不替代完整域或吞吐验收。

另有固定64字节块的只读归一化字典分析：以块首ID做模256差，完整逻辑表重建0差，但唯一块只从88387降到84608，载荷6705344→6463488字节，减少约3.61%，且多出解码运算。没有实现或运行归一化内核。Windows CPython3.13.12/NumPy2.4.6实际环境留档，原生/性能调用均0。八ID打包建议也仅静态审阅后停止：65实际汇编已跨组读取，新强制打包会增加指令和成对依赖，没有足够依据实施。没有把未实施想法当作测试结果。

[42份原件与独立复算](../../report/data/skylake-four-thread-diagnostic-v1/README.md)保留全部原始六事件、空闲采样、源码ZIP、相同二进制和只读分析。`audit.json`独立解码24组原始字节，逐TID核对enabled/running、参与求和、名义像素、输出及THP。复现需恢复同SHA模型、照片和依赖，使用新输出目录，原命令为：

```sh
python3 scripts/diagnose_skylake_four_thread_linux.py --policy experiments/skylake-four-thread-diagnostic-v1.json --output artifacts/skylake-four-thread-diagnostic-v1
```

首次执行前只对新脚本做AST/JSON及冻结哈希静态检查，没有试运行像素或测量后改源。归档库是Ubuntu/glibc2.43本机证据；真实Skylake应重编译，并使用对应处理器官方事件。

创建前fetch GitHub，读取61个PR正文并与前阶段60份全文比对，仅新增67，旧正文一致；刷新67正文、完整评论/review/行内线程。main仍`b19c5a0`，三个既有修复仍包含；7/8意见承接上一阶段已读快照。Discussion接口仍不能刷新，不把缺口当作没有新意见。[操作回执](../../report/data/skylake-four-thread-diagnostic-v1/remote-check.json)保留范围和限制。以Draft交付，不合并或关闭事项；整体三倍、官方派生表许可/预算/Threshold和Skylake实机仍待验证。
