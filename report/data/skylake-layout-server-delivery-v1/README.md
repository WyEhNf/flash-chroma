# 布局服务器入口阶段的交付核对

[阶段说明](../../../docs/stages/2026-10-20-skylake-layout-server.md)与[实际WSL证据](../skylake-layout-server-v2/README.md)记录包依赖修复、正确性及逐轮调度；没有新正式性能比较，不覆盖Windows失败。只更新研究分支及Draft PR43，不合并、不改默认或关闭issue。

`remote-snapshot.zip`保留37个PR、2个独立issue、2个Discussion和113组完整评论/review，分页完整；与已读全文相比仅上一轮自己更新PR43的正文和头变化，与回执一致，无新增外部意见。`remote-check.json`确认337a3dd、876e15b8、397cc367在当前历史中；公共实现相对PR42未变，issue8、正式Skylake与官方规则仍待办。

`static-check.json`为711个原字节blob及215个本地链接的首次通过摘要，完整回执放在details ZIP并保留SHA。`static-check-combined.json`及其details ZIP为加入本交付说明后的静态复核，末尾这两份元数据由Git跟踪且不加入先前清单的自哈希，避免循环。这些只是归档/链接检查，零新数值或性能调用，不能代替新头CI或Skylake测试。
