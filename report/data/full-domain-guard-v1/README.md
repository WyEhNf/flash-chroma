# 完整域保护与双节点前瞻证据

对应[阶段报告](../../../docs/stages/2026-10-17-full-domain-guard.md)。固定同一Cinema四级m33链；全部误差为RGB欧氏码值距离。保留两个事先冻结时期，不把单节点失败伪装成通过。

- `single/`：a7022df单节点阶段，14个训练超限颜色降到1个，完整域预算通过但训练约束不可行，没有进入完整100图/原生终验。12份保存的预算结论（包含拒绝及最终摘要）被标准库独立复算一致。
- `joint/`：071cc10双节点阶段，只重放单节点已冻结4步，不恢复1245项搜索；同一PR14完整域参考/预算不变。286对提案中首个通过者修复最后一色，完整4,668,485种训练色约束通过，随后完成一次完整256³、100图和原生终验。10份预算结论独立复算一致，不代表10个合格模型。
- 两个时期各含计划、运行身份、实测源码ZIP、源码差异说明、全域证书、旧PR15负对照、选择文件、原始日志和合同日志。单节点14份、联合15份实测源均逐文件匹配各自run，后续联合扩展/日志修补不重新标记历史运行版本。
- `case-summary.csv`、`photos-per-image.csv`、`photo-split-summary.csv`、`comparisons.json`：4配置摘要、400条逐图（300历史复用、100新执行）、12条分组及完整正负结果。
- `image-regressions.csv`：40条相对PR14/PR15的逐图退化事实，列出图片、分组、指标和前后值，供后续误差研究使用；不把整体mean下降当作每图非退化。
- `joint-counterfactual.json`：唯一残余RGB的主节点/帮手/联合独立整数重放；主节点修复局部，帮手在此色无影响，整对却能保持/改善全域代价。帮手单独的完整域收益没有另测，不假定可加性。
- `model-provenance.json`、`models-and-checkpoints.zip`、`archive-index.json`：11个ZIP成员，包括4张单节点检查点模型、4张新模型，以及重放所需的单节点run/selection/full-domain三个JSON。相对PR14共变更6节点/12分量，第一阶段和全部轴表不变。
- `native-parity.json`：本轮新赢家的标量/AVX2/C99完整流，对独立整数oracle与增量缓存SHA一致。旧配置证据继续留在父阶段，未算成新执行。
- `certificate-verifier.py`：标准库独立代数复核器的原始字节，可用Python `-I -S`运行，不需NumPy/Numba；只复算保存直方图的整数结论，实际模型/参考覆盖另由全域输出绑定。
- `full-domain-joint.png`、`integrity.json`：已目视检查的科学图和归档逐文件哈希。原始联合日志中的“接受0次节点选择”仅统计单节点；两个联合节点另完整写在round1.json，原日志保留不改，当前runner已修补计数。

新模型完整域mean/RMS/p99/max为 **1.277361/1.673274/4.690416/8.774964**，100图mean为 **1.033668**。整数上下界还证明完整域mean严格低于PR14，未放宽0.5%预算。相对原始基线，100图四项指标全都逐图改善；相对PR14仍有17图mean及9图max退化，相对PR15有4图p99及2图max退化，不宣称逐图支配所有旧方案。

## 复核与恢复

无需研究依赖即可复核两份完整域代数证书：

```powershell
python -I -S report/data/full-domain-guard-v1/certificate-verifier.py --input report/data/full-domain-guard-v1/single
python -I -S report/data/full-domain-guard-v1/certificate-verifier.py --input report/data/full-domain-guard-v1/joint
```

重建数值批次见阶段报告，必须使用新目录。第二批计划默认warm_start为 `artifacts/full-domain-guard-v1`；可先重建第一批，也可逐文件核对ZIP索引，将ZIP的`single/`七个成员恢复到该路径（4张SLUT、run.json、selection.json、full-domain.json），不需重跑单节点搜索。改变路径时另存新计划，不改写旧身份。

若重新整理报告，还需生成归档器所读的复核文件名：第一批以校验器 `--output <single目录>/certificate-verification-portable.json`，第二批以 `--output <joint目录>/certificate-verification.json`；已有记录不会覆盖。归档器的日志复制入口对应本阶段原始 `artifacts/full-domain-*.log`，迁移运行时可保持这些日志名或调整报告脚本并记录新来源。版本化证据本身不因重建而改写。

新模型按ZIP `joint/repaired-stage1.slut` 至stage4顺序交给现有 `lutlab.runtime.apply`/`cube`。完整输出SHA为 `2ad77e6a7ff6b4d761f0ced744bb236e4dc99c9313ca0c994fa243b7c31ea8e4`。缓存数组640,143,424字节、宿主进程OS峰值1,472,163,840字节均仅属于离线研究，不是映射运行时内存或性能结论。

官方数据/阈值、未知LUT泛化、实体硬件性能未验证；未替换默认/冠军，未执行全量矩阵或硬件加速研究。

Agent：Codex

Operator：WyEhNf

Task：完整域精度证书与双节点联合优化证据

Status：两个时期归档完成，候选待审查
