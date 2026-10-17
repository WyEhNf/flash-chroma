# 候选拒绝归因与真实尾部联合搜索

承接PR22，Lomo缺口2866、Velvia2097，后者在连续和真实预算两种辅助排序下均零接受。现有总拒绝计数混合热点单改、普通双改与辅助，不能直接据此判断阻碍。本阶段先补充原辅助候选的逐对回执，复现其排序与判定，依据实际原因再设计优化，不先放宽门槛或扩大矩阵。

诊断计划`velvia-candidate-trace-v1.json`固定原v3初态、原128对辅助、8主×16辅助及全部预算；只有回执字段变化，模型SHA、缺口、原试探次数/总拒绝计数及真实舍入统计SHA必须与PR22完全一致，否则失败。无新模型不重做完整100图/native终验。环境沿用Windows11 / Ryzen9 8945HX / Python3.12.14 / NumPy1.26.4 / Numba0.60.0，研究内部Numba4、BLAS/MKL/OMP单线程，统计归约串行；目的为原候选拒绝归因与来源核对，不测性能。数值进程NUMBA_NUM_THREADS不设，由runner设4。

所有距离仍为RGB欧氏码值距离，非CIEDE2000；官方Threshold未知，照片历史已观察，不称盲测或比赛四级成绩，默认/冠军及历史证据不改。算法方案、合同、优化执行与Draft PR后续按诊断证据补齐。

诊断执行冻结于`f2ccccc`，成功复现Velvia原模型/缺口2097、试探总数、拒绝计数及统计SHA。原128辅助对中118为照片保护、8为完整域保护、2未下降尾部；照片失败项中aggregate0.rms出现111次、group38.rms出现12次。所有保留对的预算排序至少有1项RMS缺口，故不应只改善尾部下界排序。

据此冻结`velvia-three-node-v1.json`：只对该Velvia反例，在原128对前缀（逐候选/判定/统计SHA必须一致）后追加最多8主×4首辅×4次辅的三节点块，最多两轮，仍最多32个接受步骤。不新增Lomo搜索，不增加全局轮次或放宽预算；这是追加候选的能力扩展，不是等时间/等试探次数比较。两节点与三节点共享辅助排序函数，并复用同一舍入统计数组。

三节点采用独立TripleMove，原JointMove仍严格要求两个不同节点，避免改变旧契约。完整域联合重放继续从最早修改级重算后缀，可覆盖前级改变后才到达的下游支撑。对首个可行三节点块，真实检查六个非空真子集，在全部可行项中按真实尾部缺口、较少节点选择，重新确认回执后提交；保存所有失败。只有这些真子集全失败，才能称这组冻结节点值需要三个修改，不能证明任意两节点都不可能。

阶段合同一次集中：两个新增必要合同（三节点跨级新支撑/提交/陈旧回执；真实有限候选内两辅必需的RMS例及六真子集），加三个既有舍入预算合同与两个受影响完整域旧合同，共7项；不重复无关完整COO、硬件或性能扫描。完成实现和合同后，才执行该单例冻结优化。

## 实际执行与收益边界

三节点实现/方案先冻结于`a436ae9`，7/7合同一次通过（6.47秒），随后仅执行冻结Velvia单例。实际Windows11 10.0.26200 / Ryzen9 8945HX / Python3.12.14 / NumPy1.26.4 / SciPy1.15.2 / Numba0.60.0 / llvmlite0.43.0 / Pillow10.4；研究内部Numba4、BLAS/MKL/OMP单线程，统计归约串行，数值进程未设NUMBA_NUM_THREADS而内部设4。合同显式设4。GCC15.2 Release既有标量/AVX2终验单线程，二进制SHA仍`ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`。

进入三节点扩展前，当场核对原128对的节点值、真实缺口、逐项拒绝、统计SHA与f2ccccc诊断完全一致；最终归档再次核对。共享辅助排序重构没有偷偷改变两节点前缀。新统计数组同轮复用，不重新组装。

第一轮生成115个去重三节点候选，实际试12个（8照片保护、3全域保护、1接受）；检查该可行块的六真子集并重新确认。随后接受一个普通单节点和一组普通辅助双节点。第二轮辅助在第17对即接受，未生成第二批三节点。总新增接受3步：2097→1829→1760→1614，本轮组合缺口下降23.03%；最终22组/24项条件仍违反，数量未降。

原两节点诊断共128单、120普通双、128辅助对。优化运行因有新接受，实际共402单、360普通双、145辅助对，另12个三节点、6个真子集与1次确认。**新增候选和后续搜索成本明确增加，不能宣称等时间/等试探预算优于两节点。** 每阶段仍按原初态保护，不放宽预算；两个补偿轮次已耗尽，停止不代表任意联合邻域无解。

## 真实三节点的局部必要性

累计第45步节点3403由`(7,18,20)`到`(7,18,22)`，35927由`(255,255,200)`到`(255,255,199)`，35929由`(255,255,213)`到`(255,255,214)`。三者两两支撑不相交，完整域SSE变化−249、Q24距离上界和变化+903229281，与统计预测及真实完整域证书精确相同。

| 冻结修改子集 | 尾部缺口 | 80图SSE剩余预算 | 全域SSE剩余预算 | 首个拒绝原因 |
| --- | ---: | ---: | ---: | --- |
| 3403 | 1550 | −178018 | 362 | 80图RMS |
| 35927 | 2147 | −3382 | 1817 | 尾部未下降 |
| 35929 | 2333 | 203359 | −1471 | 尾部未下降 |
| 3403+35927 | 1600 | −182047 | 2026 | 80图RMS |
| 3403+35929 | 1786 | 24694 | −1262 | 全域RMS |
| 35927+35929 | 2376 | 199330 | 193 | 尾部未下降 |
| 三者合改 | 1829 | 20665 | 402 | 全部原保护通过 |

辅助35929在80图释放202712的SSE，却在全域消耗1624；35927在全域释放1664，却在80图消耗4029。两辅分别补偿不同测度，配合主节点后，两组预算均满足。这是此前单个辅助不能完成这组改动的具体原因，不是后端算错。

`diagnose_three_node.py`冻结于`1bf4689`后作独立局部复算：三节点正支撑并集4021色，读取80图及既定样本频数，独立整数平方根、RGB8映射及直方图更新，七个非空子集的缺口与门禁判定全部复现。完整域剩余预算对所有子集也由更新后的完整直方图复核；原搜索可能在照片拒绝时未继续计算全域，不能将这些后验全域值冒称原来已执行。没有新增拟合、搜索或审计反馈。

**必要性仅限该时刻与这些冻结节点值。** 未证明其他任意两节点改动不可能。后续第47步还把节点3403的B由22回调21，不能把第45步局部结论扩大成最终模型的唯一可达路径。

## 完整精度与误差转移

| 方案 | 全域mean | RMS | p99 | max | 100图mean | 100图RMS | 照片最差单图p99 | 照片max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v3/两节点诊断 | 0.981714 | 1.879305 | 7.000000 | 54.000000 | 1.033230 | 1.384176 | 7.119617 | 46.043458 |
| 三节点后最终 | 0.981720 | 1.879300 | 7.000000 | 54.000000 | 1.033869 | 1.384165 | 7.141428 | 46.043458 |

所有距离为RGB欧氏码值距离，非CIEDE2000。整体SSE改善、组合尾部缺口下降并不保证其他指标改善：照片mean和最差单图p99均略升，max类缺口371→517，而p99端点类1726→1097。没有隐藏这种取舍，更没有据此升级默认。

相对v3，100图mean为33改善/66退化/1持平，RMS36/63/1，p99为2/4/94，max为0/8/92。kodak-kodim06的p99由6回升7，kodak-kodim07的max由13升14。相对历史仍有5图mean、8图RMS、9图p99、15图max退化。完整最坏回归与逐图分布见[证据](../../report/data/exact-tail-v1)。

最大的剩余p99条件仍为div2k-0853：平方阈值13允许7864像素，实际8278，代价414（前为665）。新代价也集中到div2k-0897及div2k-0879的max条件。三节点只是释放了可行方向，当前总缺口目标仍可能转移误差；后续应优先研究尾部目标的优先级/不退化条件，不能只继续增加节点数。

最终完整域SSE相对原混合初态剩余477，80图聚合剩余3011、合并样本3035。保护始终固定在原混合初态，未重置参考。全部照片历史已观察，20张本轮审计不反馈不等于历史独立盲测。

## 正确性、架构与交付

新最终SLUT SHA为`f803945e6f1bef7c1a3b57954749e918bf360f3dd486f1b7cba3b9c88c6c681d`。完整256³与100图新终验，独立NumPy整数oracle、标量/AVX2两条原生流均0字节差异。诊断臂不变，复用两份旧回执。没有修改C++/portable/embedded、运行时二进制或SLUT v1，未在C99四级/实板执行新模型。

两个标准库`-I -S`复核均通过：每个202组初/终摘要，固定计数阈值、Q24/SSE预算及接受单调性，诊断59份/优化122份完整域证书均一致；其中确认会产生额外接受证书，不能将49份接受证书冒称49个新模型或步骤。解压归档后的复核与成员审计另存。

三节点同轮复用351895104字节舍入统计，持久数组与其和仍1360072502字节；整个离线进程OS峰值1664425984字节，不是运行时内存或性能承诺。新增TripleMove与统一components/combine只用于离线搜索；旧JointMove的二节点校验不变，跨四级输入前缀更新由必要合同实际核对，不等于对本轮四级新模型完整验收。

归档入口`095c0bd`核对两节点前缀、全部六真子集、按真实缺口选择及确认回执，并检查可加预算证书。保存4汇总、400逐图（100新/300显式复用）、12分组、4原生回执（2新/2复用）、诊断19/优化25成员ZIP、原数值源码/环境/计划/日志。总归档约3.7MB，后加七子集独立归因由静态审计绑定，图已目视。

复现沿用前文环境。实际命令如下；既有目录不得覆盖，复现须改用新目录并绑定新的参考路径/计划SHA。数值源分别为诊断f2ccccc、优化a436ae9，当前扩展代码与优化源同字节；诊断源保持在原ZIP，不能冒称当前代码就是旧源。

```powershell
python scripts/run_quantile_tail_study.py --plan experiments/velvia-candidate-trace-v1.json --output artifacts/velvia-candidate-trace-v1 --executable build-engineering-alignment/jshc.exe
python -m pytest tests/test_three_node_search.py tests/test_rounded_budget.py tests/test_full_domain_guard.py::test_joint_move_covers_new_downstream_support_and_commits tests/test_full_domain_guard.py::test_commit_refreshes_suffix_and_rejects_stale_model -q
python scripts/run_quantile_tail_study.py --plan experiments/velvia-three-node-v1.json --output artifacts/velvia-three-node-v1 --executable build-engineering-alignment/jshc.exe
python -I -S scripts/verify_quantile_constraints.py --input artifacts/velvia-candidate-trace-v1 --output artifacts/velvia-candidate-trace-v1/verification.json
python -I -S scripts/verify_quantile_constraints.py --input artifacts/velvia-three-node-v1 --output artifacts/velvia-three-node-v1/verification.json
python scripts/report_three_node.py --control artifacts/velvia-candidate-trace-v1 --optimized artifacts/velvia-three-node-v1 --warm artifacts/quantile-tail-v3 --output report/data/exact-tail-v1
python scripts/diagnose_three_node.py --input artifacts/velvia-three-node-v1 --warm artifacts/quantile-tail-v3 --output artifacts/three-node-subsets-v1.json
```

新Draft基于PR22头6b96d9c，中文commit/阶段说明/PR交付，不直接推主干。发布前刷新远端及相关正文、完整评论、review与行内线程；最终范围和新头CI在PR正文补记。#7/#9工程修复337a3dd已在祖先中，#8最终接口迁移/实板仍待处理。Discussion4原文由用户提供，最新回复仍有既有404访问缺口，不执行合并或issue关闭。

官方数据/Threshold未知、默认/冠军和历史证据不改。本阶段只研究这个Velvia单级反例，没有新增Lomo或网格扫描，不称未知输入泛化、SOTA、比赛四级成绩、性能或实板验证。残余22组条件与指标退化仍需后续解决。

Agent：Codex

Operator：WyEhNf

Task：候选拒绝与真实尾部代价的联合优化

Status：诊断、有限三节点优化、完整终验与独立子集归因完成；残余失败和误差转移保留，Draft待审查
