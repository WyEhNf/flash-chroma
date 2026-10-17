# Velvia两节点拒绝与三节点块证据

[阶段报告](../../../docs/stages/2026-10-17-exact-tail.md)。诊断冻结于`f2ccccc`，优化冻结于`a436ae9`。原128对候选、真实判定和统计SHA完全一致后才追加三节点；是新增搜索成本，不是等成本对照。

- `case-summary.csv`：历史/v3/两节点诊断/三节点最终4汇总，含全域mean/RMS/p99/max、CVaR、误差≥1/2/3/5比例。
- `photos-per-image.csv`：400逐图（100新/300显式复用）；`photo-groups.csv`：12分组；`photo-regressions.json`保留每项改善/持平/退化及最坏回归。
- `block-diagnostics.json`：原128对118照片/8全域/2尾部拒绝，三节点12次实际试探、六真子集和确认，全部接受步骤/预测与实际预算、残余条件和内存；原block115个去重候选，没有全试完。
- `two_node/`与`three_node/`：环境、冻结计划、日志、独立复核，19/25成员ZIP及索引。保留原JSON/直方图/全域证书/模型/检查点/原网格/数值源码ZIP；原完整流/表留忽略缓存，可恢复核SHA。
- `native-parity.json`：4份回执，2新/2复用；最终新模型完整256³与整数oracle、标量/AVX2一致。
- `verification-sources.zip`及各回执：标准库每例202组摘要，59/122份完整域证书复算；verified不是尾部feasible。
- `source-provenance.json`：各自实际源SHA/数值Git；控制源与当前代码不同，必须使用其快照。优化源与当前数值代码同字节。`contract-tests.log`为一次7/7（6.47秒）。
- `seven-subsets.json`、`seven-subsets.log`及`seven-subsets-sources.zip`：后验独立复算4021色支撑并集及80图/固定样本，七个非空子集的尾部/预算/判定一致，无新搜索或审计反馈。所有新增文件与README由`archive-audit.json`绑定。
- `three-node-comparison.png`已目视，`integrity.json`绑定首批归档。

第45步三节点3403/35927/35929合改缺口2097→1829，六真子集全被拒绝：主+35927违反80图RMS，主+35929违反全域RMS。结论只针对这组冻结值，不证明任意两节点无解；后续又调整节点，最终缺口1614。

总缺口降23.03%不等于全面改善：max类缺口371→517、照片最差p99 7.119617→7.141428、mean略升，22组仍违反，不升级默认。

无数值依赖复核（新目录、新回执，不覆盖原verification.json）：

```powershell
python -m zipfile -e report/data/exact-tail-v1/three_node/evidence.zip artifacts/three-node-check
python -m zipfile -e report/data/exact-tail-v1/verification-sources.zip artifacts/three-node-verifiers
python -I -S artifacts/three-node-verifiers/verify_quantile_constraints.py --input artifacts/three-node-check --output artifacts/three-node-check/rechecked.json
```

距离为RGB欧氏码值距离，非CIEDE2000；官方Threshold未知，照片历史已观察，无盲测、比赛四级、SOTA、性能或实板声明。

Agent：Codex

Operator：WyEhNf

Task：候选拒绝归因与有限三节点联合优化

Status：阶段验收与归档完成，残余失败及误差转移保留，Draft待审查
