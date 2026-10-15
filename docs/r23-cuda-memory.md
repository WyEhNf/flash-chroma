# R23：CUDA测速缓冲生命周期与三条执行路径核验

日期：2026-10-15。继续串行处理，未提交或推送。R22之后仅修改CUDA程序的测速缓冲生命周期、结果检查及对应JSON字段；四级映射内核和CPU代码均未改变。

## 环境与实现

本轮实际查询两个程序，确认都使用本机NVIDIA GeForce RTX 5070 Laptop GPU、计算能力12.0；报告的全局内存8,546,484,224字节，CUDA driver API版本13000、runtime版本13020。以CUDA 13.2及MSVC x64构建原生`sm_120` cubin，不依赖新PTX的驱动JIT。CPU主线仍是已验收的AMD Ryzen 9 8945HX、16核32线程、具备OS支持的AVX2；本轮没有重跑CPU性能矩阵。

旧`bench`在传输/普通宿主往返测速结束后仍保留一对设备图像缓冲，又分配一对100图驻留缓冲。新版本在所有传输同步和输出检查完成后，通过检查返回值的`cudaFree`释放前一对，再分配驻留缓冲。析构时仅释放非空指针，没有重复释放。释放和分配均位于计时区间之外。

新增两次计时外的逐字节检查：普通宿主输出与固定页传输输出比较；驻留测速结束后下载设备输出，复用已有固定页缓冲与普通宿主输出比较。驻留分支此前只有计时，没有验证该分支的最终输出。这些比较不进入映射计时，也不把驻留kernel时间当作宿主往返时间。

JSON的`benchmark_schema_version`升为3。`image_device_buffers_bytes`现在表示各顺序阶段的**显式设备图像分配峰值**；另列`transfer_image_device_buffers_bytes`、`resident_image_device_buffers_bytes`、释放标志与三条路径的字节一致标志。该数字不包含模型、CUDA分配器/驱动开销或宿主内存，不能称为实测总显存/RSS。

## 一批验收与严格比较

本批次37.07秒。固定R22的`clip-7/m33`结构化四表，检查全部模型、100图、清单、CPU证据、旧/新二进制及构建来源的SHA。新程序实际执行全16,777,216颜色，输出SHA与冻结CPU结果一致；随后执行旧程序分组100，以及新程序分组1、7、100的实际`bench`输出，全部235,929,600字节的SHA与CPU的100图结果一致。分组7覆盖最后不足整组的情况；新程序每次还对三条测速路径逐字节比较。

模型和图片未改变，因此复用R22的误差统计；本轮核对全色及图片输出字节，没有重复计算所有误差或新增无关单元测试。R22的13项Python检查与原CPU完整CTest仍对应未改变的源码及程序；本轮CUDA变更的证据是实际新程序的上述执行。

| 显式设备分配项，100图整批 | 旧程序 | 新程序 |
|---|---:|---:|
| 设备图像缓冲峰值 | 943,718,400 B，900 MiB | 471,859,200 B，450 MiB |
| 模型节点及轴表 | 599,568 B | 599,568 B |

图像缓冲峰值减少50%。这是`bench`多个计时阶段生命周期重叠的修复；`apply`和`verify`原本没有同时保留两对图像缓冲，不能把50%降幅推广到这些命令或整个应用。

固定分组100、block256，7对AB/BA交替、每次独立进程、每程序内部3轮取中位数。宿主往返时间包含普通内存与固定页内存的复制、H2D、四级kernel、D2H和最终同步；排除拟合、加载、分配、解码、编码及输出检查。

| 100图时间，中位数 | 旧程序 | 新程序 | 配对旧/新中位数 | bootstrap 95%区间 |
|---|---:|---:|---:|---:|
| 普通宿主往返wall | 81.0966 ms | 79.7092 ms | 1.037692 | 0.982081–1.137285 |
| 固定页传输wall | 46.1928 ms | 43.1966 ms | 1.006678 | 0.999646–1.157825 |
| 设备驻留kernel event | 9.1120 ms | 11.1410 ms | 0.817878 | 0.590225–1.071002 |

宿主往返5/7对更快，但区间包含1；驻留计时仅2/7对更快，中位数反而变慢，波动明显。**本轮不作速度提升或速度无退化承诺，只确认显式图像缓冲峰值下降及执行一致性。** 不能将本轮m33程序的时间直接除以R19不同模型、不同批次的CPU时间，形成新的CPU/GPU加速比。

## 使用与证据

旧程序保留在`build-gpu/jshc_gpu.exe`，新候选为`build-r23-gpu/jshc_gpu.exe`；没有覆盖历史二进制。公共入口可显式选择新程序：

```powershell
$env:JSHC_CUDA_BIN = (Resolve-Path build-r23-gpu/jshc_gpu.exe).Path
python -m lutlab bench-models --help
```

复现本阶段：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File gpu/build-windows.ps1 `
  -OutputDirectory build-r23-gpu -Architecture 120
$env:PYTHONPATH = 'python;artifacts/r18-tools/python'
python scripts/r23_gpu_memory_study.py
```

[小型证据归档](../report/data/r23/README.md)含全部原始配对样本、预检、构建记录及源码快照；[性能摘要](../report/data/r23/paired-summary.csv)保留未舍入数值。旧GPU来源以R22源码快照与旧构建manifest的源文件SHA交叉核对。原始结果位于`artifacts/r23-gpu-memory/study.json`。

官方数据、Threshold、统计粒度和服务器配置仍未取得。R22已经明确`clip-7/m17`、`clip-23/m18`和压力家族未过本地示例门槛；本轮内存优化不改变这些精度结论。
