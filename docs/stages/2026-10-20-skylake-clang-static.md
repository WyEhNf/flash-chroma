# 同源Clang编译：静态信号不一致，未进入运行验收

Agent：Codex；Operator：WyEhNf；Task：检查编译器生成的AVX2代码；Status：Completed（对象级检查完成，收益依据不足，未链接/运行候选，不采用）。

本阶段没有修改算法，而用Clang21.1.0编译与GCC15.2参考完全相同的`channel-runtime-specialized/channel_avx2.cpp`。显式目标为`x86_64-w64-windows-gnu`、sysroot为本机MinGW；实际预处理搜索使用GCC15.2的C++头、Clang21的intrinsics头与MinGW系统头。SIMD参数为`-O3 -DNDEBUG -mavx2 -mtune=skylake -ffp-contract=off`，没有全局march、AVX512、FMA或fast-math。

目的仅为编译器/对象/汇编可行性。实际环境Windows11 26200 x64、Ryzen9 8945HX、Python3.12.14标准库、GCC15.2、Clang21.1.0及LLVM-MCA21.1.0。GCC对象复用已核验的同旗标参考构建，源码/头/对象/编译器SHA和原命令一并保存。两对象的公共C++入口修饰名完全相同，均无热循环内函数调用；这只证明符号层面的形状，不等于混合编译器运行ABI已验收。本阶段没有链接Clang候选DLL，也没有加载或执行它。

| 固定四级热循环静态指标 | GCC参考 | 同源Clang |
| --- | ---: | ---: |
| 指令数 | 568 | 588 |
| gather数 | 38 | 38 |
| vpmulld数 | 44 | 44 |
| 含rsp操作数处数 | 38 | 39 |
| MCA 100次Total Cycles | 55235 | 57541 |
| MCA 100次Total uOps | 84200 | 83500 |
| MCA Block RThroughput | 196.5 | 186.0 |

MCA显式以Skylake模型模拟：吞吐下界估计改善约5.34%，依赖序列模拟总周期却增加约4.17%，uOps只减少约0.83%，gather不变。模型不包含真实缓存未命中、微码/GDS、温度或系统负载，不能挑一个较好的模拟指标就宣布Clang更快，也不能据此宣布实际更慢。

由于没有一致且足够明确的收益依据，停止在静态阶段，不进行数值合同、完整256³、100图或性能测试，也不继续扫Clang参数。普通核心的四级映射经检查已经显式展开，不重复实现相同专门化。

[原始命令、对象、源码、汇编及MCA输出](../../report/data/skylake-clang-static-v1/README.md)保留两种方向的模型结果。下一项从坐标表示入手：只有全部G/B坐标相对R的差可表示为int16时，才能无损用一个u32保存两个差，减少坐标gather；超界保持原布局。该新编码与本编译器研究分开冻结和验收，不把推测当作已获加速。
