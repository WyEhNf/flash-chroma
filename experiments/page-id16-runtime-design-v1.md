# 固定4KiB、LE16页ID的单版可移植ROM：静态预注册

Agent：`/root/memory`；Operator：16题用户；Status：静态设计，尚未AST/冻结/导出/构建/质量/性能。root291正式窗口内仅写此协议与源，原alias三次STOP、原M16D/Model/DLL不改。

## 机制与停止条件

只复用原固定4096个4KiB逻辑页、3082个unique页和已封存pageID，不重普查、不按gold/照片选参数，不改页尺寸、排序或编码位宽。输入内部code仍为R|(G<<8)|(B<<16)，page=code>>12、offset=code&4095；LE16读取pageID，然后取pool[pageID*4096+offset]得到原8bit palette ID，再LE读取RGB32，输出三字节。保持全部256合法palette槽，没有有损近似、packed12或Windows映射要求。

这是三级串依赖；8192B地图小于旧16B字典地图，但pool较大，不能预称缓存命中改善或速度提高。原线性表的单次ID载入变为pageID→pool byte，性能假设可能失败。alias真实映射不作为本C99速度证据。当前固定a399的全局palette可表示，不能把该格式外推到超过256输出色的一般模型。

一次唯一导出/实现/质量；任何身份、guard、范围、生命周期不符STOP保留，不修后重采同阶段。实际文件加实际Model须比16779328B至少少1MiB，否则按无收益停止。完整质量通过才另冻结同场速度计划；任何有效模式低50或AA无效都如实拒绝/清档，不通过慢对照分母授档。

## 唯一序列化与容量界

所有整数均LE，无packed C结构或host uint32对齐假设。32B头为magic P4ID，后7个LE32依次version=1、page_shift=12、palette_count=1..256、logical_ID_count=16777216、unique_pages=1..4096、reserved=0、reserved=0。1056B前缀包含32B头及固定256×RGB32；合法RGB32最高字节为0，未用palette槽必须为0。

|区域|固定offset|长度/条件|
|---|---:|---|
|头|0|32B|
|palette|32|1024B，全部256槽|
|LE16 pageID|1056|8192B，4096项，逐项<unique_pages|
|pool|9248|unique_pages×4096B，逐字节<palette_count|
|显式末guard|9248+unique_pages×4096|4B，全0，计入文件|

固定实际源应为3082个pool页：文件投影32+1024+8192+12623872+4=12633124B。x64借用Model为5个自然word（blob指针、size_t blob_bytes、page_ids指针、pool指针、palette指针），投影40B，合计12633164B，较原16779328B投影少4146164B；wasm32投影20B。均待真实sizeof/导出，不写成实测，Python/loader/OS/RSS另列。

导出只消费封存support和现有alias容器的固定pool，不重新判unique。验证已有alias文件SHA与pool/原ID摘要后把4096项LE32改写为LE16，按原顺序流式复制pool和原palette，追加4B guard；原blob/DLL不重建。temporary预算以实际峰记录，不把传输ZIP压缩率当常驻。

唯一AVX2实现复用旧已合格1024B LE16的四包独立标量读取与pack/stream输出框架，lookup仅改为LE16页ID→pool byte→借ROM RGB32 memcpy；不实现或扫描硬件gather变体。palette完整32bit读取末项不越界。C99只读精确2B/1B/3B或4B LE序列，不依赖padding；4B显式guard仍计入格式并验证全0，不允许放宽任何外部source/dst长度。AVX2只在x86使用native memcpy32作为LE值，不增加AVX512/native ISA；BE声明只给C99路径。该静态选择基于既有实现，不能当性能证据。

## 借用API、零堆与范围

独立jshc_p4_* API与新Model，不能调用旧1056B ABI的prepare。prepare验证整个头、大小/乘加溢出、每个pageID、全部palette与pool字节、4B guard；仅成功后填5个借用字段。输入blob不可变且寿命长于所有apply，不得与close并发。关闭时显式清零Model，零Model必须被拒绝；Windows质量可复用原只读FileView的映射与models清零列表，但不调用其旧Model prepare，原loader源保持。

纯C99无堆、C++/OMP/SIMD；小端用字节移位，写出用显式RGB字节或memcpy已序列化字节，BE不能把host uint32裸存当LE。8像素批处理先读全本批RGB再写，前7个4B重叠写、末个3B，短尾逐像素精确读写；只声明静态局部数组，实际.su和完整运行栈边界另测，不把零堆叫零RAM。

prepare目标Model与blob重叠时无写拒绝，避免向只读ROM写零；其它prepare失败清零Model。apply先核Model/字段布局、n×3溢出、指针范围、source/dst仅可完全同址或不相交、与Model/ROM重叠拒绝，然后才写。n=0允许NULL输入输出但要求有效Model；无效Model/参数失败不写输出。

## 完整质量的预留单版门

先冻结全部源/协议/输入后才导出/构建。独立uint64 oracle直接按原a020逻辑ID和RGB32，不复用新lookup；完整外部R高位枚举输出SHA须为3c9ce8d9…，100图逐图及串联须为原f3c0d907…，原精度并非误差0，仅输出100%等价。

九个完整域/百图/guard模式明确为：standalone C99 core分离1T；OMP适配器C99的1/4T×原地/分离四模式；AVX2的1/4T×原地/分离四模式。standalone core另做同址有限/尾部/拒绝，不能把wrapper通过代替独立core库。首次任何错误STOP，未覆盖模式不能补称通过。

有限长度0、1、7、8、9、31、32、40、64、72、73、405、406、1023、1024、1025、4095、4096、4097、65535、65536、65537；输入/输出偏移0/1/3/7、ROM偏移0..7、首末及跨4KiB边界。source/dst均放字节精确NOACCESS尾guard；ROM含actual/count1/count256/max4096页固定夹具，首末pageID、全部256palette、末ID255、最后pool字节及最后map跨读均覆盖；map值4096或65535必须拒绝，不能把16bit可编码当合法范围。畸形头、尺寸/offset、guard非零、palette高字节/unused、ID越界、NULL/部分重叠/uintptr及n×3溢出、Model/ROM生命周期均验。

实际ABI/file/required metadata、prepare临时和导出峰、逐图片scratch、C99/AVX函数.su及fresh进程Private/WS/峰分列。同imports同场才能比较绝对RSS，原alias nonpaged/WS不移植为新点结果。

## 平台与性能分层

标准C99先在本机standalone及AVX/OMP库验；若本机有效速度至少50才申请WASM/Node全域实际运行，模块imports/内存夹具与核心ROM/Model分列。Cortex-M3、RV32和AArch64BE仅编译对象作为后续独立门，不冒充实板或仿真运行；原格式WASM已过不能自动继承。

未来同场至少fast78/80、原linear AVX/C99、新P4 AVX/C99；原1024B字典可以另列合格历史控制但不是主分母。4新worker、0x55允许集、完整100图5轮、全部输出SHA与A/A、每模式最劣的100/90/80/70/60/50独立门沿用；正式角色/调用数/冻结SHA待质量完成另授，不现在运行或把投影授档。
