# 官方框架 PR95 试跑代码

本目录前六个脚本/片段保留实测原字节；不是通用跨平台安装器。算法、数据契约、结果与环境见[报告](../../report/official-pr95-20261029/report.md)，发布范围与限制见[交付说明](../../report/official-pr95-20261029/publication.md)。

## 不依赖原始大数据的归档核验

在检出本分支的仓库根目录执行：

```powershell
python code/official-pr95-20261029/verify_archive.py
```

仅使用 Python 标准库，不会重新拟合、测速或调用原生库。核对归档 SHA、实测源码、8 张/设置误差直方图、全部 144 条热批次耗时与汇总。

## 完整数值重跑的目录约定

原脚本按以下 Windows 工作区布局执行：

```text
仓库根目录/
  test/                         官方完整测试包，需自行取得
  tmp/
    replay-official/            检出本 PR 的工作区
      code/official-pr95-20261029/
      artifacts/official-pr95-20261029/
```

`test` 包需包含 Readme、C/C++ 框架、4 个 Test*.3DL 和 4 张 1024×768 RGB8 bin；哈希见归档 input-manifest.json。官方数据、图片输出和 exe 未上传。源码快照 zip 中有官方 Readme 与实际使用的 C++ 框架，但没有完整数据包。

例如，从主检出创建独立重放目录，再在该目录执行报告的完整命令：

```powershell
git worktree add --detach tmp/replay-official origin/codex/official-pr95-tests-20261029
Set-Location tmp/replay-official
```

`prepare.py` 由脚本位置定位仓库，向上两层定位主检出的 test；run.py 使用 `../../test/data`。目录名不限定为 replay-official，但必须保持这种嵌套层级。新建空实验目录，避免覆盖要保留的旧结果。

原环境为 Python 3.12.7、NumPy 1.26.4、psutil（版本见 run-pinned-receipt.json），MinGW GCC 8.1.0 位于 `D:/codeblocks/MinGW/bin`。run.py 与 pin_and_run.py 保存该编译器及 DLL 路径，换机需显式调整这两处和编译命令，按实际工具链重新记录环境；不能继承旧性能。官方要求 GCC 13.2.0 的复验仍待完成。pin_and_run.py 需要系统允许设置子进程 CPU 亲和。

生成器从 Git 精确提取 fb7e195 的头文件；即使当前分支后来更新，也不会静默改成新内核。summarize.py 会重新生成本地 report.md 和证据清单，发布附加说明单独保存在 publication.md。
