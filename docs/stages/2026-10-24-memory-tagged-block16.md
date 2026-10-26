# 16题内存独立分支：固定16B块的直接RGB常量tag

Agent：`/root/memory`；Operator：当前16题用户；Status：Failed，质量通过，但四模式速度均低50%而拒绝。工作分支`codex/p16-memory-20261023`，Draft PR由root统一维护；本阶段不修改默认路径，不与精度/速度分支的新模型叠加。

## 目标、资料与预先选择

检验一个具体假设：原字典`map→pool ID→palette`的三层读取，对恒定16B块可由LE32条目直接带最终RGB24而绕过后两层。固定16B、普通条件提前返回，不扫描大小、tag布局、分支提示或其它解码版本；较旧3B略大也如实计入代价。历史旧3B有效低50%反例继续成立，本轮不能恢复其稳健全模式推荐。

[BDI原论文（PACT2012）](https://users.ece.cmu.edu/~omutlu/pub/bdi-compression_pact12.pdf)将重复值作为独立表示，并讨论解码关键路径与容量的取舍；[Velox官方Vectors](https://facebookincubator.github.io/velox/develop/vectors.html)与[Dictionary Encoding](https://facebookincubator.github.io/velox/develop/dictionary-encoding.html)给出constant直接值、dictionary索引/基表与消除多层间接访问的工程原则。这里只借这些原理，不移植其实现、覆盖率或性能数字。已查原32/3B、旧3bit加例外池、8B/64B字典、RGB32预展开及相关失败记录，未在检查范围内发现等价的16B map直接RGB实现；关键词无命中不证明历史完全不存在。

设计原件为[单版设计](../../experiments/tagged-block16-design-v1.md)。其Status仍记录最初静态提案，本正文记录后续普查、授权与实际结果，不回写设计的原始时间边界。唯一只读普查计划SHA为`111d0281b7415e75ad6abcf9f46754c6cfb201a7ffed3c1c32508433b776ae10`；native导出/编译/质量前计划SHA为`ce6384ee8dcdc00516c0c5e324b46a01e31a3dd853065257a71bbe6d8a3ff06b`，冻结源、输入和六角色协议。

## 一次固定普查与实际容量

普查只读冻结a399原M16D16B ROM；不读照片或gold选型，不生成新ROM、计时或扫描参数。全部1048576项map与107707个unique块都使用；230项合法palette RGB互异。恒定unique至多230个，因此删除pool至多3680B，不能期待显著容量收益。理论常驻范围5916048..5919728B，比旧3B固定多约21.45%..21.53%；这个上界在看真实覆盖前已写明。

实际恒定221块，占unique的0.205186%；它们被392293个map引用，占37.41197586%，对应6276688个均匀输入色。unique少不等于引用少，37.41%也不是照片tag率或分支命中率。仅在源层假设每次读数计数时，理想依赖读取数为`3−2f=2.25176048`，不等于缓存周期或速度。其余107486块按原次序稳定压紧。

| 表示 | 文件ROM | model | 常驻capacity | 与旧3B比较 |
|---|---:|---:|---:|---:|
| 同场fast78/80 | 独立编译结构，见原证据 | 已含于右列 | 28046644B | 性能唯一分母 |
| 原32bit字典 | 5918672B | 1056B | 5919728B | +1048576B |
| 原3B字典 | 4870096B | 1056B | 4871152B | 0 |
| 新M16T | 5915136B | 实测1056B | **5916192B** | **+1045040B，+21.45365%** |

M16T实际map4194304B、pool1719776B、头/palette1056B；较原32bit只省3536B。新ROM SHA为`b873b00d5b554c43f930d541c8e11e864dcabb1d9f55ff12c99b89ff35a114de`。不能将ZIP大小或删除常量块数当作主要收益；本项是在明确额外容量后检验依赖削减。

## 实现与质量

独立`experiments/tagged-block16-runtime`提供C99零堆不可变借用API及桌面适配器。LE32条目bit31置位表示低24bit最终RGB，bits30..24必须为零；否则为完整合法16B ID块的payload绝对偏移。允许零pool全常量，常量RGB不必在palette内。完整256槽及count1..256契约保留，非恒定ID严格小于count。显式LE读取不要求ROM对齐、端序或额外padding；不据此宣称已在其它架构执行。

helper改为返回最终RGB32，`read/read_wide/scalar_one`外层移除无条件palette读取。常量先返回再形成fallback地址，未使用blend或masked gather伪装读取削减；仅非恒定分支读pool/palette。AVX2输入、64像素先读后写、NTA/NT/SFENCE、输出布局、OMP粒度及短尾沿用旧3B循环，其余不变。生成器约束外层无残留palette访问。未启用AVX512或`-march=native`。

Windows 11 26200、AMD Ryzen 9 8945HX/AMD64，GCC15.2 `-O3`；C99 `-std=c99 -pedantic-errors -Wall -Wextra`，AVX2 TU `-mavx2 -mtune=skylake -ffp-contract=off`，桌面OMP。Python3.12.14/NumPy1.26.4；环境OMP/NumPy各1线程，native明确1/4线程。root授权质量窗可与tail质量并行，因此质量耗时不作速度声明。

导出独立解释全部序列化map/pool/palette；原逻辑ID摘要仍为`a020c67a…`，RGB32摘要为`29a15ba4…`。纯C99、desktop scalar、AVX2单/四线程各原地/分离共8次完整256³，全部RGB摘要`3c9ce8d9…`与冻结模型相同，精度保留100%；它继承a399相对原滤镜的误差，不是零拟合误差。mean/p99/max及每图输出不变。

另外通过584项有限/非对齐/零长、64项格式/IO拒绝、144项输入与目标双末端图像保护、40项只读ROM加NOACCESS末端保护。ROM五组是实际ROM、最后map强制指最后pool、全常量零pool、全非恒定16B最小pool、混合常量/非恒定lane。最高合法palette ID252..255、直接黑/白/abcdef、常量保留位、非法offset、零pool非恒定引用、部分重叠和失败清零均覆盖；独立字节解释验证期望。全常量最后map结束于ROM末端，不能靠用户padding或存在pool避开错误读取。

实际桌面DLL SHA`56a001549bdc0e42f585c347cf38a993bafd52a960edfe3a578419c0214ea242`，纯C99 DLL SHA`0efe033288155d2fa909a9cc969c288ce3f8da5d1829890c045b286927653fb8`。C99 prepare静态栈1152B、apply64B，AVX入口208B；不是整个进程或OMP线程的总栈。

| 账本 | 峰工作集 | 峰private提交 | 口径 |
|---|---:|---:|---|
| 一次只读普查 | 61882368B | 48398336B | Python/NumPy和普查数组 |
| 单版导出 | 84926464B | 69029888B | Python/NumPy/序列化及独立解码临时 |
| native完整质量 | 93257728B | 79310848B | Python/库/全域分块及合成夹具 |

核心运行时无堆；prepare在栈上验证并复制model，ROM生命周期由调用者保持。以上离线/质量峰值不是纯核心RAM，也不是loader/prepare专属峰值。新进程RSS另按性能协议记录；没有WASM、跨目标或MCU实板成绩。

## 正式性能：预注册一次执行，全部拒绝

六角色为同源fast78/80、原32bit、原3B、新M16T AVX2、新M16T C99桌面OMP；四新worker统一process允许CPU0/2/4/6（0x55），OMP_PROC_BIND=false，清除OMP_PLACES。记录实际mask与native wall外caller前后CPU；不逐OMP线程绑定、不锁频，不把这一新环境与旧unbound绝对时间拼接或当漂移因果实验。

每worker六角色、双接口、1/4线程，轮转及反序，预热1+5完整百图：全轮480正式、96预热、80 A/A，共656条native调用；另6个同import群新进程在照片分配前测RSS。照片固定235929600B/100张，输入输出SHA继承旧证据。速度只按每worker较快78/80耗时除以候选耗时，取四worker最劣分别列100/90/80/70/60/50。A/A逐对0.8..1.25且四worker中位在1/1.1..1.1，失败清空对应六档；不补跑、删worker或用慢控制作分母。

root明确授排他窗后，上述完整方案一次执行结束，未补跑；六个新进程RSS也完成。四组A/A均有效，中位分别为0.998877、0.992072、0.947477、0.935244，所有逐worker比例也在预定范围。以下为全部四worker中最劣相对同场较快78/80的吞吐保留率，不取中位过线：

| 角色 | 原地1线程 | 原地4线程 | 分离1线程 | 分离4线程 | 本场最劣资格 |
|---|---:|---:|---:|---:|---|
| 原32bit | 54.65173% | 75.07383% | 60.85605% | 74.81379% | 本场50/70/60/70；旧有效失败不撤销 |
| 原3B | **46.02728%** | 61.07047% | 61.03613% | 68.36624% | 原地1新增有效反例；其余60 |
| 新M16T AVX2 | **38.85694%** | **40.98871%** | **41.51788%** | **45.44131%** | 四模式全低50，拒绝 |
| 新M16T C99 | **20.18965%** | **26.95445%** | **24.55235%** | **31.06049%** | 四模式全低50，拒绝 |

新tag AVX两种4线程中位约52.75%/51.37%，但最劣worker低50%，不能以中位替换冻结门槛。旧3B原地1的有效46.02728%与此前39.8454%等反例并列；此前八worker通过历史保留，稳健全模式50资格仍已取消。原32bit此次四模式过50也不能覆盖旧有效反例。所有角色比较的是固定a399模型，没有将新精度模型或独立speed85/87容量拼入。

为使100..50衡量线完整可复核，下表仅为这六角色同场容量优选，精度保留均100%；不能称跨场全局最优，也不将旧控制升级为稳健部署。新tag在全部六档均未入围。

| 接口/线程 | 100 | 90 | 80 | 70 | 60 | 50 |
|---|---|---|---|---|---|---|
| 原地1 | 无 | ref80 | ref78 | ref78 | ref78 | 原32bit |
| 原地4 | ref78 | ref78 | ref78 | 原32bit | 原3B | 原3B |
| 分离1 | 无 | ref80 | ref78 | ref78 | 原3B | 原3B |
| 分离4 | 无 | 无 | ref78 | 原32bit | 原3B | 原3B |

同场新tag既没有取得50档，也没有凭较原32bit仅3536B的节省获得可接受速度；四模式全部worker配对慢于原32bit和原3B。37.41%均匀域覆盖、理想依赖读取数下降不能预测真实吞吐，未记录PMU分支/缓存计数，因此不能将失败确定归因于分支失误、L1命中或某种硬件机制。不再扩展tag布局或扫描参数。

独立同import群、照片分配前的新进程峰值如下；包括Python/NumPy、依赖库、流式SHA和模型准备，不是纯核心RAM或prepare专属峰值。

| 角色 | 前置峰工作集 | 准备后峰工作集 | 前置峰private | 准备后峰private |
|---|---:|---:|---:|---:|
| ref78 | 35913728B | 133304320B | 22564864B | 121647104B |
| ref80 | 35876864B | 133337088B | 22597632B | 121704448B |
| 原32bit | 35864576B | 42508288B | 22634496B | 28971008B |
| 原3B | 35840000B | 41611264B | 22528000B | 27820032B |
| 新tag AVX | 35966976B | 42627072B | 22605824B | 28942336B |
| 新tag C99 | 35999744B | 42618880B | 22671360B | 29003776B |

主要复现顺序为`scripts/generate_tagged_block16.py`、`freeze_tagged_block16.py`、`export_tagged_block16.py --output artifacts/p16-tagged-block16-rom-v1`、`build_tagged_block16.py --output artifacts/p16-tagged-block16-build-v1`、`verify_tagged_block16.py --build ... --roms ... --output artifacts/p16-tagged-block16-quality-v1`。构建、质量与性能均已执行一次；不可重运行现存输出目录冒充新独立结果。性能命令为`bench_tagged_block16.py --build artifacts/p16-tagged-block16-build-v1 --roms artifacts/p16-tagged-block16-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --output artifacts/p16-tagged-block16-perf-v1 --repeats 5`。

原件发布在[证据清单](../../report/data/p16-tagged-block16-v1/manifest.json)：含唯一census、export/build/quality/performance、原始测量ZIP、冻结源码/静态栈、原/新ROM和新库。另有[CPU计数](../../report/data/p16-tagged-block16-v1/cpu-records-summary.json)、[同场旧/新配对](../../report/data/p16-tagged-block16-v1/layout-pairs.json)、[环境说明](../../report/data/p16-tagged-block16-v1/environment-note.json)；[离线审计](../../report/data/p16-tagged-block16-v1/git-byte-audit.json)重建全部RGB、656调用、A/A及六档，并核暂存原字节/ZIP CRC。本阶段提交可由本文件Git历史定位，不在提交内容内自填循环HEAD。

本阶段没有部署推荐，跨场内存前沿不纳入新M16T；纯C99实际速度拒绝，也不追加WASM或实板验证去模糊速度门槛。默认和旧原件保持，阶段结果供Draft PR审阅，不是赛事许可或目标实机的最终结论。
