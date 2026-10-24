# 同一最劣点支撑的±1独立缩域与安全表规模

Agent：`/root/tail`。状态：唯一完整规模与独立审计通过，尚未构造CP、寻找共享解、生成新模型或计时。旧±2的5,284,765状态超4,194,304门仍为STOP，不被本阶段改写。

固定91d868首级、904e/95cb/5b8后缀及已验全部231个q41输入。完整消费上一阶段273物理节点、171,271正支撑、训练整数频数和固定外域直方图，仅把819节点分量的域改为相对91d±1并clip[0,255]。从原节点和真实Q16权重新算全部uint64端点，未从±2舍入后的RGB范围折半；未选角贡献保持。

| 唯一规模结果 | 数量／状态 |
| --- | ---: |
| 完整正支撑／节点／活动分量 | 171,271／273／819 |
| 全部当前q41输入 | 231，完整保留 |
| 真实AABB状态 | 1,400,540 |
| 单AABB最大状态 | 27 |
| 可能危险输入 | 4,058 |
| 危险输入全部安全三元组 | 74,081 |
| 空安全表 | 0 |
| 总状态／危险点／安全行门 | 4,194,304／8,192／500,000，全部通过 |
| 独立uint64端点输入 | 342,542 |
| 训练支撑质量 | 3,541,732／47,185,920 |
| 固定外域cube／train最大q | 38／38 |

全部1,400,540状态又由独立分组展开路径核min/max/count/safe_count/safe_max及安全CSR逐行一致，零训练频数输入完整保留。有限合同覆盖1,024个真实Q16端点及5个完整笛卡尔盒、0/255 clip、固定角和零训练质量。主session8914及独立审计完整exit0，首次执行后释放CPU，未补跑挑样。

安全表非空只排除了逐点空盒阻断，不证明这些表有共享节点赋值。低于规模门也不是候选精度或速度通过。当前固定外域存在q38，故在此节点集合中max²≤37已被阻断；本阶段目标仅q≤40。

另独立消费既有固定外域直方图，把全部可变支撑质量置零：cube的乐观p99仍为3（固定外q>8计540,500），不能在此集合得到p99≤√8；原60图训练乐观p99下界为3，外q>11权重377,964，故目标√11未被这个下界阻断。训练未阻断不证明可行，也不保证100图p99。相对373a的cube/训练mean和p99初门仍是任何未来候选的要求，逐图、首级忠实度、运行时容量与速度50另验。

辅助结果保留一个文字勘误：复用旧`compare_target`时，`comparison.interpretation`继承固定“122节点”字面量；本次实际输入及外层scope为273节点。独立整数秩、根界及输入身份均正确，原脚本/冻结/结果不覆盖或重跑。单独[说明](../../experiments/p16-cinema-current-expanded-outside-rank-note-v1.md)明确该标签应按273读取。

主要执行入口为`screen_cinema_current_all_max_unit.py`的`freeze/contract/run`及`audit_cinema_current_all_max_unit.py`。冻结SHA `d74ca995…`含19源/20固定输入，有限合同`b82f5069…`；实际summary SHA `2480ddb2…`，新AABB SHA `f6f33f85…`。完整旧支撑由上一阶段manifest不可变引用，不重复16M几何筛选或换节点中心。

环境为Windows11 x86-64、Ryzen9 8945HX、CPython3.12.14、NumPy1.26.4、Numba0.60.0；OpenBLAS/MKL1、Numba上限4，共享质量host，不是性能样本，无AVX512或新跨平台实测。

```text
python scripts/screen_cinema_current_all_max_unit.py freeze
python scripts/screen_cinema_current_all_max_unit.py contract
python scripts/screen_cinema_current_all_max_unit.py run
python scripts/audit_cinema_current_all_max_unit.py --output artifacts/cinema-current-all-max-unit-independent-v1.json
python scripts/check_cinema_current_expanded_outside_rank.py
python scripts/archive_cinema_current_all_max_unit.py --output report/data/p16-cinema-current-all-max-unit-20261024
```

所有脚本拒绝覆盖旧输出。版本库使用短summary及含原始JSON/数组/日志的ZIP，每成员记录SHA256、CRC32和原始字节数；不把195,076格零数组展开进新JSON。源码、暂存与HEAD原字节逐项核验，父阶段77路径/1,681 ZIP成员审计原件独立保留并消费，不冒称本阶段重新数值验证。下一无目标首解CP仅可另立协议，当前没有CP/PB/solver或默认升级。
