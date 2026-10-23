# 边界消失局部混合的最小可行性探针

代理 `/root/tail` 按本会话用户授权，只检查原Velvia两个max点及所在两个cell的全部612个RGB8输入。固定原3e5f节点/Q16轴，研究原方向与mask1/2的局部混合，以避免自由cell方向的面接缝及相容stripe的整层代价。κ=2帽函数未能改变其中一个原max点，必要条件失败；没有继续全域选择或拟合。

借鉴[DefElement的bubble定义](https://defelement.org/elements/bubble.html)中边界归零的性质，并参考[Basix官方有限元接口](https://docs.fenicsproject.org/basix/main/python/_autosummary/basix.finite_element.html)。本探针使用每个输出通道的Q16帽函数 `w_c=2 min_a(f_ca,65536-f_ca)`，不是该文献的标准多项式bubble或其求解算法。其系数在对应cell面归零，混合在面上退回原方向；这只是代数构造，本阶段未做完整面/真实RGB8邻接终验。

设原/替代方向的未舍入Q16累加器为A0/Ad，输出为 `((65536-w_c)A0+w_c Ad+2^31)>>32`，一次half-up舍入到RGB8。NumPy uint64混合与Python任意精度整数逐项相同，w=0恒等检查通过；原方向612个输出与既有完整945d流逐字节相同。分输出权重并不保证RGB欧氏误差单调，因此实际评估全部612个支撑，不能只看两个点。

| cell/点 | 原mean / max | mask1混合mean / max | mask2混合mean / max |
| --- | --- | --- | --- |
| 31725，324色 | 16.662059 / 41.012193 | 13.645027 / 41.012193 | 13.841882 / 41.012193 |
| 31726，288色 | 16.253815 / 41.012193 | 11.878600 / 39.012818 | 12.587699 / 39.012818 |

原max点(239,252,113)对蓝输出的最近面距离720，对应w=1440/65536。两个方向都仍输出[246,255,38]，参考[247,255,79]，d²1682完全不变。另一点(239,252,114)蓝w=13634/65536，输出从[246,255,39]变[246,255,41]，参考[247,255,80]，d²降至1522。局部mean/p99改善不能弥补第一个max点不变；本阶段按原冻结κ=2停止，不能把它推广成全部bubble机制无效。

Windows11 26200/AMD64、Ryzen9 8945HX，Python3.12.14/NumPy1.26.4；OMP/BLAS/MKL环境1，仅NumPy与Python整数，未调用JIT、原生或性能计时。完整参考/基线流只用于哈希和局部取数，没有映射完整域，也未验证100图、全域mean/p99/max、表示许可、运行内存或50%速度底线。

实现为 `scripts/probe_velvia_bubble.py`，静态归档为 `scripts/archive_velvia_bubble_probe.py`。[精简证据](../../report/data/velvia-bubble-probe-20261024/README.md)包含完整局部结果、两个点的分输出分数/权重、输入与源码SHA。后续若从未舍入累加器的解析区间推导新的最小整数斜率，应另立阶段，明确其参数来自训练极值，不覆盖本阶段或称作盲测。

```powershell
& $py scripts/probe_velvia_bubble.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/velvia-bubble-probe-v1.json
& $py scripts/archive_velvia_bubble_probe.py --output artifacts/velvia-bubble-probe-archive-v1
```

输出须不存在，`$py`指向冻结Python环境。没有新默认模型。
