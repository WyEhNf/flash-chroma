# 56位轴表：读取更少，但尚不足以采用

Agent：Codex；Operator：WyEhNf；Task：面向最终Skylake服务器的本机时间优化，第一候选；Status：Completed（本候选验证与负结果归档完成，整体时间优化继续）。

目标是保持PR42的a399及后三模型、全部Q16值和每级RGB8输出不变，减少非共享首级的轴表读取。用户要求最终在Skylake服务器测试，本机仍为AMD。具体服务器SKU、系统和运行入口尚未提供，已异步询问；先采用AVX2路径，不要求AVX512，也不以本机取代最终服务器验收。

## 实现与数学边界

`experiments/skylake-runtime`以独立CMake项目构建同次参考库和唯一候选，不修改公共默认、既有v3或PR42的专门化源码。参考使用原四级专门化；候选把每轴每输入码值的三个17位frac与5位idx打包成一个56位条目。m≤33时idx≤31；65536端点保留完整17位。每轴两次4lane qword gather恢复8个像素，各输出按需解码，避免同时展开9份fraction。

首级轴表gather从9次减到6次，逻辑读取从288降到192字节/8像素；整条实际四级链是38降到35次gather，不能称整链减少三分之一。共享阶段仍用原dword轴表。三通道相同但与基模型不同的侧表也被保留，不能误丢回原模型。磁盘SLUT/9216字节侧表格式和整数插值公式不变。

新准备布局的实际模型容量从1058292降到1055244字节，净少3048字节；不是RSS，也不是侧表磁盘大小的减少。`-mavx2 -mtune=skylake`仅用于AVX2翻译单元，标量/CPU检测无AVX2；没有`-march=native`、AVX512或fast-math。[GCC对调度与指令集的区分](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/x86-Options.html)是此构建边界的依据。

## 集中验证

环境：Windows11 26200 x64、Ryzen9 8945HX、32GB；Python3.12.14、NumPy1.26.4、Numba0.60.0；GCC15.2 Release `-O3 -DNDEBUG`、AVX2/OpenMP。正确性显式标量1及AVX2请求1/4线程，Numba4、BLAS/MKL/OMP环境1。实际已载两主库及GCC依赖路径/SHA已核对。

目的分别为打包/解包整数正确性、实际模型完整等价和时间收益，不混用结论。一次有限合同覆盖55种布局/长度组合：混合m17/18/25/33、分通道/共享布局、相同侧表但异于基模型、单级及三/四级、0..4097像素与4096块边界、四种字节偏移、0/1/32767/32768/32769/65535/65536等关键fraction；独立uint64 oracle逐级RGB8对照，字节与写哨兵零差。两库各拒绝非法17位值、截断和端点侧表，共6条拒绝记录，不与55组累计。

随后只对冻结候选一次执行完整256³：两库的单级/实际四级标量1和AVX2请求4均与独立oracle/既有完整oracle流逐字节一致；100张1024×768 RGB8照片逐图及聚合输出SHA完全复现PR42。新拟合0次、精度重新选型0次；保持相同输出，所以精度沿用相同模型的既有完整结果，不冒称新增精度收益。

## 唯一性能比较：未过门槛

通过Windows实际拓扑选取同一32MiB L3域内4个物理核各一个逻辑CPU：0/2/4/6。只约束计时子进程亲和性，不改全局机器设置。四个串行新进程按AB/BA/BA/AB顺序，线程顺序1/4、4/1、1/4、4/1，每配置5轮完整100图。输入预载235929600字节；每项预热并核完整100图输出。apply和copy+apply分列，排除IO/解码/准备/统计。

| 请求线程 | 参考apply摊销ms/图 | 候选apply摊销ms/图 | 同进程比值中位数 | 最差进程比值 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 10.920805 | 10.602845 | 0.973329144（时间下降2.6671%） | 0.979950109 |
| 4 | 3.148800 | 3.143115 | 0.988962003（时间下降1.1038%） | 1.118784198 |

每项先取该进程5轮中位，再算candidate/reference比，最后取四进程比值中位；不能拿表中两端聚合中位数相除替代。预冻结门槛为两个线程数apply比均≤0.97、任意进程≤1.02、copy+apply中位比≤1；前两类门槛失败。copy+apply中位比为0.973909094/0.989653339，未退化。结论是本机收益不足且四线程有波动，**不采用、不放宽门槛、不按同一候选追加计时轮次**。

本次改变了编译调度和核集合，因此不能把10.921/3.149与PR42的11.956/4.483跨阶段拼成调度或算法收益。未锁频、控温，CPU集合固定不等于频率固定；整组摊销不是单图尾延迟。Skylake的gather成本还可能受微码/GDS缓解状态影响，最终应记录而不是关闭缓解来制造收益，参见[Intel说明](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/resources/gds-mitigation-performance-analysis.html)。

## 文件、复现和后续

计划为`experiments/skylake-packed-v1.json`及`skylake-packed-perf-v1.json`；实现为`experiments/skylake-runtime`；入口是`build_skylake_runtime.py`、`verify_skylake_packed.py`、`accept_skylake_runtime.py`、`bench_skylake_runtime.py`，共用`skylake_support.py`的身份/实际模块校验。阶段档案见[原始数据与清单](../../report/data/skylake-packed-v1/README.md)，包含源码快照、两库/依赖/静态核心、55组合同、完整输出身份、拓扑、四进程80原轮次、汇编和门槛复算。

```text
artifacts/error-study-py312/Scripts/python.exe scripts/build_skylake_runtime.py --plan experiments/skylake-packed-v1.json --output artifacts/skylake-packed-build-v1 --cmake "C:/Program Files (x86)/CMake/bin/cmake.exe" --compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator "MinGW Makefiles"
artifacts/error-study-py312/Scripts/python.exe scripts/verify_skylake_packed.py --plan experiments/skylake-packed-v1.json --build artifacts/skylake-packed-build-v1 --output artifacts/skylake-packed-contract-v1
artifacts/error-study-py312/Scripts/python.exe scripts/accept_skylake_runtime.py --plan experiments/skylake-packed-v1.json --build artifacts/skylake-packed-build-v1 --contract artifacts/skylake-packed-contract-v1/results.json --output artifacts/skylake-packed-full-v1
artifacts/error-study-py312/Scripts/python.exe scripts/bench_skylake_runtime.py --policy experiments/skylake-packed-perf-v1.json --output artifacts/skylake-packed-perf-v1
```

所有目录拒绝覆盖；按本候选的提交或归档源码重建，使用新的输出目录并重新绑定新构建/回执SHA，不复用旧时间。Linux构建入口已经提供，但未在Linux/Skylake执行，不能当作跨系统验证通过。

下一候选转向精确16位成对乘加及热循环spill，依据实际汇编和独立整数推导推进，不再围绕这一个轴表布局扫描参数。官方数据、Threshold、最终服务器及实板仍未取得；分输出坐标仍是研究表示，GUI/C99与默认不变。
