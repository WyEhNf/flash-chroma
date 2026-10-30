# 三倍目标的24—30研究档案

[阶段报告](../../../docs/stages/2026-10-20-skylake-threefold.md)解释方法、环境、完整结果和限制。**三倍目标未完成，七个候选均未通过性能门槛**；固定模型完整RGB8输出全部保持相同，公共默认和已验23未改。

- 每个原名目录保存build/full/contracts/static/perf回执、测量源ZIP、二进制/对象ZIP与全部轮次。七次独立四进程比较共560轮旧接口；28—30另有240轮真实source→destination接口，不覆盖旧时间。
- `performance-audit.json`是独立标准库复算，未加载库或重新计时。`archive-audit.json`核对235份原始文件、31份源快照/2062项成员及121项二进制成员。
- `structure-profile`与`tile-locality`为只读结构/缓存行分析，不是性能结果；Windows大页探测没有修改权限。
- `construction-and-validation-generators.zip`保存生成过程，`remote-snapshot.zip`保存40PR、相关完整评论/review/Discussion快照，递归去除API临时克隆元数据字段。
- `manifest.json`只覆盖235份原始文件，不自包含，不含后补说明和审计。`input-reuse.json`声明大流未打包；小模型复用上一阶段固定模型包，完整域与235MB照片流按计划同SHA恢复。

旧源换行字节以各measured-source.zip为准，不得修改冻结SHA来适配Git归一化。移机要新建build/full/perf策略及目录。Skylake实机与官方许可均未验收。

```sh
python3 -I -S scripts/audit_skylake_threefold_archive.py --archive report/data/skylake-threefold-v1 --output artifacts/new-threefold-archive-audit.json
```
