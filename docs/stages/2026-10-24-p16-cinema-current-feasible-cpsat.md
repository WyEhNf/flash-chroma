# 当前完整安全无目标首解：max²41通过公共初门

本阶段沿用当前741e55f的122首级节点±2/clip、完整安全约束和固定公共初门，仅移除minL1目标与366个abs辅助变量，执行一次最多60秒的首解搜索。31.5543728秒找到共享安全赋值；一次完整80,751正支撑整数重放得到全域mean0.8001032554、p99为3、max²41，原60训练mean0.6844168976、p99为√12，均通过预设373a综合best初门。尚未完成新候选的完整native/16M/100图或速度资格，不升级默认模型。

Agent：`/root/tail`；Operator：本次16题任务用户；状态：本阶段首解与初门完成，完整独立资格另阶段执行。相关提交以本阶段文档所在提交为准，成果继续放在精度研究分支与Draft PR90。

## 独立新实验及约束恒等

前一[20秒minL1实验](2026-10-24-p16-cinema-current-safe-cpsat.md)返回UNKNOWN且无incumbent，原41源与结果不变。本阶段不是延长旧实验：Minimize节点L1是扰动代理，未必利于首个可行解，因此独立协议去掉目标与abs，只要求找到满足相同安全约束的首个共享解。60秒、单worker、seed20261024及`stop_after_first_solution=true`均在执行前固定，无hint、回调择优或补轮。

节点、输出域、14,955个Q16舍入行、4,985完整表及386,612安全行、373a初门逐项等于原c182问题；canonical整数数学签名为`f11b69a1e8f4560852b253200cb98b6ffbeb1136710dfa74f00de42cce5aa03e`。只删除366个abs与objective，实际显式整数变量15,321。原8192危险点/1,000,000行门继续满足，不使用已经超500,000门的608,964行训练预算表，所有历史负例保持。

冻结49份源和30项输入，确认原41源未变；8组新无objective首解参数有限合同全部通过，并复用前一阶段8组完整投影与最小L1证据。独立逐项数学恒等审计把原八角帽权、固定角完整acc、实际clip、gcd/int64行与全部安全输出误差的证据完整转移到新问题，没有新增RGB查询或删样。预检实际核`has_objective=false`，CPValidate与PB导出通过，未搜索。

| 原件 | SHA256 |
| --- | --- |
| 冻结 | `0f22c88489d70725cbfe506f521bb3d0c601d79b8f699ad7d22186c15bb55904` |
| 问题 | `9f3494cd944bf7660e17e9a2f9fc788bcaa588f72d197464265c7224483cab24` |
| PB | `90f97a2beb1092c12d3733f8f6a347b473a8e407128ab701bf61a6db82fed276` |
| 无搜索预检 | `653189523d6f88199cfe8fe7d8e370cbeef5a704c0429ca6110458dad8ba5b59` |
| 独立恒等审计 | `90fc295a342ca017d552231fd61eb0d774a46f1129168abf9db99eb05bdbc9ab` |

## 唯一首解与真实整数验收

求解返回OPTIMAL，但本模型没有目标，所以该状态仅表示可行，不表示节点L1最小。实际观察到Σabs(delta)=442。没有因为此值较大而再求解或择优，首个解即停止。响应统计472 conflicts、52,093 branches、53,040 booleans；这些是本场求解记录，不是性能优化证据。

只有取得首解后才执行一次被冻结的verify：检查所有节点整数域、原始及gcd行、完整安全表，独立uint64首级输出与Numba逐字节相等。全部80,751输入输出位于已认证AABB；4,985危险点输出与CP三元组一致；原145热点max²降到34，支撑最大41，外域固定最大41，整域拼接质量与原60图整数频数均完整。

新首级NPZ SHA为`91d868d72e9eacc482fe26a8568dad4667f0d0ca9a24685432c6cf8991fd36d6`，其轴与分输出Q16侧表不变，后缀仍为904e/95cb/5b8。模型实体在`models.zip`，包含首级NPZ/SLUT、侧表和3个后缀，不使用完整RGB输出表替代模型。

| 指标 | 完整RGB域 | 原60图 |
| --- | ---: | ---: |
| 像素数 | 16,777,216 | 47,185,920 |
| mean | 0.8001032554 | 0.6844168976 |
| RMS | 1.1993875789 | 1.1413629522 |
| p99 | 3 | √12 |
| max² | 41 | 41 |
| CVaR最差1% | 4.0491616978 | 4.3519838697 |

初门固定综合best373a：cube及训练mean/p99均不得变差、global max²≤43，实际failures为空。全域mean相对best0.8225028465降低，训练mean也低于best0.6990079845；但相对当前741的0.7996658981/0.6823633098均有小幅增加，RMS/CVaR也有代价。训练CVaR4.3519838697高于best约4.3134743，必须保留这一退化；它是观察量，没有暗改为CP内硬约束。

外支撑固定max²41是当前选中122节点集合的下界，而本模型max²也为41，因此在“只改这122节点、其他节点固定”的子空间内达到该固定外域下界。这不是全首级节点或整链全局最优；下一独立完整资格应补一个真实外支撑q41颜色及无选节点正权的源见证。

## 环境、资源和复现

Windows11 x86-64、Ryzen9 8945HX、CPython3.12.14。原NumPy1.26.4/Numba0.60.0环境生成问题与真实整数验解；隔离ORTools9.15.6755环境只读整数JSON搜索，两个环境不变。验解Numba/OMP4线程、OpenBLAS1线程，共享主机质量窗口，无AVX512或性能计时。

预检进程峰WorkingSet233,414,656B/pagefile978,878,464B；实际首解进程峰534,900,736B/1,286,299,648B。均为整个Windows进程峰，不能称模型部署RAM。问题JSON55,881,516B，PB6,152,679B，实际solver PB与预检SHA一致。

先在原环境执行prepare与完整约束恒等审计，在隔离环境执行有限合同、preflight、唯一solver，再回原环境verify：

```text
python scripts/check_cinema_current_feasible_cpsat.py --frozen artifacts/cinema-current-feasible-cpsat-frozen-v1.json --output artifacts/cinema-current-feasible-cpsat-contract-v1.json
python scripts/prepare_cinema_current_feasible_cpsat.py --frozen artifacts/cinema-current-feasible-cpsat-frozen-v1.json --contract artifacts/cinema-current-feasible-cpsat-contract-v1.json --output artifacts/cinema-current-feasible-cpsat-problem-v1.json
python scripts/preflight_cinema_current_feasible_cpsat.py --problem artifacts/cinema-current-feasible-cpsat-problem-v1.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-current-feasible-cpsat-preflight-v1.json
python scripts/audit_cinema_current_feasible_problem.py --problem artifacts/cinema-current-feasible-cpsat-problem-v1.json --prior-problem artifacts/cinema-current-safe-cpsat-problem-v1.json --prior-audit artifacts/cinema-current-safe-cpsat-problem-independent-v1.json --output artifacts/cinema-current-feasible-cpsat-problem-independent-v1.json
python scripts/solve_cinema_current_feasible_cpsat.py --problem artifacts/cinema-current-feasible-cpsat-problem-v1.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --preflight artifacts/cinema-current-feasible-cpsat-preflight-v1.json --output artifacts/cinema-current-feasible-cpsat-solution-v1.json
python scripts/verify_cinema_current_feasible_cpsat.py --problem artifacts/cinema-current-feasible-cpsat-problem-v1.json --solution artifacts/cinema-current-feasible-cpsat-solution-v1.json --preflight artifacts/cinema-current-feasible-cpsat-preflight-v1.json --output artifacts/cinema-current-feasible-cpsat-accept-v1
```

原始脚本拒绝覆盖输出。归档保留6份raw JSON、50份源码成员、18份支持成员及6份模型成员，完整问题/PB/8有限PB/全部执行日志和fresh重放均可追溯；原始字节先`-text`再显式白名单stage，核实际blob/ZIP和历史HEAD。

## 后续仍未完成

训练mean/p99不代表100图自动通过。本阶段没有运行新模型的完整双DLL native、16M/100图、逐图三分母与阈值档，首级对原rawtable1忠实度、实际后端资格/容量及速度至少50%也仍待核。下一阶段只验证固定91d868模型，不回调节点或按照片择优；任何错误保留原件STOP。当前初门通过不等于整体升级。
