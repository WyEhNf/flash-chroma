# Cortex-M / FreeRTOS 嵌入式运行时（WIP）

本目录提供可独立构建的 C99 静态库 `jshc_embedded`，及 Cortex-M3 / FreeRTOS / QEMU 验证固件。主机侧 Python/C++ 负责离线拟合；端侧只读取既有 `.slut` v1 模型并执行四级 Q16 四面体映射，每级都独立取整到 RGB8，不合成四张 LUT。

目前验证目标为 QEMU `mps2-an385`（Cortex-M3）与 FreeRTOS-Kernel V11.2.0 的 GCC ARM_CM3 端口。RISC-V、其他 Cortex-M、具体芯片 BSP、DMA/缓存一致性、ISR 内调用和实板均未验证；QEMU 结果不代表设备吞吐量、功耗或实时截止期。

## 运行时边界

- 仅编译 `src/jshc_embedded.c`，C99 标准整数；不链接桌面核心、STL、拟合器、图片解码器、OpenMP 或 SIMD。
- 无堆分配、文件读取、环境变量、异常、全局可变状态或浮点运算。运行时静态库没有未定义外部符号；RTOS 验证固件只链接内核、测试支持层及编译器 `libgcc`。
- 初始化严格核验 magic、version、reserved、m、精确文件长度、cell 范围与 Q16 分数范围；截断、尾随字节或非法表项会被拒绝。网格 f32 元数据不参与映射，权重以序列化的 idx/frac 为准，与桌面内核一致。
- 逐字节读取 little-endian 字段，无需模型地址对齐。输入模型以只读视图借用；调用者负责模型寿命和不可变性，可直接存放在能按字节寻址的 Flash/ROM 中。此版本不支持需要特殊访问指令或外部驱动的存储。
- 原地 RGB 缓冲可以整图或分块提交；0..4 级、0 像素、非对齐缓冲及短尾均有明确语义。API 参数失败不写入 RGB。缓冲区容量与不重叠约束见 [头文件](include/jshc_embedded.h)。

## 独立构建与宿主检查

无需 Pixi、Python 数值依赖或 C++ 编译器：

```bash
cmake -S embedded -B build-embedded-host -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build-embedded-host --parallel 2
ctest --test-dir build-embedded-host --output-on-failure --no-tests=error
```

库位于 `build-embedded-host/libjshc_embedded.a`，公开头为 `embedded/include/jshc_embedded.h`。作为子项目接入时可 `add_subdirectory(embedded)`，并链接 `jshc_embedded`。设置 `BUILD_TESTING=OFF` 只构建库，不要求 QEMU 或 FreeRTOS。

仓库根目录默认构建也包含该库、共用 C 契约测试以及桌面互操作测试；`JSHC_ENABLE_EMBEDDED=OFF` 可关闭新增部分。原来的桌面构建和拟合功能继续按原入口使用。

## QEMU 中的 RTOS 验证

Ubuntu 24.04 的依赖安装命令：

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends -y \
  gcc-arm-none-eabi libnewlib-arm-none-eabi qemu-system-arm ninja-build cmake python3
```

Arch Linux 对应 `arm-none-eabi-gcc`、`arm-none-eabi-newlib`、`qemu-system-arm`、`cmake`、`ninja` 和 `python`。Newlib 提供上游内核使用的标准头文件；本固件通过 `-nostdlib` 链接，不使用 Newlib 运行时或其堆实现。

在仓库根目录执行：

```bash
cmake -S embedded -B build-embedded-qemu -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=cmake/cortex-m3.cmake \
  -DCMAKE_BUILD_TYPE=MinSizeRel -DJSHC_EMBEDDED_FREERTOS=ON
cmake --build build-embedded-qemu --parallel 2
ctest --test-dir build-embedded-qemu --verbose --no-tests=error
arm-none-eabi-size build-embedded-qemu/freertos/jshc_rtos.elf
arm-none-eabi-nm -u build-embedded-qemu/libjshc_embedded.a
```

首次配置下载固定的 [FreeRTOS-Kernel 提交](https://github.com/FreeRTOS/FreeRTOS-Kernel/tree/0adc196d4bd52a2d91102b525b0aafc1e14a2386)，并校验归档 SHA-256 `6af5d78e39a5237b63faaafdc31672c87b27b68e713e2a57d3528aa3a4c1cee8`。源码与 MIT 许可证原文保留在构建目录 `_deps/freertos_kernel-src/`；分发链接内核的固件时应随附其原始版权和许可声明。不修改上游源码。离线环境可传 `-DFETCHCONTENT_SOURCE_DIR_FREERTOS_KERNEL=/path/to/verified/kernel` 使用已核验的同一提交，此覆盖路径由调用者负责来源完整性。

测试固件自行提供最小启动向量、链接脚本与诊断支持层，静态创建 LUT 任务、观察任务及 idle 任务；关闭 FreeRTOS 动态分配，不编译任何 `heap_*.c`。LUT 任务周期性阻塞，让观察任务和 SysTick 得到执行；验收同时检查映射、心跳和 tick 推进。断言、异常与栈溢出走失败退出。

`run_qemu.py` 要求 QEMU 退出码为 0 且输出精确成功标记；非零退出、缺标记、异常或 30 秒超时均失败。semihosting 只用于测试固件输出诊断和退出，运行时库不依赖它。可直接执行：

```bash
python3 embedded/freertos/run_qemu.py \
  --elf build-embedded-qemu/freertos/jshc_rtos.elf
```

## 接入应用与内存预算

调用者从自己的存储系统取得四张 `.slut` 字节，分别初始化四个视图：

```c
jshc_embedded_lut views[4];
const jshc_embedded_lut *chain[4];
for (size_t i = 0; i < 4; ++i) {
    if (jshc_embedded_init(&views[i], model_data[i], model_bytes[i]) != JSHC_EMBEDDED_OK) {
        /* 在映射前报告模型错误。 */
        return;
    }
    chain[i] = &views[i];
}
if (jshc_embedded_apply(chain, 4, rgb_block, block_pixels) != JSHC_EMBEDDED_OK) {
    /* 在应用层报告输入错误。 */
    return;
}
```

32 位 Cortex-M 上每个视图为 16 字节；函数只用固定局部变量，不复制节点、不申请整帧或块级中间缓冲。模型本身仍需要存储，不能用“零堆分配”推断模型无需 RAM/Flash：

| 网格 | 单张 `.slut` 字节 | 四张同网格字节 |
| --- | ---: | ---: |
| m=17 | 18,799 | 75,196 |
| m=18 | 21,568 | 86,272 |
| m=25 | 51,031 | 204,124 |
| m=33 | 112,063 | 448,252 |

文件大小公式为 `16 + 12*m + 3840 + 3*m³`。模型格式允许 m=2..256，实际设备须自行检查存储容量；赛题网格限制仍独立适用。使用 256 像素块时 RGB 工作缓冲仅 768 字节，由应用分配。四级映射每级的 RGB8 取整都发生在块内部，不需要保存四份图像。

QEMU 契约固件为了生成随机模型、破坏模型和检查拒绝行为，特意在 BSS 保留四份最大测试模型；这不是生产部署的只读存储方案，也不是小 RAM 芯片可直接运行的整套测试镜像。AN385 的 4 MiB 数据 SRAM 可容纳这些测试夹具。任务栈余量由测试固件输出，数值仅对应此次工具链和测试路径，不是 WCET 或所有应用调用的栈上界。

## 验证范围与后续工作

共用 C 契约在宿主和真实 FreeRTOS 任务中执行：四种混合网格、非均匀轴、四级取整、0..257 像素和哨兵、未对齐模型/RGB、Q16 端点与半值、常量和极端节点、损坏头部/表项、所有截断长度、尾随数据和错误参数。参考实现独立选择顶点并以 u64 计算重心权重。

桌面门禁另用 `SparseLut::save` 生成实际 `.slut`，分块穷举全部 `2²⁴` RGB，比较四级 C99 输出与桌面标量输出。桌面原有内核测试继续以独立 oracle 检查后端正确性。QEMU 只运行有界契约，未在仿真器中穷举全色域，也不评估真实 LUT 的拟合精度。

后续须由具体目标约束驱动：实板 BSP/存储接入、预抢占场景与栈预算深化、RISC-V RTOS 端口及对应 QEMU 机器。NEON/RVV 优化、性能测量和 DMA 接入不属于当前结果。

参考：[QEMU AN385 平台说明](https://www.qemu.org/docs/master/system/arm/mps2.html)、[FreeRTOS 支持的官方示例](https://github.freertos.org/Documentation/02-Kernel/03-Supported-devices/04-Demos/02-Supported-demos)。
