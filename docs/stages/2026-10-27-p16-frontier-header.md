# 第16题：独立单头运行库、连续三维目标与部署裁剪

Agent：Codex `/root`、`portable_core`、`cpp_runtime`、`selector_catalog`；Operator：本会话用户。实施与验证日期：2026-10-27～28，Asia/Shanghai。基线为PR #94的`b7d7e3e`，实现提交为`0bdb2d6`；本阶段通过新工作分支PR交付，不合并主干或关闭历史议题。

## 目标及完成范围

本阶段落实用户的四项要求：以精度A、处理时间B、运行内存C形成可选的权衡版本；部署端交付一个完整C++17头文件及一个可选C99头文件；用连续偏好与硬预算选择实际执行参数；提供桌面、移动、嵌入式和可移植目标开关。

连续的是输入目标域。三个偏好权重属于`[0,1]`并归一化；每图平均误差、批次时间及内存预算先作为硬约束。内部模型、m、后端、索引位宽、线程及块大小存在离散选择，所以实际性能曲线有台阶，不承诺可微、任意组合可达或未知图像上的精度保证。

| 要求 | 本阶段实现 | 当前证据 |
| --- | --- | --- |
| 三维权衡 | 全部候选保留，按约束重算非支配集合；支持非凸前沿、单轴目标及连续加权偏好 | 5套模型、20种执行配置；热批次/首批共40条目录记录，4个独立比较上下文 |
| 独立头文件 | `include/flash_chroma.hpp`自含整数核心、运行库及无堆选择器；可选`flash_chroma_c.h`独立提供C99核心 | 独立CMake目标仅编译新头及宿主适配，不依赖旧实验库；多翻译单元、双头两种包含顺序通过 |
| 参数真实生效 | 模型、后端、表示、线程、块大小、arena上限及部署策略均进入实际准备/执行 | 真实目录的三个请求在C++/Python选择一致；保存选择实际驱动100图输出 |
| 部署开关 | Desktop/Mobile/Embedded/Portable及SIMD、direct、OpenMP编译裁剪 | 四目标×两种包含顺序8项合同；两个端侧freestanding对象无外部符号；C99接入三类QEMU目标 |

## 主要文件与接口

- [C++17交付头](../../include/flash_chroma.hpp)、[C99交付头](../../include/flash_chroma_c.h)、[完整接入说明](../single-header-runtime.md)。部署时复制所需头文件和模型；Python拟合器、图片编解码器、JSON及项目私有`.cpp`不进入运行库依赖。
- [同源生成器](../../scripts/generate_flash_chroma_header.py)将C99核心、`src/flash_chroma_cpp.inc`和`src/flash_chroma_selection.inc`合成hpp；不手工维护两份整数算法。
- [连续选择及拟合工具](../../scripts/p16_frontier.py)提供`validate/frontier/select/plan/fit`；[实际执行入口](../../scripts/run_flash_chroma.py)核对保存的请求、目录、模型、库、输入和输出。
- [验证器](../../scripts/verify_flash_chroma.py)、[测量入口](../../scripts/bench_flash_chroma.py)、[分场次汇集](../../scripts/assemble_flash_chroma_measurements.py)、[封存工具](../../scripts/publish_flash_chroma_evidence.py)及[归档复算](../../scripts/verify_frontier_evidence.py)。

运行库接受只读的四个SLUT及各自可选sidecar，每级m独立为17..33。C99核心补齐9216B分输出Q16坐标，保留每级四面体插值和RGB8 half-up整数输出。两份接口都借用源模型字节，sidecar不会在端侧丢弃。初始化严格校验格式、binary32网格元数据、索引及Q16分数。

C++运行时提供Sparse Scalar、Sparse AVX2、DirectU8、DirectU16及DirectRGB24。三种direct都由固定稀疏链编译，精确复现其四级结果；U8/U16通过完整域确定palette资格，容量不合时明确拒绝。调用方提供arena，先查询容量，准备后图像执行不由本库申请堆内存。OpenMP自己的线程栈、运行库分配与调度开销单独说明，不把arena预算当作完整RSS硬上界。

所有翻译单元须使用一致的部署/功能宏和OpenMP设置。Embedded/Portable默认裁剪direct、x86 SIMD及OpenMP；移动目标在非x86上使用标量。AVX-512显式请求目前返回Unsupported，ARM NEON尚未实现。旧有界后缀缓存、扫描线专门准备器及部分特定写入变体保留在研究目录，没有把其历史性能归给本次头文件。

## 模型与三维实际结果

模型包共保存7套资产：原default、max_first、max41、max48，加本轮从相同四张原始密集LUT生成的compact17、compact25和mixed。**本轮新库的完整域及性能目录覆盖其中5套**；max41/max48仅保留研究资产，没有新增本轮性能资格。

三个新增模型使用`sample_interp/uniform`，分别取`[17,17,17,17]`、`[25,25,25,25]`、`[17,25,25,33]`。这是真实可执行的容量/误差端点，不称为这些m下的最优拟合。`fit`还可实际调整curvature的连续alpha/exponent；`plan`生成的5508种组合属于待测计划，未标记为已完成。

| 模型 | 四级m | 百图平均RGB色差 | 最差单图均值 | 源模型及sidecar载荷 |
| --- | --- | ---: | ---: | ---: |
| default / 373a | 33/33/33/33 | 0.695486159059 | 1.119051322056 | 457,468B |
| max_first | 33/33/33/33 | 0.679090181058 | 1.084102390342 | 457,468B |
| compact17 | 17/17/17/17 | 4.342706901999 | 6.644953263902 | 75,196B |
| compact25 | 25/25/25/25 | 3.102638014822 | 5.294771023991 | 204,124B |
| mixed | 17/25/25/33 | 2.986896725507 | 5.053764001908 | 232,924B |

精度由100张1024×768 RGB8的78,643,200个像素，对四张原始密集LUT逐级独立查表后复核。它属于已见Cinema来源，不是盲测或任意新LUT保证。ΔE为RGB码值欧氏距离，不是CIEDE2000；每张图的全像素mean严格`<T`，不能用总mean替代逐图门禁。

当前代表性时间和arena如下。时间均为固定百图映射，排除解码、哈希、分配及准备；正式5轮全部保留，用中位数描述。A/A每配置三周期ABBA/BAAB，不补轮、不剔除慢轮，全部周期比值须在`[0.90,1.10]`内。

| 配置 | arena预算/实际分配 | 热百图中位/ms | 本轮A/A |
| --- | ---: | ---: | --- |
| default / Sparse AVX2 / 4T | 593,727B | 443.8539 | 通过 |
| default / U8 direct / 1T | 17,392,447B | 175.9758 | 通过 |
| default / U8 direct / 4T | 17,392,447B | 66.0763 | 未通过，严格速度选择排除 |
| default / RGB24 direct / 4T | 50,925,439B | 52.7676 | 未通过，严格速度选择排除 |
| max_first / U16 direct / 4T | 35,471,167B | 52.2581 | 通过 |
| compact17 / Sparse Scalar / 1T | 0B | 3214.0446 | 通过，Portable策略在宿主执行 |
| compact17 / Sparse AVX2 / 4T | 91,199B | 286.3685 | 通过 |
| compact25 / Sparse AVX2 / 4T | 262,463B | 303.6005 | 通过 |
| mixed / Sparse AVX2 / 4T | 300,927B | 264.0447 | 通过，独立补测场次 |

20个配置中16个满足本轮A/A门禁，4个未满足。A/A通过不等于跨场、跨机或普遍加速证明。mixed的测量属于独立场次，目录不将其与前一场做速度支配比较。首批每配置只有一次新句柄观测，40条目录中的20条首批记录全部不授稳定时间资格。

arena包含持久表、准备临时区及最坏对齐余量。本次宿主适配器保留整个arena直至销毁，不能按可释放临时段假报更小常驻内存。另计源模型、808B Runtime对象及471,859,200B百图输入/分离输出。比如所选max_first U16配置的受控账单为507,788,643B；它不含OS/OpenMP栈、Python和分配器，完整RSS另有原始采样。compact17的标量库对象加源模型为76,004B，模型在设备上可由调用方放在可字节寻址的ROM/Flash，不能据此说模型无需存储。

当前性能目录仅覆盖桌面宿主中的Desktop/Portable策略和整百图分离缓冲。Mobile/Embedded、原地及分块有功能合同，但没有实际设备或流式处理的性能目录，不声明已测其三维前沿。

## 选择到输出的实际验证

在第一场的热批次上下文中，真实目录的C++和Python实现给出相同结果：

| 连续请求或预算 | 选择结果 |
| --- | --- |
| 精度/速度/省内存权重0.85/0.60/0.25 | default / Sparse AVX2 / 4T |
| 每图mean<1.1、受控运行内存≤512MiB、arena≤40MiB，尽量快 | max_first / U16 direct / 4T |
| Desktop目标，忽略时间、尽量省内存 | compact17 / Sparse AVX2 / 1T |

第二个请求已实际执行100图并写出100个PNG，输出与原始测量的整批/逐图SHA一致；100个PNG又逐一解码，像素SHA再次全部匹配。独立重新执行四张原始密集LUT后，平均误差0.679090181058、最差单图均值1.084102390342，全部严格低于示例阈值1.1。该阈值是本次验证参数，不是官方Threshold。

该次单次运行的模型内存准备286.6057ms、百图apply46.3273ms、准备至首批332.9932ms、读图至PNG输出及文件SHA完成15,934.0579ms。它不是新的稳定速度排名。模型/库读取发生在这些应用计时之前；独立参考精度校验在计时之后。

独立审计发现原回执把application笼统写为“不含输出哈希”，但`write_frames`实际在写PNG后立即计算文件SHA。已修正入口文案，原数值和原回执保持，另存[计时纠正](../../report/data/p16-frontier-header-20261027/timing-correction.json)：**application含100个PNG文件SHA，不含之后的逐图/整批像素SHA**。实际执行脚本原字节已随ZIP归档，没有因说明错误重新测速或改数值。

## 验证环境与覆盖

本机为Windows11 10.0.26200、AMD Ryzen9 8945HX；MinGW GCC15.2、C++17/C99 Release；Python3.12.14、NumPy1.26.4、Pillow10.4.0。CPU-only；测量启动命令设置OMP=4/PASSIVE、BLAS/MKL=1，进程亲和0/2/4/6，未锁频、未逐OMP线程绑核。实际编译命令、库SHA、头文件SHA及进程环境分别保存，启动命令设置不冒充独立的进程环境变量采样。

| 测试目的 | 本轮结果与范围 |
| --- | --- |
| 固定模型运行时正确性 | 5模型×4种表示共20条C++完整RGB8流通过；每条16,777,216色，另5条独立C99全域；共400项有限长度/原地分离比较 |
| 独立整数参考 | C99/C++各785组合同，混合m、非均匀轴、三种sidecar配置及各65537像素独立u64参考 |
| 原生接口/裁剪/ODR | 新CMake的12项CTest通过；Release下选择器断言显式启用，四目标两包含顺序共8项；两个freestanding对象nm无未定义符号 |
| 连续选择、宿主入口及旧评分入口 | 38项Python合同通过，含空模型清单不能形成真空通过的拒绝检查 |
| 实际目录双语言一致性 | 三个真实请求的C++/Python结果一致，编译源码及输出记录归档 |
| 最终部署运行 | 同目录选择→真实100图→100PNG→独立原LUT精度→PNG解码SHA通过 |
| 资料完整性 | 20配置的中位、A/A、资源、平台/场次、模型及源码SHA可由归档复算；不把静态复算称为数值重跑 |
| 嵌入式接入 | 新C99核心已接入原Cortex-M3/FreeRTOS、RV32/FreeRTOS、Cortex-A53/Linux QEMU工作流，旧embedded/portable回归保留；远端执行结果以本PR实际检查为准 |

本机没有QEMU交叉工具链，不能把宿主裁剪测试称为本机实板验证。Win64 freestanding对象体积只描述该编译产物，不是MCU代码体积或全应用栈上界。旧GUI、所有历史拟合与所有可选后端没有在本轮全部重跑。

## 原始记录、失败保留及复现

第一份v1测量因发现选择器缺少编译TARGET/DIRECT资格过滤而停止，已完成的7配置原值保留。修正选择器及合同后重新构建最终库。v2在会话中断时停止，保存17个完整配置；确认进程实际不再运行后，只在新场次补测mixed的3配置。汇集器核对预声明20配置恰好覆盖、相同库/源/输入、每配置5轮及3周期A/A，再形成最终目录；原始v2的`completed:false`保持在ZIP中，没有改写成完整单场。两个场次和两种计时范围形成四个context。

执行开始时旧HEAD为`b7d7e3e`，实现曾在工作区，因此不单靠HEAD宣称源码身份。ZIP保存实际执行源码；六份数值相关源文件已与实现提交`0bdb2d6`的Git字节核对一致。最初新增模型总清单的相对路径组装错误导致加载失败，保留旧清单并另生成resolved清单后完成验证。C盘临时空间不足的编译失败保留，改用任务F盘TMP后成功；没有删除用户文件。

主要证据：[目录](../../report/data/p16-frontier-header-20261027/catalog.json)、[20配置原值](../../report/data/p16-frontier-header-20261027/results.json)、[完整域](../../report/data/p16-frontier-header-20261027/quality.json)、[端到端结果](../../report/data/p16-frontier-header-20261027/selected-run.json)、[PNG往返](../../report/data/p16-frontier-header-20261027/png-roundtrip.json)、[实际执行源码ZIP](../../report/data/p16-frontier-header-20261027/raw-evidence.zip)、[成员摘要](../../report/data/p16-frontier-header-20261027/manifest.json)。

```bash
pixi run --locked build-header
pixi run --locked test-header
pixi run --locked python scripts/generate_flash_chroma_header.py --check
pixi run --locked python scripts/verify_frontier_evidence.py --evidence report/data/p16-frontier-header-20261027
pixi run --locked frontier select --catalog report/data/p16-frontier-header-20261027/catalog.json --context f10b980d400918936f38494800c5b49ec33f5198b36430bc474b4bb8ebe2fbdd --weights 0.85 0.60 0.25
```

Windows使用MinGW Makefiles及明确的GCC/G++路径；新库名为`libflash_chroma_bridge.dll`，Linux为`.so`。已有测量目录绑定当时的Windows库SHA，重新构建或迁机后必须以自己的库重新验证和测量，不能直接继承旧时间。图片和四张密集参考表仍需按真实SHA备齐，仓库不自动下载。

实际像素验证可执行：

```bash
python scripts/verify_flash_chroma.py --library build-single-header/libflash_chroma_bridge.so --manifest data/p16-frontier/models/manifest.json --profiles default max_first compact17 compact25 mixed --all-representations --output artifacts/my-header-quality.json
python scripts/bench_flash_chroma.py --library build-single-header/libflash_chroma_bridge.so --manifest data/p16-frontier/models/manifest.json --profiles default max_first compact17 compact25 mixed --quality-receipt artifacts/my-header-quality.json --reference-luts lut1.lut256 lut2.lut256 lut3.lut256 lut4.lut256 --output artifacts/my-frontier-measure
```

`fit`可生成新LUT模型，`plan`可扩充待测组合；本次发布不把尚未执行的5508组合算作完成。误差/时间/容量无解时明确返回NoFeasible，不放宽门槛。

## 协作检查与剩余边界

操作前获取origin/github，目标PR94仍为`b7d7e3e`；检查87条issue/PR索引及空第二页。完整刷新#94/#92/#89/#90/#91/#93、#6/#5/#9/#12/#37正文、conversation、review、行内评论及GraphQL审查线程，检查issues #7/#8全文和完整评论。#92行内接口初次失败后重读为空，失败原样保留。记录见[协作快照](../../report/data/p16-frontier-header-20261027/coordination.json)和[审查线程](../../report/data/p16-frontier-header-20261027/coordination-threads.json)。

历史#9基线/环境、#7实际内核绑定及相等mean/CVaR修复的`337a3dd`、`876e15b8`、`397cc367`均实际为当前祖先；本轮实际后端还由Runtime返回并核对，不只看请求名称。#5许可意见落实为模型包保留原MIT许可字节。#8的新核心分层、资源、跨实现及QEMU接入有本轮证据，历史接口迁移、实板资源与功耗验收继续跟踪，不关闭议题。

Discussion4端点仍被当前连接器拒绝，读取缺口不当作无意见；保持Draft，不执行合并或关闭。官方Threshold/计分、Xeon Gold6140、真实移动/嵌入式设备性能及NEON仍未验。当前交付证明连续选择、独立双头及部署裁剪工程已经落地，不证明最高赛事分数或全局最优。
