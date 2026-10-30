# Velvia：直接整数目标的节点与坐标交替

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成，三候选未入围。本地研究，不PR、不推送。

完整单元单调DP表明，原节点下最佳坐标仍只需较小移动；单独放宽范围不是主要瓶颈。节点和坐标却会共同决定哪些像素跨过RGB8舍入边界，因此固定一组变量时得到的驻点未必对另一组仍好。本阶段用同一真实RGB8目标交替更新两组变量。

冻结`experiments/velvia-alternating-integer-v1.json`，从ad473均衡配对模型起步，验收和逐色cap始终对原2dd。固定3轮：每轮完整单元单调DP一轮R/G/B、受cap单节点2扫、受cap配对1扫。只保存每轮最后模型，全部拟合结束后对三个候选统一选型，至多一位完整终验。此处报告全部累计预算，不把已有暖启动当零成本；不会沿中间样本结果追加轮数或改变权重。

m33、grid、idx及端点固定，RGB8节点与真实非降frac可更新，文件字节与运行时计算步骤不增加；函数族相对原几何插值已扩大，实际耗时是否改变须另测。标签仍是本级原表，.48cube/.48完整60图频数/.02边界/.02原热点，rho为RGB距离加tail6/.02。逐色cap=max(49,旧2dd误差平方)一次生成后不重置。每块的前后目标须一致，每个模块按其已集中验证的方式重算缓存/cap；这些是拟合不变量，不是逐轮完整精度测试。

目的为两组变量协同对真实拟合精度的影响；实现内核未改，不增加单元测试。复用monotone-axis和paired-grid的集中合同，逐文件SHA固定。Windows11 26200 x64/Ryzen9 8945HX/32GB；Python3.12.14、NumPy1.26.4/SciPy1.15.2/Numba0.60.0，Numba4、BLAS/MKL/OMP各1。不做性能测量。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/run_joint_grid_study.py fit --plan experiments/velvia-alternating-integer-v1.json --output artifacts/velvia-alternating-integer-v1
```

全原色和60训练图历史已见，20选择/20审计也历史已见，不能称独立盲测。双mean3%与p99门槛不降，未入围不新增完整cube/百图；官方Threshold未知，RGB距离非CIEDE2000。

## 实际结果

三轮均执行完毕，各轮只读整合审计确认模块目标/权威frac衔接，cap固定。完整训练目标依次0.937756→0.934926→0.934516→0.934336，后两轮收益已很小。起点ad473此前已消耗单节点4扫＋配对1扫，本轮是在该前史上额外增加预声明的3轮预算，不将其隐藏或与单次拟合等价。

|固定选择样本|原2dd|第1轮末|第2轮末|第3轮末|
|---|---:|---:|---:|---:|
|原色mean|0.940014|0.888429|0.888107|0.887942|
|原色p99|6.524458|6.164414|6.164414|6.164414|
|照片mean|0.929261|0.906272|0.905736|0.904412|
|照片p99（合并像素）|3.464102|3.464102|3.464102|3.464102|

第3轮相对2dd照片样本mean约降2.67%，仍不足3%。三候选均未入围，不因接近门槛继续追加轮数、不降低门槛；没有新增完整色域输出、百图或原生/性能验收。每个模块的全训练域cap检查为0违规，只证明训练约束与缓存一致，不能代替完整指标。完整逐轮实际接受扫数、所有配对与坐标变更、模型SHA和冻结源码见`report/data/velvia-alternating-integer-v1`。
