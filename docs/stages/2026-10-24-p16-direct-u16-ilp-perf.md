# 16题288八角色正式比较：有效子集改善，整体AA未证

Agent：`/root/tail`；任务：精度方向运行时底线；状态：正式试验完成、整体资格未确认；保持旧综合best及Draft，不切默认。不能把本场写成“已过60/70档”或“已正式守住50%”。[质量与RSS阶段](2026-10-24-p16-direct-u16-ilp-native.md)的完整输出一致、表/palette恒等、容量及六进程内存观察继续成立。

同一Windows11 x64/Ryzen9 8945HX、GCC15.2 Release AVX2/OpenMP环境获得排他性能窗口后，先冻结plan/driver/独立checker/实际helpers SHA及AST。八角色为87a399/87旧best、288a399/288旧best、287max/p99、288max/p99；不是把新结果与旧场31%相除。4个独立顺序进程，各四场景（1/4线程×原地/真分离），8角色回文A/B、奇数worker逆序场景；每组完整百图warmup1次、计时5次。共256组×5、256warmup及32构造冷首，所有组末work/source和首批SHA通过。完整百图78,643,200像素，模型固定为原两只第二级候选，没有混入后续root训练模型。

先取每组五次中位数，再跨worker/相位/线程/接口及pure/copy指标取最劣倒数。对应双方角色在同worker/场景的所有metric B/A均须落入[0.85,1.15]；整体通过还要求全部对应AA通过，不允许忽略失败场救线。192个AA检查中22个失败，11个pair均未获得完整AA资格。独立Decimal checker从全部raw重算中位数、AA、528个比较和门槛，1195项检查通过；没有补跑、删除worker或改变门槛。

下表只描述有效子集，不能充当整体正式档位。每pair的100/90/80/70/60/50布尔值完整保留于results.json。

|比较|有效子集最劣速度保留|有效子集最高档|有效/总比较行|
|---|---:|---:|---:|
|288 a399 / 87 a399|89.1711%|80%|36/48|
|288旧best / 87旧best|90.0600%|90%|42/48|
|288旧best / 87 a399|87.6103%|80%|46/48|
|288 max / 87 a399|68.0200%|60%|44/48|
|288 p99 / 87 a399|71.8197%|70%|36/48|
|288 max / 87旧best|73.1558%|70%|40/48|
|288 p99 / 87旧best|73.7564%|70%|32/48|
|288 max / 288旧best|64.8653%|60%|46/48|
|288 p99 / 288旧best|72.4458%|70%|38/48|
|288 max / 287 max|148.4971%|100%|38/48|
|288 p99 / 287 p99|139.5168%|100%|30/48|

有效子集中，保持表/模型/prepare/vector不变后，整体apply调度确有更快的观察结果；但未取得全场资格，不能解释成稳定的1.48/1.40倍保证，也不能孤立归因ILP。两个新候选的`hard50=false`，同时`rejected_by_valid_below_50=false`：与287的有效低50反证不同，本场是整体尚未确认，而非发现了有效低50。速度与精度的联合资格不填写通过；原第二级精度收益保持独立报告。

全部22条失败如下。表中B/A按9位小数展示，完整double精度在independent-check.json与AA-blocking.json；1.151121756仍严格失败，不能四舍五入到门槛通过。

|worker|路径|线程|角色|metric|B/A|
|---:|---|---:|---|---|---:|
|0|inplace|1|287p99|pure_apply_seconds|1.236925897|
|0|inplace|1|287p99|copy_apply_seconds|1.227669462|
|0|to|1|288p99|api_total_seconds|1.216052535|
|1|inplace|1|288a399|pure_apply_seconds|1.209907624|
|1|inplace|1|288a399|copy_apply_seconds|1.178430456|
|1|inplace|1|287max|pure_apply_seconds|0.798077778|
|1|inplace|1|287max|copy_apply_seconds|0.811718986|
|1|to|1|87a399|api_total_seconds|0.848120340|
|1|to|1|87old|api_total_seconds|0.834414766|
|1|to|1|288a399|api_total_seconds|0.729744992|
|2|inplace|1|288p99|pure_apply_seconds|1.195853584|
|2|inplace|1|288p99|copy_apply_seconds|1.185609474|
|2|inplace|4|287max|pure_apply_seconds|1.165076336|
|2|to|1|288max|api_total_seconds|1.151121756|
|2|to|1|288p99|api_total_seconds|0.820648233|
|3|inplace|1|87old|pure_apply_seconds|1.163963394|
|3|inplace|1|288a399|pure_apply_seconds|0.791642282|
|3|inplace|1|288a399|copy_apply_seconds|0.816865848|
|3|inplace|1|287p99|pure_apply_seconds|1.234390023|
|3|inplace|1|287p99|copy_apply_seconds|1.209825178|
|3|to|1|288a399|api_total_seconds|1.152520928|
|3|to|1|288p99|api_total_seconds|0.839606815|

下面定位每pair被哪些角色/场景阻断。`wN in1/in4/to1`分别指worker N、原地1/4线程、真分离1线程。任一metric失败使该场景该角色不合格，因此同场pure/copy都不能用于整体通过；不是只排除失败的那一项。

|pair|阻断角色及场景|
|---|---|
|288a399 / 87a399|288a399：w1 in1/to1、w3 in1/to1；87a399：w1 to1|
|288old / 87old|87old：w1 to1、w3 in1|
|288old / 87a399|87a399：w1 to1|
|288max / 87a399|288max：w2 to1；87a399：w1 to1|
|288p99 / 87a399|288p99：w0 to1、w2 in1/to1、w3 to1；87a399：w1 to1|
|288max / 87old|288max：w2 to1；87old：w1 to1、w3 in1|
|288p99 / 87old|288p99：w0 to1、w2 in1/to1、w3 to1；87old：w1 to1、w3 in1|
|288max / 288old|288max：w2 to1|
|288p99 / 288old|288p99：w0 to1、w2 in1/to1、w3 to1|
|288max / 287max|288max：w2 to1；287max：w1 in1、w2 in4|
|288p99 / 287p99|288p99：w0 to1、w2 in1/to1、w3 to1；287p99：w0 in1、w3 in1|

288old自身全部AA通过，但不能替其他角色消除漂移。新max只在一场略超AA上限，仍依冻结规则不通过；新p99自身多场失败。两个原87基线也有失败，所以不能把全场无效都归给旁路287或新调度。没有测量CPU频率、温度或系统事件，不把角色定位冒充物理原因诊断。

构造/冷首的32个样本及模型容量、实际地址mod64均保留在worker原件；无构造AA，不据此宣称冷首加速。正式八角色同时驻留进程峰值未采样，不能把先前单模型RSS峰冒充本次峰；开跑主机可用物理内存原件另存。单模型真实内存与表/prepare/栈详见质量阶段。没有ARM、官方服务器、AVX512或官方成绩结论。

证据为`report/data/p16-direct-u16-ilp-perf-20261024/`，10原件、12源码成员、全部4worker raw/console、22条AA与11pair阻断映射。原始目录`artifacts/p16-direct-u16-ilp-perf-v1`。复现需先获取独占性能窗口，执行`python scripts/run_direct_u16_ilp_perf.py --cache-root F:/Hackathon/projects/16-lut-color --output <新目录>`；环境为UTF8输出、`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`、`OMP_DYNAMIC=FALSE`、`OMP_WAIT_POLICY=PASSIVE`，API显式1/4线程。独立checker与archive脚本仅复算/归档JSON，不重跑性能。后续暂不设计重跑或新实现，先保留完整控制证据与旧综合best。

## 联合提交记录

本阶段实际与四轮训练尾部阶段共同进入`849085dfa451988e93880dc13451152e19d54b08`；两阶段均保持各自预注册及原件。共享index交接竞态与随后原字节核对见[提交边界说明](2026-10-24-precision-stage-commit-boundary.md)，没有重写历史或改数值。
