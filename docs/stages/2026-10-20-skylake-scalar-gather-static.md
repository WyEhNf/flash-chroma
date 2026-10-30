# 软件gather与通道几何复用：先排除不成立的提速前提

Agent：Codex；Operator：WyEhNf；Task：检查Skylake相关的非连续读取成本及固定模型的几何结构；Status：Completed（静态研究停止，未采用新后端，整体时间优化继续）。

本阶段没有做性能测试。一个软件gather原型确实消除了实验SIMD对象中的硬件gather，但生成代码失去四级融合，静态指令和栈访问预算明显增加；目标GDS状态仍未知，暂不值得在AMD追加数值/性能验收。另对固定侧表的全部轴对检查发现，各输出通道的四面体排序并不相同，不能直接把三路几何合为一路。

## 为什么研究软件gather

gather一次按八个索引读取不连续元素。当前实验内核显式使用AVX2 intrinsic。[Intel说明](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/gather-data-sampling.html)指出，部分受影响处理器启用GDS微码缓解后，gather结果可用延迟增加；减少gather可能缓解相关工作负载的性能影响，而编译器选项未必改变显式intrinsic。[Linux文档](https://www.kernel.org/doc/html/latest/admin-guide/hw-vuln/gather_data_sampling.html)说明如何读取实际状态。上述依据只支持研究方向，不能证明本项目或尚未取得的Skylake必然受影响，不改变任何安全设置。

参考为无缓存坐标差修订5。候选在`experiments/skylake-scalar-gather-runtime`以私有命名空间和修订8保留全部布局、Q16、节点、逐级RGB8、尾部和分派，只把读取原语换成core已用的“八个标量读取加SIMD组装”。不加派生颜色表，不扫描轴/节点混合策略或编译开关。计划为`experiments/skylake-scalar-gather-v1.json`。

实际Windows11 26200 / Ryzen9 8945HX / Python3.12.14标准库 / MinGW GCC15.2 Release，AVX2 TU为`-mavx2 -mtune=skylake -ffp-contract=off`，无AVX512/FMA/fast-math或全局march。只构建、反汇编和静态分析，没有加载候选。参考的运行包装与SIMD对象，均与早先已验修订5对象逐字节相同。

## 实际生成代码与停止决定

| 静态项 | 参考原九表路径 / 差值路径 | 软件读取对应路径 |
| --- | ---: | ---: |
| 每8像素固定四级循环gather | 38 / 35 | 0 / 0 |
| 循环内函数调用 | 0 / 0 | 4 / 4 |
| 完整静态指令预算 | 570 / 575 | 1456 / 1402 |
| rsp操作数预算 | 38 / 41 | 173 / 159 |

候选整个实验SIMD对象为零gather；这不表示整个动态库为零gather，无侧表仍按原规则委托既有core。编译器将首级和三个共享后缀分别调用，每次8像素发生四次函数调用。表中候选预算按完整被调函数及调用次数求和，包含序言/尾声/反汇编填充，不能当作动态指令数，更不能换算成相同比例的耗时增长。

不只看表面很短的22条指令循环，也不把40/41条指令的外层循环误当作全部工作。`inspect_skylake_scalar_gather.py`明确解析两条固定路径的全部直接调用，拒绝未知目标/嵌套调用，保留整个对象和所有循环。消除一类指令同时引入明显组装、栈和调用代价，未形成足够的本机时间收益依据；停止于静态阶段。没有执行有限整数合同、完整色域、百图、MCA或性能，不能声称实现已正确，也不证明开启GDS后的目标Skylake一定更慢。

## 通道几何能否共用

模型仍为PR #42固定a399，侧表SHA256 `85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff`。三对输出通道、三对输入轴，每对枚举256×256码值，共589824个静态坐标比较，没有调用LUT像素核、拟合或扫描新LUT家族。

三对输出通道均不存在相同的全部轴表，而且每个输入轴对都存在严格排序反转，不能归咎于相等值的排序约定。例如输入R码值1、G码值210时，输出R所用的两个Q16分量为17047/18312，而输出G所用分量为16441/9730；前者G分量较大，后者R分量较大。因此“始终共用排序和中间顶点”的前提不成立。完整RGB `(1,210,0)`的三个分量及最大轴也保存于静态回执。

这只否定无条件复用的现有证明前提，不等同于已经测出某个错误输出：若要进一步共用，还需要节点结构证明或运行时一致性判断。不能因为同一网格、共同基点或坐标差可压缩，就跳过三路不同的几何。本轮没有实现该捷径、没有统计照片命中率或为它运行性能。

复现静态分析：

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/inspect_skylake_scalar_gather.py --plan experiments/skylake-scalar-gather-v1.json --build artifacts/skylake-scalar-gather-build-v1 --prior-build artifacts/skylake-delta16-build-v2 --output artifacts/skylake-scalar-gather-static-new --objdump E:/mingw64/bin/objdump.exe
```

构建命令、原字节源码、二进制/对象、全部汇编、初步清点及最终可复现静态回执见[档案](../../report/data/skylake-scalar-gather-static-v1/README.md)。新候选不进入现有四方案服务器包或默认后端。下一项工作单独检查缓存命中后的重复RGB拆分/合并；不靠重测本候选寻求通过。Skylake具体型号/系统/GDS、官方数据/Threshold及侧表/派生缓存许可仍待取得。
