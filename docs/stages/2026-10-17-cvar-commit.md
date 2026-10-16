# 最坏百分之一误差的固定提交门禁

Agent：Codex；Operator：WyEhNf；Task：PR #26 后续；Status：Completed（固定实验、终验与误差归因完成；残余失败保留，Draft待审）。

## 误差原因与阶段目标

PR26在相同起点把历史分位缺口1613降至1582，逐图/完整域mean、RMS、p99和max均未退化，但完整域最坏1%颜色均值从11.5253793555升至11.5257059097。独立整数界证明上升，不是浮点显示错误。历史阈值缺口、均方误差及尾部均值不是同一目标，四个摘要的保护不能覆盖整个尾部形状。

同一已保存72候选中，29356+31532+34839的主缺口1585，尾部均值变化区间为[-0.0000872655,-0.0000871933]。本阶段只把这项既有发现变成可落地、可复核的提交门禁并完整验收；不扩展网格、轮次或调参扫描。1585是已观察数据上的选择，不能称独立盲验。

## 实现与可审核边界

`cvar_guard.py`固定起点完整域直方图，对最坏`ceil(N/100)`颜色的RGB欧氏距离和计算Q24整数上下界；候选上界不大于起点下界时允许提交。最坏K的频数完全相同也允许相等，避免非整数根造成错误拒绝；其他区间相交仍保守拒绝。原历史阈值、混合预算及固定起点四指标保护均保留。距离不是CIEDE2000。

`quantile_repair.py`在热点、普通双改、辅助和批次的实际提交路径统一保护CVaR。`primary_batch.py`区分四指标可行的组合材料和可直接提交的候选：单改CVaR上升仍可留池，与其他节点整块真实重放；不能单独提交。这样不会提前丢掉1585所需的两个风险单改。空提交候选返回回退，确认仍须通过全部门禁。

runner绑定起点模型签名、完整图片频数、环境、源码、计划及PR26结果哈希，逐项比较首轮原排序/统计SHA和8单改+64组合的四指标结果；确认CVaR只改变提交资格。`verify_cvar_guard.py`仅用标准库整数平方根独立复算新步骤与最终完整域证书，绑定起点与最终模型SHA。

新增门禁不是原比赛硬阈值，也不意味着每个分位均不增加；未证明全局最优或表示能力上限。不改默认、冠军、C++运行时、模型格式或硬件路径。

## 冻结实验与验证目的

`experiments/cvar-commit-v1.json`沿PR26 joint配置，从PR25同字节模型`cdbc18badb6ae3450a4cd28eadb9b941bf6d4ef243f72ccf2a693f78b0271bed`重放48步，主缺口1613。最多32步、单轮全局/辅助、8种子、双/三节点块，80完整图及既定选择像素反馈，20历史审计不反馈。对照复用已完整验收的PR26缺口1582终态，不为凑两臂重跑旧模型。

先集中执行15项必要合同：新增4项覆盖最坏K截断并列、独立Q24复算、尾部相同而主体不同、错误像素数、风险材料联合补偿、材料池非空但无提交候选，以及普通热点门禁；同时回归原11项批次、主预算及跨级三节点合同。若发现具体失败，保留首次日志，修复后再做有依据的复验。

合同通过后只启动一次冻结数值入口；仅变化终态执行一次完整256³、100图及单线程标量/AVX2与独立NumPy整数oracle逐字节终验。阶段性完整性另由原预算、四指标固定参照、新CVaR标准库验证器、所选7子集独立重放及72候选尾部复算交叉检查。归档后解压再核哈希与证书。没有性能或SOTA扫描。

环境：Windows11 10.0.26200，AMD Ryzen9 8945HX（16核32线程），RAM33605316608字节；venv Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0。合同NUMBA_NUM_THREADS=4；数值运行移除此变量，由runner设4；OPENBLAS/MKL/OMP均1。GCC15.2 Release程序`build-engineering-alignment/jshc.exe` SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`，标量/AVX2终验单线程。明确不执行实板、四级新模型或跨环境性能比较。

```powershell
# 使用artifacts/error-study-py312/Scripts/python.exe；先设置上述线程及UTF8环境。
python -m pytest tests/test_cvar_guard.py tests/test_primary_batch.py tests/test_primary_budget.py tests/test_three_node_search.py -q
# 移除NUMBA_NUM_THREADS后运行，旧目录不覆盖；复现须选择新目录并更新相应参考路径。
python scripts/run_quantile_tail_study.py --plan experiments/cvar-commit-v1.json --output artifacts/cvar-commit-v1 --executable build-engineering-alignment/jshc.exe
python -I -S scripts/verify_quantile_constraints.py --input artifacts/cvar-commit-v1 --output artifacts/cvar-commit-v1/verification.json
python -I -S scripts/verify_stability.py --input artifacts/cvar-commit-v1 --reference-run artifacts/primary-budget-constraints-v1 --output artifacts/cvar-commit-v1/stability-verification.json
python -I -S scripts/verify_cvar_guard.py --input artifacts/cvar-commit-v1 --reference-run artifacts/primary-budget-constraints-v1 --output artifacts/cvar-commit-v1/cvar-verification.json
```

## 协作与未完成项

基于PR26头2b92cee创建阶段分支；main dec1020为祖先，工程修复337a3dd保留。此前已读#9/#12至#26及#7/#8完整相关记录；PR创建/更新前再次刷新。#8接口迁移/实板仍待落实。Discussion4原文来自用户，最新回复访问404，保留检查缺口，不执行合并或关闭issue。AGENTS.md保持只读。

数值源码/计划/合同先冻结于`428c9de`；归因与归档入口`e8515bf`，解压复核`8c456bc`，局部误差方向分析`fdef020`。下列为实际结果；官方数据和Threshold仍缺，历史22组/24项失败不能以新增CVaR通过替代。

## 固定队列的实际结果

15项必要合同集中一次15/15通过，9.38秒，无跳过。唯一新数值运行记录`428c9de648653fe08ffd0e56020cb90c7ca2fa5c`；后续仅补充归因与归档，没有修改已测数值代码。

| 方法 | 起点/终态缺口 | 新步骤 | 种子/组合/确认 | 热点单/普通双总计 | 辅助双/三节点 |
| --- | --- | ---: | --- | --- | --- |
| PR26无CVaR门禁（复用） | 1613 / 1582 | 1 | 8 / 64 / 1 | 256 / 240 | 128 / 125 |
| 固定起点CVaR提交保护 | 1613 / 1585 | 1 | 8 / 64 / 1 | 256 / 240 | 128 / 123 |

首轮同一2536个负下界提案，模型、排序、SSE/Q24统计及无变化标志SHA一致；8单改和64组合的原四指标缺口/判定逐项匹配，20个重叠组合仍跳过。旧对照复用，不能将“同一候选队列”说成等时间重跑。保护新增尾部计算，后续轨迹也不同，没有性能声明。

8个四指标可行材料中，5个CVaR上升、3个可单独提交；64组合中19个因CVaR拒绝、45个可提交。全局确认另1次，CVaR标准库复核73候选回执，24项尾部门禁失败。最后只提交一个三节点块，不把45个可行块或73份回执称为新步骤。

最终节点29356/31532/34839的B分别`63→64`、`26→27`、`186→187`，其余通道保持。模型SHA `f577f0749f7aae56275774d0bdbaad9305d99652ca08ba21cc928c8ff84962c4`；完整流SHA `6db44be2164e23d52febf9674ab0d833ca6c8c1c935ac9a3cad8359fb43f8cfe`。

## 误差为何反向变化

4544色支撑并集上，独立NumPy整数重放全部七个非空子集，重新建立101组频数、原保护和CVaR，与正式候选判定全部相同。独立生成的三节点模型与第49步检查点同SHA。

| 节点子集 | 主缺口 | 完整域SSE变化 | CVaR提交资格 |
| --- | ---: | ---: | --- |
| 29356 | 1600 | −441 | 仅组合材料 |
| 31532 | 1610 | −773 | 通过 |
| 34839 | 1601 | −31 | 仅组合材料 |
| 29356+31532 | 1597 | −1214 | 通过 |
| 29356+34839 | 1588 | −472 | 拒绝 |
| 31532+34839 | 1598 | −804 | 通过 |
| 三者 | 1585 | −1245 | 通过并提交 |

这不是“所有真子集失败”的必要三节点反例；两种双改也可提交，三节点在同一有限队列中主缺口更低。若在本固定8材料/64组合队列中先删掉所有CVaR上升材料，只剩3个单改、7个非空候选，最佳主缺口1603；延迟提交判定保留风险材料后可到1585。未重新扫描其余128提案，不能推断重新搜索后的严格过滤最优值。

`explain_cvar_components.py`进一步只重放这三个已选节点各自的局部支撑，更新后的完整域误差频数SHA与原候选证书吻合。三者同样B加1，但所在区域的残差方向和误差幅度不同：

| 单节点 | 输出变化颜色数 | SSE改善/变差颜色 | 全域SSE变化 | 尾部改善/变差颜色 | CVaR均值变化约值 |
| --- | ---: | --- | ---: | --- | ---: |
| 29356 | 435 | 292 / 143 | −441 | 87 / 82 | +0.0001414063 |
| 31532 | 455 | 291 / 164 | −773 | 183 / 130 | −0.0002470551 |
| 34839 | 251 | 131 / 120 | −31 | 59 / 66 | +0.0000184194 |

三项SSE都改善，两个尾部均值却恶化。29356甚至是尾部改善颜色数87大于变差82，净尾部距离仍上升；不能按改善像素数量或SSE判断尾部距离和。截断平方误差均保持49，最坏K均值的变化等于所有颜色`max(距离−7,0)`之和的变化除以K，因此大误差颜色的移动幅度决定净效果。

具体反例：输入RGB `[211,250,155]`，29356单改使输出`[200,255,80]→[200,255,81]`，精确参考`[198,255,67]`，平方误差173→200。B加1进一步偏离参考。相反输入`[224,248,142]`，31532使输出`[222,255,37]→[222,255,38]`、参考`[222,255,45]`，平方误差64→49，颜色退出严格大于7的尾部。共享节点影响一片颜色，同向修改不能同时消除方向相反的残差。

这类误差是当前目标与共享节点局部作用的真实取舍；本轮逐字节终验未发现实现差异。有限搜索也没有证明网格表示能力不足，不能把尚未找到更优解当作表达能力不可行证明。

## 完整指标与剩余问题

距离均为RGB欧氏码值；照片p99是最差单图p99。

| 方案 | 全域mean | RMS | p99 | max | CVaR 1% | 100图mean | RMS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 固定起点（复用） | 0.981716762 | 1.879299464 | 7 | 54 | 11.525379356 | 1.033866768 | 1.384134508 |
| PR26无门禁（复用） | 0.981699699 | 1.879289663 | 7 | 54 | 11.525705910 | 1.033861467 | 1.384107526 |
| CVaR保护（新终验） | 0.981701047 | 1.879279720 | 7 | 54 | 11.525292126 | 1.033861634 | 1.384107186 |

新模型CVaR相对起点变化的独立Q24区间为`[-0.0000872655012,-0.0000871933310]`，严格下降；相对旧1582模型降低约0.000413784，但主缺口多3、完整域及照片mean也略高，不能声称全面支配旧方案。旧、新两模型逐图比较mean/RMS均为4改善、4变差、92持平，p99/max全持平；新增保护针对固定起点，不承诺胜过旧终态每一张图。

相对固定起点，100图mean/RMS均13改善、0变差、87持平，p99/max100图全持平；最差单图p99为7.141428429、max46.043457733。训练/选择/审计分组见CSV；审计mean/RMS也较起点略降，但相对旧对照略高，是历史已观察数据，不称盲验。

最终仍22组/24项历史目标失败。max类缺口517不变，p99端点1096→1068（旧对照1065），主缺口总计1585。最大误差54的热点仍在`[251,251,42]`附近，本轮没有降低该峰值。最大残余p99项div2k-0853超限414像素，其次div2k-0897超限232；div2k-0879仍3个像素超过历史max目标，损失168。下一阶段应围绕这些冻结反例定位残差方向、支撑重叠及可行联合修改，不能靠继续优化CVaR均值宣称已解决极值。

## 验证、来源及归档

新模型一次完整256³、100图、独立NumPy整数oracle、单线程标量和AVX2，2份新回执均0字节差异。旧对照的2份原生回执显式复用。原预算标准库隔离复核202组初/终摘要及128份完整域证书；固定四指标参照101组+完整域终态及起点绑定通过；新增CVaR复核1新提交、1终态、73候选尾部证书。122份完整域接受回执含旧重放、候选和确认，不等于122步。

归档解压后两臂原预算/固定参照复核、新臂CVaR复核均通过，无NumPy/SciPy/Numba依赖。[证据目录](../../report/data/cvar-commit-v1)包含54归档成员、4汇总、400逐图（100新/300复用）、12分组、4原生回执（2新/2复用）、完整候选/模型/精确数值源/计划/环境、七子集、72候选及局部方向分析，约5.1MB。旧合同日志与本轮15项日志分开，未把新合同覆盖冒称旧数值源的重测。

旧对照实测源`f095467`，新臂`428c9de`；共同数值源有且仅有`primary_batch.py`、`quantile_repair.py`和runner三项变更，新臂另有`cvar_guard.py`，其余共同源同字节。当前新臂数值源码与实测ZIP完全相同。两臂旧`interp.py`/`io.py`工作区CRLF与Git LF差异只涉及行尾，均逐项核对；精确复现恢复各自`measured-source.zip`。归档审计核对Git来源、候选完整域频数、独立模型及新旧证据标记，AGENTS.md未改。

持久数组1167367126B，沿用351895104B统计及21993444B标志，不为CVaR再复制完整颜色缓存；短直方图和回执另计。新进程OS峰值1829265408B，旧1829011456B，轨迹不同，不推断速度或运行时内存改善。

补充复现命令（环境同前，输出拒绝覆盖）：

```powershell
python scripts/diagnose_primary_batch.py --plan experiments/cvar-commit-v1.json --input artifacts/cvar-commit-v1 --warm artifacts/primary-budget-constraints-v1 --output artifacts/cvar-commit-diagnosis-v1
python -I -S scripts/diagnose_batch_tail.py --input artifacts/cvar-commit-v1 --warm artifacts/primary-budget-constraints-v1 --diagnosis artifacts/cvar-commit-diagnosis-v1 --output artifacts/cvar-commit-tail-risk-v1.json
python scripts/report_stable_tail.py --study cvar --guard artifacts/primary-batch-joint-v1 --aware artifacts/cvar-commit-v1 --warm artifacts/primary-budget-constraints-v1 --diagnosis artifacts/cvar-commit-diagnosis-v1 --tail-risk artifacts/cvar-commit-tail-risk-v1.json --output report/data/cvar-commit-v1
python -I -S scripts/audit_cvar_commit.py
python scripts/explain_cvar_components.py
```

PR创建前已再次fetch；main仍dec1020且为祖先，337a3dd保留。刷新#9/#12至#26正文、完整评论/review/行内线程及#7/#8全文与评论，检索当前22个PR及2个issue，无新增相关意见。#9基线和恢复来源修复、#7内核绑定修复包含于337a3dd并沿原阶段验证；#8最终迁移/实板尚待完成。Discussion4最新回复仍404，不把不可读等同于没有问题；不合并、不关闭issue。阶段Draft以PR26分支为base；最新头CI在PR正文补记。
