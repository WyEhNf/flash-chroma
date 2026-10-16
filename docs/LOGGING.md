# 独立实验日志与团队交接

`python/lutlab/runlog.py` 将实验记录写入 `logs/`，或由 `JSHC_LOG_DIR` 指定的持久目录。日志目录拥有独立 Git 历史，并被主仓库及 Docker 构建上下文忽略。

## 记录内容

每条记录包含 `run.json`、`stdout.log` 及实验附加文件。记录绑定主代码提交、分支、差异指纹、机器、Python 与 `pixi.lock` 哈希。查看记录：

```bash
pixi run --locked logs
pixi run --locked python -m lutlab.runlog show <运行ID前缀>
```

`Run` 默认会在日志仓库创建本地提交；部分拟合、验收和选择入口显式使用 `commit_logs=False`，不会自动提交。是否已经归档应以日志仓库的实际状态为准。测试任务本身不创建或推送实验日志。

## 共享与备份

主仓库 clone/push 不包含日志。开始实验前检查代码和日志各自的分支与工作区；结束后分别提交、备份或推送。引用结果时同时提供主代码提交、运行 ID 及日志提交，必要时包含输入、模型和二进制哈希。

```bash
git status --short --branch
git -C logs status --short --branch
```

历史日志保存在 Codeberg 的 `experiment-logs` 分支。仅在 `logs/` 尚不存在且确实需要历史证据时取回：

```bash
git clone --branch experiment-logs --single-branch \
  https://codeberg.org/Mooooonk/problem_probe_16.git logs
```

这是独立历史，不应合并进主代码分支。新实验日志使用哪一个远端由团队确定；脚本不会替团队自动发布。

## 证据边界

日志独立存储便于分别管理，但不是备份保证。不要删除日志目录，实验后应主动归档。主仓库已保存的小型冻结证据见 [报告数据索引](../report/data/DATA_INDEX.md)。

早期多语言基准 `R14_multi_lang_portable_simd` 的记录是事后汇总，缺少当时的命令与原始进程输出，只能作为历史线索。任何当前性能声明都需要新的、可复现的测量。
