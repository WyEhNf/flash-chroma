# Linux服务器入口与固定字节包证据

[阶段说明](../../../docs/stages/2026-10-20-skylake-server-entry.md)给出目的、实际环境、变更、复现、ABI声明修正和未执行范围。本阶段只在同AMD主机的WSL2验证，不是Skylake测试。

`initial-bundle-manifest.json`与`final-bundle-manifest.json`绑定所有原始输入、冻结源码和数据源；最终88项共约338MB，预解码100图235929600字节SHA与Windows已测组完全相同。原始像素及完整RGB流只在本地188MB传输ZIP，不提交Git；具体大小、ZIP SHA及源码变化见`final-bundle.json`。

`full-results.json`保留12组完整256³和528次有限对照；`linux-contract.json`保留2112次差值边界/后端/偏移比较、32条布局保护、14条计时器拒绝、回调失败中止及8组100图调度输出SHA。`linux-run.json`包含客体拓扑及绑定，`linux-policy.json`绑定实际库/编译器和调用规则；`linux-results.json`明确`performance_measured=false`。没有正式性能结论。

`server-measured-source.zip`同时保存初稿与最终源代码原字节、包内操作说明和只读派生脚本。初稿回调声明的const已修正，最终增加类型相等编译期检查；`equality.json`证明对象与共享库逐字节相同，因此复用相同机器码正确性而不重跑。`linux-binaries-and-abi-objects.zip`保留两后端、两版本计时器对象和共享库。构建日志、完整核验入口的源码ZIP亦保留。

正式四进程/两种调度性能分支留待目标服务器；先检查实际SKU、系统、微码/GDS、内存及允许CPU集合。服务器需要Python标准库、CMake、GNU C/C++与OpenMP，不需要NumPy/SciPy/Numba/Pillow；本地导出器使用已有拟合环境生成小型整数预期，未运行原生、拟合或性能。没有升级默认或宣称官方成绩。
