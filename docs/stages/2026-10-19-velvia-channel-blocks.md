# 固定分通道坐标的整块节点平移

Agent：Codex；Operator：WyEhNf；状态：有限提议未入围，已停止；仅本地记录，不PR或推送。

先前分通道坐标方案已经过完整验收。本阶段只检验另一种节点联合调整：固定000原点，把节点分成2×2×2块，一块内所有节点在当前输出通道同号移动1码。一个四面体可同时使用块中多个节点，所以先相加其权重，再计算一次RGB8舍入与真实距离；不能把单节点收益相加。这样能跨过“每次只动一个节点，输出恰好不变”的台阶。算法保持33³节点、所有坐标和运行时，未把失败单节点提议接作新起点。

一次24组（R/G/B各8种块奇偶色）只改变16个节点分量。训练rho由0.9269145401降至0.9268608893，逐色cap及fresh缓存核对通过。原冻结选择结果如下：

|选择口径|已验收3e5起点|本次候选|mean降低|
|---|---:|---:|---:|
|cube mean|0.8844946317|0.8844247288|0.0079%|
|照片 mean|0.8928847604|0.8927985239|0.0097%|
|cube p99|6.164414003|6.164414003|持平|
|照片合并 p99|3.464101615|3.464101615|持平|

原2dd门槛仍通过，但两个mean均没有相对3e5再降0.5%，selected=false。因此不做完整256³输出、100图或native/性能验收，不替换当前模型，也不扫描块偏移、权重或追加轮数。该结果只说明这一个整块方向收益小，不能证明任意多节点联合修改无效或新几何已经全局最优。与单节点886分量精化的约0.11%/0.12%选择收益并列观察，两种有限整数邻域都未兑现显著增量；下一步先测新几何的连续节点空间，区分局部停滞与表示瓶颈。

## 环境、目的与复现

Windows11 26200 x64、Ryzen9 8945HX、32GB，Python3.12.14、NumPy1.26.4、Numba0.60、llvmlite0.43；Numba4，BLAS/MKL/OMP各1。目的分两部分：一次m17/m33×3输出的独立uint64合同验证收益/cap/其它通道及24组fresh缓存；随后一个实际LUT提议按原固定样本选型。合同每组合64点，共1596个合法方向，cap与整数输出0差异；零质量行依然约束cap。另有解析构造证明整块能跨过单节点台阶。静态审查复核了同奇偶色块正支撑互斥及整块节点范围，不能以静态审查替代数值证据。

```powershell
$env:PYTHONUTF8='1'
$env:NUMBA_NUM_THREADS='4'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/verify_channel_blocks.py --output artifacts/channel-blocks-contract-v1
artifacts/error-study-py312/Scripts/python.exe scripts/run_channel_blocks.py --plan experiments/velvia-channel-blocks-v1.json --output artifacts/velvia-channel-blocks-v1
```

起点NPZ SHA为3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0；候选为986ed903667e94e1b119c264e18e7506e65ca9a61461632209855a7f5fafd1a5。原样本、60图质量、caps=max(49,原2dd d²)、原表及源码SHA均冻结，未解码照片或引入两图反例。训练全域fresh检查不等于完整精度验收；只报告预声明样本的误差结果。冻结计划、源码、合同、来源与原始指标见[精简归档](../../report/data/velvia-channel-blocks-v1/README.md)。新表示仍为实验NPZ，不属SLUTv1或官方支持；RGB欧氏距离非CIEDE2000，官方Threshold未知。
