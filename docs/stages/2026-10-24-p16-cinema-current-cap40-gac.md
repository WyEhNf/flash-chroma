# 固定cap40模型的无搜索GAC删值与独立重放

Agent：`/root/tail`。状态：唯一传播及独立重放完成，结果为 **GAC未判定**；没有矛盾证书、可行解或新模型，不据此启用混合半径。原CP唯一INFEASIBLE保持为该固定有限编码的solver状态，不被本阶段解释成局部区间冲突或全局无解。

唯一输入为已独立核全部Q16、节点clip、完整acc及74,081安全行的`f492e49…`问题，仍是273节点±1、819节点分量、4,058张完整cap40表。该数学输入不依赖solver状态。每point每channel最多4个不同节点分量、至多81赋值；先合并重复同变量系数，完整原acc保留固定角，再用half32768舍入得到输出delta。三个通道节点分量不重叠，因此可以精确按通道枚举局部赋值、筛完整安全RGB表，union仍有支持的节点值。

主程序以固定FIFO反复删除不受某point任何有效赋值支持的节点值，不分支或试探。每条记录含原因point、变量、删值及前后域mask。独立checker从原初域按顺序以另一列表笛卡尔实现重算无支持性，不信主程序支持mask；最后另外检查所有point已经达到非空固定点。

| 唯一实际传播与检查 | 结果 |
| --- | ---: |
| point修订／预定门 | 5,360／131,072 |
| 主程序局部赋值／预定门 | 710,626／33,554,432 |
| 合法删值／预定门 | 88／2,457 |
| 独立重放局部赋值 | 537,901 |
| 删值原因point／变量／物理节点 | 59／320／111 |
| 空域或常量空表矛盾 | 未得到 |
| 最终状态 | `GAC_FIXPOINT_UNDECIDED` |

88条删值是有效缩域证据，但111个理由节点不是矛盾证书，不能据此构造已授权条件下的混合±2域。非空固定点也不是SAT。该方法只完成有界一致性过滤，没有搜索、ORTools、NumPy、新RGB或照片查询。session85542完整exit0后释放CPU，无扩大门或重跑。

执行前10个有限案例逐point核全部联合笛卡尔支持与通道分解相等，并穷举所有实际全局解均不被删除。覆盖half三边、0/255及固定角、共享矛盾、跨point级联、强制非零、重复系数、常量空表和跨channel变量重叠拒绝。还特设三色奇环：穷举全局无解，但GAC仍非空固定点，确保实现不会把未判定当可行。有限合同没有调用CP或其他搜索器；小域全枚举仅用于正确性检查。

冻结SHA `5f780288ddf7eb206acc966ffa7ccc473c42340006a76a356e5b4756482c623c`含37源，父独立数学审计pass与同f492问题在冻结时明确绑定；有限合同`add1105a…`。真实删值记录SHA `8fcc8f96a903aa392ece6e3e0c26da3b52b799703f98e295af23559832a72b6e`（24,555B）；独立重放SHA `5c481f7817b589bca26ca67f53da0c1dfcd5f7c83039c34a80500946f409ccdd`（5,772B）。未修改原CP或已执行的旧阶段源。

文献启发是检查值是否仍有support并保留有效表。[Mackworth的作者机构书目页](https://www.cs.ubc.ca/~mack/Publications/b2hd-AI77.html)确认1977年的一致性研究出处，本次未完整读取其原PDF；不据此声称复现原算法。[Compact-Table作者原文](https://arxiv.org/html/1604.06641v1)的GAC定义和第6节描述支持过滤、表维护及bitset。本项目使用独立通道Q16分解与3值mask，未实现CT完整reversible sparse bitset、residue或回溯结构，也不套用论文的速度结果。

环境为Windows11 x86-64、Ryzen9 8945HX、CPython3.12.14，标准库纯整数；无原生编译、BLAS、Numba执行或性能样本。其余源码只作为冻结身份读取，不因源码快照包含依赖就称本阶段执行了那些环境。

```text
python scripts/run_cinema_current_cap40_gac.py freeze
python scripts/run_cinema_current_cap40_gac.py contract
# 真实传播独立授权后仅一次
python scripts/run_cinema_current_cap40_gac.py run
python scripts/run_cinema_current_cap40_gac.py audit
```

脚本拒绝覆盖原件。原始10合同、88条删值前缀、独立固定点重放和日志仅入ZIP，逐成员记录SHA256/CRC32/字节数，外置短summary。增量HEAD复用原cap40不可变证据及父图阶段收据（15个白名单对象、23ZIP成员、12来源行；不冒称其包含父提交另外的attrs与字节补记）。下一步只静态检查历史是否已有相同box或(prefixRGB,goldRGB)去重机制，不自动提高旧4194304门或展开新规模实验。
