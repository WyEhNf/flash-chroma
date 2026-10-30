# LUT 联合调优与本机 AVX2 候选筛查

Agent：`/root`。Operator：本任务用户。Task：LUT 联合存储、联合拟合路线与 AVX2 热路径探索。Status：本地研究完成，按用户授权向 `pipeline` 提交 Draft PR；性能资格与复现限制见[发布说明](../../report/data/joint-lut-avx2-20261027/publication.md)。

## 阶段目标与边界

本阶段回答两个问题：一是四级流水线及 LUT 库能否通过共享基底、差分或统一表示减少存储并简化恢复；二是在本机 AVX2 环境中，改变预取与输出存储策略能否稳定快于当前 direct 查表内核。

联合存储只要求逐字节恢复原 SLUT，不重新拟合，也不产生新的精度结论。AVX2 部分使用真实 100 图的 RGB8 地址流和确定性 16 MiB direct 表，测量 `RGB24 输入 → u8 ID 表 → 256 项 RGB32 调色板 → RGB24 输出`；它不是完整 runtime 的构造、加载或端到端计时，也不是 Xeon Gold 6140 结果。

## 联合方案判断

“联合调优”应拆成三层，不能把它们混成一种算法：

1. **联合拟合**：保留四级 SLUT 和每级 RGB8 舍入语义，生成候选节点时共享坐标信息，并用最终四级输出误差作为目标，同时约束单级和全链误差。这是下一阶段最值得做的精度路线。
2. **联合包存储**：按 SHA 内容寻址，精确复用相同 SLUT、网格或 sidecar；发布包再使用 zlib/xz，加载时一次性解压成普通结构。这能减少磁盘或传输量，不增加逐像素开销。
3. **联合运行时**：当前 direct 表已经把四级运算融合成一次最终查表。把级间节点差分放进像素热路径会增加解码和父对象依赖，本阶段数据不支持这样做。

若将四级重新拟合成单个稀疏 LUT，会改变级间 RGB8 舍入语义；除非题目明确允许，并重新执行完整色域和逐图精度验收，否则不能把它视为等价替换。

## 联合存储结果

### 两套四级配置

对象是现有 `default` 与 `max41` 两套 33³ 四级模型。两套配置连同 sidecar 原始共 914,936 B；按完整对象 SHA 去重后为 681,594 B，精确减少 233,342 B（25.50%）。可直接共享的是两套配置的第 3、4 级以及 sidecar1。

单套四级的节点为 431,244 B。以第一级为基底、其余使用相邻 `int8 + 逃逸` 的精确差分需要 500,733 B；以逐位置中位数为共享基底需要 611,525 B，均大于原始节点。四级节点两两平均绝对差为 20.627 至 66.351，完整 RGB 节点相同比例为 0% 至 3.10%，说明同一流水线中的不同级不是适合热解码的近邻表。

整套文件的离线压缩更有效：`default` 从 448,252 B 压到 zlib-9 的 233,100 B 或 xz-9 的 182,512 B；`max41` 分别为 232,872 B 和 182,360 B。该结果只说明包体可压缩，不说明运行时更快。

### 68 个既有最佳模型

输入沿用既有 `best-per-lut.csv` 选择的 68 个模型，其中 3 个 m17、65 个 m33，不重新拟合。原始 SLUT 共 7,340,492 B；组件 SHA 去重后为 7,157,288 B，只节省约 2.50%；整包 zlib-9 为 5,189,078 B。

精确最小生成树差分中，m17 为 44,217 B 对 44,217 B，节省 0%；m33 为 6,781,390 B 对 7,007,715 B，节省 226,325 B（3.23%），且 64 条父边中只有 26 条选择位压缩残差，其余直接存原始 u8 更小。跨 LUT 差分收益不足以抵消运行时解码复杂度。

因此，推荐落地顺序是：**对象级精确去重 → 发布包压缩 → 加载时完整解压**；不推荐逐像素差分恢复。

## AVX2 候选与验证方法

基线是仓库当前 out-of-place direct 内核，即 NTA 软件预取配合 non-temporal 输出。四个候选均从同一源码派生且每次只改变一个维度：

| 候选 | 唯一变化 |
| --- | --- |
| `repo_no_prefetch` | 删除软件预取 |
| `repo_t0` | NTA 预取改为 T0 |
| `repo_cached` | non-temporal store 改普通对齐 store，并删除 `sfence` |
| `repo_t0_cached` | 同时采用 T0 与普通 store |

正确性使用完整 16,777,216 个 RGB8 输入，验证 10 个内核逐字节一致，全部通过，输出哈希为 `10007360481601617047`。性能输入为 `assets/photos/eval.txt` 的 100 张 1024×768 图片，共 78,643,200 像素、235,929,600 B；紧密 RGB 批次 SHA256 为 `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`。

每个候选在独立进程运行，先预热当前核与候选各一次，再执行 8 个循环并交替 ABBA/BAAB；每循环的两次基线与两次候选分别取均值。1 线程固定 CPU 0，4 线程固定 CPU 0/2/4/6。下表的配对比为 `候选时间 / 同循环基线时间`，小于 1 才表示候选较快。

原程序的 `median` 函数在 8 个样本时取排序后的第 5 项，即上中位数；不是第 4、5 项的平均。下表保持原始记录，范围是实测最小—最大，不是置信区间。发布时只澄清统计口径，不重写原始 JSON。

| 候选 | 线程 | 配对比上中位数 | 最小—最大 | 判断 |
| --- | ---: | ---: | ---: | --- |
| A/A：`repo_current` | 1 | 1.030 | 0.814—1.115 | 对照自身不稳定 |
| `repo_no_prefetch` | 1 | 1.018 | 0.913—1.147 | 无收益 |
| `repo_t0` | 1 | 1.000 | 0.903—1.351 | 无稳定收益 |
| `repo_cached` | 1 | 1.004 | 0.735—1.109 | 无稳定收益 |
| `repo_t0_cached` | 1 | 1.016 | 0.902—1.067 | 无收益 |
| A/A：`repo_current` | 4 | 0.890 | 0.653—1.220 | 对照自身不稳定 |
| `repo_no_prefetch` | 4 | 1.186 | 0.746—1.637 | 方向上较差 |
| `repo_t0` | 4 | 1.047 | 0.554—1.144 | 无稳定收益 |
| `repo_cached` | 4 | 1.194 | 0.768—2.139 | 方向上较差 |
| `repo_t0_cached` | 4 | 0.922 | 0.756—1.535 | 区间跨 1，不合格 |

A/A 的范围已经远超 ±3%，且所有候选的范围跨过 1 或存在明显反例。因此本机筛查中**没有候选获得性能资格**，不能用表中的上中位数宣称加速。保留基线 NTA + non-temporal store；本轮不足以给候选排序，T0 可以保留为未来受控复测选项，但没有证据证明它是唯一值得复测的候选。

## 实际环境

- 操作系统：`Windows-11-10.0.26200-SP0`，x86-64。
- CPU：Intel Core Ultra 5 125H；系统暴露 18 个逻辑处理器。
- 编译器：MSYS2 MinGW `g++.exe 14.2.0`。
- 参数：`-O3 -DNDEBUG -std=c++17 -mavx2 -mbmi -mtune=skylake -fopenmp`。
- 后端：CPU-only AVX2/BMI；未调用 GPU/NPU，也未启用 AVX-512。

本机并非目标 Xeon Gold 6140，共享 Windows 环境还出现明显调度或频率噪声。因此这里只能确认功能正确性并淘汰明显无希望的方向，不能替代目标服务器上的性能门禁。

## 主要文件与证据

- `scripts/analyze_joint_lut_storage.py`：分析两套四级模型的对象复用、级间相关性和精确差分容量。
- `scripts/analyze_lut_library_delta.py`：对 68 个既有最佳模型建立精确差分最小生成树并估算容量。
- `scripts/prepare_avx2_photo_batch.py`：从固定照片清单生成紧密 RGB8 批次及逐图哈希清单。
- `scripts/build_joint_avx2_benchmark.ps1`：以冻结参数链接基线、四个候选与独立微基准。
- `scripts/run_joint_avx2_benchmark.py`：顺序执行完整域验证和 ABBA 配对基准，保存全部周期原值。
- `experiments/joint-avx2-runtime/`：独立微基准及四个同源候选，不接入默认 runtime。
- `report/data/joint-lut-avx2-20261027/`：联合存储明细、完整 AVX2 原始周期和环境记录。

## 复现入口

输出目录必须不存在；路径按本机实际研究目录替换。以下入口依赖上游 `4a8b27f4f8b4403986bf53b71f01f8616b53327a` 的内核、头文件及模型，不能直接在仅含本 PR 的 `pipeline` 检出中全部运行；请先按[发布说明](../../report/data/joint-lut-avx2-20261027/publication.md)准备依赖。

```powershell
python scripts/analyze_joint_lut_storage.py --manifest data/p16-unified-models/manifest.json --output artifacts/joint-storage
python scripts/analyze_lut_library_delta.py --study D:/shenni/交大/Hackthon/flash-chroma/artifacts/local-lut-study/20261016 --output artifacts/library-storage
python scripts/prepare_avx2_photo_batch.py --list assets/photos/eval.txt --output artifacts/photo-batch
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_joint_avx2_benchmark.ps1 -Compiler C:/msys64/mingw64/bin/g++.exe -Output artifacts/joint-avx2/bench_direct_avx2.exe
python scripts/run_joint_avx2_benchmark.py --exe artifacts/joint-avx2/bench_direct_avx2.exe --photos artifacts/photo-batch/photos.rgb --compiler C:/msys64/mingw64/bin/g++.exe --output artifacts/avx2-result
```

构建脚本将基线 `experiments/skylake-andn-normal-runtime/andn_outplace/channel_avx2.cpp`、四个候选 TU 与 `bench_direct_avx2.cpp` 一同链接，并使用上列固定编译参数。

## 下一步建议与未完成事项

1. 实现“保持逐级语义”的联合拟合原型：冻结四级坐标，按末级输出误差选择少量跨级节点候选；先在 4 个代表 LUT 上做 m17/m33 对照，不直接替换正式模型。
2. 实现内容寻址包清单，先只复用字节完全相同的 SLUT/sidecar；增加加载后 SHA 核验。再评估 zlib 与 xz 的包体、一次性解压时间和峰值内存。
3. 在隔离负载、固定频率或目标 Xeon Gold 6140 上重跑当前核 A/A；只有 A/A 收敛到 ±3% 内才比较 T0。正式门禁应增加运行次数、报告中位数与离散度，并覆盖完整 runtime。
4. 本阶段没有重新计算色差、没有测量 runtime 创建/加载时间、峰值 RSS 或 Xeon 性能，也没有把实验候选接入公共代码；这些结论必须继续标为未覆盖。
