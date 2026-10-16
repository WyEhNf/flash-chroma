# R52 远端整合与验证证据

本次先获取 GitHub 远端最新内容，再保存本地成果并合并 `github/main`。本地检查点为 `f72be5c`；整合基线为 `85f4a87`。本目录保留首次失败与修复后复查，未覆盖失败记录。

- [环境、构建与验收记录](validation.json)
- [配置日志](configure.log)、[构建日志](build.log)
- [首次统一门禁日志](correctness-first-run.log)：C++ 全色域通过；Python 21 项通过、1 项失败。
- [失败用例修复后复查](correctness-parity-recheck.log)：1 项通过。其余已通过用例未重复执行。
- [整合前 22 份数值源码哈希](preserved-sources.json)、[整合后一致性结果](source-preservation-check.json)：全部一致。

失败源于旧用例对所有后端统一传入单张 LUT，而 C99 和结构化 AVX2 后端要求四级链。修复仅调整测试：保留适用后端的单级验证，再用四种节点大小组成四级链核对全部已编译整数后端。未改数值实现。

本次为 Windows/MinGW 整合验证，不代表 Linux/Pixi、Docker、CUDA 或实体移动设备验收；未新增性能结论。完整研究矩阵仍停在 4471/7917 项，留出评价尚未执行。
