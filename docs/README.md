# 文档索引

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

- [R27 已测版本 PDF](../report/latest/problem16-latest-tested-report.pdf)：对应本地固定数据和机器，不能当作官方成绩。
- [历史 Typst 报告与重建说明](../report/README.md)。
- [原始数据与哈希索引](../report/data/DATA_INDEX.md)。
- [早期路线说明](../ROUTES.md)、[早期评测记录](../EVALUATION.md)、[早期审计](../AUDIT.md)。
- [R15 工具链实验](../experiments/r15-zig-default-pixi.md)、[R16 路线探索](../experiments/r16-five-directions.md)。

冻结证据继续保留原有文件与路径，避免破坏报告引用。需要新结论时，应固定新提交、输入清单、模型、构建与机器后重新测量，而不是改写历史记录。
