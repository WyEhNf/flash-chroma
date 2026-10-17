# 逐图上限与局部节点修复证据

对应[阶段报告](../../../docs/stages/2026-10-17-tail-repair.md)。本阶段固定Cinema四级m33链，修复PR14相对原始基线的四张图max回归，不把结果外推未知图片/LUT。

- `plan.json`、`run.json`：预先冻结计划和原始实测身份。实测数值Git为71fdfcc，研究映射4线程，BLAS/OMP单线程，原生验收单线程。
- `inventory.json`：60张训练图的4,668,485种颜色及最严逐图max平方上限的哈希；来源是父阶段已核验的原始基线，不是官方Threshold。
- `selection.json`、`fixed-guards.json`、`round1.json`：全部14个初始训练超限颜色、邻域339色、5次节点选择、固定保护预算、1轮全训练颜色分离至0。抽样mean的0.5%保护不能当作全色域保证。
- `training-violations.json`：完整14色RGB、参考输出、整数上限、旧误差平方及修复输出；四张旧回归图的完整结果与训练全域扫描交叉核对。
- `move-footprint.json`：在冻结65536色保护集上重放5步，单次改变208–1505种最终RGB，解释局部修复的外溢及均值成本；没有重新产生候选。
- `case-summary.csv`、`photos-per-image.csv`、`photo-split-summary.csv`、`comparisons.json`：三配置摘要、300条逐图、9条分组及正负结果。原始/PR14共200条是历史复用，本轮100条才是新执行。所有100图四项指标都优于原始基线；相对PR14则有80图mean、9图max变差。
- `node-moves.csv`、`model-provenance.json`：改动5节点/9分量，第一/四级和全部轴表不变，父ZIP及输入模型哈希可核对。
- `models-and-counterexamples.zip`、`archive-index.json`：7个成员（4张新SLUT、选择文件、模型来源、14色反例），约223KB。旧候选库仍从 `report/data/joint-box-v1/` 读取，不重复保存。
- `native-parity.json`：本轮完整256³的标量/AVX2/C99三条流，对独立整数oracle均0字节差异；历史两个配置的原生证据留在父阶段，不算新执行。
- `measured-source.zip`、`source-provenance.json`：13份源码原始字节全部匹配实测run身份。当前runner后来增加图片清单前置核验及自动快照，与实测旧版本分开记录，未重新标记旧run为新代码执行。重建新runner会产生新身份。
- `contract.log`：最初3项合同通过；`preflight-contract.log`：归档发现图片清单绑定缺口后，新增定向回归1项通过。没有重跑数值研究。
- `experiment.log`、`tail-repair.png`、`integrity.json`：原始单批日志、已目视检查的科学图和归档哈希。NumPy可选PyYAML警告保留原样。

完整色域mean/RMS/p99/max为 **1.290333/1.689251/4.690416/8.774964**，100图mean为 **1.041300**。相比PR14，完整色域mean上升0.613493%，照片mean上升0.398609%，不隐去这一代价；原始基线分别为2.022233/1.759132。全部误差为逐像素RGB欧氏码值距离。

可按阶段报告在新输出目录重建；本轮新模型按 `repaired-stage1.slut` 到 `repaired-stage4.slut` 顺序交给现有 `lutlab.runtime.apply` / `cube`。完整输出SHA为 `ad2b976bfa8a4e09933be53d8467fbeeb0cef03b5c0a3d1ac4574685a71eb696`。换构建后必须保存新的二进制/环境回执，不能复用本轮执行身份。源码快照不含图片、LUT、依赖环境或凭据。

官方数据、阈值及评分未知，未更换默认或正式冠军，也未执行性能扫描或实板测试。

Agent：Codex

Operator：WyEhNf

Task：尾部修复阶段证据

Status：阶段归档完成，候选待审查
