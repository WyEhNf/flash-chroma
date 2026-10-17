# 第16题扩展数据与逐case策略账本

当前跨版本总入口见[合并数据集 v1](../problem16-unified-v1/README.md)。本目录的 200 个源 case、320 张合成图及原矩阵仍保持各自定义；新增压力输入通过统一索引关联，不覆盖这里的 catalog 或账本。

定义为200个四级完整LUT case、320张标准合成RGB8图像、23个输入颜色探针集合；另有独立的格式边界/拒绝夹具。是否完成物化与完整校验，以`artifacts/r28-corpus/build.json`的`complete`和`data/corpus-v1/inspection.json`为准，不能只凭catalog的条目数认定完成。

2026-10-16首批构建与完整审计已通过：200条链各检查256³颜色，320张图像内容唯一；去重完整对象47,714,402,304字节。200条链有199个不同最终变换，重复项是两条回归用轴置换链；12条最终输出常量，已单独标记。留出case没有与开发/校准case完全相同的最终变换。这些是数据质量结果，尚不代表新case策略精度或速度达标。

- [catalog.json](catalog.json)：源算子参数、强度、种子、划分、分类标签及结构期望；冻结后不覆盖修改。
- [strategy-plan.json](strategy-plan.json)：9策略×3尺寸×200case的5400候选预声明矩阵；当前状态不能当作完成测试。
- [casebook/index.json](casebook/index.json)：每个case的状态、mean/max最优及Pareto；未测项保持空白。
- [casebook/summary.json](casebook/summary.json)：按类型、强度与划分统计的实际测量覆盖。
- [invalid-formats.json](invalid-formats.json)：格式边界夹具的固定期望定义；实际拒绝结果见[R32](../../docs/r32-format-contract.md)，不混入精度通过率。
- [strategy-extension-r36.json](strategy-extension-r36.json)：200个原case新增4策略、3个容量控制比较全部13策略，共2517项；两计划合计7917项。
- [R42完整类别训练快照](../../docs/r42-training-comparison.md)：只对已完成两个seed全13策略对照的类别排名，并保留全部并列项；尚非留出sweet zone。
- [完整计划与验证口径](../../docs/r28-corpus-program.md)。

原始LUT、真值、图像和探针均在被Git忽略的`data/corpus-v1/`。LUT按内容SHA256去重，case目录用同卷硬链接，不复制为第二份数据；变更模型、原始对象或证据后必须重新检查。图像标签明确为synthetic，肤色/天空等名称只是构造的颜色分布，不代表已收录真实照片。

```powershell
$env:PYTHONPATH = 'python;artifacts/r18-tools/python'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
python -m lutlab corpus catalog
python -m lutlab corpus build
python -m lutlab casebook init
python -m lutlab casebook import-history
python -m lutlab casebook audit
```

R29原始脚本保留为历史数值版本。主工作区的拟合源码已经扩展，继续原矩阵应使用保存的源映像。R50按case分片执行器通过集中验证后，已受控接替旧R38工作进程，不能把演进中的主拟合代码直接当作原数值版本恢复。当前控制器正在运行时，不重复启动，先核实实际进程与单写者锁。

```powershell
$env:JSHC_FULL_FIT_LIB = (Resolve-Path build-fit/libjshc_full_fit.dll).Path
python scripts/r50_case_scheduler.py --source-root artifacts/r29-frozen-source/19c69a6a7554b9920301 --jobs 4
# 只读检查四个训练阶段缺失项，不冻结，不读取留出输出：
python scripts/r41_freeze_combined_rules.py --inspect-only
```

R50控制器最多启动四个普通case进程，各自使用隔离工作账本，唯一父进程导入总账本；不创建subagent。分母不随分片缩小，仅完整原始键集可宣告阶段完成。两套开发/校准均完成并冻结基线与联合规则之前，不运行任何留出输出。工作区锁只有核实实际进程终止后才能清理；[调度验证与迁移](../../docs/r50-case-shards-and-canonical-import.md)、[规则冻结步骤](../../docs/r41-matrix-resume.md)。

R36扩展的开发720项、校准720项及回归357项已全部完成，控制器`459d1fe72535`正常退出。其余720项为尚未启动的留出项；因此不能称2517项扩展矩阵全部完成。R29基线仍在执行，联合规则尚未冻结。

旧R20-R27的70份不同实际验收记录已导入，涵盖9个源；导入不重复像素测试。全色mean、尾部max和容量是不同目标，没有一张通用“所有指标最优”表；历史图集与新图集的资格按清单哈希分开，旧图集通过不自动赋予新图集通过。

扩充时追加新catalog版本，保留旧case ID、完整源内容哈希和分组信息；新case默认为unmeasured。新策略采用新的对照epoch，不改写已经发生的失败或旧版胜出结果。

方法相关的后续标签单独版本化：`annotations/r51-solver-boundaries.json`保存五配置的CG预算边界、续算恢复和旧字节保持标签，绑定源、模型及成功阶段SHA。原catalog不改；恢复拟合不等于预测精度合格。该随机对抗源的mean与max/p99最优分别保留adaptive_bins/m17、adaptive_bins/m25。[测试、指标及部署](../../docs/r51-bounded-cg-recovery.md)。

`benchmark100`混合了各图像划分，专门作为固定吞吐/格式合同队列，不把它称作独立的精度留出图片集。源case划分与图像划分是两种不同对象；类别规则只从开发/校准源的完整色域结果形成。
