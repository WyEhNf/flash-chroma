# 页别名前置v1失败的最小独立句柄观察

Agent：`/root/memory`；Operator：16题用户；Status：root已授权冻结后唯一执行。原4480e0aa…前置v1保持STOP，任何新结果都不能撤销它、授alias资格或进入图像/吞吐。

只运行一个fresh合同观察进程，消费已经导出的alias/aligned原文件及原DLL；不再次导出、重测三fresh或运行其余格式/回收质量。固定前8例：alias成功关闭、aligned成功关闭，分别缺VirtualAlloc2/MapViewOfFile3/UnmapViewOfFile2的原RO fallback，然后open、file_size、section调用前各一次失败。首个总句柄不回原基线或任何owned资源未回收即STOP，不补跑。

不增加warmup、不重置基线。保留v1已有的DLL/API解析、gc及两次account调用位置，但每一步前后都保存count，不能隐藏此期间变化。每例v1既有gc位置的前后也各记数；初始化、API解析及本例开始/成功/预设失败/Model清零/VA MEM_FREE等markers列入同一日志。

真实loader API及预设注入前后，记录GetProcessHandleCount、原file/section/base/span/mapped/split/state、Model是否全零、原参数句柄/地址、原返回值/LastError与异常种类。观察调用GetProcessHandleCount本身不递归观测；它保存和恢复ctypes LastError，原调用的LastError在其它API前捕获。CloseHandle只在原函数返回非零后才能清字段，原具体handle/result/error均可复核。

固定32768条ctypes事件数组，事件只写内存；测量区不开日志文件。输入与源先冻结。结束/首失败后才把数组导出binary、schema、CSV和结果JSON，明确日志文件IO在计数区外。fallback通过独立只读观察适配器调用同一个BASE函数；只在新观察器中临时替换runtime.FileView构造符，旧loader/runtime源原字节不改。

Model清零和释放后的VirtualQuery状态单列。若owned仍未回收，保留owner和进程等显式status/retry，成功回收也不恢复该次资格。若只见全进程count偏移，真实owned关闭receipt与总数并列，不能据总数直接断言OS泄漏或其原因。未复现只表示本观察未复现；本次始终是原因观察，不是重新申请资格。

预算一个线程、事件缓冲约数MiB、总峰预期<150MiB。无图片、gold、native构建、MapView参数扫描或吞吐测量；后续可移植uint16 pageID decoder仅作为另一个静态机会，不在本协议实施。
