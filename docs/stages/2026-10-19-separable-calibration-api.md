# 精确单调坐标入口：能精确才接收

Agent：Codex；Operator：WyEhNf；模块与集中合同完成，未提交、推送或创建PR。

将Filmic特例中的区间推导整理成separable_calibration.exact_monotone(model, channels, maximum_shift=4096)。channels必须来自调用者对完整原表执行的curve.separable_channels；函数不以三个给定曲线代替原表结构证明。

入口支持输出通道置换及多个输出依赖同一输入轴。逐通道检查完整m³节点张量，再对每轴/码值求所有相关通道half-up区间的交集，叠加0..65536、总偏移和冻结首尾。将区间转为有效坐标q，求下界前缀最大值与上界后缀最小值；存在全局可行域时，把原单调q逐点clamp进去。三个非降序列的clamp仍非降，且所得解逐坐标距原点最近。

成功返回精确模型和报告，固定RGB8节点、idx、float网格及端点。不可行返回None，说明节点/单元不可达、共享轴区间冲突、端点、偏移或全局单调阻断；全局冲突附左右码值及界的见证。不自动放宽偏移，也不返回近似模型伪装成功。调用者负责明确回退原结构DP。没有改fit.py、cli.py或compatibility.py，根代理另行集成显式方法，不改默认扫描。

scripts/verify_separable_calibration.py集中一次通过11项：下降/常量/轴置换、共享轴兼容与冲突、端点、总偏移、各点可达但全局单调无解、节点张量破坏、未验证来源，以及Filmic17/33已验零误差模型的SHA精确复现。17³复现d8186ab6…，33³复现49231a37…。仅有限合成合同及同SHA复现，没有追加其他来源的全域或百图验收。

测试目的为通用精确接口的数学/整数/回退契约。Windows11 26200、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、Numba0.60.0；Numba4、BLAS/MKL/OMP=1；不测性能。精简原始回执与源码见report/data/separable-calibration-api-v1。此前静态/直接两个阶段的实测源码快照保持原样。

另对PR41 Emerald只完成同SHA历史基线重建及解析可行性：m17三轴最小必要偏移547/102/0，m33为1093/469/1，均满足4096且无单调阻断。没有生成Emerald校准模型，不能把可行性预期当作实测零误差。
