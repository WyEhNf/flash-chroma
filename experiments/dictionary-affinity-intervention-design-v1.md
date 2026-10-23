# 字典变动的单CPU干预预案（仅静态，暂缓执行）

Agent：`/root/memory`。Operator：当前16题任务用户。Status：Proposed。本预案不属于RGB32新机制的正式性能，也不恢复旧3B全情形50资格。前一无干预诊断H1/H2证据不足，187/512次调用端点CPU变化并不能证明迁移导致变动。本预案只在root另行授权后实现及冻结，当前没有执行源码、拓扑探针或数值结果。

唯一干预为同一自有子进程内，原未绑定亲和性U与预定单逻辑CPU亲和性P的交错比较。原3B和ref80使用冻结原二进制，既有七模型全部准备并常驻，相同照片、源/目标实际地址、1T原地API保持。四新进程，不按某轮性能选择CPU或样本，不引用前一场数据作为未绑定对照。

CPU选择只读取`GetLogicalProcessorInformationEx(RelationProcessorCore)`及原process/thread/system mask。仅支持本机64bit、单processor group；取原三mask交集内、拓扑实际存在的最小`(group,logical index)`。不读取计时来选核，不按CPU efficiency class、SMT位置或缓存选择更好核心。无合法交集、无法恢复原状态或多group时记前置不支持并停止，不换核。

干预调用只作用于新建的测量子进程，不在可被其它进程使用的DLL内部改变调用者策略。初步实现边界为准备后仅一个存活OS线程；每个测量组前后核验，若出现额外线程则记录不支持并停止，不删除线程。这样避免缩小process mask后其它已有线程的mask恢复不完整。保存process与caller thread原mask，P时设置process及caller为同一单bit；U时先恢复process，再恢复caller原mask，并读回核验。任何失败保存原件，finally尝试恢复，不补跑或换干预。

Microsoft文档说明拓扑结果为可变长记录，需按每项Size解析；process mask须是system子集，thread mask须是process子集。亲和性限制可能减少获得的CPU时间，因此固定核变慢也须原样保留，不能当作错误排除。[拓扑API](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getlogicalprocessorinformationex)、[process API](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setprocessaffinitymask)、[thread API](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadaffinitymask)。

四进程各16组，每组固定8次完整百图调用。偶数组采用`UA UB PB PA PA PB UB UA`，奇数组采用镜像`PA PB UB UA UA UB PB PA`；worker奇偶反转首组形式。A=ref80，B=原3B。每组两次每条件，共四进程512次。无额外预热/补跑。输入恢复、mask切换、状态查询在单次API wall区间外，切换后的首次调用照样记录；全部调用及组输出SHA保留，API失败或SHA错即停止质量。所有原始组必须进入分析，不能因迁移、短时抢占、变慢而筛样。

逐调用记录wall、线程cycle、user/kernel 100ns、调用前后CPU号、原/实际亲和性、地址、组/条件/顺序。cycle仍非频率不变的指令计数，也不换算GHz。U不要求一定迁移；P要求调用前后均为预定CPU且mask读回一致，否则干预执行无效。预定CPU再慢也不得择核。

每worker分别用32次U_A和32次P_A wall计算p90/p10（linear），16个组内B/A比值分别计算U/P的p90/p10；组比值是该条件两次B的中位除两次A的中位。预先定义`S_A=spread(P_A)/spread(U_A)`、`S_R=spread(P_B/P_A)/spread(U_B/U_A)`。主要问题是亲和性干预是否降低A及局部B/A变异，而不是是否更快。

只有至少3/4 worker同时满足`S_A<=0.80`及`S_R<=0.80`，且各自U端点CPU变化至少10%、P为0且所有亲和性核验成功，才记为“支持亲和性干预降低本场两种变异的关联证据”。即使通过，也不把端点CPU变化单独解释为全部跨场因果，不能恢复3B速度资格。若至少3/4 worker的`S_R>=0.95`且P核验有效，则“不支持该干预使局部B/A变异降低至少20%”；仅A降低而局部比值不降低时单独报告共同变动，不能归因3B串行解码。其余含U迁移不足或前置失败均为证据不足。

无论结果如何，不再追加同类主机归因轮次，不改阈值，不按最好核/worker恢复通过。若仍解释不了，保留主机变动限制，研究重点回到减少解码依赖链。RGB32预展开是独立算法方向，其正式未绑定性能不被本干预替代。
