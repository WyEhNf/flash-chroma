# 查表等待与59固定组合原始档案

本阶段59的完整RGB8输出无差异，单线程周期筛查失败；整体三倍目标未完成。

- [阶段说明](../../../docs/stages/2026-10-21-skylake-lookup-overlap.md)：变更、数据、环境、结果和限制。
- [原始文件清单](manifest.json)：35份文件的大小和SHA；后补报告与协作记录不包含在原清单。
- [独立复核](independent-audit.json)：源码、完整域、PMU门槛与诊断的离线核对。
- [协作记录](remote-check.json)：全量分页及相关事项状态；原始快照保存在`remote-snapshot.zip`。
- `diagnostic-generators.zip`保存只读布局扫描及冻结诊断策略生成器，`candidate-binaries-and-objects.zip`保存本机库和对象；大照片和模型复用旧同SHA资料。

原始候选与参考构建、实汇编、完整域、计数及六事件诊断均在本目录对应子目录。Ubuntu本机二进制仅用于复核，不代替目标Skylake重编译。没有新墙钟成绩。
