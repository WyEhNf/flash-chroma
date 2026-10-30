# final1 证据索引

本目录归档本次选型与服务器复测的原始小文件。实际运行的两份源码见 [submission/final1](../../../submission/final1)，分模块来源与原验收器见 [experiments/final1](../../../experiments/final1)，[阶段报告](../../../docs/stages/2026-10-30-final1.md)说明范围和限制。

- `selection.json`：选择规则、结果与历史覆盖范围。
- `evidence/comparable-history.json`：可比较历史候选及来源；别名/重复记录不是独立算法。
- `evidence/correctness.json`：全色域与 104 图原始数值。
- `evidence/timing.json`：五轮各 100 图耗时。
- `evidence/fixed-address-control.json`：固定地址的 ABBA 与 A/A，范围不同于实际 apply。
- `evidence/validation-receipt.json`：服务器编译、命令、输入/源码哈希、锁与 CPU 分配。
- `evidence/official-main.log`：独立编译正式 main 后的四图输出。
- `evidence/main-vs-delivery.diff`：相对上一交付 main 的四处控制参数变更。
- `evidence/package-source-manifest.json`：原始打包来源与两份最终源码哈希。
- `publish-receipt.json`：服务器发布后逐文件与 ZIP 核对回执。
- `collaboration.json`：相关 PR 正文、评论/审查线程、issue 和主题检索快照。
- `manifest.json`：本 PR 归档及源文件的仓库相对路径 SHA；`python scripts/verify_final1.py --staged` 可复核暂存字节。

`README.txt`、`release-manifest.json` 和 `original-reproduction` 是原服务器交付过程的原件。README.txt 的自带 ELF、符号链接和压缩包说明仅适用于服务器完整包。Git 中不含 ELF/EXE、图片、大 LUT、模型库、全域 RGB 输出、原 HTML 及两份合计约 8 MiB 的历史全量索引压缩件；因此不能对本目录直接执行服务器完整发布清单。被省略的文件 SHA 仍在 release-manifest 中，原件保留在 `~/workspace/zmx/final1` 及 `final1-selection-20261030`。小型历史覆盖摘要、637 提交列表、188 引用列表和候选比较表已入库。

新的生成器使用仓库相对路径，只校验或输出到新目录。原调度与打包脚本保留当时绝对路径，用于证明原执行过程，不自动访问这些路径。此归档没有凭据。
