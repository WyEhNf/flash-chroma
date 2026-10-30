# copy4达到原生50门后的可移植性验证草案

状态：只静态方案，未构建、统计或运行。新C99的正式1040调用还未执行；若出现有效低50，保留负例，不通过移植运行或补跑给原生速度授档。是否另作纯功能便携验证由root另行决定。

## 唯一验证对象与预先门

仅复用9f6b8f22的原P4 prepare/validate、独立page_copy4.c、相同40B x64借用ABI定义和已冻结ROM，不改算法、位宽、页分类或入口。WASM只编独立标准C99，无C++/OMP/AVX/BMI和堆；输入读取与文件API留给宿主，不给核心添加Windows loader。

若新C99四模式有效且最劣≥50，才提出独立冻结source/input/toolchain/flags后的唯一功能阶段；本预案不自动授权。任何编译、无imports、ABI、完整域、逐图、拒绝或guard失败均保存STOP，不能修后覆盖原运行。WASM通过只增加实际运行环境证据，不证明WASM或MCU速度达到原生50%。

## 实际wasm32/Node运行

复用现有已验证freestanding string.h/minilib和Node宿主方式。链接旧P4 C99与新copy4 C99及轻量导出桥；导出prepare、新apply、sizeof和固定buffer地址，禁止宿主误调旧apply。实际检查WebAssembly.Module.imports为空，记录Clang21/wasm-ld/Node版本、产物SHA、导出入口和真实sizeof。wasm32五word模型预计20B，必须由运行时sizeof确认，不能提前写成实测。

线性内存固定32MiB、测试栈预算64KiB，ROM12,633,124B；按单张照片2,359,296B及独立src/dst分批输入输出，不将235MB百图整体放入模块。模型、ROM、I/O arena、栈预算分别列；32MiB是测试夹具而非核心RAM或MCU实板成绩。标准C99核心仍零堆，宿主Node Buffer和文件缓冲不在此承诺内。

完整256³输入按已认证的外部R高位顺序分块生成，原地与分离各运行一次，流式SHA必须等于`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。完整百图逐张读入，两种输出模式各自累计SHA必须等于`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，并与9f6b8f22质量原件中100个独立u64 oracle逐图摘要比较。输入照片文件还核e13278…原SHA，不能仅看输出或重读旧结果冒充wasm执行。

有限合同固定覆盖0、1、7、8、9、31/32/33、64、65535/65536/65537及原生已声明长度，原地/分离、非对齐和哨兵；palette count1/256、全部ID0..255、最大4096页、最后map/pool、ROM偏移0..7、所有21格式拒绝和Model/ROM部分重叠无写拒绝沿用。WASM无进程内NOACCESS页，不能直接冒称原Windows guard已重验：分别把src、dst或完整ROM尾放到线性memory真实末端，任何额外跨尾读写将触发WebAssembly.RuntimeError；其余缓冲区置不相交区域。必须清楚记录该真实边界与普通哨兵的区别。

关闭/清零是C模型和宿主借用生命周期，不声称WASM有WinAPI句柄。实际计数、模块无imports、完整流/逐图摘要和首失败均原样保留，不借原生AVX控制赋予新的纯C99成绩。

## ARM/RV32/大端仅对象层

另将相同旧P4 C99和新copy4 C99分别编为Cortex-M3、RV32IM和AArch64BE对象，共六份，使用现有freestanding支持头、严格C99和对应显式target，不用native参数。核ELF class、machine、端序以及新/旧符号存在，记录全部编译命令、版本、输入/输出SHA。

预期分别是ELF32/ARM/LE、ELF32/RISC-V/LE、ELF64/AArch64/BE；这些只作编译器目标与标准C99接受性证据，没有BSP、链接实板、QEMU或真实BE执行。原字节memcpy4不依赖host uint32解释，是设计依据；对象通过不等于已在ARM/RISC-V/BE硬件运行，也不证明闪存等待、栈峰、功耗或硬实时界限。

此阶段不重复census、不新增压缩格式、不更改原生DLL；静态ABI投影、wasm实际sizeof、原生函数静态帧、32MiB夹具及板载RAM需求必须分别报告。
