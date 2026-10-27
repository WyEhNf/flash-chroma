# 单头文件运行库与连续目标选择接口

本接口面向部署：[`include/flash_chroma.hpp`](../include/flash_chroma.hpp)是独立的 C++17 单头运行库，[`include/flash_chroma_c.h`](../include/flash_chroma_c.h)是可选的独立 C99 单头运行库。复制所需头文件与自己的模型即可接入；部署端不依赖仓库的 Python、实验目录、JSON 解析器或私有 `.cpp`。模型拟合、参数搜索、照片解码和基准驱动保留在宿主工具中。

本阶段的实际数值、测试环境与未覆盖范围以[阶段报告](stages/2026-10-27-p16-frontier-header.md)为准。这里说明接口契约，不把接口存在当作目标机性能或官方阈值验收。

## 1. 交付形式与统一语义

C++ 在一个翻译单元中定义实现宏：

```cpp
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
```

其他翻译单元只包含该头文件。C99 对应 `FC_C_IMPLEMENTATION`；定义 `FC_C_STATIC` 时生成文件内接口。两份头文件也可以在同一 C++ 翻译单元中共同使用，嵌入 C++ 的核心具有独立命名空间与宏前缀。

两份运行库都接受四个 SLUT v1 模型，每级 `m` 独立为 17..33；执行 Q16 四面体插值，每级先按 half-up 规则生成完整 RGB8 整数，再进入下一级。可选 sidecar 恰为 9216B，排列为 `[输出通道][轴][输入RGB码]` 的小端 u32 Q16 分数，允许 0..65536；没有 sidecar 时传空指针与 0 字节。索引仍由三个通道共享。

模型、sidecar 和工作区都由调用方持有，必须在使用期间有效且保持模型不可变。运行库不根据当前图片重新拟合或换模型。direct 表从已固定的稀疏模型构造，精确保留上述四级语义；它不会消除稀疏模型相对原始密集 LUT 的近似误差。`tri` 和 `matched` 拟合模型需要各自正确的恢复器，不能因文件可解析就当作本接口的同精度模型。

C++ 头文件由 C99 核、`src/flash_chroma_cpp.inc` 和 `src/flash_chroma_selection.inc` 生成，整数核心不分别手工维护。修改维护源码后运行：

```bash
python scripts/generate_flash_chroma_header.py
python scripts/generate_flash_chroma_header.py --check
```

## 2. 运行配置与可执行表示

`fc::RuntimeConfig` 的默认值为：编译目标、`Backend::Auto`、`Representation::Sparse`、1 线程、每块 65536 像素，工作区预算为 `size_t` 上限。

| 参数 | 实际控制内容 |
| --- | --- |
| `target` | Desktop、Mobile、Embedded 或 Portable 的能力约束 |
| `backend` | Auto、Scalar、Avx2；Avx512 当前返回 Unsupported |
| `representation` | Sparse、DirectU8、DirectU16 或 DirectRGB24 |
| `threads` | OpenMP 编译启用时的请求线程数，范围 1..256 |
| `block_pixels` | 每行任务中最多映射的像素数，必须大于 0 |
| `max_workspace_bytes` | 本次准备所允许的完整 arena 预算 |

Auto 在 Desktop/Mobile 上且 CPU/OS 与编译能力允许时选择 AVX2，否则选择 Scalar。它不在运行时测多个配置择优，也不改模型。配置目录中的候选应记录明确的 Scalar/Avx2 后端，避免实测身份随机器变化。

| 表示与后端 | 准备与运行策略 |
| --- | --- |
| Sparse + Scalar | 直接读取只读模型及 sidecar；不需要 arena |
| Sparse + Avx2 | 在 arena 准备 u32 节点和打包轴表，迁入已有分输出四面体向量核 |
| DirectU8 | 穷举 RGB8 输入，建立 16MiB 索引与最多 256 项 RGB 调色板 |
| DirectU16 | 穷举 RGB8 输入，建立 32MiB 索引与最多 65536 项 RGB 调色板 |
| DirectRGB24 | 穷举 RGB8 输入，建立约 48MiB 的 RGB 输出表，另有明确容量的保护字节及对齐空间 |

三种 direct 表都支持 Scalar/Avx2。U8/U16 的调色板资格由完整输入域构造决定，模型不适合时返回 `Capacity`，不会改变模型或静默换表示。其调色板保留所选索引格式的最大容量，`palette_entries()`另报告实际使用项数。

AVX2 在 GCC/Clang x86 上以函数目标属性隔离；基础路径不要求全局 `-mavx2`。进入 AVX2 前同时检查编译能力、CPUID、OSXSAVE 和 XCR0。当前未实现单头 AVX-512 或 ARM NEON 内核。其他编译器/架构可以使用标量路径；未实测组合不能继承本机结果。

## 3. 查询容量、准备与映射

核心类型如下：

```cpp
fc::ModelBundle bundle; // models[4]、sidecars[4] 均为 fc::Bytes{指针,字节数}
fc::RuntimeConfig config;
fc::Requirements requirements;
fc::Workspace workspace; // {void* data, size_t bytes}
fc::Runtime runtime;
```

按顺序调用：

```cpp
config.backend = fc::Backend::Avx2;
config.representation = fc::Representation::DirectU8;
config.threads = 4; // 要求编译时启用 OpenMP
config.max_workspace_bytes = 24 * fc::MiB;

fc::Status status = fc::Runtime::requirements(bundle, config, &requirements);
// 应用检查 status，并在自己的分配器/静态存储中提供 requirements.arena_bytes。
status = fc::Runtime::prepare(bundle, config, workspace, &runtime);
// 应用再次检查 status，成功后才执行映射。
status = runtime.apply(source, source_bytes, source_stride,
                       destination, destination_bytes, destination_stride,
                       width, height);
```

此片段中的 bundle、workspace 和图像指针由应用填入。`Runtime` 不拥有它们，也不提供隐藏堆分配；同一个 Runtime 禁止复制和移动，避免内部模型指针失效。成功初始化后，`apply`不申请内存。线程使用不可变模型，不同调用的可写图像仍须由应用保证互不冲突。

图像不要求额外 padding 或特定对齐，支持正向 stride、非对齐地址、精确原地和完全分离输出。部分相交区域会被拒绝；输出不得覆盖模型、sidecar、Runtime 对象或持久 arena。对有效 Runtime，零宽或零高为无操作，图像指针允许空。正常参数检查在写像素前完成；缓冲区实际可访问容量和寿命仍由调用者保证。

`ready()`、`config()`、`resources()`、`selected_backend()`及`palette_entries()`提供实际诊断；`status_string()`返回中文状态说明。`compiled_capabilities()`和`available_backends()`返回 u32 掩码：1 为标量，2 为 AVX2，4 为 OpenMP；前者表示编入能力，后者另检查 CPU/OS。

## 4. arena 与内存预算口径

`fc::Requirements` 分别记录：

| 字段 | 含义 |
| --- | --- |
| `model_bytes` | 四级借用模型及 sidecar 的逻辑字节数之和 |
| `persistent_bytes` | 对齐后 arena 中，映射期间仍需有效的前段容量 |
| `temporary_bytes` | 准备阶段使用的 arena 尾段容量 |
| `arena_bytes` | persistent + temporary + 最坏 63B 起始对齐余量；无 arena 时为 0 |
| `alignment` | 内部 arena 的对齐要求，当前为 64B；传入指针可不对齐 |
| `object_bytes` | Runtime 对象本身的字节数 |

`max_workspace_bytes`检查完整准备 arena；传入工作区容量小于查询值会返回 `Budget`。U8/U16 的哈希字典、准备像素块和 AVX2 打包数据全部计入 arena。固定局部变量与编译器栈、调用者图像、OpenMP 运行库及 OS 线程栈另记，不能把 arena 当作整个进程内存上界。

准备成功后，direct 映射不再使用临时尾段；应用若支持分段回收，可释放该段。由于原始指针可能存在起始对齐偏移，保留原工作区前缀时至少保留 `persistent_bytes + 63`，并继续保持已准备数据地址不变。一般容器会保留完整 arena 到句柄销毁，实际占用仍应按容器保留容量或 RSS 报告，不能假设已经归还临时空间。

100 张 1024×768 RGB8 的输入本体为 235929600B；分离输出另需相同容量。按行/块或逐图流式执行可以降低图像工作集，但必须以所选方式重新测量时间，不能沿用整百图预载模式的成绩。模型可放入可按字节寻址的 ROM/Flash，端侧 RAM 与 ROM/Flash 应分别记账。

## 5. 部署编译开关

在包含头文件前选择默认部署目标，例如：

```cpp
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_EMBEDDED
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
```

| 宏 | 默认及实际作用 |
| --- | --- |
| `FLASH_CHROMA_TARGET` | 默认 DESKTOP；可选 MOBILE、EMBEDDED、PORTABLE |
| `FLASH_CHROMA_ENABLE_DIRECT` | Desktop/Mobile 默认 1；Embedded/Portable 默认 0，预处理裁剪 direct 实现 |
| `FLASH_CHROMA_ENABLE_AVX2` | Desktop/Mobile 且 GCC/Clang x86 时默认 1；其他默认 0 |
| `FLASH_CHROMA_ENABLE_OPENMP` | Desktop/Mobile 且编译器定义 `_OPENMP` 时默认 1；其他默认 0 |

Embedded/Portable 运行目标限定 Sparse、Scalar、1 线程；默认构建不依赖堆、异常、RTTI、文件系统或线程库。C99 入口始终是这一最小整数映射路径。Mobile 在已实现能力内使用分块、内存预算与线程控制；没有 GPU/NPU 调用，也没有已实现的 NEON 加速。

编译开关决定可用实现，运行参数必须满足编译能力与目标约束。显式请求未编入/未支持的后端或非法目标组合返回 `Unsupported`。多线程仅为请求上限：短任务、外层 OpenMP 并行区或运行库调度可能使用更少线程，不应把请求线程数当成线程实测。

## 6. 连续目标、硬预算和三维前沿

`fc::Candidate`绑定一个固定模型、明确运行配置、验证上下文、误差、时间、资源及证据位置。关键指标为：`mean_error`、`worst_image_mean`、`batch_ms`、`runtime_bytes`和`workspace_bytes`。正确性、精度、资源、时间验证与时间稳定性分别记录。上下文应固定源 LUT、验证图集、机器/软件及计时范围；不同上下文不混合排序。

权重是连续偏好，各自位于 [0,1]，不能全为 0：

```cpp
fc::Request request;
request.context = "应用填入与候选完全相同的验证上下文ID";
request.target = fc::Target::Desktop;
request.goal = fc::Goal::Balanced;
request.preference = {0.85, 0.60, 0.25}; // 精度、速度、省内存
request.max_runtime_bytes = 64 * fc::MiB;
request.max_workspace_bytes = 40 * fc::MiB;
request.max_threads = 4;

fc::SelectionView choice;
fc::SelectionStatus selected = fc::select(candidates, candidate_count, request, &choice);
// selected==Ok 后使用 candidates[choice.index].config 和对应 model_id 准备 Runtime。
```

`candidates`与`candidate_count`由应用从自己的配置目录转成记录。头文件不在部署设备上解析 JSON，也不下载或拟合模型。连续权重归一化后作用于符合约束的三维前沿；底层 m、线程、表示和后端仍是离散选择，所以输出可以保持不变后发生跳变，不能保证曲线连续或可微。

预算模式可设置 `goal=Fastest`，并开启 `has_error_limit`与`max_image_mean_error`。误差门禁使用 `worst_image_mean < max_image_mean_error`，确保绑定验证集的每张图都严格过线。`has_time_limit`与`max_batch_ms`设置同一上下文下的批次时间上限。内存和工作区上限包含等号。没有合格候选时返回 `NoFeasible`，并在`choice.rejected`保留上下文、目标、能力、未验证、时间不稳定和预算拒绝计数。

时间默认要求已验证且稳定。允许描述性观察时可显式设`require_stable_time=false`，选择结果的`provisional`会标明暂定。没有时间数据时，可设`use_time=false`并选 Accurate/Compact，或在 Balanced 中将速度权重置 0；该结果不能表述为三指标性能最优。

完整前沿独立于单个权重组合保存，便于获取非凸前沿上的候选：

```cpp
std::size_t required = 0;
auto query = fc::frontier(candidates, candidate_count, request, nullptr, 0, &required);
// query==BufferTooSmall 表示应用需提供 required 个 size_t 槽。
auto result = fc::frontier(candidates, candidate_count, request, indices, capacity, &required);
```

`frontier`输出槽不足时不修改索引数组。预算先过滤，再计算 Pareto 前沿；目录仍保留其他已验证候选，以便改变预算后重新选择。未知新 LUT 的误差必须重新拟合并验证，既有误差或连续偏好不能保证新输入质量。

## 7. 研发工具、验证与迁移边界

宿主端的[`scripts/p16_frontier.py`](../scripts/p16_frontier.py)提供目录校验、连续选择、完整前沿、混合 m/运行配置规划和实际离线拟合。`plan`只生成计划，不会把待测组合标成已验收；`fit`生成的模型仍需整链精度和实际运行时验证。单头库验证、百图基准分别由`verify_flash_chroma.py`和`bench_flash_chroma.py`承担。

构建部署合同示例：

```bash
cmake -S single_header -B build-single-header -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build-single-header --parallel 2
ctest --test-dir build-single-header --output-on-failure
```

Windows 可使用 MinGW Makefiles 并显式指定 GCC/G++。OpenMP/AVX2 可分别通过`FLASH_CHROMA_TEST_OPENMP`和`FLASH_CHROMA_TEST_AVX2`关闭。这两个名称属于仓库验证工程；直接集成头文件时使用上节的部署宏。

旧统一库、Python拟合器、实验目录和历史证据继续保留，作为兼容入口、对照及来源记录。新运行库没有自动吸收所有旧实验，包括有界后缀缓存/扫描线专门准备器、AVX-512及特定 NT 写入变体。新库准备时间和吞吐量必须按新实现实测，不能继承旧17ms或旧模型创建成绩。现有QEMU合同用于数值与系统接入，不能证明移动/嵌入式实板吞吐量、功耗或最坏时延。
