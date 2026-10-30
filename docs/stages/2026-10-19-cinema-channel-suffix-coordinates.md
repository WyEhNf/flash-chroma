# Cinema首级分输出坐标九块研究

Agent：Codex；Operator：WyEhNf；状态：固定实验完成，未入围，仅本地归档，未PR/push。

对象为四张真实创意LUT的数值四级链（1910s→1920s→1930s→1940s），无色彩域匹配证据，不称真实ISP或自然摄影管线。新增channel_suffix_coordinates模块、独立合同/driver/计划，不改旧文件；从已验af974首级复制frac三份，九块单输出/单轴完整Q16单调DP一次，首级节点/idx/grid/端点及后三模型冻结。

直接复用旧canonical cache、原60图频数质量、后缀S和原cap；标签始终T1及S(T1)，精确整链reference只cap。初始复制整链与已验78eb流全字节相等，旧最佳cap可行；四模型/四表/两标签和cache源SHA匹配。集中m17/m33×9种输出/轴的65537状态、非线性S、独立u64/单调/fresh合同通过。

真实九块全部接受，训练双项loss .676945859→.591335163，2126坐标变化、最大frac偏移43121，cap/fresh0差异。原选择cube mean1.018026809→.996018922（降2.1618%，不足3%）；photos mean.864484839→.834815405（降3.4320%）、p994.123106→3.741657。其余聚合RMS/p99/max/CVaR/worst保护通过，但唯一cube mean3%失败，停止不full/native/100图/性能，不升级基线。逐图仍有mean/RMS/max回退，完整披露。

环境Windows11 26200/Ryzen9 8945HX、Py3.12.14/NumPy1.26.4/Numba0.60.0、Numba4/BLAS1。新NPZ实验表示增加6144坐标字节，不冒称SLUT v1/官方支持/同速度；选择历史已见，非盲测。完整来源、数值、逐图及复现命令见[精简归档](../../report/data/cinema-channel-suffix-coordinates-v1/README.md)。
