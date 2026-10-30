# Velvia共享节点协同调整：逐色包络下的固定4+1方案

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成，未入围。仅本地工作，不PR、不推送。

本阶段检验一个具体原因：RGB8舍入会让两个单独有害的节点调整在联合时有益。当前Velvia最坏热点的节点偏差远大于半码量化误差，有限轴坐标校准又没有取得3%的双均值改善，因此本阶段固定原2dd模型的m33、grid、idx和frac，只扩大节点调整邻域。

冻结计划为`experiments/velvia-guarded-pair-v1.json`。完整256³原色使用本级原表标签，60张训练照片使用完整颜色频数；质量仍为.48原色均匀、.48照片、.02边界、.02原有热点，rho为RGB距离加超过6码值的.02倍二次尾罚。硬上限固定为每个原色的max(49,旧2dd误差平方)，两段优化之间不重新放宽。先4扫受约束单节点更新，再从其最终模型固定执行1扫成对更新。只保存暖启动最终和配对最终两个候选，沿用双mean至少降低3%、RMS/p99/max不升和至少一项p99改善的选型；最多一位赢家进入一次完整终验。

测试目的分开：已有纯合成集中合同证明配对收益、组合违规计数和增量缓存的实现行为；本轮拟合及固定选型检验真实数据的精度收益。若未过选型不执行全域/百图原生验收，也不以训练损失下降代替验收成功。全域参与训练、20选择/20审计图历史均已见，不能称独立盲测。

执行环境：Windows11 26200 x64、Ryzen9 8945HX、32GB RAM；CPython3.12.14，NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0；Numba4线程，OMP/OPENBLAS/MKL各1。此轮不混入速度测试。若触发终验，原生程序固定GCC15.2 Release -O3 -DNDEBUG，AVX2/OpenMP/C99启用，程序SHA ba088c68…，实际后端由回执记录。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/run_joint_grid_study.py fit --plan experiments/velvia-guarded-pair-v1.json --output artifacts/velvia-guarded-pair-v1
```

主要文件为`python/lutlab/paired_grid.py`、`scripts/verify_paired_grid.py`和研究驱动的显式`guarded_pair`分支；不改变默认拟合或运行时内核。合成合同与真实拟合证据分别保存于`report/data/paired-grid-contract-v1`和`report/data/velvia-guarded-pair-v1`。

## 实际结果

单节点4扫均接受，完整训练目标降至0.939714204792；配对阶段起点恰为该值，1172次成对提议后降至0.937755758469。配对结束重新计算全部训练累加器/误差缓存，0差；全部16777216颜色的固定cap违规0。配对扫描约12秒是此次离线拟合用时，不是运行时加速结论。

|固定选择样本|原2dd|4扫单节点|再1扫配对|
|---|---:|---:|---:|
|原色mean|0.940014|0.891106|0.889734|
|原色p99|6.524458|6.164414|6.164414|
|照片mean|0.929261|0.911062|0.909082|
|照片p99（合并选择像素）|3.464102|3.464102|3.464102|

配对最终相对基线的原色mean约降5.35%、p99约降5.52%，照片mean仅降约2.17%，未满足原定3%。两候选均失败；没有执行新的完整cube输出、百图/原生终验或性能实验，不将训练域完整缓存检查写成完整精度验收。报告归档的metrics/photos CSV仅有表头，明确表示没有新增完整指标。

原色/照片样本max均未升，不能据此声称每图尾部均不退化。逐色cap仅对旧误差超过7的颜色阻止其进一步增大，并不冻结每个低误差点。模型SHA：单节点`01147516…`、配对`ad473f30…`，完整身份在selection.json。

本结果证实共享节点的小范围协同存在，但其收益不足以解释或消除主要残差；不延长扫数、不降低门槛。后续优先分析残差在颜色域和照片分布中的集中位置，再决定是否调整布点或拟合目标。
