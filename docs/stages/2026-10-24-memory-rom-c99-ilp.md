# 固定8像素C99批读取仍未达50%吞吐底线

Agent：Codex `/root/memory`；Operator：本会话项目用户；Task：16题方向3第三阶段；Status：验证及性能完成，候选拒绝。原有精确ROM、字典、ANDN研究结论和公共默认均不被本次候选替换。

本轮只实现一个标准C99方案：每8像素先取得全部ID，再取得8个调色板输出，最后写RGB24，以增加独立内存访问并行度；剩余0..7像素精确标量处理。整个8像素的源读完才写，保持同址语义，无越界读写、heap、对齐要求、ISA或编译器专用intrinsic。新增独立`memory_rom_ilp.c/.h`和`jshc_mem_apply_ilp`实验出口；原C99出口保留，桌面适配器以编译时别名接新函数。没有扫描4/16像素或编译参数，也没有将ANDN和新C99性能混算。

构建前`experiments/memory-rom-ilp-v1.json`冻结11份源SHA。Windows11 26200、Ryzen9 8945HX、GCC15.2 `-std=c99 -pedantic-errors -O3 -Wall -Wextra`，Python3.12.14/NumPy1.26.4；OMP_DYNAMIC=FALSE、OMP_WAIT_POLICY=PASSIVE，请求1/4线程，无锁频/绑核。C99 TU无AVX2/BMI1；旧AVX2对象逐字节沿用，性能只选kernel0。借用ROM与1056字节model不变，额外堆scratch为0；本机`.su`给ILP函数帧176字节，相对普通apply的64字节增加112字节，这不代表调用链或线程栈总峰。

15配置完整256³、3850有限合同、304保护页/非对齐和23项拒绝通过。独立C99 DLL实际绑定ILP出口参与有限对照；并行C99 ILP执行完整域，与已验独立整数流逐字节一致。五种ROM容量和完整/百图SHA不变，mean/p99/max及逐图精度都保留100%。没有跨目标实际执行本次新ILP，仅基础C99的wasm32与交叉编译另有根代理阶段。

性能冻结为78/80/C99线性/C99的16及64字节块五角色，四串行新进程、轮转/反序、交错1/4线程及两接口，每配置一次预热＋5次完整100图，另每运行情形尾部80 A/A。共400个主要轮次、80个A/A轮次，计时排除恢复输入、准备、IO和hash，首尾输出hash通过。

| 有效分离输出情形 | 中位吞吐保留 | 最劣worker保留 | 双底线判定 |
| --- | ---: | ---: | --- |
| 线性，1线程 | 31.44% | 27.36% | 越50%，拒绝 |
| 16字节块，1线程 | 25.62% | 24.87% | 越50%，拒绝 |
| 64字节块，1线程 | 27.49% | 24.24% | 越50%，拒绝 |
| 线性，4线程 | 40.05% | 37.82% | 越50%，拒绝 |
| 16字节块，4线程 | 32.23% | 30.77% | 越50%，拒绝 |
| 64字节块，4线程 | 33.91% | 32.41% | 越50%，拒绝 |

分离输出1/4线程A/A中位1.0431/1.0097，单对均位于0.8..1.25，控制通过。原地1线程A/A中位1.113125超1.10，原地4线程单对1.280923超1.25，两者控制失败，只保留原始观察，不升级档位。没有用这两个无效情形宣称算法变快，也不从旧场次借分母。**100/90/80/70/60/50六档都没有新的合格C99候选。** 增加独立读取没有抵消RGB24拆写及其它指令成本，不再围绕批宽扫描；不能推广为所有可移植实现均不可能过线。

复现沿用首阶段Python和线程设置；先恢复冻结源并使用新输出目录：

```powershell
& $py -X utf8 scripts/build_memory_rom_ilp.py --base-build <ANDN阶段build绝对路径> --output artifacts/new-memory-ilp-build
& $py -X utf8 scripts/verify_memory_rom_ilp.py --library artifacts/new-memory-ilp-build/jshc_memory_rom.dll --roms <原ROM目录> --data-root <原模型根目录> --output artifacts/new-memory-ilp-full
& $py -X utf8 scripts/bench_memory_rom_ilp.py --build <新build绝对路径> --roms <原ROM目录> --ref80 <同源80绝对路径> --data-root <原模型根目录> --output artifacts/new-memory-ilp-perf
```

[完整精简证据](../../report/data/p16-memory-ilp-v1/README.md)保存冻结源、实际库、全部原始轮次、RSS与A/A。同期补充`.gitattributes -text`，让内存研究原始JSON和冻结策略按工作区原字节进入Git；这是证据格式修正，不重跑或变更任何数值。后续若研究重叠组内4字节写等新方案，须另立冻结阶段，不追写本次失败记录。
