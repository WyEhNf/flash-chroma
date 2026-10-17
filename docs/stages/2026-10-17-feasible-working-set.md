# 必要可行性筛查前移与工作集选择

Agent：Codex

Operator：WyEhNf

Task：PR33不可补偿提议的算法修复及精度验证
Status：实现与实验范围冻结，结果执行后补记

## 目标与依据

PR33同中心双箱均无收益。旧排序首先选择35877 B+2，虽将历史缺口预测1579降到1578，但固定该探针时，div2k-0834的SSE即使乐观补偿仍至少增加14。误差来源是候选对保护图的新增支撑与保留坐标的补偿能力不匹配；软排序中的失败项数量不能代替必要可行性。本阶段把该证据转为事前筛查，检查选择修复能否产生实际精度收益，不预设成功。

## 实现和冻结范围

`working_set.screen`接受旧规则产生的全部合法探针，固定一个新坐标幅度，保留三个实际活跃坐标在原±4合法RGB8整数域中自由。用现有`joint_interval.Problem.certificate`对RGB上限、逐图/全域SSE、Q24 mean和尾部计数建立必要界。只有必要界违反保护才排除；对所有未排除探针仍采用旧确定性排名，仅第一个的新节点进入一次联合箱。探针幅度只用于筛查和选节点，最终该变量仍自由±4。无未排除者则停止，不放宽保护、不换候选池或追加试验。

维持PR33同一起点9f65bf5f…、8新节点、B−2/−1/+1/+2、同12节点完整支撑、7857色及101组频数、同保护和质量字典序max²/历史缺口/完整SSE/L1。对照箱直接复用PR33覆盖树及发布SHA，核同中心/域/环境/核心数值源，并用当前独立验证器重放全部证书；没有新对照求解，不把旧时间当本轮时间。只执行至多一个新替换箱，不比较所有工作集。

标准库`verify_working_set_screen.py`从原始SLUT、Q16权重、频数和参考表独立重建每个固定探针的输出区间及必要界，包括未排除者的全部条件；核对筛查计数、顺序、最终提议、旧对照来源。外层再独立重算全部探针真实评分、合法集合/排名，以及每箱完整覆盖和原始保护。旧源审计同源/同范围/同代码，按原回执和SHA复用，不重新解码TIFF/PNG。

## 测试目的、环境和判定

源和计划提交冻结后集中一次9项合同：既有工作集2项、质量目标2项、联合区间3项，加两个针对不可补偿提议的解析样例。新例固定Q16半步权重，证明有局部尾部收益的提议仍会伤害不受保留节点影响的颜色；另核全部提议被排除时返回无替换。没有新增大矩阵或性能测试。

一次正式筛查和至多一个替换箱；只有出现新终态才一次256³/100图/整数oracle/原生scalar与AVX2。没有新模型则保留已有指标，不重复完整测试。归档原始源、全部探针/拒绝证书、新树、旧树原始来源和结果；解压后标准库重放。

Windows11 10.0.26200 / AMD Ryzen9 8945HX 16核32线程 / RAM33605316608字节；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0、Pillow10.4.0。BLAS/MKL/OMP1，Numba4（合同NUMBA_NUM_THREADS=4，正式入口移除该环境变量并显式设4）。局部求解为NumPy整数；完整映射Numba4。原GCC15.2 Release单线程程序SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`，若无新模型不执行原生终验。本阶段目的为精度和正确性，不评价速度。

```powershell
# python为artifacts/error-study-py312/Scripts/python.exe，设置UTF8/PYTHONPATH=python及上述线程环境。
python -m pytest tests/test_working_set.py tests/test_joint_minimax.py tests/test_joint_interval.py -q
# 移除NUMBA_NUM_THREADS，由入口设4。
python scripts/run_joint_interval.py --plan experiments/feasible-working-set-v1.json --output artifacts/feasible-working-set-v1
python -X utf8 -I -S scripts/verify_extreme_cell.py --input artifacts/feasible-working-set-v1 --output artifacts/feasible-working-set-v1/verification.json
python -X utf8 -I -S scripts/report_extreme_cell.py --study screened --input artifacts/feasible-working-set-v1 --output report/data/feasible-working-set-v1 --roundtrip artifacts/feasible-working-set-roundtrip-v1
```

## 工程与边界

从PR33头39c239a建立`codex/feasible-working-set`；fetch后保留主干及337a3dd修复。AGENTS.md只读，运行时、格式、embedded、原资产、构建/锁文件、默认和冠军保留。中文提交和Draft PR交付，操作前检查相关全文/评论/review/行内线程、#7/#8与主题检索。Discussion4最新回复访问缺口保留，不合并或关闭。

距离为RGB欧氏码值，非CIEDE2000。官方数据/Threshold未知；100照片已见，不称盲验。筛查只是必要条件，有限箱最优不代表所有工作集或稀疏表示全局最优，不声称SOTA、四级新模型或实板结果。实际提交、结果、归因和限制执行后补记。

## 已冻结实验及后续解释范围

数值源和计划冻结于ee4d567，9项合同一次通过（1.89秒，无跳过）。一次正式实验筛掉22探针中的8个，选择34821 B+1；一次替换箱881终端覆盖6561赋值，最优仍是基线，无新终态。独立标准库已核全部筛查、探针评分、原对照和替换箱覆盖，未触发新全域/照片/原生终验。

结果产生后另冻结`diagnose_screened_working_set.py`，只将已独立验证的互斥覆盖树限制到新坐标每个合法值，统计剩余三坐标组合的必要拒绝原因和质量剪枝。每个条件切片必须完整覆盖729赋值；必要界拒绝与目标不优分开计数，不能把quality剪枝当成不可能可行。此解释不生成模型或重算像素、不新增拟合/扫描；首个见证的分组统计依赖遍历顺序，不是最小冲突集。解释源、执行后输出与数值实测快照分开记录。
