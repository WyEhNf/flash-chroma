# Velvia舍入区间目标：固定设计的连续协同提议

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成，未入围。仅本地研究，不PR、不推送。

本阶段检验拟合目标的偏差：对于RGB8半向上舍入，连续预测在目标值附近的一个区间内都可以输出正确标签，未必需要逼近整数中心。此前单节点与成对节点调整已经改善，但照片mean仍未达到3%，因此改用区间主损失提出跨节点连续协同更新，再回到真正RGB8节点验证。此为新研究提议，不替换默认方法。

固定`experiments/velvia-rounding-interval-v1.json`：起点是上一阶段配对最终模型ad473f30…，验收仍对原2dd，不能把较强起点与较弱验收基线混称同一模型。m33、grid、idx、frac不变；所有标签来自Velvia本级完整原表。质量仍.48均匀原色/.48完整60图频数/.02边界/.02原热点。

连续主损失为各通道超出目标±.49的距离向量的平滑L2（epsilon=.05）。保留tail6/.02；另以4倍二次罚鼓励连续误差低于sqrt(cap)−sqrt(3)，cap始终是旧2dd逐原色max(49,d²)。sqrt(3)解释为节点量化和输出舍入的合计扰动界；优化并不保证满足此软半径，因此每个最终RGB8模型还必须对全部训练颜色检查真实整数cap，出现违规就拒绝入围。不能以连续损失下降宣称真实mean下降或硬约束已满足。

固定L-BFGS-B最多240次、节点相对起点±4、4分片，最终增量只保存.5与1两个预定比例，统一一次选型，至多一位赢家执行完整终验。原双mean3%及p99改善门槛保持，不临时增预算、调权重或降门槛。

环境和目的：Windows11 26200 x64/Ryzen9 8945HX/32GB；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0/llvmlite0.43.0；Numba4线程，BLAS/MKL/OMP=1。集中实现检查仅521行合成Q16设计，独立NumPy目标与12个方向有限差分梯度、1/4分片归约、无支撑节点零梯度、正确区间零主损失与符号对称；一次通过，最大梯度差2.515e−10。不含真实精度、完整色域原生或性能验证。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/verify_rounding_interval.py --output artifacts/rounding-interval-contract-v1-replay
artifacts/error-study-py312/Scripts/python.exe scripts/run_joint_grid_study.py fit --plan experiments/velvia-rounding-interval-v1.json --output artifacts/velvia-rounding-interval-v1
```

完整原色参与训练、100图历史已见，不能称独立盲测。官方数据/Threshold未知，不用RGB欧氏码值距离冒称CIEDE2000。

## 实际结果与失败项

240次迭代实际用255次函数评估，约43秒离线优化。两个预定候选只集中比较一次；没有增加迭代、改变权重或按中间输出另选比例。

|选择样本指标|原2dd|最终增量一半|最终增量全部|
|---|---:|---:|---:|
|原色mean|0.940014|0.891853|0.921814|
|原色p99|6.524458|6.082763|6.000000|
|照片mean|0.929261|0.908515|0.933725|
|照片p99（合并像素）|3.464102|3.316625|3.316625|
|全部训练色的硬cap违规数|0|5249|10369|

一半增量的照片mean约降2.23%，仍不足3%；全部增量照片mean反而升高。两候选原色选择样本max都升高，并且完整训练色的真实整数cap分别有5249/10369处违规。即使部分p99明显下降，也不能推广为通过或替换旧模型；没有完整cube输出、100图/原生终验或新性能测量。

此结果再次说明连续区间目标和RGB8量化后的实际目标不同，软罚不能提供硬可行保证；本实现已将违规计入选型失败而不是只作日志。不能仅凭此试验否定所有量化感知算法，也不能将失败归为已证实的内核错误。

模型、环境、源码、初始模型与原验收基线分别绑定的结果在`report/data/velvia-rounding-interval-v1`。实现集中合同单独在`report/data/rounding-interval-contract-v1`；CSV无完整指标行表示本轮未触发完整终验。
