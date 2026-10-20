# 原地输出、加载重叠与独立进程评估

目标仍为固定精度下达到修订23的300%吞吐。**尚未完成。** 最新的独立进程协议中，40的纯映射1/4线程为2.6444倍／3.1200倍，真实输出为3.3066倍／4.3069倍；单线程纯映射失败，按冻结规则跳过条件确认。先前来宾空闲混合进程协议的通过点保留，不用它替代后续更严格的失败结果。

本阶段基于`1c955caf5e24976a93bb8b0843e3e4bcbbd35be5`及Draft [#49](https://github.com/WyEhNf/flash-chroma/pull/49)，工作分支`codex/skylake-inplace-path-20261020`。实现提交由[交付元数据](../../report/data/skylake-inplace-path-v1/delivery-metadata.json)记录。没有修改公共默认、原23、模型或只读AGENTS.md。新算法源在`experiments/skylake-{inplace,raw32,overlap,overlap16}-runtime`；冻结计划、验证器、性能驱动和画像脚本均随提交保存。

## 实现及停止依据

| 修订 | 单一研究变量 | 结论 |
| --- | --- | --- |
| 43 | 从40出发，原地对齐主循环改用普通AVX2写，真实输出保留非临时写 | 单次画像1线程略降、4线程反升；墙钟没有支持整体收益，停止 |
| 44 | 从40出发，将u8 ID及依赖调色板访问改为64MiB直接RGB32表 | 每像素指令减少，generic cache miss和周期增加；停止扩展 |
| 45 | 从40出发，原地采用4像素GPR查表及偏移0/3/6/9的重叠32位写，携带下一组首R | 完整精度通过，但周期严重增加；保留负结果 |
| 46 | 修正45组首读取：只读未覆盖的GB16，再与携带R拼合 | 消除静态部分地址重叠后恢复多数周期成本，仍未优于40；停止此分支 |

43、45、46仍为16MiB ID表，句柄28,046,644字节。44为64MiB表，句柄78,378,292字节。原23句柄11,269,404字节。45/46的AVX2请求选择的是特化GPR原地循环，真实输出仍为40的AVX2非临时写；不能把选择器名称当作每条指令均为AVX2。模型表只从固定四个稀疏模型和逐级RGB8规则生成，构造器不读取照片、完整源LUT或gold。

45旧组首32位读与上一组末32位写有1字节地址交集，即使随后掩码丢弃该字节，机器加载仍重叠。46以16位GB读取避免交集。静态分析分别发现17个旧掩码位置消失、16位加载从1处增至18处。[Intel手册3.6.4.1](https://cdrdv2-public.intel.com/821612/248966-Optimization-Reference-Manual-V1-050.pdf)提供store forwarding限制的研究依据；本机为AMD，未采集专用stall事件，因此只能说静态变化和周期结果与该假设一致，不能声称已测得具体stall原因。

## 正确性与精度

实际为Ryzen9 8945HX／Windows11宿主WSL2 Ubuntu／Linux6.18.33.2／GCC15.2／Python3.14.4标准库。Release，独立AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`，没有native、AVX512、FMA或fast-math。用户确认最终服务器SKU未知，继续通用AVX2；没有实际Skylake验证或锁频控温。

四版分别独立解码全部16,777,216个表颜色，并执行12组in-place及12组真实输出完整RGB8比较。45/46另有R快速变化的全域置换输入，各增加in-place 1/4线程及真实输出1/4线程四组，避免常规域顺序中R长段相同掩盖携带错误。本阶段新增104组完整域API比较，逐字节完全一致。复用40的构建和24组全域证据明确标作旧证据，没有冒充新增执行。

| 修订 | 有限in-place比较 | 有限输出/别名比较 | 保护页比较 | 64种目标对齐比较 |
| --- | ---: | ---: | ---: | ---: |
| 43 | 2208 | 4416 | 736 | 1280 |
| 44 | 2208 | 4416 | 736 | 1280 |
| 45 | 2544 | 5088 | 848 | 1280 |
| 46 | 2544 | 5088 | 848 | 1280 |

每版另有44条新API拒绝检查。全域输入块262144像素，覆盖四个65536工作块；45/46增加4像素组及携带边界。相同模型的四级gold SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，单级为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`。固定100图输入SHA为`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，所有性能输出SHA均为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。

当前输出完全不变，所以已有精度不下降；没有重新拟合或声称相对官方LUT零误差。历史误差是RGB欧氏距离，非CIEDE2000；照片已见。其他网格全面矩阵、分配失败注入、MSVC及真实Skylake未新增验证。

## 三种协议的结果分别保存

下表都是同场候选／23耗时比，越低越好。AB/BA/BA/AB四个配对重复，线程次序1/4、4/1、1/4、4/1，每配置5轮100图。先取每进程轮次中位，再取四个配对比值中位。不同协议不比较绝对耗时，不挑选通过的协议或丢弃异常轮次。

| 协议及候选 | 纯映射1/4线程 | 旧copy+apply 1/4线程 | 真实输出1/4线程 | 整体 |
| --- | --- | --- | --- | --- |
| 原混合进程43 | 0.412090 / 0.489027 | 0.542571 / 0.747949 | 0.343271 / 0.244823 | 未通过 |
| 原混合进程44 | 0.533637 / 0.568403 | 0.638683 / 0.774975 | 0.410501 / 0.309074 | 未通过 |
| 原混合进程45 | 1.277470 / 1.474693 | 1.250374 / 1.251643 | 0.272817 / 0.202577 | 未通过 |
| 来宾空闲混合40 | 0.305876 / 0.320639 | 0.402305 / 0.565037 | 0.286878 / 0.262037 | 仅该点通过，未确认 |
| 来宾空闲混合46 | 0.386171 / 0.518369 | 0.509689 / 0.744808 | 0.473507 / 0.373186 | 未通过 |
| 来宾空闲独立配置40 | 0.378161 / 0.320512 | 0.472319 / 0.401269 | 0.302429 / 0.232184 | 未通过，跳过确认 |

前五行均为4个串行进程，每进程加载两库和两种线程、两种API模式。新协议的动机是观察到WSL命令间可重新启动，且46混合协议候选先行的两个进程真实输出明显较慢；[顺序描述分析](../../report/data/skylake-inplace-path-v1/skylake-isolated-protocol-v1/order-effect.json)只有每组两个进程，不证明具体成因。没有声称启动或库同处一进程必然导致某次测量偏差。

空闲前置条件：父进程至少等待120秒、PID1年龄≥180秒，每5秒采样全机和CPU0/2/4/6，连续两段忙碌≤10%；iowait计作非空闲，只加`/proc/stat`前8项，避免guest重复计入。每阶段最多等待600秒，失败会保留原始记录。PID1年龄按[proc stat文档](https://www.man7.org/linux/man-pages/man5/proc_pid_stat.5.html)中的starttime及实际时钟频率计算；CPU字段边界见[Linux文档](https://www.kernel.org/doc/html/latest/filesystems/proc.html)。两次空闲混合各5份、独立配置33份原始采样回执全部离线复算。来宾空闲不保证宿主独占、锁频、控温或测试期间无竞争。

最终独立协议每角色、线程、API模式分别exec新进程，只加载该角色主库，共32个不同PID。每子进程只预热/执行所选模式，其余计时数组为空；父进程不加载模型。`pair*.json`为两个独立角色进程的派生配对，不是原始单进程记录。库路径、实际映射SHA、PID和父PID、实际团队、TID绑定、模式轮次和派生来源均核验。固定CPU0/2/4/6，主线程CPU0，明确设置OMP_PLACES、PROC_BIND及DYNAMIC。16个候选子进程前后VMA均恰为16MiB且AnonHugePages为16MiB，不只依赖madvise成功或较大VMA的部分覆盖。

独立协议纯映射1线程四对比值为0.343398、0.417738、0.305535、0.412923；4线程为0.176334、0.348411、0.292613、0.570162。真实输出第3对两种线程为1.065715／1.275940，其余较快，全部保留，原因未定。准备加首组100图配对中位为0.724021／0.895500。

固定门槛为纯映射及真实输出1/4线程中位耗时比≤1/3、最差纯映射配对比≤0.9、准备加首组中位比≤1。预先要求首次独立系列通过后才能执行一次条件确认，两系列及合并8对均须通过；首次失败因此跳过。旧混合确认计划及审计脚本保留为**未执行方案**，不存在确认输出。[决定记录](../../report/data/skylake-inplace-path-v1/skylake-isolated-protocol-v1/confirmation-decision.json)绑定失败结果SHA。不能反复测相同代码挑到快点。

映射计时不含文件IO、解码、分配、SHA或构造；每次原生调用处理整组100图，不是100次分开API调用。真实输出含API验证、映射、对齐、尾部、fence和线程工作；参考为真实memcpy加23。旧copy+apply单列，尚未3倍。准备为4线程构造，准备加首组是预热后的首个测量，不是冷启动或完整端到端保证。

## 单次画像、失败分析与归档

四组PMU各两个版本、1/4线程，每项一次预热一次计数，共16项。原生墙钟成绩调用为0，输出、逐TID四事件组及running/enabled≥0.99通过。

| 同场配对 | 1线程周期/像素 | 4线程周期/像素 |
| --- | --- | --- |
| 40→43 | 4.3141→4.0085 | 4.5187→5.0921 |
| 40→44 | 3.2496→4.2407 | 3.5144→4.6243 |
| 40→45 | 3.4414→14.6650 | 3.5171→14.1435 |
| 45→46 | 14.7151→4.0045 | 14.1591→4.4270 |

44指令/像素由约5.401降至4.401，generic miss由约0.138升至0.217；不是指令更少就更快。不同画像参考周期变化大，不跨行相除。泛化cache事件依CPU而异，不能标为L3或Skylake事件，见[perf_event_open](https://man7.org/linux/man-pages/man2/perf_event_open.2.html)。目标服务器硬件/软件gather取舍仍需实测，依据[Intel手册15.16.4](https://cdrdv2-public.intel.com/814198/248966-Optimization-Reference-Manual-V1-049.pdf)。未改系统安全缓解、perf权限、服务、WSL配置或系统大页策略。

静态加载分析首次误以为函数内原本没有16位读取，实际标量尾部已有1处，分析断言失败。旧分析源及failure保存，随后只修正静态断言为1→18并独立重算；没有改库或重新计时。独立协议执行前发现未执行草稿存在重复pid键和未选模式空数组下标，先保存草稿与修正记录，再冻结正确版本，随后才首次原生执行；没有将失败数值测试删除。

[阶段复核](../../report/data/skylake-inplace-path-v1/performance-audit.json)分别核对5组混合、1组独立比较，共480轮旧模式及480轮真实输出和16项画像。控制台摘要沿用了800轮旧显示，JSON已明确列960轮，派生算式与完整原始记录才是依据。[档案核验](../../report/data/skylake-inplace-path-v1/archive-check.json)通过381份原始文件（约9.17MB）、20份源码ZIP的1505项源成员和95项二进制成员。清单不含之后新增的README、静态检查和操作前刷新元数据。大照片和两个全域流按冻结SHA恢复，模型复用`report/data/skylake-palette-v1/fixed-models.zip`。

构建与验证复现示例（仓库根目录，先同SHA恢复输入；不得覆盖已有输出）：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-overlap16-v1.json --output artifacts/skylake-overlap16-linux-build-v1
python3 scripts/verify_skylake_overlap16_linux.py --plan experiments/skylake-overlap16-v1.json --build artifacts/skylake-overlap16-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-overlap16-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_isolated_pinned_linux.py --policy experiments/skylake-batchspan-isolated-perf-v1.json --output artifacts/skylake-batchspan-isolated-perf-v1
python3 scripts/audit_skylake_inplace_path.py --output artifacts/skylake-inplace-path-delivery-v1/performance-audit.json
```

原始路径已存在，命令用于说明冻结流程；新环境须新计划/输出并保留新构建SHA，不能修改历史计划绕过绑定。归档Linux库是Ubuntu/glibc2.43本机证据，目标服务器应重编译。

## 协作状态和剩余工作

已完整读取43个PR、2个独立issue、2个Discussion、131组REST意见及0审查线程，分页完整；新增#49全文已读，其两项常规CI成功。原发送正文未跨会话留存，因此仅声明已读，不虚构原文逐字相等。操作前刷新结果保存到[协作检查](../../report/data/skylake-inplace-path-v1/pre-create-remote-check.json)。[#7](https://github.com/WyEhNf/flash-chroma/issues/7)/[#9](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)修复337a3dd、[#27](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)修复876e15b8及[#29](https://github.com/WyEhNf/flash-chroma/pull/29)修复397cc367均已包含。完整关联链接、状态及祖先证据见[检查记录](../../report/data/skylake-inplace-path-v1/remote-check.json)。

仍待处理：3倍整体目标、实际Skylake速度、[#8](https://github.com/WyEhNf/flash-chroma/issues/8)的官方派生缓存许可/内存预算/Threshold及接口实板、GUI #40独立事项。保持Draft，不合并、不关闭事项。下一阶段优先研究16MiB表的缓存行局部性，保留通用AVX2回退；更大表及GPR重叠写路线停止。C盘空闲0和WSL无交换盘的已知限制继续保留，未删除用户文件。
