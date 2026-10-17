# 热点主改与邻近节点的重叠联合补偿

Agent：Codex；Operator：WyEhNf；Task：PR #28 后续；Status：Completed（重叠联合块通过保护及完整终验；修复mean误拒，Draft待审）。

## 阶段问题与算法

PR28证明最坏单元在当前固定轴表下的整数RGB最小最大误差恰为42，但降低峰值的候选会损害照片。最小修改35909 B115→113可使推导全域max54→53、主缺口1585→1582，却令div2k-0900/div2k-0889/kodak-kodim03的SSE分别增加3307/1023/2322。它们及对应选择样本的mean/RMS固定保护失败，未被接受。

PR25曾由相邻节点35910 B106→107改善同三图，为补偿方向提供依据；当前模型已不同，旧收益不能相加。本阶段从PR27同字节模型`f577f0749f7aae56275774d0bdbaad9305d99652ca08ba21cc928c8ff84962c4`起步，固定主改35909 B115→113，只比较辅助35910当前B107加1、加2两个幅度。两节点在同一原模型上同时修改，并保留基线、主改单独、两种辅助单独和两种联合共6个反事实。

`local_compensation.py`提供有限冻结块的候选族，检查节点前值、合法幅度及RGB8范围，不隐式裁剪/uint8绕回。所有候选保留权威idx/frac与其他节点字节。选择只允许联合块，不能把辅助对照当作主改已修复。没有扩大主节点、辅助节点、网格或参数矩阵。

重叠支撑使RGB8舍入及SSE都不可直接相加；runner真实重放每块，记录`joint-(primary+helper-baseline)`的输出差异、完整域及101组SSE交互。不会把两份单改预算相加当作联合可行性证明。旧主改单独的模型SHA、全部频数、指标及拒绝必须逐项复现PR28，空修改基线必须通过全部保护。

## 固定验收与复现

`experiments/local-compensation-v1.json`在执行前冻结。热点单元仍为648色，其8个正权重节点再并入相邻辅助节点；一次枚举整个节点集的完整非零支撑，并一次建立80完整照片/既定选择像素/合并101组频数。20历史审计不反馈，只有最终选中模型才观察完整100图。数据已见过，不能称盲验。

原历史目标和预算保持，固定参照仍是PR27起点的101组/完整域mean、RMS、p99端点、max及CVaR；主缺口不升，全域max严格下降。只从两联合块中按完整域max、历史缺口、节点数和确定性名称选一个；如果均失败，不进一步扩充候选。独立标准库验证器重建冻结候选、权重/舍入、完整支撑、频数、交互及选择，包含原生模型/程序/输出绑定；不独立解码80张PNG。

选中后只执行一次完整256³/100图、独立NumPy整数oracle、既有单线程标量/AVX2终验。完整分布必须匹配局部完整频数，80反馈图指标也须逐项匹配。未选中则复用同字节PR27旧终态，保留拒绝。下界42直接复用PR28证书并独立复核，不重新执行LP/MILP。

集中6项必要合同：1个真实重叠Q16例验证单改受损、联合补偿、非可加输出及陈旧前值拒绝；回归原短直方图/101组空修改入口1项及CVaR4项。其他未改模块不重复堆测试。验证前冻结源/计划/合同；具体失败才做保留日志后的定向修复。

环境沿PR28：Windows11 10.0.26200 / Ryzen9 8945HX（16核32线程）/ Python3.12.14 / NumPy1.26.4 / SciPy1.15.2 / Numba0.60.0 / llvmlite0.43.0。合同NUMBA_NUM_THREADS=4；数值入口移除此变量并自行设4；BLAS/MKL/OMP1。局部映射为NumPy整数，选中后的完整映射为Numba4；原生GCC15.2 Release单线程标量/AVX2，程序SHA ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a。目的为联合可行性、舍入交互与误差转移，不比较性能。

```powershell
# python使用artifacts/error-study-py312/Scripts/python.exe；先设置上述线程/UTF8环境。
python -m pytest tests/test_local_compensation.py tests/test_local_minimax.py::test_guard_assessment_accepts_unchanged_short_histogram tests/test_cvar_guard.py -q
# 移除NUMBA_NUM_THREADS，由runner设置；输出拒绝覆盖。
python scripts/run_extreme_cell.py --plan experiments/local-compensation-v1.json --output artifacts/local-compensation-v1
python -I -S scripts/verify_extreme_cell.py --input artifacts/local-compensation-v1 --output artifacts/local-compensation-v1/verification.json
python -I -S scripts/report_extreme_cell.py --study compensation --input artifacts/local-compensation-v1 --output report/data/local-compensation-v1 --roundtrip artifacts/local-compensation-roundtrip-v1
```

## 协作与边界

已fetch，main仍dec1020且为祖先，基于PR28头d738508建立工作分支；337a3dd工程修复保留，AGENTS.md只读。创建/更新PR前刷新相关正文、完整评论/review/行内线程、#7/#8及近期检索，保留Discussion4访问缺口，不合并/关闭。每阶段中文提交、说明、Draft PR，Operator为WyEhNf。

无官方数据或Threshold；距离为RGB欧氏码值，非CIEDE2000。不修改默认/冠军、运行时、模型格式或硬件后端。这是单级局部研究，不代表四级新模型、未知照片泛化或实板性能。阶段结果、实际来源、拒绝或收益及CI在执行后补入。

## 首轮结果揭示的证书误拒与修复计划

初始源/计划/6项合同冻结于`6e37340`，一次6/6通过（5.76秒，14个既有matplotlib/pyparsing弃用警告）。冻结6反事实运行`artifacts/local-compensation-v1`完整完成；主改模型/频数/拒绝与PR28逐项一致。两节点实际重叠支撑178色，辅助+1/+2时有67/64色不能用单改输出相加；全域SSE相互作用分别+495/+346。

辅助+2的联合块已补回3完整图的mean/RMS，并同时改善全域mean/RMS/max/CVaR、主缺口1585→1582。它只因group83及100的mean充分条件被拒绝。独立复核首轮6记录/选择/交互通过，旧结果和源码不覆盖。

该两组的平方误差频数变化相同：400减1、441加1、841加1、900减1。距离和变化`−20+21+29−30=0`严格相等，SSE变化−18。未变的非平方误差频数却分别进入参照下界/候选上界，造成两个分开总和的Q24区间相交，从而保守误拒；这不是实际mean上升，不能通过继续改辅助幅度解决。

本阶段据此修复充分证书，不增加候选/阈值/配置：`histogram_delta.py`先抵消相同频数，再对有符号差值`Σ(delta_count*sqrt(d²))`计算Q24界；负系数用相反方向根号界，差值上界≤0才接受。等像素数保证mean比较等价。应用于公开`Stability`照片/全域及本阶段选择器；标准库验证器另用Python整数独立复算。原历史预算、mean不增要求及其他指标保持。新方法仍为充分条件，混合非平方根的极近差值仍可能保守。

修复后集中定向5项：2项新差值证书及公开照片/全域/独立验证器回归（真相等接受、真增加拒绝），原固定保护3项回归（误差转移拒绝/回滚、大频数统计、三节点公开路径）。先冻结修复，再仅对同一6模型重放选择，复用首轮已核支撑/频数，不再次解码80图。若联合块通过保护，只做一个新终态的完整256³/100图/原生终验。

```powershell
python -m pytest tests/test_histogram_delta.py tests/test_stability.py -q
python scripts/run_extreme_cell.py --plan experiments/local-compensation-v1.json --frequency-cache artifacts/local-compensation-v1 --output artifacts/local-compensation-v2
python -I -S scripts/verify_extreme_cell.py --input artifacts/local-compensation-v2 --output artifacts/local-compensation-v2/verification.json
python -I -S scripts/report_extreme_cell.py --study compensation --input artifacts/local-compensation-v2 --prior-run artifacts/local-compensation-v1 --additional-contract-log artifacts/histogram-delta-contracts-v1.log --output report/data/local-compensation-v1 --roundtrip artifacts/local-compensation-roundtrip-v1
```

## 修复后的真实联合结果

差值证书/公开保护/独立验证器修复冻结于`7e5a4e3`；定向5项一次5/5通过，4.11秒，无跳过。正式数值运行记录`7e5a4e32300dc58aa7642e865da8ba6e9e3a8017`，输出`artifacts/local-compensation-v2`。同一6模型、局部输出、完整频数、逐组指标及主缺口与首轮完全相同，归档器逐项核对；变化只来自更强的mean非增证明。没有新增幅度、候选或调整阈值，也没有再次解码80图建立频数。

正式选择为`joint_2`：节点35909的B115→113，节点35910的B107→109。主改单独仍10项保护失败；辅助+2单独因原/固定全域RMS及CVaR失败3项。该块的两个非空真子集均不可提交，真实联合块通过全部保护；这证明的是当前冻结块的互补性，不证明其他单节点都不可行。

| 反事实 | 全域max | 主缺口 | 全域SSE变化 | mean/RMS等保护失败数 |
| --- | ---: | ---: | ---: | ---: |
| 基线 | 54 | 1585 | 0 | 0 |
| 主改单独B−2 | 53 | 1582 | −9844 | 10 |
| 辅助单独B+1 | 54 | 1585 | +1458 | 2 |
| 主改与辅助+1 | 53 | 1582 | −7891 | 8 |
| 辅助单独B+2 | 54 | 1585 | +3620 | 3 |
| 主改与辅助+2 | 53 | 1582 | −5878 | 0 |

两节点有178个颜色的实际非零支撑重叠。辅助+2时64个颜色的联合输出与单改相加预测不同，最大分量差1；全域SSE交互+346，因此单改变化之和−6224不能作为实际联合−5878。辅助+1则67色不一致、SSE交互+495。

| 原受损组 | 主改SSE变化 | 辅助+2 SSE变化 | 单改和 | 实际联合SSE变化 |
| --- | ---: | ---: | ---: | ---: |
| div2k-0900 | +3307 | −4079 | −772 | −1086 |
| div2k-0889 | +1023 | −1272 | −249 | −410 |
| kodak-kodim03 | +2322 | −10345 | −8023 | −8131 |
| kodak选择样本 | +41 | −98 | −57 | −18 |

三张完整照片的mean/RMS现在均下降。样本及合并样本的距离和严格不变、SSE下降18；旧总和界的误拒由可独立验证的零差值证书解除，不是通过豁免或放宽保护。辅助本身增加全域SSE/CVaR，主改提供的全域余量与辅助提供的照片余量互相补偿。

## 一次完整终验

选择在100图之前冻结，仅对一个新终态执行一次完整256³、100张1024×768 RGB8、独立NumPy整数oracle及单线程标量/AVX2。新全域分布与局部完整频数逐指标一致，80反馈图的mean/RMS/p99/max也逐项相符；原生两份回执全流SHA一致、0字节差异。

| 指标 | PR27起点（复用） | 新联合块（新终验） |
| --- | ---: | ---: |
| 完整域mean | 0.981701047063 | 0.981694013715 |
| 完整域RMS | 1.879279720123 | 1.879186502283 |
| 完整域p99 | 7 | 7 |
| 完整域max | 54 | 53 |
| 完整域CVaR1% | 11.525292126127 | 11.525119273522 |
| 100图mean | 1.033861633812 | 1.033858899946 |
| 100图RMS | 1.384107186366 | 1.384062964505 |
| 最差单图p99 | 7.141428428543 | 7.141428428543 |
| 照片max | 46.043457732885 | 46.043457732885 |
| 历史缺口 | 1585 | 1582 |

100图mean/RMS各3改善、0退化、97持平；p99/max全部100图持平。20历史审计图四指标全部持平。审计没有反馈本阶段选择，但历史数据已观察，不称盲验。全域max下降1码值，约1.85%，平均指标收益很小，不夸大为普遍或显著收益。

新模型SHA `4fe0dfd4b512e0a17996c5786339a84a452d62c8e05c07bc1256bd685c743cac`；新完整流SHA `0336f91c0d956cb113c9ee8f080e680bca333c8630204a1977f629b87932bda8`；完整参考仍为 `6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7`。当前仍有历史尾部失败，1582未清零，不能称满足全部题目门槛。42是前阶段固定单元最优值，此次模型max53仍不代表全局最优。

## 证据、来源和交付

独立标准库`-I -S`重新枚举648色单元、5996色完整非零支撑、6模型、101组及完整域频数，复算2组舍入/SSE交互、零mean差证书和最终选择；核对新完整流实际长度/SHA、原生模型/程序/内核/输出绑定及完整照片与组频数一致。初始复核及解压后复核均无NumPy/SciPy/Numba依赖。未独立解码PNG的边界保持；实际100图终验由完整研究映射执行。

[证据目录](../../report/data/local-compensation-v1)约3.97MB，成功归档38成员、首轮37成员，含6模型、两次数值源/环境、旧保守拒绝与新差值证明、全部局部频数/交互/候选、200逐图（100新/100复用）、6分组及4原生回执（2新/2复用）。完整RGB流本机保留，精简包记录SHA及首次完整流复核；解压后不重新执行全域，`full_stream_checked=false`如实表示包内无该大流，不能把它当作新全域执行。

`266164c`归档器核对两轮同模型/输出/频数/指标，独立复核旧轮的源码SHA，保留两个合同批次及其来源，不把初始6项与定向5项冒称同一次11项。原始6反事实全部保留，没有删掉辅助+1的拒绝结果。旧阶段的验证器和源码快照保持原版本；本次升级公开mean证明及独立验证器，不能将新SHA写回旧记录。当前新数值源与7e5a4e3实测ZIP同字节；仅旧interp/io工作区CRLF与Git LF差异沿前阶段逐项披露，精确复现恢复快照。

推送前再次fetch，main仍dec1020且为祖先，337a3dd修复包含于本分支。刷新#9/#12至#28正文、完整评论/review/行内线程及#7/#8，检索当前24个PR/2个issue，无新增相关意见。#7内核绑定/#9基线与恢复来源修复沿原证据；#8最终接口迁移/实板待办保持。Discussion4最新回复仍404，保留访问缺口，不合并/关闭。阶段Draft以PR28分支为base，Operator为WyEhNf，最新头CI在PR正文补记。

下一步应将已验证的重叠条件补偿接入自动候选选择，减少手动指定节点；同时用剩余热点和历史p99反例验证收益，继续保留mean非增的整数证明。默认、冠军、C++/硬件路径及模型格式保持，官方Threshold未知，不作SOTA/四级新模型/实板或性能声明。
