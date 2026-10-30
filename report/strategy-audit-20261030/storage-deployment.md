# 历史策略审计：内存、表示、部署与参数入口

- Agent：`/root/history_storage_audit`；操作人：当前任务用户；状态：只读审计完成。
- 日期：2026-10-30；范围：`F:/Hackathon/worktrees/p16-frontier-header-20261027` 源码，以及实际安装的 `F:/Hackathon/极速焕彩测试框架/FlashChroma`。
- 本次只检索源码、历史研究及已有测量原件，没有修改生产代码、拟合模型或重跑性能。

## 结论

**不能说有价值的历史策略已经全部接入当前框架。** 当前高性能配置已使用 RGB24 Direct、AVX2、调用者工作区和单线程交付；单头内也已有连续偏好选择器、资源预算和目标裁剪。但“头文件包含能力”与“当前框架入口实际调用”有差别：框架没有调用选择器、没有暴露连续 ABC 权重和硬预算；旧精确对象共享、独占紧凑稀疏句柄和只读映射也没有接入。

未接入不等于都应加回。历史小字典、降位和逐像素差分有明确反例，部分 ROM 压缩只有特定模型、后端和速度档位的正证据，不能把历史模型收益直接套到赛事 LUT。

## 对象身份与当前数据路径

| 本次核对对象 | SHA256 |
| --- | --- |
| `include/flash_chroma.hpp` | `9e5fa9ac474c6f9f60c05c19ad859353bf9b6fe88983cc01c3bee21cf1e11953` |
| 实际安装 `flash_chroma_framework.hpp` | `f28d672c46a13180516741ff181d32414770ef331700cec8354bdb204473bb31` |
| 实际安装 `main_flash_chroma.exe` | `b363723be4d64073b9a8e1369e8268b59985293a22711b72b900b658f9be7c47` |

当前推荐测量配置是 `m33 / framework 网格 / chain_ls / DirectRGB24 / AVX2 / 单线程`；安装启动器的默认仍是 `sample / uniform / auto`，执行默认命令不会自动得到这套配置。已有报告记载平均 RGB 欧氏误差 1.484947、最差单图平均误差 2.385774，自有模型＋arena＋对象 51,372,819 B，约 48.99 MiB；该记账不等于完整进程 RSS，也不含单列的原框架节点副本。[既有测量](../../docs/stages/2026-10-30-rgb24-kernel.md#L57)

准备路径为：读取 16 位原 3DL → 主机上采样／最小二乘拟合 → 四个 `Stage::blob` 保存完整 SLUT → 框架 `out.data` 再复制一次节点 → `Chain::prepare` 借用 Stage → AVX2 将各级节点转换为 packed RGB32 暂态 → 构造 DirectRGB24 整体映射表。框架随后释放原始 16 位表；已准备运行器仍保留模型 blob、包装节点副本及整个 arena。该结构满足热循环不分配，但不是最小驻留表示。[适配器](../../framework/flash_chroma_adapter.hpp#L33)、[框架复制与释放](../../scripts/install_framework.py#L114)、[核心准备](../../src/flash_chroma_cpp.inc#L375)

## 已应用且当前配置触发

| 策略 | 当前状态与边界 | 依据 |
| --- | --- | --- |
| RGB8 节点、四阶段整数映射、SLUT 元数据与轴表 | 使用；源模型完整保留，AVX2 packed 是附加表示 | [Stage](../../framework/flash_chroma_adapter.hpp#L94)、[pack_views](../../src/flash_chroma_cpp.inc#L163) |
| DirectRGB24 全 RGB 域映射 | 推荐配置显式触发；无需假定输出颜色数能装入 U8／U16 palette | [Representation](../../src/flash_chroma_cpp.inc#L68)、[入口](../../scripts/install_framework.py#L63) |
| 调用者提供工作区、提前计算容量、超预算拒绝 | 已用；框架固定默认 64 MiB，超出返回 Budget | [默认预算](../../framework/flash_chroma_adapter.hpp#L129)、[容量检查](../../src/flash_chroma_cpp.inc#L342) |
| 混合四级 m 与网格、表示、后端可调 | 已用；CLI 支持单个 m 或四个 m，17～33，非连续运行模型 | [解析](../../scripts/install_framework.py#L47)、[启动器](../../scripts/install_framework.py#L250) |
| 单个主机集成 hpp | 已用；core＋适配器＋IO＋拟合器在聚合头中，main 只作为框架入口 | [安装脚本](../../scripts/install_framework.py) |
| 离线准备与热路径分离、比赛单线程 | 已用；入口强制 threads=1，准备不向逐像素路径引入拟合依赖 | [线程约束](../../framework/flash_chroma_adapter.hpp#L153)、[安装入口](../../scripts/install_framework.py#L96) |

当前 direct 模式构建后，arena 内含构建时使用的 packed 暂态区域；框架持有整个 vector，不在完成后缩减到 persistent 区域。不能只把直表字节数当作总运行容量。[Runtime 要求](../../src/flash_chroma_cpp.inc#L342)、[arena 生命周期](../../framework/flash_chroma_adapter.hpp#L203)

## 已有代码但当前入口没有触发

| 能力 | 当前缺口 | 影响与建议 |
| --- | --- | --- |
| 连续 ABC 偏好 | `Preference` 三个 double 和 `fc::select` 已随头交付；框架 main/run.ps1 不调用它 | 用户只能手选 m/模式。连续的是偏好权重，执行结果仍是合格离散候选；接入口时需要本轮 LUT、机器、头文件绑定的候选证据，不能直接用旧 Cinema 时间排名。[定义](../../src/flash_chroma_selection.inc#L11)、[选择与归一化](../../src/flash_chroma_selection.inc#L197) |
| 精度／时间／RAM 硬约束 | Request 已有误差、时间、runtime/workspace 预算；CLI 未暴露，64 MiB 仅固定默认值 | `auto` 只启用结构证明并选 Sparse，不是 ABC 最优选择。[Request](../../src/flash_chroma_selection.inc#L35)、[过滤](../../src/flash_chroma_selection.inc#L136)、[auto](../../scripts/install_framework.py#L63) |
| Desktop/Mobile/Embedded/Portable 开关 | core 的 target 宏与禁用 direct/AVX2/OpenMP 能力已实现；安装启动器只固定关闭 OpenMP，没有 Target 参数 | 可按编译期宏另建核心交付。聚合框架头仍含 vector/ifstream/拟合器/异常，不能称裸机零堆版；移动 ARM 当前没有 NEON 优化。[宏](../../src/flash_chroma_cpp.inc#L11)、[启动器](../../scripts/install_framework.py#L250) |
| 独立 C99 `.h` 零堆部署 | `include/flash_chroma_c.h` 及 portable/embedded 部署存在，借用 ROM／视图，调用者负责生命周期 | 不是当前主机框架应用的构建路径；真实板上 BSP、缓存／DMA、功耗尚未成为本轮证据。[C99 合同](../../include/flash_chroma_c.h#L4)、[实板边界](../../embedded/README.md#L143) |
| 内容寻址对象包 | `p16_submission.py` 已按 SHA 落 `objects/`，含 logical/unique 容量记账；当前框架安装和启动不走该模型包 | 现在程序源码 ZIP 的压缩不等于拟合后 LUT 对象去重，也不减少运行 RAM。[实现](../../scripts/p16_submission.py#L113) |

## 有价值且可迁移、当前尚未接入的策略

### 1. 完整对象精确共享、释放无用副本

历史联合研究的推荐顺序是完整对象 SHA 去重 → 发布包压缩 → 加载时完整解压。原 default＋max41 总模型对象 914,936 B → 681,594 B，减少 25.50%；这是两套旧模型的容量证据，不是当前四级的节省比例。[历史研究](../../docs/stages/2026-10-27-joint-lut-avx2.md#L16)

本轮存在更直接的可迁移证据：`artifacts/rgb24-regression-photos-100-20261030-long/native/stage-2.slut` 与 `stage-3.slut` 的完整 SHA 都是 `528ae36470ff282bb6b5f06856b32a3e64db3cd2b9eab9e88f51eea05c866b71`，各 112,063 B。当前每级独立持有 vector，`pack_views` 又逐级分配 packed 节点和轴；没有跨级对象共享。`PackedView::shared` 只表示同一级输出通道共用轴，不能据此说已去重。[Stage blob](../../framework/flash_chroma_adapter.hpp#L33)、[四级打包](../../src/flash_chroma_cpp.inc#L158)

原始 Test2/3/4 相同也不能直接把三者全共享：`chain_ls` 会修改第四级，必须在最终拟合后按完整对象及布局核验相等。减少 out.data 副本和同对象共享可先优化准备／驻留，不应承诺逐像素变快。现有 Runtime 借用模型、边界验证也使用其地址，不能直接清空 blob；需重构所有权或单独的 owned-only 运行句柄。[借用初始化](../../framework/flash_chroma_adapter.hpp#L169)、[包装节点副本](../../scripts/install_framework.py#L176)

### 2. 独占紧凑稀疏句柄与 RGB24 packed 稀疏节点

历史普通四级模型的 owned packed RGB32 句柄把实际常驻容量 487,737 B → 268,308 B，减少 44.99%；同场最差吞吐保留单线程 97.21%、四线程 92.86%，A/A 有效。它通过转换后释放 canonical/sidecar、共享相同轴和控制 vector capacity 节省所有权成本。[历史紧凑句柄](../../docs/stages/2026-10-24-memory-compact-sparse.md#L3)

RGB24 packed 又把该普通模型降到 206,020 B，较 RGB32 少 23.21%；但单线程最差只保留 79.19%，两线程情形合并仅有 70%档，不应当默认快速后端。当前 Sparse AVX2 仍为 RGB32 packed，四种 Representation 没有紧凑 owned 模式。[历史 RGB24 sparse](../../docs/stages/2026-10-24-memory-rgb24-sparse.md#L3)、[当前枚举](../../src/flash_chroma_cpp.inc#L68)

这是低 RAM 或禁止 direct 设备的候选，不是目前约 50 MiB RGB24 直表的无代价替代：相同旧 a399 链的 compact sparse 仅有最快直表约 3.4%吞吐，历史已明确拒绝作为快路径。[限定用途](../../docs/stages/2026-10-24-memory-compact-sparse.md#L5)

### 3. 只读预生成直表加载与发布包压缩

旧 Windows 研究消除了 ACCESS_COPY 视图保留的约 16.78 MB 提交额度，实际 ROM 容量仍 16,779,328 B，working set 约 53.55 MB 相近；原地单线程控制失效，只有其他三个模式的限定速度资格。它是提交量优化，不是物理 RAM 压缩。[只读 loader](../../docs/stages/2026-10-24-memory-readonly-loader.md)、[证据边界](../../docs/stages/2026-10-24-memory-evidence-overview.md#L95)

当前 Runtime 把 Direct 表写入调用者 arena，框架没有 prepared-table 文件加载／映射接口；要迁移需定义表身份、不可变性、生命周期和边界验证，不能直接替换 private 指针。离线压缩旧 default 文件可到 zlib 233,100 B／xz 182,512 B，但只能宣称包体节省，不等于热路径更快。[包压缩](../../docs/stages/2026-10-27-joint-lut-avx2.md#L29)

### 4. 无损页字典／精确块与编译器选择

P4 4KiB/LE16 页字典曾以 12,633,164 B 对线性 ROM 16,779,328 B，AVX 四模式最差保留 53.896116%，112 门有效；同布局 C99 全低于 50%。1024B 精确块 10,801,216 B 首场四模式最差 52.29%，后场原地单线程控制失效，没有完整跨场确认。当前核心没有页字典／块 decoder。这些是 RAM 优先的候选，先对当前输出做容量普查，再评估访问成本；旧模型字典不能直接用于当前RGB24输出。[总览](../../docs/stages/2026-10-24-memory-evidence-overview.md#L11)、[1024B边界](../../docs/stages/2026-10-24-memory-evidence-overview.md#L45)

旧 Clang 同源 C99 store 的四模式约55%吞吐资格不适用于当前 GCC AVX2 RGB24 路径。当前赛事要求的编译器约束也需优先；如允许更换，需对本轮头与 LUT 单独校准，不能据旧结果称已漏掉确定加速。[Clang 研究](../../docs/stages/2026-10-24-memory-clang-c99-store.md)

## 不应当作为“遗漏优化”盲目加回

| 历史策略 | 不纳入当前默认快路径的理由 |
| --- | --- |
| 四级逐像素精确差分恢复 | 相邻 int8＋逃逸需要500,733 B，中位数基底611,525 B，均大于原节点431,244 B；跨68模型组件去重仅2.50%、m33 MST差分仅3.23%。[证据](../../docs/stages/2026-10-27-joint-lut-avx2.md#L27) |
| 16B/3B map、小17bit split、常量tag、512bank/7bit、native页指针 | 后续有有效低于50%速度反例；native页指针还增加容量。不能只引用曾经通过的最好场次。[逐项汇总](../../docs/stages/2026-10-24-memory-evidence-overview.md#L60) |
| 512bank/6bit | 54个bank超过64色、最大95，只有普查，没有可部署ROM或速度证明。[证据](../../docs/stages/2026-10-24-memory-evidence-overview.md#L109) |
| Windows alias 页映射 | 句柄归零门禁STOP，没有完整像素域／百图／性能通过；backing大小也不等于物理RAM。[证据](../../docs/stages/2026-10-24-memory-evidence-overview.md#L99) |
| 节点6/5bit、坐标6bit、输入7bit近邻 | 历史逐图精度保留存在约3%、6.67%、43.38%失败；12/8bit坐标及节点7bit只有逻辑bitstream研究，尚无真实decoder部署资格。[证据](../../docs/stages/2026-10-24-memory-evidence-overview.md#L105) |
| OpenMP／多线程、GPU/NPU | 比赛框架要求单线程CPU；已有多线程研究不能作为当前参赛优化，core保留能力也不代表允许触发。 |

## 建议顺序

1. **先补入口整合**：将连续 ABC 权重、误差／时间／运行RAM／workspace预算、目标档位接到 CLI；输出所选候选ID、来源证据及不可行原因。先生成当前 LUT 和环境合格候选表，`auto` 与结构证明的名称语义分开。
2. **再做低风险容量收敛**：拟合后按完整对象共享相同stage，审计并去除原框架不再使用的节点副本；验证只读模型生命周期与别名拒绝合同后，再考虑 owned-only compact 句柄。当前stage2/3的完整相等已证明，尚未实测修改后的节省和速度。
3. **把低RAM后端作为独立候选**：packed RGB24 sparse、P4/1024B字典、只读prepared表分别立项，遵循新LUT容量普查 → 完整输出合同 → 同场单线程速度／容量验证；不替换已验证最快配置。
4. **保留真实部署边界**：主机framework聚合hpp和裸机core/C99.h分别给出构建命令及可用能力；真实移动ARM性能、NEON、BSP/DMA等未验证项如实列出。

该审计没有给出“新优化已成功”的结论；它区分了当前已执行能力、仅随头交付能力、可迁移正证据与明确负例，供主任务统一决策。
