# 分输出通道坐标的唯一候选入围

Agent：Codex；Operator：WyEhNf；状态：集中合同和固定9块拟合完成，选择入围；原生与完整终验尚未执行，未提交、推送或PR。

本阶段将原三通道共用的Q16坐标改为每个输出通道各自一份，仍共用原33³ RGB8节点和shared idx，不改本级原表标签。起点三份复制与旧模型严格等价，只固定节点按R/G/B输出、各R/G/B轴执行9块单调DP一次；使用原完整域/60图质量与逐色cap，没有追加轮数、照片解码或方案扫描。

集中合成合同先核m17/m33复制等价、独立uint64前向；九种通道/轴组合的全部65537状态成本最大差1.24e−14，cap与缓存差0。真实拟合9块均接受，训练cap0，末尾重新计算缓存一致。最终一次旧样本选择相对2dd：cube mean降5.9062%、照片mean降3.9146%，cube p99由6.52446降到6.16441，入围。相对实际iter003起点，本轮增量仅cube0.3883%、照片1.2745%，cube p99未再降，不能把累计收益全归新表示。

20张guard逐图mean19好1差、p994好12平4差、CVaR11好9差，不称逐图非退化或盲测。完整结果、候选NPZ、合同、计划、来源与范围见[精简归档](../../report/data/velvia-channel-coordinates-v1/README.md)。源模块为`python/lutlab/channel_coordinates.py`，独立驱动为`scripts/run_channel_coordinates.py`。

该表示不属SLUT v1：frac payload由3072增至9216字节，权重计算也可能更多，不能称同内存/速度或官方支持。只保存NPZ，没有C++、新全域流、独立完整域oracle、100图或性能测试，入围交主代理另行原生落地/终验。旧固定坐标表达能力证书不适用新表示。环境为Windows11 26200/Ryzen9 8945HX、Py3.12.14/NumPy1.26.4/Numba0.60、Numba4/BLAS1；未修改既有模块、核心、根driver或默认。
