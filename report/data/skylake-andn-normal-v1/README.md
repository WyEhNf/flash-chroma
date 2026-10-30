# 修订80：普通写组合未达到四线程三倍

[阶段说明/复现](../../../docs/stages/2026-10-21-skylake-andn-normal.md)。有效多线程原地使用独立ANDN32/T0普通写TU，单线程原地及分离保留79两个pair48对象，CPU缺BMI1仍原线性回退。模型和表不变，完整RGB8及新增跨两块64实际偏移通过。

首次正式纯apply单/四线程3.152974/2.122713倍，两档A/A有效，唯一失败为四线程纯apply；确认系列/调用0，不重跑或采用默认。原始1920内轮独立复算一致，48次预热和48次批末SHA并非每内轮独立SHA。

`manifest.json`标识133份原件，不包含后补本文、远端快照和摘要自身。构建库/命令/源码ZIP与中间产物ZIP、静态六区段及独立对象审计、全域/边界/新增64实际偏移、全部长批次/绑定/THP/源/输出记录均保留；静态初版未执行，正式v2补多ELF节字节核对；独立初版static次数误判及范围修正v2均保留，未改源/对象。`confirmation-decision.json`绑定首次失败结果，`archive.py`和`audit.json`从原始数组复算，不新增像素或计时。

原生环境Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu Linux6.18.33.2 / GCC15.2 / Python3.14.4标准库，通用AVX2、Skylake调优，三个专用TU增加BMI1。归档为Windows11/Anaconda Python3.13.12标准库；独立审计解释器详见回执。模型与大流从PR73依赖按SHA恢复，原件目录不得覆盖。不是实际Skylake或缺BMI1硬件验证，未锁频控温或证明宿主独占。

远端68份PR正文与前67份比较仅新增74，其余相同；74完整意见刷新为空，updated检索无新PR/issue，原件记录见remote-snapshot.json。Discussion刷新接口缺口保留，不合并或关闭事项。官方派生表许可/预算/Threshold及整体三倍仍待验证。
