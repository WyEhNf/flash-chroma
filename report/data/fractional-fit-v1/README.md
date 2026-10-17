# 原轴表完整域拟合证据

[阶段报告](../../../docs/stages/2026-10-17-fractional-fit.md)。数值执行Git为`ff14d60`，四个新模型在完整验收前冻结；两个五选一均沿原条件回退历史，不改默认/冠军。保留原轴表改善两例平均精度，但Lomo仍有57图max退化、Velvia仍有最差单图p99退化。

- `plan.json`、`environment.json`、`photo-partition.json`：冻结方案、实际源/依赖/硬件/线程/二进制身份和60/20/20像素哈希。
- `results.json`：完整256³/100图、KKT、支撑下界、精确整数目标比较、选择失败及Q24证书；六个旧配置（每例三个）明确复用。
- `support-certificates.json`：四个新模型的权威Q16设计见证及固定三点必要界；证书失败不等于秩亏，见证不是精度保证。
- `case-summary.csv`、`photos-per-image.csv`、`photo-groups.csv`：10条配置、1000逐图（400新/600复用）、30分组。
- `photo-regressions.json`：相对历史及相同目标整数网格的完整逐图改善/持平/退化。
- `native-parity.json`：8份标量/AVX2回执，四个新模型与独立整数oracle完整流一致。
- `models-and-selection.zip`、`archive-index.json`：10个SLUT、2份原float64网格、4份冻结拟合记录及2份完整100图之前的选择，共18成员。
- `measured-source.zip`、`source-provenance.json`、`experiment.log`、`contract-tests.log`：21文件原字节与一次8/8合同日志；当前数值源码与执行字节相同。
- `guard-counterexamples.json`与`posthoc-source-v1.py`：首次后验数据及其原源码；`guard-counterexamples-v2.json`：使用版本化基线缓存恢复入口复核，同一81920色样本、80条逐图配对及32个反例全部一致。恢复缓存不重新拟合，源指纹分别保留。
- `fractional-fit-comparison.png`已目视检查；`integrity.json`绑定初始归档，后加README/诊断由`archive-audit.json`补充核对，不改写数值运行身份。

复现命令、合同日志命名及线程范围见阶段报告，入口不覆盖已有目录。原始完整表和输出流保留本地忽略缓存，可从模型恢复并核对SHA。恢复离线原float64网格后必须核对其生成轴表与SLUT权威表一致，不能把float32坐标静默当作原拟合坐标。

所有色差为RGB欧氏码值距离，非CIEDE2000；两个单级不是比赛四级成绩，照片均历史已观察，官方数据/Threshold未知，无性能/实板/SOTA或默认升级声明。

Agent：Codex

Operator：WyEhNf

Task：原权威Q16轴表下完整域支撑证明与误差归因

Status：阶段实现与验收完成，尾部问题保留，Draft待审查
