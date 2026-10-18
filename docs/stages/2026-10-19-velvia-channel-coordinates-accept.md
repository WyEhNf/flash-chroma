# 分通道坐标的完整精度验收通过

Agent：Codex；Operator：WyEhNf；状态：唯一冻结模型通过研究核完整精度聚合门槛；本阶段原生/性能未验证，未提交、推送或PR。

在上一阶段选择完成后，另立冻结计划，只对同SHA候选NPZ运行一次完整256³和100张照片。研究输出与独立比较器/uint64 oracle完整逐字节一致，原逐色cap违规0；完整cube mean由0.9416888345降至0.8866728651（5.8423%），p99由7降至6.32455532（9.6492%）；100图mean由0.9263840942降至0.8849712151（4.4704%）。原完整聚合RMS/max/CVaR、照片最差p99保护均满足，accepted=true。

限制必须同时披露：100图mean97好3差、p9914好78平8差、CVaR65好35差；audit20 mean仅下降2.3457%且RMS略退化，不能称三个子组各达到3%、逐图全不退化或独立盲测。完整逐图差值、分组、全域直方图/top128、流SHA及来源见[精简归档](../../report/data/velvia-channel-coordinates-accept-v1/README.md)。完整输出本地文件为`artifacts/velvia-channel-coordinates-accept-v1/cube.rgb`，SHA945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0。

环境为Windows11 26200/Ryzen9 8945HX、Py3.12.14/NumPy1.26.4/Numba0.60/Pillow10.4，Numba4/BLAS1。目的为一个冻结新表示的完整精度和整数正确性验收；未追加拟合、候选或性能比较，未修改原selection源码/报告、io/interp等既有模块或根driver。独立入口`scripts/accept_channel_coordinates.py`，计划`experiments/velvia-channel-coordinates-accept-v1.json`。

候选仍是新增NPZ表示，不属现有SLUT v1；frac增加6144字节、速度未知。本阶段不包含C++/SIMD原生一致性、性能、四级泛化或官方Threshold/SOTA认可；主代理另行推进原生证据，不能与本阶段混写。
