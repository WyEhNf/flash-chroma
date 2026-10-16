# 逐组预算感知的全局主提案

Agent：Codex；Operator：WyEhNf；Task：PR #24 后续；Status：Completed（固定实验、完整终验与独立归因完成，收益很小且残余失败保留，Draft待审查）。

## 从已验证问题到本阶段实现

PR #24 两臂零接受，最低尾部损失反例却令多张完整照片的mean/RMS真实上升。旧流程仍先按尾部挑选主节点，再寻找辅助；本阶段将预算信息前移到全局主提案排序。原运行时、模型格式和历史阈值不变，固定参照仍为PR23的47步模型，SHA `f803945e6f1bef7c1a3b57954749e918bf360f3dd486f1b7cba3b9c88c6c681d`，缺口1614。

新增`primary_budget.py`，两臂使用同一全观测颜色/频数的负截断下界±1主提案库。对照按尾部下界，优化臂先按逐组SSE/mean预算失败数及归一化预算排序；不将原下界改作新的可行性证明。保留各自主顺序中的前8个实际尾部改善主改，避免辅助阶段又按尾部损失重新选主。后续辅助复用同一351895104字节统计，模型签名不同则拒绝陈旧缓存。

新增每节点/±1/组的布尔标志，记录该单改是否改变任何像素的平方误差。无变化且当前直方图等于固定参照时，可在排序中应用与真实门禁一致的直方图相等mean豁免，避免Q24上界/下界间隙虚增违规数。**多个无变化单改在重叠支撑中合改可能变化**，所以联合豁免要求全部节点两两支撑不相交；否则保守排序，实际整块验收始终保留。默认旧路径不启用这些标志，原证据快照不改。

`quantile_repair.py`添加显式全局主提案方法，默认仍是原下界路径；`rounded_budget.py`/`rounded_blocks.py`接入统计共享、主顺序与无变化范围；`run_quantile_tail_study.py`保存新增源字节。顺带补齐旧全局统计的稳定性参照内存计数，不改变数值目标。

## 冻结测试与环境

目的：独立核对全部单改无变化标志、重叠舍入反例、有限同预算主提案选择、公开三节点路径的缓存共享；回归受影响的原全局下界、舍入和稳定性路径。集中运行14项必要合同，不做逐次调参或性能扫描。

环境：Windows11 10.0.26200 / Ryzen9 8945HX（16核32线程）/ RAM33605316608字节；研究venv Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0。合同设NUMBA_NUM_THREADS=4；数值入口不设该变量，由runner设4；BLAS/MKL/OMP均1。若产生变化终态，沿用GCC15.2 Release的单线程标量/AVX2和独立整数oracle完整终验；二进制SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`。

两份`primary-budget-{tail,constraints}-v1.json`先冻结：Velvia单例、同一47步模型、80完整图和既定样本、20审计不反馈；原历史目标及四指标固定保护不变。每臂最多32步、1轮全局、1轮辅助，128主试探/16节点普通双/8主×16辅助/8×4×4三节点。相对PR24有额外全局工作，两臂也不宣称等时间或等计算量。只对变化终态各做一次完整256³/100图/oracle/标量AVX2；不变则绑定SHA复用旧终验。原保护和固定参照另由标准库复核。

历史Delta-E为RGB欧氏码值距离，非CIEDE2000。mean用整数距离界、p99两个端点保护是充分条件，仍可能保守。无官方数据/Threshold，不称独立盲验、表示能力不可行证明、SOTA或实板成绩，默认不升级。

## 固定实验结果

14项必要合同集中一次14/14通过，9.87秒，无跳过。数值源及计划冻结于`e4a4694`；tail运行记录该提交，constraints运行记录`e68cb1e`（仅修改归档入口）。两臂实测源码及冻结源码快照逐字节相同；收尾后补空候选缓存修复的来源差异另列下文。归档入口`e68cb1e`/`df4d689`，实际独立归因入口`d65af87`；此前归因脚本提交中的循环括号在执行前静态发现并修正，没有用未执行的版本冒充验证源。

| 方法 | 起始/最终缺口 | 新接受 | 热点单/普通双 | 全局单/普通双 | 辅助双/三节点 |
| --- | --- | ---: | --- | --- | --- |
| 尾部下界排序 | 1614 / 1614 | 0 | 128 / 120 | 128 / 120 | 128 / 113 |
| 逐组预算排序 | 1614 / 1613 | 1 | 256 / 240 | 1 / 0 | 128 / 127 |

缺口下降仅1，约0.062%，不称显著精度提升。两臂首轮主提案库均2537个负下界提案，整个下界数组、SSE/Q24统计、无变化标志及模型签名SHA相同；只是主排序不同。对照全局248项试探中234照片保护拒绝、14未降缺口；前128个单改实际RMS受损组数为3～82。预算排序第一个全局主改即通过。

预算排序首次接受后，已经在新状态继续热点及辅助搜索，未再接受。两个模型从该点开始分叉，试探量不同，不能把总次数当作等时间比较。只有1轮额外全局预算，不在新模型上进行第二轮全局排序，因此不能推断剩余方向均不可行。后续三节点127项也没有接受，未检验真子集。

新模型SHA `cdbc18badb6ae3450a4cd28eadb9b941bf6d4ef243f72ccf2a693f78b0271bed`，节点35910（索引坐标32,32,6）由`[255,255,106]`改为`[255,255,107]`。累计第48步来源为`global_single`，没有接受新的联合辅助块，不能把收益归为三节点搜索。

## 精度、收益来源与反例

| 方案 | 完整域mean | RMS | p99 | max | 100图mean | RMS | 最差单图p99 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 起点/尾部对照（复用） | 0.981719623 | 1.879300066 | 7 | 54 | 1.033868662 | 1.384165205 | 7.141428429 | 46.043457733 |
| 预算排序（新终验） | 0.981716762 | 1.879299464 | 7 | 54 | 1.033866768 | 1.384134508 | 7.141428429 | 46.043457733 |

100图mean和RMS各3图改善、0退化、97持平；p99/max全部100图持平。3张改善图为div2k-0900、div2k-0889、kodak-kodim03，分别SSE下降1808、576、4299。80完整反馈图及样本由整数证书保护，20历史审计图本次观测全部持平；后者不是未来未知输入保证。

`diagnose_primary_budget.py`独立重放这唯一新主改的772色支撑：101组最终完整直方图与正式终验一致，局部模型与冻结检查点同SHA。全域SSE下降38，固定p99/max不变；5个变化组是上述3张完整照片、kodak-kodim03的选择样本及合并样本，后两者SSE各下降43。每个变化组的Q24新上界均小于旧下界，确认真实mean改善，无审计反馈或新拟合。

唯一目标收益来自div2k-0900的历史p99端点条件：平方阈值17、允许尾部7864像素，代价98→97。该主改截断下界−1、真实缺口变化−1，松弛差0。其排序键严格在对照第128项之后（该末项下界−51），且确实不在原128试探中；这里只证明“前缀之后”，没有计算或编造准确原名次。预算排序预测该项SSE/mean失败数均0并列为首项，真实保护全通过。这证明原主提案截断会漏掉小收益的可行方向，而不是阈值必须放宽或有限网格必定无解。

最终仍22组/24条件违反；max类缺口517未变，p99端点1097→1096。相对更早历史模型，仍5图mean、8图RMS、9图p99、15图max退化，本阶段只保证相对PR23固定参照不退化，没有消除先前代价或达到比赛要求。

## 架构、证据与复现

新无变化标志21993444字节，SSE/Q24统计351895104字节；持久数组1167367126字节，三者总1541255674字节。额外全局下界数组1724976字节在大统计构建前释放。tail辅助复用同模型统计，两份统计SHA精确匹配；constraints先接受修改，因此下一状态辅助必须重新统计，未复用陈旧缓存。该状态没有再构建全局主排序无变化标志，保守沿用原辅助排序。进程OS峰值tail1857679360、constraints1827962880字节，包含不同搜索轨迹的临时数组；不能据此推断加速或运行时内存改善。

唯一新模型进行一次完整256³/100图终验，独立NumPy整数oracle、标量/AVX2两份新回执均0字节差异；对照复用2份旧回执。新完整输出SHA `72dc990221b3e28c9a7508abf7fb9190fb3ac54470694ef2938a19bc8579e92f`。没有修改C++/portable/embedded，不代表新四级模型或实板验收。

原标准库`-I -S`两臂各复核202组初/终摘要及51/55份完整域证书；额外稳定性复核各101组+完整域直方图及PR23参照绑定通过。解压归档后再次复核通过，未载入NumPy/SciPy/Numba。证书包括47步旧重放及其他考虑/最终检查，不能将接受证书数当作新步骤数；尾部仍未可行。

[证据目录](../../report/data/primary-budget-v1)保存4汇总、400逐图（100新、300复用）、249项全局真实试探摘要、4原生回执（2新/2复用）、两臂48个归档成员、环境/计划/模型/数值源、完整候选及独立局部复算，约3.9MB。沿用同一归档脚本的`--study primary`入口，未再复制另一套归档器。新的诊断入口只选择已冻结的那一步，不新增扫描。

`archive-audit.json`核对成员SHA、源码和独立模型。旧`interp.py`/`io.py`仍存在工作区CRLF与Git LF差异，仅行尾不同；精确复现恢复`measured-source.zip`原字节，沿用PR24的来源约定，不能把Git SHA单独当作所有工作区字节的证明。AGENTS.md未改。

收尾静态检查发现缓存生命周期边界：全局已预建统计，但辅助筛选没有真实改善主改时，旧提前返回会留下缺少`primaries`的缓存，后续三节点阶段可能索引缺失项。`901df85`在这一空列表分支释放缓存，并扩展同一实际舍入/尾部反例，覆盖负下界仍不降低真实损失时的公开全局→辅助→三节点路径。针对性复验预算主提案4项及原三节点2项，6/6通过、6.63秒；不是重复无变更测试。已测两臂辅助主改数均为8，未执行空列表分支，故没有重跑完整数值实验。`post-measurement-fix.json`保存旧/新源码SHA、范围和测试版本；`source-provenance.json`如实标出当前`rounded_budget.py`不同，原实测快照和指标保持原来源，不把新修复源冒称实测源。

同次接口检查还发现，若外部将新主排序与可选尾部排序组合，需明确“无先行主改”的零尾部变化，不能传None。`4493d37`补齐该参数，并将同一公开反例参数化覆盖尾部排序开/关；主提案5项与原三节点2项共7/7通过、4.86秒。两臂冻结计划均关闭尾部排序，该参数在原实测路径中不参与排序。最终来源记录同时标出`primary_budget.py`和`rounded_budget.py`的后补差异，保留14项初始合同及两次有代码变更后的针对性复验版本；没有重跑完整数值实验或扩大参数扫描。

前述环境中实际命令如下；已有输出不可覆盖，复现使用新目录，并相应绑定计划/来源。`python`应使用研究venv。

```powershell
python -m pytest tests/test_primary_budget.py tests/test_stability.py tests/test_rounded_budget.py tests/test_three_node_search.py tests/test_quantile_global.py -q
python scripts/run_quantile_tail_study.py --plan experiments/primary-budget-tail-v1.json --output artifacts/primary-budget-tail-v1 --executable build-engineering-alignment/jshc.exe
python scripts/run_quantile_tail_study.py --plan experiments/primary-budget-constraints-v1.json --output artifacts/primary-budget-constraints-v1 --executable build-engineering-alignment/jshc.exe
python -I -S scripts/verify_quantile_constraints.py --input artifacts/primary-budget-tail-v1 --output artifacts/primary-budget-tail-v1/verification.json
python -I -S scripts/verify_quantile_constraints.py --input artifacts/primary-budget-constraints-v1 --output artifacts/primary-budget-constraints-v1/verification.json
python -I -S scripts/verify_stability.py --input artifacts/primary-budget-tail-v1 --reference-run artifacts/velvia-three-node-v1 --output artifacts/primary-budget-tail-v1/stability-verification.json
python -I -S scripts/verify_stability.py --input artifacts/primary-budget-constraints-v1 --reference-run artifacts/velvia-three-node-v1 --output artifacts/primary-budget-constraints-v1/stability-verification.json
python scripts/diagnose_primary_budget.py --tail artifacts/primary-budget-tail-v1 --constraints artifacts/primary-budget-constraints-v1 --warm artifacts/velvia-three-node-v1 --output artifacts/primary-budget-diagnosis-v1
python scripts/report_stable_tail.py --study primary --guard artifacts/primary-budget-tail-v1 --aware artifacts/primary-budget-constraints-v1 --warm artifacts/velvia-three-node-v1 --diagnosis artifacts/primary-budget-diagnosis-v1 --output report/data/primary-budget-v1
```

## 协作状态与下一步

已fetch github，main仍dec1020且为祖先，工程修复337a3dd保留。读取并刷新#9/#12至#24正文、完整评论/review/行内线程，#7/#8正文及评论，检索所有近期PR/issue，无新增相关意见。#7/#9修复沿原证据；#8最终接口迁移和实板仍待处理。Discussion4原文由用户提供，最新网页重试仍404，保留回复访问缺口，不执行合并或关闭issue。

新阶段Draft以PR24头b108c74为base，中文提交/阶段说明，PR Operator为WyEhNf，不直接推主干；新头CI在PR正文补记实际结果。

本阶段补上主提案约束感知，并证明存在旧排序遗漏的可行方向，收益幅度很小。后续更有依据的方向是收集同一冻结状态下预算可行主改的真实尾部收益，再限规模组合与检查整体预算，避免只选大尾部下界或盲目增加全局轮数。未实现这一后续批次策略，未放宽任何门槛。默认和历史冠军不变，无性能提升或官方验收结论。
