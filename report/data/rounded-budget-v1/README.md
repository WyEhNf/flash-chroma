# 真实舍入预算补偿的固定对照

[阶段报告](../../../docs/stages/2026-10-17-rounded-budget.md)。数值源与计划先冻结`4562d96`，同v3初态、案例和搜索上限比较连续辅助与真实舍入预算排序；不增加全局轮次，不放宽任何原预算。归档/局部归因入口`0cd7bb1`。

- `case-summary.csv`：历史/v3/连续/舍入两例共8汇总，包含完整域mean/RMS/p99/max、CVaR和误差≥1/2/3/5比例。
- `photos-per-image.csv`为800逐图（100新/700显式复用），`photo-groups.csv`为24个分组；`photo-regressions.json`保留相对历史和v3全部改善/持平/退化及最坏回归。
- `budget-diagnostics.json`：同初态核对、全部残余条件、试探/接受来源、统计内存和成功节点对预测/实际SSE与Q24变化；不相交支撑可加证书逐步一致。
- `control/`与`rounded/`：各自环境、计划、日志、独立复核，以及31/55成员`evidence.zip`和`archive-index.json`；ZIP保留原结果/直方图/完整域证书/检查点/模型/原网格/数值源码。未放入重复逐例results或selected-stage1模型，原完整流留忽略缓存。
- `native-parity.json`：8份回执，2新/6明确复用；唯一新Lomo模型完整256³与整数oracle、标量/AVX2一致。
- `verification-sources.zip`：两个标准库验证器；各臂回执可在无NumPy/SciPy/Numba环境复核。verified表示保存代数一致，非尾部feasible。
- `source-provenance.json`及`contract-tests.log`：原数值源、当前源同字节与一次5/5合同（4.88秒）。`rounded-budget-comparison.png`已目视，`integrity.json`绑定首批归档。
- `pair-counterfactuals.json`、`pair-diagnosis.log`、`pair-diagnosis-sources.zip`：后加局部拆解Lomo两组已接受修改，独立整数根归约和模型SHA匹配，无新搜索、拟合或审计反馈；`archive-audit.json`绑定后加文件与README。

连续对照两例均零接受；新路径Lomo6817→2866（−57.96%），Velvia2097不变。Lomo两对辅助的80图真实SSE变化−49945/−58390，连续代理约−23324/−5167；同时改变统计与全部预算排序，不能只归因于单一组件。仍有34/22组条件违反，默认不升级。

无研究数值依赖的复核（新目录、回执不能覆盖原verification.json）：

```powershell
python -m zipfile -e report/data/rounded-budget-v1/rounded/evidence.zip artifacts/rounded-budget-check
python -m zipfile -e report/data/rounded-budget-v1/verification-sources.zip artifacts/rounded-budget-verifiers
python -I -S artifacts/rounded-budget-verifiers/verify_quantile_constraints.py --input artifacts/rounded-budget-check --output artifacts/rounded-budget-check/rechecked.json
```

全部距离为RGB欧氏码值距离，非CIEDE2000；官方Threshold未知，照片历史已观察，无四级比赛、盲测、SOTA、性能或实板声明。离线数组/峰值不能冒充运行时内存。

Agent：Codex

Operator：WyEhNf

Task：真实舍入预算与联合辅助排序对照

Status：阶段实现与验收完成，残余失败及离线内存代价保留，Draft待审查
