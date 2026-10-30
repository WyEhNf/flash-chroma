# 固定16B块的直接RGB常量tag：单版可证伪设计

Agent：`/root/memory`；Operator：当前16题用户；Status：Proposed，仅静态。当前不导出、统计、构建、质量、计时、ZIP或Git；root另授数值窗后只做一次固定ROM普查，是否实施由证据再决定。默认、旧32bit/3B原件及原a399模型保持。

## 查重与已有负例

已读现有16B LE24 map的`lookup_id`、`read/read_wide/scalar_one`和输出循环、原32bit字典、修订23的3bit加例外池、8B字典、64B字典及双表示分派。旧23按低8位255分支选择完整ID例外池，所有lane最终仍查palette；8B/64B字典也不是常量entry直接携带最终RGB。此前64像素ID先行仍重读栈并查palette；它不是此次静态map条目tag。未在上述源、阶段文档及全实验C/C++的`0x80000000/is_constant/constant_block`检索发现等价实现，不能由关键词无命中证明整个历史完全不存在同类代码。

最近RGB32预展开把所有pool像素扩大为4B，移除palette依赖但常驻10039040B、被同场旧3B支配；LE16 1024B块虽缩小map，省32KiB却三个有效模式均慢。本设计保持16B ID pool，不全体预展开；只对确认恒定的块直接返回RGB32，非恒定仍三层读取。它可能被tag测试/分支、宽map与混合输入抵消，不能引用旧方案的最好速度推定通过。

## 主资料启发及不能推导的结论

[Pekhimenko等BDI原论文（PACT2012）](https://users.ece.cmu.edu/~omutlu/pub/bdi-compression_pact12.pdf)把重复值视作可单独处理的压缩模式，并强调解压在访问关键路径上，容量与解码延迟应同时评价。这是硬件缓存压缩研究，本方案只借“重复值直接表示、不要用压缩率代替访问成本”的原理，不移植其算法或使用其性能数字，更不由多媒体常见重复值推断本模型覆盖率。

[Velox官方Vectors文档](https://facebookincubator.github.io/velox/develop/vectors.html)将标量constant直接保存value，而dictionary保存indices与base；[官方Dictionary Encoding](https://facebookincubator.github.io/velox/develop/dictionary-encoding.html)说明多层字典访问的开销，并为constant/flat提供单独路径。这里只借“运行时表示允许直接值与索引分开、合适时消除间接层”的工程原则，不引入Velox依赖，不套用数据库吞吐。ART原文抓取超时，没有把未读内容当依据。

## 容量先验上界：unique不等于覆盖

固定源M16D16B字典含1048576个map条目、107707个唯一16B ID块，合法palette230色。若这230项RGB互异，恒定unique块至多230个，删除它们至多省3680B。LE32 map比原LE24 map固定多1048576B，因此不能期待明显压小容量：

`新常驻 = 1056头/palette + 4194304 map + 16×非恒定unique数 + 1056 model`

在上述互异条件下，新常驻在5916048..5919728B之间；原32bit为5919728B，旧3B为4871152B，所以新表示比3B多21.4507%..21.5262%，而只可能比原32bit略小。该条件及数值须在一次普查中实际核对，不能把理论界当作已生成ROM。

真正未知的是少数恒定unique块在1048576项map中的引用次数。必须同时报告恒定unique占比、map引用加权覆盖率、对应全16777216输入数及每个恒定值的引用频数；不能用unique占比猜热路径，更不能默认常量占多数。普查只用该ROM，不读gold/照片选型；全域均匀覆盖不等于照片命中或分支可预测性。

## 唯一格式与执行路径

提案M16T v1，1056B头和完整256槽LE RGB32 palette，固定16B块；1048576项LE32条目：bit31为1表示常量，bits30..24必须0，低24bit是最终RGB。bit31为0是非恒定pool的绝对payload字节偏移，须16B对齐、位于map之后且整块合法。删除恒定unique块后，其余块按原顺序稳定压紧，字节内容不改；这里“原pool”指原ID块内容，不保证旧绝对偏移。没有扫描阈值、块宽、tag布局或排序。

payload不得超过2³¹字节，保证合法非恒定偏移不占tag。允许pool为零：全常量ROM只有map；如果没有pool却出现非恒定条目，prepare拒绝。palette count1..256全部保持，非恒定pool ID须小于count。常量低24bit可表示任意RGB，不受230色条件限制；导出对源模型逐字节证明等价。model仍1056B，C99显式LE32、零堆、不要求对齐/端序或用户padding，借用生命周期及所有失败/重叠契约保持。

必须把调用层从“helper返回ID后无条件palette”改为“helper返回最终RGB32”：

```c
uint32_t word = le32(table + 4*(code >> 4));
if (word & UINT32_C(0x80000000)) return word & UINT32_C(0x00ffffff);
return palette[table[word + (code & 15)]];
```

这一版使用普通条件提前返回，不加likely、branchless备用或masked gather。AVX2沿原32/3B的独立标量读取与既有AVX输出布局，只改变helper及值装配，`read/read_wide/scalar_one`均接最终RGB，删除外层无条件palette访问。宽循环仍先读全64输入后写，NTA/NT/SFENCE/OMP块/短尾保持。常量分支必须在源与对象中确实绕过pool和palette；不能用blend假装消除已发生的读取，也不能把带tag字当fallback地址。混合lane逐项条件读取，全常量pool零夹具必须成立。

全域均匀引用下，理想逻辑依赖读取数由3变为`3−2f`（f为map加权tag率），只是源层读取次数，不是缓存访问周期或可预测速度。非恒定项没有减少层数；宽map增加工作集，分支也有代价，必须接收负结果。

## 唯一普查与后续决定

数值窗仅执行一次：冻结普查脚本/计划、校源ROM SHA，解析头/map/pool，验证原palette互异条件及全部原map，重建16MiB逻辑ID SHA，按最终RGB判断每块是否恒定。报告unique与加权map覆盖、原/新投影字节、相对32/3B增加、离线峰值及静态依赖读取上界。不写新ROM、不构建、不中途看照片/计时来改参数。若无tag覆盖则此机制没有消除依赖的空间；覆盖非零也不等于值得实施。root依据该单次普查决定是否进入唯一native版本，不能把未实现的投影容量当已部署收益。

若进入native，导出后独立按序列化word、pool和palette重建完整RGB流；C99、desktop scalar、AVX1/4各原地/分离8配置完整256³，mean/p99/max和逐图字节不变。有限/拒绝/非对齐/输入及输出双末端保护页、真实与强制最后map→最后pool另验；正向包括count256最高ID252..255、全常量无pool、全非恒定最小pool和混合tag、直接RGB000000/ffffff及其它高值，全部紧贴ROM保护页。全常量最后map的4B字结束于真实ROM末端，须确保不执行fallback读取。

性能再独立冻结并等root排他窗：六角色fast78/80、旧32bit16B、旧3B16B、新tag AVX2、新tag C99，所有角色同一process0x55允许集0/2/4/6，记录实际mask与native wall外caller CPU；非逐OMP线程绑定，未锁频，不作旧unbound归因。四worker轮转/反序，每接口1/4线程预热1+5完整百图；分母仅每worker较快78/80，旧32/3B只作配对，最劣按100/90/80/70/60/50。四模式若有效低50则拒绝整体；A/A失效清空对应六档，不补跑/选worker。完整保留旧3B有效反例，不能以本次较好场次恢复。

实际ROM+model capacity、离线临时、C99静态栈、准备/loader可见账本和独立RSS分列；零堆核心不等于零ROM/RAM，ZIP不当常驻，RSS含相同Python/NumPy/库及流式SHA。当前只有静态设计与主资料，没有任何普查/实现/质量/性能结论。
