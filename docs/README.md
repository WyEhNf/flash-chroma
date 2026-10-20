# 文档索引

[2026-10-20 五项指令级研究](stages/2026-10-20-skylake-instruction-study.md)：中值网络、EVEX-256、33³常量地址及两次有依据的组合均未过预设静态资格，保留全部对象/MCA证据；零新增数值与性能调用，不采用原型。

[2026-10-20 获证快路径补验](stages/2026-10-20-skylake-domain-signed.md)：四种网格、正负节点斜率与真正非共享坐标的48次有限整数比较通过，沿用原二进制，不重测性能。

[2026-10-20 服务器包恢复入口](stages/2026-10-20-skylake-packet-restore.md)：标准库从版本化小包与三个已有大流恢复114文件/339633805字节，全部SHA与已验包一致；不重复运行像素或性能。

[2026-10-20 完整域证书与隔离快路径](stages/2026-10-20-skylake-domain-proof.md)：不改模型/持久容量，构造时证明后省范围检查，1/4线程本机apply配对中位下降7.07%/5.10%；一次完整域/100图及80轮输出SHA通过，模板版静态失败保留，Skylake待测。

[2026-10-20 坐标与节点局部性](stages/2026-10-20-skylake-coordinate-locality.md)：共享顶点排序覆盖不足、端点压缩条件不成立、首级节点重排仅约1%缓存行改善；仅切换服务器调度生成相同对象，四项均停止，零新增性能调用。

[2026-10-19 最新精度与后端结果](stages/2026-10-19-precision-latest.md)汇总当前已验模型、误差来源和速度代价；新研究方案未自动替换公共默认。

当前开发与验收入口以根目录 [README](../README.md)、[TOOLCHAIN](../TOOLCHAIN.md)、[pixi.toml](../pixi.toml) 和 [CMakePresets.json](../CMakePresets.json) 为准。下列阶段文档保存对应阶段的方法与证据，里面的本机路径、分支名、构建命令和性能数字不是当前配置的承诺。

## 当前接口与规则

- [合并数据集 v1](../datasets/problem16-unified-v1/README.md)：274 个 LUT case、455 份图片内容；保留原身份和划分，提供分队列清单、哈希核对及原合成图恢复。[第二批压力扩展](../datasets/problem16-hack-v2/README.md)追加三维峰谷、斜薄带、周期与舍入/串联场景。

- [hack image/LUT 压力子集](../datasets/problem16-hack-v1/README.md)：独立的可复现配方、边界图片与小型整数回放；[验收口径](../datasets/problem16-hack-v1/acceptance.json)明确区分运行时差异、近似误差与参考跳变，完整扫描尚未执行。

- [原题整理](../PROBLEM.md)、[选题判断与待确认规则](../DECISION.md)。
- [数据格式、来源与生成](../DATA.md)。
- [独立实验日志与交接](LOGGING.md)。
- [Agent 交流与协作规范](../AGENTS.md)。
- [日常摄影样本](../assets/photos/README.md)。

## 算法与验收演进

近期阶段： [工程对齐](stages/2026-10-16-engineering-alignment.md)、[四例误差归因](stages/2026-10-16-error-causes.md)、[有界拟合与四级联合选择](stages/2026-10-17-joint-box-objective.md)。最新算法阶段在固定Cinema链取得全色域/100图改善，同时保留两个单级负结果和四张图的max回归；没有替换默认方法。

后续[完整训练颜色约束与尾部修复](stages/2026-10-17-tail-repair.md)以5个节点修复14色反例，使固定100图的四项精度均逐图优于原始基线；相对联合版本仍有均值成本与9张图的max退化，保留两种候选与完整证据。

最新[完整域保护与双节点前瞻](stages/2026-10-17-full-domain-guard.md)保留单节点停滞负结果，用整数根号界严格保护全部256³颜色，再通过双节点联合选择取得更低全域mean与尾部。固定100图仍有相对PR14的逐图冲突，默认策略未改。

| 阶段 | 内容 | 文档 |
| --- | --- | --- |
| R17 | 整数精化、模型缓存与 CPU 部署 | [算法](r17-algorithm.md)、[交付](r17-delivery.md)、[阶段结果](r17-optimization-results.md) |
| R18 | 需求、算法与 CPU/CUDA 接入 | [需求](r18-requirements.md)、[算法](r18-algorithm.md)、[CPU](r18-cpu.md)、[GPU](r18-gpu.md) |
| R19 | 统一 CLI 与严格验收 | [交付与结果](r19-delivery-results.md) |
| R20 | 实际图片路径、位深与全色域审计 | [正确性审计](r20-correctness-audit.md) |
| R21 | 边界拟合 | [方法与证据](r21-boundary-fitting.md) |
| R22 | 可分离结构拟合 | [方法与证据](r22-structured-fitting.md) |
| R23 | CUDA 内存与测速路径核验 | [方法与证据](r23-cuda-memory.md) |
| R24 | 完整节点支撑拟合 | [方法与证据](r24-supported-fitting.md) |
| R25 | 精确全色域拟合 | [方法与证据](r25-full-domain-fitting.md) |
| R26 | 箱约束拟合 | [方法与证据](r26-box-constrained-fitting.md) |
| R27 | 阶梯插值与可达布点 | [方法与证据](r27-step-interpolation.md) |

## R28–R51 分类语料、优化与端侧研究

当前全量矩阵尚未完成，停止快照与未完成事项见[研究进展](research-progress-r28-r51.md)及[机器可读检查点](../datasets/problem16-v1/matrix-checkpoint.json)。下列文档分别保留其阶段结论，不代表后续完整矩阵通过。

2026-10-16 远端同步的构建、首次门禁与修复后复查记录见 [R52 整合证据](../report/data/r52/README.md)。本次仅验证整合，未新增性能结论。

| 阶段 | 内容 | 文档 |
| --- | --- | --- |
| R28–R29 | 分类语料、探针、逐case账本与全量计划 | [数据程序](r28-corpus-program.md) |
| R30–R35 | C99、ARM模拟、格式、分箱与结构后端 | [C99部署](r30-portable-runtime.md)、[格式](r32-format-contract.md)、[分箱](r33-monotone-bins.md)、[严格结果](r34-candidate-results.md)、[结构运行时](r35-structured-runtime.md) |
| R37–R42 | 报告恢复、后端配对性能、规则冻结与训练比较 | [持久化](r37-report-recovery.md)、[性能](r39-structured-performance.md)、[矩阵与规则](r41-matrix-resume.md)、[类别对照](r42-training-comparison.md) |
| R43–R45 | ROM部署、新策略适用区域及图像边界 | [ROM](r43-rom-export.md)、[新策略](r44-new-policy-regions.md)、[实际图像](r45-representative-images.md) |
| R47–R51 | 混合容量、调度归并与CG恢复 | [混合容量](r47-mixed-capacity.md)、[调度](r50-case-shards-and-canonical-import.md)、[求解与精度边界](r51-bounded-cg-recovery.md) |

## 冻结报告与早期研究

- [2026-10-18 联合网格与节点](stages/2026-10-18-joint-grid.md)：Velvia完整域及百图改善，未泛化成功的对照保留。
- [2026-10-18 真实RGB8与完整照片测度](stages/2026-10-18-rounded-grid.md)：采样偏差、整数目标及max退化反例。
- [2026-10-18 Cinema四级链优化](stages/2026-10-18-cinema-rounded.md)：完整域mean降低14.09%、p99降低7.07%，百图mean降低12.89%，完整三后端一致；另列前缀不可逆混叠归因。仅本地研究，暂不创建PR。
- [2026-10-19 首级与后缀保持度量](stages/2026-10-19-cinema-prefix.md)：保留本级损失、训练测度与共享节点的未入围对照。
- [2026-10-19 单调坐标校准](stages/2026-10-19-axis-calibration.md)：四级链累计完整域mean/p99降低20.42%/12.10%、百图mean降低17.72%，模型字节数保持，插值函数族扩大。
- [2026-10-19 同机速度与内存](stages/2026-10-19-precision-performance.md)：三版模型18次原生交错比较，显式AVX2、1/4线程、完整百图原始计时；无额外模型内存成本，不作微小差异显著加速声明。
- [2026-10-19 Lomo整数对照](stages/2026-10-19-lomo-rounded.md)：均值改善却尾部退化，未入围，未执行新增完整终验。
- [2026-10-19 校准坐标后的节点](stages/2026-10-19-calibrated-nodes.md)：归因后固定四扫，样本收益不足，不做完整验收。
- [2026-10-19 精确舍入事件搜索](stages/2026-10-19-exact-axis.md)：同坐标边界内约75万项合同通过，完整训练目标小幅下降，选择样本mean/p99未入围，停止同范围搜索。
- [2026-10-19 Velvia坐标对照](stages/2026-10-19-velvia-exact-axis.md)：加入逐原色尾部保护，照片样本mean仅降约0.3%，不入围、不完整终验。
- [2026-10-19 Filmic解析校准](stages/2026-10-19-filmic-calibration.md)：同SHA重建PR41，33³完整域与百图误差归零，17³照片mean降低90.68%，限定严格可分离特例。
- [2026-10-19 Filmic直接单调约束](stages/2026-10-19-filmic-direct-monotone.md)：另立阶段排除保守静态边界，17³也完整验零，仍固定节点/idx/网格与总偏移。
- [2026-10-19 精确单调API](stages/2026-10-19-separable-calibration-api.md)：11项集中合同，覆盖通道置换/共享输入轴、精确可行与明确回退。
- [2026-10-19 同家族四级先导](stages/2026-10-19-filmic-chain-calibrated.md)：原链已被后缀消去局部误差，停止完整验收，不记作新收益。
- [2026-10-19 等距四级控制链](stages/2026-10-19-filmic-isometric-chain.md)：统一CLI/不可变缓存，四张不同原表与逐级RGB8，17³完整域/百图误差归零，标量/AVX2/C99一致。
- [2026-10-19 解析17³性能](stages/2026-10-19-calibrated-performance.md)：18次交错原生比较，4线程2.55ms/图，容量相对33³减少83.22%；同容量单线程略慢，不称所有配置加速。
- [2026-10-19 Velvia插值归因](stages/2026-10-19-velvia-interpolation.md)：同节点换三线性及源浮点顶点对照，区分最坏色节点偏移与一般p99残差。
- [2026-10-19 Velvia成对节点](stages/2026-10-19-velvia-guarded-pair.md)：固定逐色上限的4+1调整，原色样本mean/p99下降但照片mean未达3%，不完整终验。
- [2026-10-19 Velvia残差分布](stages/2026-10-19-velvia-error-mass.md)：照片mean主要由广泛小误差承载，局部G上沿的条件改善上界不足3%。
- [2026-10-19 舍入区间目标](stages/2026-10-19-velvia-rounding-interval.md)：一次集中梯度合同与固定连续提议；部分尾部改善但真实硬cap违规，拒绝采用。
- [2026-10-19 照片优先测度](stages/2026-10-19-velvia-photo-priority.md)：同预算单一权重对照，选择集未优于均衡质量，不扫描权重。
- [2026-10-19 匹配算子拟合](stages/2026-10-19-velvia-matched-operators.md)：相同完整均匀L2和网格各自拟合，三线性仍未改善一般探针，不以同节点诊断代替公平对照。
- [2026-10-19 唯一三次基](stages/2026-10-19-velvia-cubic-lagrange.md)：训练矩MSE恶化6.45%，未触发探针或完整测试。
- [2026-10-19 完整单元单调DP](stages/2026-10-19-velvia-monotone-dp.md)：解除静态坐标边界后照片样本改善约2.46%，未入围。
- [2026-10-19 整数节点/坐标交替](stages/2026-10-19-velvia-alternating-integer.md)：固定三轮后照片样本mean约降2.67%，原门槛失败且不追加轮数。
- [2026-10-19 固定坐标表达能力证书](stages/2026-10-19-velvia-fixed-tetra-bound.md)：整数矩与有理运算证明原固定坐标四面体不可能全域RGB8验零；不等于当前模型接近最优，不外推新函数族。
- [2026-10-19 唯一R反射](stages/2026-10-19-velvia-r-reflection.md)：改变体对角线后同条件连续MSE恶化52.01%，按预定门槛停止，没有生成新模型或追加完整测试。
- [2026-10-19 输出裁剪归因](stages/2026-10-19-velvia-output-clipping.md)：旧完整字节显示照片73.53%距离误差来自内部输出组，不能把尾部端点关联当作裁剪因果。
- [2026-10-19 节点RGB联合方向](stages/2026-10-19-velvia-rgb-joint.md)：集中解析和整数合同通过；真实单扫只有很小收益，仍未入围。
- [2026-10-19 Emerald精确17³](stages/2026-10-19-emerald-calibrated.md)：PR41第二个可分离来源，实际完整域/百图验零，5原生后端一致；相对33³文件减少83.22%，没有新性能计时。
- [2026-10-19 分输出坐标](stages/2026-10-19-velvia-channel-coordinates.md)：同33³节点的9块单调DP，固定样本选择入围，增加坐标容量与计算。
- [2026-10-19 新表示完整精度](stages/2026-10-19-velvia-channel-coordinates-accept.md)：cube mean/p99约降5.84%/9.65%、百图mean降4.47%；保留audit与逐图退化。
- [2026-10-19 原生落地及SIMD代价](stages/2026-10-19-channel-native.md)：单级/四级完整native一致，packed实现较首版耗时降约21%；相对原2dd仍慢约44%，4线程4.83ms/图。

- [R27 已测版本 PDF](../report/latest/problem16-latest-tested-report.pdf)：对应本地固定数据和机器，不能当作官方成绩。
- [历史 Typst 报告与重建说明](../report/README.md)。
- [原始数据与哈希索引](../report/data/DATA_INDEX.md)。
- [早期路线说明](../ROUTES.md)、[早期评测记录](../EVALUATION.md)、[早期审计](../AUDIT.md)。
- [R15 工具链实验](../experiments/r15-zig-default-pixi.md)、[R16 路线探索](../experiments/r16-five-directions.md)。

冻结证据继续保留原有文件与路径，避免破坏报告引用。需要新结论时，应固定新提交、输入清单、模型、构建与机器后重新测量，而不是改写历史记录。

- [2026-10-20 精确调色板编译](stages/2026-10-20-skylake-palette.md)：相对已验修订16，本机1/4线程吞吐提高84.99%/90.62%，完整输出零差；额外8.39MB、准备成本和Skylake待验收分别披露。
- [2026-10-20 精确例外池](stages/2026-10-20-skylake-exception.md)：直接对修订22，本机1/4线程吞吐再提高70.91%/70.90%，copy+apply提高62.40%/54.32%，完整输出零差；额外约1.08MB，Skylake与规则仍待验收。

- [2026-10-19 两图频数归因](stages/2026-10-19-channel-frequency-transfer.md)：固定反例显示单图重复颜色可放大小码值退化，未加入训练。
- [2026-10-19 分通道节点精化](stages/2026-10-19-velvia-channel-nodes.md)、[整块节点平移](stages/2026-10-19-velvia-channel-blocks.md)：两种各一次有限提议增量不足，未追加完整测试。

- [2026-10-19 新几何连续空间](stages/2026-10-19-channel-continuous-floor.md)：三路完整整数矩与独立有理证书，区分连续可行空间和RGB8部署收益。

- [2026-10-19 全局盒节点提议](stages/2026-10-19-channel-global-nodes.md)：连续代理下降，但量化及cap撤销后的真实RGB8目标回退，未入围；未做完整验收。

- [2026-10-19 分通道几何的26方向联合节点](stages/2026-10-19-channel-joint-nodes.md)：用共享cube的奇偶角唯一性合并三路不同权重，真实整数目标提议增量仍不足；节点邻域研究收束。

- [Cinema分输出坐标](stages/2026-10-19-cinema-channel-suffix-coordinates.md)与[后缀联合节点](stages/2026-10-19-cinema-channel-suffix-joint-nodes.md)：分别保留mean门槛不足和max回退的固定负结果。
- [旧cap单色解释](stages/2026-10-19-cinema-cap-anchor-diagnosis.md)与[当前锚点修正](stages/2026-10-19-cinema-current-anchor.md)：首级1码值传播及全域统一约束，未把guard反例加入训练。
- [Cinema完整终验与实际四级成本](stages/2026-10-19-cinema-current-anchor-accept.md)：百图mean全部改善，尾部代价与约46%运行成本分列。
- [节点读取复用负结果](stages/2026-10-19-channel-runtime-reuse.md)与[固定四级专门化](stages/2026-10-19-channel-runtime-specialized.md)：两项不同假设各自冻结、各一次同机比较，不混合计时或隐去失败。

- [2026-10-20 时间优化阶段交付](stages/2026-10-20-skylake-runtime-delivery.md)：以Skylake为最终目标的本机研究，四候选各自冻结验证；缓存候选本机耗时降约52%，服务器与官方派生缓存许可仍待验收。
- [轴表打包](stages/2026-10-20-skylake-packed.md)、[精确16位乘加](stages/2026-10-20-skylake-madd.md)、[精确binary32](stages/2026-10-20-skylake-float.md)：保持字节一致但未达本机性能门槛，保留负结果。
- [有界精确后缀缓存](stages/2026-10-20-skylake-suffix-cache.md)：同模型完整输出一致，Windows/AMD性能、额外容量/准备时间及WSL/Linux可移植性分列。
- [批入口描述符快照](stages/2026-10-20-skylake-snapshot.md)：静态指令减少却增加栈访存，MCA信号不一致，停止于静态阶段，没有数值或性能测试。
- [按阶段遍历像素块](stages/2026-10-20-skylake-stage-major.md)：同模型字节一致、中位耗时下降，但一个4线程进程退化超限，按原门槛拒绝，不追加计时。
- [首级/后缀单边界拆分](stages/2026-10-20-skylake-prefix-split.md)：单线程下降约4.34%，4线程配对中位未改善且单进程退化超限，不采用，停止切点搜索。
- [同源Clang静态研究](stages/2026-10-20-skylake-clang-static.md)：MCA信号不一致，保留对象与汇编，未进入运行验收。
- [无损有符号坐标差压缩](stages/2026-10-20-skylake-delta16.md)：完整输出一致，本机1/4线程耗时降约12.0%/8.1%，模型容量减少3072字节，Skylake实测待完成。
- [服务器固定入口与Linux验证](stages/2026-10-20-skylake-server-entry.md)：标准库入口、整批/逐图原生调度及固定传输包；WSL完成12组完整色域、2112次边界比较与百图SHA核验，正式Skylake性能未执行。
- [缓存与坐标差的直接组合比较](stages/2026-10-20-skylake-delta-cache.md)：以已有缓存为参考，完整输出一致，本机1/4线程配对耗时再降约21.1%/22.5%；保留进程及首组波动，不乘算不同阶段收益。
- [缓存范围简化的静态停止](stages/2026-10-20-skylake-cache-range-static.md)：R凸组合界及16位判定减少13条指令，但MCA信号不一致，未执行数值或性能，不采用。
- [四后端统一入口与同场比较](stages/2026-10-20-skylake-server-matrix.md)：WSL/AMD四库24组完整色域、4224次边界比较及唯一320轮；缓存单独启用通过本轮四场景门槛，组合虽中位耗时下降约55%–63%，仍因四线程整批单进程退化未全面通过，不重测覆盖。
- [软件gather及坐标排序结构](stages/2026-10-20-skylake-scalar-gather-static.md)：实验SIMD对象消除gather却失去四级融合，静态停止未运行；固定模型存在跨通道严格排序反转，不能无条件共用几何。
- [缓存直接写回](stages/2026-10-20-skylake-packed-store.md)：完整输出一致、容量不变，唯一80轮1线程未达3%改善，4线程回退且最差进程增加28.13%，不采用；保留完整CFG及MCA与实测差异。
- [共享轴地址预计算与输入结构](stages/2026-10-20-skylake-axis-preweight-static.md)：少6次乘法但完整静态周期/吞吐下界变差，未运行；固定100图首级后约16.03%的8像素包同色，后续精确后缀方案见下一阶段。
- [首级同色后缀快路](stages/2026-10-20-skylake-uniform-suffix-static.md)：完整覆盖两类首级各216条同色及一条普通路径；实际普通包成本升约10.26%，16.03%覆盖不足以抵消，静态停止，未执行图像或性能测试。
- [不重叠读取域与restrict](stages/2026-10-20-skylake-restrict-static.md)：少46/51条循环指令但栈压力上升，两族周期/吞吐信号不一致，未达预定门槛，静态停止，没有运行候选。
- [缓存沿R连续排列](stages/2026-10-20-skylake-r-contiguous.md)：表值/容量相同，完整输出一致；唯一80组的1/4线程配对中位耗时降3.29%/6.84%，但一个进程回退3.24%超过2%，整体不采用，保留静态比较器修正及全部波动。
- [缓存布局服务器独立入口](stages/2026-10-20-skylake-layout-server.md)：冻结4/13双库与逐轮输出核验；WSL通过3432次有限比较、12组完整域和16组百图调度，正式160组性能与Skylake未执行，原四方案包不变。
- [R连续与无损半字组合](stages/2026-10-20-skylake-compact-cache-static.md)：逐块行数再降10%–16%，但实际模型静态周期比1.03746且其他路径也回退；八候选路径全部保留，静态停止，没有加载或计时。
