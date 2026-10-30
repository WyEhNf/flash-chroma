# a399之后的真实四级尾部节点研究

[阶段说明](../../../docs/stages/2026-10-23-tail-nodes.md)列出数值、边界和失败项。`results.json`保存两候选完整域、百图逐图/聚合、实际原生SHA及第一层独立精度；`accuracy.csv`给出同范围a399对照。`contract.json`为新gain有限整数合同；`run.json`冻结输入SHA、目标和环境。

`models.zip`包含两候选NPZ、必须配套的base及侧表；后三模型及运行DLL复用[上一阶段原证据](../cinema-current-anchor-accept-v1/README.md)。`fit-evidence.zip`保留全部两次八色提议、训练收益和负面边界；`source.zip`保存本次脚本及核心依赖。完整输出RGB流在本地`artifacts/channel-tail-accept-v2`，不把完整表作为运行模型。`manifest.json`记录SHA、失败v1及未测速/未升级默认的状态。

在新输出目录复现，PowerShell先设置`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`及`OPENBLAS_NUM_THREADS=1`、`MKL_NUM_THREADS=1`、`OMP_NUM_THREADS=1`；以下Python为已有3.12环境，`--cache-root`指含原始冻结缓存与照片的项目目录：

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/run_channel_tail_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/channel-tail-nodes-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/verify_channel_tail_nodes.py --output artifacts/channel-tail-contract-v1/results.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/accept_channel_tail_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --models artifacts/channel-tail-nodes-v1 --output artifacts/channel-tail-accept-v2
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/archive_channel_tail_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --output report/data/channel-tail-nodes-20261023
```

归档输出目录已有README时，先选另一个不存在的目录生成，再将证据复制到本目录；脚本拒绝覆盖既有证据。当前没有性能结论、官方阈值或新素材盲测。
