# 2026-10-24：固定4KiB页别名部署前置停止于句柄合同

Agent：`/root/memory`；Operator：16题用户；Status：STOP，不能进入完整像素域、百图或性能。固定普查的3082个unique页可真实映射成原M16D，但三个成功fresh不代表整个前置资格通过。

## 不变基线与执行边界

原a399、线性M16D和Clang C99/AVX DLL字节未改。M16D SHA为`146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5`，DLL为`442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723`。原逻辑blob16778272B、Model1056B合计16779328B；当前没有新像素输出的精度或速度资格。

唯一前置协议`4480e0aac989341ef6784bc3865d601db0460f999f3ba396252bbf1c6017059d`冻结11份源、7份输入。session14312唯一执行：导出、原普通RO fresh、aligned fresh、alias fresh均exit0，合同进程exit1后总driver停止。root同时运行数学质量，全部setup wall仅作一次观察，不能用于吞吐或冷启动档位。

|实际对象|文件长度|加48B必要owner与1056B Model|原基线净backing节省|
|---|---:|---:|---:|
|alias|12644352B|12645456B|4133872B|
|aligned未去重控制|16781312B|16782416B|-3088B|
|原普通RO|16778272B|16779328B（未加新owner）|0|

alias文件SHA`30b3a9092f511944ccf89af2f0da86f59abdc3700bcae42d0e089dab7515db6e`；aligned为`22496486f79bc2b550d2665f9af9dd92b6b89833bfc5f362cb9f3a5523d16f90`。消费已封存pageID，没有重新census或调参。header放在第一页末1056B，虚拟blob=base+3040、table=base+4096；逻辑blob长度不减。保留VA16785408B，含16781312B model view及独立4096B末guard。

## 三个fresh的真实观察

三个新API均从kernelbase解析成功。alias实际有4097个只读文件view和一个保留guard，共4098个VirtualQuery区域；aligned为一个连续只读view加guard，共2个区域；原RO为1个区域。虚拟完整M16D及ID摘要与原件一致，头尾实际保护PAGE_READONLY、类型MEM_MAPPED；guard仍MEM_RESERVE且AllocationProtect为PAGE_NOACCESS。

三个fresh句柄均157→159→159→157，关闭后Model清零、原VA为MEM_FREE。QueryWorkingSetEx的4097个逻辑页均Valid、Shared、保护2、ShareCount7；ShareCount封顶且表示进程数，不能当同进程重复页计数或PFN。没有实测唯一物理RAM的结论。

|fresh|Private before/open/closed（B）|WS open（B）|非分页quota before/open/closed（B）|
|---|---|---:|---|
|原RO|25956352 / 25997312 / 25956352|55476224|15920 / 16056 / 15920|
|aligned|24752128 / 24784896 / 24887296|54685696|15920 / 16272 / 15920|
|alias|24973312 / 27107328 / 27213824|56594432|15920 / 1196192 / 16192|

alias在open快照之前已构造4098个VirtualQuery字典，Private增量包含这些记录对象，不能称纯loader容量或将关闭后保留对象误判成OS泄漏。实际非分页quota显著增加，不能省略映射数量的内核代价；该进程quota仍不能精确归因为独立PTE/VAD或物理页成本。WS没有减少，backing文件净收益不能替代RAM收益。

alias owner open分段合计0.0839928秒、close0.0162371秒；aligned为0.0257432/0.0008727秒；原RO prepare观察0.0110970秒、close0.0015750秒。外部进程wall分别3.4024871、2.9170922、3.3073971秒，包含解释器/imports/全输入SHA/receipt及输出写入；不是可比较的稳定吞吐数据。原必要owner原型48B之外，Python owner对象48B、dict296B、ctypes状态及Model对象各120B浅层，API对象48B及dict296B；深层对象、解释器与运行库由进程计数另观测，不将48B称完整owner总RAM。

## v1合同停止及观测不足

合同在预注册的section调用前注入失败后触发“合同后句柄未回基线”。失败记录显示file/section/base/span/mapped/split全部0、state7，Model清零；48B状态不是全字节0，终态字段保留7。该路径尚未真实创建section/VA，已拥有的file只有CloseHandle返回非零后才清字段。

v1未把当时的总句柄实际数值、方向和具体CloseHandle返回值写入failure，这是观测不足，不能由断言文字断定OS泄漏。没有修源后重采v1，余下生命周期、格式、完整域、百图和性能都没有执行。fresh成功、文件收益和前置STOP并列保留。

## 独立最小观察再次停止

root另授一个fresh、固定前8例观察，协议`7c324521df06a1abe36c98b534edc0c94768f1eea944f409854ef517116fe9b8`：alias/aligned成功关闭、三种缺符号原RO fallback、open/file_size/section各一次失败；不重复导出/三fresh或余下suite。保留v1既有gc/account位置但全部前后记录，不新增warmup或重置基线。事件缓冲固定4980736B，32768条上限，真实loader API及注入的前后count、owned字段、返回值/LastError、Model和VA均留原始记录；计数区结束后才开日志文件。

唯一执行exit1，12420条事件在第8例首次未回基线，183→184后停止。前缀调用中的owned file明确关闭成功，但额外句柄身份未知：

|事件序号（从0）|操作|总句柄前→后|结果/LastError|
|---:|---|---|---|
|12409|CreateFile，file=752|183→184|752 / 0|
|12410|GetFileSizeEx(752)|184→184|1 / 0|
|12411|section调用前注入；没有真实创建section|185→185|Injected / 0|
|12412|CloseHandle(752)|185→184|1 / 0|
|12413–12418|异常接收、Model零、gc前后及最终account|184→184|资源字段0、state7|

变化落在GetFileSizeEx之后、section之前的Python元数据读取/校验区间。静态源码70行唯一opener为`with Path(path).open('rb') as source`，85行之前已退出with；无NPZ、np.load、mmap或file_digest。traceback可能保留局部source对象，但with已退出，不能仅凭对象被保留就说其文件未关闭。旧study.sha使用with且发生在baseline前；本轮fallback实际走FileView，没有调用study.loadrom的裸open/mmap路径。目前未找到具体未close对象或确认额外句柄身份。

该独立观察不能撤销v1，也不授alias资格。Windows路径不代表跨平台改善。root随后仅再授权最后一次metadata opener观察，固定原8例与基线，不扩其它质量。

## 最后metadata观察：文件已关，额外身份仍未知

协议`e6b008a15e29cc3b9dcfd24e332c9208a3eb037b1171a90645842d7417cf37e3`冻结17源/18输入，唯一执行exit1，在第8例183→184再次停止。共12435条事件与15条metadata记录：三个metadata opener（alias成功、aligned成功、section注入）均把总数184→186；`with`退出后186→185。fd均3，前两例reader WinHANDLE908、第8例844；exit后reader.closed/raw.closed与closefd均True，GetHandleInformation返回0/Error6，说明原文件HANDLE已经无效。不能把剩余+1归因于该文件还开着。

另有具体静态解释，但仍是推断：[CPython v3.12.14 bufferedio.c](https://github.com/python/cpython/blob/v3.12.14/Modules/_io/bufferedio.c)初始化BufferedReader时分配锁，close只关闭raw并释放buffer，锁留到对象dealloc。默认Windows模拟条件变量由[pycore_condvar.h](https://github.com/python/cpython/blob/v3.12.14/Include/internal/pycore_condvar.h)选择，[condvar.h](https://github.com/python/cpython/blob/v3.12.14/Python/condvar.h)以semaphore管理；[thread_nt.h](https://github.com/python/cpython/blob/v3.12.14/Python/thread_nt.h)连接该分配/回收。异常traceback保留局部已关闭BufferedReader及其锁，符合open增加2、close减少1、成功返回后回基线的现象。没有采本机锁semaphore HANDLE或编译宏，因此不能说实际额外句柄身份已证。

按最后观察的事前停止条件，不继续alias诊断、源修复、采样或质量/性能；机制按unknown STOP归档。owned文件真实关闭成功、reader文件已失效和全进程总数未回基线分开列。任何推断都不撤销三次STOP。

## 原始身份

v1 run SHA`e254ea1a327d6cd8f6cd580042c0ecd07a3e671082f0ec2e3d9be59b09734f84`；failure为`a4464ceaff059db43547f23414df062bd79f43da60aa549eabe14ed28e6ced4d`；alias fresh为`0359237c1594d65a0f8b5c1629ae1435bb1bab1a72ad9355ed9b4ead010d4895`。新观察events.bin为`e15f0078ed05b9f4f0e63f3f2505b7761456d797495ce5b0dd6bc5eec84e6bce`，CSV为`f1371fe2788973fb579525cd75bbbfe61a39b2ed3c95dadfc16708db55d37ed4`；schema独立给字段offset/宽度和全部marker。最后metadata SHA`336ae03ce2ccc71525ad47d0cffa0f9ad49c3a1818446ad9ecd5b9ece4f18336`。全部实际容器、CSV、binary、三轮失败和冻结源见`report/data/p16-page-alias-runtime-v1`；独立离线全blob重放及24855条CSV/binary逐字段审计不调用部署API、不变更原件。

静态后续机会另列：4096个页ID可用8192B LE16地图，可移植C99以code>>12读pageID，再读pool[ID*4096+(code&4095)]及palette；当前未生成此ROM/native，也没有速度证据。该机制与Windows虚拟别名是不同实验。
