# Velvia插值误差归因

Agent：Codex；Operator：WyEhNf；有界诊断完成。

同节点直接换三线性使均匀/照片探针mean分别增加20.17%/43.40%；精确源浮点顶点可显著修复旧最坏16色，却使一般探针mean/p99变差。最坏单元节点偏差约45.92码值，超出纯RGB8量化，优先追查共享节点与目标折中，不直接扩展高阶插值。

[完整中文报告及测试环境/目的/复现命令](../../report/data/velvia-interpolation-diagnosis-v1/report.md)。仅两个固定16384探针及旧最坏16色，不新拟合、生成模型或全域/百图验收，不宣称独立新oracle或SOTA。原模型与默认均保持。
