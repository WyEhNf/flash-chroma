# 当前宽palette模型的完整RGB24输出表：静态方案

Agent：`/root`；Operator：16题用户；Status：预注册，尚未生成实现、构建或运行。三个研究分支保持独立，本方案属于精度分支的精确运行时，不修改LUT数学或拟合。

## 已有证据与本次差别

历史26、44已经做过64MiB完整RGB32表；44对当时40的u8表减少指令但增加实测周期，已停止。53的RGB32输入tile也失败。不能将完整RGB表称为新机制，不能将旧分母结果当本轮87分母上的资格。本轮287/288完整u16、289 packed10与290/291热点miss回算有完整反例或AA缺口，三个新宽palette模型仍缺可靠运行时。

本次只做一个固定版本：完整RGB24输出紧密存储，每输入码直接加载其三个RGB字节；复用288/87实际四套IO/ILP/ANDN/stream框架。这样移除palette依赖载入，也避免291整8lane回算；物理表48MiB而非历史RGB32的64MiB。增加的3倍地址计算、非对齐4B载入和更大工作集仍可能使速度低于50%，不预称改善。先不实现RGB32平行变体或参数扫描。

## 格式、构建与范围合同

内部输入code为R|(G<<8)|(B<<16)。位置3*code顺序存R/G/B，uint8数组对象，逻辑50331648B；显式4B零guard使最末4B读取合法，实际50331652B。像素helper用memcpy读取4B后仅取低24位，不依赖uint32对齐或别名，不把ROM guard当外部输入/输出越界许可。scalar只读写合法RGB24；AVX2只作用x86，标准整数四级fallback保留。所有256bit返回只允许同TU always_inline，不引入跨noinline向量返回。

新format18、revision292，96B诊断含value_bytes=3、palette_bytes=0、logical_inputs=16777216、raw_words=12582913、guard=4、真实guaranteed_alignment=1与实际mod64。旧<=255色直接表和既有启用的compact palette路径继续优先，宽表仅在四级cache域已证明、AVX2可用且旧路径未启用时建立；无palette色数上限假设。临时峰、vector capacity和fallback所有旧字段都计入真实model_bytes，保留缓存，不把48MiB叫完整总RAM。

编译器只从纯模型首级整数Q16 tetra与既有suffix cache生成每个RGB值，不能读取gold、照片或oracle来prepare。每个8像素写恰24B，禁止32B vector写跨块造成并行数据竞争；固定256个65536输入块，最多4worker。整体只分配48MiB表加guard，不分配64MiB中转。OOM保留旧精确fallback；OOM和无AVX2未注入前只注明未覆盖。

## 先质量、后性能

冻结源、实际编译器依赖、工具链、模型与独立oracle SHA后只执行一次。有限合同包括首末输入码、末color/guard、24B恰长src/dst NOACCESS、原地与分离、1/7/8/9/31/32/39/40/64/71/72/73/4095/4096/4097/65535/65536/65537长度和四套kernel mode；编译输出用覆盖RGB高bit、0/255/256/65535/65536/0xffffff的完整RGB值，避免把色值当u16 ID截断。table物理字节与旧288同模型解码逐项一致，但原oracle另验，不以新表自证正确。

对象固定max_first、p99_first、max48、综合best与87综合best控制。主质量scalar1/AVX1/请求AVX4×in/to共30完整16M流；请求4T分块不冒充实际并行覆盖，另10个whole16M调用和20个前后同libgomp四成员只读快照。4新模型×100图×in/to共800实际输出，972短长/模式/backend合同，旧outplace拒绝、诊断大小/NULL/状态拒绝；synthetic旧8优先、宽表、单级和资格失败完整fallback分列。首错STOP，不覆盖失败目录或源码。

若完整质量通过，再冻结正式性能。至少87a399、87综合best、新wrapper综合best、三个宽模型及288同模型辅助；必须固定100已见照片同场四fresh worker、ABBA/BAAB、所有实际输出SHA、0.85..1.15 AA与独立Decimal。三个主分母全部四模式过门才能授100/90/80/70/60/50档；任一稳定必需场景<50直接拒绝。不能从288较慢分母救资格，不能删除失效轮重采。峰RSS独立fresh进程，table48MiB总账如实披露。

除四模式稳态门，还须另固定create→首个完整100图Out4的两阶段冷首组，每角色每阶段5个新句柄，角色顺序镜像；每次包含正常文件解析、验证、全部cache与直接表准备。该端到端边界也须对三个主分母满足同AA和最低50%，才能称100图从创建开始的整体时间资格。prepare独立耗时仍分列；OS文件cache已暖，不称进程/磁盘真冷。只过稳态的方案可列局部结果，不能升级为整体50%通过。

本阶段不证明官方单图硬阈值、官方Intel机器速度、未见数据或任意RGB分布的最劣速度；官方派生cache允许边界仍未取得新规则正文。失败也应中文阶段报告、原字节/ZIP/HEAD审计后挂到现有Draft PR #90，不替换已合格综合best。

## 资料与可审查的代价假设

Intel 的[Memory Layout Transformations](https://www.intel.com/content/www/us/en/developer/articles/technical/memory-layout-transformations.html)强调间接gather的延迟/带宽和布局转换的局部性/TLB取舍。这只支持同时考察访问链与工作集的研究方法，不能推断本代码会加速，也不能把AoS/SoA一般结论直接套成本表结果。本方案是根据已有失败提出的待实测假设。

可直接由地址算式推得：在完整均匀输入码上，3*code模64覆盖全部余数，4B读取有3/64跨64B线；模4096同理有3/4096跨4KiB页。这是地址几何，非cache miss或PMU测量，照片分布也不保证均匀。相对于32bit对齐表减少四分之一payload，同时引入这些分裂读取及3倍地址乘法，正式验收必须允许它失败，不能只凭少一次palette访问宣称优越。
