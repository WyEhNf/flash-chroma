# R22 可核验记录

- [原始证据归档](r22-evidence.zip)：九组结构化候选、两组新家族的四组基线、CPU/CUDA全色与100图结果、28张旧模型的字节兼容检查、7对完整拟合比较、两次失败诊断及源码快照。
- [归档文件索引与SHA256](evidence-index.json)：逐文件解压回读核验。
- [精度摘要CSV](accuracy-summary.csv)与[方法、结果及限制](../../../docs/r22-structured-fitting.md)。

以仓库根目录为解压根，恢复至`artifacts/r22-structured-v3/`。历史基线由[R21](../r21/README.md)及[R20](../r20/README.md)追踪；完整原始LUT、图片和原生程序不装入小型归档，其SHA保存在报告与manifest。新家族可用冻结生成器复现；压力家族参数固定，种子不产生额外随机变换。官方测试集及Threshold尚未取得，不能据本地示例通过率推断官方成绩。
