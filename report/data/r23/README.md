# R23 可核验记录

- [原始证据归档](r23-evidence.zip)：新CUDA全色输出核对、分组1/7/100的100图输出核对、三条测速路径的字节比较、7对新旧GPU比较、构建记录与源码快照。
- [文件索引与SHA256](evidence-index.json)：逐文件解压回读校验。
- [配对性能摘要](paired-summary.csv)与[环境、结果和限制](../../../docs/r23-cuda-memory.md)。

以仓库根目录为解压根恢复至`artifacts/r23-gpu-memory/`。精度及旧GPU来源引用[R22归档](../r22/README.md)，不重复拟合或推断官方得分。完整图像、LUT和本地二进制不装入小型归档，其SHA在报告中固定。峰值450 MiB只指`bench`的显式设备图像分配，排除模型、驱动及宿主内存；未证明速度改善。
