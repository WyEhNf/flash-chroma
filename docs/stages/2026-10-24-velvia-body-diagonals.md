# Velvia 四种全局体对角线的冻结探针

本阶段由代理 `/root/tail` 执行，操作者为本会话用户，目的是检验整数节点微调以外的插值几何机制。固定当前 Velvia 最佳 `3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0` 的 33³ RGB8 节点、Q16 分输出轴坐标，仅改变全局一致的四面体 body diagonal。三种新方向全部未通过 mean/p99 保护门禁，不替换原模型，不进行原生或性能升级验收。

## 机制、合同和覆盖

每个 cell 对指定轴反向，然后执行六四面体划分；所有 cell 使用同一方向，避免本阶段引入逐 cell 选择。三轴方向位分别为 R=1、G=2、B=4，互补的 mask 与 `mask xor 7` 表示同一条体对角线，因此只测 0、1、2、4 共四种。冻结预算不含节点重拟合、坐标重拟合或百图反馈后的方向追加。

独立 NumPy uint64 oracle 保持原物理节点索引，反向轴从 cell 的另一端起步，携带负节点步长；按每个输出通道的三分数排序，四个非负权重总和严格为 65536，再四舍五入为 RGB8。第二实现把节点沿相同轴翻转，将 idx 变成 `m-2-idx`、frac 变成 `65536-frac`，调用既有整数前向内部核。这两种实现不共用物理节点计算代码。

合同覆盖 m=17/33，各 4096 个固定随机点（含八端点）、全部八个 mask，物理 oracle 与重参数化核零差，四组互补方向零差；mask0 与旧独立 oracle 也零差。正式四方向分别遍历完整 16,777,216 色，双实现逐字节相等；mask0 完整输出也逐字节重现旧最佳 `945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0`。随后复用这些完整流评估历史百图 78,643,200 像素，照片文件逐项核 SHA，全部逐图统计保存，没有称作盲测。

反向 idx 对物理几何有效，但不满足现有 `ChannelLut` 的有效坐标非降合同；实际验证中 mask1/2/4 均被当前 validator 拒绝，mask0 接受。因此这里使用显式研究核，未将这些数组静默塞入普通 SLUT 或宣称原生兼容。题面许可、正式序列化、运行时支持、额外内存和速度均未验证。

## 结果与拒绝依据

| 完整域方向 | mean | RMS | p99 | max | 最差 1% CVaR |
| --- | --- | --- | --- | --- | --- |
| 原方向 mask0 | 0.886673 | 1.648294 | 6.324555 | 41.012193 | 9.984283 |
| mask1，反 R | 1.198976 | 2.071195 | 8.062257 | 39.012818 | 11.649729 |
| mask2，反 G | 1.362984 | 2.448772 | 10.049876 | 39.012818 | 14.366432 |
| mask4，反 B | 1.350253 | 2.343702 | 9.219544 | 48.507731 | 13.003810 |

| 百图合并方向 | mean | RMS | p99 | max | 最差 1% CVaR |
| --- | --- | --- | --- | --- | --- |
| 原方向 mask0 | 0.884971 | 1.231562 | 3.464102 | 38.052595 | 4.717364 |
| mask1，反 R | 1.490894 | 2.102159 | 7.071068 | 39.000000 | 8.417120 |
| mask2，反 G | 1.993610 | 2.686616 | 8.246211 | 38.000000 | 10.299102 |
| mask4，反 B | 1.515143 | 2.098744 | 7.000000 | 40.049969 | 8.285680 |

mask1/2 的完整域 max 从 41.0122 降至 39.0128，不能掩盖 mean、RMS、p99 和 CVaR 的明显上升；mask2 百图 max 的微降同样不足以通过保护门禁。所有新方向均拒绝。这个有限结果仅说明**已经为原方向优化的当前节点/坐标不能直接换全局对角线**，没有证明其他方向在重新拟合后仍不可能更优；后者不在本次冻结预算内。

环境为 Windows11 26200/AMD64、Ryzen9 8945HX，Python3.12.14、NumPy1.26.4、Numba0.60.0、Pillow10.4；Numba4线程，OMP/BLAS/MKL环境1。测试目的是插值几何合同、独立整数正确性与拟合质量，未加载原生 DLL 执行、未调用运行时计时；共享 CPU 离线时长不构成性能结论。

## 文件、复现和边界

实现为 `scripts/study_velvia_body_diagonals.py`，静态归档为 `scripts/archive_velvia_body_diagonals.py`。[精简证据](../../report/data/velvia-body-diagonals-20261024/README.md)含冻结输入/环境、合同、四种完整域/逐图统计、原最佳模型 ZIP、测量源码 ZIP、全部 SHA；四个 50 MB 输出流仅留在本地 artifacts，不作为模型或额外查表结构。

在上述冻结环境运行，下列输出必须不存在；`$py` 是该 Python 环境解释器：

```powershell
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
& $py scripts/study_velvia_body_diagonals.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/velvia-body-diagonals-v1
& $py scripts/archive_velvia_body_diagonals.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/velvia-body-diagonals-archive-v1
```

门禁是完整域与百图合并 mean/RMS/p99/max/CVaR 均不增，且至少一个 p99/max 严格改善；三种新方向都未过前一条。没有把仅局部 max 下降描述为可用精度优化，没有省略失败方向，也没有放松用户对均值的要求。
