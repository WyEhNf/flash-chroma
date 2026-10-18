# 内点地址复用的固定实验档案

[中文阶段报告](../../../docs/stages/2026-10-19-channel-runtime-reuse.md)说明对象、环境、目的、输入、结果与限制。唯一候选正确性通过、性能失败，不替换已验收的packed v3。

- `geometry-profile.json`只读轴表分类，不映射像素。
- `native-results.json`记录单级与等距四级完整色域、100张原图的字节核对。
- `benchmark-results.json`、`performance.csv`及`evidence.zip`中的worker记录保留唯一同机串行比较。
- `policy-audit.json`从原轮次重新计算预声明门槛，`performance_accepted:false`；没有增加数值或计时调用。
- `evidence.zip`保存地址分析、集中合同、构建、完整原生与性能的run/plan/源码ZIP/原始轮次日志。
- `binaries.zip`含新旧独立DLL、实际GCC运行时依赖和链接核心静态库。SHA见其中对应build/plan。旧模型、3e5 NPZ和三个控制模型沿用[已有档案](../channel-native-v1/README.md)，未重复拟合。

复现命令见[commands.txt](commands.txt)。输出目录不能覆盖既有证据；若路径已存在，使用新目录并同步计划中明确的SHA。原100图在项目assets清单内，完整约50MB RGB流留本地，来源/输出哈希均冻结在run/plan中。测试为Windows x64 AVX2/OpenMP研究库；不代表C99、其他ISA、真实自然ISP、官方数据或Threshold。
