# 独立实验日志

`python/lutlab/runlog.py` 把运行记录保存在 `logs/` 中。该目录有自己的 Git 仓库，并被主仓库忽略。每条记录包含 `run.json`、`stdout.log` 和可能的附加文件；`pixi run logs` 可列出记录。

`logs/` 不会随主仓库 clone、push 或 Docker 构建自动同步。团队要共享实验结果时，应单独备份或推送这个日志仓库，或设置 `JSHC_LOG_DIR` 到持久位置。单次记录的 Git 提交号与主仓库提交号不同，引用时应同时给出主代码 commit 和日志 commit。

目前的独立日志历史已推送到同一个 Codeberg 地址的 `experiment-logs` 分支。新工作区可在主仓库根目录执行 `git clone --branch experiment-logs --single-branch https://codeberg.org/Mooooonk/problem_probe_16.git logs`；之后运行 `pixi run logs` 查看记录。新运行会自动在 `logs/` 本地提交，但仍需单独执行 `git -C logs push` 才能分享。主仓库的 `codex/zig-default-pixi` 与日志仓库的 `experiment-logs` 是不同 Git 历史，不能用普通合并把它们拼在一起。

旧版多语言基准 `R14_multi_lang_portable_simd` 的 `run.json` 是事后写入的结果汇总，记录耗时仅 0.013 秒，缺少当时的命令和原始进程输出。它适合作历史线索，不应单独作为当前性能结论。当前分支的重新测量见 `AUDIT.md`。
