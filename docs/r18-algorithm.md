# R18：非均匀轴、分层采样与公共入口验收

本轮保留四张独立 LUT：每级只拟合自己的完整 `256³ × RGB8` 表，输出四张 `m³ × RGB8` 稀疏表；每级执行 Q16 四面体插值并立即舍入到 uint8，再进入下一级。没有合并四级、残差补偿、图像相关网络或运行时额外 shaper。非均匀轴通过既有 SLUT v1 的轴定位/权重表表达，节点数和运行时接口不变。

当前最有依据的新增候选是 `--method ls_tetra_jitter --grid dp`。它改善本轮各场景的平均误差，但不能保证最大误差下降；`clip-7 m17` 的全色最大 ΔE 从 29 增至 34。`ls_tetra_guarded` 保留为显式候选，不默认追加。

## 算法与可证明的范围

### 按轴动态规划

对每个输入轴，将另外两轴的 `24 × 24` 个等距探针和三个输出通道合成向量曲线 `Y[x]`，`x = 0,…,255`。对候选区间 `[a,b]` 计算端点线性弦插值的均方残差：

```text
E(a,b) = Σ(x=a…b) ||Y[x] - ((b-x)Y[a] + (x-a)Y[b])/(b-a)||² / D
D = 24 × 24 × 3
```

实现先计算 `256 × 256` Gram 矩阵、普通前缀和与按 x 加权的前缀和。因此每个候选区间的残差不再逐点遍历其内部颜色。平移 `Y` 不影响残差，中心化可降低浮点抵消误差。

动态规划选择恰好 `m-1` 段，首尾固定为 0 和 255；整数间距限制为 `2 ≤ b-a ≤ ceil(510/(m-1))`，并加 `1e-6 × (b-a-255/(m-1))²` 的微小间距惩罚，使近线性区域倾向均匀分配。

```text
D[j,b] = min_a {D[j-1,a] + E(a,b) + spacing_penalty(a,b)}
D[0,0] = 0
```

该 DP 对所列有限整数轴代理目标求最优解。它不求三维四面体误差、实际 Q16 舍入误差或四级最终误差的全局最优；轴之间的交互、裁剪边界和逐级量化仍需实测。代码中的 `selected_chord_sse` 不包含间距惩罚，不能据它单独宣称三维效果最优。

### 等体积分层采样

旧 LS 的输入样本位于步长 4 的固定张量格。新方案在每个 `4×4×4` 输入块内取一个固定随机整数颜色，共 262144 点，seed=`0x533138`。它减少规则取样相位与量化阶跃对齐造成的偏差，保持每个输入块相同权重，不使用测试图像分布。

LS 使用实际 Q16 四面体权重，但拟合目标仍是未作最终 uint8 舍入的二次误差；以可分离三线性 LS 初始化，CG 参数为 `lambda=1e-4, rtol=1e-7, maxiter=300`。不收敛、非有限解和残差异常沿用 R17 的拒绝发布机制。随后运行 4 轮旧整数二次目标精化。R17 的同色稀疏 Hessian 优化证明与限制见 [r17-algorithm.md](r17-algorithm.md)。

### 可选的真 Q16 局部守护精化

`ls_tetra_guarded` 在分层 LS 后追加至多 3 轮真实 Q16 ±1 节点调整。另取 65536 个与训练颜色不重合的 guard 点，seed=`0x473138`。按网格坐标奇偶分成八色；一个四面体中同色节点最多一个，故同色节点的样本支持互不重叠。RGB 通道依次处理，避免忽略欧氏距离的通道耦合。

候选节点变化在训练集与 guard 集上分别约束 ΔE 总和、平方误差总和、最大误差，并限制超过 p99 两个相邻顺序统计量阈值的样本数不得增加。两个顺序统计量均不增加时，NumPy 线性插值定义的 p99 也不增加。每轮结束仍用真实输出复算 mean/rms/p99/max，违约则回滚整轮；浮点比较容差为 `1e-12`。

这些 guard 点参与优化，不能称为盲测。单级训练/guard 不退化也不能推出四级链或全色不退化。本轮 72 次精化的统计均经独立 `apply_tetra_q16` API 核对，未触发 `contract_rollback`，但六组 `dp_guarded` 的四级盲测平均误差都略差于 `dp_jitter`，所以不会默认强推。

## 冻结阶段实验

运行环境为 Windows 11、Python 3.13.12、NumPy 2.4.6、SciPy 1.17.1；脚本将 BLAS/OpenMP 库线程设为 1。本轮只集中执行一次三场景、两种尺寸、七种方法的阶段比较，用时 138.019 秒，没有尺寸全扫。

输入复用 `artifacts/r17-algorithm` 的完整 LUT；R17 文件和模型没有被覆盖。`artifacts/r18-algorithm/study.json` 保存 42 条四级候选链、168 个 SLUT 路径与 SHA256、样本与源码哈希、CG/DP/精化诊断、单级和四级统计。168 个模型已只读复核尺寸与 SHA256 全部一致。

每组四级结果使用固定种子 `2026101518` 的 262144 个随机输入；排除普通格点训练、分层训练以及两组 guard 的所有颜色。另报告 216 个边界颜色。比较方法包括均匀节点直接插值取样 `sample_interp`、冻结旧 LS、旧 LS 加 guard、均匀分层 LS、均匀分层 LS 加 guard、DP 分层 LS、DP 分层 LS 加 guard。所有链都执行相同 Q16 四面体、逐级 uint8 舍入。

| 场景 | m | 旧 LS mean | DP+jitter mean | mean 降幅 | 旧/新 p99 | 旧/新 max |
|---|---:|---:|---:|---:|---:|---:|
| isp-0 | 17 | 1.463152 | 1.060198 | 27.54% | 4.242641 / 3.316625 | 14.456832 / 11.090537 |
| isp-0 | 18 | 1.292846 | 0.976441 | 24.47% | 4.000000 / 3.162278 | 12.328828 / 12.083046 |
| clip-7 | 17 | 1.832863 | 1.482692 | 19.11% | 7.000000 / 6.082763 | 23.000000 / 28.000000 |
| clip-7 | 18 | 1.719771 | 1.406157 | 18.24% | 6.082763 / 6.082763 | 30.000000 / 23.000000 |
| warp-7 | 17 | 1.691024 | 1.485688 | 12.14% | 5.385165 / 4.123106 | 11.357817 / 10.392305 |
| warp-7 | 18 | 1.611634 | 1.429378 | 11.31% | 5.099020 / 3.741657 | 10.677078 / 9.055385 |

随后主任务对两个冻结候选执行原生全 `2²⁴` 输入和 5 张固定 `1024×768 RGB8` 合成图验收，记录于 `artifacts/r18-progress/algorithm-accuracy.json`：

| 场景 | m | 全色旧/new mean | 全色新 p99 | 全色旧/new max | 最差单图 mean |
|---|---:|---:|---:|---:|---:|
| isp-0 | 18 | 1.293268 / 0.975933 | 3.162278 | 14.177447 / 14.142136 | 1.253158 |
| clip-7 | 17 | 1.831042 / 1.483448 | 6.082763 | 29 / 34 | 1.920032 |

二者通过的是示例门槛“每图 mean < 2 且全色 mean < 2”。官方阈值、聚合口径与正式数据尚未给出；不能把示例通过说成官方达标，更不能把平均误差改善说成所有像素改善。全色结果也说明有限盲样本的最大误差低估了真实最大误差。

## 公共入口和缓存

`lutlab.cli` 的 fit/evaluate/bench 支持：

- `--method ls_tetra_jitter` 或 `--method ls_tetra_guarded`；`--grid dp`。
- `--inputs LUT1 LUT2 LUT3 LUT4`：四个原始 `256³×3` 字节 RGB8 文件，顺序即处理级序；每个大小必须为 50331648 字节。
- `--model-dir DIR`：不可变缓存批所在的命名空间。输入文件位置不进入算法身份，相同字节可以跨路径复用。
- 没有上述两个参数时仍使用原 scenario 路径。非均匀 DP 的默认命名后缀为 `_dpgrid`。
- `evaluate --inputs` 直接由实参四表组成参考输出，防止误用默认 scenario 的 composite。

selector/workflow 新增 `dp_jitter` 与 `dp_guarded` profile。默认候选包含 `dp_jitter`；`dp_guarded` 需显式选择。二者均按所选 mean/p99/max、images/cube/both 门槛筛选；DP 不能绕过尾部约束。四级独立 seq 仍是主线；composite/residual 仍需显式研究许可，也不能成为提交成功的依据。

模型身份包含四个源文件内容哈希、有效 fit 参数、拟合源码哈希、环境版本和函数默认值。新增 `algorithm_settings` 明确记录分层 seed/count、CG 参数、整数精化轮数、guard seed/count/轮数、DP 探针和间距约束。默认值采集现在解开 `@lru_cache` 包装，否则缓存采样函数的默认 seed 会在枚举时遗漏。已完成批仍按整批验证，损坏或混合批不被复用。

真实公共入口验收脚本为 `scripts/r18_integration_check.py`：

```powershell
& C:/Users/admin/miniconda3/python.exe scripts/r18_integration_check.py --executable artifacts/r18-baseline/jshc-r17.exe
```

它先用 `cli.main` 的真实参数解析执行 `fit --inputs ... --model-dir ... --m 18 --method ls_tetra_jitter --grid dp`，四个输入 SHA 均各异；再换成同字节的 scenario 路径、禁止调用数值 fitter，确认仍命中原批；最后 selector 使用 `existing_only=True` 复用该批并执行原生全色和 5 图验收。模型、数据引用、日志和结果均在 `artifacts/r18-integration/`。

首次数值拟合耗时 2.078 秒；四个输出与冻结 R18 模型逐字节一致。selector 返回 pass，语义依据为 `verified_model_manifest`，全色 mean/p99/max 为 `0.975932794 / 3.162277660 / 14.142135624`，最差单图 mean 为 `1.253157598`。功能性单次计时不作为速度结论。

验收过程中保留了一项测试钩子失败：将 fitter 替换为 `Mock` 后，缓存按设计发现有效函数默认值集合改变，拒绝复用；改用 `functools.wraps` 保留被禁用函数的原始签名后验收通过。业务源码与已拟合模型不需改动，也没有重做数值拟合。完整失败日志和首次拟合日志均保留。

## 相关公开方法与适用性

- [AdaInt，CVPR 2022，论文官方页面](https://openaccess.thecvf.com/content/CVPR2022/html/Yang_AdaInt_Learning_Adaptive_Intervals_for_3D_Lookup_Tables_on_Real-Time_CVPR_2022_paper.html) 与 [作者实现](https://github.com/ImCharlesY/AdaInt)：学习非均匀采样间隔，用于图像增强。它说明固定均匀轴不是唯一方案；本轮使用的是有给定完整 LUT 的离线整数 DP，不是复现其图像自适应网络或训练结果。
- [Monga 与 Bala，Sort-Select-Damp，Color Imaging Conference 2008](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/cic/16/1/art00047)：根据输入重要性与变换变化程度调整采样点，是非均匀 LUT 采样的重要先例。本轮没有实现其完整排序/阻尼过程，也不宣称 DP 非均匀采样是首次提出。
- [OpenColorIO 官方 LUT3D CPU 实现](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/src/OpenColorIO/ops/lut3d/Lut3DOpCPU.cpp)：成熟的三线性/四面体及 SIMD 后端参考。主任务另行进行 OpenColorIO 2.6.0 实际对比；本页的算法表仅是同一 Q16 执行语义下的本项目方法对比，不能由此推出胜过 OpenColorIO 的普遍结论。

本轮已经实现 DP 网格、分层 LS、可选局部 Q16 guard，并接通缓存/选择入口；没有复现 AdaInt 训练，也没有采用额外 1D/深度网络表示替代题目的四张整数 LUT。因此结果应表述为当前固定模拟场景下的可复现改进，不是全局 SOTA 证明。

后续如继续算法工作，应冻结当前模型后引入新的完整 LUT 场景作独立验收，并优先处理裁剪区域最大误差；以独立 guard 选择尾部约束或网格容量分配，不能利用现有 heldout 反复调参后继续称它为盲测。正式数据与阈值一旦给出，应按正式口径重新筛选候选。
