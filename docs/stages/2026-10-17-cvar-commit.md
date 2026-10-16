# 最坏百分之一误差的固定提交门禁

Agent：Codex；Operator：WyEhNf；Task：PR #26 后续；Status：In Progress（方案及数值源码先冻结，验收结果待补）。

## 误差原因与阶段目标

PR26在相同起点把历史分位缺口1613降至1582，逐图/完整域mean、RMS、p99和max均未退化，但完整域最坏1%颜色均值从11.5253793555升至11.5257059097。独立整数界证明上升，不是浮点显示错误。历史阈值缺口、均方误差及尾部均值不是同一目标，四个摘要的保护不能覆盖整个尾部形状。

同一已保存72候选中，29356+31532+34839的主缺口1585，尾部均值变化区间为[-0.0000872655,-0.0000871933]。本阶段只把这项既有发现变成可落地、可复核的提交门禁并完整验收；不扩展网格、轮次或调参扫描。1585是已观察数据上的选择，不能称独立盲验。

## 实现与可审核边界

`cvar_guard.py`固定起点完整域直方图，对最坏`ceil(N/100)`颜色的RGB欧氏距离和计算Q24整数上下界；候选上界不大于起点下界时允许提交。最坏K的频数完全相同也允许相等，避免非整数根造成错误拒绝；其他区间相交仍保守拒绝。原历史阈值、混合预算及固定起点四指标保护均保留。距离不是CIEDE2000。

`quantile_repair.py`在热点、普通双改、辅助和批次的实际提交路径统一保护CVaR。`primary_batch.py`区分四指标可行的组合材料和可直接提交的候选：单改CVaR上升仍可留池，与其他节点整块真实重放；不能单独提交。这样不会提前丢掉1585所需的两个风险单改。空提交候选返回回退，确认仍须通过全部门禁。

runner绑定起点模型签名、完整图片频数、环境、源码、计划及PR26结果哈希，逐项比较首轮原排序/统计SHA和8单改+64组合的四指标结果；确认CVaR只改变提交资格。`verify_cvar_guard.py`仅用标准库整数平方根独立复算新步骤与最终完整域证书，绑定起点与最终模型SHA。

新增门禁不是原比赛硬阈值，也不意味着每个分位均不增加；未证明全局最优或表示能力上限。不改默认、冠军、C++运行时、模型格式或硬件路径。

## 冻结实验与验证目的

`experiments/cvar-commit-v1.json`沿PR26 joint配置，从PR25同字节模型`cdbc18badb6ae3450a4cd28eadb9b941bf6d4ef243f72ccf2a693f78b0271bed`重放48步，主缺口1613。最多32步、单轮全局/辅助、8种子、双/三节点块，80完整图及既定选择像素反馈，20历史审计不反馈。对照复用已完整验收的PR26缺口1582终态，不为凑两臂重跑旧模型。

先集中执行15项必要合同：新增4项覆盖最坏K截断并列、独立Q24复算、尾部相同而主体不同、错误像素数、风险材料联合补偿、材料池非空但无提交候选，以及普通热点门禁；同时回归原11项批次、主预算及跨级三节点合同。若发现具体失败，保留首次日志，修复后再做有依据的复验。

合同通过后只启动一次冻结数值入口；仅变化终态执行一次完整256³、100图及单线程标量/AVX2与独立NumPy整数oracle逐字节终验。阶段性完整性另由原预算、四指标固定参照、新CVaR标准库验证器、所选7子集独立重放及72候选尾部复算交叉检查。归档后解压再核哈希与证书。没有性能或SOTA扫描。

环境：Windows11 10.0.26200，AMD Ryzen9 8945HX（16核32线程），RAM33605316608字节；venv Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0。合同NUMBA_NUM_THREADS=4；数值运行移除此变量，由runner设4；OPENBLAS/MKL/OMP均1。GCC15.2 Release程序`build-engineering-alignment/jshc.exe` SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`，标量/AVX2终验单线程。明确不执行实板、四级新模型或跨环境性能比较。

```powershell
# 使用artifacts/error-study-py312/Scripts/python.exe；先设置上述线程及UTF8环境。
python -m pytest tests/test_cvar_guard.py tests/test_primary_batch.py tests/test_primary_budget.py tests/test_three_node_search.py -q
# 移除NUMBA_NUM_THREADS后运行，旧目录不覆盖；复现须选择新目录并更新相应参考路径。
python scripts/run_quantile_tail_study.py --plan experiments/cvar-commit-v1.json --output artifacts/cvar-commit-v1 --executable build-engineering-alignment/jshc.exe
python -I -S scripts/verify_quantile_constraints.py --input artifacts/cvar-commit-v1 --output artifacts/cvar-commit-v1/verification.json
python -I -S scripts/verify_stability.py --input artifacts/cvar-commit-v1 --reference-run artifacts/primary-budget-constraints-v1 --output artifacts/cvar-commit-v1/stability-verification.json
python -I -S scripts/verify_cvar_guard.py --input artifacts/cvar-commit-v1 --reference-run artifacts/primary-budget-constraints-v1 --output artifacts/cvar-commit-v1/cvar-verification.json
```

## 协作与未完成项

基于PR26头2b92cee创建阶段分支；main dec1020为祖先，工程修复337a3dd保留。此前已读#9/#12至#26及#7/#8完整相关记录；PR创建/更新前再次刷新。#8接口迁移/实板仍待落实。Discussion4原文来自用户，最新回复访问404，保留检查缺口，不执行合并或关闭issue。AGENTS.md保持只读。

本阶段计划/代码冻结提交、实际合同/数值结果、独立归因、归档和CI须在验收后补记；当前不将预期1585写为已测成功。官方数据和Threshold仍缺，历史22组/24项失败不能以新增CVaR通过替代。
