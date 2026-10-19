# 不重叠内存域与restrict：少读元数据，仍不足以进入实测

Agent：Codex；Operator：WyEhNf；Task：减少固定四级SIMD循环的重复模型读取；Status：Completed（静态阶段停止，候选未运行，整体时间优化继续）。

本轮为私有实验建立图像与模型读取区不重叠的检查，再给AVX2入口增加GNU `__restrict__`。生成代码确实少了46/51条循环指令，但寄存器压力增加，含rsp操作数从41/38增至70/66。当前a399模型对应路径的MCA周期估计只改善2.22%，另一条路径改善5.48%，两条吞吐下界都略差，未通过测试前固定的“两条完整路径均有至少3%明确潜力”条件。因此没有加载候选或执行新的整数、完整色域、照片及性能测试，也没有继续扫描别名或快照变体。

## 为什么需要先检查不重叠

图像是`uint8_t`字节写入，编译器不能无条件假定它不覆盖模型对象或轴/节点数组，可能在每8像素之后重新读取元数据。[GCC15.2官方说明](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/Restricted-Pointers.html)允许C++定义使用`__restrict__`表达不别名，并说明最外层参数限定符不影响函数匹配；因此无需改变原函数原型或公共ABI。这个承诺需要真实前提，不能只靠修饰符获得速度。

参考为已验无缓存坐标差修订5，候选私有命名空间`jshc_restrict`、声明修订12。AVX2代码只在`fixed_four`和`avx2_chain`定义的chain/data指针增加限定符，RGB装载、几何、Q16公式、逐级half-up及RGB8、尾部、布局判断、内联组织均沿用修订5；不混合此前停止的共享轴或同色后缀实现。Win64的Rgb仍只经引用传递。

创建完成全部模型和指针后，Handle准备一组`[begin,end)`所有者范围：Handle及模型/View/外层vector/原模型指针数组，每级canonical节点、三条grid、PackedTables对象及packed节点、私有坐标数组，并包含范围数组自身的容量区。先reserve再记录自身，排序后只合并相邻或重叠区间，不以整个堆地址的最小/最大值包围所有模型，避免误拒分配间隙中的合法图像。容量预算为`6+7*stages`，四级x64预计多24字节vector头和544字节范围存储，合计568字节；这是源代码核算，尚未运行资源诊断，不是RSS。

`apply`在后端分派、线程启动和写入前检查地址溢出/交叠；`bench`还在`memcpy`前检查工作区，防止先复制破坏模型。只读诊断分别导出所有者范围和从真实View指针导出的shader读取范围，计划用独立覆盖核对及拒绝测试验证前提，而不是只相信自报的保护列表。地址仅供未来进程内检查，当前没有运行或发布地址。

这些范围不枚举shared_ptr控制块或分配器头，不声称能安全处理任意坏指针；错误缓冲区仍按原有效独立输出约定。拒绝逻辑、额外资源核算和只读诊断都尚未通过运行合同。脚本新增可选摘要及仅在`restrict_policy`下使用的资源分支，其他计划保留原默认判定；这几个新分支未执行，不以历史合同给它们补发通过结论。公共core、默认、冠军、CLI/GUI/C99、AGENTS.md不变。

## 一次构建与两条完整循环的结果

目的为静态潜力筛选，环境为Windows11 26200、Ryzen9 8945HX、Python3.12.14标准库、MinGW GCC15.2及LLVM-MCA21.1。Release AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`，基线分派TU没有AVX2泄漏；未用AVX512、FMA、fast-math或全局march，未改变频率、温度或安全缓解设置。MCA以Skylake模型建模，不等于实际Skylake性能。

分析器固定选择35/38-gather、44次vpmulld、单后向分支、零调用的两类完整循环，全部分析，不挑最好的一条。参考两个对象与原修订5构建逐字节相同，独立源码、计划、库/对象、工具身份及完整日志均归档。

| 每8像素循环 | a399差值：参考→候选 | 原九表：参考→候选 |
| --- | ---: | ---: |
| 指令数 | 575→529 | 570→519 |
| gather / vpmulld | 35 / 44，均不变 | 38 / 44，均不变 |
| 含rsp操作数 | 41→70 | 38→66 |
| MCA 100次Total Cycles | 44732→43737 | 56434→53343 |
| 建模周期变化 | −2.224% | −5.477% |
| Total uOps | 83300→80000 | 84400→80600 |
| Block RThroughput，越小越好 | 180.5→183.0 | 196.5→198.0 |

减少元数据指令没有直接换成稳定潜力：数据指针和常量更长时间活跃，栈操作数明显增加；吞吐下界分别变差约1.39%/0.76%。这些是生成代码特征及静态估计，不能把rsp操作数称为实际cache miss，也不能宣称实测快或慢。新增范围检查和准备成本尚未计时，静态循环本身已未达门槛，故不进入运行阶段。

## 复现、交付与后续

在保存的原字节源码快照下复现；Git换行规范化后若冻结哈希不同，应恢复快照，不改历史计划的哈希。

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/build_skylake_runtime.py --plan experiments/skylake-restrict-v1.json --output artifacts/skylake-restrict-build-reproduce --cmake "C:/Program Files (x86)/CMake/bin/cmake.exe" --compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator "MinGW Makefiles"
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/inspect_skylake_restrict.py --plan experiments/skylake-restrict-v1.json --build artifacts/skylake-restrict-build-reproduce --output artifacts/skylake-restrict-static-reproduce --objdump E:/mingw64/bin/objdump.exe --mca "C:/Program Files/LLVM/bin/llvm-mca.exe"
```

[完整证据](../../report/data/skylake-restrict-static-v1/README.md)保留这一次构建、两族全部汇编/MCA、停止依据及未执行项目。没有新拟合、误差或性能结果；RGB欧氏距离口径及现有四方案服务器传输包不变。本阶段向现有Draft PR43追加中文提交，不合并。

此前快照、预计算和本轮结果共同说明，减少循环指令还受寄存器压力限制。接下来先核算已验精确后缀缓存的工作集与访问局部性，判断是否值得改存储布局；不重测已失败项，不把新的静态提议算作性能成果。Skylake具体SKU/系统/入口/GDS、正式实测、官方数据/Threshold及派生表许可仍待取得。

后续状态：[R连续缓存阶段](2026-10-20-skylake-r-contiguous.md)完成新的访问剖面、完整正确性与唯一性能比较，中位改善但回退保护失败，未采用；本阶段restrict本身仍未运行。
