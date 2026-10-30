# Native页指针：独立WASM32功能验证静态协议

Agent：`/root/memory`。状态：**只有纯文本方案**，没有AST、哈希、编译、链接、实例化、native调用或计时。Windows速度资格独立；旧linear/store WASM通过只是工具流程参考，不是本候选的通过结论。原P4 ROM、全部旧源、唯一新native-pages C99源和Windows对象/DLL保持。

## 唯一验证对象与工具闭包

只编译原`experiments/page-id16-runtime/page_id16.c`和已冻结`experiments/page-id16-native-pages-runtime/page_native_pages.c`，保留原各自头及internal头。独立wrapper仅导出布局、固定测试缓冲地址和新`jshc_p4_pages_*`入口调用，不包含旧M16D的1056B Model调用、不调用旧P4 apply替代新核；不编C++/OMP/AVX、无WASI、Emscripten或宿主allocator。运行时实际调用表需逐项记录新export名，旧符号存在也不计为新路径覆盖。

拟沿既有`verify_memory_rom_wasm.py`及`verify_memory_rom_store_portability.py`流程，用同路径`C:/Program Files/LLVM/bin/clang.exe`、其配套wasm-ld和`C:/Program Files/nodejs/node.exe`。当前未读取新版本或哈希；另获授权后先解析实际路径，记录Clang/链接器/Node可执行文件SHA、完整版本/Node process.versions、Python驱动版本，冻结后唯一串行构建。路径不可用或版本与所冻结记录不同就STOP，不自动换WSL/浏览器/工具版本补试。

拟固定Clang参数为`--target=wasm32 -std=c99 -O3 -pedantic-errors -ffreestanding -fno-builtin -fno-vectorize -fno-slp-vectorize -fstack-usage`，只含本阶段明确的string头路径；各TU先生成WASM对象，分别保存命令、日志、对象长度/SHA、符号与target_features，再链接。最终模块`--no-entry --export-all`、固定initial=max=64MiB、线性栈64KiB，不增长内存。具体compiler/linker命令及source/input闭包必须在执行前完整冻结；不能边失败边加flag或换工具。

标准字符串shim固定复用既有`experiments/memory-rom-store-portability/include/string.h`和`minilib.c`以及其实际include的`experiments/memory-rom-wasm/minilib.c`原字节。它只提供memcpy/memset/memcmp字节循环，无堆、I/O、时间、OS或模型逻辑；memcpy标准声明中的restrict只属于libc函数原合同，不给新像素核增加restrict。核心仍调用标准语义；shim不是新RGB算法。若新构建另需compiler-rt/其它libc符号或imports，首次失败STOP，先解释缺失，不扩shim后重采。

用`WebAssembly.Module.imports`实际断言空数组，记录完整exports、模块SHA、内存实际bytes/max、WASM对象身份及链接对象清单；不能只凭编译参数宣称零imports。新四个layout getter及wrapper offsetof getter必须实际读取，所有后续地址按实测布局计算。

## 32位ABI与完整容量

以下仍是**预期**，必须由新wasm32模块真实sizeof/offsetof/对齐读回；任何不符保存STOP，不将投影改名实测：

| 部分 | wasm32预期B |
| --- | ---: |
| 原P4 ROM，固定SHA a953eef0… | 12633124 |
| 旧base sizeof | 20 |
| 新view sizeof，pages offset | 24 / 20 |
| native pointer sizeof/保守对齐 | 4 / 4 |
| caller槽表4096项 | 16384 |
| ROM+caller槽表+新view完整capacity | 12649532 |

相比原P4 wasm32投影ROM+20B base，新表示多16388B。这个32位账本不能拿Windows的48B view/32768B槽表套用，也不包含代码、shim、wrapper测试缓冲、64MiB VM内存、Node/V8和宿主参考数据。64MiB是固定**测试夹具预算**，不是核心RAM；各函数`.su`是静态帧，不能把线性栈上限或V8栈当成实际函数峰。

WASM32在同一线性内存中使用本机32位pointer；指针缓存不能从Windows x64序列化复制。prepare必须在WASM内从原LE16 map重新生成全部4096槽。Node若检查pointer对象表示，用DataView的显式LE u32读取；RGB仍原字节memcpy4，serialized字段仍显式LE。WASM32实际运行不能当作大端或Harvard flash实机证明。

地址输入明确按uint32 bit pattern传给WASM i32，输出地址按`>>>0`解释；本夹具有效对象低于64MiB，不靠JS浮点表达超过53位整数。UINTPTR_MAX=0xffffffff、view/cache/blob数值跨度溢出和pixels×3溢出用32位边界构造，不能沿用Windows的UINT64_MAX或view+40/47。Model与表要求实测4B对齐，ROM偏移0..7保持合法；view尾字段为+20/+23、槽尾为+16383。

## 内存布局与guard边界

wrapper只用静态低区：最大4096页夹具ROM所需16786468+8B，输入/输出各完整一张1024×768×3+32B，若干24B view副本、4096槽及控制哨兵，无malloc。导出每个区域的地址/长度/对齐和`__data_end`，并断言低区结束小于24MiB。完整照片按单图流式注入，不把100图235MB全部放入WASM。

64MiB固定memory的高端用作一次一个的真实末端对象。最大ROM尾放置起点为67108864−16786468=50322396B，略低于48MiB=50331648B、仍高于47MiB，因而与小于24MiB的低区不交叠；source/target、ROM、槽表和view的末端测试分开，不能让两个对象同时占据同一末地址。每次迁移ROM/表后重新合法prepare，不使用旧缓存中指向前一位置的pointer。

WASM没有Windows VirtualProtect；只允许声称两类实际检查：普通内部缓冲的前后canary，以及对象恰好结束在线性内存末端、意外越界会触发WASM bounds trap。内部页不是NOACCESS。固定memory最大值，不growth后把原边界变成可访问；零长度一过尾指针不应访问。

四fixture固定实际3082页、单页单色、单页256色、最大4096页/ID4095；所有256个palette合法项必须保留。每fixture独立核4096槽实际32位地址等式，共16384项；最高合法P4页ID4095，65535拒绝，不能误借其它字典格式的范围。

## 预注册有限合同

只有新纯C99 out/in两路径，没有OMP/AVX路径。下一实施前需将以下方案与逐项标签、全部执行源一起冻结，不能执行后补计数；本表不代表已经运行。

| 项目 | 拟固定覆盖 |
| --- | --- |
| 普通有限 | 原22长度×偏移0/1/3/7×out/in=176，加合法零长NULL两项，共178；输出oracle与哨兵 |
| 格式拒绝 | 原21格式/长度×零/已准备两状态=42，失败不写view/槽 |
| 其它prepare拒绝 | 24逻辑项×两状态=48：5错count、NULLview/槽、NULLblob两长度、3跨度溢出、view/槽各3错位、三对对象全/部分重叠6项 |
| 失败旧态重放 | 21+24=45；标签含format/argument来源，避免两个count0混作唯一标签 |
| IO拒绝 | 两路径旧10种20项；新view尾/槽首尾等5位置×src/dst×两路径20项；clear后n=0/1共4；NULLview n=0/1共4；view及槽各3错位×两路径12；槽NULL/溢出4；槽alias ROM/自身view4；合计68 |
| 生命周期 | view副本apply、clear副本不改ROM/槽、原view继续apply、repeat clear四场景；NULL/错位1..3 clear拒绝4项 |
| ROM非对齐 | 实际ROM偏移0..7×out/in=16项固定探针 |
| 线性内存末端图像 | 原18 guard长度×原地一项/分离source端与target端两项=54；n=0也不能访问尾外 |
| 线性末端ROM/槽表/view | 四fixture×out/in，各8项，共24；加图像合计78末端放置 |

源/目标只允许同址或完全不相交；与**整个24B view**、全部槽表和ROM交叠必须无写拒绝。错count或错blob失败时，零state仍零、已准备state仍可用；view和whole caller表字节原样保留。自重叠槽必须指当前bad view自身，不能再指另一个model对象。clear只清该view；ROM/槽SHA及其它副本可用性不变，不执行allocator或OS句柄清理。

另设4个**明确预期trap**的独立新实例案例：source=memory末端、target=memory末端、prepare的槽表=memory末端、clear的view=memory末端。它们在uint32数值范围内却不是有效可访问对象，属于VM边界演示，不能要求标准C返回1或把trap混成合法拒绝。每例独立实例、记录RuntimeError和未返回，不在trap后继续使用可能半写状态；若不按预期trap则STOP。普通合法末端案例任何trap都算失败。

## 完整域和百图

只使用原固定模型的canonical RGB输出流，执行前冻结其实际路径/长度50331648B及SHA `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`；文件缺失或身份不同就STOP，不在本阶段重新拟合/导出选择参考。该参考已由既有M16D/u64索引验证；本阶段是WASM候选实际运行与独立输出映射比较，**不是重新执行四级uint64插值**。

新out/in两路径各完整256³，按外部R高位固定枚举、每次65536像素；每块逐字节比较canonical stream，同步检查整流SHA。实际ROM放在byte偏移1，caller表仍按4B对齐。模块内调用次数为每模式256次完整域；每个结果明确绑定新export名，全部中间输出也比较，不能由最后汇总摘要替代覆盖。

照片固定同一100图235929600B、输入SHA e13278cf…，Node逐图读入WASM。参考由canonical cube用精确24位整数输入code查RGB3，索引小于2^24、JS Number可精确表达；这是已验输出的字节映射，不是浮点插值近似。每路径逐图全部像素比较，100图整流SHA必须为f3c0d907…；两路径共200次整图apply，和512次完整域调用分别计数。旧linear WASM结果不会替代这里实际新export运行。

## 执行证据与停止规则

未来只有明确grant后才能冻结/构建/运行。先冻结所有旧C/头、wrapper、shim实际include闭包、Node检查器、驱动/审计源、工具/全部输入身份及预期计数；保存每条命令stdout/stderr/exitcode。第一编译、imports、ABI、合同、guard、输出/引用身份错误均保留STOP，不改源码/工具/计数后覆盖重采。

Node记录process.versions、模块imports/exports、每次新入口尝试/返回/预期trap、所有输出计数/摘要、prepare/clear前后view/槽与ROM身份、真实offset和地址跨度。原生Windows View48B/slot32KiB不能冒充WASM View24B/slot16KiB实际读回；即便本阶段通过，也只是Node/V8 wasm32功能证据，没有MCU/移动端/大端实机、闪存等待、功耗、WASM对Windows相对速度或50档保证。性能仍独立，源码功能验证不以补跑恢复既有失败。
