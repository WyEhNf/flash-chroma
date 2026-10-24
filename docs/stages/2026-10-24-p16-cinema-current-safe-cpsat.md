# 当前122节点完整安全minL1：唯一20秒求解未决

本阶段固定当前741e55f模型的122首级节点±2/clip，保留4,985个危险点的全部386,612个安全三元组，寻找使完整RGB域max²≤43的共享节点赋值。有限全集、实际Q16问题及独立预检全部通过；唯一单worker、seed20261024、20秒minL1搜索返回UNKNOWN，无incumbent。按预注册停止，没有新模型、照片选型或性能结论，UNKNOWN不能解释为无解。

Agent：`/root/tail`；Operator：本次16题优化用户；状态：本轮有界试验完成，目标未获解。原件保留在精度分支及Draft PR90，不替换默认模型。相关提交以本阶段文档所在提交为准。

## 与前序预算表的关系

[公共训练两预算桥](2026-10-24-p16-cinema-max48-training-bridge.md)的608,964行超过预定500,000门，已经STOP且不改判。本阶段是不同表达：只复用[原fullrisk门已通过的完整安全表](2026-10-24-p16-cinema-max48-risk-upper.md)，不内嵌全部训练mean/p99成本表，沿用8192危险点/1,000,000行的原风险门。它既未删样，也没有把旧500,000门调大。

固定741e55f首级、904e/95cb/5b8后缀、完整80,751正支撑与145个当前max48输入，366节点分量实际域为±2并在0/255裁剪。非选角贡献保留在完整acc，使用真实四面体4活动角、Q16及half32768，逐行精确gcd/ceil/floor和int64审计；没有使用此前错误的Q48或三线性假设。

## 目标与事先候选初门

模型有366个节点delta、14,955个首级输出delta和366个abs辅助整数，共15,687变量，14,955舍入行、4,985完整AllowedAssignments。目标Minimize Σabs(node_delta)只作为较小扰动代理，不是平均精度保证。

候选初门在求解前固定为373a综合best：完整RGB域及原60图的mean、p99均不得变差，完整域max²≤43。RMS、CVaR以及a399/373a/741三分母对照全部披露，但不假称这些精度量已经编码进CP。373a全域/训练mean为0.8225028465/0.6990079845，741为0.7996658981/0.6823633098，更低的741均值必须保留比较。

安全表、恒安全盒及固定外域max²41给出条件充分上界43；它还自动保护全域mean/RMS/p99/max相对373a，但没有证明共享安全赋值存在。若找到incumbent，才允许一次独立uint64的145/4,985/80,751支撑重放、完整直方图与原60图整数频数验解，再按上述初门判断。初门仍不等于100图或运行时速度资格。

## 完整前置验证

冻结41份源与24项输入，AST通过。8组有限合同独立穷举小节点域，与CP完整可行投影逐项相等，再核最小L1；覆盖half精确/上下、共享节点不相容、固定角、0/255、三个输出安全表耦合。三项强制正L1最优分别1、2、4，避免只测全零解的漏洞；另有2项溢出行拒绝。

实际问题导出55,879,729B JSON，PB为6,177,951B。独立八角帽权审计全部4,985输入，核完整acc、节点clip、14,955个原始及gcd行与386,612个安全输出实际误差。最大raw/reduced绝对总界均262,144，L1目标上界732，逐项int64审计通过。CPValidate与PB导出通过，预检没有调用真实solver。

| 原件 | SHA256 |
| --- | --- |
| 源/输入冻结 | `e7cc03f02ac259933a99d74d44e053058eaa98a77eff1fcfa8477437dbb9ca77` |
| 问题 | `c18298f914011cd1d43a2b1aa0b9d144af9e850e6b3c200346ccb3a357747c16` |
| PB | `3684fa7b7515e9042a36676f305a56327af93b21a42e5f1e0bcd9618fca43d35` |
| 无搜索预检 | `1f765d945bee99399fbb191c79def42f471b5403b1c43bd83b9f88be48c16ebe` |
| 独立问题审计 | `54a50314e322e0d19a79ced83b643b4e2716a94f1de6da8ca846a9d3eeb829c4` |

## 唯一实际搜索及限制

实际搜索严格单worker、seed20261024、20秒，无hint或补轮。求解调用测得20.3236751秒，状态UNKNOWN、无可行变量数组、无整数L1目标值。响应记录196 conflicts、29,898 branches、53,077 booleans及目标下界1.0；这些统计不构成共享安全模型可行或不可行的证明。CP响应中的默认objective数值也不能在无incumbent时当成一组节点解。

没有FEASIBLE/OPTIMAL，故没有调用真实候选verify、生成节点模型、完整native/100图质量或速度测试。不能称max²43已实测达到；43仍只是安全共享解若存在时的条件上界。没有加时间、换seed、增加样本或修改原问题重试。

预检进程峰WorkingSet为233,594,880B、pagefile为978,665,472B；唯一solver进程峰分别522,612,736B、1,272,254,464B。这是各Windows进程整个生存期峰值，包含JSON、Python与CP构建，不能解释为部署模型RAM或稳态RSS。

## 实际环境、复现和证据

环境为Windows11 x86-64、Ryzen9 8945HX。原NumPy1.26.4/Numba0.60.0/CPython3.12.14环境仅导出问题和独立审核；隔离`p16-cpsat-py312`的ORTools9.15.6755只读整数JSON，不导入lutlab/NumPy/Numba进行真实搜索。安装包版本及RECORD、官方轮子SHA复用原环境锁和[环境归档](../../report/data/p16-cinema-first-cpsat-20261024/manifest.json)，未改变两个环境。无原生编译、AVX512或性能计时；质量窗口共享主机。

原环境关键命令：

```text
python scripts/prepare_cinema_current_safe_cpsat.py --frozen artifacts/cinema-current-safe-cpsat-frozen-v1.json --contract artifacts/cinema-current-safe-cpsat-contract-v1.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-current-safe-cpsat-problem-v1.json
python scripts/audit_cinema_current_safe_problem.py --problem artifacts/cinema-current-safe-cpsat-problem-v1.json --output artifacts/cinema-current-safe-cpsat-problem-independent-v1.json
```

隔离ORTools环境关键命令：

```text
python scripts/check_cinema_current_safe_cpsat.py --frozen artifacts/cinema-current-safe-cpsat-frozen-v1.json --output artifacts/cinema-current-safe-cpsat-contract-v1.json
python scripts/preflight_cinema_current_safe_cpsat.py --problem artifacts/cinema-current-safe-cpsat-problem-v1.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-current-safe-cpsat-preflight-v1.json
python scripts/solve_cinema_current_safe_cpsat.py --problem artifacts/cinema-current-safe-cpsat-problem-v1.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --preflight artifacts/cinema-current-safe-cpsat-preflight-v1.json --output artifacts/cinema-current-safe-cpsat-solution-v1.json
```

所有执行脚本拒绝覆盖原输出。归档脚本`archive_cinema_current_safe_cpsat.py`保存5份raw JSON、42份源码ZIP成员及16份支持成员（完整问题、预检/实际PB、8个有限PB、5段执行日志），引用完整风险/质量/环境manifest。先设原字节`-text`再显式暂存，核raw/source blob、ZIP成员及历史HEAD证据，未重跑数值。

## 下一步仅独立提案

去掉minL1和abs、仅寻找首个安全解，是另一份静态协议，原41冻结源和本轮UNKNOWN保持。任何后续执行都须重新冻结并独立授权；不能把新实验当成延长本轮20秒。只有真实候选通过已固定公共初门后，才可另行完整native/全域/100图逐图三分母与实际速度50%底线验收，仍不得默认升级。
