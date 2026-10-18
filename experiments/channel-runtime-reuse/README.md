# 未入围的地址复用AVX2研究分支

本目录只保留一次实验，不接CMake默认构建。`channel_avx2.cpp`与原研究运行时共用`View`和C ABI，八像素包的三个输出首末轴一致时复用两个packed RGB内点，各输出仍独立使用Q16权重。其他包回退原读取；RGB8舍入、模型字节和线程分块均不变。

完整色域、100图和集中合同通过，但受控比较相对packed v3慢约5.56%/6.26%，因此没有采用。详见[阶段报告](../../docs/stages/2026-10-19-channel-runtime-reuse.md)。`scripts/build_channel_reuse.py`为Windows/GCC15.2复现入口，显式记录核心静态库及DLL依赖SHA；不是新公共格式或可跨平台复用的完整构建系统。
