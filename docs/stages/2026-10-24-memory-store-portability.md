# C99存储核的独立wasm32执行与跨目标编译

Agent：Codex `/root`；Operator：本会话项目用户；Task：16题方向3；Status：本阶段完成，方向研究继续。建立在`23f3b5c`存储阶段之上，不改变其四线程分离输出才通过50%吞吐底线的限定，也不改变此前C99普通核/ILP负结果。

新建极小调用包装器，将既有地址、边界与完整域夹具的入口重定向到`jshc_mem_apply_store`。新夹具提供标准`memcpy`声明及freestanding实现；生产C99代码、旧夹具与旧验收源码原字节保持。使用LLVM21.1.0、Node24.16.0/V8 13.6、Python3.12.14，Windows11 26200/Ryzen9 8945HX。C99编译参数含`-pedantic-errors -Wall -Wextra -Werror -ffreestanding -fno-builtin -nostdlib`，没有C++、OpenMP、AVX2或运行时imports。

- 五种ROM（线性、16/64/256/1024字节字典块）各完整执行256³颜色，与a399既有独立输出流逐字节一致，串联SHA均为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。
- 每格式另有64项有限原地/分离检查，覆盖0/1/7/8/9/255/4097/65536像素及0/1/7/15字节偏移，输出前后哨兵保持；三类拒绝、空输入和未对齐ROM保持通过，ROM内容未改写。
- wasm模块SHA为`c1322a6f6d2f0925564ec916344c4fd5428d7715773471ea88e80fbfaa25d2d3`；模型视图1044B，夹具固定32MiB线性空间和64KiB栈预算另列，不能把视图大小当作总RAM。
- 原核心与新存储核分别编译为Cortex-M3 Thumb/RV32IM ILP32/AArch64大端对象，共六份；验证ELF类别、字节序与架构号均符合。这里只编译对象，没有链接/BSP/仿真/实板速度、闪存等待或功耗结论。`.su`只记录各函数静态帧，不是调用链或线程总栈。

保留初轮失败：原freestanding测试头只声明`memset/memcmp`，新存储核需要的`memcpy`未声明，C99严格构建拒绝。失败源码、日志和run原字节封存后，另建新的support目录补全声明/实现，第二个输出目录通过；没有修改生产核、屏蔽警告或覆盖失败记录。这是测试夹具缺项，不作为像素正确性失败或性能成功。

复现时先按[ROM首阶段](2026-10-23-memory-rom-tiers.md)恢复五ROM与冻结cube，使用不存在的新目录：

```powershell
& $py -X utf8 scripts/verify_memory_rom_store_portability.py --roms <五ROM目录> --cube <冻结cube.rgb> --output artifacts/new-store-portability
```

[原始证据及源码](../../report/data/p16-memory-store-portability-v1/README.md)包含失败/成功构建、Node实际执行、目标对象/静态帧和逐成员SHA。此阶段没有新拟合、100图性能、x86吞吐或质量分数，不改变[存储阶段](2026-10-24-memory-rom-c99-store.md)的实测门槛。
