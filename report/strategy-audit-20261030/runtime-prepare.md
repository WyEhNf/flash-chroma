# 历史运行时与准备策略迁移审计

Agent：Codex `/root/framework_strategy`；Operator：本会话项目用户；日期：2026-10-30；状态：完成只读审计。

本次仅阅读历史阶段文档、当前源码和已保存回执，并解析一张 112,063B 的冻结 SLUT 检查节点范围；没有编译、拟合、执行图像映射或重测性能。环境为本机 Windows / PowerShell / Python 3.12.14。本文件是新增审计记录，不修改生产实现和历史测量。

结论：当前交付已经吸收主要通用 RGB24 查表、ILP、输出打包、65536 像素分块和输入预取策略，但不能说所有历史有效策略都在当前任务中启用。最明确的差别是：双像素 64 位输入读取 / BMI ANDN 只在 U8/U16 分支；修订 100 扫描线准备器与首级小域后缀缓存虽然已迁入库，当前首级范围使其提前回退；旧 bridge 的免重复清零没有进入 framework adapter。前两项中仍有可研究的通用迁移方向，尚无当前 RGB24 同场收益证据。

## 审计对象和实际执行路径

本报告的“当前性能配置”专指已验证的 `m=33,33,33,33 / grid=framework / fit=chain_ls / representation=direct_rgb24 / backend=avx2 / threads=1`。它与无参数 `run.ps1` 的 `auto / uniform / sample` 默认配置不同。生成脚本的 README 快速示例若遗漏 `-Grid framework`，将不能复现此配置；应使用完整参数。

```powershell
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Backend avx2 -Grid framework -Fit chain_ls
```

审计时 SHA256：

| 对象 | SHA256 |
| --- | --- |
| `include/flash_chroma.hpp` | `9e5fa9ac474c6f9f60c05c19ad859353bf9b6fe88983cc01c3bee21cf1e11953` |
| 实物 `FlashChroma/flash_chroma_framework.hpp` | `f28d672c46a13180516741ff181d32414770ef331700cec8354bdb204473bb31` |
| `src/flash_chroma_direct.inc` | `ca352346705cbdfa5131efff6b1c8fdf92703b5064bd26def81bc056539d9dd0` |
| `src/flash_chroma_prepare.inc` | `350eeccb2995af5e9cac6adfa0aab8484183853918e0b3aec40aa6cde54ce613` |
| `src/flash_chroma_cpp.inc` | `9e2098c095e2d181ba6feaacbd182c971236c916bb13cc125caafff96786148e` |
| `framework/flash_chroma_adapter.hpp` | `951302cf6f4d7a417c81c6694b8eb91c52a258b74aa8fa19c807c8c416b6e617` |

原框架实际执行日志 `artifacts/rgb24-original-framework-20261030/runs/r01-01-after.stdout.log:4` 报告 `structured=0 backend=2 representation=3 threads=1`，模型 448,252B、arena 50,919,295B、object 5,272B、wrapper 节点副本 431,244B。`main.cpp:374–378` 只用完整源 LUT 拟合第四级，前三张采样模型不改；准备位于读取图片之前。

实际调用链是 `Chain::apply → Runtime::map → direct8 → direct_rgb24_run → direct_rgb24_block_run<false>`。`direct8` 的 RGB24 分支在检查 BMI 前返回。框架强制关闭 OpenMP；原生算法为 1 线程，不能把进程观测到的 3 个线程写成 3 线程算法，也不能宣称整个进程只有一个线程。

## 已迁移且当前确实执行的策略

| 策略与历史证据 | 当前位置 | 当前配置的实际状态 |
| --- | --- | --- |
| 线性完整 RGB8 直接表；旧 `skylake-load-packing` 的 33/35 等从稀疏计算转为独立标量加载、AVX2 打包。旧模型 U8 表特性不能推广到新 LUT。 | `flash_chroma_cpp.inc:405` 构建 RGB24 表；`flash_chroma_direct.inc:265` 每项读 4B、只消费低 24 位；表末 4B guard。 | 已启用 RGB24 48MiB 表，保持四级模型逐级 RGB8 的精确输出；不依赖少色调色板。当前大表不能称作原始 m³ 模型容量。 |
| 八路独立查表、缩短依赖链、输出预排；历史 33/65/79 的思想。当前 RGB24 专门迁移了 ILP，不能仅因旧 U8/U16 有函数就认为曾覆盖 RGB24。 | `direct_rgb24_read_wide:285`、四项一组的编译器屏障 `:291/:297`、`direct_rgb24_block_run:303`。 | 已启用；主循环仍是 8 次 32 位输入加载、8 次表值加载。编译器屏障不是 CPU 栅栏，具体目标机器收益以当前测量为准。 |
| 64 像素读取后统一写出、64B 目标对齐、精确尾部；旧 37/40 的块结构。 | `direct.inc:308–351`；64 像素的 192B 输出由 6 条 256 位普通存储完成，32/8/标量尾部独立。 | 已启用。64 像素宽读要求至少 72 像素剩余；8 像素尾部准确读 24B。保留输入/输出边界而非通过越界加载换速度。 |
| 1024B NTA 输入预取、65536 像素运行块；旧 38/40 的有效整合。旧 40 的真实输出曾达到相对 23 的 3.0559/3.8973 倍，但不能与当前提速相乘。 | `direct.inc:305–316`；`RuntimeConfig:74`、`cpp.inc:468–486`；adapter `:128/:198`。 | 已启用；每张 1024×768 图以 12 个 65536 像素块调用内核。当前回归驱动也按此块大小调用，避免整图单调用隐去块边界成本。 |
| Shared/nonshared 四面体整数核心与标量/AVX2 分派；保留每级 RGB8 舍入，后端不改数值。 | `cpp.inc:178–195,264–265,405–422,484–496`。 | RGB24 准备回退用 AVX2 `sparse8`，热路径用 RGB24；尾像素用标量。`Auto` 可选 AVX2/Scalar，显式不支持的后端拒绝。 |

当前新 RGB24 内核有独立于历史模型的同场证据：`artifacts/rgb24-regression-photos-100-20261030-long/summary.json` 和 `paired-analysis.json`。100 张相同照片每统计点重复 3 遍，报告除以 3 后的百图等价时间；单线程 CPU16，前后各核 A/A、7 轮 ABBA/BAAB；输出逐字节比较、前后源/输入/exe 身份均通过。含每图 fresh 分配/零初始化的配对中位 after/before 为 **0.7193688**，纯 hot 为 **0.6460553**；两范围各自 4 个 A/A 均通过，漂移上限分别 1.0723% / 2.1816%。第一场 cached hot 预 A/A 漂移 6.6443% 的失败仍保留，没有拿它排名。

原框架另外 5 对独立进程为 `10.960 → 7.877ms/四图` 的样本中位，配对中位比 `0.7162409`，每图 Delta 一致；该场**没有评估 A/A 稳定性**，作为真实框架确认，不替代上述控制。所有性能数字都是已有回执，本审计未运行这些测试。

## 已迁移但有条件，当前未触发或只部分迁移

| 策略与历史有效性边界 | 当前位置/条件 | 当前配置结论与遗漏 |
| --- | --- | --- |
| 固定四级的共享性编译期专门化：10-19 在同一 a399 链把 `transform<false/true/true/true>` 固化，1/4T 配对耗时下降 10.7048%/7.7643%，各进程保护门槛通过；未绑核/锁频，不能推为当前平台普遍收益。 | `cpp.inc:247–262` 的 `transform` 仍在函数中判断 `v.shared`；`:264–265` 只有固定四级长度的普通 `for`。没有四级共享模式的模板入口；`prepare_first8<Shared>` 只专门化已获证小域准备器的第一层。 | **没有完整迁入**。编译器可能展开长度 4 的循环，不等于源码已将 shared/nonshared 固化；本审计未反汇编，不能断言最终分支数。当前四级全 shared，历史 `false/true/true/true` 入口不直接适用，但全 shared 专门化值得作为 Sparse / 通用建表候选。RGB24 表建成后的热循环不执行 tetra，因此不会直接改变该配置的图像 TimeCost。 |
| 首层小域精确后缀缓存：旧修订 4 在冻结 a399 上，1/4T 同场 apply 比约 0.4764/0.4772；修订 16 用逐 cell 证书省掉运行时范围判断，后续比约 0.9293/0.9490。固定模型、不同协议的收益不可相乘。 | `prepare.inc:28–94` 证明域；`cpp.inc:333–340,395–403` 仅在非 Sparse、AVX2、域满足 2MiB 上限时加速 direct **准备**。 | 条件能力已迁入；当前域超限，未触发。原来作为热映射表示的“首层 + 小后缀表”没有独立 `Representation`：当前 Sparse 仍计算四层，缓存仅作 direct 构建临时区。对未来首层压缩颜色的小域 LUT，这种低内存热模式仍属未迁入的历史有效选项；对当前首层无收益资格。 |
| 修订 100 扫描线准备：R 轴连续读取，G 行/B 批固定；旧 N100 创建到首输出相对 97 的 ordinary/a399 分别下降 8.4093%/22.1809%，对应控制有效；全场仅 49/126 项控制有效。 | `prepare_first8:141`、`prepare_direct_blue:170`、`prepare_cached_direct:208`；所有入口受同一个小域证明约束。 | 实现已迁入，当前没有执行。域失败后 `cpp.inc:405–422` 枚举颜色、通用四层 `sparse8`；不存在“不依赖小域也用扫描线首层”的后备准备器。可研究把扫描线第一层与通用后三层组合，但这是新迁移候选，不继承 100 的现成百分比。 |
| U8/U16 调色板与宽索引；历史 293 把后缀上限扩到 2MiB，使 max41 的 264,222 槽可用；历史 Cinema 224/336/613 等颜色数仅属对应模型。 | `cpp.inc:329–332,425–451`；完整色域建立实际 palette，256/65536 容量检查；`prepare.inc:269–276` 支持三格式。 | 当前明确选择 RGB24，不用 palette。旧框架 sample m33 矩阵 U8/U16 的 Scalar/AVX2 均 status=10 Capacity；不能据此冒称 chain_ls 的同一容量测量已经做过。若未来新 LUT 压色，U8/U16 可重新作为显式低内存候选；不可强制截断 ID。 |
| 双像素 64 位读取 / BMI ANDN（79）：每 8 像素 4 次输入读，四 ID 先行。旧 79 相对 23 的真实输出通过其单项门槛，整体 4T pure 目标失败；**不是 79 对 78 的同场直接配对**，因此单独收益没有被隔离。 | `direct_pair48_input:66`、`direct_read_pair48:78`、`direct_palette_run_bmi:203`；`direct8:369` RGB24 提前返回，BMI 检查在 `:372`。 | 已接入 U8/U16，RGB24 **未接入**。RGB24 宽循环目前 8×u32；3×u64 是 `direct_rgb24_read_exact:270` 的尾部，不是 BMI 主循环。可优先研究 RGB24 pair48 和不依赖 BMI 的普通 u64 成对版本，需独立 ISA 回退、尾边界、保护页与同场 A/B；不能说历史已证明它会再提速。 |
| NT 流式输出、SFENCE；旧 37/40 对对应分离输出有效，多线程原地普通写在 43/80 另有条件。 | `direct.inc:328–341` 的 `Stream=true`；`:360` 显式 `FLASH_CHROMA_RGB24_STREAMING=1`，默认 `:363` 为 cached。 | NT 选项已迁入，但当前关闭。4 图 screen 的 allocated 中位 legacy/cached/stream 为 10.836/7.901/8.134ms，仅 5 次描述性结果，未授权“cached 稳定优于 stream”结论；正式 100 图比较只验证 legacy 与 cached。因此保留显式开关合理，不应因历史 NT 有效就改默认。 |
| 避免 arena 先清零再覆盖；10-28 修复已在旧 bridge 用未初始化字节分配。 | `single_header/bridge.cpp:77` 为 `new uint8_t[]`；framework adapter `:203` 为 `vector<uint8_t>::resize`。 | **adapter 未迁移**，会零填 50,919,295B arena，随后准备器再写表。值得做启动成本候选，但官方图像 TimeCost 排除了 prepare；不能承诺热分数提高。更换存储须验证所有被读区域和 guard 已初始化、失败/重复 prepare 生命周期及对齐。 |
| 证明全四层通道可分离时压成 3×256 曲线。 | adapter `:165–194` 要求四层全部 `separable_proven` 且每层完整 256³ 证明。 | 当前 Test1 可分离，Test2/3/4 不可分离；实际 `structured=0`。这是合法回退，不是遗漏。仅利用首层身份/可分离性质跳过部分计算并未实现，属于新候选，不属于已有四层捷径自动可用。 |

### 当前准备缓存不触发的可复核依据

冻结文件 `artifacts/rgb24-regression-photos-100-20261030-long/native/stage-1.slut`，SHA256 为 `a06a38890c90377c8683b5a86118c53062c873e9364be44589f67ee37464005b`。从文件第 4,252 字节开始读取 `33³` 个 RGB8 节点，直接得到：

```text
R = [0,255]
G-R = [-255,255]
B-R = [-255,255]
按 prepare_domain 加 ±2 并 clamp 后仍为上述范围
矩形槽数 = 256 × 511 × 511 = 66,846,976
上限 = 2 MiB / sizeof(uint32_t) = 524,288
```

所以 `prepare.inc:43` 在逐 cell 证明前返回 `entries=0, proven=false`；`cpp.inc:395` 条件不成立。当前 actual arena 50,919,295B 正好为 50,331,712B 对齐 RGB24 表、587,520B packed 稀疏暂态和 63B 对齐余量，没有额外后缀缓存。此结论来自冻结模型、确定代码条件及原框架日志互证，不是仅看到函数存在，也没有执行新的准备计时。

把上限强行扩到此矩形需要约 255MiB 缓存，而且不少槽是非法 RGB；当前不能称为高价值优化。合适方向是保留原拒绝、让通用扫描线准备独立受益，或另设计源 LUT 证明支持的精简表示。

核心已提供 `prepared_with_suffix_cache()` 和 `preparation_cache_entries()`（`cpp.inc:115–116`），但 framework `Info` 和原 main 日志未传出它们。这是可观测性遗漏：建议以后暴露实际准备路径与拒绝原因，避免再次将“启用编译开关”误报为“本模型已命中快路径”。

## 不应因有历史代码就盲加的项目

| 候选 | 历史证据与当前判断 |
| --- | --- |
| AVX-512 | 10-26 unified 后端完成实际完整域/有限合同，但最终流水版本机 8 个配置相对 AVX2 吞吐仅 54.73%–70.88%，非目标 Xeon Gold 6140 实测。当前 `Backend::Avx512` 有枚举，`resolve:193` 明确不支持；没有迁入不构成已证收益遗漏。未来仅在目标 CPU/OS gate、精确尾部和同场实测后作为可选后端。 |
| 原地、普通写/T0/PREFETCHW、多线程专用路径 | 43/80/73/74 的条件针对实际 workers>1 或原地，部分总体门槛失败。当前官方计时创建独立输出，1T；为了选中旧路径改成原地或移出 fresh 分配会改变比较范围。保留 alias 正确性与加入有收益的接口是两件事。 |
| R 连续后缀缓存布局（13） | 同场中位改善 3.29%/6.84%，但 4T 单进程回退 3.24% 超过上限，不采用；当前无小域缓存热路径可套用。模型访问地址统计不是硬件缓存收益。 |
| stage-major（逐阶段扫块） | 降低元数据活跃范围，却多三轮 RGB8 读写，单进程退化门槛失败；当前 `sparse8` 保留像素融合四阶段合理。 |
| prefix-split（非共享首级一次扫块，共享后三层融合） | 10-20 同场 1T 配对比 0.956586，下降 4.3414%；4T 配对比 1.003322、最差进程 +5.9418%，所以整体拒绝。**不能将 4T 拒绝解释为单线程永无价值**。它可作为非共享首层、1T Sparse 的有条件历史正例；当前全 shared，且 RGB24 热映射不跑四面体，原触发布局不成立。 |
| RGB32 64MiB、二维 tile、地址 swizzle | 44/53/54/73 增加 footprint/索引成本，53 单线程周期约 +90%，54 约 +24%，73 控制/性能失败。RGB24 的当前成功不为这些候选补发资格。 |
| 全地址/稀疏 ID 预取、PREFETCHW | 39/56/74 均有明确停止或整体失败；当前只保留输入 NTA。不能用“内存受限”泛称增加预取一定有利。 |
| 早期索引 101 | 10-26 汇总补充完整质量已通过，但没有性能结果；实际栈 768B 对比 100 的 704B，未实现预期缩帧。不是漏掉已证明提速。 |
| 更激进 YMM 输入、输出布局组合 | 50/57 单项局部指标改善不能相乘；59 组合后单线程周期退化，81/82 有调度/溢出问题，83 首轮性能失败。当前必须独立查看目标编译器生成码和真实批次。 |
| 字典/3bit/5bit/P4 压缩 | 历史字典依赖读取/解码有明显成本；10-26 P4 内存缩小约 4MiB，最差速度保留仅 53.896%。适合显式内存档研究，不宜在桌面几十 GiB 场景默认替换 RGB24。存储细节由本轮另一份存储审计展开。 |
| 编译器替换 | 10-20 Clang21 仅静态、未完成链接/运行；55 同源 Clang22 指令下降约 9% 但单线程周期约 +1.6% 后停止。现交付 GCC15.2、O3、C++17、静态链接；指定 GCC13.2 下载失败、未验证，不能称编译器选择已全局最优，也无证据直接换 Clang。 |

上述历史多数实测在 Ryzen9 8945HX / Windows 或其 WSL2，而非 Skylake。PMU、MCA、指令数、缓存行集合及跨场百分比均不等同目标服务器速度。

## 优先行动建议

1. 先修复交付示例的完整配置表达，并传出准备缓存诊断。这不改变数值/速度核，却可防止现场测到不同网格、不同拟合或误报快路径。
2. 若继续优化正式图像热时间，优先评估 RGB24 双像素输入读取；冻结当前 cached 实现为 baseline，比较普通 u64 成对与 BMI1 版本，保护 AVX2 无 BMI 的机器，沿用前后 A/A、fresh allocation 与完整输出合同。历史研究仅支持试验动机，尚不支持收益承诺。
3. 若优化现场反复启动/调参，先去除 adapter 重复 arena 清零，再研究脱离小域证明的扫描线全色域准备和全 shared 四级编译期专门化。后二者也可影响 Sparse 候选；对当前 RGB24 它们影响 prepare/首次输出 wall，需要单列测量，不改原框架 TimeCost 定义。旧非共享首层的 prefix-split 单线程正例只在对应布局重新评估。
4. 对后续不同 LUT、内存较小设备，考虑把“首层 + 有界精确后缀表”恢复为显式表示，并保留证明失败回退。当前模型不满足条件，不能代替 RGB24 推荐档。
5. 不因“全部策略都用上”强开 NT、AVX-512、多线程、palette 或负例布局。组合只能在同数值、同来源、同计时范围的新证据后升级；已经失败/未测的资格继续保留。

## 主要历史与原始证据

- [10-26 三方向汇总](../../docs/stages/2026-10-26-p16-unified-research.md)、[10-27 单头初版](../../docs/stages/2026-10-27-p16-frontier-header.md)、[10-28 性能修复](../../docs/stages/2026-10-28-header-performance-repair.md)。
- [10-19 精度与运行成本汇总](../../docs/stages/2026-10-19-precision-latest.md)、[四级编译期专门化](../../docs/stages/2026-10-19-channel-runtime-specialized.md)、[prefix-split 单线程正例和四线程拒绝](../../docs/stages/2026-10-20-skylake-prefix-split.md)。
- [小域后缀缓存](../../docs/stages/2026-10-20-skylake-suffix-cache.md)、[逐 cell 证明](../../docs/stages/2026-10-20-skylake-domain-proof.md)、[100 扫描线准备](../../docs/stages/2026-10-24-p16-scanline-prepare.md)。
- [载荷与打包](../../docs/stages/2026-10-20-skylake-load-packing.md)、[预取与分块](../../docs/stages/2026-10-20-skylake-cache-hints.md)、[pair48](../../docs/stages/2026-10-21-skylake-pair48-input.md)、[ANDN 分离入口](../../docs/stages/2026-10-21-skylake-andn-split.md)。
- [原地写出](../../docs/stages/2026-10-21-skylake-inplace-path.md)、[普通写路径](../../docs/stages/2026-10-21-skylake-andn-normal.md)、[AVX-512](../../docs/stages/2026-10-26-p16-unified-avx512.md)。
- 负例：[R 连续](../../docs/stages/2026-10-20-skylake-r-contiguous.md)、[stage-major](../../docs/stages/2026-10-20-skylake-stage-major.md)、[direct tiles / Clang](../../docs/stages/2026-10-21-skylake-direct-tiles.md)、[lookup overlap](../../docs/stages/2026-10-21-skylake-lookup-overlap.md)、[输出编排](../../docs/stages/2026-10-21-skylake-output-path.md)、[PREFETCHW](../../docs/stages/2026-10-21-skylake-prefetchw.md)、[YMM 输入调度](../../docs/stages/2026-10-21-skylake-input256-ordered.md)。
- 当前：[受控 100 图摘要](../data/p16-rgb24-optimization-20261030/evidence/rgb24-regression-photos-100-20261030-long/summary.json)、[配对统计](../data/p16-rgb24-optimization-20261030/evidence/rgb24-regression-photos-100-20261030-long/paired-analysis.json)、[原框架确认](../data/p16-rgb24-optimization-20261030/evidence/rgb24-original-framework-20261030/summary.json)、[旧 sample 矩阵](../data/p16-framework-20261029/evidence/framework-samples-matrix-20261029-v2/native/results.json)、[独立源 LUT 证明](../data/p16-framework-20261029/evidence/framework-oracle-20261029/manifest.json)。

验证边界：本报告只对指定配置和冻结版本作静态路径判断，未以此授予任何新候选性能资格；官方最终阈值/评分许可和目标 Intel 成绩仍不能由本机研究替代。
