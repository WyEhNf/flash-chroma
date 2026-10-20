# 坐标读取与节点局部性：四个方向在实现前停止

Agent：Codex；Operator：WyEhNf；Task：继续寻找首级映射的时间优化依据；Status：Completed（结构剖面与对象比较完成，没有新运行库或性能验收）。

本轮没有找到值得进入新一轮测速的候选。三通道共享顶点排序的八像素覆盖只有34.09%；共享端点标志的压缩不满足精确性条件；首级节点改成R连续只减少约1%的逐块缓存行；仅改变Skylake服务器调度目标则生成相同对象。四项原始结果和反例均保留，不降低事先条件或追加排列/标志扫描。

## 想省掉什么，为什么没有继续

**共享顶点读取。** 当前首级三个输出通道各自有坐标，同一个输入颜色的三个四面体不一定相同。若三个通道的稳定顶点排序一致，可保留各自权重而共享四个节点值。比较使用严格关系`y>x、z>x、z>y`，相等时优先R、再G、再B；不能只看三个坐标接近，或直接复用旧代码在全相等时加载的零权重顶点。

固定100图中，逐像素排序一致比例为67.8897565%，但整个八像素组全部一致的比例只有34.0914205%，低于运行前固定的60%资格。每组判断和回退都有成本，所以没有实现这个分支。最先发现的颜色为`RGB=(96,95,95)`，三通道排序类别为`6/6/4`，完整九个坐标及图像位置已保存。这个反例说明无条件共享几何会算错；它不是现有内核的错误报告。

**共享ONE端点标志。** Q16坐标允许65536，需要17位。提议把G/B低16位放入同一u32，再用R的bit16恢复两个端点；精确成立的条件是每个轴、每个输入码的三个通道ONE标志完全相同。完整九张256项表发现两个不满足条件的轴/码，共三个错误展开值：

| 输入轴/码 | 原R/G/B坐标 | 错误共享标志后的R/G/B |
| --- | --- | --- |
| G/38 | 65536 / 65524 / 65533 | 65536 / 131060 / 131069 |
| G/147 | 63637 / 63728 / 65536 | 63637 / 63728 / 0 |

因此不写压缩实现。当前表没有65535并不能证明共享标志合法，也没有据此改换哨兵或扫描另一种编码。这里只做独立数学资格检查，未新增C++正确性测试。

**首级节点R连续。** 这是对首级RGB32节点的完整置换设想，与此前后缀缓存修订13的布局不同。本轮精确复现现有AVX2实际访问的八组节点地址，包括相等坐标处的零权重顶点，只把物理索引从`(R*m+G)*m+B`换成`(B*m+G)*m+R`。不改变节点值、网格或排序，不扫描其他排列。

对全部16种u32自然对齐偏移，八像素组的缓存行数比为0.986228..0.995074，逐4096像素块为0.989897..0.991239。逐块只减少约0.88%–1.01%，没有达到事先的至少10%；逐组条件虽满足，也不改变总拒绝结论。没有节点重排的原生实现。这些是访问行并集，不是真实cache miss或时间收益。

**服务器调度选项。** 保持同一缓存修订4源码、`-O3 -mavx2 -ffp-contract=off`及其余选项，只比较`-mtune=skylake`和`-mtune=skylake-avx512`。[GCC15.2说明](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/x86-Options.html)区分调度目标与ISA选择；这里没有启用AVX512、FMA、全局march或fast-math。

两个对象SHA256均为`823a27fa6b8018b969758d0e62597f3f60a2369a2be9018c34282769aee0d1d3`，也精确复现旧参考4对象；所有函数的解析指令同样相等。没有新的指令序列可比较，因此没有链接/加载、MCA或重复测速。这个结论仅限本机MinGW GCC15.2，不能替代Linux GCC对象比较或Skylake实测。

## 环境、覆盖与复现

实际环境为Windows11 26200 / Ryzen9 8945HX，Python3.12.14 / NumPy1.26.4 / Pillow，MinGW GCC15.2。剖面是CPU上的NumPy数据分析，线程数及原生后端不适用；编译器比较只生成两个对象，没有执行内核。没有并行agent、拟合、图像输出、完整域扫描或性能调用。

复用a399模型与固定100张1024×768 RGB8照片，逐图原始字节SHA和合并流`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`均核对。坐标剖面覆盖78643200像素、9830400个八像素组；节点剖面另覆盖19200个4096块及全部16种基址余数。侧表SHA为`85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff`。

下列命令记录实际运行入口；复现须使用新输出目录。两项剖面只使用历史计划的固定输入字段，不宣称重新验证了历史构建源码。编译比较另有冻结计划和完整源码/工具SHA。

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/profile_skylake_coordinate_reuse.py --plan experiments/skylake-r-contiguous-v1.json --bundle artifacts/skylake-server-matrix-v1 --output artifacts/skylake-coordinate-reuse-profile-v1
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/profile_skylake_node_layout.py --plan experiments/skylake-r-contiguous-v1.json --bundle artifacts/skylake-server-matrix-v1 --output artifacts/skylake-node-layout-profile-v1
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/inspect_skylake_server_tuning.py --plan experiments/skylake-server-tuning-v1.json --output artifacts/skylake-server-tuning-static-v1
```

[完整归档](../../report/data/skylake-coordinate-locality-v1/README.md)保存逐图结果、全部端点反例、两个对象及完整反汇编/函数/命令、源码与小型固定输入。235MB照片流沿用已有服务器包，不重复装入归档。编译命令的包含响应文件保留原本机路径，异路径复现需要显式重建包含路径并记录映射，不能声称原路径计划可直接移植。

本轮未增加原生候选：此前18项中10项执行性能、8项静态停止的计数不变。当前服务器候选集合与4对13准备包不变，13在Windows最差进程门槛失败的事实不变。仍需实际Skylake SKU/OS/GDS/入口、官方数据和Threshold、派生缓存许可。误差口径仍是RGB欧氏距离，没有新精度、SOTA或服务器速度结论。
