# CPU 交付入口与历史评分候选

2026-10-30 新增：[final1 单文件交付](final1/README.md)，用于当前 256³ 文本 3DL / RGB8 bin 赛事框架，单线程、33³ + prefix_nodes + DirectRGB24；[单文件验证与分段耗时](../docs/stages/2026-10-30-final1-single.md)和[历史选择依据](../docs/stages/2026-10-30-final1.md)记录当前结果。该组 LUT 与下文旧 Cinema 候选不同，精度和耗时不可直接混用。final1 独立保存，不覆盖旧交付。

需要连续精度/时间/内存选择与独立头文件部署时，使用新的[单头接口](../docs/single-header-runtime.md)和[本轮配置目录](../report/data/p16-frontier-header-20261027/catalog.json)。新入口为 `pixi run --locked build-header`、`frontier` 和 `header-run`；下文保留原修订102的评分候选及历史耗时，不能把它们当作新头文件的重测结果。

[性能与策略方法总结](../docs/p16-cpu-performance-summary.md)说明当前模型、等价direct编译、AVX2及内存取舍，并区分三种批次计时范围。

当前推荐配置为 **373a固定模型＋修订100准备器＋AVX2线性direct＋4线程**，发布包在 [p16-cpu](p16-cpu/manifest.json)。这是已验证研究中的保守选择，不能在官方Threshold、精度换分及目标机结果未知时证明最高总分。[本轮完整结果与选择理由](../docs/stages/2026-10-27-p16-score-candidate.md)。

默认所有测试图像使用同一套参数，四级m独立允许17..33；本包两个示例均m33。运行时CPU-only，优先AVX2、不支持时标量回退，发行构建去掉AVX-512对象。保留四级Q16四面体及每级RGB8整数舍入；派生direct精确复现固定四级模型。程序不按图片重新拟合或换profile。

| profile | 用途 | 本轮百图平均ΔE | 最差单图平均ΔE | Model容量 |
| --- | --- | ---: | ---: | ---: |
| `default` | 推荐默认，保留成熟速度路径 | 0.695486159059 | 1.119051322056 | 18,715,824B |
| `max_first` | 显式均值优先档 | 0.679090181058 | 1.084102390342 | 35,495,456B |

数值来自同一已见Cinema四LUT和100图的本轮独立密集原表复核，不是未知LUT承诺。表格显示值经过取舍；正式门禁使用程序未舍入的逐图mean严格`<T`。max48/max41保留研究数据，平均值并未优于max_first，不放入当前精简发布包。

## 构建与运行

仓库默认Linux/Pixi环境无需新增依赖。`psutil`只是可选的进程观测；缺失时RSS明确不可用，模型和图像容量照常报告。Windows可用MinGW GCC和Python，已测Python3.12.14、NumPy1.26.4、Pillow10.4.0。

```bash
pixi run --locked build-score
pixi run --locked score run --package submission/p16-cpu --library build-score/libjshc_unified.so --images assets/photos/eval.txt --image-root . --output artifacts/my-score-run --threads 4
```

Windows库名为`libjshc_unified.dll`；配置命令改用`-G "MinGW Makefiles"`并指定GCC/G++。本机已构建库在`artifacts/p16-score-cpu-build/libjshc_unified.dll`，其身份见阶段回执。目标Xeon6140需要使用同一代码重新构建和验证，不能沿用本机耗时。

输入清单必须正好100张1024×768 RGB8，路径相对`--image-root`；图片需自行准备，仓库入口不自动下载。默认只返回真实输出SHA及运行记录，映射后的像素实际在caller-owned输出区生成；需要PNG文件时加`--write-images`。

验证实际平均误差时追加原始四张密集RGB8 LUT（各恰为256³×3B），以及评测给定的阈值：

```bash
pixi run --locked score run --package submission/p16-cpu --library build-score/libjshc_unified.so --images my-100-images.txt --image-root /data --output artifacts/verified-run --reference-luts lut1.lut256 lut2.lut256 lut3.lut256 lut4.lut256 --threshold YOUR_THRESHOLD
```

将`YOUR_THRESHOLD`替换成实际数值，不预设官方值。程序先逐级独立原表查找，再逐像素计算RGB欧氏距离；每图取全像素平均，汇总按像素数加权。某图mean未严格过线时返回退出码2。没有参考表或T时不会伪称官方过线、估算赛事分数。

输出分别记录整百图映射、SLUT读入/精确缓存准备至首批完成、读图至首批输出可用的应用wall；额外7轮热批次全部保留。`--write-images`启用时应用wall还包含PNG写盘。离线从密集LUT拟合稀疏参数的时间另计，不包含在上述SLUT准备时间中。

## 新的四张LUT

本包是固定Cinema回归模型，不能用它处理另一套LUT。新LUT先走现有通用拟合入口，例如：

```bash
pixi run --locked lutlab fit --inputs lut1.lut256 lut2.lut256 lut3.lut256 lut4.lut256 --m 33 --grid dp --method ls_tetra_jitter --mode seq
```

该命令只是成熟起点，m33和该拟合器不保证任意LUT最优。可离线比较各级m和拟合配置，必须用最终四级输出核均值，再冻结一组；现有[混合m组装](../python/lutlab/stage_bundle.py)可保留阶段来源。本入口不静默使用legacy `accept`的max/both默认，也不把Numba matched研究当作新C++后端。

把选定四个SLUT及可选的四个sidecar槽记录成与 [源清单](p16-cpu-source-manifest.json) 相同结构，填写真实SHA256、显式`interpolation_basis: tetra_q16`，运行：

```bash
pixi run --locked score pack --manifest my-model-manifest.json --output artifacts/my-fixed-model-package
```

四级可有不同m。普通独立拟合的sidecars均为null。明确声明tri或matched阶段的模型会被拒绝，因为它们需要不同恢复器，不能把三线性拟合节点当作同质量的四面体节点。自有私有模型可不提供第三方许可；如涉及第三方资产，应保留实际来源许可，不能套用Cinema的MIT归属。

## 内存与包体

两套模型原文件共914,936B，按整文件SHA内容寻址后只存6个对象、569,531B，减少37.75%。[MIT许可](p16-cpu/licenses/00-LICENSE.stripedpurple)原字节保留。去重只减少交付包体，不声称减少像素运行RAM。

100图完整输入和分离输出合计471,859,200B，另加所选Model及程序开销；运行仅加载一个profile。参考原LUT的独立精度验证还需四个只读映射，这属于验证阶段，不混作生产热路径模型容量。真正RSS及进程峰值含Python/模块/allocator，不能当作算法纯RAM。逐图或原地模式可另行设计，但不能冒用本次整百图分离计时。

所有输出目录默认拒绝覆盖。源码、模型、库、图片及环境的身份写入回执；模型在整个批次前后核SHA。CI额外构建CPU发行库并从发布包重放两套模型的完整RGB8流，功能正确性、拟合误差、性能及官方判分分别判断。
