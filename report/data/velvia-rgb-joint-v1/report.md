# Velvia单节点三个通道同时调整

Agent：Codex；Operator：WyEhNf；状态：本地研究完成，唯一候选未入围，不PR、不推送。

此前单通道坐标下降和相邻节点配对仍可能遗漏同一个节点内的RGB联合方向。这不是增加旧算法轮数：集中解析反例中，六个单通道±1步都增加损失，而R/G同时+1使真实RGB8平均距离下降0.089073。因此新增`python/lutlab/rgb_joint_grid.py`，在同一个节点上枚举26个非零`[-1,1]³`方向，以8色正支撑互斥方式批量应用。各候选方向直接计算三通道联合距离与逐色cap，不组合单通道禁止位。

算法只提出一次8色扫。节点值仍为RGB8，权威idx/frac、网格、文件大小和运行时内核步骤均保持起点；每组后的累加缓存最终独立重算，目标预测、RGB8范围和逐色cap均核对。优化损失仍为RGB欧氏距离加阈值6以上权重0.02的二次惩罚，质量为.48完整颜色域/.48完整60图/.02边界/.02旧热点。浮点归约不是无理数严格证书。

冻结计划为`experiments/velvia-rgb-joint-v1.json`。起点是上一阶段第三轮最终模型`1f0a9f1d84b3fd157aab7db348b340aca209c2e35f72dd3b195aa1023411c37c`，其权威坐标已经更新，不能重新从grid生成。驱动对此路径显式绑定父run身份、selection及最终模型SHA，并核有效坐标非降和端点。验收基线及cap锚点始终为原2dd，不能把起点变强隐藏为当前单扫的贡献。累计前史为单节点4扫/配对1扫、三轮各坐标1次/单节点2扫/配对1扫，当前额外一次RGB联合扫。

测试环境：Windows11 26200 x64、Ryzen9 8945HX、32GB；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0/llvmlite0.43.0，Numba4，BLAS/MKL/OMP各1。本阶段测试目的分别为新提议的数值正确性，以及固定样本的拟合精度选型；没有原生或性能测试。

集中合同只执行一次：解析联合步反例通过；587个合法和37个越界方向与独立uint64比较器oracle核对，最大收益误差`1.30e-13`；513行合成整扫兑现预测损失和全部cap；17/33两种网格共221184个四面体几何证明同色正支撑互斥。含0/255节点、Q16权威表偏移、非法预算/起点cap等必要边界。它是有限内核合同，不代表真实精度通过。

实际完整训练域中106个节点移动，其中71个同时移动多个通道；目标0.934336降为0.934238，cache/cap均0不一致。唯一终态再执行一次原固定选择样本比较：

|选择样本|原2dd|第三轮起点|RGB联合单扫|
|---|---:|---:|---:|
|颜色mean|0.940014|0.887942|0.887953|
|颜色p99|6.524458|6.164414|6.164414|
|照片mean|0.929261|0.904412|0.904220|
|照片合并p99|3.464102|3.464102|3.464102|

照片mean相对2dd约降2.69%，仍未达到3%。改动主要检验一个明确局部障碍，实际收益过小，不追加轮数、权重或方向扫描。没有新完整输出、百图、原生正确性或运行时性能验收，已验收冠军不变。训练cap全域检查不能替代完整精度指标。

复现须用[精简归档](../../report/data/velvia-rgb-joint-v1/report.md)内实测源码，保留原数据与父运行；后续驱动变化会触发身份拒绝，不能混用当前HEAD重放旧验收。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/verify_rgb_joint_grid.py --output artifacts/rgb-joint-grid-contract-v1
artifacts/error-study-py312/Scripts/python.exe scripts/run_joint_grid_study.py fit --plan experiments/velvia-rgb-joint-v1.json --output artifacts/velvia-rgb-joint-v1
```

所有颜色和照片历史已见，不称盲验；RGB距离不是CIEDE2000。没有官方数据/Threshold，不作官方或SOTA结论。
