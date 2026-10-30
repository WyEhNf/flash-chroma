# 187正式性能负例

代理 `/root/tail`，操作者为当前会话用户。固定三控制、四进程、每组预热1次后5次计时，全部100图与4096全满命中压力集、原地/真分离、1/4线程均覆盖。192组的末work和源只读SHA全过，没有追加重跑或删除worker。

百图主集有效最劣187on/同187off为85.5366%，只过80档；dense有效最劣187on/冻结87为18.4527%，严格低50%，因此整体拒绝，不切默认。96项A/A中8项失败，涉及5个dense单线程场景，原件全部保留；dense四线程各场景A/A全过仍严重退化，不能用不确定场拯救有效负例。

`identity.json`和`plan.json`保存执行前冻结身份；`raw-workers.zip`保留每组5次原始时长、末work哈希、源只读检查和UTC时间，`results.json`保留完整正式汇总。`independent-check.json`不导入原汇总器，678项独立检查通过；`derived-first-check.json`及`audit-note.json`保留辅助分表偶数样本中位数修复，正式raw、原summary与底线判定未改、未重跑计时。

`quality-stage-manifest.json`和`frozen-model.json`绑定已验收187库、原模型和κ3数学输出；`source.zip`保存实际计时/复核代码与原生计时器。原187逻辑句柄相同不代表每线程约24KB命中记录栈免费；RSS/冷首性能未测。新basis非stock SLUT，题面许可未知，RGB8邻接跳变代价仍有效。详见[阶段文档](../../../docs/stages/2026-10-24-velvia-bubble-perf.md)。
