# 反例驱动的整数区间联合求解

Agent：Codex；Operator：WyEhNf；Task：PR30后续联合优化；Status：In Progress（执行前冻结，结果待补）。

## 问题、范围与算法

PR30的358次条件评分没有找到保护通过的max52模型；不能从4个贪心前缀推断联合箱无解。本阶段保持PR29已测终态和全部保护，用有完整覆盖证书的小型联合求解替代逐个辅助的选择，重点区分贪心漏解与限定变量本身不足。

原模型SHA为`4fe0dfd4b512e0a17996c5786339a84a452d62c8e05c07bc1256bd685c743cac`。从PR30主改节点开始，依次加入最少失败三节点反例的残余前5颜色中全部正权重节点，再加入该三节点块的其他节点，完整去重；超过4节点停止，不截断。没有手填节点ID或根据新验收结果重选。所有变量是原值±4内的合法B节点，R/G、权威idx/frac及其他节点不变。

扩大单辅助±2到一次联合±4有具体原因：已冻结反例[255,255,49]的节点35909/35910权重42129/23407，B原值113/109。原整数和7311940，主改−2后为7227682；保持输出至少112需整数和≥7307264。因此只靠相邻35910抵消该色至少要+4，±2局部辅助不足。这里同时允许所有导出节点协作，不强制逐色无损或手动固定原主改，以完整逐图/全域预算验收。

`joint_interval.py`以完整Q16非负权重求每个未完成分支的RGB8输出上下界；将目标B裁入该整数区间，再加固定R/G误差，得到逐色平方误差必要下界。任一色的下界大于目标max、任一逐组/完整域SSE下界为正、mean的Q24差值下界为正、或固定p99/max端点计数下界超预算，都可严格拒绝整个分支。mean使用新下界减旧上界，仅在严格为正时剪枝；不靠浮点容差、近似梯度或忽略舍入。

每个节点域按绝对变化、符号确定性排序，DFS覆盖联合整数箱；已经找到完整保护通过解时，可剪掉最小可能L1不优于该解的分支。真实叶子再走独立于必要界的真实Q16条件评分，固定保护通过者才走全部原历史/混合预算/CVaR和缺口验收。求箱内达到floor(旧max)-1且满足全部保护的最小L1解，平局保留首次确定性解，不声称平局时mean或max最优。没有可行解则保留旧终态。最多4节点、10000赋值；这是一个冻结整数问题的求解，不做外层参数/方法/网格扫描。

每个终端记录前缀、覆盖赋值数和必要界见证；完整叶子保留评分/接受或拒绝。`verify_joint_interval.py`仅用标准库独立解析SLUT、从父反例重建变量/整数域，核每个剪枝证书、叶子实际舍入与原保护回执，检查终端互斥、遍历顺序和覆盖数等于整个笛卡尔积；只有这项证明完成后才能说箱内不可行或最小L1。不能据此证明箱外、其他轴表或全域模型最优。

## 环境、阶段验证与复现

复用PR30同字节支撑/照片频数，验证原模型、结果、源表、环境、支撑、矩阵及反例SHA，不重复解码80张PNG。80完整图+既定选择样本共101组；20历史审计只在最终新模型完整100图中观察，已见数据不称盲验。标准库复核不独立解码PNG。

集中必要合同6项：3个新解析例，分别要求必须三节点联动、RGB非平方距离及half-up边界下与独立小整数枚举的最小修改一致、相邻两码值跳变在限定箱无解；回归3个原条件补偿合同。冻结源/计划/合同后只运行一次，具体失败才保存日志并定向修复。

环境沿父测量：Windows11 10.0.26200、Ryzen9 8945HX 16核32线程、RAM33605316608字节；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0；BLAS/MKL/OMP1、Numba4。新求解器为NumPy整数，无MILP/浮点求解依赖；本次目的为联合精度和证明正确性，不作计时性能比较。若选中新模型，仅一次完整256³、100图、独立NumPy整数oracle及原生GCC15.2 Release单线程scalar/AVX2终验，既有程序SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`。没有新解则不重复完整终验。

```powershell
# 使用artifacts/error-study-py312/Scripts/python.exe及上述UTF8/线程环境。
python -m pytest tests/test_joint_interval.py tests/test_automatic_compensation.py -q
# 移除NUMBA_NUM_THREADS，由runner设置4。
python scripts/run_joint_interval.py --plan experiments/joint-interval-v1.json --output artifacts/joint-interval-v1
python -I -S scripts/verify_extreme_cell.py --input artifacts/joint-interval-v1 --output artifacts/joint-interval-v1/verification.json
python -I -S scripts/report_extreme_cell.py --study joint --input artifacts/joint-interval-v1 --output report/data/joint-interval-v1 --roundtrip artifacts/joint-interval-roundtrip-v1
```

## 工程、协作与未完成事项

从PR30头7cc4893建立分支，fetch确认main仍dec1020且为祖先，工程修复337a3dd保留，AGENTS.md只读。创建/更新Draft PR前刷新父PR及相关正文/完整评论/review/行内线程、#7/#8和主题检索，Discussion4访问缺口保留；不合并、不关闭议题。每阶段中文提交/说明/PR，Operator为WyEhNf。

默认/冠军、运行时、模型格式、embedded和硬件后端不变。无官方数据/Threshold；指标为RGB欧氏码值，非CIEDE2000。单级有限研究不能当作四级ISP、未知照片泛化或实板成绩。数值结果、证明覆盖、实际提交及CI将在执行后补记。
