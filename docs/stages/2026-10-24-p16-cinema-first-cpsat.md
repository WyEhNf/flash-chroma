# 首级热点整数耦合：可行见证与完整支撑失败

Agent：`/root/tail`。Operator：本任务用户。状态：唯一求解与一次完整支撑验解完成，候选严格拒绝，不补跑、不切默认。

前阶段证明116个原max50热点逐点存在较好首级arrival，但单节点、一次八色和52项统一组方向均未把max降到49。本阶段从原max_first（0ea0/904e/95cb/5b8、143e完整流）出发，直接连接86个节点的共享整数变化与116点首级RGB舍入状态，只做一次有限热点可行性求解。旁侧输入和平均预算在求解后完整验证，未把热点成功当作完整模型通过。

## 精确模型和环境桥

节点RGB分量共258个整数delta，域为原值±2与[0,255]相交；116点各有3个输出整数delta，共606变量。每点AllowedAssignments表保留其首级RGB盒中经当前固定后缀得到d²≤49的全部安全三元组，共2351项。

首级实际为四面体Q16，Q=65536、half=32768。原完整未舍入acc包括固定角贡献。每个输出的精确闭区间约束为 `Σw·节点delta-Q·输出delta ∈ [原RGB·Q-half-原acc, (原RGB+1)·Q-half-1-原acc]`。348行逐行取系数gcd，lower精确ceil、upper精确floor，原系数/变量域乘积、约简乘积、累计范围和区间端点均用Python整数审int64溢出，附加保守界2^62-1，不使用浮点近似舍入边界。

原NumPy1.26/Numba0.60环境只生成整数JSON和做uint64验解。ORTools9.15.6755安装于独立`artifacts/p16-cpsat-py312`，只读JSON运行CP-SAT，未导入lutlab/Numba或修改原环境。10个wheel的实际SHA均与官方PyPI元数据一致，版本、安装RECORD及公开直接下载链接完整锁定；大venv和wheel不纳入Git。新环境独立使用NumPy2.5.4/Pandas3.1.0，属于离线研究依赖，不增加现有原生运行时依赖。

五组有限小域完整穷举覆盖half正好与上下1、fixed角、0/255截断、共享节点和共享局部无解，CP全部可行集合与独立Python原acc舍入穷举相等，另两行溢出正确拒绝。实际热点模型还在求解前单独完成CP验证与PB字节导出，未搜索；其PB与实际求解PB完全一致。

## 唯一求解与完整代价

固定1 worker、seed20261024、最多20秒、无目标函数，只执行一次。CP-SAT在0.612810600秒返回`OPTIMAL`，在无目标可行性模型中该状态只用于表明找到可行见证，不能解读为精度或扰动最优。原环境逐项核对全部原始/约简整数行、AllowedAssignments及真实uint64首级/后缀，116个旧热点的最大平方误差确实由50降到34。

完整70,571正支撑上有285个旁侧点违反固定cap，候选整体质量如下，故严格拒绝：

| 范围 | 指标 | 原max_first | CP热点可行候选 |
| --- | --- | ---: | ---: |
| 全域 | mean | 0.7990738071534367 | 0.8003306063357355 |
| 全域 | RMS | 1.1976684589597302 | 1.2007283950520344 |
| 全域 | p99 | 3 | 3.3166247903554 |
| 全域 | max² | 50 | 108 |
| 全域 | 最差1% CVaR | 4.029054534445704 | 4.080308069381532 |
| 原60图合并 | mean | 0.6823481783784588 | 0.6823758924555118 |
| 原60图合并 | RMS | 1.1366130440332765 | 1.136688481379768 |
| 原60图合并 | p99 | 3.4641016151377544 | 3.4641016151377544 |
| 原60图合并 | max² | 50 | 97 |
| 原60图合并 | 最差1% CVaR | 4.303192100572805 | 4.304230683102822 |

支撑外固定整数直方图完整保留、`hist[50]==0`，原60图47,185,920个像素的整数频数守恒。七项mean/RMS/p99/CVaR观察指标退化，加固定cap及严格49失败；没有按热点收益放宽门槛、增点补跑或替换正式模型。保存的节点文件只为复核失败见证。

独立只读审计进一步复算全部606整数值、348条gcd/舍入行、116张表、PB/源/环境/wheel身份及失败门槛映射，没有额外搜索或重跑像素。Windows x86-64共享主机上执行质量研究，解释器3.12.14；0.613秒只描述该SAT求解，不是原生映射或性能配对。没有新完整四级/native/百图/RSS/吞吐验收。

归档位于 [report/data/p16-cinema-first-cpsat-20261024](../../report/data/p16-cinema-first-cpsat-20261024)，保留原整数问题、实际PB、求解状态日志、全部变量、环境锁/官方wheel链接、有限合同、一次验解摘要及未晋级模型，未纳入大依赖目录。协议是`experiments/p16-cinema-first-cpsat-v1.json`；主要桥接脚本为`prepare_cinema_first_cpsat.py`、`solve_cinema_first_cpsat.py`、`verify_cinema_first_cpsat.py`及纯整数`cinema_first_cpsat_model.py`。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/prepare_cinema_first_cpsat.py problem --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-first-cpsat-problem-v1.json
& 'F:/Hackathon/worktrees/p16-tail-20261023/artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/solve_cinema_first_cpsat.py --problem artifacts/cinema-first-cpsat-problem-v1.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-first-cpsat-solution-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/verify_cinema_first_cpsat.py --problem artifacts/cinema-first-cpsat-problem-v1.json --solution artifacts/cinema-first-cpsat-solution-v1.json --output artifacts/cinema-first-cpsat-accept-v1
```

本阶段说明热点的整数耦合存在解，主要障碍转到完整旁侧输入和预算保护；不证明完整70571问题不可行，也没有把局部见证写成可用优化。官方分输出坐标许可问题保持原状。
