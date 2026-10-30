# 固定前缀max57下界与局部MILP原件

对应[阶段说明](../../../docs/stages/2026-10-24-cinema-fixed-prefix-bound.md)。`pair-certificate.json`含七gold球交、两个原色的独立Python整数轨迹、参考源编号、226>224的精确见证；`milp-summary.json`保留首轮infeasible与冻结预算停止。`evidence.zip`包含所有run/contract/progress/summary、实际执行源码及两个预冻结计划；manifest逐成员核SHA/CRC。

完整861行支撑、当前模型和上界验证复用`report/data/p16-cinema-arrival-budget-v1/evidence.zip`，不重复大数组或照片。固定前两级的下界不能外推至可改变它们的模型族；求解器失败不等于全局不可行。

使用原Python环境，设PYTHONUTF8=1及BLAS/MKL/OMP=1，输出目录须不存在：

```powershell
python scripts/check_integer_last_milp.py --output artifacts/cinema-last-milp-v1-contract.json
python scripts/run_cinema_last_milp.py --contract artifacts/cinema-last-milp-v1-contract.json --output artifacts/cinema-last-milp-v1
python scripts/certify_cinema_arrival_pair.py --output artifacts/cinema-arrival-pair-bound-v1.json
```

实际source/input SHA和环境在ZIP run中。没有新模型、性能、指定服务器或实板成绩。
