# 分通道坐标：精度收益、原生落地与实际代价

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成，保留精度/速度取舍，不PR、不推送、不替换默认。

## 当前结果

前两个阶段已经冻结一个非可分离Velvia新模型：33³ RGB8节点和shared idx不变，三个输出各用自己的Q16轴坐标。相对原2dd完整域mean下降5.8423%、p99下降9.6492%，百图mean下降4.4704%，原聚合门槛通过。97张照片mean改善、3张退化，audit20的RMS略增；这些限制保留，不能把平均改善写成逐图或全部子组改善。选择、完整精度及全部原始数据分别见前阶段[选择报告](2026-10-19-velvia-channel-coordinates.md)和[完整验收](2026-10-19-velvia-channel-coordinates-accept.md)。

本阶段把该NPZ接入独立C ABI，实际完成单级及四级等距控制链的标量/AVX2完整输出、100图一致性。首版受控测速发现较大运行成本后，集中改进硬件实现，保持同一节点、idx、三份frac和所有输出字节不变。最终同机比较：

|100图四级摊销apply，ms/图|1线程|4线程|
|---|---:|---:|
|原2dd普通四面体|9.55802|3.35974|
|同一精度候选的首版原生实现|16.37587|6.14405|
|同一候选的packed SIMD实现|13.40442|4.83115|

三个新进程的配置顺序为ABC/BCA/CAB，每配置完整预热及SHA验证后计时五组，各组100图、4级。表格为各进程中位数的中位数；原始15轮/配置、进程范围、copy+apply和同进程比值均归档。按进程配对，packed相对首版耗时降低17.68%/21.37%；相对原2dd仍增加41.94%/43.80%。不是精度、速度和内存的同时支配，现阶段属于有明确代价的精度选项。

## 实现方面

- 新增可选`JSHC_ENABLE_CHANNEL_RESEARCH`，默认OFF。生成独立共享库，只暴露标量/AVX2和OpenMP，不修改SLUT v1、公共模型结构或默认运行时。原核心按原算法执行无侧表的阶段，混合链每级用自己的m和stride。
- C ABI加载base的grid/idx/nodes，另读取`uint32[3][3][256]`坐标侧表；先核Q16范围、非降坐标和端点，再准备数据。每级先完成全部三个RGB8输出，再进入下一独立LUT。
- 模型准备时原地合并`idx<<17 | frac`，保留65536端点；三个输出共用立方体两端点的节点gather；高/低轴和中值公式取代完整交换网络。shared路径仅在完整侧表相等证明后启用，复用几何和四个节点。这三项作为一次合并改动比较，没有分别测独立贡献。
- AVX2仅在独立TU启用，分派器沿用真实CPUID/OSXSAVE/XGETBV检测；八像素块严格16+8字节读写，剩余0..7像素标量。像素内没有动态分配、CPUID或完整256³查表。四级向量寄存器内保留逐级整数舍入。
- Python显式核库SHA和算法revision，用上下文管理句柄。静态审计发现create成功后读取来源hash异常时会泄漏句柄，已经补清理，并注入OSError验证恰好destroy一次。opaque handle要求调用者不在apply时destroy。

研究入口`apply_channel_model.py`可以直接把NPZ用于图片，输出PNG、hash回执及私有适配缓存；一个实际1024×768例子与完整域流的输出SHA相同。具体命令及ABI合同见[运行库说明](../../experiments/channel-runtime/README.md)。该入口尚未接入现有GUI、C99或公共CLI，移动端也未实测。

## 正确性及四级范围

最终集中合同覆盖11种长度0/1/7/8/9/15/16/17/4095/4096/4097、1/4线程、标量/AVX2、0..3字节偏移、哨兵、混合m17/18/25/33四级链，与独立uint64参考一致；另核普通shared和三份相同侧表两种路径，以及ABI错误/构造异常清理。中间版本只在实际实现变化后重核，不能按重复运行累计独立用例。

原型和packed两份库分别在单级及四级控制链上执行完整256³、100图；两后端0字节差异，packed未改变模型结果。单级完整输出SHA为`945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0`；四级为`7297346aa45cb2260179eea546ce8ec32df2c7217cedb85c7402ae994153be99`。原型数值DLL为`6905b23636eaadeb15af1756b108a35619042d3da131ebf40ea1718ea0ebf500`；packed DLL为`7ceb30d7913a8cf032e1828c25c3fe062082be8e9d531d105282ba8d1794b072`，ABI1/revision2。

四级固定为Velvia、cycleGBR、invertRGB、swapRG，四个原LUT的完整RGB字节SHA互异；后三者的全部节点及768码值公式先证明整数精确，再完整生成核原LUT SHA。它们保持RGB欧氏距离，所以首级误差分布会完整传到终端。本阶段四级证据限这条可解释控制链，尚未研究自然ISP后缀对该新表示的误差放大；不把它称作自然四级泛化。新模型的完整独立uint64参考复用前一阶段冻结流，原生输出逐字节对照该流及已证明的控制公式。

## 内存、环境和复现

33³节点仍是107811字节。理想替换原frac的净增量为6144字节；当前可执行适配器保留base原frac，实际额外保存完整9216字节。四级输入模型文件合计168460→177676字节；最终准备模型对象容量核算397092→406212字节。后者包括RGB节点、packed节点和模型容器，不是峰值RSS。100图源像素为235929600字节，基准另外分配同大小工作区；加载/解码/模型准备/hash/误差统计均不计入apply。

环境为Windows11 26200 x64、Ryzen9 8945HX16核32线程、32GB；Python3.12.14/NumPy1.26.4/Pillow10.4；GCC15.2 Release `-O3 -DNDEBUG`、OpenMP、独立AVX2 TU，CPP SIMD/Zig/Rust关闭。基准NumPy/BLAS/MKL/OMP环境各1，原生请求线程按配置1/4，`OMP_DYNAMIC=FALSE`；没有其他数值任务并行。未锁频、温度或绑核，因此披露进程范围和配对比，不作统计显著或官方服务器结论。

本阶段入口与冻结计划：

```powershell
artifacts/error-study-py312/Scripts/python.exe scripts/verify_channel_native.py --library artifacts/channel-native-runtime-v3/jshc_channel_packed.dll --output artifacts/channel-native-contract-packed-v1
artifacts/error-study-py312/Scripts/python.exe scripts/accept_channel_native.py --plan experiments/channel-native-accept-packed-v1.json --output artifacts/channel-native-accept-packed-v1
$env:OMP_DYNAMIC='FALSE'
$env:OMP_PROC_BIND='FALSE'
artifacts/error-study-py312/Scripts/python.exe scripts/bench_channel_native.py --plan experiments/channel-native-benchmark-packed-v1.json --output artifacts/channel-native-benchmark-packed-v1
```

其余线程/编码环境同前阶段；已完成目录不覆盖，历史复现用对应ZIP源码。构建命令、两个库/依赖/源码hash、所有合同、完整回执、单次应用和原始计时见[精简证据](../../report/data/channel-native-v1/README.md)。本阶段以9be1bcb为起点，与代码一起本地中文提交保存。

RGB距离不是CIEDE2000，官方数据/Threshold仍未知；没有官方得分、SOTA、GPU、ARM/C99新表示或默认升级声明。

交付静态核对使用Windows上的CPython3.13.12标准库：117项归档SHA/大小、最终合同绑定的9份原生来源及Python AST通过；3个worker的原始5轮计时独立复算与6项汇总/4项配对比一致，相关文档相对链接可达。仅修正Emerald归档副本的自链接及清单，没有执行数值或性能重测。静态回执收于本阶段证据包。
