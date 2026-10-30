# 字典、载荷与非临时输出：31—37证据

[阶段报告](../../../docs/stages/2026-10-20-skylake-load-packing.md)列出全部结果、协议变化及限制。**整体三倍目标未完成**；37仅四线程真实输出达到3.0283倍，纯映射仍未达三倍。七版完整RGB8逐字节相同，公共默认未改。

- 原名目录保存全部build/full/static/perf源ZIP、二进制/对象及轮次。`performance-audit.json`独立复算完整560轮旧模式＋560轮真实输出。
- 34 v1团队检查失败，三个完整worker共120轮部分模式记录全部保留，不参与接受判定。34 v2四份完整回执后父汇总NameError，原源不改，`offline-results-v1.json`独立复算，不重测。未来复现使用修复入口与v3-recipe；本阶段v3未运行。
- 34—37有保护页及只读源测试；37另有全部64种目标偏移1280比较和512次保护页比较。原始汇编中两入口共12条非临时写、2条SFENCE。
- `pmu-profile`保存8项一次性用户态组计数，不是新的墙钟成绩；`pmu-probe`、`pinned-openmp`和两项停止的只读结构分析分别保存。没有更改权限、缓解或全局配置。
- `manifest.json`覆盖235份原始文件，不自包含，不含后补说明/审计。23份源快照/1687项成员及133项二进制成员通过归档审计。
- `remote-snapshot.zip`保存41PR及相关完整意见；`construction-and-validation-generators.zip`用于溯源，不能在现工作树重跑覆盖冻结策略。旧源实际字节见measured-source.zip。

小模型复用旧固定模型包，两个50MB完整域流与235MB照片流按同SHA恢复，本目录不是无数据独立运行包。Skylake实机、官方预算与许可待验收。

```sh
python3 -I -S scripts/audit_skylake_load_packing_archive.py --archive report/data/skylake-load-packing-v1 --output artifacts/new-archive-audit.json
```
