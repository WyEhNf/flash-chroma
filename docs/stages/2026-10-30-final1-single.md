# final1 单文件交付、原函数审计与分段耗时

按用户要求，正式目录现在只需 `main.cpp`，不再附自定义 hpp。生成器在原 include 位置原样展开原头文件，没有改变算法和已有函数内容。当前文件 236,493 字节，SHA256 `50984adc7e75be79bed8fab84de3917e61f60613c2f2caa0a71f51bdfcaaa548`。

```sh
g++ -O2 -std=c++17 -o lut3d main.cpp
./lut3d data 4
```

## 单文件等价性

Windows GCC 15.2 和服务器 Linux GCC 13.3 均编译通过，两个环境各自的新旧 `g++ -E -P` 结果逐字节相同。更强的服务器检查：新单文件编译出的完整 ELF 与上一版已测可执行文件逐字节相同，SHA256 均为 `87e1edd90c12b02b3b291ebf11262e703e7b8c351ba47bd343878dee181dd547`。

因此之前完整 RGB8 验证和五轮映射结果仍对应相同服务器可执行文件。本次另跑正式四图，第二 Delta 为 1.467711、1.562505、1.592951、1.303775；百图分段诊断的每图 mean 与历史结果最大偏差 4.96e-12（求和方式差异）。输入和源码执行前后哈希不变。它不是新的精度优化，不能把本场波动说成提速。

## 本次分段测量

环境：i9-14900K / Ubuntu 24.04、Linux 7.0.0-38 / GCC 13.3，`-O2 -std=c++17`，自动实际 AVX2，单线程。继续持物理 P 核 6 的 `~/locks/6.lock`，绑定逻辑 CPU 12。一次完整 100 张 1024×768 照片诊断，不是五轮重测；所有数据、命令和锁分配见[validation.json](../../report/data/final1-single-20261030/validation.json)。

为保持正式 main 的原计时区和原函数不变，新增独立 [stage_timing.cpp](../../experiments/final1/stage_timing.cpp) 调用相同函数，分段使用原 `now_sec()`。高精度总区间对应原四个 print_time_now 标记，包含其间原始操作与少量诊断记账。原 print_time_now 仅输出秒级日历时间，不能据它估算毫秒用时。

| 四个标记之间的阶段 | 本场耗时 |
| --- | ---: |
| Start → getLut：原框架读取四张 3DL | 7.432837 s |
| getLut → SpareLut：参考表、采样、拟合、搜索、Direct、释放 raw | 21.939548 s |
| SpareLut → End：读 100 图、映射、原参考、两次色差 | 1.405859 s |
| Start → End | **30.778244 s** |

预处理拆分：

| 操作 | 总耗时 | 所属实现 |
| --- | ---: | --- |
| 256³ 参考表准备 | 0.337642 s | 原 `lut_sparse_ref` |
| 四级 33³ 初采样 | 0.001056 s | `lut_sparse` 新增的实现 |
| chain_ls 末级拟合 | 8.838951 s | 新增准备逻辑 |
| prefix_nodes 前中层整数节点搜索 | 12.484399 s | 新增准备逻辑 |
| DirectRGB24 构建 | 0.265409 s | 新增准备逻辑 |
| prepare 内其他开销 | 0.000985 s | 节点准备、校验、复制等 |
| 释放原始 16bit LUT | 0.011095 s | 原 main 操作 |

`prepare` 合计 **21.589745 s**，为拟合、搜索、Direct 和其内部其他开销之和；这些工作在 TimeCost 外，但用于加速或改善后续映射。四张 LUT 的读取成本另外是 7.432837 s。剩余约 0.000011 s 为阶段边界及诊断计时开销。

| 图片阶段 | 百图总计 | 平均每图 | 计入 TimeCost |
| --- | ---: | ---: | --- |
| 检查/读取图片 | 0.027427 s | 0.274272 ms | 否 |
| 分配输出、out=img、优化映射 | 0.100000 s | **1.000004 ms** | 是 |
| 原四级 256³ 参考映射 | 1.055162 s | 10.551615 ms | 否 |
| 第一次色差：输入 vs 参考 | 0.120722 s | 1.207225 ms | 否 |
| 第二次色差：参考 vs 优化输出 | 0.102169 s | 1.021686 ms | 否 |
| 整个图片循环（含打印、析构与记账） | 1.405859 s | 14.058589 ms | 仅其中映射部分 |

本场全部 30.778244 s 按 100 图均摊为 **307.782442 ms/图**，包含准备、读图、原参考和色差，范围不同于 TimeCost。原五轮百图 TimeCost 均值中位数 **0.975453 ms/图**继续作为原正式性能记录；本场 1.000004 ms 是增加分段观测后的单轮诊断值，不将二者混算。未单独分离 out=img 与查表，因为正式 TimeCost 本来就包含两者。

## 相对最初 C++ 模板修改的函数

基线是用户最初 `C++/main.cpp`（SHA256 `d6d9b1817d03c7165931f33d1126500b4ff5e9535ebecfdd4b0cbdbcfb9d0ea5`），保存为 [original_main.cpp](../../experiments/final1/original_main.cpp)。将换行统一为 LF 后逐函数对比，13 个原有自由函数中 3 个改变、10 个原文相同。审计 SHA、函数行号和逐函数 diff 见 [function-audit.json](../../report/data/final1-single-20261030/function-audit.json)。

| 原有函数 | 内容变更 |
| --- | --- |
| `lut_sparse` | 在原 `add your code here` 处调用 `fc_delivery::sample`，生成稀疏节点；失败返回 false。原函数此前为空实现。 |
| `apply_3d_lut` | 保留原 `out = img`，之后调用 `fc_delivery_pipeline.apply`；失败返回 false。原函数此前仅复制输入。 |
| `main` | 默认目录 ../data→data；增加可选图片数量并限制 1..100；稀疏尺寸 17→33；采样后、释放 raw 前调用 `prepare`；图片循环由固定四图改为参数控制（默认仍四图）。 |

原文不变的 10 个函数：`clamp_i`、`now_sec`、`image_load_bin`、`lut_read_3dl`、`lut_sparse_ref`、`apply_lut256`、`apply_3d_lut_ref`、`color_dalta_calc`、`file_exists`、`print_time_now`。Image/Lut3D 定义及成员函数亦未改。TimeCost 的 t0/t1 边界、区内输出复制和四个日历时间打印位置不变；新增 prepare 位于 getLut 与 SpareLut 之间。新增全局 Pipeline 对象及内嵌算法不计为改动原函数。

**本次从两文件变单文件，没有再次修改这 13 个函数；上表描述的是 final1 相对最初空模板的累计变化。** 原始框架文件原地 SHA 仍未变，修改发生在独立交付副本。

## 文件与交付

- 正式源码：[submission/final1/main.cpp](../../submission/final1/main.cpp)。
- 构建来源检查：`python scripts/package_final1.py`；暂存及证据核验：`python scripts/verify_final1.py --staged`。
- 新证据：[final1-single-20261030](../../report/data/final1-single-20261030)，包含本机/服务器等价回执、100 图逐段原始样本及原函数审计。
- 服务器独立复现目录：`~/workspace/zmx/final1-single-20261030`；正式目录继续为 `~/workspace/zmx/final1`，旧两文件包备份保留，发布回执记录确切位置。

在复现目录运行 `python3 ../run_on_pcore.py --core 6 --timeout 180 -- python3 run_single_validation.py`；脚本需要仍为两文件的 previous 目录做旧版对照，发布后将脚本中的 previous 指向发布回执里的备份目录，不能拿已更新的单文件目录冒充旧版。数据位置仍在同一 zmx 下，且按原输入 SHA 核验。

本次读取并刷新 PR #106 正文、完整评论和审查线程，均无新意见；此前 #96 旧验证/目录绑定问题、#8 实板待办和 Discussion4 读取缺口仍按原报告保留。本包不声称修复这些问题。正式规则、额外缓存许可、规定工具链未验收，PR 继续 Draft；不合并。

Agent：Codex /root

Operator：本会话明确要求单文件交付和阶段/函数审计的用户

Task：final1 hpp 内嵌 main、逐函数审计及分段计时

Status：单文件构建、等价验证和服务器诊断完成；正式赛事条件待验收
