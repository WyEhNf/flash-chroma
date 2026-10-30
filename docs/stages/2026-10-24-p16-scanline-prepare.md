# 第16题速度研究：固定枚举扫描线准备器（修订100）

Agent：`/root/speed`。工作分支：`codex/p16-speed-20261023`。父实现为97，未叠加99。唯一构建、私有有限合同、新增完整质量与正式性能已完成。两条固定链N100的创建至首批输出连续wall，相对97有受控窄收益；全场49/126项AA有效，未授予全场50%资格。

## 问题与机制

已有87/95/97完整direct构造按`code=begin+p`枚举RGB8，R为最低8位；每8输入不跨256像素R行。旧compile仍借用任意输入transform，各lane从轴表gather。94只按共享坐标分派，未利用固定枚举的R连续和G/B常量。检查相关源、阶段文档及原repo只读cost-split诊断，未在该范围发现等价扫描线实现；不声称整个仓库或业界没有类似实现。

新私有入口只接受64K对齐的完整B批，将循环写成G行×R八码。R轴用loadu，G坐标每行读取，B每批读取；shared复用一套四面体几何，nonshared仍各channel独立分数、排序和权重。轴packed17bit、65536端点、节点、首级单次RGB8舍入、ID和palette身份全部保持。只有合法完整B批走新核，其他合法范围回原97入口。

公开ABI、Handle成员、默认策略、2²⁶工作量门、原domain证明、256批OpenMP分块不变。构造器的新direct_index与只读轴/节点/cache/ids各有独立所有权，批目的范围不相交；不扩张私有入口对故意输入/输出别名的合同。普通默认和低hint仍cached；共享高hint以及a399原非共享direct才使用新prepare。

## 实际构建及成本

Windows x64、GCC15.2、Release、C++17，唯一`-j1`构建，AVX2/`-mtune=skylake -ffp-contract=off`，旧BMI对象原参数。生产冻结`e7c2366010e1b9876f1a386c8405568eea853f81bbdcbb7d7d54fb574439793f`，202来源。

生产DLL SHA为`a11eac986485f89af0c602e86f57b271f055c41641b9cdfe96d120eb4366e2e1`，私有EXE为`3cb6d038cb477ca718cfa4a71113947910697a10de204d8c928615add97f0265`。八个旧prepare/checked/direct/bench对象逐字节同97，包含原compile_shared对象`3ee52f4f…`。新包装器仅私有prepare调用名及revision有变化；旧95/97/99已执行源未改。

实际新object只有一个void入口，外部符号仅旧void fallback，无call指令、无aligned YMM rsp存储；R确实为vmovdqu，G/B用广播。shared/nonshared内环各5/9条gather，分别含4/8节点和1个ID gather。这不是“八角变四角”：旧shared本来已经四节点。

实际`.su`静态栈帧704B，旧97 prepare为512B，增加192B并存在spill；新核没有新增持久表或owner，不代表CRT/RSS没有变化。不能由gather减少或旧对象相同推出计时收益。内部向量helper强制inline，跨TU全部void，未引入已证的Win64 hidden-YMM-return临时区对齐故障形式。

## 唯一有限合同

固定m17/18/25/33，分别shared同指针、shared相等异指针、nonshared各channel分数，共12 Views。轴地址mod32=4，保留0/1/16384/32768/65535/65536、不等距单调分界及正负节点梯度。独立uint64 oracle按每channel四项凸权重求首级RGB，再查固定18,513词ID域；没有读取gold、照片或完整输出拟合。

完整B批仅固定0/127/255三批，并有八个合法fallback。新入口792次、旧97显式参考132次，924个显式私有调用、924组输出哨兵和924次输入只读比较全部通过；独立oracle与旧97各2,363,136像素，新入口含六种目的偏移共14,178,816像素。576次候选fallback内部还进入旧97，若按含嵌套函数进入计数为1500；924不是这一嵌套口径。108个轴地址均核mod32=4，生成坐标中0/65536各5403/2705。

有限执行计划SHA为`03946c1a2d3efdf67771ea5cf2e13a4c5178bd5d8afabcd14bd5ed5d5831fbfa`，结果SHA为`eea1dde0e5dd9c70fede5348682d48ef3ff8e3d7da663ec4f95d78758cbdf529`。原静态提案的256个B批是未执行设想，本次有限通过仅三批；完整输入域覆盖来自下一项新增整链质量。

## 新增完整质量

质量计划SHA为`a098d3bdff6587491c083bc2595cf53d3e47003b4c769951cfb2a5c25e98873a`，212来源。只测试100新增/变更；消费旧已认证ordinary/a399 cube和99已认证照片前缀，不重复旧99私有native或旧reference全域。

ordinary默认/高hint及a399默认/高hint共四实例，每个100新实例AVX1/4、真实分离1/4，合计16条完整16M流、1024分块调用，逐块对独立cube原件0差。两独立流SHA分别为ordinary `78ebea523d67db084c045369697a8dd3b906b37e35517d6cf52c3fd7349a096f`、a399 `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。

14对实模型构造与97实际比较ID/palette/cache逐字节、domain/direct/cache诊断与model_bytes一致。结果14行保存表hash/条目/bytes；完整诊断值保存在10个finite hint状态中，其余4对通过已冻结`equal_tables`的完整诊断/容量断言，不能称14对全schema原样导出。

五unsigned hint（0、阈值−1、恰阈值、阈值+1、UINT64_MAX）下10080有限比较、110无效分离拒绝、10合法空调用通过；10 Python类型拒绝、10 native无效create拒绝通过。高hint新增八种独立uint64/资格fallback合同，64个100后端比较通过。N1/10/85/86/100×两模型×1/4线程×原地/真分离，40个100实际输出SHA对99已认证前缀全通过；照片源前后SHA保持。

新增质量结果SHA为`7c5ac4e334951f80e68e2cf055bebcd6f8e204219883867efa31081b17c66d0e`，独立离线身份/计数/流SHA审计通过，没有再次调用native。该阶段只证明固定模型和合同的输出一致，未做OOM或无AVX2硬件故障注入，未证明速度/精度方案综合升级。

## 正式计时与门槛

正式计划`bd51bee8e992d46e26fb6b2678d44f5b24c81255643b85d52b8eab4c189b5936`，driver `f31a6897a2f38e2f99638717127f8b87f37920a29f0540bb3260c33b68c4209a`，audit `9853d0e3cd0f4d5f9e6cb544461c4de0add203e627d0c8589cb96b51169192ba`。经root唯一排他授权，四worker与16独立RSS全部exit0，2112组实际caller-owned输出SHA全部通过。正式前唯一预检核226项源/库身份，0.5秒相关进程观察未发现非self超过0.1CPU秒；这不证明宿主绝对独占，未知PID未杀。

四角色87/95/97/100，N1真默认/N10低hint/N100高hint；每角色冷5正式+5 AA交错，热warm2+63/16/9与同长AA，in/out1/4，四个镜像角色序。Windows进程允许集合为0/2/4/6，不是逐OpenMP线程绑定。输入SHA、work填充和输出SHA在计时外；native create实际文件读取/解析/校验/cache/direct、首out4与create至首输出连续wall全部保留。冷指新句柄，未宣称磁盘冷或新进程冷。

float独立审计通过384热记录、96冷记录、2112 SHA和16RSS；50位Decimal逐项复算126统计集、1764标量，最大绝对差`7.580903401096501867934598030178061E-16`，低于1e-14，全部AA/最劣/六档/无明显退化判定一致。正式结果SHA为`c6cdcc0bf3913b6d668672d9cfffb9cada473b18a23f7d5f44eb010d688c116c`。没有补测、改阈值或删除慢轮。

N100创建至首批真实分离输出的连续wall，两模型对三分母六项AA均有效，并符合预设无明显退化门。时间比小于1较快；最劣吞吐为四worker最大时间比的倒数，不是median倒数。

|固定模型|分母|连续wall中位时间比|最劣吞吐保留|AA与门|
|---|---|---:|---:|---|
|ordinary|87|0.387714|245.4284%|有效，100档|
|ordinary|95|0.888830|109.8981%|有效，100档|
|ordinary|97|0.915907|107.1990%|有效，100档|
|a399|87|0.708873|128.0944%|有效，100档|
|a399|95|0.748491|113.4583%|有效，100档|
|a399|97|0.778191|118.2879%|有效，100档|

上述相对97的连续wall中位时间分别下降8.4093%与22.1809%，是完整新句柄+首100图作业收益，不能改称热像素提速。ordinary对87还包含原显式高hint direct生命周期与cached路径差异，不能把全部245%吞吐归为本次扫描线机制。

单独prepare的证据更窄：ordinary N100对95 AA有效，中位时间比0.811177、最劣吞吐121.9577%；对97中位0.826264、最劣118.7771%但AA失效，不能确证这项prepare加速。a399各N对三分母所有单独prepare AA失效，虽中位时间比约0.59..0.70，不宣称受控prepare成功。ordinary N100对87单prepare描述中位比3.277290、最劣27.7555%，AA同样失效；高准备成本原件保留，不能使用95/97分母掩盖或授予87的该项门。

全场统计边界如下。失效项不授档，不能因为有效项未低50而称所有路径合格。

|分母|统计项|AA有效/失效|有效项最劣吞吐|有效低50数|全场50|
|---|---:|---:|---:|---:|---|
|87|42|17/25|74.9643%|0|未证明|
|95|42|16/26|82.8125%|0|未证明|
|97|42|16/26|85.6148%|0|未证明|

三分母有效最劣分别发生在a399 N10热apply、a399 N1首out4、a399 N1热apply。即使旧像素对象字节相同，本次有效结果仍存在低于100档的代价；不能以相同对象推定速度保持。所有热/冷/首组字段、每worker比值、AA和100/90/80/70/60/50门均应随完整126行表提供；未测N86不授性能档。

## 内存与边界

100对97实际账单保持：ordinary N1为1,852,824B，N100为18,630,040B；a399两N均18,579,204B。100没有新增owner或持久表，704B静态帧代价仍存在。独立新进程的RSS差是描述性单次快照，不授予内存改善：

|模型/N|97 RSS增量|100 RSS增量|100构造后RSS|
|---|---:|---:|---:|
|ordinary/1|2,392,064|2,342,912|73,056,256|
|ordinary/100|20,082,688|20,090,880|90,812,416|
|a399/1|20,017,152|20,054,016|90,697,728|
|a399/100|20,037,632|20,029,440|90,443,776|

各进程基线、构造后RSS及peak_wset都保留，不由单次差值推断allocator真实保留或统计内存优势。精度方面本单版保持固定模型逐位输出，不是新的拟合方案。OOM/noAVX2硬件未注入，其他机器/编译器尚未验证。

## 交付与后续

主要实现为`experiments/p16-scanline-prepare-runtime/compile_scanline_avx2.cpp`及独立包装器；固定有限/正式合同在同前缀预注册文件，生成、构建、质量、离线审计脚本为`scripts/*p16_scanline*.py`。本阶段基于提交`58b244c1712b12d69c8851529428258269bf338a`独立增量交付，由root统一更新Draft PR89，不自行推送或合并。

原件保存于[阶段证据目录](../../report/data/p16-scanline-prepare-v1/identity.json)，含[全部126门槛](../../report/data/p16-scanline-prepare-v1/all-grades.csv)、[完整汇总](../../report/data/p16-scanline-prepare-v1/summary.json)、[正式float复算](../../report/data/p16-scanline-prepare-v1/offline-audit.json)、[Decimal复算](../../report/data/p16-scanline-prepare-v1/decimal-audit.json)和[新增质量复算](../../report/data/p16-scanline-prepare-v1/quality-offline-audit.json)。49份raw、220份执行/事后源、63份构建元数据、23份自有构建产品、6份固定模型输入共361个ZIP成员逐个SHA回读通过，所有worker/partial/失效AA均保留。新101静态草稿未混入100归档或提交。

五ZIP为只存储不压缩，保留实际字节；外部MinGW依赖、原已认证cube和100照片未复制，原计划绑定路径及SHA，离线复现仍需要这些外部原件。`.gitattributes`与本阶段正文沿既有text规则归一LF，其余执行源/raw/ZIP按原字节做增量index/HEAD核对；不借阶段封存宣称全历史HEAD重新验收。

后续只静态检查实际704B帧与spill的活跃区间，先区分源码期望与GCC机器码，不立即构建另一版本，不借本次窄N100收益宣称所有路径提速。
