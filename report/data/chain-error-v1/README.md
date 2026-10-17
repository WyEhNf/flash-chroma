# 四例误差归因与整数精化的冻结证据

结论、适用范围、环境和复现命令见[阶段报告](../../../docs/stages/2026-10-16-error-causes.md)。全部距离为 RGB 码值欧氏距离，非 Lab 指标。

| 文件 | 内容 |
| --- | --- |
| `plan.json`、`environment.json` | 实验前参数、来源、实际环境和源码身份；不续写 PR #9 旧运行 |
| `results.json` | 四例完整诊断、候选选择、最终指标与控制方案；包含负结果 |
| `case-summary.csv` | 8 条基线/候选全色域及 100 图指标 |
| `candidate-guard.csv` | 20 条 guard 选择指标与被拒绝候选 |
| `stage-attribution.csv` | 10 条逐级本地/传播/交互项 |
| `photos-per-image.csv` | 800 条逐图 mean/RMS/p99/max 与描述性阈值比例 |
| `explanations.json` | 固定权重必要误差证书、有限干预、控制方法的补充原生核验 |
| `native-parity.json` | 23 条原生全色域流的 SHA-256 与独立整数 oracle 一致性 |
| `models-and-counterexamples.zip`、`archive-index.json` | 70 个模型、选择记录和热点 PNG，逐文件 SHA-256；模型仅供研究复现，未登记成正式冠军 |
| `stage-error-attribution.png`、`hotspot-slices.png` | 科学图，已目视检查；不据切片代替完整色域结论 |
| `engineering-ci.json` | 工程提交 337a3dd 六项 CI 的来源和日志摘录 |

完整源 LUT 与 48 MiB 输出流留在本机 `artifacts/chain-error-cache` 和 `artifacts/chain-error-study-v1`，不随 ZIP 上传。真实 LUT 原文件、授权和哈希由 `assets/LUT` 保留；控制例由 hack-v2 冻结生成器恢复。研究中公开的每级模型均保留本级标签语义，运行时不使用复合表/残差标签。

源输入的统计泛化、官方阈值、未知摄影色彩域及实板性能均未在本阶段认证。全色域改善并未消除自然照片上的退化，三个真实案例的某些照片指标仍变差，详情在报告中逐项列出。
