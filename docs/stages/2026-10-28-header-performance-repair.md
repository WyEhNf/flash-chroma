# 单头运行库性能修复与集中验证

Agent：Codex `/root`、`cpp_runtime`、`portable_core`、`selector_catalog`；Operator：本会话用户。日期：2026-10-28，Asia/Shanghai。修复基线为 PR #95 的 `aad1871`，实现提交 `271e10f`，继续在 `codex/p16-frontier-header-20261027` 交付；保持 Draft。

## 问题、修复与交付边界

前一轮同场分析发现，单头库的 U8/U16 direct 热循环使用两次依赖 gather 和移位，相比旧库专用查表退化；输出采用小块普通写入；准备阶段对完整 RGB8 域串行计算四级模型。生成一个头文件本身不要求这些退化。

本轮落实三项修复：

- [`flash_chroma_direct.inc`](../../src/flash_chroma_direct.inc)：迁入标量 ILP 查表、AVX2 RGB 打包、64 像素成块 NT 写入和预取。普通 AVX2 与 x86_64 BMI 版本由 CPU 能力分派；短尾精确读取，NT 写入在普通尾部和返回前 fence。i386 保留普通 AVX2，64 位 ANDN 明确裁剪。
- [`flash_chroma_prepare.inc`](../../src/flash_chroma_prepare.inc)：逐 cell 证明首层可达的小域，包含分输出 sidecar 的 Q16 坐标扰动；在最多 2MiB 缓存内精确编译后三层，再并行扫描首层。不能证明、域过大或缓存调色板超容量时回到通用四级构建。缓存超集不会冒充完整 RGB8 的实际 palette 资格。
- [`bridge.cpp`](../../single_header/bridge.cpp)：宿主 arena 不再先重复清零；增加独立诊断符号，保持原 Info 结构 ABI，便于旧、新 DLL 同场加载。运行库仍由调用者提供工作区。

维护片段由生成器展开进一个完整的 [`flash_chroma.hpp`](../../include/flash_chroma.hpp)。部署不需要这些 `.inc`、Python 或私有 `.cpp`。可选 C99 头字节未变。`FLASH_CHROMA_ENABLE_PREPARE_CACHE=0` 可裁剪准备缓存，Embedded/Portable 默认不包含该路径；接口详见[接入说明](../single-header-runtime.md)。

缓存、ID、哈希、worker RGB 块和实际可达 ID 位图均计入 arena；`palette_entries()`仍报告完整 RGB8 实际颜色数，内部调色板可以保留未用槽。两个新诊断分别报告是否真正使用缓存及缓存槽数。证明的固定局部数组 1920B 和角点 96B 属于栈，另列于 arena 外。固定准备计划的预算不足时返回 Budget；需要更小准备内存可编译关闭缓存。

default/max_first 均实际使用 219719 槽缓存；palette 实际分别为 224/336。4 线程 U8 arena 为 19187391B，U16 为 37298623B；比修复前分别增加约 1.71/1.74MiB 临时容量，持久表格式不变。40MiB U16 示例仍可用。宿主保留整块 arena，不能假定临时段已经归还 OS。

## 集中正确性与部署检查

实际环境：Windows 11 10.0.26200 / AMD Ryzen 9 8945HX / AMD64；MinGW GCC/G++ 15.2.0，C99/C++17 Release `-O3 -DNDEBUG`，函数级 AVX2/BMI，OpenMP 4.5；Python 3.12.14、NumPy 1.26.4、Pillow 10.4.0。TMP/TEMP 位于 F 盘。

修复后统一构建，再执行以下检查；性能负载在编译和正确性检查结束后运行。

| 检查 | 实际范围与结果 |
| --- | --- |
| AVX2/OpenMP 构建 | 15 项 CTest 全通过；包括新 direct、prepare、关闭缓存变体及原有双头、多翻译单元、四部署目标 |
| Scalar、无 OpenMP 构建 | 15 项 CTest 全通过；准备快路径的无 AVX2 跳过状态明确记录 |
| Python | 原相关 38 项加新增基准防漏写 3 项，共 41 项通过 |
| 完整 RGB8 | 五套固定模型 × 四种 C++ 配置，共 20 条全域流，与各模型独立 oracle SHA 一致；另五条独立 C99 全域流一致 |
| 有限边界 | 400 项随机短长、原地/分离比较通过；direct 合同另有 347496 项比较，覆盖全部 64 种地址余数、stride/padding、保护页首尾、普通 AVX2/BMI 强制路径和 1/4 线程 |

完整域验证遍历每套模型全部 16777216 个输入颜色。四级 Q16 四面体和每级 RGB8 half-up 结果未改变。实际模型仍为 `data/p16-frontier/models/manifest.json` 中的 default、max_first、compact17、compact25、mixed；没有重新拟合或按图片更换模型。

## 三方同场性能结果

[`bench_flash_chroma_regression.py`](../../scripts/bench_flash_chroma_regression.py)固定比较旧评分库、修复前单头库、修复后单头库。每种模型和 1/4 线程均执行三侧 A/A、old↔fixed、before↔fixed；每组四周期 ABBA/BAAB，共 320 次正式热映射、320 次正式首批和 40 次热身。每次计时外覆盖输出，首次独立 SHA 验证后用正确输出的逐字节取反作为后续毒化值，避免上一轮输出掩盖漏写。实际模块路径、独立句柄、DLL SHA 和链接来源回执均核对，所有输出 SHA 一致。

输入为固定 100 张 1024×768 RGB8，预载、相同分离输出；CPU 亲和为 0/2/4/6，OMP_WAIT_POLICY=PASSIVE、OMP_NUM_THREADS=4、BLAS/MKL=1，不锁频。热映射排除解码、分配、准备和 SHA。下表为 before↔fixed **各自同一配对组**的样本中位；比值为四个周期 mean(B)/mean(A) 的中位。

| 模型/线程 | 修复前热批次/ms | 修复后热批次/ms | 配对耗时比 fixed/before |
| --- | ---: | ---: | ---: |
| default 1T | 133.30605 | 53.45045 | 0.40061 |
| default 4T | 35.36495 | 16.34295 | 0.46296 |
| max_first 1T | 146.95250 | 59.19550 | 0.41151 |
| max_first 4T | 39.14245 | 18.75550 | 0.47912 |

**热映射相关 A/A 控制没有同时通过，以上只作本场描述性观察，不授稳定加速或旧版无退化资格。** 24 组 A/A 中仅 8 组通过预先固定的全部周期 `[0.90,1.10]` 门槛；未补轮、未删慢轮。

old↔fixed 热批次比值分别为 default 1T 1.03918、4T 0.96393，max_first 1T 1.12462、4T 1.04758；对应控制均未同时通过。1T 尤其仍有描述性的残余差距，当前不能声称完全追平旧评分库。

4T 准备到首批输出的 fixed/before 比值为 default 0.12269、max_first 0.13060，两组比较各自的 before/fixed A/A 均通过。fixed/old 为 0.99111、0.73196，但旧侧 A/A 未通过。这一范围包含新句柄创建、arena 分配、准备和首批映射，旧 API 还含模型文件读取，新 API 模型已读；另保存 native_prepare_ms，不把范围差异称为纯准备算法公平比值。旧准备固定 4T，新准备按请求线程；1T 首批不能作为相同准备线程的对照。

实际 DLL 身份：旧库 `afdb1a89…cf32e524`，修复前 `d01ae65c…87f0d8f8`，修复后 `39a1d80e…2c44b17`。修复后交付头 SHA256 为 `f09079b092233d5376100dec7895fef80eb34f1c50b5bc0324f9a42e76346fa8`，与实际链接回执完全一致。构建基于 aad1871 工作树加本阶段补丁；源码与工具快照随证据保存。

## 复现入口与证据

先生成头，在独立构建目录编译，再运行：

```powershell
python scripts/generate_flash_chroma_header.py --check
cmake -S single_header -B artifacts/single-header-perf-build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe -DCMAKE_MAKE_PROGRAM=E:/mingw64/bin/mingw32-make.exe -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build artifacts/single-header-perf-build --parallel 2
ctest --test-dir artifacts/single-header-perf-build --output-on-failure --no-tests=error
python -m pytest tests/test_p16_frontier.py tests/test_flash_chroma_support.py tests/test_run_flash_chroma.py tests/test_p16_submission.py tests/test_flash_chroma_regression.py -q
python scripts/verify_flash_chroma.py --library artifacts/single-header-perf-build/libflash_chroma_bridge.dll --manifest data/p16-frontier/models/manifest.json --profiles default max_first compact17 compact25 mixed --all-representations --output artifacts/header-perf-quality-20261028.json
python scripts/bench_flash_chroma_regression.py --output artifacts/header-perf-regression-20261028
python scripts/bench_flash_chroma.py --library artifacts/single-header-perf-build/libflash_chroma_bridge.dll --manifest data/p16-frontier/models/manifest.json --profiles default max_first compact17 compact25 mixed --quality-receipt artifacts/header-perf-quality-20261028.json --output artifacts/header-perf-measure-20261028
```

上述 Python 使用既有 `error-study-py312` 环境。无 SIMD/线程变体在另一构建目录配置 `FLASH_CHROMA_TEST_AVX2=OFF`、`FLASH_CHROMA_TEST_OPENMP=OFF`。原来的 `single-header-build` DLL 原样保存用于修复前对照，不在该目录重新构建。

更新后的连续选择目录、逐配置记录、完整域回执、三方原始周期与源快照保存于 [`report/data/p16-header-performance-20261028`](../../report/data/p16-header-performance-20261028)。旧阶段目录与诊断原始失败值保留。模型包复用已有内容寻址对象，目录绑定新 DLL 和本轮环境，不继承旧时间资格。

本轮目录包含 20 配置、40 指标点和 2 个计时上下文，19 配置的三周期 A/A 通过；default U8 1T 未通过，首批点均不授稳定时间资格。此目录是另一项预声明测量，不能拿它的 A/A 覆盖三方对照的失败。

三种实际请求的 C++/Python 选择一致：`mean<1.1 / runtime≤512MiB / arena≤40MiB` 的 Fastest 选择 max_first U16 AVX2 4T；连续权重 `{0.85,0.60,0.25}` 选择 default U8 AVX2 4T；忽略时间的 Compact 选择 compact17 Sparse AVX2 1T。Fastest 目录中位为 17.8337ms，属于本轮独立目录，不与三方配对绝对时间混算。

保存的 Fastest 请求实际执行 100 图，整批输出 SHA 为 `5564f7e184cbf00614a2f5f76c1e0e58550592af51e85a0ad2896c27bd3f7929`，逐图 SHA 与新目录原始证据一致，模型、源像素及库未改变。这次应用不写 PNG，精度按同输入/模型/库/输出 SHA 绑定继承刚完成的百图密集参考结果；没有另做新一轮拟合精度或速度排名。单次 apply 38.7771ms、prepare 25.494ms、准备到首批 64.3887ms 仅保留为执行记录。

本轮只验证本机 x86_64。没有实际嵌入式/移动设备功耗、最坏时延、ARM NEON、32 位执行性能或 Xeon Gold 6140 成绩；AVX-512 仍 Unsupported。官方 Threshold、未知 LUT 泛化和稳定追平旧库尚未验收。

## 协作记录与操作依据

检查全仓 88 条 issue/PR 索引及空第二页，完整刷新本 PR #95、基础 #94、准备 #89 的正文、会话、review/行内记录和审查线程，以及 issues #7/#8 全文和完整评论。另完整读取域证明 [#43](https://github.com/WyEhNf/flash-chroma/pull/43)、流写 [#48](https://github.com/WyEhNf/flash-chroma/pull/48)、ILP [#62](https://github.com/WyEhNf/flash-chroma/pull/62)、ANDN [#71](https://github.com/WyEhNf/flash-chroma/pull/71)、pair48 [#73](https://github.com/WyEhNf/flash-chroma/pull/73) 和原地写出 [#75](https://github.com/WyEhNf/flash-chroma/pull/75) 的正文及完整会话；这些研究的性能失败和未测范围继续保留。本轮的新头、新模型绑定和数值/性能结果独立验证，不继承它们的通过结论。

其余关联历史核对沿用前阶段已保存的完整正文/评论快照。#7 后端身份修复及历史均值保护不被本轮替换；#8 的实板、资源和接口待办仍开放。本 PR 的评论/review/行内线程为空；连接器传输失败及重试成功分别保留在证据。Discussion4 当前接口读取缺口保留，不把不可读当作无意见。本轮只更新 Draft PR，不合并、不关闭 issue。
