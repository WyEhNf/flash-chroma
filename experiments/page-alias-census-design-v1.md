# 固定4KiB精确页别名：唯一普查协议

Agent：`/root/memory`；Operator：16题用户；Status：Proposed，仅静态。当前不调用VirtualAlloc2/MapViewOfFile3，不部署、不计时，不改原M16D/DLL或已测RO结果。

## 可证伪机制

原线性ID查找没有软件dictionary依赖，模型文件16778272B（1056B header+16MiB表），原model1056B。固定把**payload相对起点**分为4096个4KiB逻辑页，完全相同字节页共用一个backing页。将来可把原16MiB连续虚拟table各页映到唯一页pool，计算内核指令、24bit索引与原ABI均保持。仅用OS自然4KiB，不扫描页尺寸、key、照片或gold。

[Microsoft MapViewOfFile3](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile3)说明MEM_REPLACE_PLACEHOLDER免除64KiB base/offset约束，但仍须页对齐、大小和placeholder范围严格相等。它使4KiB别名在本Windows上有API依据，不证明实现、性能或物理RAM收益。该机制需要Windows新API；portable C99未变，不称可移植性增强。

原payload从文件1056起，不能直接把原文件4KiB页当table页。预定compact backing第一个4KiB页末1056B保存原header：原blob=虚拟base+3040，原table=base+4096；虚拟table第p页映到pool的pageID[p]页。接着4个页容纳4096项LE32 pageID，共16384B，再接U个唯一4KiB页。先出现顺序编号，全部字节相等才去重，无hash碰撞捷径。

固定顺序安装4097个映射，地址均由base+i*4096推导；不用常驻4097指针或复制pageID数组。owner必要状态原型为file、section、base、span四个指针/size_t及mapped_pages、split_pages、state、reserved四个u32，x64实际ctypes原型48B；这不是已经部署的owner或Python/OS总开销。旧model仍1056B。

## 门槛与唯一执行

普查只消费已绑定原ROM SHA`146a5f28…`，原payload ID SHA`a020c67a…`。一次读取全部4096页，保存exact-byte计数与页ID；独立pool顺序回放重算完整16MiB ID摘要。固定有限合同为每页0/1/4094/4095四偏移（16384项）及两非法code拒绝，另核header末端+table起点、max code和metadata边界。profile不生成新backing文件或部署loader。

审计容量：新backing=`4096+16384+4096*U`；门槛总额加owner原型48B与原model1056B，对原16779328B**净省至少1MiB**才可请求后续单版部署。实际原型ABI大小进入结果；若部署后增加必需常驻字段或额外索引，应重新扣账，跌破门槛停止，不以初筛投影冒充实际容量。Python包装、一次性metadata解码以及OS映射成本不藏进48B。

虚拟映射跨度4097×4096=16781312B，原逻辑blob_bytes仍16778272B；这些没有因去重缩短。unique backing不是实测物理RAM；Windows工作集可能按虚拟页重复计。同场未来要分别报告backing/虚拟跨度/model/owner、fresh private/WS/峰、进程pool quota及句柄、准备阶段和失败清理。必要时增加QueryWorkingSetEx的Valid/Shared/ShareCount/保护属性；[官方字段文档](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-psapi_working_set_ex_block)中ShareCount是共享此页的进程数（上限7），Shared只表示可共享，均不是同进程别名数；该API不提供PFN，不能据此精确计独立物理页。PTE/VAD若不可由无特权进程独立归因，应列未测成本，不拿系统commit噪声代替。

若唯一页或原型门槛失败，保留负例并STOP，不换尺寸或继续映射。通过只报告有可检验的净backing投影，实际部署、全部域/guard、速度四模式六档另立协议；当前都未执行。
