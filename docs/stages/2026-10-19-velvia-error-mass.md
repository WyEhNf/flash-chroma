# Velvia残差分布：均值和尾部需要分别处理

Agent：Codex；Operator：WyEhNf；状态：本地只读归因完成。不PR、不推送。

目标是判断几个饱和热点能否代表整体照片残差。仅比较旧已验收2dd输出流与同SHA原表，按完整cube均匀测度和60训练图全部47185920像素频数聚合；没有加载模型重新映射、生成候选或计时。Windows11/Ryzen9 8945HX/Python3.12.14/NumPy1.26.4，BLAS/MKL/OMP=1；原生后端不适用。

60图mean为0.900275；78.785%的误差和来自RGB距离≤2，92.642%来自≤3；即使把全部>7的误差清零，mean最多改善0.871%。照片误差有23582个非零3D单元，最大的单元只占1.737%，需3810个单元承载90%误差和。这支持优先分析广泛小误差，不能仅修几个max反例，也不能因此把所有小误差都归为纯量化错误。

G236..255承载cube尾部27.643%，却只承载照片误差和3.120%。全部消除该区域误差的60图mean改善宽界为3.120073%；若只移动两个G内结点且节点/端点平面固定，G255不变，扣除后上界为2.909466%，不足3%。后一结论不能套用全局节点重新拟合，也不能替代20选择图/100图的验收。

复现命令：`artifacts/error-study-py312/Scripts/python.exe scripts/explain_velvia_error_mass.py --output artifacts/velvia-error-mass-v1-replay`。完整中文报告、输入/源码SHA、全768码值和96轴区间、32³单元压缩数组及质量守恒见`report/data/velvia-error-mass-v1`。主要脚本`explain_velvia_error_mass.py`与其快照绑定，不修改既有拟合或运行时。
