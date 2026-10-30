# 原60图尾部单扫未降p99，固定前缀覆盖下界未排除目标

Agent：Codex `/root`。Operator：本会话授权用户。Task：16题精度分支。Status：Draft；本阶段停止原单扫协议，未产生可升级模型。

当前第二级max_first的完整RGB8 p99为3，而100张历史照片合并仍为√12。旧九项收益对训练分布只约束mean/RMS，尾部计数按均匀色域计算。本阶段新增原60图的尾部目标，未把100图重新用于拟合。起点仍是已独立验收的第一级0ea0、第二级904e、原第三级95cb、末级5b8b，完整域mean0.799073807、p993、max√50；未用此前mean-only末级放宽预算。

## 先确认固定阈值适用

`probe_cinema_training_tail.py`只读检查冻结uint32原色频数及143e5cc0完整输出流，独立从全部16,777,216输入重建训练整数直方图。频数总47,185,920，等于60×1024×768；广义CDF与完整重复像素NumPy线性等价p99均为√12，d²>11有627,527像素（1.329903%）。固定目标11适用，未按结果换阈值。

继承1219行、386个末级arrival的完整无损联合支撑。训练mass乘47,185,920还原int64计数，最大浮点残差9.31e-10；起点训练CDF、超限计数及完整域整数直方图与上述独立原流一致。完整域频数仍为16,777,216。两个分布和两种分位数分别保留，未将归一化浮点质量直接冒充整数像素。

## 十一项预算与有限合同

新增`channel_training_tail.py`，不改已封存的九项收益/选择器。训练d²>11像素数和平方超额接在原九项之后；每个parity批次完整域p99/max目标计数和训练超限计数不增，其余指标只能使用从同一起点已取得的余额。逐点cap仍为max(49,原起点d²)。78个±1/±2/±4方向，八色各一次，参数与停止门预先固定。

执行前26份源码/计划/提案原字节快照保存。256个随机选择器合同、一项强制预算交换及3项非法预算拒绝通过；m17/m33跨通道坐标、0/255节点、零训练频数、显式重复样本、11/12与49/50阈值通过。独立uint64前向核对2319个合法节点方向，177个越界方向拒绝，最大十一项收益误差5.26e-13。所有实际批次再经独立uint64、accumulator和真实十一项指标核对，最大误差1.51e-9。

## 实际单扫结果与停止

| 指标 | 起点 | 单扫后 |
| --- | ---: | ---: |
| 完整支撑mean | 0.7990738071534367 | 0.7986965833312298 |
| 完整支撑RMS | 1.1976684589597302 | 1.1911235786675307 |
| 完整支撑p99 / max | 3 / √50 | 3 / √50 |
| 完整支撑最坏1% CVaR | 4.029054534445704 | 3.9040282720234236 |
| 训练mean | 0.682348178378459 | 0.6818985194334478 |
| 训练RMS | 1.1366130440332765 | 1.1291684759484468 |
| 训练p99 | √12 | √12 |
| 训练d²>11像素 | 627527 | 543481 |

59个节点分量改变，末级SHA `ffa035fc3372f3f14c9e8fa805a509581443f3d36bde942ecf25d22941f23259`。超限数减少84,046，约13.39%，但仍高于p99目标允许的471,859。训练p99未严格下降，因此按协议停止，不追加新完整四级原表/native/100图/运行时速度，也不升级综合best。上述新数字是完整无损支撑的拟合统计，不等同新的原生全空间验收。

## 固定前三级的覆盖下界

另立`p16-cinema-training-bound-v1.json`只读诊断，从原5b8b末级起点检查数学限制，不继续拟合。每个相同arrival可以任取一个RGB8输出，放松共享末级节点与全局mean/RMS预算，只保留各行原cap。所有覆盖至少一个正训练频数样本的RGB必在其gold的d²≤11整数球并集中；并集外输出覆盖为零，无法优于已含的原输出。故枚举这些球并集加原输出，得到每组放松问题的完整整数最优，逐组相加是实际LUT超限数的必要下界。

64个8³小域夹具独立穷举每个512输出，含零频数/混合cap/边界，最少超限数和见证均相等。实际386组的必要下界为148,154像素（0.313979%），低于1%，所以**没有排除固定前三级达到训练p99≤√11的可能性**。这不是可实现末级模型：见证未满足共享节点或全局均值预算，也不能据此许诺更多扫描一定有效。全部组见证与候选数量保留。

## 环境、重放及原件

Windows11 x64 / Ryzen9 8945HX；Python3.12.14、NumPy1.26.4、Numba0.60。BLAS/OMP环境1、Numba请求4线程。与其它代理归档并行，只记录离线过程秒数，不作吞吐或目标i7服务器成绩；无AVX512、新素材或官方阈值判分。

```text
python scripts/probe_cinema_training_tail.py --output artifacts/cinema-training-tail-probe-v1.json
python scripts/check_cinema_training_tail.py --output artifacts/cinema-training-tail-contract-v1.json
python scripts/run_cinema_training_tail.py --contract artifacts/cinema-training-tail-contract-v1.json --probe artifacts/cinema-training-tail-probe-v1.json --output artifacts/cinema-training-tail-v1
python scripts/certify_cinema_training_bound.py --output artifacts/cinema-training-bound-v1.json
python scripts/archive_cinema_training_tail.py --output report/data/p16-cinema-training-tail-v1
```

全部输出拒绝覆盖。源码、计划、26份执行前快照身份、有限合同、独立原频数直方图、单扫逐批记录、候选和覆盖下界封存在[`p16-cinema-training-tail-v1`](../../report/data/p16-cinema-training-tail-v1/README.md)。旧依赖CRLF与父Git LF双身份保留，不改旧执行源；ZIP逐成员CRC/SHA与index/HEAD逐blob分别核验。继承完整RGB流、原60图频数和1219行支撑按路径/SHA绑定，不重复上传。仍归精度Draft PR90，未合并。
