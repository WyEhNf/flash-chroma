# Velvia照片均值：一个固定测度取舍点

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成，未入围。本地研究，不PR、不推送。

旧输出的完整频数归因显示，60图的78.785%误差和来自距离≤2，清除全部>7误差也只能让mean降低0.871%。而相同cube/照片质量的4+1调整，cube选择样本mean已改善5.35%，照片仅2.17%。本阶段因此只提出一个明确的照片优先测度，而不继续只修极少热点，也不扫描权重。

冻结计划`experiments/velvia-photo-priority-v1.json`把cube/照片质量从.48/.48改为.21/.75，边界与热点各.02、rho和硬cap不变。同一原2dd起点，固定4扫单节点＋1扫配对；不继承前阶段节点以延长预算。节点RGB8，m33/grid/idx/frac固定。本级完整原表标签、60图完整频数与原选择/验收基线均相同。两个最终候选同池选型，至多一赢家完整终验；双mean3%、RMS/尾部不升的原门槛保留，公开照片与均匀色域的取舍。

测试目的是拟合测度对真实精度的影响；不新增算法正确性单元测试，不比较速度。Windows11 26200 x64/Ryzen9 8945HX/32GB；Python3.12.14、NumPy1.26.4/SciPy1.15.2/Numba0.60.0；Numba4线程，BLAS/MKL/OMP各1。原色完整参与训练，60/20/20图历史已见，不称盲测或通用最优权重。官方Threshold未知，RGB欧氏误差非CIEDE2000。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/run_joint_grid_study.py fit --plan experiments/velvia-photo-priority-v1.json --output artifacts/velvia-photo-priority-v1
```

## 实际结果

4扫均接受，目标0.930489；1173次成对提议后进一步下降至0.928023，但选型如下：

|选择样本指标|原2dd|照片优先单节点|照片优先配对|均衡质量配对（前阶段）|
|---|---:|---:|---:|---:|
|原色mean|0.940014|0.897206|0.896800|0.889734|
|原色p99|6.524458|6.164414|6.164414|6.164414|
|照片mean|0.929261|0.913665|0.912871|0.909082|
|照片p99（合并像素）|3.464102|3.464102|3.464102|3.464102|

两个候选仍因照片mean未降3%而失败。相对均衡质量方案，本权重点的原色和选择照片mean都更高，不把训练目标改善或照片权重更大当作泛化改善。该对照仅一个权重点，不证明所有照片质量都无用，不继续扫描。

同一逐色cap全训练域0违规，配对增量与整缓存重新计算一致；这只说明约束及拟合缓存通过，不替代完整精度。未运行新的完整cube输出、100图/原生终验或性能测量。结果在`report/data/velvia-photo-priority-v1`。

完整只读归因在`report/data/velvia-error-mass-v1`，包括768码值/96轴区间、全原网格单元和质量守恒；该归因没有调用新模型映射或拟合。
