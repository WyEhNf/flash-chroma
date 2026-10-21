# 六案例逐TID诊断档案

Agent：Codex /root；Operator：WyEhNf；Status：In Progress。整体三倍目标尚未完成，本档案不包含新的吞吐验收。

`manifest.json`绑定42份原件；`raw/`包含六案例全部事件原始读取、逐TID派生值、空闲/THP和实际团队、源码ZIP。`libraries/`保留同SHA原65及驱动二进制，未重编译。`normalized-dictionary-readonly/`保存固定64字节块归一化的离线分析，没有新原生候选。

`archive.py`不加载库，独立解码24组六事件字节及参与线程求和、名义像素、输出与THP，结果在`audit.json`。不重复运行到已有目录。README、审计本身及后补远端回执不在42份原件清单内。

实际环境、复现、事件来源及含barrier/收尾等限制见[阶段说明](../../../docs/stages/2026-10-21-skylake-four-thread-diagnostic.md)。模型、照片和原65完整域由冻结计划同SHA恢复。不可据不同输入的周期比声称吞吐提速或Skylake性能。
