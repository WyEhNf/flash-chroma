# Velvia固定坐标表达能力的严格证据

Agent：Codex；Operator：WyEhNf；状态：完成本地证书，未提交、推送或PR。

本阶段回答“如果原2dd的网格和权威idx/frac不动，只继续调整节点，能否最终全色域零误差”。结果是否定的：即使把RGB8节点放宽为[0,255]实数节点，该固定凸四面体的连续全域MSE也得到约1.852670448665647的严格有理下界，而最终RGB8全部正确要求连续MSE至多0.75。该证据证明这一特定函数族有表达能力障碍，不说明当前模型已经接近理论最优，也不排除继续降低mean/p99。

为避免前阶段浮点LS残差缺少舍入界的问题，这次只重新调用一次已验证C ABI组装旧原表的uint64正规矩，核SHA与matched阶段完全相同；独立整数见证重建正定下界6629704929/2⁴⁰。把已有连续系数精确转为Q20有理向量后，矩乘、二次型、残差及最终比较全部使用Python大整数/Fraction。还由纯有理比较证明最终RGB8全域RMS严格大于0.49。

环境为Windows11 26200/Ryzen9 8945HX，Python3.12.14/NumPy1.26.4，旧输入矩组装实际4线程、BLAS环境1。目的为数学和数值证据，没有拟合新模型，没有原生像素映射、新全域流、百图或性能测试。原始矩、见证、Q20向量、源码和身份见[精简归档](../../report/data/velvia-fixed-tetra-bound-v1/README.md)。独立入口为`scripts/prove_velvia_fixed_tetra_bound.py`，冻结计划为`experiments/velvia-fixed-tetra-bound-v1.json`；没有修改核心或默认。

该结论严格限原2dd权威坐标和合法RGB范围节点，不适用于无界节点再clip、新DP坐标/网格、轴反射或其它算子，不能据此宣称新候选无解。RGB距离不是CIEDE2000，没有新增官方数据或Threshold，也没有SOTA声明。
