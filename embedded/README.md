# Cortex-M / RISC-V / Cortex-A 嵌入式运行时（WIP）

本目录提供可独立构建的 C99 静态库 `jshc_embedded`，及三个 QEMU 系统级验证目标。主机侧 Python/C++ 负责离线拟合；端侧只读取既有 `.slut` v1 模型并执行四级 Q16 四面体映射，每级都独立取整到 RGB8，不合成四张 LUT。

| 目标 | OS / 端口 | QEMU 机器 | 覆盖 |
| --- | --- | --- | --- |
| Cortex-M3 | FreeRTOS V11.2.0 / GCC ARM_CM3 | `mps2-an385` | 静态任务、SysTick、心跳、共用 LUT 契约 |
| RV32IMAC + Zicsr / ILP32 | FreeRTOS V11.2.0 / GCC RISC-V | `virt`，单 hart、M-mode | 静态任务、CLINT mtime、心跳、同一 LUT 契约 |
| Cortex-A53 / AArch64 | Linux 6.12.51-0-virt | `virt`，单核 | 启动 Linux，以静态 PID 1 执行同一 LUT 契约 |

具体芯片 BSP、其他 Cortex-M、RV64、DMA/缓存一致性、ISR 内调用和实板均未验证；QEMU 结果不代表设备吞吐量、功耗或实时截止期。

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

库位于 `build-embedded-host/libjshc_embedded.a`，公开头为 `embedded/include/jshc_embedded.h`。作为子项目接入时可 `add_subdirectory(embedded)`，并链接 `jshc_embedded`。在两个 QEMU 选项均关闭时，设置 `BUILD_TESTING=OFF` 只构建库，不要求 QEMU 或 FreeRTOS。

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

### RV32 / FreeRTOS

Ubuntu 24.04 使用 `gcc-riscv64-unknown-elf libnewlib-dev qemu-system-misc`，另需通用的 CMake/Ninja/Python。`libnewlib-dev` 只提供上游内核要求的标准头，自动从 `/usr/include/newlib` 查找，不链接其运行时。Arch Linux 对应 `riscv64-elf-gcc riscv64-elf-newlib qemu-system-riscv`。编译器必须提供 `rv32imac/ilp32` 的 `libgcc` 多库；程序虽由名为 riscv64 的工具链编译，实际生成 ELF32 RV32 指令。

```bash
cmake -S embedded -B build-embedded-riscv -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=cmake/riscv32.cmake \
  -DCMAKE_BUILD_TYPE=MinSizeRel -DJSHC_EMBEDDED_FREERTOS=ON
cmake --build build-embedded-riscv --parallel 2
ctest --test-dir build-embedded-riscv --verbose --no-tests=error
```

运行器选择 `qemu-system-riscv32 -M virt -cpu rv32 -smp 1 -m 16M -bios none`。最小启动代码设置栈和 `mtvec`，使用上游 RISC-V 端口及 `RV32I_CLINT_no_extensions`。CLINT mtime 时基固定 10 MHz，UART 输出诊断，SiFive test finisher 给出退出码，不使用 OpenSBI。两个 RTOS 目标复用同一任务入口和契约，任务栈均按 16 字节对齐。GCC 会报告上游 `port.c` 中已知的 u64 定时器地址转 RV32 指针警告；该平台地址在 32 位范围内，保留上游原文，不屏蔽告警。

### Cortex-A53 / Linux

Cortex-A 选择 Linux，以验证常见的 Linux 用户态集成方式。测试使用完整系统模拟器启动真实内核，未使用 QEMU user-mode 替代内核；也未安装一套完整发行版用户空间。只构建静态测试 init，并生成含 `/init` 和 `/dev/console` 的确定性 newc initramfs，无 shell、磁盘或客户机网络。

Ubuntu 24.04 使用 `gcc-aarch64-linux-gnu libc6-dev-arm64-cross qemu-system-arm`；Arch Linux 使用 `aarch64-linux-gnu-gcc qemu-system-aarch64`，另需通用构建依赖：

```bash
cmake -S embedded -B build-embedded-linux -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=cmake/aarch64-linux.cmake \
  -DCMAKE_BUILD_TYPE=MinSizeRel -DJSHC_EMBEDDED_LINUX_QEMU=ON
cmake --build build-embedded-linux --parallel 2
ctest --test-dir build-embedded-linux --verbose --no-tests=error
```

首次测试按 [kernel-lock.json](linux/kernel-lock.json) 下载 Alpine 3.22.2 的 Linux `6.12.51-0-virt`（约 9 MiB），核验固定 SHA-256，再从 EFI zboot 中提取 gzip 内容并核验 ARM64 Image 头。缓存每次重验哈希；不在仓库提交内核二进制，也不使用滚动的 `latest` 下载地址。内核的发行构建来源、配置链接和许可证记录在锁文件中。

运行器固定 `qemu-system-aarch64 -M virt -cpu cortex-a53 -smp 1 -m 256M`，传入内核和 initramfs。客户机核验 `PID=1`、`uname.machine=aarch64`，报告内核版本后执行共用 LUT 契约，成功才打印标记并关机。客户机失败、内核 panic、缺少成功标记或 60 秒超时都不会被当成通过。静态 init 的 libc 依赖属于测试支持层；C99 映射库仍不依赖 libc。

这一路径只验证该 C99 库在 Linux 下的集成；没有在 AArch64 运行桌面 CLI、完整拟合库、Python 门禁或全色域桌面互操作测试。三个目标的代码体积、BSS 与 libc 不同，不宜直接比较。

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

32 位 Cortex-M/RV32 上每个视图为 16 字节，AArch64 上为 32 字节；函数只用固定局部变量，不复制节点、不申请整帧或块级中间缓冲。模型本身仍需要存储，不能用“零堆分配”推断模型无需 RAM/Flash：

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

后续须由具体目标约束驱动：实板 BSP/存储接入、预抢占场景与栈预算深化、RV64 和其他核心配置。NEON/RVV 优化、性能测量和 DMA 接入不属于当前结果。

参考：[QEMU AN385 平台说明](https://www.qemu.org/docs/master/system/arm/mps2.html)、[FreeRTOS 支持的官方示例](https://github.freertos.org/Documentation/02-Kernel/03-Supported-devices/04-Demos/02-Supported-demos)。

新增平台参考：[QEMU RISC-V virt](https://www.qemu.org/docs/master/system/riscv/virt.html)、[FreeRTOS RISC-V 移植说明](https://compatibility.freertos.org/Using-FreeRTOS-on-RISC-V)、[QEMU Arm virt](https://www.qemu.org/docs/master/system/arm/virt)。
