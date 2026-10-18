# 唯一Q16 cubic Lagrange基研究

Agent：Codex；Operator：WyEhNf；状态：完成并按预声明门槛停止，未PR、提交或推送。

在与matched算子阶段相同的Velvia完整RGB8原表、2dd m33小数grid与权威idx/frac上，构造唯一四点/轴Lagrange Q16张量基。前三权重由精确整数有理式half-up，最后一项守恒；保留负权重，显式64顶点，与旧tetra/tri_float不同。完整枚举768行通过常量守恒、有理量化误差、端点索引及signed int64绝对累加界检查。

仅一次float64轴SVD/全表张量拟合，目标是完整cube均匀未舍入L2。训练矩MSE为1.972246046，相对冻结matched四面体1.852670449恶化6.454229%，没有达到至少降低20%的预声明门槛。因此未评价原探针，也未执行64顶点整数oracle、新完整cube、native或百图；没有生成SLUT或改变默认/核心/原生代码。

环境为Windows11 26200/Ryzen9 8945HX、Python3.12.14/NumPy1.26.4、BLAS1。目的为单个新增函数族的数值可行性研究，不做性能测试。连续节点不可部署，RGB8节点payload相同不等于旧文件语义或后端已支持；浮点训练矩和残差不称严密全局证书。原始SHA、权重/节点、冻结计划、实测源码与中文报告保存在[精简归档](../../report/data/velvia-cubic-lagrange-v1/README.md)。不扩展为参数/基矩阵扫描，不宣称官方或SOTA结果。
