# 固定273节点±1完整安全模型的唯一首解求解

Agent：`/root/tail`。状态：已完成冻结、有限合同、完整整数导出、独立审计和唯一真实求解；求解器返回INFEASIBLE，没有新候选。结论仅限固定91d868为中心的273节点±1域、4058张完整cap40安全表。没有独立形式证书，不能推广到旧±2域或整链全局无解。

本次消费上一阶段已独立认证的171,271完整正支撑、全部231个当前q41输入、原60图整数频数和外域q38直方图，不删训练零频点。规模预检中的1,400,540状态、4,058危险点和74,081安全三元组均在原4,194,304／8,192／500,000门内。固定外域已经阻止cube p99低于3；本次目标主要为max²≤40，不把该安全模型称为p99优化器。

真实模型含819个节点delta与12,174个首级RGB8输出delta，共12,993显式整数，12,174条Q16舍入行和4,058张AllowedAssignments。没有目标、abs变量或hint。原完整acc保留固定角，节点实际±1并clip[0,255]。每行使用Q16、half32768、精确gcd及ceil/floor端点，原始/约简域乘积逐项审signed int64，最大原绝对总界131,072。没有借用旧±2的`point_box`范围。

执行前逐表核74,081个安全RGB按lex排列且唯一，减去固定original RGB后与`add_point`的sorted顺序一致，没有为迁就导出改表。隔离环境有限合同先核锁、实际packages及已安装RECORD并记录解释器；7个小域完整可行投影与独立穷举相同，另核真实首解参数返回成员。半舍入上下、共享不相容、固定角、0/255及三个输出耦合均覆盖，强制非零样例的最小扰动L1为1及3，两个溢出输入正确拒绝。L1在真实模型中只观察，不作目标。

原环境以标量四角导出全部整数问题，另一实现用八角帽权核所有4058输入的完整acc、节点clip、原始及gcd行、输出域和全部74081安全行。隔离环境CPValidate及PB导出通过，预检不调用真实solver。

| 原始身份 | SHA256／大小 |
| --- | --- |
| 32源／26输入冻结 | `037456d96456059112d968006c6200d247334f62a5d686bf48afee9acabfc8bc` |
| 有限合同 | `574514f6d21cdd84de085db6491ed315cb22fb5be71a04ea13664c0baaa1815d` |
| 问题JSON，31,196,383B，仅ZIP | `f492e49bc17dd98efbf743629180a8ed656729d859c1953bbe83f3c29ddfe41c` |
| 独立完整整数审计 | `1a8f155348b096644cd30b0f4f2c8d7d53099f9186a2d6bdefcb22bec7a717d1` |
| 预检／实际PB，1,841,070B | `b9c02878b80cf859ee4feadb370a1f3b075792dc50b9c90a5e90ba539adcab88` |
| 无搜索预检 | `bacd9e813d4acd3cd2e95886c02e7010e3299c6647226c6536051fa461561709` |
| 唯一实际solution | `c3e63c2edf797678e39489d217953eff7d2b4207b5f29a01bf30e589efa324af` |

真实求解严格固定单worker、seed20261024、60秒上限、`stop_after_first_solution=true`，没有hint或objective；日志开启且原件完整保存。session70986中solver实际0.8220190000720322秒返回INFEASIBLE，presolve日志称`during probing`，零分支、无incumbent，节点L1为空。没有补seed、延时或同问题重跑。因没有解，未执行真实`verify`、native、完整100图或性能；没有新的mean/p99/max或精度退化数字可报告。验解脚本虽在冻结源中，不能当作已经执行。

若未来另有候选，公共初门仍为373a的cube／原60图mean与p99不退、global max²≤40；RMS/CVaR和相对741/91d退化完整披露。当前INFEASIBLE不依赖是否编码这些精度预算，因为本次CP未编码它们。下一独立整数传播证书如能找到矛盾可另报告，当前不凭solver状态冒称已具有可重放形式证明。

环境为Windows11 x86-64、Ryzen9 8945HX。原导出及审计环境为CPython3.12.14、NumPy1.26.4、Numba0.60.0；隔离求解环境ORTools9.15.6755及已锁依赖，未改原Numba环境。OpenBLAS/MKL1，原环境Numba上限4；实际solver单worker，共享质量窗口，非性能计时。预检进程峰工作集174,063,616B／pagefile144,326,656B；solver进程峰工作集236,126,208B／pagefile208,519,168B，均为进程生存期峰值，不是部署模型RAM。

```text
# 原环境
python scripts/prepare_cinema_current_cap40.py freeze
# 隔离ORTools环境
python scripts/check_cinema_current_cap40.py
# 原环境
python scripts/prepare_cinema_current_cap40.py problem
python scripts/audit_cinema_current_cap40_problem.py
# 隔离环境，预检与真实求解分别授权，真实只执行一次
python scripts/run_cinema_current_cap40_solver.py preflight
python scripts/run_cinema_current_cap40_solver.py solve
```

脚本拒绝覆盖原件。版本库只存短summary及包含原始JSON/PB/log的ZIP，成员逐项保存SHA256／CRC32／字节数，引用上一完整支撑manifest。未执行的新证书稿排除在本阶段执行源之外；新阶段不修改既有UNKNOWN、首解、±2超门或±1规模过门证据。
