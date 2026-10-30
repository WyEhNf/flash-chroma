# 公共训练mean/p99两预算桥：安全表规模超门停止

本阶段从已认证的741e55f、122首级节点±2/clip及完整80,751正支撑出发，将共享安全条件与公共综合最佳373a的训练mean/p99预算合并为直接成本表。唯一只读普查得到13,091个表点、608,964安全行、12,565个成本/flag变量；安全行超过事前固定的500,000门，按协议严格STOP。没有构造CP、查询新RGB、拟合、生成候选或运行solver，不能称精度优化通过。

Agent：`/root/tail`；Operator：本次16题任务用户；状态：有界规模负例及归档完成。相关提交以本阶段文档所在提交为准，保留于精度研究分支及Draft PR90，未升级默认模型。

## 为什么只补训练两预算

[完整风险与条件误差上界](2026-10-24-p16-cinema-max48-risk-upper.md)已经证明：若共享节点赋值满足全部危险点的cap47安全表，全域max²至多43，且全域mean/p99/max不劣于373a综合最佳；但训练mean/p99没有自动保证。本阶段预先固定373a为公共分母，增加保守训练mean和p99两项直接表列，试图避免原八预算中大量one-hot选择器。

分母没有按结果改选。373a的全域/训练mean分别为0.8225028465、0.6990079845，741e55f当前点为0.7996658981、0.6823633098。因此即使新公共预算通过，也必须披露相对741更低均值的代价。旧max_first八预算失败、741独立三分母质量与速度未获整体资格均保持原判。

固定首级NPZ SHA为`741e55f55c674384543511dc20b98ecd7d6a1ed4c1b9bb17406cabd7cc86bea0`；本阶段只读风险screen SHA为`a016695a72446e728ee64d5b93d0db61d68375651db00e991c556a3b94df0baa`。其完整122节点盒、904e/95cb/5b8后缀、2,102,192状态、4,985危险点与386,612安全行全部复用认证原件，不改节点域、cap、真值或频数。

## 固定分类及数学预算

令D为全部危险点；T为训练频数大于0且最小安全q小于最大安全q的点。必须建表的全集为D∪T，所有零训练频数危险点完整保留。T点的安全RGB直接附加`ceil(2^20*sqrt(q))`整数成本；只有安全q跨12的点再附加一个`q>12`布尔列，无显式q变量或one-hot变量。

训练mean完整预算为：综合best全47,185,920像素的逐q根floor和，减去支撑外及支撑内恒q训练点的逐q根ceil固定贡献，得到可变成本上限。该保守编码一旦通过足以保证真实mean不升，但编码无解不等于真实mean预算无解。所有零权重点、恒q点、恒flag点及支撑外项均计入，不能只盯145热点。

训练p99目标固定√12。按线性分位的上端整数秩，`count(q>12)`最多471,859；支撑外、内部恒flag和可变flag的真实整数频数全部计入。成本与flag由表中的实际RGB共同决定，不得独立挑值。训练mean/p99不能自动担保100图均值、尾部或逐图表现。

## 事前门与唯一普查

三门在读取实际分类数量之前写入静态方案、随后正式协议与冻结源；不因本次结果调整。

| 固定资源门 | 上限 | 实际 | 判定 |
| --- | ---: | ---: | --- |
| D∪T点数 | 16,384 | 13,091 | 通过 |
| 全部表安全行 | 500,000 | 608,964 | 超门STOP |
| 成本与flag变量 | 131,072 | 12,565 | 通过 |

进一步完整账单：T点8,779个，跨12的flag点3,786个，D中训练零频点4,291个全部保留。预计显式节点、输出、成本、flag整数变量总数52,204，表列单元数2,303,961；这只是输入表示规模，不是已建CP模型或进程RSS。原风险8192危险点/1M行门仍满足，不能用原门替代新500,000行门。

完整16,777,216项训练频数重新恢复47,185,920整数像素，受影响80,751输入的频数901,853与保存screen逐项相等，最大恢复残差为0。支撑外固定项没有丢失。实际整数预算如下：

| 项目 | 整数值（根尺度2²⁰） |
| --- | ---: |
| best完整根floor和 | 34,585,526,974,820 |
| best完整根ceil和 | 34,585,539,368,254 |
| 固定贡献根floor和 | 32,672,976,007,234 |
| 固定贡献根ceil和 | 32,672,987,565,581 |
| 可变mean上限 | 1,912,539,409,239 |
| 逐点松弛可变mean最小值 | 474,326,329,226 |
| 逐点松弛可变mean最大值 | 2,492,391,580,017 |
| 固定q>12质量 | 319,393 |
| 可变flag最大质量 | 287,115 |
| 可变flag剩余上限 | 152,466 |

松弛区间与预算相交仅说明没有被这种逐点上下界排除，不能推出共享节点可行。资源超门后没有继续生成真实表或模型，也没有删样、改分母、调整门、重试solver。

## 环境、验证与证据

目的为保守整数预算合同、完整频数与表规模数据完整性；未测试运行时或性能。环境为Windows11 x86-64、Ryzen9 8945HX、CPython3.12.14、NumPy1.26.4，原隔离环境不变。本阶段没有Numba JIT或原生编译，没有AVX512。主机为非计时共享质量窗口；全过程不读取100图进行选择。

冻结6份源/协议和8项输入，AST通过，冻结SHA为`aebcad8c2ddd664507251725d0426813811263193380b9f90f5e4444dbf27e9c`。有限合同用两个独立整数根算法核68个q，覆盖6种恒q/可变q/跨阈/零频分类，完整18种q赋值中3种通过预算；对样本数1..201逐个枚举超阈计数核上端秩。未调用真实CP来代替数学合同。

独立审计逐点循环全部80,751输入，重新分类集合、累加固定项，并以binary整数根重新计算21项整数预算/规模；全部通过。生产普查使用isqrt，审计不用该根算法。完整原件位于[本阶段归档](../../report/data/p16-cinema-max48-training-bridge-20261024/manifest.json)：5份raw JSON、7份源码ZIP成员和2份支持证据成员；复用的完整风险及模型质量manifest均独立核SHA。

复现命令使用`F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe`：

```text
python scripts/check_cinema_max48_training_bridge.py --output artifacts/cinema-max48-training-bridge-contract-v1.json
python scripts/census_cinema_max48_training_bridge.py --frozen artifacts/cinema-max48-training-bridge-frozen-v1.json --contract artifacts/cinema-max48-training-bridge-contract-v1.json --output artifacts/cinema-max48-training-bridge-census-v1
python scripts/audit_cinema_max48_training_bridge.py --stage artifacts/cinema-max48-training-bridge-census-v1 --output artifacts/cinema-max48-training-bridge-independent-v1.json
python scripts/archive_cinema_max48_training_bridge.py --output report/data/p16-cinema-max48-training-bridge-20261024
python scripts/audit_tail_git_evidence.py --git-ref HEAD --output artifacts/cinema-max48-training-bridge-head-audit-v1.json
```

原始脚本拒绝覆盖已存在输出；复现时应复制被冻结源并使用新的独立输出路径。raw、源码及静态方案先设`-text`再显式白名单stage，核实际暂存blob/ZIP成员SHA，提交后再核完整历史HEAD证据，避免换行归一改变测量身份。

## 后续边界

本次表达按固定资源门失败，不代表所有两预算表达、节点模型或共同用户目标无解。后续仅静态研究实质不同的保守域或精确压缩表达，例如禁止原训练q≤12点新增越12，从而自动保护训练p99，再单独证明mean预算；任何新协议都须重新事先固定资源门并保留当前超门负例。当前没有CP或候选，完整原生/全域/100图三分母与实际速度至少50%的资格均未新增。
