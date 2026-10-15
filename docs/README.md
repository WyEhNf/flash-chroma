# 文档索引

当前开发与验收入口以根目录 [README](../README.md)、[TOOLCHAIN](../TOOLCHAIN.md)、[pixi.toml](../pixi.toml) 和 [CMakePresets.json](../CMakePresets.json) 为准。下列 R17–R27 文档保存对应阶段的方法与证据，里面的本机路径、分支名、构建命令和性能数字不是当前配置的承诺。

## 当前接口与规则

- [原题整理](../PROBLEM.md)、[选题判断与待确认规则](../DECISION.md)。
- [数据格式、来源与生成](../DATA.md)。
- [独立实验日志与交接](LOGGING.md)。
- [Agent 交流与协作规范](../AGENTS.md)。
- [日常摄影样本](../assets/photos/kodak/README.md)。

## 算法与验收演进

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

## 冻结报告与早期研究

- [R27 已测版本 PDF](../output/pdf/problem16-latest-tested-report.pdf)：对应本地固定数据和机器，不能当作官方成绩。
- [历史 Typst 报告与重建说明](../report/README.md)。
- [原始数据与哈希索引](../report/data/DATA_INDEX.md)。
- [早期路线说明](../ROUTES.md)、[早期评测记录](../EVALUATION.md)、[早期审计](../AUDIT.md)。
- [R15 工具链实验](../experiments/r15-zig-default-pixi.md)、[R16 路线探索](../experiments/r16-five-directions.md)。

冻结证据继续保留原有文件与路径，避免破坏报告引用。需要新结论时，应固定新提交、输入清单、模型、构建与机器后重新测量，而不是改写历史记录。
