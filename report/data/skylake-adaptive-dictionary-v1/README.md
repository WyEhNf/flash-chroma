# 修订72双表示实验原始档案

Agent：Codex /root；Operator：WyEhNf；Status：In Progress。完整RGB8逐字节通过；首次受控性能系列失败，单线程A/A控制也失败，未执行独立确认。整体三倍目标尚未完成。

`manifest.json`按长度/SHA绑定107份原件，`audit.json`从原始数组独立复算1920内轮、四worker配对比及控制门槛。`archive.py`只归档和复算，不执行原生像素或性能。不要覆盖已有目录重新运行归档。

`skylake-adaptive-dictionary-linux-build-v1`包含构建、编译参数、源码ZIP和本机库，中间文件另压缩；`skylake-adaptive-dictionary-linux-full-v1`保存完整色域及双表检查；`skylake-adaptive-dictionary-long-perf-v1`保存全部首轮数组、批次、空闲及真实团队/THP记录。`confirmation-decision.json`绑定原失败结果，新增确认调用0。`static-asm.zip`保存两种像素对象反汇编。

`palette-bank-readonly`保存离线分析源、完整结果及导出身份，`tables.zip`含原16MiB ID表和调色板。恢复为`artifacts/skylake-palette-bank-readonly-v1/`原路径后可按原脚本复算。没有原生照片映射或性能调用，不能当作速度成绩。

模型可按原计划从`report/data/skylake-palette-v1/fixed-models.zip`恢复；照片及大oracle流按冻结SHA恢复。环境、测试目的、计时口径、复现和已知限制见[阶段说明](../../../docs/stages/2026-10-21-skylake-adaptive-dictionary.md)。本机为Ryzen9/WSL2，未验证Skylake。后补本README、远端回执和阶段说明不在107原件清单内。
