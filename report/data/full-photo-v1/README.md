# 完整域与照片等质量优化证据

[阶段报告](../../../docs/stages/2026-10-17-full-photo.md)。数值Git为`34b3daa`，一次固定四配置研究。Lomo整数混合模型改善完整域及完整100图的整体四项，但选择集尾部、64张图max仍退化，未提升默认；两个五选一均按冻结条件回退历史。

- `plan.json`、`environment.json`、`photo-partition.json`：冻结方案、实际环境、输入/二进制/源指纹、60/20/20与像素索引哈希。
- `results.json`：十配置完整指标、四个新拟合的KKT/精确整数目标变化、完整域Q24保护、选择条件与完整100图。三个旧配置/每例明确复用。
- `case-summary.csv`、`photos-per-image.csv`、`photo-groups.csv`：10配置、1000逐图（400新执行、600复用）、30分组；照片p99为最差单图p99。
- `fit-objectives.csv`：完整域与照片SSE的精确整数分量及交叉比较。针对未舍入Q16连续输出，不替代真实RGB8 mean/max。
- `native-parity.json`：四新模型的8条标量/AVX2完整流回执，均与独立整数oracle一致。单级不冒充C99四级验收。
- `photo-regressions.json`：全部逐图改善/持平/退化数量及最大退化图。
- `guard-counterexamples.json`：后验同81920个选择像素的只读诊断，完整流/指标复算一致，保存RGB、参考、旧/新输出、图片坐标及80条逐图配对。没有调参或反选模型。
- `models-and-selection.zip`、`archive-index.json`：10个SLUT、4份冻结模型拟合记录、两份完整域参考证书、两份完整照片之前的选择记录，共18成员。
- `measured-source.zip`、`source-provenance.json`、`experiment.log`：18文件实测原始字节和原日志，归档器另记源码SHA；后验解释器SHA在反例文件中。
- `full-photo-tradeoffs.png`已目视检查；`integrity.json`绑定初始归档，后加说明/诊断不冒充数值执行；`archive-audit.json`为整理后的补充字节与结构核对。

复现命令见阶段报告，输出目录不可覆盖。原始完整表、约300MB完整流保留本地忽略缓存，ZIP模型及源记录可重建；不存在父流缓存时入口会重建并核对旧SHA。没有官方数据/Threshold、性能、实板、未知LUT泛化或默认升级结论，全部误差为RGB欧氏码值距离。

Agent：Codex

Operator：WyEhNf

Task：完整域/照片等质量目标及网格候选联合选择

Status：集中实验、完整验收与负结果归档完成，候选未替换默认
