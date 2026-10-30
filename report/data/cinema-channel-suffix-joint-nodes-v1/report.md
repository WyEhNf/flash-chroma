# Cinema固定新坐标后的单轮RGB联合节点耦合

Agent：Codex；Operator：WyEhNf；状态：冻结实验完成，候选未入围，仅本地归档，未推送或PR。

对象是四张真实创意LUT的数值四级链（1910s→1920s→1930s→1940s），没有色彩域匹配证据，不称真实ISP或自然摄影管线。本轮从上一未入围aed888坐标提议出发，冻结全部grid/shared idx/channel_frac及后三模型，仅首级RGB8节点做一次8色26方向联合±1。完整验收基线仍af974链，不把aed升为已验新基线。

相对af974，cube/photos选择mean降低3.5384%/4.4633%，两个p99都从4.123106降至3.741657；但photos.max从7.071068升至7.549834，唯一失败为photos.max。因此不执行完整终验、不追加扫数/权重/候选，不升级默认。双mean通过不能替代完整门禁。

## 冻结方法、目标与身份

新增`channel_suffix_joint_nodes.py`、独立verify/driver及`experiments/cinema-channel-suffix-joint-nodes-v1.json`。只读复用已证shared cube/parity和三路设计/整数缓存辅助，不改旧模块、格式、原生或默认。

aed起点SHA aed888e75375e1e2cc1bff32f8fbe62b67afbfdb33d800bb521739aec76b5a41，来自上一九块冻结run/selection/optimizer；当时仅cube mean3%未过，未经完整终验。其首级节点/idx/grid与af974相同，只有三输出frac不同。后三933a/95cb/932f完全冻结，既有af974完整流78eb只作基线查表。

所有canonical原RGB行、独立T1标签、质量、后缀缓存、整链精确参考及caps原样复用，不解码新图或改质量。loss始终rho(p−T1)+rho(S(p)−S(T1))，两项1:1；S为固定稀疏后三阶段逐级RGB8，精确整链reference仅cap，没有复合或残差标签。两标签/四原表/后三模型/质量与缓存SHA同上一冻结阶段。训练起始双项loss重现0.5913351632500841且整链cap0。

每节点RGB方向为[-1,1]^3去掉零向量的26项，固定parity0..7恰好一次，不从失败全局节点提议出发。shared idx使各输出共用同一cube，八角parity互异；固定色时各输出正支撑若存在必是同一角，但各通道权重可不同或为零。同色不同节点支持并集不交，所以可独立汇总每节点联合收益。

每个方向先用三路真实Q16权重和half-up求完整RGB8 p，再直接调用ac._cost查非线性S(p)，计算source+suffix两项loss及精确整链cap。没有相加单通道gain或线性组合后缀变化。节点边界对完整方向全局禁止，cap包括零质量行；geometry与当前本级d²/整链cap另有诊断。

三输出I/W约1.5GiB是离线缓存，另有acc、平方误差、26方向私有归约等，不是运行时内存或速度结论。模型参数数目不增，保持aed实验NPZ表示，不能因此称SLUT v1或官方支持。

## 实际结果与门禁

8色7094节点移动，8800个节点分量改变，其中1505次多通道联合步。两项加权训练目标0.5913351632500841→0.5435687566307119。geometry、完整训练cap和fresh缓存差异均0，最大预测/实际收益差2.813e-13。三输出几何及后三模型未变。

唯一最终候选在原cube262144、guard20*4096上作一次严格选型；旧af974基线只查已验完整输出流，真值查原参考缓存。aed列仅观察增量，不参与替代完整验收基线。

| 指标 | 已验af974链 | 未全验aed起点 | 最终候选 |
|---|---:|---:|---:|
| cube mean | 1.018026809 | 0.996018922 | 0.982005132 |
| cube rms | 1.410686362 | 1.385474794 | 1.368888451 |
| cube p99 | 4.123105626 | 4.123105626 | 3.741657387 |
| cube max | 8.124038405 | 8.124038405 | 8.124038405 |
| cube cvar_1pct | 4.758563640 | 4.679778345 | 4.621761189 |
| photos mean | 0.864484839 | 0.834815405 | 0.825900527 |
| photos rms | 1.323092487 | 1.283544059 | 1.271302850 |
| photos p99 | 4.123105626 | 3.741657387 | 3.741657387 |
| photos max | 7.071067812 | 6.403124237 | 7.549834435 |
| photos cvar_1pct | 4.896166908 | 4.665093264 | 4.604315810 |
| photos worst_image_p99 | 5.196152423 | 5.196152423 | 5.196152423 |
| photos mean_image_cvar_1pct | 4.784029321 | 4.566041996 | 4.515906422 |

相对aed，cube/photos mean再降1.4070%/1.0679%。但照片max比af974和aed均变差。

相对af974，guard20逐图mean和RMS均20好/0平/0差，p999好11平，max0好15平5差，CVaR全部20图改善。相对aed，mean19好1差，RMS18好2差，p993好16平1差，max0好15平5差，CVaR14好2平4差。聚合/部分尾部改善不等于逐图支配。

唯一失败photos.max，其余双mean3%和mean/RMS/p99/max/CVaR/worst保护均通过。这里“cap0”与max退化不矛盾：复用的cap仍为更早daad链的max(49,d²)，只保证相对该旧锚点不产生新的>7退化，并不保证相对当前af974的每个色或照片max不退化。当前检查没有私改锚点、追补照片热点或放宽验收阈值。

最终候选SHA `f13923f1ab8edf25e8773ca0519dea20f6583edf5561a31d713d11b09e960662`；run身份`88e0b4d7123e7e47deb8899c32a867e5a208c7143cde85435406888c9dfb331a`。NPZ字段format=channel_coordinates_v1_experimental，source_model_sha256=aed，baseline_model_sha256=af974，后三模型另列；grid/shared_idx/channel_frac与aed逐元素完全不变。没有完整cube输出流、100图或原生/性能验收；候选不被当成已全验模型。

## 集中合同、环境与边界

真实拟合前一次集中m17/m33各25点，对全部实际正支撑节点合法26方向检查1912/1938次；非法节点RGB8方向各38次、零质量cap禁止各170次。独立uint64首级和显式非线性suffix oracle手写两项标签cost及独立reference cap，不调用ac._cost作为真值。最大gain差5.684e-14/3.579e-14，cap计数、geometry、输出和8色fresh均0差异。

环境Windows11 26200 x64/Ryzen9 8945HX、Python3.12.14/NumPy1.26.4/Numba0.60.0/llvmlite0.43.0；Numba4/OMP与BLAS1。目的为联合非线性cost/cap正确性及一次固定预算精度提议，不是运行时或性能测试。代码、计划、实际输入/cache文件与array SHA、T1/S(T1)派生SHA、两套提议来源及复现命令全部保存。

本轮失败即停止，未追加轮数/权重/方法矩阵。标签语义、质量和cap不变；数据/选择历史已见，不称盲测。无官方Threshold，欧氏RGB距离不混称CIEDE2000，不宣称整数全局最优或SOTA。后续若另立约束研究，必须单独冻结和记录，不能把本轮未通过说成已验收成功。
