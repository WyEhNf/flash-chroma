# 修订84：正常块直接RGB，异常整包精确回退

Agent：Codex /root、/root/base_delta_delivery；Operator：WyEhNf；Task：保持完整RGB8精度、通用AVX2、相对23至少三倍吞吐；Status：Failed（四线程纯apply）/ Draft。工作分支`codex/skylake-brick2-hybrid-20261023`，基于[PR81](https://github.com/WyEhNf/flash-chroma/pull/81)。**一次构建、静态及完整正确性通过，但首轮A/A有效时四线程纯apply仅0.951626倍23吞吐，失败、不采用；整体三倍目标未完成。**

## 机制与资源

前序纯pool格式的池通过2MiB，但照片异常8包14.782206%、最差46.474202%，未过原5%/20%，失败判定保留。84是独立混合内核：保留原16MiB linear ID及palette，再构造16MiB的2³输入块表；正常块直接恢复RGB，任意lane带bit63 tag时，整个八像素包精确回退原ID→palette，不建立例外pool。它不改旧纯pool门槛或将其失败重新解释为通过。

块地址为`q=(R>>1)|((G>>1)<<7)|((B>>1)<<14)`，块内`k=(R&1)|((G&1)<<1)|((B&1)<<2)`。原四张模型及逐级RGB8产生唯一标签；建表从已构造的direct+palette读取，不读照片、gold或预期输出。全部有效230项palette推导minDG=-11、minDB=-6及span11/6，满足4/3bit容量。低15bit存baseR8、DG_offset4、DB_offset3，八个3+2+1残差放在bit15..62；正常词bit63=0，例外词仅bit63=1。合成基值有效且非ffffff、残差范围均满足才编码，否则留tag；全局格式或构造失败不发布新表，保持原精确路径。

新TU每次先完整读取8像素24B，再查八个主词和判断tag；正常路径按6k+15移位恢复差分，以有符号偏置的32位模加法精确恢复RGB，最后普通写恰好24B。没有pool、gather、BMI、AVX512、非临时写或预取。只有有效workers>1且新表启用才分派新内核；单worker、真正分离输出及新表不可用时保留79的pair48/linear，BMI1仅用于原两个pair TU，不依赖失败83的ordered内核。

| 计量项目 | 实际字节 |
| --- | ---: |
| 参考23单级／四级句柄 | 272,835／11,269,404 |
| 84单级／四级句柄 | 272,939／**44,823,940** |
| 相对83四级增加 | 16MiB常驻表＋80B Handle字段 |
| 相对23四级增加 | 32MiB派生表＋104B元数据 |
| 已知临时容量峰值记账 | **127,650,352** |

构造先生成16MiB临时u64词，再分配常驻表并复制、发布；临时词与新表重叠的32MiB均计入原temporary_peak_bytes，构造完整纳入palette prepare计时。容量记账不是RSS或完整分配器峰值；本阶段未做分配失败注入。原direct ABI不变；新56B只读hybrid_info、精确词数导出、新表页诊断及资格getter独立提供，getter不是每次调用执行计数。

## 静态与完整正确性

[冻结计划](../../experiments/skylake-brick2-hybrid-v1.json)绑定源、模型与构建。唯一构建为Release、GCC15.2，AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`；原两个pair TU另加`-mbmi`，generic runtime不泄漏ISA。reference仍为23库，候选库SHA为`f37d116d32f2bcdd2595dc79d341d64419fc421b5b8fb95f8aeab47ebb48ea24`。

根静态结果及独立ELF/重新反汇编审计均通过：完整normal控制流**97条宏指令、11次load＝8主词＋2输入＋1RIP常量**，在事前128/18预算内。正常热循环无栈访问，序言保存及退出恢复单列；两组fallback各先得到四ID再读取对应palette。独立核对ELF常量池、24B输入输出标签、分支/共用输出、旧三个对象.text等79及runtime ISA/分派。计数不是微操作、缓存miss或性能预测。独立结果SHA：`48288d19d27c27d10ae3cd24a993fba5295d019e14b899f39b4751987a5cb051`。

原生完整矩阵一次通过：两库×单/四级×标量1与AVX2请求1/4，各12组原地及12组真正分离输出，**每组全部16,777,216色零字节差**；另有2208有限原地、4416分离/同址、736保护页、1280旧对齐、44分离拒绝、9原direct拒绝检查通过。额外64个实际地址偏移0..63，每次65793像素跨两块，输出与哨兵一致；完整域每批262144像素覆盖四块，按冻结分派分别覆盖workers2/4，不虚构内核内计数。

独立导出的新表2,097,152词中正常2,033,554块，逐项检查**16,268,432个正常颜色**与原direct+palette精确相等；63,598个tag词均严格只含bit63，其实际异常输入由完整原生矩阵验证。新表SHA为`8c86a1e798a4bfe849036996c713766daf28511a4071879bf939066bea6a0d9e`。两个16MiB表均实际2MiB对齐、完整THP覆盖。新增9项hybrid ABI拒绝及null资格检查通过。该矩阵不做照片性能或重新拟合，固定模型输出保持不变。

三项胶水基础设施失败完整留证：静态初件先误判绝对/相对反汇编标题，随后计数分类漏vpinsrq第二内存操作数并误把符号括号算load，修正后另存results-v2；性能preflight初件误读独立结果schema，见preflight/perf-schema-failure。它们没有触发候选重编译、重复像素矩阵或更改门槛，不是候选精度失败。

## 唯一首轮性能失败

[验证身份](../../experiments/skylake-brick2-hybrid-validation-v1.json)及[首轮策略](../../experiments/skylake-brick2-hybrid-long-perf-v1.json)绑定实际静态passed、库/构建/完整矩阵。四串行新进程AB/BA/BA/AB及1/4线程平衡，沿用同库A/A、quiet、实际TID绑定和前后THP核查；每批内部均值形成worker候选/23比，再聚合四对中位。首轮唯一执行共1920内轮（640控制、1280比较），1/4线程每批16/64内轮；48预热、48批末SHA，非每内轮独立SHA，全部原始数组保留。

验收要求纯apply和真正分离输出的1/4线程中位耗时比均≤1/3、任一纯apply进程≤0.9、准备加首组中位≤1，并通过同库控制。结果来自`artifacts/skylake-brick2-hybrid-long-perf-v1/results.json`，耗时比为84/23，吞吐为倒数：

| 接口 | 1线程耗时比／吞吐 | 4线程耗时比／吞吐 |
| --- | ---: | ---: |
| 纯apply | 0.328305／**3.045947倍** | 1.050833／**0.951626倍** |
| 真正分离输出 | 0.284789／3.511375倍 | 0.213699／4.679473倍 |
| 准备＋首组分离输出 | 0.760793 | 0.979410 |

四线程纯apply耗时增加5.0833%，吞吐下降4.8374%；四对耗时比为`[1.022064,1.060943,1.063419,1.040723]`，全部超过0.9，故同时失败“四线程三倍”和“任一进程≤0.9”门槛。分离输出不能替代纯apply；两档准备中位通过，但4线程两个进程1.128655/1.129641仍完整保留，原门槛只要求中位，未事后放宽。

同库A/A中位1/4线程为0.968439/0.977317，四对均在0.8—1.25范围内且中位满足原控制门槛，测量控制有效。首轮失败，因此确认系列/调用均0，不重测、不择优、不采用。正常路径97条宏指令及额外寻址、拼接与回退成本尚需用实际证据分解；本次结果已说明减少串依赖载荷不能直接当成加速，不从静态计数归因具体周期损失。

近期严格协议的历史最好仍为80单线程3.152974倍及78四线程2.525664倍，来自不同版本和不同场次；不拼接为同一候选的整体三倍，也不据本轮重新评判旧失败。

实际环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu Linux6.18.33.2、GCC15.2、Python3.14.4标准库，来宾CPU0/2/4/6绑定；未锁频控温、证明宿主独占或执行实际Skylake。官方派生表许可/预算/Threshold、Skylake实机及整体三倍目标继续待办，不合并或关闭事项。

## 文件、复现与交付

主要实现为[新像素TU](../../experiments/skylake-brick2-hybrid-runtime/hybrid_inplace/channel_avx2.cpp)、[构造与分派](../../experiments/skylake-brick2-hybrid-runtime/channel_runtime.cpp)及独立CMake/ABI；[完整矩阵入口](../../scripts/verify_skylake_brick2_hybrid_linux.py)、[新表独立核验](../../scripts/brick2_hybrid_support.py)与[长批次入口](../../scripts/bench_skylake_brick2_hybrid_long_linux.py)保留原口径。它们同本阶段单独工作分支提交交付，完整提交SHA由对应Draft PR正文列出。

[归档](../../report/data/skylake-brick2-hybrid-v1/README.md)含235份原字节及235项清单，ZIP SHA为`26f913c0bb27d28fb94d409bb9bc893df7dde5137d0df559b8eb7f7e623463bb`，包括唯一构建对象/ELF、冻结源、完整域、48批原始时间、quiet、A/A与确认跳过记录。标准库独立复算全部样本均值、四对比值、中位、准备加首组和A/A门槛，结论一致；不因归档再测。后补操作刷新与暂存交付回执在ZIP之外，避免自引用。

实际执行命令如下，输出目录为原件；不是要求覆盖已有证据。需要完整复现时先恢复同SHA模型、cube、单级oracle和百图，并在新身份/新目录重建绑定；大输入不在本ZIP。

```bash
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-brick2-hybrid-v1.json --output artifacts/skylake-brick2-hybrid-linux-build-v1
OMP_DYNAMIC=FALSE OMP_PROC_BIND=TRUE OMP_PLACES='{0},{2},{4},{6}' python3 scripts/verify_skylake_brick2_hybrid_linux.py --plan experiments/skylake-brick2-hybrid-v1.json --build artifacts/skylake-brick2-hybrid-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-brick2-hybrid-linux-full-v1 --affinity-cpus 0,2,4,6
python3 -u scripts/bench_skylake_brick2_hybrid_long_linux.py --policy experiments/skylake-brick2-hybrid-long-perf-v1.json --output artifacts/skylake-brick2-hybrid-long-perf-v1
```

仅核对归档而不加载候选：Windows11 / Python3.13.12标准库执行`python -X utf8 report/data/skylake-brick2-hybrid-v1/verify_archive.py`，临时目录重算与原审计一致。JSON/AST/本地文档链接/空白与Git暂存原字节另核对，不冒称全仓数值门禁。

操作前再次fetch GitHub，main仍`b19c5a0c8f67c3b4822692682698fb06462b7ed7`。75份完整PR正文对前74份仅新增81、旧正文无变；81完整正文及全部comment/review/行内均刷新为空。最终updated PR/issue检索无新增。issue7/8正文与全部评论已读，`337a3dd`、`876e15b8`、`397cc367`实际为本分支祖先：7的绑定修复保留，8的接口/预算/实板待办不混作已完成。当前连接器不能刷新Discussion，保留缺口，不合并或关闭事项。[末次协作快照](../../report/data/skylake-brick2-hybrid-v1/remote-refresh.json)保留原文和检查范围。
