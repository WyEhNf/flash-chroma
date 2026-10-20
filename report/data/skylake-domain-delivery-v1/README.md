# 完整域证书阶段的交付核对

[阶段说明](../../../docs/stages/2026-10-20-skylake-domain-proof.md)与[本机验收](../skylake-domain-isolated-v1/README.md)、[WSL移植](../skylake-domain-server-v2/README.md)分别报告已运行范围。本目录仅做协作与静态交付，不新增像素或性能调用。

`remote-snapshot.zip`完整刷新37个PR、2个独立issue、2个Discussion、113组REST分页与所有审查线程。与上一阶段已读快照的差异只有本任务PR43自身先前正文/头更新，没有新外部意见；修复337a3dd、876e15b8、397cc367均为当前祖先。官方规则/Skylake入口与issue8仍未完成，不以本机通过关闭问题。

`static-check.json`及`static-check-details.zip`绑定第一次全部暂存原字节/本轮文档链接检查；`combined-check.json`及`combined-check-details.zip`为加入本说明后重新核对的完整回执，二者为避免自身哈希循环不列入先前manifest，由Git单独跟踪。

实际Windows11 / Python3.12.14 / Git，编译器/后端/线程不适用。只推送工作分支并更新Draft PR43，不merge、不改变公共默认/核心/CLI/GUI/C99/AGENTS.md。静态通过不替代新提交CI；CI也不替代已单独记录的研究库和真正Skylake测试。
