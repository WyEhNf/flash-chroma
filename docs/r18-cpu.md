# R18 CPU：跨图调度与精确 SIMD 候选

日期：2026-10-15。运行环境沿用 R17 已核实的原生 Windows、AMD Ryzen 9 8945HX、GCC 15.2。CPUID 的 AVX/AVX2、OSXSAVE 及 XCR0 的 XMM/YMM 保存状态均通过检查；这不是官方服务器的硬件确认。旧二进制保存在 `artifacts/r18-baseline/jshc-r17.exe`，本轮构建使用 `build-r18-cpu/`。

## 设计依据

读取了 [OpenColorIO 的 AVX2 四面体实现](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/src/OpenColorIO/ops/lut3d/Lut3DOpCPU_AVX2.cpp)、[CPU 分派实现](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/src/OpenColorIO/CPUInfo.cpp) 和 [AMD 官方 Ryzen 优化资料](https://gpuopen.com/download/GDC2024_AMD_Ryzen_Processor_Software_Optimization.pdf)。这些是设计参考，不能直接把其浮点结果当成本题整数链的真值。

OCIO 按实际 CPU 能力选择 SIMD，并对部分慢 gather CPU 避开 AVX2 gather 路径；其 AVX2 实现采用无分支比较、重心权重和向量化颜色通道。AMD 资料强调缓存共享、跨核一致性与 SMT 资源竞争。因此本轮同时比较指令选择与调度方式，不仅检查是否有 AVX2 指令。

R17 已把每级轴表读取压到三次 gather、节点读取压到四次 gather，并在四级之间保存向量 RGB。反汇编仍显示若干向量栈溢出；这只是寄存器压力证据，不能据此宣称某条指令是实测瓶颈。生成的汇编保存在 `artifacts/r18-cpu/avx2-disassembly.txt`。

## 跨图共用一个线程团队

新增 `RgbImageView` 和 `apply_chain_batch(chain, images, kernel, threads)`。图像可位于不同地址、具有不同长度；零长度视图合法，重叠的非空视图在修改数据前报错。

调度器构造图像的虚拟块前缀，在整批图像上创建一次 OpenMP 团队。100 张图只需 101 个块前缀元素，并不拼接图像；所有工作线程共享同一批已经准备好的模型。每个像素仍独立经历全部映射及每级整数舍入。没有 OpenMP 时，同一 API 串行执行。

命令行 `bench --batch` 保存全部工作图像副本，其内存成本由 `work_image_bytes` 单列。整组时间包含图像复制和映射。批次模式没有独立测量每张图延迟，因此这些旧延迟字段为 `null`；吞吐量的每图摊销不是单图延迟。先复制全批再映射也改变缓存冷热程度，收益需要包含这项成本比较。

## 三种可选内核

`auto` 暂时仍选择 R17 的 `tetra_avx2`。新内核不改变模型、网格、节点或四级语义。

- `tetra_avx2_scalar_gather`：用标量读取加向量组装替换 gather，其余 Q16 算法不变。它是慢 gather 处理器的候选；不能先验认为本机更快。
- `tetra_avx2_madd`：通过精确的 signed-16 分解，以 `vpmaddwd` 合并前两个差分乘积。RGB 插值中的乘法指令由每级九条改为六条，但增加了打包和 blend，最终成本由测量决定。
- `tetra_avx2_exact_float`：对非负整数重心权重使用 binary32 乘加，再转换为整数并右移。下述范围证明保证它仍与 Q16 逐字节一致；没有要求 FMA，不扩大 AVX2 运行条件。

### MADD 等价性

对 `0 <= f <= 65536`，有 `f = int16(f) + 65536 * [f >= 32768]`。三个分数已满足 `f1 >= f2 >= f3`，所以望远镜形式中高位修正加上 `c0` 恰好是 `c0/c1/c2/c3` 之一，可在 packed RGB 上统一选择。低位差分在 `[-255,255]`，其乘积与两项之和不会溢出 int32。65536 端点被显式包含在此等式中。

### binary32 等价性

四面体重心权重 `w0..w3` 都是非负整数，且和为 65536；节点通道是 0..255。每个乘积和任何部分和均为整数，且不超过 `255 * 65536 = 16,711,680`。加上半位 32768 后，最大为 16,744,448，仍严格小于 `2^24`。binary32 能精确表示这一范围内的所有整数，因此每次乘法、加法及转换都精确，最后 `>>16` 与整数 round-half-up 一致。

这个证明只适用于当前 RGB8/Q16 格式。如果扩展节点位深、Q 格式或允许负权重，必须重新证明或禁用该内核，不能保留名称而沿用结论。

## 集中验收

`ctest --test-dir build-r18-cpu --output-on-failure` 为本轮阶段门禁。新增内核参加原有独立 64 位重心 oracle 的全色比较、不同 m 和非均匀网格、四级整数链及线程一致性。另加 343 个半位/端点分数组合、极值节点、批次不连续地址、空图、短图、块尾部与重叠拒绝控制。

2026-10-15 14:12 的首次门禁遇到 SegFault，不能作为通过证据。GDB 将故障定位到 `avx2_chain_scalar_gather`；旧二进制 RVA `0x11479` 的故障指令为 `vmovdqa %ymm5, 0xa0(%rsp)`。MinGW GCC 15.2 将较大的 `transform<false,true>` 提取为函数后，为按值 `Rgb8` 参数生成了 32 字节对齐的存储，而 Win64 调用栈只保证 16 字节对齐；真正的局部 `Rgb8` 已有单独的 32 字节对齐指针，因此故障不是 LUT 索引读取。已将内部 load、transform、store 的全部 `Rgb8` 参数和返回改为引用，避免此聚合对象跨函数按值复制；插值算式和逐级量化保持不变。

修复重新构建后，主任务统一执行的完整 CTest **通过，exit 0，6.37 秒**，包括所有可用内核的全色 oracle、极值分数、链式映射和批次调度控制。[最终验收记录](../artifacts/r18-progress/ctest-final.json) 绑定测试程序与命令行程序 SHA256。此用时是正确性门禁耗时，不是吞吐量成绩；性能仍以单独记录的固定批次为准。

失败证据保存在 `artifacts/r18-cpu/ctest-full.log`、`LastTest-failed-1412.log`、`segfault-gdb.log`、`segfault-instructions.txt`，原二进制为 `jshc-tests-failed-f20a01e5.exe`，SHA256 为 `f20a01e5f2bd834c938826a96361e3d92beb98fee252673b29a56e3145404469`。修复后的反汇编另存为 `avx2-after-abi-fix-disassembly.txt`，不覆盖失败证据。

性能只在独占测量阶段记录。比较应保留原 AVX2、三个新候选及单图/批次两种调度，明确线程数、输入、模型、二进制哈希、复制成本和工作图像内存。未通过阶段门禁的候选不进入性能推荐；接近的结果也不应直接切换默认。
