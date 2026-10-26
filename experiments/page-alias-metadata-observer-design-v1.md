# 最后一次metadata opener最小观察

Agent：`/root/memory`；Operator：16题用户；Status：root授权冻结后唯一执行。原4480e0aa…和7c324521…两次STOP不改，不授资格。

严格复用7c324521的固定8例与原baseline/gc/account、owned返回值观察和首漂移STOP。仅对两个候选路径的Path.open返回context manager加观察：调用原opener、原reader.__enter__、原reader.__exit__；__enter__仍返回原reader，所以原loader读取对象和流程不变。只用字符串normcase/normpath匹配路径，不在测量区新增resolve/stat/opener。其它文件调用原方法。

保存opener前后、enter前后、exit前后的count，以及原reader fd、msvcrt.get_osfhandle返回的WinHANDLE、reader.closed/raw.closed/closefd。保留上次完整owned file/section及CloseHandle返回值和LastError。exit后用GetHandleInformation只读探测刚才的metadata WinHANDLE是否有效，记录原返回/LastError；不能由数字相同排除并发handle复用，也不把总数不变等同没有泄漏。

代理和日志只保存整数、布尔与文本，不把reader对象放进日志延长生命周期。事件仍写固定32768条数组，不开文件日志到计数区结束；保留v1已有gc前后的数，禁止新增warmup或改baseline。输入/源先冻结；唯一一个fresh、无导出、三fresh、其它格式/回收质量、图像、构建或性能。

如首count漂移则保留整个日志STOP；若owned仍在则保留进程等显式回收。即便本次不复现也不撤销先前STOP。若仍不能确定额外+1身份，页别名机制按unknown归档，不追加同类微调；转另一个可移植LE16 pageID机制仅静态设计。
