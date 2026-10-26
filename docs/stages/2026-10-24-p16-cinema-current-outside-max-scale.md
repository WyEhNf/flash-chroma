# 当前最优点的固定外域下界与全部最劣点支撑扩展

Agent：`/root/tail`。操作依据：用户第16题精度方向，优先p99/max、平均精度不下降。状态：两个有界只读研究阶段已完成；没有新候选、CP、拟合、native或性能调用。固定模型仍为已独立完整验收的 `91d868…`，共同精度分母仍为 `373a`，其余既有失败保持。

本阶段首先确认：旧122节点集合已无法改善三个核心尾部指标。完整cube直方图减去已验80,751正支撑误差直方图，训练按原整数频数同样扣除，逐格与旧screen外域完全相同。再把全部可变支撑理想化为误差零，构造任何该子空间模型都不能低于的乐观p99。使用`99*(N-1)/100`的linear秩，两个独立累计秩实现及1,248个有限展开直方图与NumPy一致；没有把CVaR的`ceil(N/100)`定义移作p99。

| 范围 | 全量 | 支撑质量 | 固定外域超过目标q的计数 | 乐观p99下界 | 目标 | 结论 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 全RGB8均匀cube | 16,777,216 | 80,751 | q>8有555,817 | 3 | √8 | 严格阻断 |
| 原60图整数频数 | 47,185,920 | 901,853 | q>11有528,686 | √12 | √11 | 严格阻断 |

两个乐观p99的上下秩均落在同一q（9及12），另用2³²整数根区间严格比较。固定外域q41有22个不同输入、训练权重1,439，因此该122集合也不能实现max²≤40；独立完整质量中的单点见证仍有效。下界只针对固定122节点、固定轴及后缀，不是所有首级节点或整链全局最优。因此保留完整hint静态稿，但不再执行该L1优化作为p99/max方向。

第二个阶段从固定 `91d868…` 完整oracle `728666…` 与gold唯一列出全部q41输入。用真实分输出Q16四面体正权和独立八角帽权提取顶点，固定新集合为旧122与这些顶点的并集，所有RGB分量相对91d±2并clip[0,255]。这个选择没有按训练或100图择优。

| 完整选择与支撑 | 结果 |
| --- | ---: |
| 全部q41输入 | 231 |
| 最劣输入触及的物理节点 | 249 |
| 旧122之外新增节点 | 151 |
| 固定并集节点／活动分量 | 273／819 |
| 两侧idx盒候选输入计数 | 628,994 |
| 完整正支撑并集 | 171,271 |
| 全16M独立四角核支撑差异 | 0 |
| 重新恢复的训练支撑质量 | 3,541,732 |
| 独立uint64端点输入数 | 342,542 |
| 新固定外域cube／train最大q | 38／38 |

所有231个q41输入均在新完整正支撑内。所有未选角贡献保留于完整首级acc；不是把固定角映射到可变dummy节点。端点按原节点重新clip和Q16整数累加，未从已有舍入RGB上下界推算。

在查询任何AABB状态前，按每个输入的真实首级RGB端点宽度乘积精确计数，共 **5,284,765** 状态，超过本阶段预先新增的 **4,194,304** 总状态资源门。因此严格STOP，实际状态查询0、安全表未构造、CP调用0。不能称发现cap40无解，也不能把未查询的危险点或安全行数写成0。其他固定门为节点928、完整支撑1,048,576、单AABB125、危险点8,192、安全行500,000；没有放宽旧500,000门。单节点编码盒65,536沿既有实现界，4,194,304明确是本次新资源限制而非历史原限。

独立审计再次从完整16M误差列出全部231个输入、核新旧顶点并集，完整复核171,271行的两个整数端点、训练频数、固定外域直方图和状态乘积。原始AABB及选择均保留。外域q38只说明固定此新集合仍不能得到max²≤37，不证明存在max²38/40的共享节点赋值。

主要入口为`check_cinema_current_outside_rank.py`、`screen_cinema_current_all_max.py`和`audit_cinema_current_all_max.py`，两份协议和静态提案与源码快照均归档。冻结身份：外域秩`2eea2598…`；支撑扩展`b425b230…`，16源/14固定输入；有限合同`001b7407…`含512真实分输出正支撑输入、1,024整数端点及5个cap40完整笛卡尔盒，覆盖共享/固定角、0/255 clip、空安全表和零训练质量。独立规模summary SHA `926c6a6a…`，AABB SHA `1e8038ae…`。

环境为Windows11 x86-64、Ryzen9 8945HX、CPython3.12.14、NumPy1.26.4、Numba0.60.0，原隔离环境；OpenBLAS/MKL1、Numba最多4线程。质量计算与root293构建共用host，未进行吞吐计时、AVX512或跨平台实测。实际session32467完整exit0，随后释放CPU；此前仅冻结/有限合同，不重复真实普查。

```text
python scripts/check_cinema_current_outside_rank.py --freeze
python scripts/check_cinema_current_outside_rank.py
python scripts/screen_cinema_current_all_max.py freeze
python scripts/screen_cinema_current_all_max.py contract
python scripts/screen_cinema_current_all_max.py select
python scripts/screen_cinema_current_all_max.py run
python scripts/audit_cinema_current_all_max.py --output artifacts/cinema-current-all-max-support-independent-v1.json
python scripts/archive_cinema_current_outside_scale.py --output report/data/p16-cinema-current-outside-max-scale-20261024
```

脚本拒绝覆盖原件，重现须另设独立路径并重新冻结。原始JSON及源码先设`-text`，归档逐ZIP成员、暂存及HEAD blob核字节SHA，历史证据消费27050b1已认证祖先的增量审计。后续±1缩域属于独立新问题，本阶段不自动重跑、构造安全表或升级模型；任何未来候选仍须保373a cube/原60图mean与p99、披露逐图代价并验速度50%底线。
