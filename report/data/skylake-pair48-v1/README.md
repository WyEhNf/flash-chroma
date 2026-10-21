# 修订79：完整精度通过，四线程三倍未通过

[阶段说明](../../../docs/stages/2026-10-21-skylake-pair48-input.md)。唯一16MiB精确ID表不变，每对RGB24以一次64位ANDN读取，两独立BMI1 TU有CPU检测及原线性回退。完整RGB8与边界通过，首次正式纯apply单/四线程吞吐3.084902/2.353089倍，两档A/A有效；唯一失败是四线程纯apply，按冻结规则不执行确认，不重试或采用。

`manifest.json`记录124份原件，不包含后补本文、远端快照和复算摘要自身。`*-linux-build-v1`保存库/构建命令及源码ZIP，中间产物另ZIP；`*-static-v1`保留初次入口导入失败、死mask误判初件/正式v2、完整反汇编及独立审计；`*-preflight-v1`保存源码/检查/策略生成器、协议归一审计及交付辅助失败记录。排除临时Python缓存。源码/对象和门槛未因检查器修正改变。

`*-linux-full-v1`保存16M物理表与24配置完整RGB8、有限/guard/align/拒绝证据；`*-long-perf-v1`保存4串行新进程的全部1920内轮、实际绑定/THP及48预热/批末SHA；`confirmation-decision.json`绑定首次结果，新增确认0。`archive.py`从原始数组独立复算，`audit.json`记录全部进程比、中位和控制，不新增像素或计时。

原始运行环境Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu Linux6.18.33.2 / GCC15.2 / Python3.14.4标准库；泛型AVX2、Skylake调优，仅两个ANDN TU加BMI1。只读归档与交付字节审计为Windows11/Anaconda Python3.13.12；独立对象审计解释器详见其回执。未在真实Skylake或缺BMI1机器执行，未锁频控温。

恢复固定模型用PR71及`report/data/skylake-palette-v1/fixed-models.zip`，大流和单级oracle按计划SHA恢复；原件目录拒绝覆盖。`remote-snapshot.json`记录66份PR全文核对只新增72、其余65份与前阶段原件一致及72正文/完整意见刷新；Discussion无法读取的缺口保留，不合并或关闭事项。官方许可/预算/Threshold及总体三倍仍待验证。
