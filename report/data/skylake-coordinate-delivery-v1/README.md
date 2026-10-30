# 坐标与局部性阶段交付核对

[阶段说明](../../../docs/stages/2026-10-20-skylake-coordinate-locality.md)与[原始证据](../skylake-coordinate-locality-v1/README.md)另列三项结构资格及相同对象调度结论。本目录仅检查协作与交付，不执行数值、拟合或性能。

`remote-snapshot.zip`完整读取37个PR、2个独立issue、2个Discussion、113组REST分页及全部审查线程；与上一轮已读快照比较，只有本任务PR43先前已核对的正文/头更新，无新外部意见。关联修复337a3dd、876e15b8、397cc367均为当前祖先；官方规则/服务器与issue8未完成状态保留。

`static-check.json`及`static-check-details.zip`保存第一次暂存原字节与文档链接核对；完整重复明细压缩保存，摘要绑定其SHA。`combined-check.json`及`combined-check-details.zip`在本交付说明加入后核对全部暂存档案，二者为避免自身哈希循环不列入先前manifest，但本身由Git原字节跟踪。

实际Windows11 / Python3.12.14 / Git；编译器、后端与线程不适用。静态交付通过不构成新运行时/质量/性能通过，也不代替新提交CI。只推送研究分支并更新Draft PR43，不merge、不关闭issue、不改变公共默认或AGENTS.md。
