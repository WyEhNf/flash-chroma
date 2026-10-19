# 两次16位乘加：整数精确，但本机更慢

Agent：Codex；Operator：WyEhNf；Task：Skylake时间优化的第二个独立候选；Status：Completed（负结果归档，不采用，整体优化继续）。

第一候选的56位轴表未过门槛后，本候选回到原32位轴表和原四级专门化，只改插值算术。`experiments/skylake-madd-runtime/channel_avx2.cpp`将每输出三次差分vpmulld改成两次vpmaddwd；另8次四级基址乘法保留，逻辑gather次数仍38，不混入第一候选。

令排序坐标x≥y≥z，且0..65536。每个f都满足`f=s16(f)+65536*[f>=32768]`，65536是低16位0加进位1。三个指示量是前缀1，节点差的进位项望远镜合并为四顶点中的一个。用一次MADD计算前两组差分乘积，第二次计算`[n3-n2,0]·[s16(z),0]`，再补所选节点乘65536及32768后右移16。节点差仅±255，MADD特殊的−32768平方溢出不可能发生；完整中间量在signed32范围内。

这复用了原项目已有signed16进位思路，但进一步去掉最后一个32位乘法。二进制实际会包含重排、进位选择与编译器spill，不能由乘法条数推出速度。保存的汇编将非共享transform独立成函数，每8像素调用且有0x1e8栈帧及真实spill。

本候选C ABI及准备布局保持revision2；**仅extended侧表路径使用新算术**，完全无侧表的链仍由原TetraAvx2处理，不能称普通默认LUT路径已经加速。原默认、CMake主项目、模型节点及格式都未替换。

## 验证与结果

目的为算术等价及实际时间收益。环境与[第一候选](2026-10-20-skylake-packed.md)一致：Windows11 26200、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、Numba0.60.0；GCC15.2 Release，AVX2 TU仅`-mavx2 -mtune=skylake`。Numba4、BLAS/MKL/OMP环境1；正确性标量1与AVX2请求1/4，性能固定同L3域物理核0/2/4/6，实际加载两库和4个依赖SHA核对。

冻结同一a399及后三模型，55组有限整数合同和6条非法侧表拒绝通过；两库单级/实际四级完整256³的标量1、AVX2请求4均与独立uint64/冻结完整流逐字节一致，100图逐图及聚合SHA复现。模型容量仍1058292字节，准备布局、序列化大小和精度均不变。新拟合0次，不新增精度选型。

唯一性能比较采用同次构建参考库：4个串行新进程AB/BA/BA/AB，线程顺序平衡，每配置5轮完整100图。apply与copy+apply分列，排除IO/解码/加载/统计，逐项预热核完整100图输出。

| 请求线程 | apply配对比中位数 | 时间变化 | copy+apply配对比中位数 |
| --- | ---: | ---: | ---: |
| 1 | 1.101621500 | 增加10.1622% | 1.103747175 |
| 4 | 1.112605970 | 增加11.2606% | 1.119176559 |

比值先按每进程5轮中位数计算，再取四进程比值中位。预冻结门槛仍为两个线程数apply≤0.97、任一进程≤1.02、copy+apply≤1；均未通过。保存负结果，停止该候选，不通过修改门槛或追加测量挑选通过结果。

未锁频/控温；本机AMD结果不等于Skylake表现。Skylake服务器具体SKU、微码/GDS状态和入口仍未取得。该算术可作为后续目标机显式候选，但不自动晋升默认，也不宣称Skylake加速。

## 复现与证据

源代码及冻结输入为`experiments/skylake-madd-v1.json`，性能计划为`experiments/skylake-madd-perf-v1.json`。入口复用第一候选的统一builder、合同、完整等价和性能脚本；builder按计划选择项目/目标，并修正动态库依赖清单的重复主库问题，不影响原计算。

```text
artifacts/error-study-py312/Scripts/python.exe scripts/build_skylake_runtime.py --plan experiments/skylake-madd-v1.json --output artifacts/skylake-madd-build-v1 --cmake "C:/Program Files (x86)/CMake/bin/cmake.exe" --compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator "MinGW Makefiles"
artifacts/error-study-py312/Scripts/python.exe scripts/verify_skylake_packed.py --plan experiments/skylake-madd-v1.json --build artifacts/skylake-madd-build-v1 --output artifacts/skylake-madd-contract-v1
artifacts/error-study-py312/Scripts/python.exe scripts/accept_skylake_runtime.py --plan experiments/skylake-madd-v1.json --build artifacts/skylake-madd-build-v1 --contract artifacts/skylake-madd-contract-v1/results.json --output artifacts/skylake-madd-full-v1
artifacts/error-study-py312/Scripts/python.exe scripts/bench_skylake_runtime.py --policy experiments/skylake-madd-perf-v1.json --output artifacts/skylake-madd-perf-v1
```

归档及源快照见[原始证据](../../report/data/skylake-madd-v1/README.md)。使用对应提交/源码和新目录重建，Linux/Skylake未实测。本轮整体阶段最终统一以PR交付，目前为本地中间检查点。
