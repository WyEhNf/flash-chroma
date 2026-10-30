# 四网格正负斜率的获证路径有限补验

[阶段说明](../../../docs/stages/2026-10-20-skylake-domain-signed.md)记录覆盖缺口、实际环境、固定参数及命令。`results.json`保存m17/18/25/33四例、每例实际证书/启用状态和模型容量；两库×三种后端/线程×两种偏移共48次，每次8203像素，独立uint64 oracle与哨兵均零差。

`run.json`在生成前记录seed=2026102022、参数、Windows/AMD/Python/NumPy和原构建/库身份。`fixture-models.zip`保存实际首级、侧表及后三随机模型，`measured-source.zip`保存原字节生成器和运行源；原探针字节未导出，按冻结版本/seed/生成器恢复，不声称已保存。

没有新原生构建、拟合或性能；沿用修订4/16且真正fast_path_enabled=1，不以回退通过替代新路径覆盖。不代表四个模型的完整域、全部网格或Skylake成绩，也不替换比赛100图契约。
