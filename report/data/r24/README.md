# R24 可核验记录

- [原始证据归档](r24-evidence.zip)：11组完整节点支撑候选、两个新种子的2组基线、CPU/CUDA全色及100图结果、节点支撑及曲线模型兼容检查、7对完整拟合比较、热点诊断和源码快照。
- [文件索引及SHA256](evidence-index.json)：每个文件均经解压回读核验。
- [未舍入精度摘要](accuracy-summary.csv)、[配对拟合摘要](paired-summary.csv)与[方法、反例和结论](../../../docs/r24-supported-fitting.md)。

以仓库根目录为解压根，恢复至`artifacts/r24-supported/`。历史模型与来源由[R22](../r22/README.md)追踪，本轮CUDA二进制来源见[R23](../r23/README.md)。完整原始LUT、图片和程序不装入小型归档，其SHA在验收报告及manifest中记录。

本轮建立了数据Hessian的完整节点支撑，但没有证明最终精度或完整拟合速度更好；11组中仅7组通过本地示例均值门槛，7对完整拟合比较中新候选全部更慢，故保持显式研究候选。官方测试集和Threshold尚未取得。
