# 显式准备对象共享的完整原件

Agent：Codex /root/speed；Operator：当前用户。2026-10-24实际Windows11 x64、Ryzen9 8945HX、GCC15.2 Release、Python3.12.14/NumPy1.26.4，进程允许CPU0/2/4/6，不是逐OpenMP TID绑定。无锁频控温、目标Intel或宿主完全独占证明。[阶段说明](../../../docs/stages/2026-10-24-p16-prepared-plan.md)保留实现、所有权契约、测试和实际退化。

`raw-evidence.zip`按STORE原字节保存全部13份JSON及临时非法SLUT payload：完整域、生命周期正确性、冻结计划、72组构造/释放和工作集记录、16组纯映射、四进程partial、结果及内存派生汇总。`raw-members.json`逐项绑定成员SHA和大小。没有删掉最慢worker1，全部32个A/A有效；原地1线程最劣吞吐86.40%，整体80%档，事前“无明显退化”失败。N10/100构造中位比0.100382/0.009899包含首次完整prepare，不能当作热像素或N1首次准备收益。

另直接保留`executed-plan.json`、`correctness.json`、`runtime-correctness.json`、`results.json`、`memory-summary.json`便于审阅，与ZIP对应成员逐字节一致。runtime覆盖完整16,777,216色、所有直接表词、504合同、11拒绝及单级fallback；owner测试覆盖初始owner释放后alias存活、4并发owner×16轮、错实例/空参数和显式snapshot文件变化语义。token不是文件SHA，不保护悬空指针。没有TSan/ASan、内存失败或计数溢出注入。

`memory-summary.json`从原Windows `memory_info`聚合构造后工作集和构造前后增量。N10/N100进程工作集比中位0.268698/0.032487；不是单纯容量比，也不是瞬时峰值。raw完整保留private、销毁后和高水位字段，不能把同进程累计高水位归因给一个变体。

`identity.json`绑定DLL/源码、编译器、构建参数和五复用COFF `.text`一致。`89-flags.make`、`89-includes.rsp`及`89-link.txt`为生成文件原件。固定a399模型复用`../p16-final-model-pair-v1/fixed-models.zip`的baseline内容，原87 DLL没有覆盖。

旧依赖`experiments/channel-runtime/channel_native.py`的实际执行工作区为CRLF、既有Git blob为LF；`execution-source/channel_native.py`保留实际执行原字节，identity同时记录旧Git与执行SHA。两者只差换行，未修改原依赖、原始测量或旧历史；首提交的源身份审计未通过此项，随后限定修复归档身份，不把失败审计写成通过。

只读复算不加载DLL或重新计时：

```powershell
python -X utf8 scripts/audit_p16_prepared_plan.py report/data/p16-prepared-plan-v1/raw-evidence.zip
```

从头复现按阶段说明先build，再用新目录verify/measure；若重建库因PE时间戳或环境产生新SHA，必须另立新计划绑定新库并保存原计划，不能修改本轮原件使其适配。`manifest.json`绑定除清单自身的全部原字节，`offline-audit.json`保存只读复算。
