# 精度与后端优化的统一 PR 交付说明

Agent：Codex；Operator：WyEhNf；Task：将当前已完成成果组织为一次PR；Status：Completed（限定范围实现与实验已完成，提交团队审查，尚未合并）。

本次将原有25个中文提交整体提交到`main`，保留实验顺序、原始模型和失败证据，不改写历史。交付分支为`codex/joint-grid-precision-20261018`；操作前fetch确认`main`仍为`da5ed25b4fb42d95417630d657c47bc6e162e031`，已经是本分支祖先，无需额外合并。GUI的PR #40、研究建议PR #39和协作者诊断PR #41保持独立。

## 本次具体完成了什么

可分离来源方面，新增`separable_calibration.py`的精确单调Q16坐标求解及显式方法`ls_tetra_calibrated`。完整验证源与节点结构后才校准；不可行时明确回退原结构DP，非可分离时回退通用补支撑。缓存身份包含新方法的源码及参数，原默认不变。Filmic06、Emerald的RGB8 17³模型在完整256³色域和100张照片上误差均为0，这不是任意三维LUT的保证。

一般三维来源方面，研究网格与整数节点联合优化、按输出通道分配坐标，以及四级RGB8舍入后的后缀放大。接受Velvia分输出坐标模型和Cinema当前锚点四级模型；同时保存不达门槛的节点、坐标、连续代理及读取复用实验。整数oracle、原生标量和AVX2按同一模型分别验证，模型误差与运行时差异分开报告。

| 对象与比较基准 | 完整色域mean | 完整色域p99 | 100图mean |
| --- | ---: | ---: | ---: |
| Velvia新模型，对冻结2dd模型 | 0.886672865，降低5.84% | 6.324555320，降低9.65% | 0.884971215，降低4.47% |
| Cinema当前锚点，对已验收af974链 | 0.981110597，降低3.48% | 3.741657387，降低9.25% | 0.810320559，降低4.72% |

这些降幅不是统一相对PR #41的百分比。所有距离是逐像素RGB欧氏距离，不是CIEDE2000；mean、RMS、p99、max和CVaR的完整数值与逐图退化见[最新结果](2026-10-19-precision-latest.md)。Cinema的100图mean全部改善，但仍有1图RMS、1图max、3图CVaR退化；Velvia有3图mean及审计组RMS退化，未隐藏这些代价。

后端方面，新增独立的固定四级AVX2专门化：首级使用分输出坐标、后三阶段共享坐标，运行前分派，保留其他布局的回退。相同a399模型与相同数据下，单线程apply耗时下降10.70%，请求4线程下降7.76%，容量不变。该库通过独立builder和C ABI运行，未替换公共CMake或原v3库。新模型实际多9216字节侧表；此前v3新表示相对普通af974模型慢约46%，该成本比较与后续同模型后端比较属于不同阶段，不拼接成最终新库对旧模型的速度比。

## 验证目的、环境与证据

数值阶段环境为Windows11 26200 x64、Ryzen9 8945HX、32GB；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0，Numba4线程、BLAS/MKL/OMP环境1。原生GCC15.2 Release `-O3 -DNDEBUG`、AVX2/OpenMP，显式标量1及AVX2请求4线程。目的分别为拟合精度、同模型整数正确性、四级误差传播和同机性能；各自的输入/模型/源码/DLL哈希、复现命令和原始回执保留在对应档案中。

- [Filmic06直接单调校准](2026-10-19-filmic-direct-monotone.md)、[Emerald完整验收](2026-10-19-emerald-calibrated.md)：严格可分离17³完整色域/百图验零及原生对照。
- [Velvia完整验收](2026-10-19-velvia-channel-coordinates-accept.md)：冻结候选的完整256³、100图、独立整数oracle及原生单级/控制链对照。
- [Cinema完整验收与成本](2026-10-19-cinema-current-anchor-accept.md)：四张原始完整LUT逐级RGB8参考、四级稀疏oracle、完整域和100图标量/AVX2逐字节一致。
- [AVX2专门化](2026-10-19-channel-runtime-specialized.md)：44项有限合成合同，以及实际模型单级/四级完整域与百图等价；四个串行新进程AB/BA/BA/AB、每配置5次完整100图，apply和copy+apply分列。未锁频、控温或绑核，结果是本机批次摊销，不是单图尾延迟或跨机器保证。
- [单色反例解释](2026-10-19-cinema-cap-anchor-diagnosis.md)：首级B增加1导致最终平方误差27变57，定位旧训练上限未保护当前基线；后续统一收紧191个颜色约束，未逐热点追补。

本次发布只追加文档和静态核对，不新增拟合、像素映射、单元测试或性能实验。静态环境仍为上述Windows/Python，使用Python标准库与Git；编译器、数值后端、线程和计时不适用。核对目的为档案清单与Git blob的原字节一致、文档本地链接有效及差异格式，无权替代数值或全仓CI。

复现静态交付检查（输出目录须为新目录）：

```text
artifacts/error-study-py312/Scripts/python.exe scripts/audit_precision_delivery.py --output artifacts/pr-delivery-20261019/archive-check-v1
git diff --check github/main...HEAD
git diff --cached --check
```

静态回执见[交付检查](../../report/data/precision-pr-delivery-v1/static-check.json)，协作查询与包含关系见[远端核对](../../report/data/precision-pr-delivery-v1/remote-check.json)。此次不宣称重新通过全仓门禁，PR的CI以提交后的实际运行状态为准。

## 相关意见的处理状态

GitHub连接器本轮传输失败，改用GitHub REST/GraphQL完成读取。检索全部35个现有PR、2个独立issue和2个Discussion，逐页获取35个PR的完整会话评论、提交review及行内意见，共107组REST记录；重点核对#3/#6/#9/#12/#16/#19/#22/#32/#34/#37/#38/#39/#40/#41的GraphQL审查线程，均无未读分页或现有线程。读取Discussion #4全文及评论（0条），并在创建前刷新远端记录；不将接口失败等同于没有意见。

| 原始记录 | 当前处理与证据 | 本次操作边界 |
| --- | --- | --- |
| [PR #9两项P2](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[issue #7内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7) | 修复`337a3dd`实际为HEAD祖先；历史正负回归与集成结果见[PR #37最终验收](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676) | 不改写历史计时、不自动关闭issue；本轮源码没有修改这些修复文件 |
| [PR #27尾部保护](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)、[PR #29](https://github.com/WyEhNf/flash-chroma/pull/29) | `876e15b8`和`397cc367`均为HEAD祖先；后续研究保存自己的门槛、拒绝与逐图代价 | 不把聚合改善说成每图每项均不退化 |
| [PR #34整体审计](https://github.com/WyEhNf/flash-chroma/pull/34#issuecomment-6229807001) | 117项/CTest和原模型全域复测属于协作者旧提交与其WSL2环境 | 不重标为本次Windows新验收或当前模型性能 |
| [PR #41误差诊断](https://github.com/WyEhNf/flash-chroma/pull/41)、[PR #39后续建议](https://github.com/WyEhNf/flash-chroma/pull/39) | 推进准确位置、整数输出、少量反例与四级传播，并在候选冻结后同机计时 | 未自动合并两个独立PR；不跨Intel/AMD环境换算加速比 |
| [Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)、[PR #5素材建议](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072) | 明确区分整数运行时错误和表示能力，保留来源与哈希；Cinema仅证明四张创意LUT的数值串联 | 未证明色彩域兼容，不称真实ISP；未执行全面压力扫描 |
| [issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)、[GUI PR #40](https://github.com/WyEhNf/flash-chroma/pull/40) | 接口迁移、资源预算、实板及GUI独立审查仍待办 | 新表示未接公共CLI/GUI/C99；不代替这些任务的验收 |

## 主要提交与尚未完成事项

`92f49c9`及`9be1bcb`落地可分离精确校准；`bf8b03c`落地分输出坐标及原生验证；`f59a1d0`解释旧锚点反例，`d790492`统一收紧当前锚点约束，`1330961`完成新候选四级完整验收与成本；`26e6ac3`完成后端专门化和同模型性能比较，`4c7a406`汇总结果并静态核验档案。其余阶段提交完整保留，未入围候选与慢于基线的读取复用均能追溯。

待办：新素材或官方数据上的冻结模型验证、官方Threshold及格式许可、分输出坐标正式格式/公共入口/端侧支持、最终后端对旧普通模型的同轮净成本比较。已有100图为已见数据，不称盲测；没有官方评分、SOTA胜出、CUDA或实板新成绩。AGENTS.md、默认模型与冠军不修改，本次只提出一个PR，不执行合并。
