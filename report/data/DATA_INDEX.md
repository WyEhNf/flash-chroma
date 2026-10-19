# 报告数据索引

2026-10-20新增[时间优化阶段](../../docs/stages/2026-10-20-skylake-runtime-delivery.md)：[56位轴表](skylake-packed-v1/README.md)、[精确16位乘加](skylake-madd-v1/README.md)、[精确binary32](skylake-float-v1/README.md)均未达本机速度门槛；[有界精确后缀缓存](skylake-suffix-cache-v1/README.md)在同模型、同核集合的Windows/AMD对照中使1/4线程apply耗时下降约52%，增加742544字节准备容量，准备成本另列。缓存另有WSL/Linux完整字节比较，不代表Skylake实测；派生缓存的题目许可与目标服务器验收仍待办。四候选各自保留冻结计划、原始轮次及源码/二进制身份，不更新默认或历史PDF。

后续[描述符快照静态研究](skylake-snapshot-static-v1/README.md)只完成构建、汇编及MCA建模：热指令减少而栈访存增加，模型信号不一致，未运行新像素、整数正确性或性能测试，不采用。

[按阶段遍历像素块](skylake-stage-major-v1/README.md)保持实际四级字节与准备容量不变，一次比较1/4线程apply配对中位耗时下降6.1047%/3.2690%，但一个4线程进程退化8.6293%，未通过“任一进程退化≤2%”门槛，不采用、不排除该进程或重跑。

[首级/后缀单边界拆分](skylake-prefix-split-v1/README.md)同模型完整字节一致、容量不变；一次比较1线程apply配对中位下降4.3414%，4线程增加0.3322%、最差进程增加5.9418%，门槛失败，不采用。保留聚合绝对中位与同进程比中位的区别，不能挑较好的口径。融合边界族停止，不追加块尺寸/线程扫描。

最新本地汇总见[当前精度结果](../../docs/stages/2026-10-19-precision-latest.md)。`cinema-current-anchor-accept-v1`保存a399真实四级完整域/百图/独立整数与原生终验、逐图退化、约46%成本背景；`channel-runtime-specialized-v1`保存同a399模型的唯一编译期专门化合同、完整原生等价和受控配对速度收益，两个阶段的速度不跨阶段相乘。

`cinema-channel-suffix-coordinates-v1`、`cinema-channel-suffix-joint-nodes-v1`保留两个未入围候选；`cinema-cap-anchor-diagnosis-v1`保留唯一原色的逐级轨迹；`cinema-current-anchor-v1`保留统一收紧191色及唯一整合拟合/选择。`channel-runtime-reuse-v1`保留节点读取减少却变慢的负结果。新格式未接公共默认/GUI/C99，仍无官方数据或Threshold。

2026-10-19本地精度研究新增：[Filmic静态解析校准](filmic-calibration-v1/report.md)、[直接单调m17](filmic-direct-monotone-v1/report.md)。同SHA恢复PR41来源与两尺寸基线，m33及后续独立m17候选完整256³/百图误差归零，保留逐图与实际单级后端证据；这是严格可分离单LUT特例，不代表通用三维或四级比赛链。另有[Cinema节点续优化](cinema-calibrated-nodes-v1/report.md)、[Cinema精确事件搜索](cinema-exact-axis-v1/report.md)、[Velvia事件搜索](velvia-exact-axis-v1/report.md)三个未入围对照，未执行新增完整验收或速度测试。历史PDF范围不变，不宣称官方成绩或SOTA。

[通用精确单调API](separable-calibration-api-v1/README.md)集中11项合同通过并接入显式CLI方法，默认策略不变。[同家族四级先导](filmic-chain-calibrated-v1/report.md)发现旧链已精确、停止新增完整验收；另立[等距四级控制链](filmic-isometric-chain-v1/report.md)，在四张不同原表及逐级RGB8下，新17³完整256³/100图误差归零，标量/AVX2/C99一致。[独立性能](filmic-isometric-runtime-v1/report.md)保留18次交错同机调用，文件容量相对33³减少83.22%，同容量单线程略慢，不能称所有配置加速。[Velvia有界插值归因](velvia-interpolation-diagnosis-v1/report.md)显示单换算子或采样节点不能同时改善一般mean/p99，旧极端节点偏差远超纯量化；未产生新模型。

[R51](r51/README.md)记录有界CG续算：四个已成功配置保持16张旧模型字节，一个原失败m33模型恢复并通过CPU/CUDA/C99三条完整色域一致性检查。其RGB误差仍高，不替换质量冠军。五配置追加方法边界标签，比较账本保留原38条有效观测及1条失败，原矩阵分母不变。

[R50](r50/README.md)保存分片执行的一次集中验收、旧写入器受控退出检查点，以及45条R45/R47资格记录正式导入的凭据。2条新完整色域流精确复现原模型/输出/指标/23组探针，52条旧记录未重跑。新控制器最多4个普通子进程续跑；原7917项分母和数值版本不变，留出评估尚未执行。

[R47](r47/README.md)记录三个曲线家族的1458项训练容量搜索、54个旧原生均匀配置复现、45条新CPU/CUDA/C99完整色域流，以及135条留出前冻结的类别／预算指南。9/18源相对各自全13策略×3尺寸参照降低mean，5源同时节省节点存储；混合研究729个留出配置尚未评价，原7917项矩阵继续执行。

[R44](r44/README.md)记录四新策略的完整180组训练对照及117项全13策略容量控制，分开报告恒定链和非恒定源的收益。[R45](r45/README.md)为三个训练源完成6条完整色域流、600次标准图与多后端照片核对，并保留一个最差mean14.0382的本地精度失败；三条图像资格已在后续R50导入总账本。全13策略与留出评估仍未完成。

[R42](r42/README.md)保留2083项训练记录的固定快照和42/180组完整类别对照，明确保留并列、缺失与未执行留出状态。[R43](r43/README.md)补齐C99 ROM导出：两套已编译数组逐字节核对、两个完整色域流、四类目标对象和真实三线性拒绝；不新增速度或实体手机成绩。全量矩阵、联合规则冻结与留出评估仍在推进。

最新的同模型CPU后端配对比较为[R39](r39/README.md)：三类模型、三种后端、9项比较、162次计时；压力与17箱模型证实结构AVX2更快，clip模型未决。[R40](r40/README.md)把九项配置与完整色域正确性证明登记到逐case速度组，保留点最优、证实最快与耗时/模型内存Pareto。[全部结果](../../docs/r39-structured-performance.md)。两阶段不代表完整策略矩阵或实体移动设备验证，PDF仍为R27冻结范围。

最近包含完整100图及CPU/CUDA严格性能对照的阶段为[R34](r34/README.md)：R33新压力候选的完整色域/100图、五张自然照片及7对比较；新模型精度改善，但新旧模型速度差异未被证明。同16线程的SIMD/标量配对加速中位数2.07091倍。[R27](r27/README.md)仍为最近的完整PDF冻结范围，另含OpenColorIO对照。[R27完整PDF](../latest/problem16-latest-tested-report.pdf)。下文为历史探索报告的固定数据索引。

后续阶段另列：[R28完整扩展数据与账本](r28/README.md)、[R29首个case的27候选快照](r29/README.md)、[R30独立C99接口验收](r30/README.md)、[R31 AArch64大小端模拟执行](r31/README.md)。R29仍为完整5400计划的一部分；R30/R31不包含实体移动设备速度/功耗结论。这些新增阶段尚未写入R27冻结PDF。

新增：[R32格式集中门禁](r32/README.md)、[R33单调分箱和两级前瞻先导](r33/README.md)、[R34实际图像与严格性能](r34/README.md)。三个完成阶段分别保存证据；运行中的总账本不装入源码快照，防止将不同时刻的索引与观测拼成一份冻结账本。

[R35](r35/README.md)另完成C99/结构AVX2的统一入口、特性开关与集中正确性验收，没有新增配对性能结论。R36扩展计划另存`datasets/problem16-v1/strategy-extension-r36.json`；后续已完成开发720、校准720、回归357项，其余720项留出尚未执行，不能称2517项全部完成。

[R37报告持久化与证据恢复](r37/README.md)保留一次真实Windows共享冲突的修复和1条零像素重跑恢复。初版失败也归档，不改变整个矩阵未完成的状态。

归档范围更正：R28–R35的嵌套源码快照实际包含仓库已有五张Kodak参考照片及其评测版本；不包含完整合成语料、完整LUT或本机二进制。相应外部索引按实物标注，原压缩包字节不改。从R37起源码归档也排除这些版本化照片负载，避免每个阶段重复收录。

由 `scripts/build_typst_data.py` 从 Git `f73b8dd81a360521098ee985d68bcb3b548ccb19` 和独立日志 `32f23355ab678e0696725ac871762a5be7a0ce57` 生成。
包含 43 次运行、24 个当前候选、696 条逐图结果；原始日志按字节归档，生成器不修改 `logs/`。

| 文件 | SHA-256 |
| --- | --- |
| `run_records_exact.tar.gz` | `c2508b7102ab4b3bb00fb7bbea07f25ae551648f99fbe83abf32d25115d7af31` |
| `manifests_exact.tar.gz` | `cbdee2b59eb94eed019176cb5ab468eefa35aab01e050c7b1c4b64f63d9e2417` |
| `experiments_exact.tar.gz` | `df057ccd32cdaa03d02e4cb83d080eb0762c375f5c8a1904678901aabea519e2` |
| `ledger.csv` | `b59d7371f880db75780b5ffe6404823b31e8f968954112b1ad775737196884ba` |
| `image_results.csv` | `b11c2dd1f295264ae64d1b785ce6bcadf8d53a338f39e3ef12a1d46b89b9f636` |
| `cube_hotspots.csv` | `338714396d4adbcb4cdfc0168b987179c9fdcc010d9fbb2d2ee90e69651d8b88` |

原始图像和完整 LUT 约 1.8 GiB，保留在被 Git 忽略的 `data/`；本归档只保存清单和实验记录。
`run_records_exact.tar.gz` 包含运行目录中的 JSON、stdout、测试日志和代码差异；路径及字节不变。
本地补充：`paired-grid-contract-v1`保存成对节点的纯合成实现合同；`velvia-guarded-pair-v1`保存实际Velvia固定4+1拟合与未入围选择证据。二者不能替代完整精度验收，后者没有新增百图或原生性能结果。

本地后续：`velvia-error-mass-v1`为旧字节的完整质量归因；`rounding-interval-contract-v1`为合成目标/梯度合同；`velvia-rounding-interval-v1`和`velvia-photo-priority-v1`为两个分别冻结的真实拟合负结果，均未入围，无新增完整终验。

本地插值归因：`velvia-matched-operators-v1`分别拟合匹配的四面体/三线性；`velvia-cubic-lagrange-v1`的单一三次基未达到训练矩门槛，未评价探针。`monotone-axis-contract-v1`保存完整单元DP集中合同，`velvia-monotone-dp-v1`保存真实未入围结果。

本地后续归档：`velvia-alternating-integer-v1`保存固定三轮坐标/节点交替与未入围结果；`velvia-fixed-tetra-bound-v1`保存原固定坐标的有理MSE下界证书；`velvia-r-reflection-v1`保存唯一R反射同条件连续拟合的负结果。三者均无新完整输出、百图或运行时性能验收，不能替代已验收冠军。

本地下一阶段：`velvia-output-clipping-v1`只分析旧完整输出与60图频数的饱和相关性；`rgb-joint-grid-contract-v1`验证26个RGB联合方向；`velvia-rgb-joint-v1`保存单次真实提议及未入围结果。无新增完整精度或性能验收。

`emerald-calibrated-v1`完成另一可分离来源的17³实际模型，候选完整色域/百图误差均为零，5个原生后端与独立整数参考一致。包含三模型300条逐图与独立解析聚合；旧两基线cube指标是曲线卷积，未重映射旧cube。不新增四级或性能计时。

`velvia-channel-coordinates-v1`保存9块一次新表示与选择；`velvia-channel-coordinates-accept-v1`保存唯一候选完整精度，cube mean/p99约降5.84%/9.65%、100图mean降4.47%，逐图/audit局限完整披露。`channel-native-v1`另存独立C ABI的合同、单级/四级等距控制完整输出回执、实际应用与两阶段串行性能比较；新表示有内存及速度代价，默认不变。

`channel-frequency-transfer-v1`记录两图固定频数与118个中间反例，指出0843由重复灰色主导。`velvia-channel-nodes-v1`和`velvia-channel-blocks-v1`分别保存分通道坐标固定后的单点/2³块一次提议，均未达到额外双mean0.5%门槛，未做完整精度/native/性能验收。

`channel-continuous-floor-v1`保存三路权威几何的完整整数矩、连续解和精确盒下界；独立标准库审计通过。当前节点与clip连续可行点有16.76%未舍入均匀MSE空间，不等于真实RGB8/照片mean或p99收益。

`velvia-channel-global-nodes-v1`保存一次160步全局连续节点及三轮cap撤销；连续代理改善未转为真实RGB8收益，完整记录失败、离线内存和未执行范围。

`velvia-channel-joint-nodes-v1`保存最后一次8色26方向RGB联合提议及集中独立整数合同；相对3e5选择双mean仅降约0.107%，未入围，节点族收束，未执行新完整精度或性能验收。

`skylake-clang-static-v1`保留同源GCC/Clang对象级比较，信号不一致而未运行。`skylake-delta16-v2`保存无损坐标差压缩的55+88组合同、完整色域/百图零差、唯一80轮性能及门槛复算，本机1/4线程耗时降约12.0%/8.1%；[阶段说明](../../docs/stages/2026-10-20-skylake-delta16.md)。AMD结果不代表Skylake实测，独立缓存候选收益不相乘。

`skylake-server-entry-v1`保存纯标准库服务器入口、固定输入清单、独立Linux构建及12组完整色域/2112次边界比较/百图SHA回执。实际为同AMD的WSL2，正式性能分支未执行；最终本地传输ZIP约188MB，原始流不提交Git。[复现与限制](../../docs/stages/2026-10-20-skylake-server-entry.md)。

`skylake-delta-cache-v1`直接比较已有缓存与同缓存加无损坐标差，保存55/88/55/77组集中合同、完整域/百图、表槽、唯一80轮与参考对象相等证明；本机1/4线程配对耗时再降约21.1%/22.5%，严重波动完整保留。[阶段说明](../../docs/stages/2026-10-20-skylake-delta-cache.md)不把此结果换算为不同基线总加速或Skylake成绩。
