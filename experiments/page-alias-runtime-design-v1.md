# 固定4KiB页别名单版部署：静态API与回收状态机

Agent：`/root/memory`；Operator：16题用户；Status：前置单版协议，root已授权唯一导出/API/生命周期/格式验收；冻结后方可执行。完整像素域/百图和吞吐仍未授权。原固定普查f98d7c09…和其结果不改。

## 不变对象与唯一对照

原a399、旧Clang线性计算DLL和1056B model均保持；消费已封存3082 unique页的pageID，不再普查/排序/扫描参数。候选是alias；两个必要控制是原普通RO与同header页末/同table对齐的不去重RO。各自AVX/C99及fast78/80可形成8角色，正式另冻结，当前没有性能计划执行。

别名backing文件第一4KiB页开头放独立容器元数据，末1056B放原M16D header；4096项LE32 pageID从文件4096开始，pool从20480开始，长度12644352B。元数据固定pageBytes4096、logicalPages4096、uniquePages3082与两个原摘要，不让字段指向任意地址。保留全部256合法palette槽。

不去重对照文件同样第一4KiB页末放原header，但其后直接接原16MiB table，文件16781312B。它不需要多余pageID副本。两者虚拟blob=base+3040、table=base+4096，原逻辑blob_bytes仍16778272。原普通RO保持旧文件/布局；不把对齐改善混同页复用效果。

## API与对齐

先只解析`VirtualAlloc2`、`MapViewOfFile3`、`UnmapViewOfFile2`及标准VirtualFree/VirtualQuery/CreateFileMappingW等符号，再创建alias owner。缺失新API时明确返回`fallback-linear-readonly`，由原RO loader读取原M16D；记录缺失符号、真实路径/容量和实际mode。正式alias候选若落到fallback则停止资格测试，不能以fallback成绩冒充alias。

只在本进程新申请的placeholder范围内操作，不调用MapViewOfFileEx抢占未知地址。三种process API统一使用GetCurrentProcess返回的本进程伪句柄（不关闭它）。`VirtualAlloc2(currentProcess,NULL,reserveBytes,MEM_RESERVE|MEM_RESERVE_PLACEHOLDER,PAGE_NOACCESS,NULL,0)`，reserveBytes为4098×4096=16785408B：4097页用于header+table，末一页始终保留NOACCESS作为ROM字节精确尾guard。该额外4KiB仅是保留VA，不加backing；应在实际部署账本单列，不能回写原普查的模型视图跨度16781312B。

alias先用`VirtualFree(base+i*4096,4096,MEM_RELEASE|MEM_PRESERVE_PLACEHOLDER)`顺序split 4097次，形成4097个单页placeholder加末guard。每次`MapViewOfFile3(section,currentProcess,base+i*4096,fileOffset,4096,MEM_REPLACE_PLACEHOLDER,PAGE_READONLY,NULL,0)`严格替换相同范围：第0页offset0，其后offset=20480+pageID[i-1]*4096。所有offset/长度先检查溢出、4KiB对齐与文件范围，VirtualQuery核预期占位/映射范围。

aligned对照只将前16781312B保留区split一次，用同API映射一个连续RO view，末guard不替换。普通RO不用新API；使用已有loader保持原行为。

[官方MapViewOfFile3](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile3)明确MEM_REPLACE_PLACEHOLDER下免64KiB base/offset限制；[VirtualAlloc2](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc2)与VirtualFree的placeholder规则约束split/coalesce。不能把MapViewOfFile的普通64KiB规则套到错误偏移，也不能由文档存在推断本机调用成功。

## 固定owner与成功状态

owner必要状态仍是48B原型：file/section/base/span四个8B项，mapped_pages/split_pages/state/reserved四个u32，另原model1056B。所有映射地址由base和常数推导，无指针数组；pageID只在安装时读取，不保留第二常驻副本。Python外壳、临时16KiB索引读取与OS对象成本另列。若实现需要额外必需常驻数据，重新扣账并复查至少1MiB净backing门，不隐去字段。

状态沿`EMPTY → FILE → SECTION → RESERVED → SPLIT(k) → MAPPED(j) → READY`推进。split_pages记录已完成顺序split数；mapped_pages记录从第0页起成功映射的连续前缀长度；READY必须全部view/保护/虚拟canonical SHA以及原native prepare通过。canonical虚拟blob重新得到原完整M16D SHA146a5f28…和ID a020…才可以映射图片。未READY不向调用者暴露可用model。

文件以GENERIC_READ/FILE_SHARE_READ打开，保持file与section到回收结束，禁止外部写共享。单owner仅管理自身一份Model，close开始即清零，关闭为终态不得重开以免旧引用复活；外部自行复制Model仍受原ROM借用生命周期约束。禁止与native apply并发close，标准C99本身不增加锁。alias加载失败是明确异常和清理，不在候选内部静默改用原表；只有符号缺失的应用入口明确fallback。

## 部分失败与close

1. 还没reserve：关闭已获得的section/file，句柄成功关闭才置空。
2. split阶段失败：保留base/span和split_pages；地址为已拆单页前缀及剩余tail，可在确认全为自有placeholder后coalesce成一个，之后VirtualFree(base,0,MEM_RELEASE)。
3. 部分映射失败或close：先清零model；按倒序从mapped_pages-1调用UnmapViewOfFile2(currentProcess,address,MEM_PRESERVE_PLACEHOLDER)。每成功一个才递减计数；失败即停止该段，保持仍存在的连续映射前缀，状态可供显式重试，不误标全关闭。
4. mapped_pages为0后，所有范围均为自有placeholder；若split过则VirtualFree(base,span,MEM_RELEASE|MEM_COALESCE_PLACEHOLDERS)，成功后split_pages清零；再释放单个完整placeholder。coalesce/release失败保留状态，不关闭file/section以免隐藏未回收资源。
5. VA释放后依次CloseHandle(section/file)；成功才置空，失败保留以重试。最终CLOSED允许close幂等返回，仍禁止重开。构造异常同时记录原失败和清理异常，不用清理异常覆盖原因；异常携带仍存活owner，清理失败时调用者能显式重试，不能让未回收状态随构造异常丢失。

实际代码需按alias/单view控制的不同view extent释放，不能把aligned大view按4KiB拆Unmap。两路径分别预注册明确分支，运行时不猜测布局。测试覆盖0、1、中间、末个split/map失败，native prepare失败，Unmap/coalesce/release/CloseHandle失败后重试，以及真实文件/保护错误；使用注入API记录顺序与真实OS合同并列，不能用注入替代真实调用。

## startup和内存口径

分别记录整个加载前后、文件/元数据校验、reserve/split/map、canonical验证、native prepare、全页只读触碰、close的wall与进程计数；所有前置SHA也计入另列全成本，不能只报告映射热循环。这些setup观察与后续稳态吞吐独立报告，若冷启动越50底线应明确限定/拒绝该场景。

实际账本包括两个真实文件长度、模型sizeof、owner实例字段大小、临时索引/哈希预算、虚拟model span和额外guard VA。fresh同imports记录PrivateUsage/WS/峰、PageFaultCount、进程pool quota/句柄及VirtualQuery可见区域数，不能将0或不可归因的pool数写成没有PTE/VAD成本。

QueryWorkingSetEx可记录4097个逻辑view页的Valid/Shared/ShareCount/保护属性，按虚拟地址只读触碰后采样。[字段文档](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-psapi_working_set_ex_block)中的ShareCount是进程数而非同进程别名数，Shared只表示可共享，没有PFN。文件重复offset复用是API/布局依据，unique backing与WS均不能冒充实测独立物理页数；未知kernel成本保留限制。

## 本次唯一前置与后续门的边界

源/协议/原输入SHA先冻结，唯一导出alias与aligned文件后另存receipt及真实文件SHA，不能覆写。随后原普通RO、aligned、alias各一个相同imports的fresh进程，最后一个真实API/失败/格式合同进程。本次全部只做准备/映射前置：不是图像、稳态吞吐或冷启动合格声明。三个外部进程wall含解释器/imports/全输入SHA/导出receipt校验及结果写入，owner内部分段另列。所有约4097个逻辑页只读触碰，QWS原属性及完整VirtualQuery区域保留。

固定open/file_size/section/reserve调用前失败；split/map各0、1、2048、4096及prepare调用前失败；close时unmap4096/coalesce/release/close_section/close_file失败各显式重试。另map2048与回收unmap2047双失败，核异常含原因和清理失败、清零model并保留owner；预设一次注入用尽后显式重试回收。每例真实已创建资源最终句柄回基线，VA释放回MEM_FREE；任何预料外失败原件STOP，不修源重采。若仍未回收，子进程保存owner并等status/retry显式命令，不能退出借OS销毁掩盖未回收。

格式前置包括原容器、count1/count256固定合法夹具，全部256槽与末ID255；magic/version/page/pages/unique数/metadata/offset/kind/reserved/原头字段/首末非法pageID/截断/多余/ID及canonical摘要/native count0或257/缺失文件拒绝。符号缺失各自独立核明确原RO fallback与原SHA，不给alias授档。统计wrapper/API浅层Python对象大小和必需属性，48B只是native必要状态，不与Python外壳或OS成本混称total。

本前置通过后仍需另授三个loader同源全域与百图、C99/AVX1/4原地/分离、source/dst guard、actual/count1/count256 ROM末端guard与非对齐图像；这些本次不执行。

本次没有native构建、像素完整域/百图或吞吐；原DLL与数学不变。前置全过仅报告ready，完整质量和未来同场四模式100..50速度资格各另授窗口。
