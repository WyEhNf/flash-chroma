# 完整误差预算的整数成本合同与规模边界

Agent：`/root/tail`。Operator：本任务用户。状态：新独立有限合同、唯一完整成本规模普查及离线审计完成；两项资源门超限，按预注册停止，没有建立或求解新的CP。

minL1给出max²48但六项原max_first预算上升的见证后，本阶段研究直接把误差预算放进CP所需的精确成本和规模。全部基线仍是原max_first的0ea0/904e/95cb/5b8、143e完整流，没有借用失败见证的均值预算。旧minL1结果和源码保持原状。静态数学推导见`experiments/p16-cinema-first-budget-cpsat-proposal-v1.md`，本次正式协议是另立的`experiments/p16-cinema-first-cost-census-v1.json`。

对每个完整正支撑输入及全部首级整数AABB状态，真实后缀得到整数平方误差q。目标cap49保留q≤49状态；每点用三个首级delta、q和不同q的onehot选择器即可把八项预算写为整数线性和。mean系数采用`ceil(2^20*(sqrt(q)-sqrt(q0)))`，负差作为保守退款，零差精确0。RMS用精确q-q0；p99用原固定阈值以上计数保护上端秩；CVaR固定原第k大阈值t，用正超额`max(error-t,0)`差的保守ceil成本保护尾均值。固定外部域贡献精确抵消，原60图全部47,185,920像素以整数频数计入，不做浮点权重近似。

执行前冻结四项新源/协议并通过AST。纯整数有理isqrt区间法与独立符号/反复平方比较法在0..50全部2,601根差上相等，包含精确平方、相等和负差ceil；对0..50全部阈值的132,651个CVaR成本再用独立代数和判号核ceil上下边界。46,875组完整加权序列对覆盖零质量、101/201像素、严格非均匀频数，核mean退款、平方和、p99计数和固定阈值CVaR上界，全部通过。没有以double猜根号边界。

唯一完整规模普查重枚举全部70,571点的1,187,079个首级状态，逐项匹配前阶段已独立证明的min/max和安全计数。只删去“整个盒恒安全且所有状态q恒等q0”的约束点；危险点即使安全q恒定也保留cap表，恒安全但成本会变的点全部保留。结果如下：

| 项目 | 实际结果 | 冻结门槛 |
| --- | ---: | ---: |
| 精确恒零成本省略点 | 37,729 | 仅按已证明规则省略 |
| 必须保留约束点 | 32,842 | ≤16,384，失败 |
| 必须保留安全表行 | 975,852 | ≤500,000，失败 |
| 不同成本q选择器 | 93,564 | ≤131,072，通过 |
| 需要q变量的点 | 32,248 | 观察值 |
| 预计整数变量，不含abs | 224,596 | 未实际建模 |
| 预计Q16舍入行 | 98,526 | 未实际建模 |

两个资源门超限，因此按原协议STOP，未抽样删输入、调高门槛或启动真实CP。这个结果只说明当前完整盒的直接预算表示超过本阶段冻结规模，不证明精度目标不可行，也不是OR-Tools实际内存失败。

全域/训练阈值分别为sqrt9/sqrt12，尾大小167,773/471,860，上端秩16,609,443/46,714,060，对应阈值以上完整计数门为167,772/471,859，基线实际164,670/354,337。固定支撑外max²48保持；32,842个保留点中30,785个训练频数为0，但仍完整计入全域质量。八项实际整数成本系数和累计界全部小于2^62-1，最大全域mean累计绝对界134,605,510,994、训练mean界9,982,053,801，未把预算约束当作已满足。

保存数组载荷1,464,881B、前置screen数组1,632,373B、当前可见分块数组载荷峰1,421,176B；分块最大28,925查询。映射输入分别为baseline/reference/suffix各50,331,648B、mass67,108,864B。这些是数组有效载荷和映射范围，未包含解释器、分配器、已释放表达式暂态或OS页缓存，不是进程RSS峰值，更不能推断未来CP的RSS。

离线审计用前置已独立核过的min/max和安全计数重新推导全部保留点、表行和门槛，用第二整数方法核2,550项实际成本池、原143e误差及固定外直方图，全部通过。不同q类别数复用唯一普查数组，未再次完整枚举RGB状态。环境为Windows x86-64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4/Numba0.60.0；共享主机质量窗口，没有吞吐、RSS、新模型或新百图结论。

主要源为`python/lutlab/integer_error_cost.py`、`scripts/check_cinema_first_error_cost.py`及`scripts/census_cinema_first_error_cost.py`；归档`report/data/p16-cinema-first-error-cost-census-20261024`保留执行前身份、有限合同、完整统计数组、实际源和审计，复用原完整支撑/后缀与鲁棒筛查manifest。复现命令使用原环境且禁止覆盖已有原件：

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_error_cost.py --output artifacts/cinema-first-error-cost-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/census_cinema_first_error_cost.py --contract artifacts/cinema-first-error-cost-contract-v1.json --output artifacts/cinema-first-error-cost-census-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_error_cost_census.py --output artifacts/cinema-first-error-cost-census-audit-v1.json
```

下一步若限制节点域、压缩表示或评估此前max48的跨基线Pareto价值，均须另立协议；不能修改本阶段已冻结宽域、超门判定或此前minL1相对max_first的六预算失败。
