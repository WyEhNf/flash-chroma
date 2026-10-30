# 历史精度策略向当前赛事框架迁移审计

Agent：Codex `/root/framework_contract`；Operator：本会话用户；日期：2026-10-30，Asia/Shanghai。已读取只读 `AGENTS.md`。本次只读取阶段报告和实际源码，未编译、拟合、执行数值/像素/性能测试；只新增本文。历史数字是对应报告的既有结果，不是本次重测。

## 结论

**当前框架没有应用历史全部有价值的精度策略。** 已迁入的是两种固定网格采样、完整色域单级LS、固定前三层的末层链目标LS、RGB8节点整数二次目标精化、最终完整域mean/SSE回退，以及每级不同m的执行能力。它们是可用的通用起点，但不能等同于历史精度研究的完整工具集。

最明确的遗漏是：**LUT驱动的非均匀轴、直接优化真实Q16/RGB8终点距离的节点搜索、前/中层的整链离散优化、分输出坐标sidecar、p99/max/CVaR与固定锚点保护**。混合m接口已接入，但没有把历史组合搜索变成框架的自动LUT-only选择器。逐级tri/tetra matched仍是未完成工程化的研究方向，不能称作已经验证、只差打开开关的生产功能。

“未接入”不等于“无条件应全部开启”：历史不少成功模型使用原60张照片频数、固定Cinema前后缀或局部约束；有的候选未通过升级门禁，有的只改善连续SSE却使最终RGB均值变差。**这些机制可以改造成只依赖原LUT的候选，但旧模型、旧照片权重、旧收益百分比不能直接转授给当前四张3DL。**

## 当前真正执行的入口

| 层次 | 实际代码与行为 | 当前使用边界 |
|---|---|---|
| 框架安装与运行 | `scripts/install_framework.py:79–93,152,161–171`仅接受`uniform/framework`及`sample/independent_ls/chain_ls`；可传一个m或四级m数组 | 参数确实进入拟合；没有curvature、DP、sidecar拟合、matched或离散尾部搜索选项 |
| benchmark | `framework/benchmark.cpp:67,199–208,250`同样只走三种fit；记录固定CG160、残差1e-8、正则1e-5、整数8扫 | 历史Python方法名没有接到此入口；benchmark结果不代表其他方法已执行 |
| 网格/模型构造 | `framework/flash_chroma_adapter.hpp:25,59–123`，`prepare_stage`仅构造FrameworkStep/UniformRounded，采样得到真实m³节点 | FrameworkStep33与UniformRounded33是两个不同模型；两者都不是内容自适应网格 |
| 独立LS | `framework/fit_experiment.hpp:129–151,233–299`枚举原表全部256³输入，Q16基函数正规方程、正则CG、节点舍入及整数坐标下降；最后以真实整数输出mean/SSE回退 | “完整域”覆盖正确；优化中的二次目标仍是未舍入插值，不是最终RGB欧氏均值 |
| 链LS | `framework/fit_chain_experiment.hpp:29–125`固定前三层，枚举全部原始RGB，计算实际稀疏前缀和原四级gold，仅拟合末层；改节点后清除旧结构资格 | 已部分迁入终点补偿思想，但不是四级联合或前/中层离散优化 |
| 结构捷径 | `framework/flash_chroma_adapter.hpp:65–84,167–192`完整证明每个输出c仅依赖输入c，只有四级均证明后才组成精确曲线链 | 这里768B曲线sidecar与历史9216B分输出Q16坐标sidecar不是同一种数据 |
| 通用运行库 | `include/flash_chroma.hpp:46–48,249,410`支持每级m及可选9216B分输出fraction；`ModelBundle`有`sidecars[4]` | 底层能力存在，但当前adapter以空sidecar初始化模型，未给`bundle.sidecars`赋值（adapter:169–170），因此框架没有使用这项历史精度能力 |

Python研究能力必须另列：`python/lutlab/cli.py:16–18,22–46,114–145`提供更多方法和`uniform/curvature/error/dp`；`scripts/p16_frontier.py:22–23,284–326`实际支持四级m、curvature的alpha/exponent和部分拟合器，但它读取规范化RGB8 `.lut256`，不是新框架原序uint16文本。不能把它存在于仓库解释成`main_flash_chroma.exe`已调用。桥接时还须保留当前原3DL的轴序、通道倒序、整数除16再uint8转换，不能直接把文本或u16缓存送入旧RGB8接口。

## 逐项迁移账本

### 1. 曲率、DP及其他非均匀轴：缺失，优先级高

- **历史依据**：[R18非均匀轴和分层采样](../../docs/r18-algorithm.md)已有不读取图片的DP轴方法；六组固定探针mean改善，两个后续原生全域验收也改善mean，但clip-7/m17的完整域max从29升到34。[2026-10-18联合网格](../../docs/stages/2026-10-18-joint-grid.md)在Velvia取得完整域mean约4.07%、百图mean约10.39%改善，但使用照片混合目标，且逐图有退化，迁移到Lomo未入围。
- **真实接口**：`python/lutlab/fit.py:893 adaptive_dp_grid`，`:964 adaptive_grid`，`:988 adaptive_error_grid`；`cascade.py:22–32 _grid_for`和`cli.py:19,35–41`可实际选择；`p16_frontier.py:308–312`也实际调用curvature/DP。
- **当前缺口**：adapter `prepare_stage`没有接收三条自定义轴，`Grid`只有两项；fit头虽然能读取序列化坐标，但入口先固定了轴。历史运行库的非均匀轴合同不等于框架已生成非均匀模型。
- **可迁移内容**：先按完整LUT曲率或轴弦SSE生成固定m的轴，再用当前全域LS/链目标评估。仅改轴和节点即可沿用Q16恢复器。DP只对轴向代理最优，不保证最终四级最优；必须同时保留现有网格候选和真实链路门控。联合网格的旧照片损失不可照搬。

### 2. 分输出sidecar与单调坐标校准：底层支持，框架未接

- **历史依据**：[2026-10-19轴校准](../../docs/stages/2026-10-19-axis-calibration.md)的Cinema完整域mean约1.097405→1.016505、百图mean约0.900428→0.850501；[分输出坐标完整验收](../../docs/stages/2026-10-19-velvia-channel-coordinates-accept.md)的Velvia完整域mean下降5.84%、百图mean下降4.47%，但3图mean变差。前者是共用三轴校准，后者是每输出独立三轴，不能混写。
- **真实接口**：`axis_calibration.py:115 propose`保留节点/idx并调整共同frac；`channel_coordinates.py:12 ChannelLut,131 propose`调整3×3×256 frac；`separable_calibration.py:158 exact_monotone`对已证明的单轴输出求精确可行坐标；`fit.py:1065 fit_model`的`ls_tetra_calibrated`已接公共Python方法，对不可分离源明确回退。
- **当前缺口**：adapter没有9216B fraction侧表存储、传递和fit几何；`fit_detail::Coordinates`也只读取共用三轴分数。不能把`Stage.curves`及`sidecar_bytes()`的768B统计当成已迁入分输出坐标。
- **适用限制**：一般分输出校准机制可从LUT-only目标重新构造，但上述成功模型包含历史照片质量；旧sidecar不能套新表。精确`exact_monotone`必须先证明完整源结构和节点张量，不可用抽样证明。当前adapter只识别对角依赖；Python`curve.separable_channels`还支持输出轴置换/共享输入轴，结构范围更广。额外坐标表示的赛事许可应单独披露，不能因hpp接受就推断题方认可。

### 3. 每级mixed m与matched插值：前者部分接入，后者未工程化

- **历史依据**：[R47混合容量](../../docs/r47-mixed-capacity.md)对18个已证明可分离训练源完成1458个组合的精确解析评价，9源降低最优mean，部分同时省节点；9留出源未验。[2026-10-27选择汇总](../../docs/stages/2026-10-27-p16-score-selection.md)第51–75行明确pipeline的六个链/尺寸设置中matched相对uniform tetra为4好2平，但相对uniform tri存在退化，旧24个模型未在本机齐备，也没有逐级kind数组的统一C++恢复器。
- **真实接口**：`stage_bundle.py:75 assemble`按四个父模型各自级位组装；`p16_frontier.py:284 fit_candidate`支持四级m；`study_chains.py:20 map_chain`是研究执行入口。当前框架m1..m4和混合尺寸执行已存在，不能标成完全遗漏。
- **当前缺口**：没有自动的LUT-only混合m/网格/方法组合选择；当前恢复器统一Q16 tetra，没有逐级tri/tetra元数据及匹配拟合后端。
- **适用限制**：R47的三条曲线卷积证明不能用于一般耦合3D表。matched需同时绑定节点拟合basis、逐级恢复器和整数边界，不能只把tetra节点切换成tri。旧pipeline按照片抽样选择单级模型，不能照搬为新框架的压缩选择器。将mixed m列为“已有执行能力、缺少内容驱动选型”，matched列为“候选研究、尚非可直接开启的已验生产优化”。

### 4. 逐级真实整数优化：只迁入二次目标版本，真实Q16距离搜索缺失

- **历史依据**：[2026-10-16误差归因](../../docs/stages/2026-10-16-error-causes.md)证明陡变、节点裁剪和级间传播的重要性；热点整数改动在完整域有效，但三个真实案例至少一项照片指标退化。[R18](../../docs/r18-algorithm.md)的真实Q16 guard已有数学合同，但六组`dp_guarded`四级探针mean反而略差于`dp_jitter`；[2026-10-18真实RGB8精化](../../docs/stages/2026-10-18-rounded-grid.md)亦保留照片max退化和未入围结果。
- **真实接口**：`fit.py:330 q16_refine`、`:755 q16_refine_guarded`、`:472 fit_q16_tetra`与`:878 fit_guarded_tetra`；公共CLI的`ls_tetra_q16/ls_tetra_guarded`可调用。研究`rounded_grid.py`、`channel_joint_nodes.py`还支持真实欧氏距离与RGB联合方向。
- **当前缺口**：`fit_experiment.hpp:265–276`和`fit_chain_experiment.hpp:72–81`的8轮integer_sweeps是对正规方程的整数坐标下降；节点虽为uint8，但它没有逐候选重算`round(Q16)`输出跳变或RGB欧氏距离。最终mean/SSE评估能拒绝坏候选，却不能指导搜索跨越整数台阶。
- **可迁移内容**：在当前全域LS之后，增加预算固定、只看LUT的真实Q16后优化候选，保留原模型回退。不能把“历史有真整数优化”简化为当前只需增加CG或扫数。历史证据并不支持无条件开启guard版本。

### 5. 全链终点优化、前/中层联合支撑：末层LS已接，离散整链优化缺失

- **历史依据**：[2026-10-24末级联合优化](../../docs/stages/2026-10-24-cinema-last-stage.md)保留真实前缀到达与原四级gold，完整域mean0.909378→0.847552；[到达预算交换](../../docs/stages/2026-10-24-cinema-arrival-budget.md)进一步到0.822503；[第二级完整支撑](../../docs/stages/2026-10-24-cinema-second-nodes.md)突破固定前缀信息碰撞后到0.799074，产生max_first。后者说明只拟合末层可能受前缀碰撞限制，不能靠增末层预算解决所有错误。
- **真实接口**：`cascade.py:71 fit_cascade_residual`已有末层实际到达→整链gold的LS思路；`channel_arrival_nodes.py:8 gains,67 measure`、`channel_arrival_budget_nodes.py:7 select`、`channel_first_joint.py:33 choose`支持真实后缀、RGB联合方向及预算。`scripts/run_cinema_second_nodes.py:64–96`按(到达RGB,gold)合并全部输入，保留均匀频数与另列训练质量。
- **当前状态**：`fit_chain_last`确实迁入了完整域终点目标和实际到达分布，不能说整链补偿完全没用；但前三层固定，末层只做LS/二次整数扫，没有全链真实整数搜索、前/中层节点调节、支撑增量回放或已获预算交换。
- **适用限制**：历史脚本硬绑定Cinema原表/模型，并读取`photo-arrival-frequency.npy`（`run_cinema_last_stage.py:36–38`、`run_cinema_second_nodes.py:33–42`）；不能直接当通用新LUT入口。可迁移的是只保留完整RGB域整数频数的联合支撑和后缀重放机制，必须删除照片质量分支并重新证明统计等价。861行、230到达值等压缩比仅属于旧Cinema，不能许诺新表同样小。

### 6. 终点误差校准与“频率迁移”：机制部分可迁移，照片频数不可迁移

- **历史依据**：[2026-10-19频数归因](../../docs/stages/2026-10-19-channel-frequency-transfer.md)不是新的拟合算法。RGB(16,16,16)在一张图占80.167%，一次小码值取舍放大为主要退化；它证明均匀域/训练频率与单图分布不同，不证明通过频率迁移获得泛化保证。[2026-10-19当前精度汇总](../../docs/stages/2026-10-19-precision-latest.md)强调固定锚点、前级1LSB后缀放大和逐图代价。
- **真实接口**：`suffix_objective.py:36 SuffixObjective`、`axis_calibration.py:41 _cost,115 propose`把本级原表忠实度与后缀保持损失结合；这些底层函数接收mass，本身不保证其来源只含LUT。
- **当前状态**：chain_ls已使用终点gold；没有对前级实施本级+后缀双loss、有效坐标校准、固定逐色cap。`frequency-transfer`诊断不应列为“已验证算法忘了接”。
- **合法分界**：从完整256³输入经过LUT前缀推得的到达次数只依赖LUT，可以作为新LUT的固定离线测度；来自训练/测试/补充照片的频数与逐图权重都利用了图片信息。不能以“只使用历史60图、没读取本次100图”为理由宣称符合新框架。

### 7. 尾部保护、固定锚点与CVaR：有最终双门控，但遗漏更细保护

- **历史依据**：[2026-10-17完整域保护](../../docs/stages/2026-10-17-full-domain-guard.md)以完整直方图、Q24根号上下界和固定参照证明mean预算，同时保护RMS/p99/max；联合节点可利用别处的均值改善修复热点。[2026-10-17 CVaR提交门禁](../../docs/stages/2026-10-17-cvar-commit.md)明确mean/RMS/p99/max不退仍可能让最差1%均值升高，并修复相同尾部频数的等号接受。
- **真实接口**：`full_domain_guard.py:17 root_bounds,24 summary,51 certify,134 DomainGuard`；`cvar_guard.py:8 tail_summary,34 CvarGuard`；不是当前framework fit的调用依赖。
- **当前缺口**：两fit头仅接受`candidate.sse<=baseline.sse && candidate.mean<=baseline.mean`；虽统计max_squared，但未作为拒绝条件，没有误差直方图、p99/CVaR或逐色cap，也没有固定跨多步骤锚点预算的通用接口。当前whole-domain guard不能表述为尾部全面不退。
- **可迁移内容**：对原LUT完整域计算直方图、固定参照、可选max/p99/CVaR约束与整数证书，不依赖照片，且不增加像素运行路径的计算。均值是当前主指标，额外硬约束会缩小可行集合；应作为明确的质量档/保护策略，不必把全部历史硬约束无条件设为默认。Q24证书保证给定直方图代数，仍须绑定真实输出。

### 8. minimax、CVaR目标与有限箱精确搜索：有研究价值，不能称通用最优器

- **历史依据**：[2026-10-17联合minimax](../../docs/stages/2026-10-17-joint-minimax.md)在冻结四节点±4箱内优化`(max²,历史缺口,SSE,L1)`，全域max52→51，证明只限该箱；[2026-10-26汇总](../../docs/stages/2026-10-26-p16-unified-research.md)指出max41比373a更低max，但有逐图退化且CVaR上升，max_first的平均值更低。
- **真实接口**：`joint_minimax.py:7 lower_objective,18 objective,22 solve`直接引用`state.photos`、历史组频数；`fit.py:246 fit_irls_tetra,269 fit_tail_tetra`为通用RGB域近似Lp/尾部加权候选，公共CLI已暴露，但当前框架未接。
- **当前缺口与限制**：没有minimax/CVaR选型、IRLS或tail候选；有限箱搜索的机制可以只按原LUT目标重构，但原历史缺口/照片约束不能保留。不是必须立即搬运的已验证全局最优方案，不能以max更低自动替代mean更优模型。

### 9. 连续箱约束、更多CG预算：已有实现，但不是优先遗漏收益

- **历史依据**：[R25](../../docs/r25-full-domain-fitting.md)的完整域H/b及15邻接结构已被当前C++ LS明显吸收；[R26](../../docs/r26-box-constrained-fitting.md)38个阶段中28个改善未舍入整数二次目标，但最终四级mean仅4组下降、9组上升，max没有下降、1组上升，未新增示例通过场景。[2026-10-19全局节点提议](../../docs/stages/2026-10-19-channel-global-nodes.md)连续代理下降而真实RGB8目标退化，未入围。
- **真实接口**：`fit.py:694 fit_full_tetra,706 fit_full_box_tetra`与`box.py`；CLI支持`ls_tetra_full_box --grid dp`。当前fit头用正则CG+clip/round+整数坐标下降，不是带KKT检查的箱约束QP。
- **结论**：箱约束功能确实没迁，但历史不支持把它标为遗漏的必然精度增益；比起增加连续求解预算，应优先评估非均匀表示与真实整数终点目标。

## 不能迁移的成品与不能沿用的收益

1. **373a、max_first、max41/max48是固定Cinema模型。** [2026-10-27评分交付](../../docs/stages/2026-10-27-p16-score-candidate.md)明确两档为固定回归示例，不适用于另一套LUT；[选择汇总](../../docs/stages/2026-10-27-p16-score-selection.md)给出源模型/sidecar/oracle身份及matched研究边界。把模型包存在于`data/`当作新框架已经使用，会误报。当前框架按传入四表重新prepare/fit，未装载这些固定资产，这一点是正确的。
2. **不能沿用照片目标。** 新框架Readme第64–65行明确压缩不利用图片信息；第52–53行允许四级m不同，第56–57行预处理不计时，第36–37行禁止多线程和GPU/NPU。历史不少Python拟合默认Numba/OpenMP四线程，即使移到预处理阶段也不能假定自动豁免；当前单线程约束应保留。
3. **不能把“只重标fixed模型”当迁移。** 新表需按本框架的原始uint16/轴/通道/截断规则产生参考。历史Hald/TIFF烘焙来源、旧均匀RGB8表和当前3DL不是同一输入身份。
4. **参数选择的保守边界**：只依赖LUT的固定拟合与选择规则可迁移；冻结后用照片报告收益/退化不等于把照片频数喂给压缩。本文只核当前自动fit在读图前完成，不替人工选择参数推定额外官方许可。旧基于照片的冠军选择和权重不能自动继承。

## 建议的有限整合顺序

| 顺序 | 候选整合 | 为什么优先/为何保留限制 |
|---|---|---|
| 1 | 桥接curvature/DP三轴到adapter，沿用当前全域LS和固定m/chain入口 | 不必改Q16像素恢复器，有LUT-only旧接口和既有证据；保留现有网格作为对照，不宣称更大m或非均匀必然更准 |
| 2 | 加真实Q16整数终点后优化及完整误差直方图/固定锚点回退 | 直接补当前“连续SSE目标与最终RGB距离不同”的缺口；先只依赖全RGB域，不搬照片mass |
| 3 | 从末层扩到前/中层的联合支撑和精确后缀重放 | 历史已显示固定前缀碰撞会限制末层；不预设新表具有旧Cinema的高压缩比 |
| 4 | 明确表示许可后，接分输出sidecar与坐标校准；补每级mixed m的LUT-only选型 | hpp已有表示/混合容量能力，缺的是框架模型生成、元数据和来源/执行绑定 |
| 5 | 将matched、箱约束、IRLS/minimax/CVaR目标作为显式研究候选 | 当前证据有负例或部署缺口，不能为了“所有策略都用上”叠加进默认 |

这些是静态审计确认的工程缺口及候选优先级，不是新增的精度收益或性能资格。当前三种fit不是全历史最优集合，但已用部分关键思想；正确说法是“完成一条可靠通用基线，尚未迁入若干已验证机制”，不是“历史策略全部已应用”，也不是“把旧冠军文件复制过来就能提高当前成绩”。
