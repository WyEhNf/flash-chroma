# Cinema固定新坐标的单轮RGB联合节点耦合

Agent：Codex；Operator：WyEhNf；状态：固定实验完成，未入围，仅本地归档，未PR/push。

对象为四张真实创意LUT数值四级链，无色彩域匹配证据，不称真实ISP/自然摄影管线。从上一未全验aed坐标起点，全部几何/后三模型冻结，只首级节点做一次8色26方向RGB联合±1。af974/78eb仍为完整验收基线，aed只作提议起点和增量观察。新增独立模块/合同/driver/plan，不改旧模块/native/default。

目标保持T1与S(T1)双loss，精确整链reference仅旧cap；每方向先算真实三路权重的完整RGB8 p，再查非线性S(p)直接求cost和cap，不线性相加通道/后缀。原质量/标签/cache/cap均不变，含零质量硬约束，未加入照片反例。

集中m17/m33全部实际正支撑节点26方向、独立u64+非线性suffix cost/cap、边界/零质量/geometry/fresh合同通过。真实8色7094节点/8800分量移动、1505多通道步，双项loss .591335163→.543568757；cap/geometry/fresh0差异。

对af974原选择cube mean1.018026809→.982005132、photos mean.864484839→.825900527，均超过3%改善；两p994.123106→3.741657。但photos.max7.071068→7.549834，唯一photos.max门槛失败，停止不full/百图/native/性能。旧cap锚定更早daad链，cap0不保证相对af974照片max不退化；未改锚点或放宽门槛。

Numba4/BLAS1，环境Windows11 26200/Ryzen9 8945HX、Py3.12.14/NumPy1.26.4/Numba0.60.0，三路I/W为1.5GiB离线缓存。详细来源、两基线/逐图、合同和复现见[精简归档](../../report/data/cinema-channel-suffix-joint-nodes-v1/README.md)。
