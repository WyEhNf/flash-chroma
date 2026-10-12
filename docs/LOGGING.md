# 独立实验日志

`python/lutlab/runlog.py` 把运行记录保存在 `logs/` 中。该目录有自己的 Git 仓库，并被主仓库忽略。每条记录包含 `run.json`、`stdout.log` 和可能的附加文件；`pixi run logs` 可列出记录。

`logs/` 不会随主仓库 clone、push 或 Docker 构建自动同步。团队要共享实验结果时，应单独备份或推送这个日志仓库，或设置 `JSHC_LOG_DIR` 到持久位置。单次记录的 Git 提交号与主仓库提交号不同，引用时应同时给出主代码 commit 和日志 commit。

旧版多语言基准 `R14_multi_lang_portable_simd` 的 `run.json` 是事后写入的结果汇总，记录耗时仅 0.013 秒，缺少当时的命令和原始进程输出。它适合作历史线索，不应单独作为当前性能结论。当前分支的重新测量见 `AUDIT.md`。
