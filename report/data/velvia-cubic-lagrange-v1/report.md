# 唯一Q16 cubic Lagrange基：未达到预声明训练MSE门槛

Agent：Codex；Operator：WyEhNf；状态：按冻结规则停止。仅完成有理权重审计、连续近似LS求解和训练正规方程矩诊断；没有评价任何探针、创建SLUT、运行64顶点整数映射、native、新完整cube或百图。未改核心、默认、原生或根代理驱动，未提交、推送或创建PR。

当前单个三次基的完整均匀L2矩MSE为1.972246046，相对matched四面体1.852670449恶化6.454229%，没有达到预先要求的至少降低20%。因此没有进入后续探针评价，不更换基、网格或阈值以追求通过。

## 研究对象与坐标语义

计划在执行前冻结为`experiments/velvia-cubic-lagrange-v1.json`，只研究一个明确基。

原RGB8表SHA为6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7；原2dd模型SHA为2dd467b040a4ed25f9000e7debd085af4a07f08d780be2fbcd156c9aa8118947；原m33小数grid SHA为1b62bbc42278fc9deb993e1dc3b1c1973fbc9a47aa7e108d891c51cec26d2eb3。已核该网格与原权威idx/frac相同，没有改变原坐标自由度或使用新的来源。

每个axis/code取原cell i和frac，s=clip(i−1,0,m−4)，局部t=(i−s)+frac/65536，使用局部索引0/1/2/3的四点Lagrange多项式。该基建立在有效索引坐标上，不是按真实非均匀物理knots距离定义的三次插值，也不等价于B-spline或全局C1样条。结论只适用于这一预声明基。

以Q=65536、T=Q×t，四个Q16权重的精确有理式采用共同分母6Q²，分子分别为：

```text
−(T−Q)(T−2Q)(T−3Q)
3T(T−2Q)(T−3Q)
−3T(T−Q)(T−3Q)
T(T−Q)(T−2Q)
```

前三权重用整数floor(n/d+0.5)舍入，最后一个用Q减前三和，负权重不裁剪。随后用该量化Q16基矩阵本身做float64轴SVD伪逆和张量收缩，而非先拟合另一套浮点基再替换量化基。

拟合是同一完整16777216色上的均匀未舍入L2，连续节点无RGB盒、无ridge、无照片权重、tail或cap。节点仍按33³×3存储，但连续解不可部署；另外保存的RGB8节点只是统一clip+half-up后的容量控制，没有进行输出评价或整数再优化。

## 先行权重与累加器审计

完整枚举3×256行权重，检查内容包括有理常量恒等式、Q16常量守恒、端点stencil合法、索引0..32、负权重保留与权重量化误差。

- 每行四权重之和严格为65536，保留1466个负权重。
- 前三权重最大有理误差分别0.499443、0.499272、0.499718个Q16整数单位，均≤0.5。
- 最后一项最大误差1.127661个Q16整数单位，≤1.5；完整精确分子/分母存于results.json。
- 三轴最大整数L1和分别106768/106790/106744，实数L1约1.62915/1.62949/1.62878。
- 对任意RGB8节点，64项signed Q48累加器的保守绝对界为255乘三轴最大整数L1和的乘积，即310352570987078400；再加半向上偏置2^47后为310493308475433728，小于signed int64上限9223372036854775807。

这是本基在完整RGB8码值域上的权重/绝对累加界验证，不是64顶点前向实现已通过oracle的声明。因为训练MSE门槛失败，脚本中的signed Q48显式64权重与独立整数Horner路径没有执行，不能把未覆盖部分写成已验证。

## 环境、近似LS和停止口径

实际环境为Windows11 26200 x64、Ryzen9 8945HX、CPython3.12.14、NumPy1.26.4；OMP/OPENBLAS/MKL环境各1。仅NumPy float64张量操作，没有调用原生拟合或映射内核，也没有性能结论。

SVD的rcond固定1e-14。三轴基矩阵条件数约2.77847/3.41020/3.13530，左逆最大误差5.9561e-15；归一到1/64后的正规方程残差范数分别7.6941e-10、1.3936e-9、1.4654e-9。它们只是浮点诊断，未包含SVD、张量收缩、矩相减或残差求值的舍入区间，不是严格全局证书。

MSE口径为每个RGB输入的dR²+dG²+dB²再对完整cube取平均，不再除以3；它不是平均RGB欧氏距离，也不是CIEDE2000。

| 同完整均匀L2训练矩 | MSE | 与冻结matched四面体的关系 |
|---|---:|---|
| matched四面体参照 | 1.852670449 | 固定参照 |
| 本次Q16 cubic Lagrange | 1.972246046 | 恶化6.454229% |
| 预声明进入探针评价的上限 | 1.482136359 | 至少降低20%才触发 |

参照来自matched阶段results SHA=66de80cb4bfcd4c896634ec805c9c2b95c802c2614addebd0ec6ccac97cfc2a8，运行身份3848f243…。没有改用较弱的三线性参照，也没有用不同目标的实际2dd指标替换matched门槛。

当前连续节点范围−8.248487…256.610938，有13241个节点通道越出0..255。其输出仍可能产生额外过冲；本轮没有探针mean/RMS/p99/max结果，未评估裁剪/量化后的精度，不应将缺失指标写成0或通过。

## 容量、交付和限制

原2dd SLUT实测112063字节。本基的RGB8节点payload为107811字节，与33³×3一致，但这不代表旧SLUT语义或tetra/tri_float后端能够执行64顶点算子。没有创建候选SLUT，更没有验证文件格式、题面可接受性、native后端、实时速度或内存成本。显式算子族改变必须单独说明，不能把节点套给现有内核冒充实现完成。

本次身份5b60daf8ae084ed7ad6d2037226c2a84bf7d26577d657f0feba5d90e2c3145e3。源码SHA=4ae6bef2d9f61d94e40cf483f642391246d513e7e2a1923491bf9b985720e6d4。

- run.json SHA：67a57417bf854f3ee097bcf41e96dddce33bfe5eed396d6b33c596d158fe0c47。
- results.json SHA：9ff03c1b19f42a3f5352473e6ed7e1133eb9ff11ab1882453279e85f5b80afed。
- basis-and-nodes.npz SHA：9dc1eeab6241e13b5f1ff856ba7b4db6ea0030d48fb92c693d6f99ac8d56a206；含start/Q16权重、连续/RGB8节点与原grid/idx/frac。

```powershell
$env:PYTHONUTF8='1'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
artifacts/error-study-py312/Scripts/python.exe scripts/explain_velvia_cubic_lagrange.py --output artifacts/velvia-cubic-lagrange-v1-replay
```

源码、计划、节点和指标已保存，负结果保留。不追加基、阈值或预算；不据此否定所有高阶方法，也不声称本次显式算子已落地。官方数据和Threshold仍未知，无官方或SOTA结论。
