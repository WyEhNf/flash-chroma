# 第16题 R17：优化、阶段验收与交付结果

日期：2026-10-15。起点：`7059bc745c038229a1f1e87e0ac4ea1e271597e9`，本地 `codex/zig-default-pixi`。本轮修改未提交、未推送，源码与产物以最终 manifest 为准。

本轮完成算法、CPU 后端、验证和工程架构四方面的改动。实际收益包括：四级 AVX2 在本机 100 图配对测量中比同构建标量实现快约 2.63–2.96 倍；一个裁剪场景的全色域平均色差降低 1.74%；独立四级 m18 在 ISP 场景比 m17 降低平均色差 11.44%。全部数值只适用于本轮明确记录的输入和机器。

## 题面与已有成果核对

已阅读用户提供的题面截图、`source.htm` 对应的 [PROBLEM.md](../PROBLEM.md)、[AUDIT.md](../AUDIT.md)、[R16 五方向结果](../experiments/r16-five-directions.md)、历史评测及工具链文档，以及工作区此前的开发建议。保留上游报告及原始结果，没有把历史 i7-13700H/WSL 时间移作本机成绩。

| 题面要求 | 本轮实现与判定 |
|---|---|
| 输入 1024×768、RGB、每通道 8-bit；4 个 256³ 整数 LUT | 保守模式检查图像规格和四阶段。当前适配格式为 uint8 RGB 原始 LUT，正式 LUT 容器、整数位宽仍需按官方包适配。 |
| 稀疏空间 m³，17≤m≤33 | 拟合 CLI、缓存、选择器及 `--competition` 入口检查范围；m18 已纳入实测，不只比较历史17/25/33。 |
| 每级稀疏映射，输入输出为整数 | 四张表独立拟合；每一级执行 Q16 加半后右移并得到 uint8，下一阶段使用该整数输出。 |
| 允许等价计算减少次数 | 融合只消除中间 RGB 存取，四级映射及舍入全部保留。单级复合、跨级残差只作为显式研究候选。 |
| RGB 欧氏距离 ΔE 严格小于阈值 | 未改成 Lab/CIEDE2000；图片与全色统计/约束分开，使用未舍入值和严格 `<`。 |
| 正确性40、速度40、架构创新20 | 不编造综合评分；输出精度、速度和模型内存 Pareto 集。 |
| 100张图平均耗时，题面举例 i7-14700、1.5秒/张 | 本轮测试100张同规格合成图；没有把举例机器视为已确认的正式服务器，也没有将低于1.5秒视为速度满分。 |

仍未知：官方 Threshold、阈值施于逐像素/均值/p99/max 的口径、正式 LUT 文件格式、稀疏化和 I/O 是否计时、等价复合的具体许可范围。

## 算法改动与真实精度

1. 旧 `int_refine` 的八色节点之间没有共享四面体支持。利用这一结构，每色的 `H@x` 从3次减到1次，保留原整数节点决策。24个阶段与冻结的旧实现逐节点完全一致。本批局部观察约2.1–3.0倍加快，未做该子步骤的独立配对计时，不将其解释为整个拟合过程的加速倍数。
2. 新增可选 `ls_tetra_q16`：用实际 Q16 舍入后的 RGB 欧氏误差接受节点 ±1；通道依次更新，同色节点批量更新。每轮检查训练及独立守护样本的 mean/RMS/p99/max，退化时回滚整轮。守护样本参与接受决策，不称盲测。
3. CG 记录状态、迭代数和实际残差，非有限或未收敛时明确失败，不发布部分新模型。保留历史合格批次。

一次冻结算法比较覆盖 `isp-0/clip-7/warp-7 × m17/m18`，共24个独立阶段。训练262,144点、守护65,536点；最终另取262,144点，明确排除训练及守护颜色，再检查216个边界颜色。23个阶段保留原解，仅 `clip-7/m17` 的第二阶段接受一轮。拒绝的候选和原因保存在 [study.json](../artifacts/r17-algorithm/study.json)，未通过删守护规则扩大收益。

随后对四组冻结模型运行**实际原生内核的全部16,777,216种 RGB 输入**，另检查5张1024×768合成图：

| 场景／模型 | 全色 mean ΔE | 全色 p99 | 全色 max | 最差单图 mean | 示例门禁 |
|---|---:|---:|---:|---:|---|
| clip-7，旧m17 | 1.831042 | 7.000000 | 29.000000 | 2.592316 | 失败 |
| clip-7，Q16精化m17 | 1.799205 | 6.557439 | 29.000000 | 2.548877 | 失败 |
| isp-0，旧m17 | 1.460329 | 4.123106 | 15.264338 | 1.703129 | 通过 |
| isp-0，旧m18 | 1.293268 | 4.000000 | 14.177447 | 1.460643 | 通过 |

示例门禁为“每张图 mean<2.0 且全色 mean<2.0”，不是官方标准，也不保证逐像素 ΔE<2。裁剪场景的 mean 降低1.7387%、p99降低6.3223%，max不变，但仍未达到该图片均值门禁。m18 的优势只在本批场景得到支持，不设为所有 LUT 的唯一默认尺寸。完整证据：[accuracy.json](../artifacts/r17-acceptance/accuracy.json)；推导：[r17-algorithm.md](r17-algorithm.md)。

## 硬件确认与CPU实现

实际机器为 Windows 11、AMD Ryzen 9 8945HX，16核32线程；MinGW GCC15.2、CMake4.2。CPUID确认 AVX/AVX2，OSXSAVE 为真，XCR0=231，XMM/YMM保存位齐备。硬件探针和 [构建证据](../../../outputs/project16-runtime-2026-10-15/hardware-build.json) 已保存。

只有 `lut_simd_avx2.cpp` 使用 `-mavx2`；分派器、标量和主程序保持 C++17 基础 ISA，无全局 `-march=native`。`auto` 按已编入且可执行的后端选择；手工指定不可用后端明确报错。原先没有汇编实现的 `tetra_asm` 不再伪装成另一后端。

AVX2每次处理8像素，四级 RGB 留在寄存器中，每级独立舍入。每轴将单元索引与17位fraction合并，轴表gather从6次减至3次，65536端点完整保留。RGB装载/写回恰好覆盖24字节，尾部走标量。标量也按像素连续完成四级，避免双块临时缓冲。

删除冗余RGBA节点表示；SIMD packed节点按需、线程安全构建，编辑后 `prepare()` 使旧缓存失效。预热后的四级m18分项如下：

| 内存口径 | 字节 |
|---|---:|
| 四表RGB节点载荷 | 69,984 |
| 四个SLUT文件 | 86,272 |
| 标量运行时模型对象及数组估计 | 99,040 |
| AVX2运行时模型对象及数组估计 | 204,736 |
| 100张预加载RGB图像本体 | 235,929,600 |

标量/AVX2融合路径的**像素块缓冲**为0；这不表示线程栈帧或寄存器溢出占用为0。模型估计不包括分配器和进程其他内存。本机 Python 未安装 psutil，本批峰值进程内存和同期宿主CPU占用字段为 null，没有用数组估计冒充峰值RSS。

## 集中性能测量

固定 `isp-0`、四级独立m18、同一可执行文件和100张合成RGB8图。1线程和4线程各5组，按 AB/BA 交替，每次执行一个完整100图轮次；保留冷首图、全部原始时间、命令及输入/模型/二进制哈希。没有同时运行本任务的其他重计算。

| 线程 | 标量中位 ms/100图 | AVX2中位 ms/100图 | AVX2 ms/图 | 配对加速比中位 |
|---:|---:|---:|---:|---:|
| 1 | 2392.333 | 810.059 | 8.10059 | 2.9563× |
| 4 | 676.879 | 257.184 | 2.57184 | 2.6346× |

10个配对全部更快。此处是与**同构建标量实现**比较，没有声称超过上游 Zig 的历史成绩。4线程整组中位内部计时中，复制约11.604ms，映射约245.703ms；二者中位数不要求与整组中位数严格可加。冷首图含首次SIMD表准备，中位3.547ms。主程序内部端到端中位369.485ms，包含模型加载、图像解码及冷轮；外部进程墙时中位440.424ms还含启动/采样开销。二者均未执行输出编码，也没有包含稀疏化。

公共拟合入口另一次真实集成记录的四表拟合耗时为0.940秒，不含完整LUT读取、哈希和日志成本。若官方计入预处理，不能直接使用上表2.572ms/张作为总成本。[benchmark.json](../artifacts/r17-acceptance/benchmark.json) 保留所有配对原始值；集成计时不混入这张性能表。

## 正确性与工程落地

阶段验收通过：

- CTest完整批次：m17/18/25/33和非均匀m26，各自全色域；标量、AVX2、C++ SIMD与独立64位重心权重oracle逐字节一致。四张不同LUT、混合m、1/4线程链结果一致；覆盖未对齐尾部、4096块边界、序列化和缓存失效。原生拟合器保留了既有恒等控制，它不证明所有原生拟合场景。
- 关闭AVX2、C++ SIMD、Zig、Rust和OpenMP的纯C++17构建成功；65,536颜色及同类链/边界交付检查通过。
- Python阶段检查9/9通过，覆盖序列化跨后端、缓存来源与损坏/并发、CG失败、Q16回滚、真实内核验证范围及Windows正常/异常映射清理。
- 真实完整LUT经过公共拟合入口生成缓存，重复请求命中同一完整批次；四个新生成模型与性能批次模型逐字节一致。选择器核验原四级真值、模型manifest和实际内核，正确产出独立主线推荐与Pareto结果。

最终集成发现旧日志模块在Windows按GBK解码UTF-8 Git diff会出现后台解码异常；数字和模型校验成功，但该次日志没有可靠diff。已修复为显式UTF-8，单独验证中文stdout、Git diff及JSON成功，未因此重复拟合或性能测量。原始异常保留在 [integration.log](../artifacts/r17-acceptance/integration.log)，修复证据为 [logging-repair.json](../artifacts/r17-acceptance/logging-repair.json)。

缓存身份绑定四张完整LUT的SHA、参数、拟合代码和依赖版本；整批临时写入、复读、原子发布，损坏/缺失不命中，并发不混阶段。验证结果区分 `image_set_pass`、`cube_constraint_pass` 和 `submission_contract_pass`；语义来自已核验manifest时明确记录，裸模型只记声明。仅全色域max阈值才可给固定LUT链的任意输入像素上界。

构建、部署依赖与命令见 [r17-delivery.md](r17-delivery.md)。已验证的是本机MinGW环境；其他编译器、ARM机器、Zig/Rust工具链和Docker未在本轮重新验收。保守拟合主线是带收敛检查的Python实现，旧 `fit-r14` 复合拟合器保留研究用途，未宣称其全部数值边界已解决。

## 复现与证据入口

先按交付文档构建并设置 `PYTHONPATH=python`、`JSHC_BIN`。以下脚本按阶段使用，无需在每次编辑后全跑：

```powershell
python scripts/q16_refinement_study.py --output artifacts/r17-algorithm
python scripts/phase_acceptance.py prepare
ctest --test-dir build --output-on-failure
python -m pytest -q tests
python scripts/phase_acceptance.py accuracy --executable build/jshc.exe
python scripts/phase_acceptance.py bench artifacts/r17-algorithm/isp-0/baseline_m18/stage1.slut artifacts/r17-algorithm/isp-0/baseline_m18/stage2.slut artifacts/r17-algorithm/isp-0/baseline_m18/stage3.slut artifacts/r17-algorithm/isp-0/baseline_m18/stage4.slut --executable build/jshc.exe --threads 1 4 --pairs 5
python scripts/r17_integration_check.py
```

本轮生成资产约1.2GiB量级，包括完整模拟LUT、两套模型、225MiB性能图和集成来源副本；它们在被Git忽略的 `artifacts/` 中，交接时需另行保留。精确文件规模、源码与产物SHA、测试日志和二进制绑定见 [delivery-manifest.json](../artifacts/r17-acceptance/delivery-manifest.json)。没有启动官方数据下载或长期定时任务。

后续应优先接入正式格式、阈值和计时边界；在目标机器重测少量已合格候选，并保留裁剪/非连续场景的不可行结果。当前证据不支持“所有LUT均达标”或“已获得官方分数”的结论。
