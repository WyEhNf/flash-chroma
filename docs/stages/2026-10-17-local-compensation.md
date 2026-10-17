# 热点主改与邻近节点的重叠联合补偿

Agent：Codex；Operator：WyEhNf；Task：PR #28 后续；Status：In Progress（方案及源码先冻结，再执行有界对照）。

## 阶段问题与算法

PR28证明最坏单元在当前固定轴表下的整数RGB最小最大误差恰为42，但降低峰值的候选会损害照片。最小修改35909 B115→113可使推导全域max54→53、主缺口1585→1582，却令div2k-0900/div2k-0889/kodak-kodim03的SSE分别增加3307/1023/2322。它们及对应选择样本的mean/RMS固定保护失败，未被接受。

PR25曾由相邻节点35910 B106→107改善同三图，为补偿方向提供依据；当前模型已不同，旧收益不能相加。本阶段从PR27同字节模型`f577f0749f7aae56275774d0bdbaad9305d99652ca08ba21cc928c8ff84962c4`起步，固定主改35909 B115→113，只比较辅助35910当前B107加1、加2两个幅度。两节点在同一原模型上同时修改，并保留基线、主改单独、两种辅助单独和两种联合共6个反事实。

`local_compensation.py`提供有限冻结块的候选族，检查节点前值、合法幅度及RGB8范围，不隐式裁剪/uint8绕回。所有候选保留权威idx/frac与其他节点字节。选择只允许联合块，不能把辅助对照当作主改已修复。没有扩大主节点、辅助节点、网格或参数矩阵。

重叠支撑使RGB8舍入及SSE都不可直接相加；runner真实重放每块，记录`joint-(primary+helper-baseline)`的输出差异、完整域及101组SSE交互。不会把两份单改预算相加当作联合可行性证明。旧主改单独的模型SHA、全部频数、指标及拒绝必须逐项复现PR28，空修改基线必须通过全部保护。

## 固定验收与复现

`experiments/local-compensation-v1.json`在执行前冻结。热点单元仍为648色，其8个正权重节点再并入相邻辅助节点；一次枚举整个节点集的完整非零支撑，并一次建立80完整照片/既定选择像素/合并101组频数。20历史审计不反馈，只有最终选中模型才观察完整100图。数据已见过，不能称盲验。

原历史目标和预算保持，固定参照仍是PR27起点的101组/完整域mean、RMS、p99端点、max及CVaR；主缺口不升，全域max严格下降。只从两联合块中按完整域max、历史缺口、节点数和确定性名称选一个；如果均失败，不进一步扩充候选。独立标准库验证器重建冻结候选、权重/舍入、完整支撑、频数、交互及选择，包含原生模型/程序/输出绑定；不独立解码80张PNG。

选中后只执行一次完整256³/100图、独立NumPy整数oracle、既有单线程标量/AVX2终验。完整分布必须匹配局部完整频数，80反馈图指标也须逐项匹配。未选中则复用同字节PR27旧终态，保留拒绝。下界42直接复用PR28证书并独立复核，不重新执行LP/MILP。

集中6项必要合同：1个真实重叠Q16例验证单改受损、联合补偿、非可加输出及陈旧前值拒绝；回归原短直方图/101组空修改入口1项及CVaR4项。其他未改模块不重复堆测试。验证前冻结源/计划/合同；具体失败才做保留日志后的定向修复。

环境沿PR28：Windows11 10.0.26200 / Ryzen9 8945HX（16核32线程）/ Python3.12.14 / NumPy1.26.4 / SciPy1.15.2 / Numba0.60.0 / llvmlite0.43.0。合同NUMBA_NUM_THREADS=4；数值入口移除此变量并自行设4；BLAS/MKL/OMP1。局部映射为NumPy整数，选中后的完整映射为Numba4；原生GCC15.2 Release单线程标量/AVX2，程序SHA ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a。目的为联合可行性、舍入交互与误差转移，不比较性能。

```powershell
# python使用artifacts/error-study-py312/Scripts/python.exe；先设置上述线程/UTF8环境。
python -m pytest tests/test_local_compensation.py tests/test_local_minimax.py::test_guard_assessment_accepts_unchanged_short_histogram tests/test_cvar_guard.py -q
# 移除NUMBA_NUM_THREADS，由runner设置；输出拒绝覆盖。
python scripts/run_extreme_cell.py --plan experiments/local-compensation-v1.json --output artifacts/local-compensation-v1
python -I -S scripts/verify_extreme_cell.py --input artifacts/local-compensation-v1 --output artifacts/local-compensation-v1/verification.json
python -I -S scripts/report_extreme_cell.py --study compensation --input artifacts/local-compensation-v1 --output report/data/local-compensation-v1 --roundtrip artifacts/local-compensation-roundtrip-v1
```

## 协作与边界

已fetch，main仍dec1020且为祖先，基于PR28头d738508建立工作分支；337a3dd工程修复保留，AGENTS.md只读。创建/更新PR前刷新相关正文、完整评论/review/行内线程、#7/#8及近期检索，保留Discussion4访问缺口，不合并/关闭。每阶段中文提交、说明、Draft PR，Operator为WyEhNf。

无官方数据或Threshold；距离为RGB欧氏码值，非CIEDE2000。不修改默认/冠军、运行时、模型格式或硬件后端。这是单级局部研究，不代表四级新模型、未知照片泛化或实板性能。阶段结果、实际来源、拒绝或收益及CI在执行后补入。
