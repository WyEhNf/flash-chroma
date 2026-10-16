# 全颜色分位提案及下界松弛证据

[阶段报告](../../../docs/stages/2026-10-17-global-quantile.md)。实际数值源/计划冻结在`c34bf79`，从PR20的v2检查点只重放20/32个已接受步骤，再新增4/12步。原轴表、原混合初态和所有预算不变。

- `case-summary.csv`：历史/原混合/v2/v3共8汇总，含完整域mean/RMS/p99/max、CVaR和既有阈值比例。
- `photos-per-image.csv`：800逐图，200新/600显式复用；`photo-groups.csv`为24条60/20/20分组；`photo-regressions.json`列相对历史和v2的改善/持平/退化及最大退化。
- `global-diagnostics.json`：全局下界负提案数量、实际单/双候选、下界松弛、保护拒绝、接受来源及全部残余条件；明确全局2轮已耗尽，不能将最终热点停滞当成全局无解。
- `evidence.zip`及`archive-index.json`：62个原执行成员，含原结果/直方图/完整域证书、全部新检查点、warm重放模型、原float64网格及数值源码ZIP；不纳入重复selected-stage1模型或逐例重复results。warm父证据仍在PR20归档，不改写。
- `environment.json`、`plan.json`、`experiment.log`、`contract-tests.log`：实际环境、冻结参数、原日志与4/4合同。
- `native-parity.json`：两个新模型完整256³与独立整数oracle、标量/AVX2一致，共4份新回执。
- `verification.json`、`verification-sources.zip`：标准库独立复核每例202组摘要、全部保存的111/211份完整域证书；verified不是feasible。
- `source-provenance.json`：全部执行源码/当前字节及归档工具SHA。`global-quantile-comparison.png`已目视检查，`integrity.json`绑定首批归档。
- `bound-gap-decomposition.json`、`bound-diagnosis.log`及`bound-diagnosis-sources.zip`：后验只重放16个原接受步骤，四个全局修改的乐观松弛逐条件分解；每步模型SHA及最终101组直方图吻合，没有新搜索或审计反馈。后加文件/README由`archive-audit.json`绑定。

下界不是收益预测。Lomo步骤21下界−802、真实−73，差729来自活跃截断；Velvia步骤39下界−278、真实−5，差273中130来自新触发条件、143来自活跃截断。原目标总缺口可下降而个别条件恶化，全部失败保留。

无研究数值依赖的复核（使用全新解压目录）：

```powershell
python -m zipfile -e report/data/quantile-global-v1/evidence.zip artifacts/quantile-global-check
python -m zipfile -e report/data/quantile-global-v1/verification-sources.zip artifacts/quantile-global-verifiers
python -I -S artifacts/quantile-global-verifiers/verify_quantile_constraints.py --input artifacts/quantile-global-check --output artifacts/quantile-global-check/rechecked.json
```

Lomo缺口7636→6817，Velvia3616→2097，仍有43/22组违反，不升级默认。距离均为RGB欧氏码值距离，非CIEDE2000；官方Threshold未知，照片历史已观察，无四级比赛/盲测/SOTA/性能/实板声明。

Agent：Codex

Operator：WyEhNf

Task：全颜色候选覆盖与截断下界误差归因

Status：阶段实现与验收完成，残余失败和搜索预算边界保留，Draft待审查
