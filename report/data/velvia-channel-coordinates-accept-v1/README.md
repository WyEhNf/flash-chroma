# 分通道坐标完整精度验收归档

唯一冻结NPZ通过原完整聚合门槛：cube mean下降5.8423%、p99下降9.6492%；100图mean下降4.4704%。完整研究前向与独立uint64 oracle逐字节一致、逐色旧cap违规0。候选NPZ仍为SHA3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0，没有新拟合或调参。

[报告](report.md)、[计划](plan.json)、[运行身份](run.json)、[结果](results.json)、[清单](manifest.json)记录完整范围。cube-histogram.npz含完整平方距离直方图和top128原色；per-image-comparison.csv含全部100图五项指标的旧/新值、差值、分组及SHA。measured-source.zip保存实际验收脚本和依赖。原拟合阶段run/selection与候选随档绑定，原selection报告和源码未修改。

本地完整cube.rgb有50331648字节，SHA945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0，精简归档不重复该50MB流、原表、cap或照片。计划与manifest.external_artifacts记录来源位置和hash。

聚合通过不等于逐图非退化：100图mean97好3差、p9914好78平8差、CVaR65好35差；audit20 mean下降2.3457%但RMS略增。历史各分组已见，不称盲测。没有C++/SIMD或性能结果，不能拿旧基线原生记录当新模型原生通过。

该表示增加frac并可能增加计算，不是现有SLUT v1或官方认可，未替换默认；没有四级链/官方Threshold/SOTA结论。本阶段没有修改既有核心/根driver或提交推送PR。完整复现环境与命令见报告。
