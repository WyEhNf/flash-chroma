# 批入口描述符值快照：静态阶段停止

Agent：Codex；Operator：WyEhNf；Task：减少四级热循环的重复元数据读取；Status：Completed（静态潜力不足，不进入数值或性能验收，不采用）。

本候选只把固定四级路径的四个`const View&`改为批入口的四个局部`const View`值。描述符指向原有只读节点/坐标；没有新增查色表、修改插值公式或模型。假设是局部快照能让编译器把不变的指针/stride读取移出循环。源码在`experiments/skylake-snapshot-runtime`，冻结计划为`experiments/skylake-snapshot-v1.json`。

只进行了构建、汇编检查和静态建模。环境：Windows11 26200 x64 / Ryzen9 8945HX；MinGW GCC15.2、Release `-O3 -DNDEBUG`，AVX2 TU为`-mavx2 -mtune=skylake -ffp-contract=off`。LLVM-MCA21.1.0显式`-mcpu=skylake -iterations=100`，输入为同次objdump提取的最长后向条件分支热循环；CPU执行的是模拟工具，不是Skylake实机测试。没有加载候选库执行像素，没有数值、单元或性能测试。

| 热循环静态指标 | 同次参考 | 快照候选 |
| --- | ---: | ---: |
| 指令数 | 568 | 526 |
| gather数 | 38 | 38 |
| vpmulld数 | 44 | 44 |
| vpbroadcastd数 | 12 | 0 |
| 含rsp的操作数处数 | 38 | 73 |
| 通用寄存器内存加载 | 30 | 18 |
| MCA Block RThroughput | 196.5 | 201.5 |
| MCA 100次模拟Total Cycles | 55235 | 54045 |

指令减少7.39%，但栈访存处数增加92.11%，最主要的38次gather没有减少。MCA吞吐估计下界恶化2.54%，100次依赖模拟总周期却仅改善2.15%，并未给出一致、足够大的收益理由；候选整对象指令数还从947增至994。不能只挑指令条数或某一个模拟数值宣称更快。

该模型不包含真实缓存未命中、微码/GDS、前端细节、温度或操作系统干扰；这些模拟值绝不是实测周期或速度。由于当前静态证据不足以支持可观性能改进，停止本候选，不做完整256³、百图或benchmark，不声明候选运行时已验收，也不修改默认。

下一步改为检查按阶段遍历同一12KiB像素块：一次只活跃一张模型表，尝试降低单级内核的寄存器活跃范围和长依赖链，同时明确增加三轮RGB8读取/写入。这是不同的数据流假设，不是在本快照上继续扫编译选项。

[原始构建、完整汇编及MCA输出](../../report/data/skylake-snapshot-static-v1/README.md)保留所有相互不一致的静态证据；复现从源码ZIP恢复字节，构建命令见build.json，MCA命令见analysis.json。静态归档与链接检查也不替代整数正确性。
