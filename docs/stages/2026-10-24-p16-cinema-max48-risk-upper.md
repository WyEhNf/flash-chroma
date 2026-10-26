# 当前122个首级节点完整风险与公共误差上界

本阶段固定已验收的741e55f首级、904e/95cb/5b8后缀以及实际RGB8逐级舍入语义，从当前145个max²48输入触及的122个物理首级节点出发，仅证明有限±2节点盒中的条件质量上界。完整筛查通过预注册资源门；若共享节点赋值能满足全部安全表，则其全域max²最多43，全域mean/p99均不劣于373a综合最佳模型。尚未求解共享节点赋值，没有新模型、照片选型或性能结论。

Agent：`/root/tail`；Operator：本次16题优化任务的用户；状态：本阶段证书与归档完成，后续共享求解及完整验收待做。相关提交以本阶段文档所在提交为准，成果继续保留在精度研究分支、Draft PR90中，不切换默认模型。

## 固定起点、实际范围与资源门

首级NPZ SHA为`741e55f55c674384543511dc20b98ecd7d6a1ed4c1b9bb17406cabd7cc86bea0`，完整整链流SHA为`de4a98d5f3b3d430e349e83146d211296a4e6b3e2a9664a5806b321384a3c3f9`。后缀完整查表SHA为`0ced3cb5f1acad4ff15d392dfc52bf44af8e99807afc9b62ee7cb5625392a3d1`。全部模型、真值、原60图整数频数及三个分母直方图的完整路径/SHA保存在`run.json`，模型实体复用已提交的[三分母完整质量归档](../../report/data/p16-cinema-max48-pareto-quality-20261024/manifest.json)。

122个节点的366个RGB分量相对741e55f取±2闭区间，并在0/255处裁剪；轴、Q16坐标、其他节点与后缀不变。完整正支撑重新构造，并独立扫描全部16,777,216个输入验证，没有沿旧70,571或47,013集合删样。每个受影响输入的首级RGB整数AABB都完整枚举，未选角贡献保留在原acc中。目标cap为q≤47；RGB整数平方和不可能等于47（模8平方余数只能为0、1、4），因此等价于q≤46。

某输入的整个AABB都满足cap，是它对该节点盒恒安全的充分证书；AABB含超限状态仅标记可能危险，不证明该状态在共享节点耦合下可达。危险点保存全部安全首级RGB三元组；零安全表会否定此盒，危险点超过8192或安全表总行超过1,000,000即STOP，不删点或改门。

| 项目 | 实际值 |
| --- | ---: |
| 完整正支撑输入 | 80,751 |
| AABB全状态 | 2,102,192 |
| 全盒恒安全输入 | 75,766 |
| 可能危险输入 | 4,985 |
| 危险点安全三元组 | 386,612 |
| 零安全表 | 0 |
| 支撑外固定max²（全域/训练） | 41 / 41 |
| 受影响原60图像素频数 | 901,853 |
| 两端点独立uint64重放输入数 | 161,502 |
| 两端点差异 | 0 |

资源门全部通过，145个当前max48输入全部包含在危险集中。保存数组payload共12,534,933B，安全CSR payload为1,219,664B；这些是数组字节账单，不能当成进程RSS或部署内存。最大端点acc为5,274,195，最大未舍入跨度262,144（4Q）。

## 条件上界及三个分母

对每个受影响输入取其所有安全状态中最大的q，支撑外保持固定原q，得到悲观误差直方图。任何真正共享节点赋值，只要满足所有危险点的安全表，其逐输入q都不大于这份直方图对应值。因此它给出所有安全解的充分质量上界。逐点选中的最坏状态不一定能由同一组节点实现；本阶段没有证明安全共享解存在。

这份条件上界的max²为43，强于预设cap47。以下为上界本身的数值，不能标成新模型实测：

| 指标 | 完整RGB域 | 原60图整数频数 |
| --- | ---: | ---: |
| 像素数 | 16,777,216 | 47,185,920 |
| mean | 0.8059398455 | 0.7107271249 |
| RMS | 1.2131725481 | 1.2046641359 |
| p99 | √12 | √17 |
| max² | 43 | 43 |
| CVaR最差1% | 4.2539853886 | 5.0687150959 |

下表列出条件cap一旦实现后，哪些指标无需额外预算约束即可得到充分保护。“未自动保护”只说明此悲观上界不足以担保，不能据此断言任何实际安全解必退。

| 分母 | 完整RGB域自动保护 | 原60图自动保护 |
| --- | --- | --- |
| a399共同起点 | mean、RMS、p99、max、CVaR | mean、RMS、max |
| 373a综合最佳 | mean、RMS、p99、max | max |
| 741e55f当前质量点 | max | max |

373a综合最佳的全域mean为0.8225028465，训练mean为0.6990079845；741e55f当前点分别为0.7996658981、0.6823633098。后续若以共同综合最佳为预算，仍必须披露相对741更低均值的代价，不得把本阶段严格局部预算失败改写为通过。原[直接八预算CP阶段](2026-10-24-p16-cinema-first-direct-budget.md)与[741独立三分母质量阶段](2026-10-24-p16-cinema-max48-pareto-quality.md)的结果保持原样。

mean与CVaR采用scale=2³²的整数根上下界，配合等根式系数精确判等；RMS比较整数平方和，p99核对完整整数秩与根区间，max比较整数q。浮点数只用于显示，不决定充分证书。所有累计根界均审计整数总界。CVaR定义为ceil(N/100)个最差像素的欧氏误差均值。

## 验证、环境与复现

本阶段测试目的为数学/格式合同、有限盒完整性和数据完整性，不是运行时速度。执行环境为Windows11 x86-64、Ryzen9 8945HX、CPython3.12.14、NumPy1.26.4、Numba0.60.0；OMP/Numba4线程，OpenBLAS1线程。质量执行共享主机，未作计时结论，无AVX512。未改变原Python环境，也未调用OR-Tools。

新有限合同覆盖全安全、混合、空安全表、单值及0/255盒，共5点；完整遍历24种均匀/整数权重误差选择验证直方图支配，检查0..66与195075的整数根界以及不同直方图的等根式。完整执行冻结29份源和17项输入，冻结SHA为`2390f0f477b7298127d5bc1cb797e7c2db4a78f366804e3126807f69559e6756`。

独立审计用逐点flatten方式重新枚举全部2,102,192个状态，而非复用主程序125偏移次序，复核min/max/safe_count/safe_max、完整安全CSR、固定外域以及六组上界和严格比较。完整正支撑核、原整链流重放、两个节点端点uint64重放均通过。

原始执行命令使用原项目隔离Python，并令`PYTHONPATH=python`、`OPENBLAS_NUM_THREADS=1`、`OMP_NUM_THREADS=4`、`NUMBA_NUM_THREADS=4`；各脚本的`--help`给出路径参数。已完成阶段的关键命令为：

```text
python scripts/check_cinema_max48_risk_upper.py --output artifacts/cinema-max48-risk-upper-contract-v1.json
python scripts/screen_cinema_max48_risk_upper.py --frozen artifacts/cinema-max48-risk-upper-frozen-v1.json --contract artifacts/cinema-max48-risk-upper-contract-v1.json --output artifacts/cinema-max48-risk-upper-v1
python scripts/audit_cinema_max48_risk_upper.py --stage artifacts/cinema-max48-risk-upper-v1 --output artifacts/cinema-max48-risk-upper-independent-v1.json
python scripts/archive_cinema_max48_risk_upper.py --output report/data/p16-cinema-max48-risk-upper-20261024
python scripts/audit_tail_git_evidence.py --git-ref HEAD --output artifacts/cinema-max48-risk-upper-head-audit-v1.json
```

源与输入冻结记录、有限合同、run、summary及独立审计作为raw JSON保留；`source.zip`包含29份执行冻结源和归档器，`support-evidence.zip`含完整screen、危险安全CSR和执行日志。manifest逐项记录原字节SHA，所有raw/source先设置`-text`再显式暂存，Git HEAD审计核实际blob及ZIP成员，避免CRLF转换改变证据。

## 边界与下一步

本阶段未建CP、拟合、生成候选或重跑照片，不证明每个单点安全状态能够共同实现，不含100图质量或性能资格。原60图的mean/p99也不能自动担保另外100图逐图结果。后续仅可另立固定综合best分母的训练mean/p99两预算桥，先检查预定资源门，再决定是否构造一次受限整数模型；任何候选仍须独立完整域、100图及三个分母的逐图验收，并在实际后端验证速度至少50%。
