# 描述符快照的静态研究证据

本候选在静态阶段停止，没有运行像素、整数正确性或性能测试。指令减少而栈访存增加，MCA两个估计方向不一致，不采用。[阶段说明](../../../docs/stages/2026-10-20-skylake-snapshot.md)列出目的、环境及限制。

`build.json`与`build-log.json`保存同次构建和ISA核对；`measured-source.zip`保存冻结源码；`binaries-and-core.zip`保存未进入运行验收的两库及核心/依赖。`assembly-and-mca.zip`保留两份完整objdump、提取的热循环和MCA完整stdout/stderr；`analysis.json`保存提取范围、原始计数、工具/输入身份和停止决定。

MCA21.1.0显式以Skylake模型模拟，实际宿主仍为AMD。没有真实缓存/微码/GDS建模，不能将模拟周期当成服务器成绩。`manifest.json`记录本目录原始字节，不修改此前任何运行或计时证据。
