# 固定连续方向场后的节点一轮重拟合

代理 `/root/tail` 按本会话用户授权执行本阶段。固定上一阶段 global1 两扫末的相容 stripe 场、原 3e5f Q16 轴，尝试重新优化原本为 mask0 学得的节点。独立 17/33 几何/节点方向合同及完整支撑研究计算通过，但一轮结束时相对原 3e5f 的 mean 预算仍失败，因此停止，未做照片、原生或性能升级验收，不改写为成功。

## 冻结预算及实现

只允许一轮奇偶颜色组0..7，每个节点26个RGB±1方向；每个节点的全部真实整数输出支撑参加计算。硬上界 d²≤1522 从不放宽。初始 stripe 场均值原本不合格，选择目标为五项相对原3e5f预算的归一正超额 `(max,sum)`，再训练mean、uniform mean；五项为完整域距离和/平方距离和、60图频率距离/平方距离、d²>40计数。每颜色组按节点号升序选择，一轮后结束，不追加轮数或改照片目标。最终预算始终来自原3e5f，没有改成较弱的stripe起点。

`python/lutlab/oriented_tetra.py`将外部方向场解释为原物理cell的有向四面体设计。设计核使用三比较器网络，fresh核独立使用六区域分支；现有八色gain/apply复用这些显式设计权重。每个cell的八个角有不同奇偶颜色，反向并不改变这一性质，故每色正支撑节点在三个输出通道间仍唯一且相同。相容场和共享节点保持，节点改值不改变面三角划分的相容代数条件；本失败项没有再做后拟合面采样。

独立合同 m17/33 各2056点，含端点与随机点；设计输出/fresh六区域核/原物理节点uint64 oracle逐字节相同。各检查72个节点方向，共144项，gain误差最大3.418e-12，cap计数、八色共同支撑零差。正式每色完整域fresh重算与累加器逐字节相同，gain预测差最大8.657e-9，hard cap违反为0。

## 结果和失败归因

| 指标 | 原3e5f预算 | 固定stripe原节点 | 一轮节点后 |
| --- | --- | --- | --- |
| 完整域mean | 0.886672865 | 0.901268736 | 0.901736680 |
| 完整域RMS | 1.648294036 | 1.672249672 | 1.652026856 |
| 60图频率mean | 0.850324782 | 0.860737863 | 0.864688121 |
| 60图频率RMS | 1.207775741 | 1.222486648 | 1.217057812 |
| d²>40数量 | 165,930 | 172,517 | 164,072 |
| 研究核完整域max d² | 1682 | 1522 | 1448 |

最后相对原预算 uniform mean +1.6989%、训练mean +1.6892%，平方距离和 +0.4534%、训练平方距离 +1.5430%，p99超阈数下降1.1197%。最大超额最终由两项mean主导；RMS平方只在第0颜色组后短暂成为最大超额，第1组起基本由mean主导。因此不能把失败全归因于额外RMS约束，也不能仅删除RMS就预言可恢复预算。

max d²=1448对应38.052595，比原1682小；但它仅由完整域研究fresh核确认，没有完成本候选独立uint64整域终验。mean门禁失败，不能把这项max变化作为正式可用升级，也不能将d²>40计数减少冒充已经测得精确p99或CVaR。五预算试验按原冻结方案封存，新的目标/步长/上界必须另立试验。

## 内存、环境和验证边界

为避免与其他质量任务争内存，仅离线设计索引在m≤33时采用uint16（物理节点号≤35936），Q16权重仍int32以容纳65536；设计两数组实际 **1,207,959,552 B**，不是运行模型内存。开跑前主机可用5,280,816KB（约5.04GiB），八批记录最低3,189,178,368B（约2.970GiB），进程RSS最高2,180,878,336B（约2.03GiB）；最低值读回时任务已结束，已向协调者报告，未关闭其他应用或重设WSL。退出后观察可用5,092,772KB，设计数组随进程释放。

相容stripe状态实际另存12B packed、96B byte及32768B展开研究数组；这些文件存在不等于12B原生常驻模型已实现。原有分输出坐标仍需9216B侧表；新增插值不受现有ChannelLut/native ABI支持。Windows11 26200/AMD64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、Numba0.60.0、psutil5.9，Numba4线程、OMP/BLAS/MKL环境1。没有新C++、跨架构或受控性能结果，不能称通过速度50%底线。

## 文件与复现

主要实现为 `oriented_tetra.py`、`verify_oriented_tail_nodes.py`、`run_velvia_stripe_nodes.py`；静态归档为 `archive_velvia_stripe_nodes.py`。[精简证据](../../report/data/velvia-stripe-nodes-20261024/README.md)包括原冻结run/summary、全部批次轨迹ZIP、失败研究模型、合同、内存和源码SHA。通用 `accept_velvia_cell_diagonals.py`新增显式模型/方向SHA及动态独立重参数化入口，作为未来验收准备；本次未执行该新增整域分支，不能称它已被本失败项覆盖。

在前几阶段的冻结数据与环境中，输出须不存在：

```powershell
& $py scripts/verify_oriented_tail_nodes.py --output artifacts/oriented-tail-contract-v1.json
& $py scripts/run_velvia_stripe_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --contract artifacts/oriented-tail-contract-v1.json --output artifacts/velvia-stripe-nodes-v1
& $py scripts/archive_velvia_stripe_nodes.py --output artifacts/velvia-stripe-nodes-archive-v1
```

后续若以mean优先、稍宽但仍优于原模型的max上界、较大离散步长继续探索，应明确其新目标与放宽的自加约束，保持原3e5f比较基线，不能重写本轮失败或混用结果。
