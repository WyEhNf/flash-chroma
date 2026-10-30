# 单头文件三维配置交付证据

完整解释见[阶段报告](../../../docs/stages/2026-10-27-p16-frontier-header.md)。本目录覆盖5套模型、20种配置、40个热批次/首批指标点；7套模型包中max41/max48没有本轮新库性能资格。两个场次保留四个比较上下文，未混排速度。

`catalog.json`可由连续偏好/预算选择器读取，模型manifest与evidence均使用相对路径；`results.json`为完整逐配置汇集，ZIP保留实际执行字节、原始中断记录及逐图精度。`quality.json`为20条C++及5条C99完整RGB8输出检查。`selected-*`、`png-roundtrip.json`记录真实100图部署运行及独立参考精度。

`timing-correction.json`纠正原部署回执中的哈希计时说明：应用wall包括PNG文件SHA，不包括后续像素SHA，原数值保留。A/A通过16配置、失败4配置，失败点不进入默认严格速度选择；首批单次观测均无稳定时间资格。

静态核对命令：

```bash
python scripts/verify_frontier_evidence.py --evidence report/data/p16-frontier-header-20261027
```

该命令核成员与模型SHA、配置、统计、资源及场次身份，不重跑像素映射或性能。Linux/MSVC/目标机、实板、官方Threshold及未知LUT结果不能从本机记录外推；远端构建/QEMU结果以当前PR实际检查为准。
