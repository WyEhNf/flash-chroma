# 固定分通道几何的一次RGB联合节点研究

Agent：Codex；Operator：WyEhNf；状态：固定实验完成，未入围，未commit/PR/push。

新增channel_joint_nodes模块/独立合同/driver/计划，不改旧文件。从原3e5固定几何起点按parity0..7一次选择26种RGB联合±1方向。shared idx保证同cube八角parity唯一，三输出当前色正支撑必是同一角，权重可不同/为零，因此可直接汇总每节点真实联合收益和完整d² cap，不能相加单通道收益或禁止位。

一次m17/m33集中合同覆盖25点全部正支撑节点26方向、全部cells八角唯一性、边界/零质量cap/fresh/u64，并复现六单步变差但联合步改善的解析例，全部通过。真实8色947节点移动/103个多通道步，rho .926914540→.926150608，预测/实际最大差1.03e-15，geometry/cap/fresh0差异。

原冻结选择cube mean .884494632→.883548024、photos .892884760→.891925966，仅约降.1070%/.1074%，p99均不变。原2dd旧门槛通过，但相对3e5双mean再降0.5%失败，停止不full/100图/native/性能。没有追加扫数或扩节点族，不称全局最优。

环境Windows11 26200/Ryzen9 8945HX、Py3.12.14/NumPy1.26.4/Numba0.60.0、Numba4/BLAS1。三路I/W约1.5GiB为离线暂存，保持原质量/标签/caps，没有新照片或audit反例训练。详细复现/逐图/身份与限制见[精简归档](../../report/data/velvia-channel-joint-nodes-v1/README.md)。
