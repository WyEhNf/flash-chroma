# 精确ROM内存阶段证据

Agent：Codex `/root/memory`；Operator：本会话项目用户。阶段说明见[六档研究](../../../docs/stages/2026-10-23-memory-rom-tiers.md)。

`build.json`记录实际命令、编译器/源/库/静态核心SHA；`export.json`记录5容量文件大小、完整230色及逻辑表SHA；`full.json`为15个完整RGB8配置和3850个有限合同；`contract.json`为304个保护页/非对齐对照和23项拒绝。`performance.json`及`performance-raw/`保留四新进程全部轮次、A/A控制、各独立RSS新进程读数。`measured-source.zip`保存包括实际生成AVX2源的测量版本，`measured-libraries.zip`保存实际候选、78/80对照及四个GCC依赖。`failed-build-v1.json`和`rejected-export-v1.json`保留未通过版本，不作为有效结果。

`manifest.json`绑定归档时28份主要文件；两份失败原件、此README和阶段说明后补，不冒充其原始清单成员。没有新执行数值/性能或重算原始轮次。大ROM与照片不入库，按阶段命令从既有冻结模型新建独立目录复现，模型与逻辑SHA不变；不能覆盖已有证据目录。计时以保存的脚本/库身份为准，后续可移植性修正不改变本次原件。
