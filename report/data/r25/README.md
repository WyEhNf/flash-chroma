# R25 可核验记录

- [原始证据归档](r25-evidence.zip)：11组固定尺寸全量拟合、两组合法m33容量扩展、CPU/CUDA全色与100图、15项检查、原生/参考组装及完整拟合配对、通过模型的CPU/CUDA映射配对、无OpenMP构建、两项数学诊断和源码快照。
- [文件索引及SHA256](evidence-index.json)：每个文件均经解压回读检查。
- [精度摘要](accuracy-summary.csv)、[容量摘要](capacity-summary.csv)、[配对性能摘要](paired-summary.csv)与[完整说明](../../../docs/r25-full-domain-fitting.md)。

以仓库根目录为解压根恢复到`artifacts/r25-full/`。历史基线引用[R22](../r22/README.md)与[R24](../r24/README.md)，实际CUDA程序来源见[R23](../r23/README.md)。完整原始LUT、图像、离线库及程序不放入小型归档，其SHA和构建命令在记录中保存。

固定尺寸11组全色mean均下降，但五组max增加、7/11通过本地示例均值门槛。两组m18裁剪失败在合法m33容量下通过；压力家族仍失败。官方测试数据、Threshold和判定口径尚未取得，不能推断官方得分。
