# 完整单元内的单调坐标DP

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成，真实候选未入围。本地研究，不PR、不推送。

此前精确事件搜索仍使用原位置±4096及相邻静态中点，不能跨越这些人为边界。Filmic的134码反例表明静态边界确实可能阻挡精确解。本阶段对非可分离Velvia检验更大的函数族：节点、idx、grid及首尾坐标固定，每个输入码的frac可在完整0..65536中选择，直接约束有效坐标非降，不再用静态中点或总偏移限制。此处同字节数不代表相同几何插值函数族。

每一轴的各输入码分别拥有一个损失/硬cap状态表。idx不同的单元天然有序，同一个idx连续段内以非降状态DP联选；前缀最小值使复杂度为O(码值数×65537)。使用全部真实RGB8舍入事件生成成本，float64归约，不宣称无理数严格最优证书。固定一轮R/G/B，跨轴串行后独立全域重算损失和cap，不能称跨轴全局最优。

先进行一次集中实现合同：64个小型状态问题与独立穷举比较、跨静态中点的可行反例、端点/不可行路径拒绝，以及三轴完整65537状态的真实像素直接枚举及独立u64 oracle。只有这些通过后才冻结真实拟合计划。实现合同覆盖小合成输入，不能代替真实模型精度终验。

环境：Windows11 26200 x64、Ryzen9 8945HX/32GB；Python3.12.14、NumPy1.26.4、Numba0.60.0/llvmlite0.43.0；Numba4线程，BLAS/MKL/OMP各1；原生运行时及性能计时不适用。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/verify_monotone_axis.py --output artifacts/monotone-axis-contract-v1
```

集中合同一次通过：64个DP问题均与独立穷举的损失及最小总位移一致；静态中点反例能选择[25000,26000]而非被原20000边界挡住。三轴各65537状态、每轴17点直接像素枚举的最大损失差1.954e−14，cap计数0差；额外u64 oracle控制一致。固定端点已有违规时明确拒绝，不覆盖其禁止状态。

真实阶段冻结为`experiments/velvia-monotone-dp-v1.json`，采用原2dd为验收基线，从ad473的均衡配对节点起步，沿用完整cube和60图频数的.48/.48/.02/.02测度、原表标签及旧逐色cap=max(49,d²)；至多一个最终候选，双mean3%与p99门槛不变。恒等后缀缓存仅复用离线事件计算器，其额外损失权重为0，目标恰为本级rho。实际单级研究不伪造四级比赛。

```powershell
artifacts/error-study-py312/Scripts/python.exe scripts/run_joint_grid_study.py fit --plan experiments/velvia-monotone-dp-v1.json --output artifacts/velvia-monotone-dp-v1
```

实现合同源码与环境SHA独立保存于`report/data/monotone-axis-contract-v1`；真实阶段在`report/data/velvia-monotone-dp-v1`。完整域已用于训练且照片历史已见，不称盲测；官方数据/Threshold未知，RGB欧氏码值距离非CIEDE2000。

## 实际结果

三轴单次更新全部接受，完整训练rho目标0.937756→0.935845，全部训练原色cap违规0。R/G/B实际最大移动仅313/1417/988个Q16单位，虽可用整个65537状态，最终仍在很小范围；这不能说明所有坐标自由度无用，但不支持“旧总偏移范围是本例主瓶颈”。

固定原色选择样本mean0.940014→0.889063、p996.524458→6.164414；照片选择样本mean0.929261→0.906375、合并像素p99仍3.464102。照片mean仅降低约2.46%，原双mean3%门槛失败，唯一候选未入围。未执行新的完整色域输出、百图/原生终验或性能测量，不把全训练目标/cap重算写成完整精度验收。

原实测驱动的源码快照已保留。阶段结束（session34442已exit0）后，驱动才增加另一研究分支，故当前整文件SHA不同；重放本阶段应使用其measured-source.zip，不能以新驱动冒充同一运行身份，不为文档或后续分支变化重跑本轮拟合。
