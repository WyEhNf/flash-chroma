# 第16题评分导向的研究选择依据

Agent：Codex `/root/research_merge`；Operator：本会话用户；日期：2026-10-27（Asia/Shanghai）。本文先静态审计已同步的研究结果；后续实际实施、重新复核及最终选择见[交付报告](2026-10-27-p16-score-candidate.md)。本文引用的旧耗时仍保持原来源，不将推荐配置称为已经证明的最高总分。

审计工作树为 `F:/Hackathon/worktrees/p16-unified-avx512-20261026`、工作分支 `codex/p16-score-candidate-20261027`，静态读取时HEAD为 `082f3d975566dd4ac409b7981891372308fd1337`。该提交已汇入 `b685a3b` 联合存储/AVX2筛查及其祖先 `3d4d6d9` 逐级插值研究；不是仅看远端标题推断实现已升级。本文只新增说明，不改源码、模型或既有证据。

## 应冻结的当前版本

**当前固定Cinema演示配置继续选择373a模型、100扫描线准备器和AVX2线性direct后端。** 实施复核后，显式均值优先选项改为max_first；max48/max41保留研究记录。AVX-512及最新T0/store变体均没有取得默认升级资格；内存宽裕时不把页字典解码放进默认像素路径。

**针对未知四张新LUT，提交物必须是接收源LUT、固定拟合参数、保留四级整数边界的通用流程，而不是将373a二进制当作通用模型。** 现有通用CLI、四面体AVX2、标量回退和结构化路径保留；固定Cinema分输出/direct研究是其中有资格时的加速/精度示例，不能替代新LUT拟合验收。

按当前40分精度、40分速度、20分工程方向，先满足逐图平均ΔE阈值，再在合格候选中比较批次总时间及运行内存。官方Threshold、低均值如何折成精度分、速度归一分母及工程打分细则都未知，所以不能由“40/40/20”计算一个精确总分，更不能承诺当前配置必然夺冠。[题面与最新六项口径](../../PROBLEM.md)仍是依据。

## 固定Cinema模型的精度与实际代价

以下精度使用相同100张1024×768已见图，按全部78,643,200像素的RGB欧氏距离求平均。它不是官方测试集或新的盲测。运行时正确性一致不等于相对四张密集原表的近似误差为零。

| 模型 | 百图平均ΔE | p99 | max | 已有证据支持的选择 |
| --- | ---: | ---: | ---: | --- |
| 373a | 0.695486159059 | √12 | √57 | 已交付固定模型，普通8位direct，继续默认 |
| max_first | 0.679090181058 | √12 | √50 | 这四个已验模型中平均误差最低，宽表吞吐需新同库比较 |
| max48 | 0.679109463497 | √12 | √48 | 均值仅略高于max_first、max更低；速度尚未完整授档 |
| max41 | 0.680936007872 | √12 | √41 | max更低的精度选项，均值不是四者最小 |

精度原件为 [完整max41质量JSON](../../report/data/p16-cinema-current-full-quality-20261024/results-v2.json)、[max48质量JSON](../../report/data/p16-cinema-max48-pareto-quality-20261024/results.json) 与 [max_first质量JSON](../../report/data/p16-cinema-second-nodes-v1/max_first-accuracy.json)。[统一精确表](../../report/data/p16-tail-frontier-plot-20261024/data.md)可交叉检查公共角色。各模型还存在部分逐图、CVaR及单级独立忠实度代价，不能只用聚合均值掩盖，具体见 [前一轮汇总](2026-10-26-p16-unified-research.md)。

最新统一库在Ryzen9 8945HX的既有一次描述性百图场中，AVX2四线程373a为17.0495ms、max41为19.1434ms；新句柄至首批连续wall的单次观测为41.0228ms和65.0877ms。由这组记录直接计算，max41均值改善约2.0921%，热批次时间增加约12.2813%，首次wall增加约58.6623%。这只是同场观察量，不是分数差或严格性能保证；该场没有A/A或配对交错。完整边界见 [统一实施报告](2026-10-26-p16-unified-avx512.md)。

因此，若373a已经满足实际逐图均值Threshold且速度权重较大，现证据更支持保留373a；若某个真实LUT的373a类拟合不合阈值，则必须另选已验更准模型，不能用快而不合格的输出换速度分。max41也不能仅凭名称和max较小自动升级，因为用户明确主指标是平均值。

max_first在旧287库有有效低50%吞吐负例；后续288改善了有效子集，但A/A不完整，不能授整体资格。max48在87因palette超过255回退；新293/统一库可能解锁宽表，仍须在同一库中实际检查路径并集中比较。旧库负例不证明新库必然失败，旧质量通过也不证明新库一定快。见 [287负例](2026-10-24-p16-direct-u16-perf.md)、[288边界](2026-10-24-p16-direct-u16-ilp-perf.md)及 [宽表正式场](2026-10-24-p16-direct-cache2-performance-v2.md)。

## 四套固定模型的可用身份

373a和max41已经随Git交付，分别位于 `data/p16-unified-models/default/` 与 `data/p16-unified-models/max41/`；四级及sidecar完整SHA见 [manifest](../../data/p16-unified-models/manifest.json)，来源和MIT许可见 [模型说明](../../data/p16-unified-models/README.md)。它们各457,468B的文件负载，不等于运行时direct/cache和图像总内存。

max_first和max48的小模型及oracle在本机精度研究工作树可用，尚未由本文加入统一包。本文读取旧identity并静态核对这两套共10个SLUT/sidecar实际SHA，均一致；没有读取50MiB oracle重新做像素验证。

| 角色 | 模型目录（四SLUT及sidecar） | 首级SLUT SHA256 | 独立完整RGB预测流 |
| --- | --- | --- | --- |
| max_first | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-second-nodes-v1/max_first/candidate/` | `73dc15fea4db5fb10a481336e18256cff040ca291a9713dc1c383ad84739b5ad` | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-second-accept-max_first-v1/candidate.rgb` |
| max48 | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-first-safe-cpsat-accept-v2/candidate/` | `59c333adb5480244ea0e22808f625259a94a21d3b7e53c28656f7362990627f4` | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-max48-pareto-quality-v1/candidate.rgb` |

两目录中的文件名为 `candidate-base.slut`、`stage2.slut`、`stage4.slut`、`channel-frac.bin`；第三级共用 `F:/Hackathon/projects/16-lut-color/artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut`。两者的stage2/3/4 SHA依次为 `904e30a1c0f805175b0b9518949e4e96c9ff2a7e7980978ed8e90fd1282bd924`、`95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234`、`5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386`，仅首级sidecar非空，SHA为 `85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff`。

max_first完整流认证SHA为 `143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e`；max48为 `de4a98d5f3b3d430e349e83146d211296a4e6b3e2a9664a5806b321384a3c3f9`。373a为 `373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed`；max41为 `728666cbc05f0cd2d9da112ce41a26117d67baee1511760d83df8f8cefe8ed98`。这些oracle是测试资产，运行时不读取它们。

## pipeline逐级插值成果究竟改变了什么

`3d4d6d9e07df9e24c25f52f733c8535e3d9890e1`带来的是 [Numba研究归档](../../report/data/pipeline-interpolation-20261021/report.md)，不是新的C++默认插值实现。固定三条数值链、每链统一m17或m33，从六种旧拟合配置按单级4096像素/图均值选模型，再比较相同节点的统一tetra、统一tri和逐级matched。它没有重新拟合，没有枚举全部16种tri/tetra组合，也没有实现每级不同m的这组研究。

相同m33设置的百图均值如下；`kinds`中0为tetra、1为tri：

| 固定源链 | uniform tetra | uniform tri | matched | matched kinds | 仅在已测三配置中均值较优者 |
| --- | ---: | ---: | ---: | --- | --- |
| Amber Haze→Arcade Dayz→Blow Me Down→Caramel Plum Cake | 1.189925 | 1.082575 | 1.125933 | 0,1,0,1 | uniform tri |
| 1910s→1920s→1930s→1940s | 2.019840 | 2.768806 | 1.783380 | 0,1,0,0 | matched |
| Grey Matter→December Greens→Emerald Malaise→Irish Uprising | 0.719381 | 0.662954 | 0.662954 | 1,1,0,0 | uniform tri / matched |

六个链/尺寸设置相对uniform tetra为4个均值降低、2个保持，但相对uniform tri存在1个退化。链3的uniform tetra从m17均值0.711059到m33反而0.719381，说明较大网格配固定恢复器也不必单调更好。可吸收的判断是**每级m和恢复方式可在离线阶段固定选择，最终应按四级终点误差检查**；不能据此把matched无条件设为所有新LUT默认，或以每级最小均值推导全链最优。

这条旧Cinema matched均值1.783380与现代373a不是相同模型；即使源顺序相同，也不能把pipeline表中的11.71%下降直接乘到373a上。三线性和四面体是不同数学恢复器，精确语义不同，不能把已验tetra模型简单改kernel再声称原质量证据有效。

pipeline性能使用Intel Core Ultra5 125H、Numba0.60/TBB四线程，含输出分配与四级恢复、不含拟合/读图/JIT。例如Cinema m33 matched五轮中位为约3780.158ms/100图；这不是新统一C++ direct热核的时间，也不能与另一台8945HX的17ms相除产生加速倍数。每配置仅98,304探针核独立参考，另100图全像素与重复输出一致；没有四级完整RGB8原生验收。

模型与参考身份保存在 `report/data/pipeline-interpolation-20261021/evidence.zip` 的 `data/plan.json` 和 `data/experiment-run.json`，matched输出SHA在 `data/chains.json`。本机 `F:/Hackathon/projects/16-lut-color/artifacts/local-lut-study/20261016` 只有summary，固定24条SLUT模型路径均不存在、references也缺失；归档没有携这些模型或全域oracle，所以不能把可读报告当成即刻可部署模型。重新拟合所得模型也不能冒充原SHA复跑旧证据。

现有C++核心 `apply_chain(..., Kernel k, ...)` 提供全链一个kernel，包括tetra与tri_float；统一研究wrapper也没有接入pipeline的四个kind数组。要工程化逐级matched，须明确保存四个恢复器及各自整数边界，补后端一致性和真实批次测试；它是后续可做工作，不属于本次同步自动获得的能力。

## 对未知LUT的通用选择边界

通用流程先固定源四LUT、源格式/域/舍入，再分别拟合每级。以当前成熟四面体C++路径为起点，可在离线比较m17/25/33、不同网格及已有拟合方法；m可各级不同，不能按测试图像改参数。确有单级tri收益时，把tri匹配模型作为另一个整链候选，以四级终点均值和完整语义验证决定，不能跳过序列化来源及实际后端验证。

现有 [R47混合容量](../r47-mixed-capacity.md) 说明允许不同m有实际收益，但仅限已证明可分离的18个训练源，9个留出源未验；不能把其解析曲线选择器无证明地套给一般三维LUT。原始68个既有模型筛选也使用旧照片抽样，并不构成新LUT的独立泛化保证。通用得分候选应由**拟合器＋固定选择规则＋正确运行时**组成，Cinema模型只作为回归和性能样例。

几十GB内存条件下，保留精确线性派生表和调用方输出缓冲；对象SHA去重可在模型包/加载层共享相同后级。`b685a3b`将两配置914,936B静态对象去重为681,594B，这是可利用的包体/重复owner信息，尚无生产加载器实现。级间差分比原始节点更大，不进像素热解码。zlib/xz包体缩小不等于运行内存或批次时间降低。

## CPU后端、评分选择和下一次集中验证

保持CPU-only，目标6140未实测。已实现AVX-512在8945HX两场均未快于同场AVX2，不能因指令更宽升级；最新 [joint AVX2筛查](2026-10-27-joint-lut-avx2.md) 的四个prefetch/store候选也都未取得性能资格。它的完整域检查是确定性合成ID表夹具，不是新的真实四LUT色差验证，且环境为125H。当前应继续使用已验AVX2基线、显式AVX-512选项及标量回退。

要改变默认，下一次集中验证至少应固定同一库、四模型和照片SHA：先核实际direct格式及输出与各自oracle一致，再同环境测完整百图、创建至首批连续wall、参数固定性及运行内存。重复和A/A控制须随计划记录；不能将历史不同库、不同硬件、不同计时边界的最优值拼作一个新总分。若无法得知官方评分函数，可交付明确的平均精度/批次时间Pareto表和满足Threshold后的推荐，不能生成伪精确得分。

本文静态审计不要求为同步而反复重跑旧heavy质量矩阵。实际实施已对新增模型和交付包集中验证，见交付报告；未变结果继续沿原件引用。工程20分方面优先补齐通用输入、固定参数清单、正确回退、来源许可、可复现构建和清晰内存账本，不以代码变多、文件更小或未执行的平台声明换取“创新分”。

## 本轮静态核对记录

本次静态审计使用Windows PowerShell、Git、JSON和ZIP只读访问核对提交来源、pipeline计划/原始输出角色及模型可用性，10个max_first/max48小模型SHA通过。本文数值来自上述历史原件或标明的同场算术换算；该审计子任务本身未执行编译、JIT、拟合、native像素调用、性能/RSS采样、push或PR操作。主任务后续执行结果见交付报告，仍未测试6140或取得官方Threshold。
