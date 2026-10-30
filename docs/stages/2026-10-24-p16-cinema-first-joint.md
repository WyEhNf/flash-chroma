# 首级完整正支撑上的一次八色联合尝试

Agent：`/root/tail`。Operator：本任务用户。状态：完成固定单扫，严格 max49 未达，不晋级、不切默认。

上一阶段证明固定几何与后缀下任意单个首级物理节点最多覆盖 32/116 个原始 max50 输入。本阶段进一步允许这 116 点触及的全部 86 个物理节点在一次八色扫描中共同变化，仍固定原 `max_first` 的首级 Q16 轴、904e/95cb/5b8 后缀及原 60 图整数频数。目标为 max²50→49，八项绝对预算全部相对原 `max_first`，没有借用后续 mean-only 或四轮训练模型。

协议见 `experiments/p16-cinema-first-joint-v1.json`。每个节点仍只比较相同的52项方向，最多应用一次；八色按物理节点三轴奇偶和编号固定顺序处理，不追加轮。紧凑变动设计中，选中节点外的权重设为零，合法占位索引不能产生修改；baseline 未舍入累加值保留全部顶点贡献。固定逐点 cap 为 `max(49,原d²)`，因此允许消除旧 max50，但不能制造新的50。

节点提案必须保持全域及原60图合并的 mean、RMS、p99、最差1% CVaR 八项指标不超过原始绝对预算。选择先减少 max50 计数；计数相同时，仅在两范围 mean 之和严格下降时接受非零移动，为后续节点积累已经取得的余额。完整52项接受/拒绝原因、每个节点和每色结果均保留。该方法是有限贪心，不是联合整数全局最优。

真实完整正支撑并集沿用已独立认证的70,571个RGB8输入，其余16,706,645个输入的整数直方图完全固定。单独断言支撑外全域和训练直方图的 `hist[50]==0`，确认全部116个原始热点均包含在变动支撑中。每色结束以独立uint64前向重算完整并集，查已完整认证后缀，再加支撑外固定直方图恢复完整16M域与47,185,920个训练像素的全部指标。八次核对均为零差异，同色正支撑互斥，外节点零权重合同通过。

| 范围 | 指标 | 原max_first | 一次八色后 |
| --- | --- | ---: | ---: |
| 全域 | mean | 0.7990738071534367 | 0.7990305585593758 |
| 全域 | RMS | 1.1976684589597302 | 1.1975855936507724 |
| 全域 | p99 | 3 | 3 |
| 全域 | max² | 50 | 50 |
| 全域 | 最差1% CVaR | 4.029054534445704 | 4.02772176485185 |
| 原60图合并 | mean | 0.6823481783784588 | 0.6823467670950999 |
| 原60图合并 | RMS | 1.1366130440332765 | 1.1366104523004315 |
| 原60图合并 | p99 | 3.4641016151377544 | 3.4641016151377544 |
| 原60图合并 | max² | 50 | 50 |
| 原60图合并 | 最差1% CVaR | 4.303192100572805 | 4.303170756453442 |

共58/86个节点接受修改，max50计数逐色为107、104、102、98、96、93、92、91，起点为116。所有八项预算保护，但p99/max没有严格改善，因此按预注册保留负例，不继续扫轮、不进入新的全四级/原生/百图终验，也不替换正式模型。保存的候选仅供复核，不作为当前最优起点。

Windows x86-64主机与项目Python3.12环境上，有限17/33节点合同覆盖外节点占位、同时多节点修改、同色互斥以及独立52方向选择。真实单扫约2.52秒，当时共享主机进行质量工作，不能作为性能比较。没有测量新的运行时吞吐或进程RSS，旧分输出坐标研究表示的官方许可仍未知。

主要实现为 `python/lutlab/channel_first_joint.py` 及 `scripts/{check,run,audit}_cinema_first_joint.py`。独立审计已另外从原始完整流和原60图频数重建支撑外直方图，再逐色uint64重放与日志核对，八色完整并集和最终模型均通过；它不重新搜索4472项选择优先序，不以这个审计冒充新的原生或逐图验收。

精简归档为 [report/data/p16-cinema-first-joint-20261024](../../report/data/p16-cinema-first-joint-20261024)，包含十份原件、18项冻结源、五份未晋级模型原件及全部4472项方向接受/拒绝记录。完整正支撑与后缀沿用上一阶段归档，以manifest SHA明确关联，未重复打包；当前候选的nodes、所有固定坐标和后缀身份可独立复核。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_joint.py --output artifacts/cinema-first-joint-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/run_cinema_first_joint.py --contract artifacts/cinema-first-joint-contract-v1.json --output artifacts/cinema-first-joint-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_joint.py --study artifacts/cinema-first-joint-v1 --output artifacts/cinema-first-joint-independent-v1.json
```
