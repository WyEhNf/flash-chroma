# Cinema 当前最优首级热点的完整正支撑有限证书

Agent：`/root/tail`。Operator：本任务用户。状态：已完成，固定单节点方向无候选晋级。本阶段不替换默认模型，不产生性能结论。

目标是从当前已独立验收的 `max_first` 整链出发，将完整 RGB8 域最大平方误差从 50 严格降至 49，同时保护完整域及原 60 图合并的 mean、RMS、p99、最差 1% CVaR。起点固定为首级 `0ea0…`、第二级 `904e…`、第三级 `95cb…`、末级 `5b8…`，完整输出流为 `143e…`。本阶段不使用后来的 mean-only 或多轮训练模型借取预算。

## 范围与完整性

预注册见 `experiments/p16-cinema-first-hotspot-v1.json`。选点包括全部 116 个最大平方误差 50 的原始 RGB8 输入，并取三个真实分输出 Q16 基下有严格正权重的物理首级节点并集。每个物理节点独立尝试 26 个非零 RGB 方向及步长 1、2，共 52 项；每项均相对同一个原始模型，节点变化不叠加，不追加扫数。

一个物理节点 `(i,j,k)` 只能由共享 `idx` 三轴分别属于 `{i-1,i}`、`{j-1,j}`、`{k-1,k}` 的输入触及。因此，先枚举这些 cell 对应的完整 RGB8 编码盒，再按三个输出通道的实际四面体权重是否大于零取支撑，能够保留全部旁侧输入，包括原 60 图整数频数为零的输入。不能只在 116 个热点上评价候选。

独立完整性检查不复用四面体排序。另以立方体八角的解析 Q16 帽函数计算正权重，在全部 16,777,216 个 RGB8 输入上统计选中节点的逐节点正支撑计数及并集，并与局部枚举逐节点计数和完整并集严格比较。局部支撑中还逐点核对两套权重及未舍入累加值。其余未触及输入的原始直方图先精确扣除局部旧计数，再精确加入局部新计数，不能丢掉它们的 max、p99 或 CVaR 预算。

后缀必须由当前 `904e/95cb/5b8` 三张表重新完整构造，不能复用旧 `envelope-suffix.npy`。冻结 87 库的 AVX2 输出与独立 `uint64` 整数前向对全部后缀输入逐字节核对。随后用独立八角首级输出查该后缀，对全部 RGB8 输入重放并核对 `143e` 基线流。

原 60 图总像素数固定为 47,185,920，从原始 RGB8 频率逐项恢复整数计数，最大残差不得超过 `1e-6`，总数必须完全一致。mean、RMS、NumPy linear 等价 p99 与按 `ceil(N/100)` 个最差像素定义的 CVaR 均从整数直方图计算。浮点比较容差为绝对 `1e-12`。

## 实现与资源

`python/lutlab/channel_hotspot_support.py` 实现完整编码盒、主要四面体设计、独立八角权重、52 个方向以及精确直方图统计。`scripts/check_cinema_first_hotspot.py` 执行有限合同；`scripts/run_cinema_first_hotspot.py` 固定输入身份、构建后缀、核对完整支撑并生成每项候选的原始记录。

本阶段逐节点顺序处理，不创建旧方案的全域大设计。RGB8 后缀净载荷为 50,331,648 字节，完整并集临时位图为 16,777,216 字节；输入和金标准、频率、基线输出采用只读映射。选中节点最多 928 个、单节点编码盒最多 1,048,576 行、正支撑并集最多 1,048,576 行，超过任一冻结资源界即停止。初始 profile 在大分配前报告实际最大编码盒及按每行 512 字节保守估计的局部暂态，不能把载荷字节等同于进程 RSS。

## 完整域结果与单节点覆盖边界

在共享 Windows x86-64 主机、项目 Python 3.12 环境上，有限 17/33 节点模型的边界与内部节点共六组合同已通过，每组完整支撑上核对全部 52 方向；另以展开的整数像素频数独立核对 mean、RMS、p99 与 CVaR。证据为 `artifacts/cinema-first-hotspot-contract-v1.json`。它仅说明有限合同通过，不能替代真实模型的完整域证书。

真实冻结输入与 116 个 max50 源输入完全一致，共触及 86 个物理首级节点。其完整正支撑并集为 70,571 个 RGB8 输入，最大单节点编码盒 5,376 行；按冻结的每行 512 字节保守估计，最大局部暂态上界为 2,752,512 字节。原 60 图 47,185,920 个像素的整数频数完全守恒。完整后缀 16,777,216 行的原生 AVX2 对独立 uint64 重放、八角首级对既有 `143e` 完整基线流的重放，以及全部节点支撑计数和并集核对，均为零差异。

| 统计范围 | mean | RMS | p99 | max² | 最差1% CVaR |
| --- | ---: | ---: | ---: | ---: | ---: |
| 当前完整域 | 0.7990738071534367 | 1.1976684589597302 | 3 | 50 | 4.029054534445704 |
| 当前原60图合并 | 0.6823481783784588 | 1.1366130440332765 | 3.4641016151377544 | 50 | 4.303192100572805 |

固定 86×52=4,472 项中，2,819 项保持完整域 cap50，其中最好仅将 max50 像素数从 116 降至 97。这个数字包含 mean 或其他保护指标退化的方案，不能作为守住全部预算的结果。真正保持两范围全部八项预算的有 298 项，最好仅将 max50 像素数降至 111。没有任何项达到严格 max49，因此未生成新候选或进入后续百图/原生/性能验收。

另有一个比“52方向没有成功”更强、但范围明确的几何证书：86 个节点中的任意一个最多正支撑 32 个原始 max50 输入，至少 84 个原始最大误差输入必然不变；该并集中以外的节点连一个原始 max50 输入也不触及。因此，在固定首级几何和其余三级下，**任何单个物理节点的修改均不能把完整域 max²50 降到49**，这个结论不依赖本次步长是否仅为1、2。独立检查为每个节点保存一个正权重为零、原始平方误差仍为50的具体源 RGB8 反例。它不能推出多节点联合修改、轴修改或其他表示无解。

`scripts/audit_cinema_first_hotspot.py` 在只读阶段独立复核全部 4,472 项通过/失败映射，并以 Python 整数比较器排序重新列出 116 个热点的正支撑集合，核对 86 个逐节点覆盖反例。它没有重新计算每项候选的全部像素浮点目标，这个限制在证据中保留。主要证据为 `artifacts/cinema-first-hotspot-v1/{run.json,profile-initial.json,summary.json,directions.json,support-index.npz}` 及 `artifacts/cinema-first-hotspot-independent-v1.json`。

完整质量执行约 47.82 秒；当时与其他分支的质量工作共享主机，没有正式性能计时，因此该耗时只描述本次运行。新后缀净载荷仍是 50,331,648 字节，构造它的三层冻结87句柄报告模型容量788,129字节，均不等于进程峰值RSS。本阶段没有测量进程RSS、执行百图候选终验、实现新原生运行时或进行正式性能。

复现命令：

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_hotspot.py --output artifacts/cinema-first-hotspot-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/run_cinema_first_hotspot.py --cache-root F:/Hackathon/projects/16-lut-color --contract artifacts/cinema-first-hotspot-contract-v1.json --output artifacts/cinema-first-hotspot-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_hotspot.py --study artifacts/cinema-first-hotspot-v1 --output artifacts/cinema-first-hotspot-independent-v1.json
```

首级分输出坐标仍属官方许可未知的研究表示，本阶段没有把它改称普通 SLUT v1。三分支兼容性、速度与内存线也不能从这项质量证书推断。

版本库中的精简归档位于 [report/data/p16-cinema-first-hotspot-20261024](../../report/data/p16-cinema-first-hotspot-20261024)。八份原始证据包含完整后缀/支撑索引/全部方向原件 ZIP、冻结执行源 ZIP及六份原始模型 ZIP，manifest分别列出外层文件和ZIP成员SHA。原始金标准、原60图频率及既有全域流以完整SHA绑定原缓存，未重复纳入本归档。
