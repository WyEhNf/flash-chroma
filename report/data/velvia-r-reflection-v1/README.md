# 唯一R反射负结果归档

同一Velvia完整RGB8均匀L2、同物理网格m33，R反射改变四面体划分后，连续矩MSE=2.816171668979223，相对matched标准1.8526704487157986恶化52.006077%。未达预声明20%改善门槛，按计划停止。

[报告](report.md)、[冻结计划](plan.json)、[运行身份](run.json)、[数值回执](results.json)、[文件清单](manifest.json)保留来源与范围。reflection-nodes.npz含连续/量化节点、理想/存储grid及反射/折回idx/frac；raw-integer-moments.npz含反射域一次组装的原始diagonal/upper/rhs/metadata。measured-source.zip保存实际源码、计划与依赖，matched-reference-results.json固定唯一同目标比较基线。

没有评价固定探针，未生成SLUT、执行独立前向oracle、native、新完整域输出、百图或性能测试。节点数组不等于可部署模型或运行时已验证。浮点LS矩目标/残差不是带舍入区间的严格证书。

这只是一种固定反射在当前连续L2目标下的负结果，不是对所有反射或所有RGB8/照片目标的结论；没有改换G/B、对角线或门槛。旧固定坐标严格证书不能套到此设计；降序权威表参数化也未被当作官方认可。没有修改核心、默认、根驱动或提交推送PR。原表、matched节点等同SHA输入及完整复现命令见报告，归档不包含50MB大表或新全域输出。
