# 唯一Q16 cubic Lagrange基负结果归档

本阶段只研究一个明确4点/轴、64顶点Q16张量基。完整均匀未舍入L2矩MSE=1.972246046，比冻结matched四面体1.852670449恶化6.454229%，未达预声明20%改善门槛，因此没有评价探针或运行整数64顶点/Horner对照、native、新完整cube或百图。没有SLUT或已落地的新算子。

[中文报告](report.md)、[冻结计划](plan.json)、[运行身份](run.json)、[数值回执](results.json)与[清单](manifest.json)保存实际范围和SHA。basis-and-nodes.npz包含三轴256行start/Q16权重、连续/RGB8节点和原grid/idx/frac；连续节点不可部署，RGB8节点payload不等于旧tetra/tri_float语义支持。measured-source.zip保存实际源码、计划和依赖。

matched-reference-results.json是本阶段唯一比较基线的训练矩来源，不能改用更弱参照后倒填本轮成功。baseline.slut及baseline-grid.npy仅为原2dd坐标/容量身份；fixed-probes.npz虽然随档保存，但本轮没有读取其颜色作输出评价。

复现命令见报告，需要同SHA的原完整RGB8表和计划中的原路径。归档不含50MB大表，也不包含新的完整输出。已有source文件和表来源继续沿用原项目合同。该基使用有效索引坐标的三次多项式，不能把它描述成真实非均匀物理knots插值或所有高阶方法的结论。

权重常量、精确有理误差、索引和signed int64绝对界已检查；未执行的整数前向不能宣称oracle通过。浮点矩和残差没有舍入区间，不是严密全局证书。负结果按冻结规则保留，不扫描或调整阈值。未提交、推送或创建PR。
