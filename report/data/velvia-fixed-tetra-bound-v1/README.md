# 固定坐标表达能力的有理证书归档

对指定Velvia原表和原2dd固定idx/frac，合法RGB8或[0,255]节点的凸四面体无法全色域RGB8零误差。连续全域MSE严格有理下界约1.852670448665647，严格超过必要上限3/4；最终RGB8全域RMS纯有理证明大于0.49，浮点展示的较紧下界约0.49510297。

[报告](report.md)、[冻结计划](plan.json)、[运行身份](run.json)、[精确数值](results.json)、[清单](manifest.json)保存范围与证据。raw-integer-moments.npz保存diagonal/upper/rhs/metadata及idx/frac；rational-vector.npz保存Q20整数向量；witness-certificate.npz保存35937个互异见证、四面体索引/权重及对称余量。measured-source.zip保存本次实际脚本、计划、依赖和C ABI来源。matched-reference-results.json保留旧矩SHA与原证书来源，baseline.slut/grid只用于坐标身份。

原矩重新组装一次，SHA与matched完全一致；所有最终矩乘、二次型、残差及Fraction判定均为任意精度整数/有理数，未把浮点残差当作严格证书。该证据可直接从所保存原矩、向量和见证复算，不需要新的LS求解、像素映射或百图。

不适用无界节点再clip、新DP坐标/网格、R反射或其它插值算子。没有证明现有模型接近最优，没有给mean/p99或照片分布下界，没有新模型或性能收益，也没有官方/SOTA结论。没有修改核心、默认或根代理驱动，未提交推送PR。复现入口和环境见报告；归档不包含50MB源全表或新的完整域输出。
