# 逐图分位预算与全节点补偿证据

[阶段说明](../../../docs/stages/2026-10-17-quantile-tail.md)。两次执行分别冻结于`cb10dd7`、`455975a`，保留旧失败；v2只重放v1接受步骤，不重启搜索，不更换预算。

- `case-summary.csv`：8条完整域/100图汇总，含mean/RMS/p99/max、CVaR及既有阈值比例。
- `photos-per-image.csv`：800逐图，其中300新执行、500显式复用；`photo-groups.csv`：24条60/20/20分组；`photo-regressions.json`：相对历史及混合初态的改善/持平/退化与最大退化。
- `constraint-diagnostics.json`：两例×两阶段的初/终全部计数条件、残余组数、max/p99类缺口与拒绝统计。缺口不是色差单位，verified不是feasible。
- `compensation-counterfactuals.json`：拆解首个成功主/辅助/整对修改的完整101组整数结果。Velvia两单改分别违反不同保护，合改通过；Lomo辅助单改也可接受，不能将两例都称为双节点必要。
- `epoch-v1/`与`epoch-v2/`：实际环境、冻结计划、日志、独立复核回执、`evidence.zip`及逐成员`archive-index.json`。ZIP保留所有原JSON约束/完整域证书/检查点、模型、原float64网格、数值源码ZIP；不纳入重复selected-stage1模型及重复逐例results。完整数值结果在根results中。文件路径保留实验原文，复核无需它们仍在原盘符。
- `native-parity.json`：8份回执（6新/2复用），三个新模型完整256³与独立整数oracle、标量/AVX2一致。
- `verification-sources.zip`：两个独立标准库验证器；`source-provenance.json`记录实际数值源、Git及当前源是否一致。v1 runner/搜索与当前v2源不同，以其执行快照为准。
- `contracts-v1.log`为4/4；`contracts-v2-first-failure.log`保留首次1/2失败；先改用完整桶范围后`contracts-v2-fixed.log`为2/2。发布核对再补齐短桶报告接口，恢复64桶反例，`contracts-report-bins.log`为2/2，覆盖原失败。`diagnosis.log`只做局部反事实，无重新优化。
- `post-measurement-audit.json`绑定发布前短桶报告修复、源码和针对性复测。原数值过程均用完整桶，原执行源码/模型/指标和首次归档哈希不改；`source-provenance.json`的current字段是归档当时快照，发布时差异以新审计为准。
- `quantile-repair-comparison.png`已目视检查；`integrity.json`绑定初始归档与发布前报告索引修正，不包含后来新增README。原始50MB流、完整表和大倒排留在忽略缓存，可重建核SHA。

无数值依赖复核（使用全新解压目录；以下新回执不能覆盖旧verification.json）：

```powershell
python -m zipfile -e report/data/quantile-tail-v1/epoch-v2/evidence.zip artifacts/quantile-evidence-check
python -m zipfile -e report/data/quantile-tail-v1/verification-sources.zip artifacts/quantile-verifiers
python -I -S artifacts/quantile-verifiers/verify_quantile_constraints.py --input artifacts/quantile-evidence-check --output artifacts/quantile-evidence-check/rechecked.json
```

Lomo缺口21577→7636、Velvia109092→3616，仍有45/28组未满足，不升级默认。全部距离为RGB欧氏码值距离，非CIEDE2000。官方Threshold未知，照片历史已观察，无四级比赛/盲测/SOTA/性能/实板声明。

Agent：Codex

Operator：WyEhNf

Task：逐图分位约束、联合补偿及误差原因分析

Status：阶段验收与归档完成，残余失败保留，Draft待审查
