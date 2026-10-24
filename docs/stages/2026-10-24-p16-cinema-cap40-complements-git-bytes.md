# 补集封存Git检查器的机械V2说明

Agent：Codex `/root`；Operator：本会话用户。首次暂存区审核退出1，失败为原V1检查器直接要求只读AGENTS工作副本SHA等于Git blob SHA；现有Git文本属性已将该文件CRLF工作副本转换为LF提交内容。没有修改AGENTS，也没有数值、候选、源码或原证据错误。

V1检查器、冻结结果、13成员ZIP和manifest原样保留，失败退出与完整stderr保存到同目录`git-v1-failure.json`。V2只将AGENTS单项改为分别记录两个实际SHA并验证仅已有CRLF/LF转换后文本相等；ZIP内冻结工作副本仍核原SHA，其它执行源/结果/Git blob仍严格逐字节。V2源、本说明及失败原件各自额外核实际Git blob。

修正不重跑补集普查、有限合同、独立计数或任何native/CP/性能。V1失败不能称为通过。通过V2的INDEX与HEAD回执才是本次阶段交付门；只覆盖本阶段12个归档对象及3个额外对象，不能称全历史重新审核。
