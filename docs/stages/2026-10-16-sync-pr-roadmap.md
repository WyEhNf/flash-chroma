# 阶段说明：同步最新主干与后续工作建议

日期：2026-10-16。本阶段完成仓库整合、一次集成正确性门禁和后续规划；下列新实验与架构调整均为建议，尚未开始实施或全面扫描。

## 1. 本阶段实际完成的工作

- 获取 GitHub 远端 `https://github.com/WyEhNf/flash-chroma.git`，先整合 `3c743faa25c9a349900970ef29ad2f829f36e4d5`，最后刷新再同步到 `github/main` 的 `dec102056ce999ac08180230ddb5b32f31a55f99`，使用工作分支 `codex/sync-pr-roadmap`。不改写历史，不直接推送 main。
- 保留原分支的三笔未进主干成果：`f72be5c`（R28–R51 研究检查点）、`b89b88f`（上次主干整合）、`3a79f5a`（压力数据与统一数据入口）。因此本分支相对 main 的累计差异包含这些历史成果，不能把整份 PR 描述成单纯文档修改。
- 整合 `.gitattributes`、`AGENTS.md`、`CMakeLists.txt`、`README.md` 四处冲突：保留数据集 LF/二进制规则和 PR #9 原始字节保护规则；同时保留 portable 与 embedded 两套 C99 构建选项；保留已有中文提交约定及 PR #10 阶段/测试规范；补齐当前导航。
- 合并前的本地规范修改及阶段说明均已保留。未修改冻结的拟合、插值和研究工作流源码，未改写旧数据集或历史指标。
- 在新的 `build-sync-pr-roadmap` 目录构建并集中执行一次集成门禁，未触碰旧实验使用的二进制。
- 阅读近期 PR、研究报告、CSV 摘要、嵌入式契约及现有数据登记，形成下列分阶段建议。
- 读取相关 PR 的完整评论/审查线程及关联 issue，核对评论中的缺陷是否已实际修复，修订优先级；由已提交 CSV 独立复算确认 PR #9 的 8 行基线选择问题，未重新拟合或测速，未覆盖历史汇总。

主要新增说明为本文件；本轮整合修改为上述四个冲突文件。合并提交以包含本说明的提交为准，历史成果分别见上述三笔提交及其已有报告。本阶段通过工作分支 PR 交付；累计历史差异较大，建议按草稿评审，先审整合内容和证据边界，再分模块审查历史成果。

## 2. 近期 PR 已带来的能力与限制

| PR | 本次核实的状态 | 可以据此推进的工作 | 不能据此得出的结论 |
| --- | --- | --- | --- |
| [#9：现成 LUT 的 22 种配置研究](https://github.com/WyEhNf/flash-chroma/pull/9) | 已合并，主干合并点 `3c743fa` | 已有 68 份 LUT、100 张照片、2740 条抽样记录、188 条完整 100 图候选、188 条单级全色域记录、60 条四级数值链记录 | 22 个配置名称不等于 22 种独立算法；不同入围子集的速度不能直接排名；100 图复核不是独立盲测；未完成原生 C++/CUDA 部署比较 |
| [#6：嵌入式 C99 与三类 QEMU](https://github.com/WyEhNf/flash-chroma/pull/6) | 已合并，主干合并点 `4d716f8`，交付能力仍有 WIP 边界 | Cortex-M3/FreeRTOS、RV32/FreeRTOS、Cortex-A53/Linux 的 C99 集成，以及宿主全色域互操作 | 没有实板吞吐、功耗、DMA/缓存、ISR 或实时截止期证据；AArch64 未验证桌面拟合/Python 环境 |
| [#10：阶段与测试规范](https://github.com/WyEhNf/flash-chroma/pull/10) | 已合并，主干合并点 `3cdb467` | 后续每个阶段保留中文说明、环境/目的/结果，并通过 PR 交付 | 创建 PR 不等于已经审查合并 |
| [#11：操作前检查协作记录](https://github.com/WyEhNf/flash-chroma/pull/11) | 已合并，主干合并点 `dec1020`，仅增加规范文档 | 把审查评论、关联 issue/discussion 与实际修复证据纳入操作前检查 | 已合并或 CI 通过不能消除尚未处理的缺陷 |
| [#5：68 份外部 LUT 素材](https://github.com/WyEhNf/flash-chroma/pull/5) | 已关闭、未单独合并；素材提交 `b9e923f` 已经随 #9 进入 main | 使用固定来源、授权、原始字节和格式元数据建立正式适配层 | 原始 CUBE/TIFF/3DL 不是比赛要求的四张 `256³ RGB8` 完整表；68 份单级素材不能直接计成 68 条合规四级链 |

已通过 GitHub Actions 接口复核历史运行：[#9 正确性工作流](https://github.com/WyEhNf/flash-chroma/actions/runs/38873006945)、[#6 正确性工作流](https://github.com/WyEhNf/flash-chroma/actions/runs/38865748481)、[#6 嵌入式工作流](https://github.com/WyEhNf/flash-chroma/actions/runs/38865748524) 均为 success。它们对应各 PR 当时的源码，不能替代本次整合分支的 CI；也不证明可选研究依赖中的 13 项测试由默认 CI 执行过。

### 操作前协作记录与尚未解决的事项

本轮检索仓库全部 issue（结果为 #7/#8）及近期 PR，读取 #3/#5/#6/#9/#10/#11 的正文、合并时间、完整评论时间线和行内线程，另核对 #6/#9 的 review 提交、#7/#8 的正文及全部评论；对应接口无剩余分页。沿评论引用读取实际源码并检查修复是否进入本地及 main。以下项目没有在本分支修复，也未见已进入 main 的修复提交：

| 原始记录 | 核实与当前处理状态 | 修复提交/验证 |
| --- | --- | --- |
| [#9 审查评论：基线选择](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540) | `report_local_lut_study.py` 仍只取首个 `sample_tetra`，没有限定 m33；独立关联完整表确认 8/68 行基线及派生降幅错误，全部 68 行的降幅中位数修正前后均约 43.417444% | 未修复；本轮只有 CSV 复算，不能把评论中的修正代码当作已落地补丁 |
| [同一评论：环境身份与续跑](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540) | `compatibility.environment()` 的身份仍未包含实际 CPU/系统/依赖环境，恢复入口先写 `run.json` 再复用结果；风险仍存在 | 未修复；未重跑风险探针，也没有证据认定历史实验已经混用环境 |
| [Issue #7：账本执行内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7) | issue 打开，native cube screen 分支仍缺少实际 kernel 与登记 kernel 的一致性核对；本轮现有 28 项测试通过不能排除此缺口 | 未修复；未宣称已有 4602 条历史观测误登记 |
| [Issue #8：两套 C99 集成协调](https://github.com/WyEhNf/flash-chroma/issues/8#issuecomment-6213698494) | 本轮解决本地构建冲突并通过共同宿主门禁，尚未完成接口选择、目标 ABI 资源测量及 portable 系统级 QEMU 覆盖 | 仅推进集成前置步骤；不关闭 #8，不将 embedded 的 QEMU 结果记作 portable 结果 |
| [#5 素材审阅意见](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072) | 轴序、输入域、源插值、裁剪/舍入、未知摄影域与逐来源授权仍须进入正式适配验收 | 后续 P1；本轮不更改素材或宣称完成摄影域适配 |

[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4) 的原始方案已由用户在本会话完整提供，本规划遵循其“运行时正确性与拟合表达能力分开、固定反例、小规模起步”的要求。网页读取返回 404，不能据此认定无后续讨论；最新回复的检查尚有缺口，创建草稿 PR 时明确披露。没有执行依赖该缺口结论的 GitHub 合并或 issue 关闭，也没有把已知缺陷描述为全部修复。

## 3. 决定优先级的具体证据

1. **先处理误差尾部和语义衔接。** PR #9 的 68 个已复核单级最低 mean 候选中，`ls_tri_tri` 胜出 28 个、`dp_supported` 14 个、`ls_tetra_int` 11 个，其他配置胜出 15 个，没有通用赢家。`Lomochrome Purple 2` 的最低 mean 候选仍有 mean 约 0.8146、照片 max 约 49.1935；`Velvia_Vivid_v2` 的照片 max 为 49、全色域 max 为 54。低均值不足以说明局部误差可接受。
2. **四级任务要单独验收。** 三条数值链各自最低 mean 候选仍出现约 `1.1514 / 1.7591 / 0.6672` 的 mean，对应 max 约 `21.0238 / 9.8489 / 4.5826`。188 条单级全色域记录不能代替四级全色域证据。
3. **原生部署不能直接继承研究内核。** PR #9 的结果依赖 profile 指定的恢复算子；`ls_tri_tri` 的三线性恢复与四面体 Q16 不是同一语义。仅保存相同节点或把 `.slut` 文件交给另一个后端，不保证复现该项精度；`ls_tri_tetra_mismatch` 本来就是失配对照。
4. **统一数据入口还缺真实 LUT 层。** `problem16-unified-v1` 登记 274 个 case、273 条不同有序源链、455 份不同图片 RGB 内容；PR #9 的 68 份外部 LUT 尚未接入该登记。62 个新增压力 case 仍是 `unmeasured`，有限探针回放不等于拟合质量通过。
5. **先修调度证据，再考虑恢复大矩阵。** 现有矩阵冻结在 4471/7917 次已尝试，其中 4465 条有效观测、6 次拟合失败，控制器状态为 `stopped_error`。需区分 worker 完成、结果入账和 controller 收尾，确认是否存在完成判定竞态及陈旧状态，不能直接将未完成条目改为成功或重跑全部矩阵。

依据：[PR #9 报告](../../artifacts/local-lut-study/20261016/report.md)、[最低 mean 候选](../../artifacts/local-lut-study/20261016/summary/best-per-lut.csv)、[四级结果](../../artifacts/local-lut-study/20261016/summary/chains.csv)、[统一数据说明](../../datasets/problem16-unified-v1/README.md)、[停止检查点](../../datasets/problem16-v1/matrix-checkpoint.json)。上述误差均为 RGB 码值欧氏距离，名称采用 `rgb_l2_code_value`，不是 CIEDE2000。

## 4. 建议的后续 PR 与验收顺序

### P0：先闭合整合与复现入口

先交付三个小范围修复，分别对应 #9 的基线选择、#9 的恢复环境绑定、#7 的账本执行内核绑定，避免和大矩阵或 C99 接口重构混在一起：

- 报告显式选 `sample_tetra/m33` 并检查唯一性；加入同时含 m17/m33 的最小回归用例，将修正后的 68 行派生表保存为新版本及勘误，保留原始实验。只复算已有汇总，无需重做拟合或测速。
- 恢复时校验 CPU、OS、Python/NumPy/Numba、实际线程/计时配置等相关身份，在任何写入前拒绝不兼容环境；保留原始环境来源。验收“环境变化被拒绝且原 run.json/结果不变”和“相同环境可恢复”。
- 将账本声明的 kernel/backend 绑定到实际执行证据，`auto` 采用解析后的真实内核。验收不一致时无新观测、索引/冠军不变，以及一致时能正常登记；集中执行默认与纯标量门禁。若审计发现旧记录不一致，应隔离并保留原始证据，不能仅改标签。

本轮整合 PR 保持 Draft，先运行默认、标量、Docker 和三类 QEMU 的既有门禁并审查累计历史差异；在相关缺陷修复并验证前不提出可直接合并声明。另用独立的 Python 3.12 研究环境安装 `experiments/local-study-requirements.txt`，有针对性地复验 PR #9 的 13 项正确性测试，记录实际版本与结果；不要覆盖默认 Pixi 锁文件或现有数据构造环境。审查评论已记录他人的独立 13/13 验证，本机不重复冒充该环境的结果。

验收：两套 C99 核心都能构建；原生测试与本次构建产物绑定；13 项研究测试无静默跳过；明确每项属于哪个环境。PR #9 工作流的 12 份冻结源码指纹应保持不变。当前 `io.py` 包含后续来源校验扩展，`curve.py` 原始换行也与历史 run 身份不同；如需重跑，使用新运行身份和新输出目录，不能接着旧实验缓存写入。

### P1：真实 LUT 接入与最小反例归档

在新版本登记中增加外部源命名空间和适配元数据，保留 `unified-v1`；复用 `source_lut.py` 的格式解析能力并冻结解释政策。明确轴序、`DOMAIN_MIN/MAX`、源插值、越界处理、RGB8 裁剪与舍入、逐级顺序、来源授权和输出哈希。先完成单级源适配，再登记有明确四张配方的数值压力链，摄影色彩域兼容性单列。

首批从 `Lomochrome Purple 2`、`Velvia_Vivid_v2`、`Lobster` 的既有热点，以及窄峰、斜阈值、前级压缩后级放大的可解释压力家族中选少量例子。冻结生成器、参数、seed、输入/模型哈希、top-k 坏颜色及 ±1 LSB 邻域；另保存足够小的模型、热点图片和误差摘要，避免反例依赖他人机器的大缓存。

验收：固定模型的标量、AVX2、两套 C99 相对独立整数 oracle 为 **0 字节差异**；拟合误差另记 mean/RMS/p99/max、超限比例及最坏 RGB。对 LUT/颜色扰动同时计算精确参考变化，分开报告实现错误、有限网格表达不足与重新拟合敏感性。不得给任意不连续 LUT 预设必过的小阈值；不在本阶段做全家族/全参数扫描。

### P2：小规模、同样本的算法选型

先冻结共同测试集合、四级配方、两档 m=17/33、输入顺序与模型字节。四面体主线先比较 `sample_tetra`、`ls_tetra_int`、`dp_supported`；`ls_tri_tri` 单列为算子匹配的三线性路线。IRLS/guarded 当前仅有五个来源代表子集，不直接扩大为默认方案。

验收分两步：先在固定小集合检验质量与正确性，发生可解释的收益后，再集中测速。主指标继续分别保存逐图 mean/RMS/p99/max、全色域统计、阈值超限比例、失败数；官方 Threshold 未取得前不宣布官方达标。全色域仅对冻结的少量最终四级候选显式运行，不在常规 CI 扫描。100 张照片作为历史对照；最终验收应先冻结新的来源/参数/seed 留出集，再做选择，不能将这批反复使用的照片改名为盲测。

公平性能比较必须使用相同模型集合、相同硬件、线程、后端、1024×768 RGB8 图像和计时范围；保存预热、原始重复值及波动。映射、I/O、离线拟合冷启动、模型存储、运行时工作内存分别计量。PR #9 的 Numba 四线程结果与历史 C++ 多线程结果不能拼成加速比；不同入围集合的中位 ms 也不能直接排名。三线性路线进入正式运行时前需显式绑定恢复算子并建立其独立正确性口径，不能用四面体 oracle 验收三线性精度。

### P3：部署架构收敛与硬件加速

沿用 [Issue #8](https://github.com/WyEhNf/flash-chroma/issues/8) 继续协调，不另建重复议题。先以共用语义文档和夹具对齐 `portable/` 与 `embedded/`，列清 API 的四级/0..4 级语义、视图与预处理表、所有权、结构化捷径及错误写入保证。用同一组序列化模型和独立 oracle 做互操作，由维护者确定接口分层与兼容策略，再决定共享哪些核心代码；本轮不删除任何一套实现。为选定 portable 路径补齐系统级 QEMU，不能继承 embedded 的覆盖声明；历史研究材料、数据入口与接口/内核按独立可评审阶段拆分。

目标 CPU/板卡明确后，再检查 ISA、编译结果与热点，优先考虑节点访存、查表、布局、块大小和批处理，再决定 AVX2、NEON、RVV 或手写汇编的收益。验收以同模型逐字节一致、固定环境的阶段性能数据为准，不以汇编行数或 QEMU 用时衡量加速程度。CUDA、Zig、Rust 等仅对实际启用且可取得的设备/工具链提出已测声明。

嵌入式首先确定真实 Flash/ROM/RAM 与块缓冲预算，再接 BSP 和实板：四张 m17 模型约 75,196 字节，四张 m33 约 448,252 字节，尚不含帧、栈、RTOS/BSP 及存储访问成本。验收记录 map/stack、存储位置、输出正确性、周期/帧耗时及截止期；功耗须在具备测量条件时单独测试。QEMU 继续承担兼容性门禁。

### P4：受控恢复矩阵与发布统一报告

在小候选集收敛后，先给控制器补完成回执、进程退出/入账一致性核对及幂等恢复，仅用一个已知停机案例验收，再明确恢复哪个剩余子集。不自动恢复 7917 项或把旧失败抹掉；保留原观察分母与未覆盖项。

最后新增对应版本的报告，逐项对照题目指标及三个打分项，把官方条件缺失、工程完成度、质量、性能和资源预算分开写。开源对照选择能在同一固定环境复现的明确版本与相同算子/输入契约；新报告不覆盖 R27 冻结 PDF，也不借 PR #9 数据宣称跨环境 SOTA。

推荐实际启动顺序为 **P0 → P1 → P2**。P3 的接口盘点可在此期间进行，性能优化等待目标硬件确认；P4 的调度修复先于任何大矩阵恢复。每个阶段独立说明、独立 PR、集中验证。

## 5. 本次验证记录

### 环境与目的

- 系统/硬件：Windows 11 `10.0.26200`，x86_64，AMD Ryzen 9 8945HX，16 核/32 线程。
- 工具链：Git `2.51.0.windows.1`、CMake `4.2.0`、MinGW GCC/G++ `15.2.0`，MinGW Makefiles，Release；构建并行度 8。
- 构建选项：`JSHC_ENABLE_AVX2=ON`、`JSHC_ENABLE_FULL_FIT=ON`、`JSHC_ENABLE_PORTABLE_C=ON`、`JSHC_ENABLE_EMBEDDED=ON`；OpenMP 可用；C++ SIMD/Zig/Rust/CUDA 未启用。
- Python：`C:\Users\admin\miniconda3\python.exe`，3.13.12；NumPy 2.4.6、SciPy 1.17.1、Pillow 11.1.0、pytest 9.1.1。此环境没有 Numba、tifffile、psutil。
- 线程：环境 `OMP_NUM_THREADS=1`、`OPENBLAS_NUM_THREADS=1`、`MKL_NUM_THREADS=1`；C++ 内核测试另显式覆盖 1/4 线程，嵌入式互操作为单线程。
- 目的：确认冲突整合后共同构建、运行时契约和数据入口回归，核对冻结字节；不是拟合质量或吞吐比较。

### 复现命令

以下在项目根目录的 PowerShell 执行，需将 MinGW 与 CMake 加入 PATH：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:PATH='E:\mingw64\bin;C:\Program Files (x86)\CMake\bin;' + $env:PATH
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
cmake -S . -B build-sync-pr-roadmap -G 'MinGW Makefiles' `
  -DCMAKE_BUILD_TYPE=Release `
  -DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe `
  -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe `
  -DJSHC_ENABLE_FULL_FIT=ON -DJSHC_ENABLE_AVX2=ON `
  -DJSHC_ENABLE_PORTABLE_C=ON -DJSHC_ENABLE_EMBEDDED=ON
cmake --build build-sync-pr-roadmap --parallel 8
C:\Users\admin\miniconda3\python.exe scripts/check_correctness.py --build-dir build-sync-pr-roadmap
git diff --check github/main
```

### 实际结果与证据边界

- 构建成功；CTest **3/3** 通过。
- `kernels --full` 在全部 `256³` RGB 输入、m=17/18/25/33 及非均匀 m26 上通过独立整数 oracle 对照，检查短尾、非对齐及四级边界；日志确认 `default=tetra_avx2`、`avx2_cpu_os=true`，五种通用后端通过，另覆盖 C99/结构化路径。
- `embedded_desktop_parity` 使用实际 `.slut` 序列化、四张不同模型（m=17/18/25/33，含非均匀轴），穷举全部 RGB，嵌入式与桌面标量四级输出逐字节一致。`embedded_contract` 通过独立 u64 oracle 及非法输入等有界契约。
- Python **28 passed，2 skipped**；两个跳过对象是 `test_chain_study.py` 与 `test_compatibility.py` 模块，缺少可选 Numba，不能称为新增研究 13 项本机复验通过。
- 冻结完整性：既有 22 份数值源码与同步前指纹一致；PR #9 工作流 12 份源码与提交记录的 SHA-256 一致。对 #9 的 115 个文件核对，108 个与 Git blob 原始字节一致，6 个仅为检出换行差异，另 1 个为本轮有意合并的根 `.gitattributes`。两份本地规范/阶段文档已完整保留。
- 空白检查：本分支相对 `github/main` 的自有差异通过；合并暂存区包含上游第三方 README/LICENSE 的原有尾随空白，保留原文未清洗，不作为本轮新增问题。最后同步的 #11 仅追加 AGENTS.md，数值门禁没有因纯文档变更重复执行。
- 本机详细日志保存在忽略目录 `artifacts/sync-pr-roadmap/`（`configure.log`、`build.log`、`correctness.log`、`integrity-audit.json`）；CTest 明细位于 `build-sync-pr-roadmap/Testing/Temporary/LastTest.log`。本文件记录可持久审查的命令、环境和结果，日志路径不代表新检出仓库含完整缓存。
- 未执行：新的 LUT 拟合、压力参数矩阵、照片/全色域拟合误差扫描、性能比较、官方评分、CUDA、其他可选 SIMD、QEMU 本机复跑及实板测试。运行时穷举通过不代表任意稀疏模型对完整 LUT 都有小误差。

Agent：Codex

Operator：本次会话的项目用户

Task：同步远端并根据最新 PR 规划后续工作

Status：本轮本地整合与规划完成，集成 PR 保持 Draft；三个相关缺陷待修复，建议实验尚未实施
