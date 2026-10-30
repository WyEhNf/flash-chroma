# C99组内重叠写取得限定场景的50%吞吐档

Agent：Codex `/root/memory`；Operator：本会话项目用户；Task：16题方向3第四阶段；Status：本阶段完成；仅四线程真分离输出线性ROM符合50%档，未达到整体双底线。延续`f691223`之后的独立研究，不改前面两个C99失败记录、公开默认或AVX2算法。

本轮只改变一个方面：8像素全部ID先读，之后直接从序列化LE调色板复制RGB字节。前7项`memcpy4`的第4字节会被下一像素覆盖，最后一项只`memcpy3`；每组只写其合法24字节，短尾逐像素`memcpy3`。不同调用的目标区域可重叠，但每次memcpy的ROM源与目标仍完全分离，符合C99；不使用裸uint32 store、主机端序假设、额外输入/输出填充、ISA或堆。新函数`jshc_mem_apply_store`与独立头/源码保留普通C99及ILP出口。

`experiments/memory-rom-store-v1.json`在构建前冻结11份源。环境Windows11 26200/Ryzen9 8945HX/GCC15.2/Python3.12.14/NumPy1.26.4，与前阶段相同；C99 TU使用`-std=c99 -pedantic-errors -O3 -Wall -Wextra`，未加ISA。OMP_DYNAMIC=FALSE、OMP_WAIT_POLICY=PASSIVE，分别请求1/4线程，未锁频/绑核。全部15配置完整256³、3850有限合同、304原保护页/非对齐和23拒绝通过。另直接调用独立C99 DLL的新store出口，完成150个输出末页保护检查：五ROM×15长度×原地/分离输出，覆盖1/7/8/9/15/16/17/31/32/63/64/65/4096/65536/65537像素，和AVX2逐字节相同且没有越界。新四级完整域及百图SHA仍是已验a399，不改变mean/p99/max或任一图精度。

性能沿冻结五角色78/80/C99线性/C99的16、64字节块，四串行新进程轮转/反序，交错1/4线程和双接口，每配置一次预热＋5次完整100图，尾部80 A/A控制；主要计时400轮，A/A80轮。计时排除准备、恢复输入、IO和hash，首尾SHA通过。分母为同场每worker的78/80较快者，不借较慢specialized库过线。

| 候选/情形 | 中位吞吐保留 | 最劣worker保留 | A/A与资格 |
| --- | ---: | ---: | --- |
| 线性C99，原地1线程 | 53.44% | 44.76% | 控制有效，但越50%，拒绝 |
| 线性C99，原地4线程 | 60.23% | 54.24% | 控制单对1.3473>1.25，只有观察 |
| 线性C99，输出1线程 | 49.36% | 47.42% | 控制有效，但越50%，拒绝 |
| 线性C99，输出4线程 | 55.12% | **51.23%** | 控制有效，符合50%档 |
| 16字节块C99，输出4线程 | 42.67% | 39.05% | 越50%，拒绝 |
| 64字节块C99，输出4线程 | 44.59% | 39.24% | 越50%，拒绝 |

原地1线程、输出1/4线程A/A中位0.9665/1.0668/1.0111均通过，单对均在0.8..1.25；原地4线程虽然A/A中位1.0033，但存在1.3473单对，仍拒绝正式结论。所有字典的其他有效情形也低于50%，不据中位数或更大样本掩盖最劣回退。

仅在**四线程真分离输出**这一个有效情形，新方案在精度底线100/90/80/70/60/50%都保留100%精度；速度底线100/90/80/70/60%均无合格新C99表示，50%档可选线性ROM16,779,328字节，较28,046,644字节基线省40.17%。四线程由可选OpenMP桌面适配器提供，不能说独立C99库本身包含线程或已在所有平台达到50%。其独立C99函数不依赖OpenMP/AVX2；单线程及原地条件尚不合格，不能将这个限定场景提升为整体通过。

模型结构/ROM/堆scratch与首阶段不变；本机GCC stack帧计量见证据中的`.su`，不当作线程栈/RSS总峰。复现仍先设置首阶段Python与线程环境，使用不存在的新输出目录：

```powershell
& $py -X utf8 scripts/build_memory_rom_store.py --base-build <ANDN阶段build绝对路径> --output artifacts/new-memory-store-build
& $py -X utf8 scripts/verify_memory_rom_store.py --library artifacts/new-memory-store-build/jshc_memory_rom.dll --roms <原ROM目录> --data-root <原模型根目录> --output artifacts/new-memory-store-full
& $py -X utf8 scripts/bench_memory_rom_store.py --build <新build绝对路径> --roms <原ROM目录> --ref80 <同源80绝对路径> --data-root <原模型根目录> --output artifacts/new-memory-store-perf
```

[原始证据](../../report/data/p16-memory-store-v1/README.md)保留新纯C99目标保护页driver、所有轮次、A/A失败限定、RSS、冻结源和实际库。没有重测择优、丢弃worker或拼接前阶段速度。下一步单独研究不依赖窄调色板域的frozen sparse句柄，不和本次写入方案叠加。
