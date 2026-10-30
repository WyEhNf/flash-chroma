# Cinema第二级完整支撑单扫：p99与max同时下降，速度资格尚未通过

Agent：Codex `/root`。Operator：本会话授权用户。Task：16题三条独立研究中的精度方向。Status：In Progress / Draft；不合并、不升级综合best。

## 目标与边界

上一阶段已证明：固定原前两级时，两种真值距离平方226，却在第二级碰撞到同一RGB，任意后缀的最差平方误差至少57；现有best恰为57。因此本阶段固定第一级、第三/四级和全部轴，改第二级节点，尝试解除碰撞。该旧证书的限制不适用于改动第二级后的候选。

起点为 `first 0ea0a380`、原第二级 `933a4311`、原第三级 `95cb685e`、新末级 `5b8be3d4`，完整流 `373a2fcb…`。实际完整SHA、路径与执行源在归档及 `run.json`，并非从较弱原a399重置预算。

完整16777216种RGB8按“第一级到达RGB、独立四原表整链gold RGB”联合分组，保留int64均匀频数及原60图训练质量。得到10633条联合支撑、5218个不同到达值、166个正支撑物理节点；未抽样、未删稀有颜色，零训练质量支撑仍保留。设计数组1020768 B，4份78方向收益3729024 B，后缀缓存50331648 B。这是离线工作数组，未测峰值RSS，不能称运行时模型节省。

预注册两种策略各从同一起点开始，仅一次八色扫描，78个±1/±2/±4方向。目标分别为平方误差>56计数与>11计数；两条mean、两条RMS、尾部hinge等九项不能超过当前best绝对上限。只消费此前已经取得的余额，两个目标计数每批不增，逐输入cap为 `max(56, 起点d²)`。100张照片没有进入本阶段收益或选择器；它们已在历史研究中多次使用，本阶段仍不称盲测。

## 精度结果

| 方案 | 完整域mean | RMS | p99 | max | 最坏1% CVaR |
|---|---:|---:|---:|---:|---:|
| 起点best | 0.822502847 | 1.225513544 | 3.464101615 | 7.549834435 | 4.095497757 |
| max_first | 0.799073807 | 1.197668459 | 3.000000000 | 7.071067812 | 4.029054534 |
| p99_first | 0.822502730 | 1.211813628 | 3.000000000 | 7.071067812 | 3.874347271 |

两方案分别改181和217个第二级节点分量，其余表/轴不变。均通过拟合门禁：完整域mean/RMS/CVaR、原60图mean/RMS不退，p99和max严格下降。max_first平均误差更低，p99_first的CVaR更好，保留两者的取舍；两者的误差≥5占比也略升，原件完整披露。

独立四原表串联真值、四级uint64 oracle、旧87 scalar请求1线程及AVX2请求4线程完整域逐字节一致，100照片原生输出亦与完整流一致。max_first完整流SHA `143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e`；p99_first为 `4f3bb1eb15cadc38eea189fdbdc11495c9541889c67315bbbc96e5c08f9cf12c`。这是两个原生配置的质量覆盖，不是四种接口/线程性能。

| 历史100图合并 | mean | p99 | max |
|---|---:|---:|---:|
| 起点best | 0.695486159 | 3.464101615 | 7.549834435 |
| max_first | 0.679090181 | 3.464101615 | 7.071067812 |
| p99_first | 0.693002848 | 3.464101615 | 7.071067812 |

max_first相对起点逐图mean为99好1差，唯一变差div2k-0868约3.2865%；p99为28好2差70同，div2k-0811从√12升到√17、dped-sony-092从√17升到√22；max为73好1差26同，div2k-0823从√41升到√48。CVaR为77好23差。p99_first逐图mean72好28差，p99为42好3差55同，max为71好8差21同，CVaR86好14差。不能把合并指标下降写成逐图全不退；所有100行原件及恶化比例均保留。

独立审计不调用拟合或原验收统计函数，从三个实际RGB流重建整数直方图，使用 `math.fsum`、整数CDF及最坏 `ceil(n/100)` 个样本重算指标；与联合支撑直方图、原生/oracle SHA及逐图mean/RMS/max合计一致。选择器另有512个随机独立收益重算、2个构造预算交换及3个拒绝合同，11/56阈值显式重复频数等价检查通过。

六档精度代理另在归档后用冻结JSON计算，见 `quality-tiers.json` 与 `scripts/tier_cinema_second_nodes.py`：完整域、合并照片和100逐图的mean/p99/max共306项，逐项取 `min(1,基线误差/候选误差)` 后取最小，基线0必须候选0。相对三分支共同a399，max_first最小保留率100%，六档全部通过；p99_first为92.4211%，瓶颈div2k-0849的max，过90档及以下。相对本方向上一best，两者分别84.0168%和86.6025%，均仅过80档及以下。速度未测，联合档不填；这些是研究代理，不能冒充官方精度分。

## 旧87资格损失与未完成事项

旧87的整个suffix cache分别有603、703种值，完整RGB8实际输出也有336、380种，均超过8位索引。旧87因此精确回退，两个候选model_accounting均为1938464 B；这不是相同快核的无损RAM胜利，不能在没有吞吐时声称综合升级，也不能靠只剔除不可达cache槽恢复8位资格。

后续在同一精度分支独立研究16位直接索引及动态RGB32 palette，预计直接表增加约16 MiB，所有guard、对齐、元数据、prepare与首批成本均须实算；旧87源/DLL保持冻结。需要原a399、起点best和两候选同场受控吞吐，最劣保留率低于50%即拒绝，100%至50%按10%分档；未执行前不填速度档。该后续内核尚未包含在本阶段结果中。

另用完整联合支撑和独立uint64前缀检查两候选全部旧max50热组，半径平方49的整数球交在固定前1/2/3级下均可行：max_first各有5/1/1组，p99_first为5/3/1组。没有找到max≥50的固定前缀不可行证书；这不证明现有插值网络能实现49，也不构成新拟合结果。

## 环境、重放与证据

实际Windows 11 x64 / Ryzen 9 8945HX / Python3.12.14 / NumPy1.26.4 / Numba0.60；质量Numba请求4线程，BLAS/OMP环境设1，原生分别scalar1和AVX2请求4。旧87 DLL SHA `58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158`，沿用既有GCC15.2构建；本阶段未重编译，也未在i7-14700、ARM或官方服务器测性能。两候选完整验收并行执行，部分独立代理同时做档案，所有seconds仅过程描述，不能作受控速度证据。

在本worktree用 `F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe` 执行，先设置 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`、`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`、`OMP_DYNAMIC=FALSE`、`OMP_WAIT_POLICY=PASSIVE`：

```text
python scripts/check_cinema_second_nodes.py --output artifacts/cinema-second-nodes-v1-contract.json
python scripts/run_cinema_second_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --best artifacts/cinema-arrival-last-budget-v1/candidate --cube artifacts/cinema-arrival-budget-accept-v1/candidate.rgb --contract artifacts/cinema-second-nodes-v1-contract.json --output artifacts/cinema-second-nodes-v1
python scripts/accept_cinema_second_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --trial artifacts/cinema-second-nodes-v1/max_first --baseline artifacts/cinema-arrival-budget-accept-v1/candidate.rgb --library F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll --output artifacts/cinema-second-accept-max_first-v1
python scripts/accept_cinema_second_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --trial artifacts/cinema-second-nodes-v1/p99_first --baseline artifacts/cinema-arrival-budget-accept-v1/candidate.rgb --library F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll --output artifacts/cinema-second-accept-p99_first-v1
python scripts/audit_cinema_second_nodes.py --study artifacts/cinema-second-nodes-v1 --accept-root artifacts --baseline artifacts/cinema-arrival-budget-accept-v1/candidate.rgb --reference F:/Hackathon/projects/16-lut-color/artifacts/cinema-axis-calibration-v1/envelope-reference.npy --output artifacts/cinema-second-nodes-audit-v1.json
python scripts/inspect_cinema_second_palette.py --cache-root F:/Hackathon/projects/16-lut-color --study artifacts/cinema-second-nodes-v1 --accept-root artifacts --library F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll --output artifacts/cinema-second-palette-v1.json
python scripts/certify_cinema_second_bound.py --study artifacts/cinema-second-nodes-v1 --accept-root artifacts --output artifacts/cinema-second-bound-v1.json
python scripts/tier_cinema_second_nodes.py --original F:/Hackathon/projects/16-lut-color/artifacts/cinema-current-anchor-accept-v1/results.json --accept-root artifacts --output report/data/p16-cinema-second-nodes-v1/quality-tiers.json
```

脚本拒绝覆盖既有输出；重放须选新目录并相应传入依赖。本地大完整输入/输出不重复上传，归档manifest提供SHA。小诊断曾因临时命令默认GBK解码失败，显式UTF-8后完成；拟合/验收/审计源与参数未因此改动。

主要源码：`python/lutlab/channel_arrival_priority.py`、`scripts/run_cinema_second_nodes.py`、`scripts/accept_cinema_second_nodes.py`、`scripts/audit_cinema_second_nodes.py`、`scripts/inspect_cinema_second_palette.py`、`scripts/certify_cinema_second_bound.py`；预注册计划两个，归档在 [`report/data/p16-cinema-second-nodes-v1`](../../report/data/p16-cinema-second-nodes-v1/README.md)。本阶段提交在同一精度PR90，发布时记录实际提交与Draft状态。

ΔE按PROBLEM.md的RGB欧氏距离。本地保留率是研究代理，不是官方分数。官方逐图硬阈值、sidecar/派生表许可、官方服务器性能及真实嵌入式运行仍未确认，不能据此判定图片过官方硬门槛。
