# 写预取的完整精度与受控三倍验收

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：固定模型RGB8精度不降、通用AVX2、相对修订23吞吐至少三倍；Status：Failed（候选74），整体In Progress。**74的完整精度及两档A/A控制均通过，但四线程纯映射仅2.088002倍，整体目标未完成。** 按冻结规则跳过确认，不重测、不采用。

阶段分支`codex/skylake-prefetchw-20261021`从Draft [PR #69](https://github.com/WyEhNf/flash-chroma/pull/69)头`434c34ac8478742251d0fcefe87debf57ee2f95d`继续。源码在73测量期间提前准备，计划`base_commit`因此仍记录当时的`90f2b68`；实际构建身份由[71项源SHA和计划](../../experiments/skylake-prefetchw-v1.json)绑定，没有使用73的第二张表。

74保留65/72同字节线性像素TU及16MiB精确ID表，单线程和全部分离输出仍使用NTA/NT/SFENCE。多线程原地使用65四ID先行与68普通写；仅把原T0内核的五处预取表达式换成写预取，初始有效窗口、1024字节前瞻、全部边界、65536像素块、连续static调度和RGB24输出保持。两个独立普通写TU源码除五处提示外相同，入口名称由CMake宏区分；仅W单元获得`-mprfchw`。

构造时只检测一次`__builtin_cpu_supports("prfchw")`，不支持就走T0普通写。新增只读`jshc_cc_prefetchw_enabled`报告句柄是否同时满足CPU能力及直表存在，null和单级返回0；该标志不表示所有线程/接口都执行W，路径还取决于原地和workers>1。本机完整域和全部性能句柄均实际报告chain=1，批次另记linear/prefetchw选择。bool放入既有padding，四级记账28046644字节、单级272859，与65相同；相对23分别增加24+16MiB及24字节，不是RSS。

[Intel优化手册050](https://cdrdv2-public.intel.com/821612/248966-Optimization-Reference-Manual-V1-050.pdf)说明Broadwell/Skylake可用，不能仅凭AVX2推定所有处理器支持；[Intel SDM](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2b-manual.pdf)将它定义为面向写入的独占所有权预取提示，实现可忽略。这里的研究假设是提前请求所有权可能减轻普通写等待，既有六事件并未证明该根因。GCC检测名、intrinsic及CPUID位的官方源链接均在计划中。没有改变系统缓存、安全或频率设置。

实际Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu / Linux6.18.33.2 / GCC15.2 / Python3.14.4标准库 / glibc2.43。Release SIMD为`-mavx2 -mtune=skylake -ffp-contract=off`，仅W额外`-mprfchw`，无native、AVX512、BMI2或fast-math。没有Skylake实机、宿主独占、锁频或控温证据。

静态核对T0/W的.text仅五个预取opcode字节不同；各792条指令，64/32像素主体344/170条，无栈引用，每组四ID先于其调色板读取，64像素全部读取后普通写。8像素尾部保持60条原精确24字节读取，不声称尾部也有四ID屏障。W有五处prefetchw，T0有五处prefetcht0，两者均无NT/SFENCE；线性对象仍321/322条主体。全部像素对象无call/gather/BMI2/AVX512或EVEX；独立检查编译命令和通用分派器未发现ISA泄漏。静态差异不是性能证明。

完整16,777,216色独立表及12组原地+12组真实输出RGB8配置逐字节通过，另有有限原地2208、分离/同址4416、保护页736、目标对齐1280、API拒绝44、direct拒绝9及新只读null检查1通过。完整域显式记录本机W实际启用，固定模型精度不下降。线性表SHA仍`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`，四级完整域输出SHA仍`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。没有重新拟合、其他模型全面矩阵、分配失败注入或真实缺prfchw硬件执行；不以静态分派审计冒充缺特征硬件测试。

完整域通过后冻结[长批次策略](../../experiments/skylake-prefetchw-long-perf-v1.json)：四个串行新进程ABBA、线程顺序1/4、4/1、1/4、4/1，每角色一句柄，每线程先candidate同句柄A/A，再23/74的legacy和outplace批次。1线程每批16内轮、4线程64内轮，先批内均值，再四worker配对比中位。共1920内轮、48次预热及48次批末完整100图SHA，非每内轮独立SHA。实际团队/TID绑定、源/哨兵、前后W启用、16MiB精确VMA/全部THP/2MiB对齐均核对。

| 接口 | 1线程中位耗时比／吞吐 | 4线程中位耗时比／吞吐 |
| --- | ---: | ---: |
| 纯映射apply | 0.330898／3.022078倍 | **0.478927／2.088002倍** |
| 真实分离输出 | 0.263720／3.791902倍 | 0.229247／4.362112倍 |
| 旧copy+apply | 0.496174／2.015423倍 | 0.779417／1.283010倍 |
| 准备+首组真实输出 | 0.624401 | 0.785579 |

纯映射四线程四对为0.479119/0.478734/0.490095/0.476960，全部高于1/3。单线程四对0.328431/0.333366/0.328351/0.335786，中位过门槛，不声称每对均过。准备+首组为预热后的首个测量加准备，不是冷启动。所有比值来自本次直接74/23，不与73或旧65场次拼接，也不据此判定W相对T0的独立收益，因为本次没有直接T0配对。

A/A单线程B/A四对1.006546/0.941065/1.001449/1.070224，中位1.003998；四线程1.015003/0.998916/1.023088/1.024214，中位1.019045。两档均满足事前中位`[1/1.10,1.10]`和任一对`[1/1.25,1.25]`。控制有效不替代性能；原门槛仍为两接口1/4线程各≤1/3、最差纯映射对≤0.9及准备+首组≤1。四线程纯映射失败，所以[确认决定](../../report/data/skylake-prefetchw-v1/confirmation-decision.json)跳过唯一确认，新增确认调用0，不补测择优。

[108份原件及独立复算](../../report/data/skylake-prefetchw-v1/README.md)保存构建、库、源码ZIP、静态/独立审计、完整域及所有数组。输入100张1024×768 RGB8共235929600字节，SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`；输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。计时包含API验证、映射、对齐、尾部、fence和线程工作，不含IO、解码、分配、SHA或模型准备。

复现按冻结SHA恢复模型、照片和独立首级oracle，在独立副本的新目录运行，不覆盖已有档案：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-prefetchw-v1.json --output artifacts/skylake-prefetchw-linux-build-v1
python3 scripts/verify_skylake_prefetchw_linux.py --plan experiments/skylake-prefetchw-v1.json --build artifacts/skylake-prefetchw-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-prefetchw-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_prefetchw_long_linux.py --policy experiments/skylake-prefetchw-long-perf-v1.json --output artifacts/skylake-prefetchw-long-perf-v1
```

候选库SHA为`d4ba3c35bb06b72b59877f7ab82defbc7f72ca408e337b7d98f45f49e540c1bc`；归档Ubuntu/glibc2.43库只作本机证据，目标服务器应重编译。108份清单不含后补README、阶段说明与远端刷新。创建PR前的正文/意见核查范围与限制以[协作回执](../../report/data/skylake-prefetchw-v1/remote-check.json)为准；Discussion接口仍不可刷新，不把缺口当作没有新意见。保持Draft，不合并、不关闭事项。整体三倍、真实Skylake及官方派生表许可/预算/Threshold继续待验证。
