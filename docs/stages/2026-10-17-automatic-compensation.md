# 自动条件补偿与误差冲突分析

Agent：Codex；Operator：WyEhNf；Task：PR29后续算法研究；Status：In Progress（执行前冻结，结果待补）。

## 目标与冻结范围

PR29终态全域max为53，固定单元必要界仍为42。上一阶段证明两个节点的整数舍入输出及SSE收益不能相加；本阶段把节点选择与补偿方向自动化，找出继续降低峰值时到底受哪些颜色/照片预算阻碍。仅研究一个已测Velvia模型，不改变默认模型、运行时、硬件后端或模型格式。

起点为PR29 `397cc3679f6b9cc4b92742bcdc57a92c5e47c568`，模型SHA `4fe0dfd4b512e0a17996c5786339a84a452d62c8e05c07bc1256bd685c743cac`。`local_study_snapshot.py`将父终态的完整频数重建为后续状态视图，保留原历史阈值/混合预算，不能把该转换称为新测量。

`automatic-compensation-v1.json`冻结：从首个已记录最坏RGB自动取所在单元及残差最大通道，以floor(max)-1为目标，一次MILP求该通道±4内最小L1整数修改。求解候选必须重放整个单元；其余通道固定误差计入RGB半径，Q16舍入上下界保留严格整数端点。

自动辅助池为主改节点一格Chebyshev完整邻域，排除已修改节点，不写死任何节点ID；超过64节点/4096单元色/131072支撑色即停止，不静默截断。一次枚举全部节点的完整非零支撑、建立101组照片频数。候选每个合法RGB通道取-2/-1/+1/+2，直接计算联合Q16输出，再按是否降低max、固定保护失败数、max平方、历史缺口、总L1及节点/通道/幅度确定性排序。候选排序保留原混合预算之外的全部固定保护，最终取前4逐一走原完整保护；全部不可行才对每个实际前缀取第二辅助前2并去重，最多8个。不能用单改收益或预算相加代替条件评分。

全部原历史/固定起点101组和完整域mean/RMS/p99端点/max/CVaR、历史缺口不升保持；只有通过保护且全域max严格下降才能选中。按全域max、历史缺口、修改节点数、名称选择一次，再观察完整100图。没有选中则保留旧终态和所有拒绝，不扩大搜索。

## 正确性和阶段测试

`verify_extreme_cell.py`延续完整支撑、逐组/完整频数、原历史及固定保护、选中逻辑、42整数必要界和原生模型/输出绑定。新增纯标准库`verify_automatic_compensation.py`独立解析节点及权重，重算所有合法辅助的真实条件分数、完整排序、前4/前2及去重树；主改只独立验证整数可行性，不独立声称证明MILP最小L1。频数复核不独立解码80张PNG；生成入口核对原始文件/像素及既定采样哈希。

集中必要合同为新条件选择/必要第二辅助/通道主改及越界拒绝3项，回归既有局部最小最大3项和有符号mean差值2项，共8项。冻结源码/计划/合同后执行一次。若有具体失败，保留日志，只做针对性修复。若选中，执行一次256³/100图、独立NumPy整数oracle和原生scalar/AVX2完整逐字节；无选中不重复完整域。归档再解压独立重放局部证据。20审计照片只最终观察，已见过，不能称独立盲验。

实际环境固定：Windows11 10.0.26200，Ryzen9 8945HX 16核32线程，RAM33605316608字节；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0。BLAS/MKL/OMP=1；合同NUMBA_NUM_THREADS=4，研究入口移除此变量并自行设4；局部NumPy整数，完整Numba4。原生GCC15.2 Release单线程scalar/AVX2，既有程序SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`。目的为精度/联合可行性与正确性，不作计时性能比较。

```powershell
# 使用artifacts/error-study-py312/Scripts/python.exe，并设置上述UTF8/线程环境。
python -m pytest tests/test_automatic_compensation.py tests/test_local_minimax.py tests/test_histogram_delta.py -q
# 移除NUMBA_NUM_THREADS，runner自行设置4。
python scripts/run_automatic_compensation.py --plan experiments/automatic-compensation-v1.json --output artifacts/automatic-compensation-v1
python -I -S scripts/verify_extreme_cell.py --input artifacts/automatic-compensation-v1 --output artifacts/automatic-compensation-v1/verification.json
python -I -S scripts/report_extreme_cell.py --study automatic --input artifacts/automatic-compensation-v1 --output report/data/automatic-compensation-v1 --roundtrip artifacts/automatic-compensation-roundtrip-v1
```

## 协作与限制

main祖先及337a3dd工程修复保留，AGENTS.md只读。创建/更新Draft PR前刷新相关PR正文、完整评论/review/行内线程、#7/#8及主题检索；Discussion4读取缺口如实记录。不合并、不关闭问题。中文提交和阶段PR，Operator为WyEhNf。

官方数据及Threshold仍未取得；所有误差是RGB欧氏码值距离，非CIEDE2000。本阶段有限邻域失败不能证明没有其他联合可行解，局部42必要界不能当成整个色域的可达最优；单级结果不能冒称四级ISP或实板收益。实际结果与提交在执行后补入。
