# 固定两图频数归因归档

0843主要退化不是未见/低频转移：RGB(16,16,16)占该图80.167%，其旧→中间输出变化已经解释主要观察到的误差和增加，新分通道阶段对该色RGB8输出未再改变。该色训练出现4767次，但仅占60图像素0.01010%，不能把≥32分箱等同于足够训练概率。

[报告](report.md)、[计划](plan.json)、[运行身份](run.json)、[结果](results.json)、[清单](manifest.json)保存范围与证据。frequency-groups.csv提供两图固定四组的计数、误差和、毛改善/毛退化及净mean贡献；top-colours.csv提供每图top64摘要与9项frac偏移，results.json保留完整target/旧/中间/新RGB、坐标及分解。frequency-group-histograms.npz保存组内旧新平方距离整数hist，intermediate-counterexamples.npz仅118色及一次独立u64结果。measured-source.zip保存实际脚本/计划和依赖。

中间模型/新候选随档，明确新nodes/shared idx/grid与iter003相同。没有中间整图流，所以不归因整图阶段mean；top按退化选择，不是无偏样本。两图整图仅查既存旧/新输出；总计2图解码、0整图模型前向、中间118色一次前向，无新拟合、其它颜色/图片扫描、原生或性能测试。

大表、旧/新完整流、频数和两张原图不重复归档，计划绑定同SHA源路径。不能由频数相关性称因果或据此改权重/约束；本轮停止。未改核心/根driver或commit/PR/push。
