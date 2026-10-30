# 全正支撑的鲁棒危险筛查

Agent：`/root/tail`。Operator：本任务用户。状态：有限穷举、完整筛查和独立重放完成；没有运行新的CP求解，没有新模型晋级。

首轮CP把116个旧max50热点降到34，却在完整70,571正支撑产生285个越cap旁侧点。本阶段继续从原max_first（0ea0/904e/95cb/5b8，143e完整流）出发，完整识别86个首级节点各RGB分量±2与[0,255]相交的整数盒中，哪些输入可能越过max²49。没有把首轮失败节点当作新基线，也没有只把那285个已见反例追加成训练集。

对每个输入，实际Q16四面体的非负权重和为65536；完整原acc保留固定角贡献。将86个选中节点同时取各分量下界与上界，得到首级输出RGB的精确整数端点；逐点完整枚举端点AABB，经固定904e/95cb/5b8后缀计算全部最终误差。盒中所有结果d²≤49足以证明该输入对整个节点盒恒安全；发现某项>49只把它列为可能危险，不能据此判定某个联合节点候选一定失败。

这里单个输入的AABB还可以说明得更强：每个输出分量从全下界走到全上界，依次将一个整数节点分量加1。每一步acc增加不超过65536，舍入输出只会增加0或1，因此会经过两端之间的全部整数。RGB三个节点分量的域相互独立，所以逐点没有整数RGB空洞；不同输入仍共享节点，逐点可达不能推出联合可达。17/33两种有限模型含共享节点、固定角和0/255截断，分别完整枚举2,025及15,625种节点赋值，逐点可达集合、端点盒和危险统计相等。

完整结果如下：

| 项目 | 结果 |
| --- | ---: |
| 固定选中物理节点 | 86 |
| 全部受影响RGB8输入 | 70,571 |
| 第一遍完整AABB查询 | 1,187,079 |
| 对整个节点盒恒安全的输入 | 68,347 |
| 可能危险输入 | 2,224 |
| 危险点保留的全部安全RGB三元组 | 126,765 |
| 没有安全三元组的危险点 | 0 |
| 正支撑外固定最大平方误差 | 48 |
| 原116个max50热点遗漏 | 0 |

预声明资源门是最多8,192危险点、1,000,000安全三元组且空表为零，本次全部满足。门内第二遍保存危险点全部安全三元组CSR，不按照片或候选结果删减。CSR数组有效载荷406,991B；端点数组3,810,834B，8角支撑设计18,066,176B，三者不是进程RSS峰值。完整后缀50,331,648B和已认证正支撑复用前阶段原件，没有把这些研究暂态算成免费的运行时表。

全部211,713个输出分量行的Q16权重、完整acc、端点acc及域乘积范围都审过保守signed int64界2^62-1。实际最大Q16权64389、原acc2502799、端点acc2505817、舍入行绝对乘积和界262144。独立四角uint64对141,142行端点与原首级输出逐项相等；另一实现按每点盒尺寸展开RGB、512源点一块，完整重算1,187,079项、全部危险点和全部安全CSR，最大块28,925查询，零不一致。

环境是Windows x86-64共享主机、Python3.12.14、原NumPy1.26/Numba0.60环境。此处是离线质量证书，执行窗口与其他代理质量工作可并行，没有任何吞吐、prepare计时或RSS结论。协议`experiments/p16-cinema-first-risk-v1.json`、实现`python/lutlab/channel_first_risk.py`、主脚本`screen_cinema_first_risk.py`和独立审计`audit_cinema_first_risk.py`均冻结实际SHA。证据归档目标为`report/data/p16-cinema-first-risk-20261024`，复用前阶段完整后缀/支撑manifest。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_risk.py --output artifacts/cinema-first-risk-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/screen_cinema_first_risk.py --contract artifacts/cinema-first-risk-contract-v1.json --output artifacts/cinema-first-risk-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_risk.py --study artifacts/cinema-first-risk-v1 --output artifacts/cinema-first-risk-independent-v1.json
```

这组结果允许下一个独立试验对所有2,224危险点施加完整AllowedAssignments，同时用恒安全证书保护其余68,347点、用固定外部直方图保护余下全域。它没有证明这些危险点能共享同一套节点实现，也没有证明mean、RMS、p99或CVaR预算可满足。后续最小节点L1只是减小扰动的代理；是否通过原八项绝对预算仍须一次完整验解。表约束和纯整数建模参考Google官方[CP-SAT说明](https://developers.google.com/optimization/cp/cp_solver)及[AllowedAssignments示例](https://developers.google.com/optimization/assignment/assignment_groups)，这里的鲁棒筛查和Q16完备性证明是针对本模型推导，并非官方库提供的精度保证。
