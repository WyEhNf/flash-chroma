# 固定分通道坐标的单轮节点精化

Agent：Codex；Operator：WyEhNf；状态：按冻结计划完成，候选未入围，未commit/PR/push。

本阶段新增`channel_nodes.py`及独立driver/集中合同/计划，不改旧坐标、原生、核心或默认。在3e5候选全部grid/shared_idx/channel_frac固定时，R/G/B依次各做8色节点±1，24块恰好一次。沿用原完整域本级标签、60图频数质量和原2dd逐色cap；不把两图归因audit反例加入训练。每输出独立I/W，当前RGB/d²缓存保留其它输出误差，逐块收益核对、末尾fresh前向核缓存。

一次集中m17/m33合成独立u64合同通过，含边界0/255、零权重/质量、不同输出几何、收益/cap/其它通道及24块cache。真实训练886个节点分量改变1，目标0.9269145401→0.9262197464，预测/实测最大差5.202e-16、cap和fresh缓存0差异。

原固定选择样本cube mean .884494632→.883498122（降0.1127%）、照片mean .892884760→.891807338（降0.1207%），p99均持平。照片CVaR1%微升4.668076354→4.671462483；guard逐图mean14好6差、p991好17平2差。相对原2dd旧门禁通过，但相对3e5两个mean至少再降0.5%均失败，按计划停止，无追加轮次或full/100图/native/性能，不升级最佳模型。有限邻域小收益不能证明全局最优。

环境Windows11 26200/Ryzen9 8945HX、Python3.12.14/NumPy1.26.4/Numba0.60.0；Numba4/BLAS1。入口`experiments/velvia-channel-nodes-v1.json`、`scripts/verify_channel_nodes.py`、`scripts/run_channel_nodes.py`。精确结果、复现命令、源码快照、模型及身份见[精简归档](../../report/data/velvia-channel-nodes-v1/README.md)。没有官方Threshold，欧氏RGB误差不混称CIEDE2000；候选NPZ扩展格式未冒充SLUT v1或官方支持。
