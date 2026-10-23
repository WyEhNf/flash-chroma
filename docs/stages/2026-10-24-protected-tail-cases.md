# 完整支撑节点法在普通四级 SLUT 与 Velvia 难例上的边界

本阶段由代理 `/root/tail` 执行，操作者为本会话用户，属于 16 题精度方向的后续研究。主候选仍为 [Cinema 末级联合优化](2026-10-24-cinema-last-stage.md)。本阶段检验同一方法能否推广到保守的普通共享轴四级表示及另一种颜色变换；没有切换默认模型。普通链的聚合 mean/p99 改善，但一张照片的 mean 明显退化，max 不变；Velvia 只有小幅均值改善，p99/max 不变。

## 起点、方法与语义

两个案例分别从各自已经验证的最佳模型开始，不从更弱的旧模型开始。普通 Cinema 的首级为 `af9747e4b396ee8382897cd9af717d7464eccfe066add1262c12ff95582f3fc0`，后三张为既有 `stage4_sweep004/selected-stage{2,3,4}.slut`；它们都是共享坐标的普通 SLUT，候选不新增分输出侧表。Velvia 的起点为 `3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0`，这是带 9216 B 分输出坐标侧表的单级研究表示，不能据此宣称四级推广或题面许可已确认。

冻结策略为一次八个奇偶节点组、每组 26 个 RGB ±1 方向，优先减少严重尾部。每个节点的全部整数输出支撑同时参与计算，保护全域均匀 mean/RMS、原 60 图频率 mean/RMS、p99 超阈计数，逐色上界为 `max(49, 本案例原模型 d²)`。普通链 p99/严重阈值为 d²=14/36，Velvia 为 40/100。阈值在训练前固定，全部结果保留，不由百图回测追加轮数或改变候选。每组完成后重新完整计算支撑和收益，零 cap 违反、零累加器与 fresh 输出差异。

普通链的目标是原始四张 256³ LUT 按 RGB8 逐级查表后的最终输出，后三张稀疏模型固定；Velvia 是单张原始表，离线恒等后缀仅供统一训练接口。所有误差是最终 RGB8 输出对参考 RGB8 的欧氏距离，不是连续浮点节点误差。两案均固定 33³/Q16、逐级四舍五入。全域用于训练；既有 100 张照片是回顾验证，不能称为盲测。

## 完整域与百图结果

| 案例/范围 | mean 原→新 | RMS 原→新 | p99 原→新 | max 原→新 | CVaR 最差 1% 原→新 |
| --- | --- | --- | --- | --- | --- |
| 普通四级，256³ | 1.016505→0.943805 | 1.410656→1.317844 | 4.123106→3.464102 | 8.124038→8.124038 | 4.778482→4.306926 |
| 普通四级，百图合并 | 0.850501→0.800667 | 1.321702→1.248714 | 4.123106→3.741657 | 8.124038→8.124038 | 5.011612→4.602515 |
| Velvia 单级，256³ | 0.886673→0.885311 | 1.648294→1.644903 | 6.324555→6.324555 | 41.012193→41.012193 | 9.984283→9.968729 |
| Velvia 单级，百图合并 | 0.884971→0.884321 | 1.231562→1.230812 | 3.464102→3.464102 | 38.052595→38.052595 | 4.717364→4.713751 |

| 逐图好/平/差 | mean | RMS | p99 | max | CVaR 最差 1% |
| --- | --- | --- | --- | --- | --- |
| 普通四级 | 99/0/1 | 99/0/1 | 78/22/0 | 51/49/0 | 100/0/0 |
| Velvia 单级 | 80/0/20 | 84/0/16 | 1/99/0 | 4/96/0 | 85/7/8 |

普通链的 `div2k-0877` 是重要的泛化边界：mean **1.222871676301→1.937968771619（+0.715097095318，约 +58.48%）**，RMS **1.612144285095→2.330215914741**。聚合均值改善不能掩盖这张图的明显回退。因此不能把“逐节点保护训练频率”解释为“任意照片均值受保护”，本阶段不把它作为用户主精度候选。全部逐图退化在 `regressions.csv` 中列出。两案最大误差均未下降；Velvia 未达到本轮 p99/max 的目标，保留为有界负结果。

## 已验证范围和未完成门禁

在 Windows 11 26200/AMD64、Ryzen 9 8945HX、Python 3.12.14、NumPy 1.26.4、Numba 0.60.0 环境运行；拟合 4 个 Numba 线程，OMP/BLAS/MKL 环境线程数为 1。原生验收使用速度分支 revision 87 的 MinGW Release DLL，SHA `58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158`，标量请求 1 线程、AVX2 请求 4 线程；未使用 AVX512。

每案完整 16,777,216 色的独立 NumPy uint64 排序与加权 oracle、原生 scalar 和 AVX2 输出逐字节相等，百图 78,643,200 像素也与同一完整流逐字节一致。最终流 SHA 分别为普通链 `8b20e0dad8cf4763b97d756470818a75624dc1684f74b0ff47c59b1daf9c6696`、Velvia `27ab6d9d3f0d1757cad7b4a37eed52aa8ec0e357c43ece13079f922f20e6332a`。完整原始表组合也按每级 RGB8 语义重算确认。正确性测试不代替精度或性能门禁。

候选原生账户容量分别为普通链 2,005,672 B、Velvia 单级 272,859 B；这里只是候选的实际构造值，没有把 a399 的 16 MiB 直表资格推给普通 af974 起点。后续需对 af974 与新模型在同一 87 库逐项比较 cache/domain/palette/direct 资格、容量，并配对实测速度。两案目前没有受控吞吐结果，不能声称通过速度 50% 底线，也不能声称内存相对改善。普通链不加侧表仅指输入表示，运行时账户容量可能因缓存资格变化而改变。

## 文件与复现

`scripts/run_protected_tail_case.py` 是冻结的通用训练入口，`scripts/accept_channel_tail_nodes.py` 支持 `cinema_shared/velvia` 参考与原生验收；`scripts/archive_protected_tail_cases.py` 仅做静态归档。精简证据在 [report/data/protected-tail-cases-20261024](../../report/data/protected-tail-cases-20261024/README.md)，包含两案输入 SHA、冻结策略、完整验收统计、逐图退化、模型 ZIP 和实际测量源码快照。

在原冻结数据缓存与上述 Python 环境中运行，输出目录必须不存在；`$py` 指向该环境的解释器：

```powershell
$cache = 'F:/Hackathon/projects/16-lut-color'
$dll = 'F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll'
$sha = '58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158'
& $py scripts/run_protected_tail_case.py --cache-root $cache --case cinema_shared --output artifacts/protected-tail-cinema-shared-v1
& $py scripts/run_protected_tail_case.py --cache-root $cache --case velvia --output artifacts/protected-tail-velvia-v1
& $py scripts/accept_channel_tail_nodes.py --cache-root $cache --case cinema_shared --models artifacts/protected-tail-cinema-shared-v1 --modes candidate --baseline-cube "$cache/artifacts/cinema-axis-calibration-v1/stage1_sweep012/cube.rgb" --library $dll --library-sha256 $sha --output artifacts/protected-tail-cinema-shared-accept-v1
& $py scripts/accept_channel_tail_nodes.py --cache-root $cache --case velvia --models artifacts/protected-tail-velvia-v1 --modes candidate --baseline-cube "$cache/artifacts/velvia-channel-coordinates-accept-v1/cube.rgb" --library $dll --library-sha256 $sha --output artifacts/protected-tail-velvia-accept-v1
& $py scripts/archive_protected_tail_cases.py --cache-root $cache --output artifacts/protected-tail-cases-archive-v1
```

下一步在固定 Velvia 起点上检验四种全局一致 body diagonal，以探索节点微调以外的机制。该探针将单列表示与运行时兼容性，不能把反向坐标重参数化悄然称作普通合法 SLUT。
