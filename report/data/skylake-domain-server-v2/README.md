# 修订4/16服务器包与WSL正确性

[主阶段](../../../docs/stages/2026-10-20-skylake-domain-proof.md)的Windows性能另列。本目录保存目标Linux标准库入口和一次修正后的AMD/WSL移植验收，**没有正式Linux或Skylake性能比较**。

包SHA为`74649bd457527a55295d03bf3335041aa388cf1b4e090fd36b600eb4321e84b2`。完整ZIP188561958字节，SHA为`ce0ff0a5842dbc670a138cdab2b451dd1cc893b4f52452a298c376626063aa61`，本机路径见`delivery-packet.json`。`server-packet-small.zip`保留除三个大流外的全部冻结文件和manifest；按清单从旧包恢复235MB照片流、完整首级流及最终预测流，或使用完整ZIP，不能把小包称为无需数据的独立运行包。

实际为Linux6.18.33.2-WSL2 / glibc2.43 / Ryzen9 8945HX，Ubuntu GCC15.2.0-16ubuntu1、Python3.14.4标准库，无NumPy/Pillow；显式AVX2。CPU0/2/4/6四个不同物理核，真实OpenMP团队为1@[0]与4@[0,2,4,6]，主线程绑定后允许集[0]属预期。虚拟微码0xffffffff、GDS记录Not affected，均不代表Intel Skylake状态。

`linux-correctness.json`记录3432次有限后端/偏移比较、72条诊断拒绝、13份域诊断、全部原缓存槽、12组完整256³、两种整批/逐图调度的8配置各2轮百图、14条计时器拒绝及回调中止，全部零差。实际域证明/快路径与Windows相同，模型1800836字节保持。调度验证调用计时器但不采纳其时间；`linux-results.json`明确performance_measured=false、adoption=null。

`linux-fallback-object-proof.json`另核对实际Linux原回退对象逐字节相同；这不证明新准备/入口没有成本。`linux-built-libraries.zip`、`linux-build-details.zip`与policy/run/commands绑定真实库、工具链、依赖和路径。系统依赖只记录路径/SHA，不把这些本机.so称为其他服务器可直接使用的二进制。

首包在有限阶段因`equal_changed_shared`同名不同模型误绑预期而拒绝，未进入完整域或性能。`initial-failure-and-fix.json`及`initial-failed-packet-small.zip`保留原包、日志和不同模型SHA。修正只对cache_分组按模型/侧表的真实哈希绑定诊断；原生源、派生构建计划和有限数值预期未变，新包完整入口重新通过，不删除失败或归因为噪声。

完整包中执行：

```sh
python3 scripts/run_skylake_domain_server.py --bundle bundle-manifest.json --output artifacts/domain-server-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
```

正式Skylake先确认实际SKU/系统/微码/GDS/NUMA与四个同L3不同物理核，可用`--expected-cpu`和`--cpus`固定；显式加`--measure`才执行四新进程、1/4线程、整批/逐图、5轮，共160组百图且逐轮SHA。四场景全部达到中位至少3%改善、任一apply进程回退≤2%、copy+apply及准备加已预热首轮中位不退化才通过。没有自动重试、改安全设置或频率；官方数据/Threshold及派生缓存许可仍待确认，旧两个服务器包与默认不改。
