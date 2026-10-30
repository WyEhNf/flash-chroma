# 首级窄域直接八预算CP：有界无解状态与固定外域下界

Agent：`/root/tail`。Operator：本任务用户。状态：V1元数据路径失败保留，V2有限合同、问题导出、无搜索预检和唯一真实求解完成；solver报告INFEASIBLE，没有整数候选，按约停止。仅指本窄域和保守八预算编码，无独立形式不可行证明，不能排除宽域或其他模型。

此前只优化节点L1的741e55f见证把max平方降至48，却使原max_first的六项局部预算小幅上升。本阶段另立直接预算协议，把完整受影响输入的真实误差状态与全域/原60图mean、RMS、p99、CVaR直接绑定。预算仍为原max_first，不借见证均值；旧L1失败、旧宽域超资源门和max48三分母独立质量结论均保持。

## 模型与合同

沿唯一已认证的窄域：53物理节点、95活动RGB分量，每个delta从0到741e55f对应分量取闭整数区间。完整47,013正支撑中保留10,335点；另外36,678点在全盒内误差恒等原值，外部固定域也保留。51,926条完整安全RGB状态携带真实后缀误差平方。每点使用真实Q16四角累加与32768半舍入，固定角完整贡献保留，逐行gcd约简和signed int64界核验。

实际模型共有63,090个整数/布尔变量：95节点分量、31,005输出delta、10,165误差平方、21,825显式one-hot误差选择器；10,335表、31,005舍入行、八个完整预算。一个安全RGB确定一个q；q与选择器精确相等，全部成本使用这个同一个q，固定q直接累计常数。

mean和固定阈值CVaR用`ceil(2^20×差)`保守整数成本，负差退款也向上取整；平方和RMS精确。p99使用原上端秩计数充分约束：全域阈值平方9，原超阈164,670、上限167,772；训练阈值平方12，原超阈354,337、上限471,859。使用这些原有秩余量不增加p99，不把额外“超阈数必须不增”误作用户要求。

有限合同在原NumPy环境独立整数穷举节点全集，并用第二种符号平方算法算成本；隔离ORTools环境枚举CP全部节点投影，两集合必须完全相等。共12组覆盖half下/恰好/上、共享角与固定角、0/255裁剪、强制非零预算可行、共享节点mean无解、零训练质量仍约束全域、p99原秩余量可行与零余量无解、真实误差持平但ceil保守拒绝。最后一例的sqrt1/sqrt2交换使真实分布不变，但两项ceil之和为1，明确展示编码的保守性。

## V1失败与V2唯一执行

V1冻结34源SHA `582bbe20c08daceccbacbd6e5712a20a96c27f6ff93b137ceac515298df1f6c7`，12合同全过。但真实JSON写出前，元数据`relative_to`收到命令传入的相对contract路径而抛ValueError；未生成V1真实problem/PB，未执行真实solver。源、有限输入/结果和完整失败日志均保留。

新V2只增加路径规范化wrapper和协议，三个参数必须resolve在本worktree授权artifacts内；未修改V1算法或数学。V2冻结36源SHA `cb3a72ecdcafec7700a7c2254f3789c392ec5cbedd75a85395d64317868d51ef`，同12有限合同身份重核全过。实际问题SHA `d1f092d54e05d9bd0884fc43bb1aeb43d0fb86290e957d5afb0aed365095351f`（73,003,996B），PB SHA `3345e78b9884b58a135e035aab23a3164227e7f656486a50218d7888eb06e95f`（4,269,651B），预检SHA `09f144b3c4f13fa3a2923fd0ef27d745825fbbe03d6814e8ce1bd6b1a2d20f4f`。

CPvalidate、逐行原始系数乘积、预算累计与普查一致性全过。最大舍入原绝对界261,962，最大预算原绝对界24,633,309,809。预检不搜索；真实求解前再次核三SHA、36源、证据和隔离环境lock/RECORD，实际PB与预检逐字节相等。

唯一真实参数为1 worker、seed20261024、20秒上限、无目标、无hint。实际0.5094418秒返回INFEASIBLE，响应branches为0，变量值为空。没有追加seed、时间、删预算或重求。因为没有incumbent，未执行新候选fresh验解、原生、100图或性能；没有新模型和新完整色域流。

预检进程峰工作集310,059,008B、峰pagefile计账1,056,100,352B；实际求解进程峰工作集369,123,328B、峰pagefile343,281,664B。这些为不同Python进程自启动累计峰值，包含JSON/模型/solver，不是部署LUT RAM，不能据此作内存优化结论。

## 独立编码审计与后续方向

只读audit用独立八角权逐点核10,335个原acc和活动节点权，逐行重算51,926个安全RGB经真实后缀后的误差，并用第二整数根差算法核全部点成本。表行唯一、全部在端点内且安全，行数等于唯一完整普查，因而没有删安全状态。V1/V2的12组有限节点全集一致。

零端点成本全0，但恰116点不满足安全表；741e55f端点全部表安全，但全域/训练mean、RMS、CVaR六预算仍违反。两端点各自失败不证明其他节点组合失败，也不识别哪一项预算是唯一阻断；本阶段无解结论严格来自该保守编码的单次solver状态，未生成独立形式证明。

固定外域还提供了无需solver的尾部下界。把全部受影响输入的误差乐观置0，保留外部完整固定直方图：

| 范围 | 受影响质量 | 外域平方48质量 | 乐观p99下界 | 乐观max平方下界 |
| --- | ---: | ---: | ---: | ---: |
| 全色域 | 47,013输入 | 6输入 | 3 | 48 |
| 原60图 | 3,629像素 | 513像素 | sqrt12 | 48 |

全域外部仍有561,788输入的误差平方至少9；训练外部仍有627,171像素的误差平方至少12。该乐观分配未必可达，但已经足以证明：只改变这95分量、保持其他节点/轴/后缀不变，不能把完整域max平方降至47，也不能降低当前全域或训练p99。741e55f已达到这一所选子空间的尾部下界；这不表示它在mean/RMS上最优，也不表示所有首级节点或其他表示已经最优。

因此后续精度研究应扩大正支撑或更换变量选择，避免继续在这95分量中盲求p99/max。用户的共同参考还包含a399与综合best；max48相对这两者均值更优的已验质量价值保留，不能把本阶段更严格的max_first八局部预算失败扩大成全局无价值。其速度50%尚未验证，仍不默认升级。

执行环境为Windows x86-64、Ryzen9 8945HX、原Python3.12.14/NumPy1.26.4/Numba0.60.0与隔离Python3.12.14/ORTools9.15.6755，依赖lock沿原独立venv，未改原数值环境。实际solver明确1线程；原环境只生成整数JSON或离线核验。为质量共享主机，期间root仅轻量原生调试，无正式性能结论。未用AVX512。

主要文件为`experiments/p16-cinema-first-direct-budget-cpsat-v1.json`与v2协议、`cinema_first_direct_budget_model.py`、`prepare/check/preflight/solve/verify_cinema_first_direct_budget.py`及V2 wrapper。证据在`report/data/p16-cinema-first-direct-budget-20261024`，大型JSON和PB以ZIP成员保留原SHA；未把venv或wheel放入Git。原始协议中“静态准备”是执行前预注册状态，本阶段实际执行与失败以本正文和原始记录为准。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/prepare_cinema_first_direct_budget_v2.py contract --output artifacts/cinema-first-direct-budget-contract-input-v2.json
& './artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/check_cinema_first_direct_budget.py --input artifacts/cinema-first-direct-budget-contract-input-v2.json --output artifacts/cinema-first-direct-budget-contract-v2.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/prepare_cinema_first_direct_budget_v2.py problem --contract artifacts/cinema-first-direct-budget-contract-v2.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-first-direct-budget-problem-v2.json
& './artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/preflight_cinema_first_direct_budget.py --problem artifacts/cinema-first-direct-budget-problem-v2.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --output artifacts/cinema-first-direct-budget-preflight-v2.json
& './artifacts/p16-cpsat-py312/Scripts/python.exe' scripts/solve_cinema_first_direct_budget.py --problem artifacts/cinema-first-direct-budget-problem-v2.json --environment-lock artifacts/cinema-first-cpsat-environment-v1.json --preflight artifacts/cinema-first-direct-budget-preflight-v2.json --output artifacts/cinema-first-direct-budget-solution-v2.json
```

原件不覆盖；复现需独立输出目录。任何后续改域或改预算都必须是新协议，不改本次状态和停止条件。
