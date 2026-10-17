# R45：三个代表源的实际图像路径与精度边界

本轮从 R36 已完成训练结果中选取前置量化 strong/m25，以及逐轴量化 medium/m25 的两个训练 seed。只核验新的图像／后端路径，没有重新拟合，也没有测速或读取留出输出。最终阶段 `artifacts/r45-representative-images/stage.json` 的路径一致性验收通过；其中一个源没有通过本地示例精度门槛，二者分开报告。

## 实际执行范围

- 三个源各在结构化 AVX2 CPU 和 CUDA 上执行完整 256³ 色域，共 6 个输出流，均与此前 R36 同模型的完整输出 SHA256 相同。
- 三个源各在 CPU/CUDA 实际处理固定 100 图队列，共 600 次标准图像执行；每张输出均核对完整色域映射，两个后端输出逐字节一致。
- 每源另执行 5 张已知 Kodak 自然照片，CPU/CUDA 与独立 C99 的优化／通用路径一致，共 60 次照片执行。不把这些已知照片称为新家族盲测。

CPU 使用 R35 的 `tetra_structured_avx2`，CUDA 使用 R32 格式门禁版本的 `cuda_q16_fused4`。C99 照片调用使用此前已验证的独立库；本轮没有新增独立 C99 的完整色域执行证明。原始源链、真值、模型、二进制、图片与执行代码均绑定哈希。

## 逐源结果

误差为 RGB 欧氏距离，mean 不是 CIE Lab ΔE。阈值 2 仅是此前沿用的本地示例，判定为完整色域 mean<2 且全部 100 图各自 mean<2，官方数据／阈值仍未取得。

| 源／策略／m | 完整色域 mean | 完整色域 max | 100 图最差 mean | 本地示例精度门槛 |
| --- | ---: | ---: | ---: | --- |
| quantize_early strong seed 0／reachable_bins／25 | 0 | 0 | 0 | 通过 |
| axis_posterize medium seed 0／lookahead_bins／25 | 0 | 0 | 0 | 通过 |
| axis_posterize medium seed 1／lookahead_bins／25 | 4.244875 | 21.377558 | 14.038200 | 未通过 |

第三个源的改善仍然成立：其完整色域 mean 原为 8.563340，经前瞻降到 4.244875；但改善不等于达标。CPU/CUDA/C99 一致证明它们计算相同模型，不能消除模型本身的近似误差。

两个 axis_posterize seed 的类别平均是 2.122438，既不能赋给任一源，也不能拿来替代逐图最大 mean。这正是保留逐源与逐图边界、并等待未知源留出评估的原因。

最初的两源队列已经完成后，逐 seed 分析明确了 axis_posterize 的差异，因此追加 seed 1 作为边界资格检查。原两源成功报告和驱动保留在 `completed-before-append/`；追加核验旧输入、模型与凭据后只执行新源，未重复先前通过的像素测试。

## 总账本导入状态

三个归一化观测已在独立资格账本通过完整导入检查，保存其内容寻址 ID；两个零误差源获得该固定图集的本地示例资格，失败源仍保留实测记录。R38 当前持有总账本单写者锁，所以本轮没有并发写入总账本，也不声称三个图像资格已经在总账本发布。

当前模型质量最优仍由正在运行的总账本维护；这三条新记录增加实际图像路径资格，不改变已经测量过的同模型全色域指标。`pending-canonical-import.json` 与最终阶段中的 `pending_canonical_import` 保存待导入记录。控制器结束并释放锁后执行：

```powershell
python scripts/r46_import_qualifications.py
```

以上是 R45 结束时的待导入状态。2026-10-16 的 R50 受控迁移间隙，R46 已实际导入本轮 3 条记录及 R47 的 42 条记录，45 条均通过，总账本当时为 4,129 条；失败的图像精度记录也保留。凭据为`artifacts/r46-qualified-import/4e4dac36d1b6/stage.json`，没有重复像素测试。[后续归并与续跑](r50-case-shards-and-canonical-import.md)；[本轮原始归档与逐文件索引](../report/data/r45/README.md)。
