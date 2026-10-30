# 第16题统一CPU运行时（修订102）

Agent：Codex `/root`；Operator：本会话用户；任务：合并三方向研究并实施AVX-512。研究与取舍见[汇总](../../docs/stages/2026-10-26-p16-unified-research.md)，本轮实际验证及测量见[阶段报告](../../docs/stages/2026-10-26-p16-unified-avx512.md)。

本目录将100的扫描线准备器、293的16位精确direct表及新的AVX-512核连接到同一C ABI。默认研究配置采用373a模型和AVX2；max41为精度选项。每级m独立取17..33，模型和首级sidecar在create时固定，对所有图像保持不变。输入图像不参与运行时重新拟合。所有执行均为CPU，C++17/OpenMP，不调用GPU/NPU。

## 构建

需要GNU兼容x86-64编译器、CMake≥3.24与OpenMP。已执行环境和精确选项以阶段报告的构建回执为准，MSVC及Linux目标机尚未在本阶段验收。

```sh
cmake -S experiments/p16-unified-runtime -B build-unified -DCMAKE_BUILD_TYPE=Release
cmake --build build-unified --target jshc_unified p16_avx512_contract -j 2
```

Windows实际使用MinGW Makefiles，显式指定GCC/G++。库名为`libjshc_unified.dll`或`libjshc_unified.so`。`-DP16_ENABLE_AVX512=OFF`可去掉新对象，仍保留原标量/AVX2接口；本阶段不把配置存在称为已在无AVX512硬件执行。

AVX-512仅编译独立对象，选项限定F/BW/DQ/VL并按Skylake-SP调度，不使用VBMI/VBMI2/VNNI。公共wrapper为基线ISA；先检查CPUID、OSXSAVE及XCR0，再允许进入新核。依据[6140官方规格](https://www.intel.com/content/www/us/en/products/sku/120485/intel-xeon-gold-6140-processor-24-75m-cache-2-30-ghz/specifications.html)与[Intel支持集合说明](https://www.intel.com/content/www/us/en/support/articles/000058341/processors/intel-xeon-processors.html)选择目标集合。更宽向量并不保证更快；[Intel向量化指南](https://www.intel.com/content/www/us/en/developer/articles/technical/tuning-simd-vectorization-when-targeting-intel-xeon-processor-scalable-family.html)也要求考虑访存约束，本阶段以实测作判断。

## 接口与表示

包含`unified.h`，调用`jshc_cc_create_for_workload`加载四级SLUT及逐级sidecar槽，预计像素提示可填`100*1024*768`；它只决定是否值得准备精确缓存，不改变任何插值参数或结果。默认create相当于hint=0。句柄只保存模型和精确派生表，图像空间由调用方持有。

- `kernel=0`：标量；`kernel=1`：AVX2；`kernel=2`：显式AVX-512。
- `capabilities`的bit0/1/2为标量/AVX2/OpenMP，bit3为本库编入且CPU/OS允许AVX-512。
- AVX-512还要求句柄已有u8/u16 direct表。一般稀疏链不满足时明确拒绝，调用方可选择AVX2或标量。默认调用方继续使用AVX2，不根据“支持AVX-512”擅自切换。
- `apply_to`允许原地或完全分离的紧密RGB8，拒绝部分重叠；图像不要求对齐或额外padding。原地入口为`apply`。
- u8 direct使用恰好16MiB载荷、对齐DWORD提取ID；u16使用32MiB载荷加4B guard和实际palette。RGB24内核只有独立合同，本轮统一wrapper未选择RGB24表示。

准备器保持逐级Q16插值、RGB8 half-up舍入，再从这些稀疏模型编译等价direct输出。cache资格由完整域证明控制；本轮2MiB cache预算承接max41所需域。不满足资格或分配失败时沿已有精确通用路径，不使用近似替代。

## 质量与批次时间

`scripts/verify_p16_unified.py`核完整RGB8、百图逐图SHA、有限尾部/偏移/拒绝及独立u64混合m合同；`scripts/bench_p16_unified.py`要求绑定通过的质量回执，再固定预热1批、正式7批。模型和输入按SHA固定，已有输出目录拒绝覆盖。示例从仓库根目录运行：

```sh
python -X utf8 scripts/verify_p16_unified.py --library build-unified/libjshc_unified.so --plan experiments/p16-unified-quality-v1.json --output artifacts/unified-quality
python -X utf8 scripts/bench_p16_unified.py --library build-unified/libjshc_unified.so --plan experiments/p16-unified-quality-v1.json --correctness artifacts/unified-quality/correctness.json --output artifacts/unified-benchmark
```

上述质量计划目前绑定本机外部oracle和100照片路径；迁往目标机需复制同SHA验证资产并更新路径，不能把未带素材的命令当作即装即跑。运行时本身无需oracle、完整源LUT或照片清单。

报告同时给出固定已准备模型的100图apply总时间、模型创建时间，以及创建至首批100图输出的连续wall。图像解码、输出哈希、图像分配/预触页在apply计时之外；create包含SLUT/sidecar读入及direct准备，**不包含从原始密集LUT重新拟合稀疏模型的离线时间**。全部七轮原值保留。

运行内存分别记录真实Model容量、输入、输出、准备暂态账单和进程RSS。100张RGB8输入235,929,600B，分离输出另需相同空间；原地或逐图流式调用可降低图像工作集，吞吐须按选定模式另测。RSS含Python、模块和分配器，不能直接当作算法专属内存。
