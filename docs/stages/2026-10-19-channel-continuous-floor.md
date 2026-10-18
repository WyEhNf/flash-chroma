# 固定分通道几何的连续节点空间诊断

Agent：Codex；Operator：WyEhNf；状态：冻结诊断完成；未commit/PR/push。

新增独立计划`experiments/channel-continuous-floor-v1.json`和`scripts/explain_channel_continuous_floor.py`，不修改旧模块。固定3e5的全部shared idx与各输出权威frac，以原Velvia表在完整均匀RGB域上逐输出组装一次uint64 H/b（共3次）、各解一次无ridge连续LS，不通过grid重生frac。保存原始矩、连续证据节点/残差、独立整数支撑和有理下界。

新几何连续均匀L2 MSE约1.84708523234，相对旧共享几何1.85267044872仅降0.30147%。但当前RGB8节点未舍入MSE为2.57789472265；clip后的合法连续Q20点为2.14577819321，仍有16.7624%的连续可行空间。该点不是RGB8节点或部署模型，不保证原加权真实RGB8距离/照片mean/p99收益，也不能因局部±1收益小而宣称全局最优。

主证书完全用Python整数/Fraction、一阶凸性及[0,255]盒，不依赖SPD：未舍入MSE≥146335093803017038629881354575/79228162514264337593543950336≈1.84700855301>3/4，故此冻结几何合法节点不可能全域RGB8零误差；有理平方比较严格得到最终RGB8 RMS>.492。另对新几何独立最近RGB见证余量77683/70936/64779，均通过；没有套用旧几何证书。

环境Windows11 26200/Ryzen9 8945HX、Python3.12.14/NumPy1.26.4/SciPy1.15.2，原生完整矩请求/实际4线程、BLAS1；CG各25步、相对残差均<1e-12。用途为连续表达与精确下界；0像素映射、0部署模型，无样本/百图/full输出或性能。详细范围、原始矩/库/输入身份、证明与复现命令见[精简归档](../../report/data/channel-continuous-floor-v1/README.md)。

根代理另以CPython3.13.12标准库、独立NPY解析器和逐边Python整数矩乘，复核全部三路盒下界、clip连续可行点及当前节点MSE，并以有理平方比较严格验证最终RGB8 RMS>123/250。命令：`python scripts/audit_channel_floor.py --input artifacts/channel-continuous-floor-v1 --output artifacts/channel-continuous-floor-v1/independent-audit.json`。这次审计没有重新组装矩、求解或映射像素，来源和环境另存归档。
