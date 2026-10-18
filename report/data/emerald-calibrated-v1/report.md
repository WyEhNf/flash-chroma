# Emerald Malaise：17³模型兑现精确校准

Agent：Codex；Operator：WyEhNf；状态：本地限定范围验收完成，不PR、不推送。

PR #41除Filmic外还指出Emerald Malaise的误差与支撑问题。此前本地只复现了其17³/33³结构DP基线，并解析证明固定节点/idx/端点、Q16坐标总偏移不超过4096时精确解存在，没有生成新模型。本阶段完成这一明确待办，没有扫描其他来源或再拟合节点。

对全部256³原表字节验证同轴可分离后，直接调用已集中验证的`separable_calibration.exact_monotone`。17³仅7个frac值变化，最大547个Q16单位；节点、idx、grid与端点字节均保持。解析768码值全部精确才触发一次集中完整验收。此逻辑已包含在上一阶段显式拟合方法`ls_tetra_calibrated`中，本阶段没有修改公共拟合器、运行时、格式、默认模型或AGENTS.md。

|范围与指标|历史DP17|历史DP33|本次精确17|
|---|---:|---:|---:|
|完整域mean|0.02723649|0.03497783|0|
|完整域RMS|0.16535946|0.18750000|0|
|完整域p99|1|1|0|
|完整域max|1.41421356|1.73205081|0|
|完整域CVaR1%|1.00758444|1.01260421|0|
|百图mean|0.03082946|0.03507477|0|
|百图RMS|0.17596106|0.18789979|0|
|最差单图p99|1|1|0|
|百图max|1.41421356|1.73205081|0|
|文件字节|18799|112063|18799|

两个历史基线的完整域指标是基于已证明分离结构的256码值误差直方图卷积解析结果，未再次完整映射旧模型。标准库独立聚合复核，并补出CVaR；最终v2沿用项目`ceil(N×1%)`最坏像素口径，首次分析的分数尾质量版本留本地，不与历史指标混用。候选另外实际穷举256³，与独立uint64比较器oracle及分离公式逐字节一致；完整输出SHA与原表RGB字节相同：`9cf223067852495f5b7f0ce035f11f70602a3adec4e265351933ca4aac994589`。

候选的C++标量、AVX2、AVX2 MADD、AVX2 scalar-gather和AVX2 exact-float五个可用后端各完整色域验证一致；它们执行同一模型，不能把不同内核的次数算成五个独立来源。100张完整1024×768 RGB8照片对三个模型各实际映射，共300条逐图记录；新17模型再运行AVX2/请求4线程完整百图，与研究输出逐字节一致。没有新增四级/C99/其他ISA验收，没有运行性能计时。

候选SHA：`cb123fe085e09003bb56c653556a41f4b26a62dcba6e5e0d6c2949677e8eb9c9`。相对旧33模型文件减少83.2246%，相对同容量17模型没有容量变化。原误差已经较小，清零的100%相对降幅不能暗示绝对收益很大，更不能推广到Velvia等非可分离LUT。

环境：Windows11 26200 x64/Ryzen9 8945HX/32GB，Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0/llvmlite0.43.0，Numba4、BLAS/MKL/OMP1。原生沿用GCC15.2 Release `-O3 -DNDEBUG`，AVX2/OpenMP/C99编入，二进制SHA为`ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`；单级cube各后端1线程，照片AVX2请求4。同期允许另一项精度研究，不作受控性能结论。标准库审计使用CPython3.13.12，无数值后端。

复现入口为`scripts/run_emerald_calibrated.py`、独立聚合为`scripts/audit_emerald_calibrated.py`，冻结计划为`experiments/emerald-calibrated-v1.json`。旧完整参考、源cube、基线与前阶段run/results均按SHA绑定；11项接口集中合同复用同SHA回执，没有重复单元测试。精简模型、逐图/指标CSV、来源及原生回执见[归档](report.md)。大RGB输出及reference留原artifacts，归档保留哈希。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/run_emerald_calibrated.py prepare --plan experiments/emerald-calibrated-v1.json --output artifacts/emerald-calibrated-v1
artifacts/error-study-py312/Scripts/python.exe scripts/run_emerald_calibrated.py accept --plan experiments/emerald-calibrated-v1.json --output artifacts/emerald-calibrated-v1
python -X utf8 -I -S scripts/audit_emerald_calibrated.py --run artifacts/emerald-calibrated-v1 --output artifacts/emerald-calibrated-v1/independent-analytic-audit-v2.json
```

已完成目录不覆盖；复现旧数值需归档内实测源码，不能混合后续HEAD。原始source `.cube` SHA为`b76d97e0958d9b2b80b6f3c51da6c634a46cb0b5741b854a014beb405510194e`，原始reference.npy SHA为`246751885156d439621b20c66563d62715ef6179b4ba2cd3040bfc116c6a4f50`。本阶段基于本地提交669a659；本阶段变更与说明一起以中文提交保存，尚未推送。

照片和来源均历史已见，RGB欧氏距离非CIEDE2000；官方数据/Threshold仍未知，没有官方成绩或SOTA声明。单一来源全域验零是完整的限定结论，整个精度目标仍未完成。
