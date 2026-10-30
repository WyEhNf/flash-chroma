# 修订38—42原始证据

本目录是缓存提示、大工作块、可逆地址置换及主词普通加载的研究检查点。新输出接口有超过3倍的本机结果，纯映射整体门槛未达到。没有Skylake实测，保持WIP；阶段说明见[报告](../../../docs/stages/2026-10-20-skylake-cache-hints.md)。

- [manifest.json](manifest.json)：194份原始文件的字节数与SHA；自身及之后增加的交付元数据不在清单中。
- [performance-audit.json](performance-audit.json)：五个候选直接对23的400轮旧模式、400轮真实输出独立复算，以及20项探索计数核对。
- [archive-check.json](archive-check.json)：21份源码ZIP、1583项源码成员及95项二进制成员逐项核验。
- 各`*-linux-build-v1`含实际动态库、对象ZIP及源码身份；`*-linux-full-v*`含完整RGB8验收；`*-linux-perf-v1`含全部worker、stdout/stderr、冻结策略和源码ZIP；`*-pmu-v1`为无墙钟成绩的单次配对计数。
- [42首次失败](skylake-wordload-linux-full-v1/failure-note.json)：旧16MiB容量断言没有同步为8MiB，原源和失败保留。只有full-v2作为42已通过验收；没有在失败后重测性能择优。
- [只读几何分析](skylake-skew-geometry-v1/results.json)、[PMU映射](pmu-mapping/results.json)、[磁盘/WSL限制](host-space/results.json)均不代表性能测量。
- [remote-check.json](remote-check.json)与`remote-snapshot.zip`保存完整协作意见检查；[primary-sources.json](primary-sources.json)记录一手技术来源及适用边界。
- `construction-and-validation-generators.zip`保存构造/冻结生成器；[input-reuse.json](input-reuse.json)说明已有模型包和大输入的同SHA恢复方式。

模型、精度口径和公共默认未变。照片已见，RGB欧氏误差不是CIEDE2000；派生表许可/预算和实际目标服务器仍待验证。不要覆盖旧测量路径或把不同进程协议、操作系统的绝对耗时相除。
