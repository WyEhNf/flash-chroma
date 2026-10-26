# 16题：通用节点RGB24无损存储

这是继通用冻结句柄后的独立第六阶段，固定同一a399和一般随机四级模型，逐个节点完整保留RGB8三个字节。一般四级实际capacity为206,020 B，比specialized v2的487,737 B减少57.76%，比上阶段268,308 B再少23.21%。本轮四进程同场实测最差吞吐保留单线程79.19%、四线程81.30%，精度保留100%，四组A/A控制有效。单线程没有达到80%，两线程情形合并只授予70%档，不能因接近门槛升档。

a399四级为450,344 B，比specialized的1,058,292 B减少57.45%，比上阶段594,072 B再少24.19%；但相对同场最快78/80，最差吞吐仅2.61%/3.13%，仍严格拒绝全部50%以上档。

## 读取合同与参考依据

原RGB32每节点最高字节恒为0，但普通C++不允许任意把三字节流当成不对齐int对象解引用。新库仍以owned `vector<uint32_t>`管理存储和对象生命周期，通过unsigned-char对象表示规则复制连续RGB字节。每级实际分配`ceil(3N/4)+1`个uint32对象，尾部额外guardword归句柄所有且初始化为0；没有要求用户节点或图片留padding。

AVX2像素TU将节点索引变为3*i，以scale=1执行一次VPGATHERDD，再mask24；轴表仍用原scale=4读取。这里依据的是[Clang intrinsic文档的Load32字节地址语义](https://clang.llvm.org/doxygen/avx2intrin_8h_source.html#l04981)与[Intel gather操作文档](https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/intrinsics-for-gather-operations.html)，没有把intrinsic扩展等同于ISO C++普通int解引用。最后节点多读的一个字节始终位于owned guard区域；其他节点的第四字节虽属于下一节点，但被mask丢弃。索引最大3*(33³-1)=107,808，远小于有符号32位索引上界。

本机GCC15.2头文件直接转入gather builtin，发布的objdump原件确认节点生成scale1、轴表生成scale4。无需第二次对齐gather与移位拼接，本阶段只冻结单gather方案。标量路径按三个unsigned-char显式组合LE RGB，无普通不对齐uint32读取；整个句柄仍是C++17/原SLUT加载器，不能由此宣称独立C99或整库big-endian认证。桌面多线程仍使用OpenMP。

## 正确性与边界

研究库ABI1/revision1002，所测DLL SHA-256为`5c63a735f188b6d32406912763fe321de50ef47539221c4d25e82de67db4a3ec`。上一阶段已测运行源未改，新快照在`experiments/rgb24-sparse-runtime`，原3/4级校验及RAII生命周期保留。

- 独立节点probe覆盖N=1/2/3/4/5/7/8/9/15/16/17/33/4913/5832/15625/35937，每个16组、每组8节点，总256组。实际映射存储的guardword后紧贴Windows PAGE_NOACCESS，每组必含最后节点和首节点，并随机覆盖3*i的四种对齐余数。全部输出等于三个原RGB字节；probe库仅供此测试，不参加性能。
- 原有限合同1,584次和三级补充192次的uint64 oracle/旧specialized对照通过，四个非法输入被拒绝；长度、偏移与共享/分通道混合布局同上阶段。
- a399单级/四级分别在标量1线程、AVX2 1及4线程完整遍历256³，单级SHA仍为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`，四级仍为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。
- seed=2026102405、m=17/18/25/33的首级分通道随机节点四级也完整遍历256³，对照旧specialized，SHA仍为`045b39b5f5291c826217021c1490fafdd45cd2b60a83f2e74694d91d7331b4ab`。节点从全字节范围取样，不是证明所有16M种输出均出现。

因此相对冻结模型的mean/p99/max与逐图误差原值不变，精度保留100%。a399相对原滤镜的全域误差仍为mean0.9811105967、p993.7416573868、max8.1240384046。create的GCC静态栈记录为7,296 B，AVX2像素函数512 B；节点与轴准备后没有新增逐图片堆缓冲。

## 冻结性能协议

`experiments/rgb24-sparse-v1.json`在构建前绑定源码和既有模型/core/参考DLL的SHA。四个独立worker顺序轮换compact（本阶段RGB24）、specialized、78、80；各自单/四线程，预热一遍加五遍完整百图。每个worker以三参考端点最快中位耗时除以候选中位耗时，最差worker按100/90/80/70/60/50划档。A/A门槛与前阶段相同：80尾部对照每对[0.8,1.25]，四worker中位[1/1.1,1.1]。

Cinema始终与同场最快直表比；一般模型必须在78/80诊断中显示direct disabled。正确性全过后才计时；不允许跨场拼接或用旧specialized慢分母改写Cinema资格。

| 模型/线程 | 吞吐保留中位 | 最差worker | A/A中位 | 100 | 90 | 80 | 70 | 60 | 50 |
|---|---:|---:|---:|---|---|---|---|---|---|
| a399/1 | 3.11% | 2.61% | 0.99631 | 拒绝 | 拒绝 | 拒绝 | 拒绝 | 拒绝 | 拒绝 |
| a399/4 | 4.41% | 3.13% | 1.09106 | 拒绝 | 拒绝 | 拒绝 | 拒绝 | 拒绝 | 拒绝 |
| 一般四级/1 | 87.58% | 79.19% | 0.97337 | 拒绝 | 拒绝 | 拒绝 | 通过 | 通过 | 通过 |
| 一般四级/4 | 88.47% | 81.30% | 0.99258 | 拒绝 | 拒绝 | 通过 | 通过 | 通过 | 通过 |

每个单元格的精度保留均100%。一般模型78/80再次诊断direct disabled，不依赖窄域假设。本阶段相对specialized的单/四线程最差保留也只有80.15%/88.63%；不能拿这个较慢分母替代主判分母。a399相对specialized也只有79.12%/62.79%，其最快端点退化远低于底线。

与[上一阶段](2026-10-24-memory-compact-sparse.md)并列，一般模型100%档继续使用原参考，90%档可选268,308 B的RGB32冻结句柄；80%档若要求单/四线程都达标，仍选该句柄；70/60/50%档则有206,020 B的RGB24候选。若只要求四线程，RGB24可入80档。前后两阶段没有同场互测，不将两个阶段保留率相除冒充直接速度代价，只报告各自同场固定参考的实测值。

## 容量暂态与真实工作集

| 模型 | 序列化输入B | RGB24常驻capacity B | 已知冻结暂态B | 已知loader载荷界B |
|---|---:|---:|---:|---:|
| a399四级 | 457,468 | 450,344 | 565,639 | 566,790 |
| 一般首级分通道四级 | 212,677 | 206,020 | 321,315 | 322,466 |

暂态与loader列仍仅为可见对象/向量/文件载荷账本，排除分配器、FILE、CRT和运行库隐藏分配，不冒充RSS峰值。SLUT/坐标文件没有改变，磁盘输入大小不下降；常驻RGB24包含每级实际对齐取整和owned guardword，并非按3N逻辑位宽估算。没有新增逐图片堆缓冲。

每行RSS来自独立新进程，在分配照片前完成指定数量句柄后记录；进程工作集/峰值含Python、NumPy、DLL、分配器，不是纯核心RAM。32句柄只用于放大容量差异。

| 模型/角色 | 句柄数 | 准备后工作集B | 进程峰值B |
|---|---:|---:|---:|
| a399 RGB24 | 1 | 37,425,152 | 37,425,152 |
| a399 specialized | 1 | 38,088,704 | 38,088,704 |
| a399 ref78 | 1 | 65,040,384 | 133,459,968 |
| a399 ref80 | 1 | 66,404,352 | 133,505,024 |
| a399 RGB24 | 32 | 51,675,136 | 51,675,136 |
| a399 specialized | 32 | 71,307,264 | 71,307,264 |
| 一般 RGB24 | 1 | 37,117,952 | 37,117,952 |
| 一般 specialized | 1 | 37,212,160 | 37,212,160 |
| 一般 ref78 | 1 | 37,515,264 | 37,515,264 |
| 一般 ref80 | 1 | 37,298,176 | 37,298,176 |
| 一般 RGB24 | 32 | 43,925,504 | 43,925,504 |
| 一般 specialized | 32 | 53,456,896 | 53,456,896 |

## 精简证据与重放

`scripts/generate_rgb24_sparse.py`保留父快照并生成新源码，`freeze_rgb24_sparse.py`绑定新快照和协议；`build_rgb24_sparse.py`构建正式库与仅测试的probe库。`verify_rgb24_sparse.py`执行有限及完整域，`verify_rgb24_probe.py`测试保护页，三级补验沿用独立`check_compact_three_stage.py`。`bench_rgb24_sparse.py`完整执行四worker与12个RSS新进程。

精简包`report/data/p16-rgb24-sparse-v1`包含所测源/栈记录、新库与对象、guard/finite/three/full/build原件、性能原件和所有worker/RSS、一般模型、机器码与SHA清单。输入照片/完整RGB域不上传，78/80与四MinGW依赖具体在`report/data/p16-memory-rom-v1/measured-libraries.zip`，specialized在`report/data/channel-runtime-specialized-v1/binaries-and-core.zip`，均用本轮SHA重复绑定；文件先设置`-text`再入库，静态核对Git blob、工作树、清单与ZIP CRC。
