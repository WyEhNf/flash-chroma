# 修订93：默认单图路径的布局与角色分块原因辨别

未找到92小作业有效退化的可复核解释，也没有新的产品优化。新诊断的16个配对cell有12个控制有效、4个失效；有效最劣吞吐85.6642%，仍只到80档。24项因素交互仅13项有效，全部未达到预注册的±10%且至少3/4 worker同向兴趣线；11个失效项全部保留。普通N1默认路径的caller工作区偏移、角色分块、构造先后三个有限假设均未获支持，原因仍未解。

**本阶段不恢复92资格。** 92 ordinary N1单线程原地的原最劣82.3051%和其它全部失效继续原样成立；新93的85.6642%来自不同调用组织，不能替换、拼接或平均成更好的92门槛。本阶段不调整2^26提示阈值，不更换模型、库或像素实现，没有新编译。新的有效BAAB/pair0/offset0/blocked中位时间比1.065053、最劣85.6642%，仍未过无明显退化门。

## 为什么要做这个窄诊断

92 ordinary N1/T1/inplace四worker比0.911590、0.974057、1.012771、1.214991；最后worker的92中位3.7525ms对87的3.0885ms，双方A/A为1.01666/1.08710，均有效。它不能因其它worker较快而被抹去。92 N10/T4/分离也有有效退化，但93事先只冻结N1这一问题，没有顺势扩成参数或场景扫描。

静态检查发现六个AVX2对象文件完整字节SHA相同，覆盖cached、andn原地/分离、normal、exception；四个runtime目标函数归一化反汇编201/143/178/357条相同，apply相关RVA相同，外部hot符号整体移0xc0。hint没有保存到Handle，未见新增热操作，但指令相同不能否认有效性能差，也不能证明运行时DLL/heap/缓存/CPU状态相同。原始对象SHA、目标符号及归一化限制见experiments/p16-default-layout/machine-equivalence-v1.json，不冒称四函数的完整机器字节相同。

## 单版预注册与完整合同

仅ordinary af974首图N1、AVX2单线程、原地纯apply，87/92两库都调用默认create。4进程各完整2构造序ABBA/BAAB×2对句柄×2共同work偏移0/64×2角色顺序，共64 cell，禁止筛选。每构造序的四句柄同时存活，在两布局/两顺序复用；全部容量1,852,824B、direct关闭，不传新hint。公共ABI不公开cache数据指针，所有table_mod64明确为None；构造序仅为分配先后代理，不称heap已控。

每进程固定同一source和backing，work0为64B对齐基址，work64后移64B；二者mod64同为0，mod4096相差64（可能跨页回绕）。两个重叠视图只串行使用，与source不重叠；同cell两库完全相同work指针。源、实际work、句柄、模块和公开apply函数地址完整记录。CPU逻辑编号只在每C ABI块外部wall前后读取，端点相同不证明中间未迁移。

blocked与interleaved都每role9个7轮C ABI块，正式63轮、A/A同样63轮，每cell每role对称warm2。blocked先整角色九块再另角色九块，具体首角色在worker/构造/pair/偏移/顺序间按冻结规则镜像；interleaved交错18块并镜像相邻角色顺序。因此原生边界数相同。交错仍会改变两张缓存的共存状态，解释上限是“角色分块状态混淆”，不能唯一归因纯时间漂移或频率。

纯apply使用原库内部时钟，排除前置source→work复制；原copy_apply数组及每块完整C ABI外部wall亦保留。路径/文件SHA、首图解码、fixture分配、毒化/末输出SHA和CPU端点均在wall外。每块仅核最后实际caller-owned输出，2432组SHA全部通过；正式/AA内轮16128、warm内轮256，合16384次整首图映射。source首尾SHA相同，短接口质量另16个实际输出及共同指针合同通过，不以短质量计时论速度。

质量注册6f90d74e1e0660c75498193dc61cc7dedc5d0bdf3d6772081d542ab219aa97a1，质量结果b5cccd78c79f0377204a8b493f272ffbacbbc4c56a33056897a8284fd24a20e1；正式计划22fd615b8aed01808f2f56896b38ebed4331095875fcd74a7c19c2431e7134e4，driver63bddeb8615200023f858228c800560b5630b05c6c5caf441b520a5771911954。正式计划移除新增quality_proof后与事前质量注册逐结构相同，无后改参数。库SHA仍为87的58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158及92的64122d6aca9fe1f1ff2a22e85eb9869264a7fa0b730e5b6b779397875b885c7b。

每cell每role拼接9块63数取中位，A/A严格0.85..1.15，四worker配对按最劣吞吐100/90/80/70/60/50；无明显退化仍要求中位时间比≤1.05且每worker≤1.10并控制有效。全部原始内轮、慢轮和失效保留，不补测/放宽。因素交互比较的是两cell的candidate/reference比之商，要求两cell控制均有效、至少3/4 worker同向越过±10%且中位亦越同线；这是原因研究的兴趣线，不是用户50底线、统计显著性或因果证明。

## 全部配对cell

时间比为92/87，未有效的描述数字不授档，不用于原因支持。

| 构造序 | pair | work偏移 | 调度 | 中位时间比 | 最劣吞吐保留 | AA范围 | 资格/最高档 | 无明显退化 |
|---|---:|---:|---|---:|---:|---|---|---|
| ABBA | 0 | 0 | blocked | 1.012641 | 97.2509% | 0.972196~1.008216 | 有效/90 | 通过 |
| ABBA | 0 | 0 | interleaved | 0.995582 | 99.9672% | 0.919301~1.003959 | 有效/90 | 通过 |
| ABBA | 0 | 64 | blocked | 0.997481 | 98.5354% | 0.953303~1.085402 | 有效/90 | 通过 |
| ABBA | 0 | 64 | interleaved | 1.005021 | 97.6241% | 0.937764~1.063487 | 有效/90 | 通过 |
| ABBA | 1 | 0 | blocked | 0.991822 | 97.1135% | 0.891683~1.034450 | 有效/90 | 通过 |
| ABBA | 1 | 0 | interleaved | 0.985163 | 99.9701% | 0.924539~1.107790 | 有效/90 | 通过 |
| ABBA | 1 | 64 | blocked | 1.018327 | 86.8189% | 0.812224~1.165394 | 失效/未证 | 未过 |
| ABBA | 1 | 64 | interleaved | 1.014053 | 94.1657% | 0.854381~1.102850 | 有效/90 | 通过 |
| BAAB | 0 | 0 | blocked | 1.065053 | 85.6642% | 0.854487~1.090909 | 有效/80 | 未过 |
| BAAB | 0 | 0 | interleaved | 1.026715 | 94.4428% | 0.895387~1.088099 | 有效/90 | 通过 |
| BAAB | 0 | 64 | blocked | 1.007568 | 96.5360% | 0.970031~1.155272 | 失效/未证 | 未过 |
| BAAB | 0 | 64 | interleaved | 1.039680 | 95.4404% | 0.906542~0.973800 | 有效/90 | 通过 |
| BAAB | 1 | 0 | blocked | 1.081360 | 87.8647% | 0.815144~1.178461 | 失效/未证 | 未过 |
| BAAB | 1 | 0 | interleaved | 0.979612 | 96.1782% | 0.917326~1.194507 | 失效/未证 | 未过 |
| BAAB | 1 | 64 | blocked | 0.989121 | 99.9055% | 0.977621~1.130625 | 有效/90 | 通过 |
| BAAB | 1 | 64 | interleaved | 0.988001 | 99.8409% | 0.945250~1.125320 | 有效/90 | 通过 |

## 全部因素交互

比值为该因素第二水平的候选/基线比，除以第一水平；调度第二水平interleaved、偏移第二水平64、构造第二水平BAAB。fixed字段明确其它不变维度。

| 因素 | 其余固定维度 | 四worker比之中位 | AA资格 | 预注册判断 |
|---|---|---:|---|---|
| schedule | construction=ABBA, pair=0, work_offset=0 | 0.974317 | 有效 | unresolved |
| schedule | construction=ABBA, pair=0, work_offset=64 | 1.008480 | 有效 | unresolved |
| schedule | construction=ABBA, pair=1, work_offset=0 | 1.001925 | 有效 | unresolved |
| schedule | construction=ABBA, pair=1, work_offset=64 | 1.016639 | 失效 | invalid |
| schedule | construction=BAAB, pair=0, work_offset=0 | 0.964689 | 有效 | unresolved |
| schedule | construction=BAAB, pair=0, work_offset=64 | 1.019426 | 失效 | invalid |
| schedule | construction=BAAB, pair=1, work_offset=0 | 0.898008 | 失效 | invalid |
| schedule | construction=BAAB, pair=1, work_offset=64 | 1.002599 | 有效 | unresolved |
| work_offset | construction=ABBA, pair=0, schedule=blocked | 0.985052 | 有效 | unresolved |
| work_offset | construction=ABBA, pair=0, schedule=interleaved | 1.009475 | 有效 | unresolved |
| work_offset | construction=ABBA, pair=1, schedule=blocked | 1.026797 | 失效 | invalid |
| work_offset | construction=ABBA, pair=1, schedule=interleaved | 1.049349 | 有效 | unresolved |
| work_offset | construction=BAAB, pair=0, schedule=blocked | 0.957439 | 失效 | invalid |
| work_offset | construction=BAAB, pair=0, schedule=interleaved | 1.015688 | 有效 | unresolved |
| work_offset | construction=BAAB, pair=1, schedule=blocked | 0.902758 | 失效 | invalid |
| work_offset | construction=BAAB, pair=1, schedule=interleaved | 1.002490 | 失效 | invalid |
| construction | pair=0, work_offset=0, schedule=blocked | 1.042102 | 有效 | unresolved |
| construction | pair=0, work_offset=0, schedule=interleaved | 1.031257 | 有效 | unresolved |
| construction | pair=0, work_offset=64, schedule=blocked | 1.012106 | 失效 | invalid |
| construction | pair=0, work_offset=64, schedule=interleaved | 1.021871 | 有效 | unresolved |
| construction | pair=1, work_offset=0, schedule=blocked | 1.117591 | 失效 | invalid |
| construction | pair=1, work_offset=0, schedule=interleaved | 0.986003 | 失效 | invalid |
| construction | pair=1, work_offset=64, schedule=blocked | 0.972570 | 失效 | invalid |
| construction | pair=1, work_offset=64, schedule=interleaved | 0.955944 | 有效 | unresolved |

BAAB/pair1/offset0的interleaved/blocked中位0.898008看似跨过10%线，但控制失效，明确不支持角色分块解释。其余13个有效交互均为unresolved，不将其解释成因素必然无影响，只说明此次有限干预未给出支持。

## 地址与CPU端点观察

全部2432组caller CPU端点有393组前后不同（约16.16%），说明允许集内迁移确实存在；端点相同也可能在内轮迁出又返回。本次没有逐TID钉核、频率/温度计量，不能归因频率、迁移或据此追加无限试验。public apply函数mod64及模块地址只是可读信息，不把其相同推成所有代码/cache布局相同。

| worker | work0地址 | work64地址 | 两者mod4096 | reference/candidate apply mod64 | CPU端点变化/块数 |
|---:|---:|---:|---|---|---|
| 0 | 2624471515200 | 2624471515264 | 64/128 | 48/48 | 101/608 |
| 1 | 1538810155072 | 1538810155136 | 64/128 | 48/48 | 64/608 |
| 2 | 2744819191872 | 2744819191936 | 64/128 | 48/48 | 132/608 |
| 3 | 2316746653760 | 2316746653824 | 64/128 | 48/48 | 96/608 |

Windows11/Ryzen9 8945HX/GCC15.2，进程allowed CPU0/2/4/6，非逐OMP TID绑定；不锁频温控，不使用AVX512，没有目标Intel实测。根代理明确授排他窗，四worker期间全组不编译/JIT/质量/ZIP/Git；既有GUI Python及未定归属credential-manager仍在预检，不宣称宿主绝对独占。

## 结论与归档

本阶段没有识别出能修复小N默认路径的单一机制，保持原因未知；不据有限负交互证明布局/分块永远无影响，也不借CPU端点现象声称因果。92大工作量的独立已证收益和原小N有效退化分别继续成立，本阶段不改变它们。

全部64cell、16配对、24交互、2432实际SHA/16384内轮及地址/CPU数据见report/data/p16-default-layout-v1。独立离线audit复算通过，不加载DLL；execution-sources.zip保留原执行字节与保守支持源，旧CRLF/Git LF关系及两库原构建身份分别明列。没有新原生构建，模型仅为固定ordinary四级。阶段只作为原因研究证据供审阅，不启用新默认策略。
