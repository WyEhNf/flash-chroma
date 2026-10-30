# 第16题三方向研究汇总与统一实现选择

Agent：Codex `/root/research_merge`；Operator：本会话项目用户；日期：2026-10-26（Asia/Shanghai）。本文合并精度、速度、内存研究的已有证据，并按用户最新六项说明选择统一实现。本文工作为源码、已有 JSON、模型路径及小模型文件 SHA256 的静态核对，没有重新拟合、执行像素映射或测量性能。统一运行时的本轮构建、正确性与性能应由对应实施报告另行给出，不能由这份汇总代替。

## 本轮评估口径

1. 四级的 `m` 可以彼此不同，均须满足 `17 <= m <= 33`。每个固定 LUT 的稀疏化参数一经选定，所有测试图像使用相同参数；不能按测试图片重新拟合或选不同稀疏模型。运行时后端和等价布局选择不得改变这些参数或逐级整数语义。
2. 精度主指标为所有像素 RGB 欧氏距离的平均值：先对每像素计算 `sqrt(dR*dR+dG*dG+dB*dB)`，再求平均；不能以 RGB 分量均值或 RMS 代替。逐图均值仍须报告。当前100图尺寸相同，百图全部像素均值等于100个逐图均值的等权平均；以后尺寸不同时按像素数加权。p99、max、CVaR继续作为质量观察量。
3. 目标数据是日常图像处理、类似 Photoshop 调整生成的 LUT。当前 Cinema 固定四表链和已见100图是研究样例，不能据此声称覆盖任意常用 LUT，或将模型特有的少色调色板性质当作通用前提。
4. 性能报告以批次处理总时间为单位，不只给单张或单像素时间。固定100张1024×768图包含78,643,200像素。分别报告已准备句柄的完整百图映射时间，以及新句柄创建至首批实际输出返回的连续 wall；准备、解码、文件 I/O、分配是否包含必须随结果明确列出。历史排除准备/解码的热时间不能直接充当首次作业总时间。
5. 使用通用 CPU，不使用 GPU 或 NPU；初步目标是 Intel Xeon Gold 6140。C/C++/Python均可，建议 C++17承担热路径、Python承担离线拟合和复现驱动。历史性能实测机为 Windows11 x64 / Ryzen9 8945HX / GCC15.2，不能写成目标 Intel 成绩。
6. 内存指程序运行期间的 LUT、图像、输出和准备暂态等占用。测试机有几十GB以上内存，因此本轮优先保住精度和批次速度，不为缩小几MiB派生表默认引入明显解码代价。模型容量、构造暂态、映射后端工作区及进程 RSS 分开记录。

## 推荐统一配置及备选

默认精度模型选择 **373a**，准备器选择已有完整质量与百图作业收益证据的 **修订100扫描线实现**，热映射保留线性8位 direct 表。新增实现同时接入293的宽索引支持，使 **max41** 可以作为显式精度选项；AVX-512是保持整数结果的可选热后端，须具备 CPU/OS 状态检查和 AVX2/标量回退。

这是一份当前证据下的工程选择，不是所有算法或全部 LUT 的全局最优证明。默认373a的原因是其精度收益已有同核速度验收；max41改善最大误差，但更宽调色板和更大直接表带来实际代价。以下均为同一固定100图的所有像素聚合值：

| 模型 | 平均ΔE | p99 | max | 当前资格 |
| --- | ---: | ---: | ---: | --- |
| a399 | 0.810320558604 | √14 | √66 | 共同原锚点 |
| 373a | 0.695486159059 | √12 | √57 | 共同87核同场相对a399最劣95.6864%，90%速度档通过 |
| max_first | 0.679090181058 | √12 | √50 | 平均误差更低的 Pareto 候选；宽表整体速度资格未取得 |
| max48 | 0.679109463497 | √12 | √48 | 精度研究候选，未获得完整速度资格 |
| max41 | 0.680936007872 | √12 | √41 | 完整数学/原生质量通过；293百图热场60档，完整冷热50%尚未证明 |

373a完整色域平均ΔE为0.822502846523、p99为√12、max为√57；max41为0.800103255389、3、√41。用户明确平均值口径后，不能只按max选型：max_first的百图平均误差低于max41，后者并不在所有指标上支配前者。

max41相对373a的百图聚合均值更低，但逐图有2图均值、6图p99、2图max退化；百图CVaR由4.32123800825升到4.35270417251。相对max48，max41有94图均值变差。统一接口应保留明确的模型名称，不把尾部改善描述为任意图片或每级独立LUT全部更准。

指标直接来源为 [完整质量结果](../../report/data/p16-cinema-current-full-quality-20261024/results-v2.json) 的 `photos.a399`、`photos.best`、`photos.current741`、`photos.candidate`，其中 `best`即373a，`candidate`即max41；原JSON SHA256为 `7c3553d01031cbd0df611426f8ce9426bdc1d4115800fa645bc23713de567778`。max_first来自 [独立质量结果](../../report/data/p16-cinema-second-nodes-v1/max_first-accuracy.json)。[聚合精确表](../../report/data/p16-tail-frontier-plot-20261024/data.md)核对了公共角色的重复字段一致性。真值为四张原始256³ LUT逐级整数串联，不能把稀疏预测自身当gold。

## 速度方向可吸收的成果

修订100利用完整RGB8枚举中R连续、G/B行内常量的性质，减少准备阶段轴表读取。它不改变四面体、Q16舍入、逐级RGB8、节点或现有热映射；普通模型高workload hint才启用direct，低hint保持旧路径。固定模型的完整RGB8和真实百图质量已通过。

100的N100新句柄至首批真实分离输出连续wall，相对97在ordinary/a399两模型的中位时间分别下降8.4093%/22.1809%，对应配对A/A有效。不能把这两个作业收益写成热像素提速，或推广到所有模型和批次；全场126统计项仅49项A/A有效，全情形50%没有被证明。详见 [100阶段报告](2026-10-24-p16-scanline-prepare.md)。373a同87核速度验收见 [三模型同场报告](2026-10-24-p16-arrival-model-triple.md)，其资格不能未经测试直接转授新组合。

修订101将缓存索引代数提前展开；其完整质量结果已实际通过，旧阶段文档仍保留“仅有限阶段”的历史边界，本汇总补充最新状态：

- 原件：`F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-early-index-quality-v1/{results.json,independent.json,calls.jsonl}`。
- `results.json`及独立审计均为 `passed=true`；结果SHA256为 `9df2158b4666ace754f6b26bb8f784e1ded818ff84de986986903363d8552928`。
- 覆盖24条分块完整RGB流、12条真整幅流、24条百图流和2400逐图比较；21个父子表对、2442合法映射、66非法映射、24个团队快照通过。
- 本次核对时上述完整质量成果尚未进入speed分支提交/封存；没有101性能结果。101实际静态栈768B，100为704B，原缩帧预期没有实现。

因此统一配置先吸收100，101继续作为通过质量但待测速度的候选；不以索引表达式更短或有限合同通过代替批次时间。

## 宽表与内存研究的取舍

max41的包络缓存有264,222槽，旧1MiB预算只允许262,144个uint32，因超2,078槽而关闭快路径。293/294将预算增至2MiB后，重新取得32,768可达cell的完整domain证明。新成本包含真实缓存和直接表，不只是上限差的8,312B：

| 表示 | max41 Model容量 | 主要热数据 |
| --- | ---: | --- |
| 293 | 35,673,508B | 32MiB uint16索引、613色palette及guard |
| 294 | 52,448,272B | 48MiB RGB24直接输出及guard |

293的主U策略48/48热百图A/A有效并通过60档，但N1与N100冷wall均仍有A/A缺口，所以完整冷热50%尚未证明。294辅助P策略还出现一个有效低50反例。宽表是解锁精度候选的实现条件，不代表已经确定最佳布局。详见 [宽表质量](2026-10-24-p16-direct-cache2.md)及 [正式性能](2026-10-24-p16-direct-cache2-performance-v2.md)。

内存方向的P4显式页ID ROM为12,633,164B、精度100%保留，全四模式最劣53.896116%吞吐；线性ROM为16,779,328B。省4,146,164B带来的额外依赖读取不适合本轮充裕内存条件下的默认速度优先策略。3B字典后续已有有效低50反例，不能借早期好场次恢复推荐。保留这些格式作为受限内存部署选项，同时吸收只读借用、避免重复owner、通用C99回退和真实容量账本；不默认叠加P4解码。

100图完整输入为235,929,600B，真分离完整输出另需235,929,600B；原地模式不必再分配完整输出。流式接口可按图或块限制工作集，但测速必须固定同一批次及边界，不能用分块调用代替真实整百图调用的时间。离线拟合Python数组不等于部署运行内存，ROM字节数也不等于进程RSS。内存全表及负例见 [研究索引](2026-10-24-memory-evidence-overview.md)。

## 固定模型路径与SHA256

以下是本机可用原件。sidecar仅首级非空，其余三级为null。本次静态核对实际对这两套四级SLUT和sidecar执行SHA256；后续统一包复制后仍须核同一摘要，不能依赖文件名。

373a默认模型：

| 角色 | 原件路径 | SHA256 |
| --- | --- | --- |
| stage1 | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-arrival-last-budget-v1/candidate/candidate-base.slut` | `73dc15fea4db5fb10a481336e18256cff040ca291a9713dc1c383ad84739b5ad` |
| stage2 | `F:/Hackathon/projects/16-lut-color/artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage2.slut` | `933a4311800dabfafdec534cc149c56aeb7043e5e57df8bef4dd174058b57650` |
| stage3 | `F:/Hackathon/projects/16-lut-color/artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut` | `95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234` |
| stage4 | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-arrival-last-budget-v1/candidate/stage4.slut` | `5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386` |
| 首级sidecar | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-arrival-last-budget-v1/candidate/channel-frac.bin` | `85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff` |

对应独立oracle为 `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-arrival-budget-accept-v1/candidate.rgb`，既有认证SHA256 `373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed`。oracle是验证数据，不由运行时读取。

max41精度选项：

| 角色 | 原件路径 | SHA256 |
| --- | --- | --- |
| stage1 | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-current-feasible-cpsat-accept-v1/candidate/candidate-base.slut` | `07c9f25252132bb8509a183d97cc59457da5fcdbbe7d0d58618bd74e797b7c95` |
| stage2 | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-current-feasible-cpsat-accept-v1/candidate/stage2.slut` | `904e30a1c0f805175b0b9518949e4e96c9ff2a7e7980978ed8e90fd1282bd924` |
| stage3 | `F:/Hackathon/projects/16-lut-color/artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut` | `95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234` |
| stage4 | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-current-feasible-cpsat-accept-v1/candidate/stage4.slut` | `5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386` |
| 首级sidecar | `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-current-feasible-cpsat-accept-v1/candidate/channel-frac.bin` | `85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff` |

对应独立oracle为 `F:/Hackathon/worktrees/p16-tail-20261023/artifacts/cinema-current-full-quality-v2/candidate.rgb`，既有认证SHA256 `728666cbc05f0cd2d9da112ce41a26117d67baee1511760d83df8f8cefe8ed98`。两套模型路径与oracle来自旧 `p16-direct-cache2-quality-frozen-v1/frozen.json` 的 `models.old_best` / `models.max41`，没有从相似目录猜测。

## 合并边界与AVX-512实施要求

三研究分支共同基线为 `16ae431030a5c734a1485089c8b58d15b21902f6`。静态路径交集仅 `.gitattributes`、三方向协作文档及其README/remote.zip；大部分实现位于独立experiments目录，Git合并并不自动形成一个已验证运行时。统一工作树已保留三方向历史，新的wrapper应显式连接100准备器、293宽表和可选AVX-512入口；原研究原件不回写为新组合证据。

AVX-512需保持独立编译单元和完整运行时能力检查，避免基础路径泄漏新指令。Xeon Gold 6140目标尚未实测，本机Ryzen历史结果不能预测其AVX-512吞吐、降频或gather收益。新增核至少要用固定373a、max41及通用混合m模型验证精确等价，覆盖原地/真分离、非对齐、尾部和不可用后端回退；这些属于本轮实施验证，本文没有声称已经执行。

官方Threshold数值、分输出sidecar和派生direct表的最终格式许可仍未在已有证据中解决。用户本次说明明确了固定参数、均值、CPU和内存方向，但没有把历史模型转成官方测试集验收。统一版本应保留这些已知边界，不用本地百分档或max阈值替代官方判分。

## 本文静态核对记录

执行环境为本机Windows PowerShell、Git及 `Get-FileHash -Algorithm SHA256`；不适用编译模式、映射线程数和启用ISA。核对对象包括三分支修改路径交集、上述已有JSON角色/计数/结果SHA、两套四级SLUT和sidecar实际字节摘要，以及文档内相对引用。没有执行拟合、native像素、性能、RSS采样、源归档或目标Intel测试。最终组合是否成功以统一实现的新增验证回执为准。
