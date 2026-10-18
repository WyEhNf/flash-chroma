# Cinema首级分输出坐标：固定九块研究

Agent：Codex；Operator：WyEhNf；状态：单次固定实验完成，未入围，仅本地归档，未推送或PR。

本对象是1910s→1920s→1930s→1940s四张真实创意LUT的数值四级链，保留逐级RGB8舍入；没有色彩域匹配证据，不称真实ISP或自然摄影管线。

只把已验af9747首级的Q16 frac复制三份，再分别优化输出R/G/B各轴R/G/B，共九块一次。首级RGB8节点、shared idx、grid和端点不变，后三张933a/95cb/932f完全冻结。结果照片选择mean降低3.4320%，p99降低9.2515%，但cube选择mean仅降2.1618%，未达双mean各3%的严格门槛。因此不full/100图/native/性能、不修改默认，不追加扫数、权重或候选。

## 标签、后缀与约束

新模块`channel_suffix_coordinates.py`和独立driver/集中合同/计划，未改已有数值模块或原生。直接复用cinema-axis-calibration-v1的完整canonical原RGB行、训练质量、固定稀疏后三阶段S缓存、整链精确参考/caps及原选择像素；没有新照片解码或缓存重建。

标签根始终为独立T1原完整表，损失固定为rho(p−T1)+rho(S(p)−S(T1))，两项1:1，rho为RGB8欧氏距离+6以上.02尾罚。精确整链Y只进入cap禁止位，没有复合/残差拟合标签。T1 SHA37b1fa…，S(T1)派生SHA e077a2…与原suffix-objective元数据严格匹配。四原表SHA与旧run完全相同。

首级原色无前缀，质量为0.10全域均匀+0.45原色cube频数+0.45原60图完整频数，前两项合计0.55全域均匀；不改质量。caps继续锚定旧末级优化链daad的max(49,旧误差平方)，不是改锚到af974。本轮选型基线则始终是已验af974/933a/95cb/932f链和78eb输出流；两种身份明确区分。

当前af974旧完整流逐色满足复用cap，复制起点经S与旧78eb完整流逐字节完全相等。suffix缓存文件/array SHA与其元数据、后三模型和历史完整验收绑定；四表源与初始模型/旧run/winner/full/native身份都通过检查。

每块固定其它两输出当前RGB8缓存，只改变一个输出的一条轴，按exact_axis._line枚举该输出真实整数舍入事件。每次事件后以完整RGB查S，再由ac._cost计算两项独立标签损失及整链cap；非线性S的变化不线性相加。完整0..65536状态，按同idx连续段单调DP保证q=idx*ONE+frac非降，端点冻结；没有静态中点或±4096总偏移。这是扩大插值函数族，不是只修Q16舍入或普通网格移动。

九块全部接受，两项加权训练目标0.6769458587735461→0.5913351632500841，2126坐标改变、最大frac偏移43121，训练整链cap0。块预测/实际目标最大差5.367e-12，最终本级RGB/平方误差/两项loss/fresh缓存均一致。没有跨轴/输出全局最优声明。

## 唯一最终候选选择

只复用原cube262144及guard20*4096选择像素，旧基线只查已存78eb流，真值查既有四原表参考流；旧流样本指标与历史af974赢家逐项一致。候选为新首级真实RGB8输出后接固定S。

| 指标 | 当前已验af974链 | 最终候选 |
|---|---:|---:|
| cube mean | 1.018026809 | 0.996018922 |
| cube rms | 1.410686362 | 1.385474794 |
| cube p99 | 4.123105626 | 4.123105626 |
| cube max | 8.124038405 | 8.124038405 |
| cube cvar_1pct | 4.758563640 | 4.679778345 |
| photos mean | 0.864484839 | 0.834815405 |
| photos rms | 1.323092487 | 1.283544059 |
| photos p99 | 4.123105626 | 3.741657387 |
| photos max | 7.071067812 | 6.403124237 |
| photos cvar_1pct | 4.896166908 | 4.665093264 |
| photos worst_image_p99 | 5.196152423 | 5.196152423 |
| photos mean_image_cvar_1pct | 4.784029321 | 4.566041996 |

原严格门禁唯一失败为cube.mean_reduction_3pct；所有其它mean/RMS/p99/max/CVaR/worst_image_p99保护通过，照片p99严格改善。新加CVaR保护明确使用cube及合并照片样本各自CVaR1%；逐图CVaR均值另列。guard20逐图mean19好1差、RMS19好1差、p999好11平、max2好17平1差、CVaR全部20图改善；聚合通过不代表逐图支配。

候选SHA `aed888e75375e1e2cc1bff32f8fbe62b67afbfdb33d800bb521739aec76b5a41`，run身份`aafe81b16dcd82a1cba8c9747f97ab57cd277f67a2e1d604e27e2cd565768e1d`。保持channel_coordinates_v1_experimental NPZ范式，source/baseline首级SHA均af974，后三模型SHA另列；不冒充SLUT v1或官方支持。坐标payload由3072增为9216字节，增加6144字节，三输出可用不同四面体，不能称同内存/同速度。候选未经完整终验，不把它升级为已验基线。

## 集中合同、环境和边界

先一次集中m17/m33各9种输出/轴、共18例，每例9点完整65537状态。使用非线性跨通道耦合RGB8后缀；独立六分支uint64暴力计算输出与手写两项标签/独立reference cap，最大成本误差1.137e-12，cap计数/其它输出/fresh0差异，DP真实单调/端点/可行性均过。各尺寸另1033点独立u64前向0差异。

环境Windows11 26200 x64/Ryzen9 8945HX、Python3.12.14/NumPy1.26.4/Numba0.60.0/llvmlite0.43.0；Numba4、OMP与BLAS1。测试目的为单输出事件、非线性后缀及数据身份正确性，随后唯一九块提议与样本选择，不是原生或性能验收。

新入口`scripts/run_cinema_channel_suffix_coordinates.py`，计划`experiments/cinema-channel-suffix-coordinates-v1.json`。源码快照、准确输入/cache文件与array SHA、两标签SHA、四模型/四原表SHA、完整样本数值/逐图CSV和复现命令均保留；大cache只记录原路径与SHA，未复制或重建。

本轮全部RGB颜色参与训练，选择集历史已见，不称盲测；没有官方Threshold。mean/p99等为欧氏RGB距离，不是Lab/CIEDE2000。训练全色约束核对不等于新完整精度/运行时验收，未生成完整输出流或100图结果。固定九块收益不足不证明其它表示或全局优化无解。
