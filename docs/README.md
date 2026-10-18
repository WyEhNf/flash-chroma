# 文档索引

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

- [2026-10-19 两图频数归因](stages/2026-10-19-channel-frequency-transfer.md)：固定反例显示单图重复颜色可放大小码值退化，未加入训练。
- [2026-10-19 分通道节点精化](stages/2026-10-19-velvia-channel-nodes.md)、[整块节点平移](stages/2026-10-19-velvia-channel-blocks.md)：两种各一次有限提议增量不足，未追加完整测试。

- [2026-10-19 新几何连续空间](stages/2026-10-19-channel-continuous-floor.md)：三路完整整数矩与独立有理证书，区分连续可行空间和RGB8部署收益。

- [2026-10-19 全局盒节点提议](stages/2026-10-19-channel-global-nodes.md)：连续代理下降，但量化及cap撤销后的真实RGB8目标回退，未入围；未做完整验收。

- [2026-10-19 分通道几何的26方向联合节点](stages/2026-10-19-channel-joint-nodes.md)：用共享cube的奇偶角唯一性合并三路不同权重，真实整数目标提议增量仍不足；节点邻域研究收束。

- [Cinema分输出坐标](stages/2026-10-19-cinema-channel-suffix-coordinates.md)与[后缀联合节点](stages/2026-10-19-cinema-channel-suffix-joint-nodes.md)：分别保留mean门槛不足和max回退的固定负结果。
- [旧cap单色解释](stages/2026-10-19-cinema-cap-anchor-diagnosis.md)与[当前锚点修正](stages/2026-10-19-cinema-current-anchor.md)：首级1码值传播及全域统一约束，未把guard反例加入训练。
- [Cinema完整终验与实际四级成本](stages/2026-10-19-cinema-current-anchor-accept.md)：百图mean全部改善，尾部代价与约46%运行成本分列。
- [节点读取复用负结果](stages/2026-10-19-channel-runtime-reuse.md)与[固定四级专门化](stages/2026-10-19-channel-runtime-specialized.md)：两项不同假设各自冻结、各一次同机比较，不混合计时或隐去失败。
