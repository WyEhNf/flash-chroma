# 完整危险表的最小L1整数耦合

Agent：`/root/tail`。Operator：本任务用户。状态：唯一20秒求解、一次完整支撑验解及离线审计完成；六项预算上升，严格拒绝，不补跑、不切默认。

前阶段完整70571输入的节点盒筛查得到2224个可能危险输入和126765个安全RGB三元组。此阶段仍从原max_first（0ea0/904e/95cb/5b8，143e完整流）出发，把全部危险点同时施加精确Q16舍入与AllowedAssignments，用68347个恒安全点证书及支撑外固定max²48覆盖完整RGB8域，尝试取得整体max²≤49，避免首轮只保护116热点时产生旁侧越cap。

258个节点分量delta仍各自为原值±2与[0,255]相交，6672个危险点首级输出分量delta通过6672条精确gcd舍入行相连，再加入258个abs(delta)辅助整数并最小化其和。模型共7188整数、2224张表/126765元组，L1总界516；逐行原/约简绝对乘积和最大262144，CPvalidate通过。目标只是少扰动代理，未把最小L1当作mean、RMS或CVaR保证。

预检v1的五类有限合同均通过，但可行例的最优L1均为0，正L1目标覆盖不足。因此保留全部已执行v1源码、合同、问题和PB，新增独立`check_cinema_first_safe_cpsat_v2.py`、生成器`_v2.py`及协议v2，增加两个强制非零扰动例。七例CP与原acc独立穷举一致，新增两例严格最小L1分别为1和2。v1/v2均没有搜索真实问题；实际整数模型PB相同，仅冻结源/合同身份更新。

最终问题SHA `0a09b85c161b245984ad1479f60e55e277a68b606b2a92abc28f0dd2c877cd39`，PB SHA `8738cb0760620289778589fbf17776339c981a06aa1fa0a24ffef222ced47dc6`，预检JSON SHA `1a373f960733b94ce66ad06b5056d576ef147ae04274c205af314445361d61f5`。固定1 worker、seed20261024、20秒，只调用一次真实solver，20.031291800秒返回`FEASIBLE`，L1=143、solver下界24，未证明L1最优。没有变seed或延时补跑。

回原环境一次fresh uint64完整重放70571行并与Numba逐字节比较，零不一致；全部2224危险点输出与CP整数值一致，旧116热点max²降到22，整个支撑与支撑外的最大平方误差都为48，0点越cap。但均值与CVaR等预算实际如下：

| 范围 | 指标 | 原max_first | minL1见证 |
| --- | --- | ---: | ---: |
| 全域 | mean | 0.7990738071534367 | 0.7996658981158761 |
| 全域 | RMS | 1.1976684589597302 | 1.19876375793104 |
| 全域 | p99 | 3 | 3 |
| 全域 | max² | 50 | 48 |
| 全域 | 最差1% CVaR | 4.029054534445704 | 4.042947781563382 |
| 原60图合并 | mean | 0.6823481783784588 | 0.6823633097737783 |
| 原60图合并 | RMS | 1.1366130440332765 | 1.1366463258327217 |
| 原60图合并 | p99 | 3.4641016151377544 | 3.4641016151377544 |
| 原60图合并 | max² | 50 | 48 |
| 原60图合并 | 最差1% CVaR | 4.303192100572805 | 4.303584250448429 |

双mean、双RMS和双CVaR六项上升，违反原八预算，故候选严格拒绝。最大误差下降的见证不掩盖均值损失；未新增native、完整四级执行、百图、RSS或吞吐验收。保存NPZ SHA `741e55f55c674384543511dc20b98ecd7d6a1ed4c1b9bb17406cabd7cc86bea0`只用于复核这个有限Pareto代价。离线审计独立核完6930个基本整数、6672条gcd/舍入行、2224张表、258个abs与L1，再按Python整数重新更新完整域和原60图直方图、复算全部指标及六项失败，没有第二次求解或节点插值。

执行环境为Windows x86-64、Ryzen9 8945HX、Python3.12.14。原NumPy1.26.4/Numba0.60.0只负责JSON及u64/Numba验解；隔离ORTools9.15.6755环境只读整数问题并执行CP。复用前阶段10个wheel的官方PyPI SHA与环境锁，未改变原Python环境。质量工作允许共享主机；20.031秒只记录此SAT求解，不能当成映射吞吐。研究没有改模型大小、轴或运行时，但官方分输出坐标许可仍未知。

归档目标`report/data/p16-cinema-first-safe-cpsat-20261024`保留两版实际源码、合同/PB、唯一真实问题/PB/结果、完整回放和失败节点。鲁棒筛查证据另见[前阶段](2026-10-24-p16-cinema-first-risk.md)。主要源为纯整数模型桥`cinema_first_safe_cpsat_model.py`、`prepare_cinema_first_safe_cpsat_v2.py`、`solve_cinema_first_safe_cpsat.py`和`verify_cinema_first_safe_cpsat.py`。复现真实求解会建立新的实验调用，已有原件禁止覆盖：

```powershell
& 'artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/check_cinema_first_safe_cpsat_v2.py --output artifacts/cinema-first-safe-cpsat-contract-v2.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/prepare_cinema_first_safe_cpsat_v2.py --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --contract artifacts/cinema-first-safe-cpsat-contract-v2.json --output artifacts/cinema-first-safe-cpsat-problem-v2.json
& 'artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/preflight_cinema_first_safe_cpsat.py --problem artifacts/cinema-first-safe-cpsat-problem-v2.json --output artifacts/cinema-first-safe-cpsat-preflight-v2.json
& 'artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/solve_cinema_first_safe_cpsat.py --problem artifacts/cinema-first-safe-cpsat-problem-v2.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --preflight artifacts/cinema-first-safe-cpsat-preflight-v2.json --output artifacts/cinema-first-safe-cpsat-solution-v2.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/verify_cinema_first_safe_cpsat.py --problem artifacts/cinema-first-safe-cpsat-problem-v2.json --solution artifacts/cinema-first-safe-cpsat-solution-v2.json --output artifacts/cinema-first-safe-cpsat-accept-v2
```

方法采用Google官方[CP-SAT整数建模](https://developers.google.com/optimization/cp/cp_solver)和[表约束](https://developers.google.com/optimization/assignment/assignment_groups)。本阶段的有用边界是：固定86节点±2与当前真实后缀内，完整cap49有整数见证；少扰动目标仍不足以保护平均精度。它没有证明同时满足六项平均/尾部预算的解不存在。下一步若直接建误差预算，须另立协议覆盖完整支撑实际误差，不能修改本轮L1模型或把失败改判。
