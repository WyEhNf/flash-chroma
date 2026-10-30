# P4调用者页指针表：单版静态可行性评估

状态：仅静态评估，没有AST冻结、新导出、构建、统计、质量或计时。原P4 ROM、40B ABI、9387738及此前所有已测源/对象/DLL不改；Windows alias的unknown STOP保持。

结论：值得一个固定纯C99候选，但预期收益边界很窄。它能消除页ID加载后的shift12和offset合并，不能减少三次串行内存读取；32KiB native表的占用和更宽首级加载可能抵消收益。旧copy4只有4T限定50、1T分离有效45.385871%且1T原地失效，均不替新方案取得全局资格。

## 现有实汇编与新访问链

已封存copy4对象的第一lane实际是：0xb0 `movzx ecx,WORD [page_ids+index]`，0xb5 `shl ecx,12`，0xb8低12位mask，0xbf合并offset；随后0x1c7读取pool的byte ID，0x1f2读取palette的DWORD。其它7lane同样。页map的LE16在x64已合为单WORD加载，不是每像素两次字节解码；Model中的pool/palette基址按组加载。

| 阶段 | 原copy4 | 新页指针候选 |
| --- | --- | --- |
| 第一级 | `page_ids[code>>12]`，native实码单WORD | `pages[code>>12]`，native指针加载 |
| 页内地址 | 已取ID左移12，结合低12位并加pool基址 | 预计算page指针加低12位 |
| 第二级 | pool byte ID | 相同pool byte ID |
| 第三级 | palette DWORD/原字节copy4 | 相同palette DWORD/原字节copy4 |

两者都是第一级→pool byte→palette的三次数据依赖读取。新方案只提前计算页指针，不宣称消掉一级load或cache miss。输入RGB到24bit code、页索引提取、低12位mask、最后palette访问、8像素批读/写与短尾都保持；x64地址生成可能把pagePtr+low折入byte load，但未构建，不能提前写成真实指令。

原LE16 map为8192B，新native表64位为32768B，首级工作集扩大4倍、单次加载从2B变8B；这是读取宽度，不等于DRAM流量按6B增长。L1容量、相联、照片命中和跨核副本均未测，不能由32KiB直接称“装得下L1”。四线程可共享同一caller数组，容量只算一份；各核缓存占用是另一口径。

## 唯一视图与完整容量投影

不产生新ROM、不删除原8192B serialized map，也不修改palette或输出。另立类型，原jshc_p4_model定义不变：

```c
typedef struct jshc_p4_pages_view {
    jshc_p4_model base;
    const unsigned char *const *pages;
} jshc_p4_pages_view;
```

base按值保存原prepare得到的借用字段，因此无需额外常驻的外部40B Model；pages指向caller提供的4096个native pointer槽。下面都是尚未实测的ABI投影，必须在新阶段检查sizeof和对齐：

| 部分 | flat x64投影B | flat 32bit投影B |
| --- | ---: | ---: |
| 原P4 ROM | 12633124 | 12633124 |
| 4096 native页指针 | 32768 | 16384 |
| 新借用view | 48 | 24 |
| 总capacity | 12665940 | 12649532 |
| 相对原P4 view方案增加 | 32776 | 16388 |

64位新投影仍比linear的16779328B少4113388B，代价不是免费。代码/DLL、宿主owner/ctypes、进程WS/private、prepare暂态、每函数栈分别实测，不从投影推物理RAM。库不malloc；caller可用静态数组或自己的arena/allocator，不建议隐藏在每像素或每图栈上。prepare仅有局部验证/发布对象，不需要另一份4096指针scratch。

## 准备与失败语义

拟独立入口接受view、原blob/bytes、可写native pointer数组和page_count；page_count固定等于4096。先完成所有可返回失败的范围、对齐、交叠和原ROM验证，再写表并发布view。

1. view和数组是有效可写对象；blob是有效可读字节范围。整数长度/地址溢出、NULL、错误count及对齐在写前检查。native pointer数组必须按指针对象要求对齐，ROM本身仍允许0..7非对齐，页指针值指向byte数据无需8B对齐。
2. view、数组有效跨度和blob三者必须完全不重叠，包括部分交叠；拒绝这些情况不写任何对象，避免损伤readonly ROM或已有状态。数组跨度只认4096×sizeof(element)，不接受多余count作为另一候选。
3. 调用原P4 prepare进入局部base，完整验证原格式、palette、页ID范围、pool ID和guard。失败时caller的view和整个数组都保持原字节；零初始view失败仍为零，已准备view失败仍可继续使用旧状态。原P4 API自身语义不改。
4. 验证成功后逐项写`pool + ((size_t)pageID << 12)`；pageID已证明小于uniquePages，每个指针覆盖合法4096B，最后页内4095也在pool内。最后才发布带base和pages的新view。写表后没有进一步可能正常返回失败的步骤，避免半表发布；硬件故障/无效内存不是纯C99可恢复错误。
5. 重新prepare或clear必须在没有并发apply时进行。原ROM和页表从成功prepare到最后一次apply结束均不可变；API不承诺每次apply重新扫描4096个caller槽，也不承诺接受被外部篡改的native pointer表。

纯C99没有_Alignof。拟使用实际pointer数组契约，并以C99 offsetof对齐探针给支持的flat ABI做保守写前检查；预期x64为8、32位为4，必须实际测量。探针若给更严对齐也须公开，不能伪称任意ABI自然对齐已证。旧实现本身依赖8bit byte与uintptr_t的flat地址范围模型；不扩张到能力指针、分段指针或特殊Harvard flash地址空间。

## Apply与销毁契约

热路径固定为`pages[code>>12][code&4095]`取ID，再读取原palette并copy4。保留copy4的8输入先读、8颜色先求、前7项4B组内重叠写/末3B写与原短尾。仅纯C99候选，不另立native页表AVX变体。

apply需验证view/表指针范围和对齐、原base字段/头与必要IO合同，不能仅调用旧validate后遗漏新view尾部8B或caller表。src/dst允许完全同址或完全不相交；均不得与整个新view、全部pointer表或blob交叠，零长度和溢出边界保持原原则。prepare生成且保持不可变的表是使用前提；任意伪造、失效地址和权限无法由标准C探测。

clear只将调用者的有效view置为空状态，不释放、遍历、覆盖caller页表或ROM。它不触碰任何OS句柄，也不卸载DLL；caller在全部引用结束后自行释放表/ROM。相同ROM/已完成页表可以被只读view副本共享，清零一个view不销毁另一份借用；准备写表和读者并发不允许。已clear view随后apply包括零长应拒绝；clear自身要求有效可写对象，不能向任意ROM地址调用并期待权限探测。

native pointer表是进程内临时表示，不序列化、不跨进程/重定位/32与64位复用。大端目标由C编译器存取本机pointer，只有prepare仍显式读旧LE16，palette仍原字节copy4；这是设计依据，不是BE实际运行证据。统一可读ROM地址空间和自然pointer表示是当前边界。

## 如获授权：只允许一个固定候选

先冻结新独立源/协议和所有原件；保持Clang21.1.0严格C99 generic x64、旧prepare/ROM/ABI不动、不restrict/ISA/预取/页尺寸扫描。实际sizeof/对齐和对象机器码先核：首级应为native pointer表加载，旧每像素ID左移12/offset合并应消失，仍如实注明三次串行load。没有实现该机制就停，不调整第二版本追分。

质量须重新覆盖明确新入口的完整域、100逐图u64、四线程/原地/分离与全部旧拒绝/guard，并新增caller表的末槽NOACCESS、错count/NULL/各错位、表与view/blob/IO部分重叠、失败保留已准备状态、clear不改表/ROM、最后页/最大4096页、全部256palette、ROM非对齐。prepare必须覆盖所有槽，不能读取初始垃圾pointer；一页/4096页夹具不更改固定实际3082页模型。首错保存STOP。

之后才另冻结同场性能，主分母仍每phase更快78/80，linear C99和原copy4作辅助；所有角色自身双阶段AA与外围控制、全部worker/phase最劣及100..50六档保持。4T限定50不救全局：新方案必须自己四模式全有效且最低≥50才给完整50。原copy4的1T分离需要约10.2%额外吞吐才触底，这只是计算门槛，不是预测。任一有效低50即保留一次固定候选负例，不扩cache大小、分区或其它变体。

因此值得一次有明确停止条件的验证；当前尚无新速度、容量实测、WASM、ARM/RV32/BE对象或实板结论。
