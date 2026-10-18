# Cinema当前已验收基线锚定的约束修正

Agent：Codex；Operator：WyEhNf；状态：唯一整合提议完成并通过原固定样本选择，完整验收待根代理另行执行；仅本地归档，未推送或PR。

前一f139候选双mean/p99改善，但photos.max失败。固定反例RGB(42,43,37)说明旧daad锚定cap57允许丢失当前af974已有改善；这不是对该像素追补的理由。本轮只改一项全域约束口径：对每个原RGB一律使用max(49,当前af974完整流与原独立四级参考的误差平方)，从af974重新开始，质量/标签/目标/规则/选择样本及原门槛不变。

对象是四张真实创意LUT的数值四级链（1910s→1920s→1930s→1940s），没有色彩域匹配证据，不称真实ISP或自然摄影管线。候选目前只通过选择，不把它写成已完整验收成功。

## 新旧约束与数据身份

新cap只从已存af974完整输出78eb…与原四独立表参考493c…派生，未读取照片名单、反例条件或频数来修改约束。完整256³逐块以int32向量平方和及独立逐通道int64平方和双算，0差异；逐色new<=old，0超过旧cap。统一公式严格收紧191色，其余16777025色相同，最大平方误差上限收紧28；af974初始0违规。

新Numpy文件SHA `b211f195efe0dc0f9d27b6487382d1c4f31f099f055d550384dde9228e4d3a77`，array SHA `b4fbbab8986be5bdcd7126db1083f3e496df94b093d7b81cecae41126eeff57d`。metadata完整记录旧cap文件SHA与来源。归档中的derived-cap-npy.zip仅压缩保存同一原字节Numpy文件，不改数组或重建约束。

points、原60图完整频数质量、T1/S(T1)、suffix、四原表、grid/idx、节点规则及目标权重全部沿用原SHA，没有新增(42,43,37)或任何训练色、图片或频数。标签根仍独立T1，loss=rho(p−T1)+rho(S(p)−S(T1))；精确整链reference只进入cap。S为冻结933a/95cb/932f三模型逐级RGB8映射。af974/78eb仍为唯一完整验收基线。

## 唯一整合执行与来源

新增`scripts/run_cinema_current_anchor.py`及`experiments/cinema-current-anchor-v1.json`，原cs/sj及所有辅助数值模块原封不动。两个旧集中合同的结果文件及全部模块SHA被冻结并核验，未重跑kernel合同；它们已覆盖合法cap、零质量、非线性后缀、完整状态/26方向、独立u64及fresh。新driver仅额外对已有字节派生cap全域双算和关系检查。

从af974首级原frac复制三份，先cs.propose九块（输出R/G/B各轴R/G/B）各一次，再sj.propose八色×26方向节点各一次；没有中间selection、额外sweep、权重或方法矩阵。没有加载旧aed/f139作为起点。

本轮重新生成的坐标checkpoint字节SHA恰好仍为aed888e75375e1e2cc1bff32f8fbe62b67afbfdb33d800bb521739aec76b5a41：新cap没有改变九块坐标的路径，反映确定性复现；不意味着跳过重跑。driver输入、日志、九块回执及来源快照都保留。节点阶段使用本轮checkpoint，新cap影响后续联合步选择。原模块scope文字含旧“aed”名称，driver保留inherited_kernel_scope_text并另记本轮实际checkpoint，未修改模块字节。

训练双项目标0.6769458587735461→0.5913351632500841→0.5435448149905596。坐标变化2126项、最大frac偏移43121；节点7095个、8796分量改变，1503次多通道联合。两阶段fresh/cap均0差异/违规，初始复制链与af974旧完整流逐字节相等。三路I/W约1.5GiB为节点阶段离线缓存，不当成运行时内存或速度声明。

首次入口曾在新driver的合同路径拼接ROOT[path]处TypeError退出，当时主目录未创建、cap派生/cs/sj调用均0。已保存preflight-driver和failure.json，仅修该路径为ROOT/path后才执行唯一实际拟合。该工程预检失败不隐去，也不虚计为一次数值实验；没有修改数据、计划、合同或数值内核。

## 唯一最终选择

只在两阶段完成后，对一个最终候选在原cube262144、guard20*4096作一次选择；旧基线只查af974已验完整流，真值查原参考缓存。中间坐标模型没有被评价/选择，未读取full/audit指标调参。

| 指标 | 已验af974链 | 最终候选 |
|---|---:|---:|
| cube mean | 1.018026809 | 0.981963842 |
| cube rms | 1.410686362 | 1.368806240 |
| cube p99 | 4.123105626 | 3.741657387 |
| cube max | 8.124038405 | 8.124038405 |
| cube cvar_1pct | 4.758563640 | 4.620673397 |
| photos mean | 0.864484839 | 0.825672867 |
| photos rms | 1.323092487 | 1.270433574 |
| photos p99 | 4.123105626 | 3.741657387 |
| photos max | 7.071067812 | 6.928203230 |
| photos cvar_1pct | 4.896166908 | 4.587918542 |
| photos worst_image_p99 | 5.196152423 | 5.196152423 |
| photos mean_image_cvar_1pct | 4.784029321 | 4.503949177 |

cube/photos mean分别降3.54244%/4.48961%，两个合并p99各降9.25148%；photos.max从7.071068降到6.928203。原双mean3%、mean/RMS/p99/max、cube及合并照片CVaR、worst_image_p99保护与至少一种p99严格改善全部通过，failures=[]、selected=true，训练新cap0。

guard20逐图mean/RMS均20好，p999好11平，max1好16平3差，CVaR全部20图改善。聚合门禁通过不代表逐图支配，选择数据历史已见，不称盲测。

最终NPZ `current-anchor-pipeline.npz` SHA `a399b72a2222acef815b6405ebd0132f94f1f3a4e4315f957e90b81f836744bb`，run身份`531fc6f95773405a290cc2c865b8dffc5ad1d63dfe57988744a2b0496c4506d3`。source_model_sha256与baseline_model_sha256均af974，direct_parent_coordinate_checkpoint_sha256另列本轮checkpoint；后三模型SHA另记。首级grid/shared idx与af974不变，channel_frac与本轮坐标checkpoint不变，只RGB8节点再按预定规则更新。保持实验NPZ表示，不冒充SLUT v1或官方支持。

## 环境、复现与未覆盖范围

Windows11 26200 x64/Ryzen9 8945HX、Python3.12.14/NumPy1.26.4/Numba0.60.0/llvmlite0.43.0；Numba4/OMP与BLAS1。目的为全域约束口径修正、固定预算拟合和选择；没有计时任务并行或性能比较。原两合同报告、源快照、新cap关系、两阶段回执及复现命令保留。

本阶段尚未执行新完整色域精度/独立逐级u64/实际原生四级/100图验收。只有根代理按事前冻结的完整验收口径通过后，才能给完整精度或后端结论。这里不改变默认、不宣称SOTA或全局最优。无官方Threshold，误差为欧氏RGB距离，不混称CIEDE2000。旧aed/f139等失败记录仍保留，不被追溯改写成成功。
