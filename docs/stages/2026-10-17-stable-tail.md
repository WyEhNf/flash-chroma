# 固定参照下的尾部误差转移分析

Agent：Codex；Operator：WyEhNf；Task：PR #23 后续；Status：Completed（固定实验及误差归因完成，未取得新精度收益，Draft待审查）。

## 问题与本阶段范围

PR #23 从固定尾部缺口2097降至1614，却使100图均值及最差单图p99上升。原优化目标是各照片、各阈值的缺口总和，原mean/RMS保护参照是更早的历史/混合模型，因此允许近期成果之间相互牺牲。本阶段把PR #23已验证终态作为额外固定参照，以隔离这种误差转移；不替换原历史目标，不声称有限稀疏模型一定存在全指标改善解。

## 实现

- `stability.py` 冻结101组直方图与完整色域，增加mean、RMS、p99两个秩端点及max充分非退化条件。事务试探及回滚更新额外尾部计数。
- `rounded_budget.py` 与 `rounded_blocks.py` 复用真实RGB8单改统计；一臂只用更严格的mean/RMS预算排序，另一臂增加尾部计数排序。单改计数int32，组合先提升int64；支撑重叠时不能把相加估计当作验收。
- `quantile_repair.py` 保留原保护证书，另列稳定性拒绝及接受回执。`run_quantile_tail_study.py` 在热启动重放后冻结参照，保存最终稳定性证书。
- `verify_stability.py` 用标准库从最终完整直方图独立核对充分条件及旧参照绑定，不把中间回执存在说成独立重放。

mean以Q24距离整数上界不超过固定参照下界证明非增，或允许直方图完全相同。两者都是充分条件，可能保守拒绝实际没有退化的候选。p99两个端点均非增同样是充分条件。历史Delta-E仍是逐像素欧氏RGB码值距离，不是CIEDE2000。

## 冻结实验与测试目的

环境：Windows 11 10.0.26200，Ryzen 9 8945HX（16核32线程），RAM 33605316608字节；研究venv Python 3.12.14、NumPy 1.26.4、SciPy 1.15.2、Numba 0.60.0、llvmlite 0.43.0，Numba 4线程，BLAS/OpenMP 1线程。原生终验GCC 15.2 Release，标量/AVX2各单线程，程序SHA为`ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`。本阶段不计时比较性能。

合同测试目的：拒绝跨照片误差转移且正确回滚；独立展开全部节点±1核对额外尾部统计，覆盖接近频数上限及整数提升；覆盖新约束下公开三节点接受路径，并回归受影响的旧两/三节点路径。集中执行一次，失败时保留原日志并仅修复有证据的问题。

数值实验：固定 `stable-tail-guard-v1.json` 与 `stable-tail-aware-v1.json`，只比较Velvia一例，起点为47步、模型SHA `f803945e6f1bef7c1a3b57954749e918bf360f3dd486f1b7cba3b9c88c6c681d`，缺口1614。每臂最多32步/2轮，其他候选规模保持相同。80张完整照片、20选择样本及合并组用于反馈；20张审计照片只在终验观察，已在历史研究中见过，不宣称盲验。变化模型仅终态进行一次256³/100图/独立整数oracle/标量AVX2；未变化则严格核对SHA后复用旧证据。额外完整直方图用标准库复核。

## 两臂结果

合同一次8/8通过，用时9.03秒。源和计划先冻结于`84f1826`；guard运行记该提交，aware运行记`93f08ea`（仅增加归档脚本）；归档核对两臂全部实测数值源码同字节。归档入口`93f08ea`/`bfadee7`，独立局部归因入口`b12efbe`。

| 臂 | 起始/最终缺口 | 新接受 | 单/普通双/辅助双/三节点试探 | 辅助双首次判定 | 三节点首次判定 |
| --- | --- | ---: | --- | --- | --- |
| 只加稳定性保护 | 1614 / 1614 | 0 | 128 / 120 / 128 / 111 | 113照片拒绝、15缺口未降 | 90照片拒绝、21缺口未降 |
| 再加尾部计数排序 | 1614 / 1614 | 0 | 128 / 120 / 128 / 114 | 125照片拒绝、3缺口未降 | 114照片拒绝 |

两臂从同一47步起点生成1683个主提案，均在第一轮辅助失败后停止，未花完预设2轮。所有已记录辅助双/三节点候选都带有至少一项额外逐组mean和RMS失败，包括因缺口未下降而更早返回的候选；这是条件诊断，不把同一候选重复算作多个首次拒绝。尾部失败候选由双/三节点75/63个降到32/32个，mean/RMS冲突仍在。

只保护臂有7辅助对、19三节点在原照片保护下没有失败，却被新稳定性条件挡住；计数排序臂为6/17。这里未推定它们都能通过旧完整域保护。两臂仍22组/24项历史目标违反，max类缺口517、p99端点类1097。有限候选失败不能证明任意两/三节点、不同主提案或稀疏模型都无解。

最终模型均为起点同一SHA `f803945e6f1bef7c1a3b57954749e918bf360f3dd486f1b7cba3b9c88c6c681d`，没有重复完整映射；以下指标全部明确复用PR #23同字节终验。

| 方案 | 完整域mean | RMS | p99 | max | 100图mean | RMS | 最差单图p99 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 历史 | 1.031289 | 1.992443 | 7 | 54 | 1.123080 | 1.458911 | 7.071068 | 49 |
| PR23起点 / 两臂终态 | 0.981720 | 1.879300 | 7 | 54 | 1.033869 | 1.384165 | 7.141428 | 46.043458 |

## 真实退化还是保守界限

`diagnose_stable_tail.py`在两臂完成后，分别选取**已记录辅助候选中缺口最低的一例**，只独立重放其支撑并集并重建101组直方图。不是新增搜索、重拟合或扩大候选；不宣称它们是所有主提案的全局最优。

| 反例 | 支撑并集颜色数 | 候选缺口 | mean失败/经整数区间证明真实上升的组 | RMS上升的组 | 其中80张完整图mean/RMS上升数 |
| --- | ---: | ---: | --- | ---: | --- |
| 只加保护臂 | 7313 | 1117 | 48 / 48 | 38 | 36 / 27 |
| 尾部计数排序臂 | 6397 | 996 | 62 / 62 | 58 | 50 / 46 |

若新直方图距离和下界已经大于旧上界，即可证明真实mean上升，不依赖浮点显示精度。这两例全部mean失败都满足该条件，不能归咎于Q24的保守判据；其他未独立复算候选不据此一概而论。

第一例节点3336/3403/10107，第二例3403/11230/32532。共同主节点3403在多个照片分布中共享支撑。第二例把该节点改为`[6,17,22]`，总缺口虽降至996，却使div2k-0824的SSE增加106237、固定p99端点超限628像素。第一例该照片SSE也增加97697。小量热点颜色的收益会被节点共享支撑传播到其他照片，两个辅助的总预算补偿不能自动补齐每张照片的损失。

本阶段定位的原因是**总尾部缺口目标、共享节点支撑和逐组多指标保护之间的冲突**。尾部计数排序确实减少部分尾部违规，但并未解决平均误差/RMS冲突；未取得新的可接受精度收益。运行时算术错误、当前提案策略不足和有限网格表示能力不足仍须区分：这里有真实误差转移证据，没有得到稀疏模型表达能力的不可行性证明。

下一步更有依据的方向是让主提案阶段也感知逐组SSE/mean约束，例如从真实变化向量中找最坏受损组并构造联合方向。当前流程先按尾部热点选主改，再用两个辅助补偿，可能已错过满足多组约束的方向。应先冻结少量反例和有限候选实验，不能直接扩张成四/五节点扫描，也不能通过放宽阈值掩盖失败。本阶段未实现这一新方向。

## 验证、内存与可复现证据

两臂原标准库复核各通过202组初/终摘要及51份完整域证书；新增标准库复核各从101组和完整域终态直方图核对四指标充分条件及PR23参照绑定。解压归档后再次复核均通过，未载入NumPy/SciPy/Numba。保存回执不等于独立重放每个中间模型；51份证书含47步旧重放和最终检查，不是51个新接受步骤。

额外固定参照占159189728字节；持久数组共1167367126字节。SSE/Q24统计351895104字节，两臂SHA相同；aware新增尾部统计263921328字节，总参与数组1783183558字节。进程OS峰值guard为1823281152、aware为2074066944字节。额外计算/内存成本已披露，不作等计算量、运行时内存或加速声明。

[证据目录](../../report/data/stable-tail-v1)含4汇总、400逐图（全部指标复用）、4份复用原生回执、两臂46个归档成员、源码快照、阈值/完整直方图/模型/候选拒绝、两个局部反例及独立复核。没有新增原生运行，因此不能把旧标量/AVX2的0字节差异写成本轮新执行。C++、portable、embedded及SLUT格式未改，本轮不涉及新四级模型或实板。

复现命令中的`python`须使用前述venv。合同设`NUMBA_NUM_THREADS=4`；数值入口移除此变量，由runner设4，其余BLAS/MKL/OMP均设1。已有输出不得覆盖，复现须更换目录并同步参考路径。

```powershell
python -m pytest tests/test_stability.py tests/test_rounded_budget.py tests/test_three_node_search.py -q
python scripts/run_quantile_tail_study.py --plan experiments/stable-tail-guard-v1.json --output artifacts/stable-tail-guard-v1 --executable build-engineering-alignment/jshc.exe
python scripts/run_quantile_tail_study.py --plan experiments/stable-tail-aware-v1.json --output artifacts/stable-tail-aware-v1 --executable build-engineering-alignment/jshc.exe
python -I -S scripts/verify_quantile_constraints.py --input artifacts/stable-tail-guard-v1 --output artifacts/stable-tail-guard-v1/verification.json
python -I -S scripts/verify_quantile_constraints.py --input artifacts/stable-tail-aware-v1 --output artifacts/stable-tail-aware-v1/verification.json
python -I -S scripts/verify_stability.py --input artifacts/stable-tail-guard-v1 --reference-run artifacts/velvia-three-node-v1 --output artifacts/stable-tail-guard-v1/stability-verification.json
python -I -S scripts/verify_stability.py --input artifacts/stable-tail-aware-v1 --reference-run artifacts/velvia-three-node-v1 --output artifacts/stable-tail-aware-v1/stability-verification.json
python scripts/diagnose_stable_tail.py --guard artifacts/stable-tail-guard-v1 --aware artifacts/stable-tail-aware-v1 --warm artifacts/velvia-three-node-v1 --output artifacts/stable-tail-counterexamples-v1.json
python scripts/report_stable_tail.py --guard artifacts/stable-tail-guard-v1 --aware artifacts/stable-tail-aware-v1 --warm artifacts/velvia-three-node-v1 --output report/data/stable-tail-v1
```

## 工程与协作状态

已fetch目标远端github，main仍`dec1020`且在本分支祖先中。工程修复`337a3dd`包含在当前分支：证据内核绑定、历史报告基线及共有C99夹具的修复保留，未重写历史。PR #9及#12至#23正文、完整评论/review/行内线程、#7/#8正文及评论已读取并刷新，和此前检查相比无新增意见；搜索近期所有PR/issue，无新相关记录。#7/#9已修复项沿原验证，#8最终接口迁移/实板仍未完成。

Discussion #4原文由用户提供；本阶段连接器不允许该端点，网页访问仍404，无法检查最新回复，不把无法读取当作无问题。保持Draft，不执行合并或关闭issue。新阶段PR基于PR23头`c6a3df3`，中文提交/说明，不直接推主干；新头CI在PR正文补记实际结果。

官方数据和Threshold仍缺，全部照片历史已观察，不称独立盲验、未知输入泛化、SOTA或比赛四级成绩。无新精度提升或性能提升结论；默认和历史冠军保持原状态。
