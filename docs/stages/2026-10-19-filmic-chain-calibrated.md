# 将解析校准接入统一入口并验证四级链

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成。仅本地研究，不PR、不推送。

单个Filmic06已证明17³可以在固定整数节点下精确恢复。下一步不是把同一个模型重复四次，而是预先固定Filmic04/05/06/07四张不同原LUT，按此顺序构成真实四级链。四张源SHA各不相同，但同属一个严格可分离家族；本阶段不能证明普通三维或其他四级组合也精确。

新增显式方法`ls_tetra_calibrated`，由`fit_model`返回带权威idx/frac的完整模型，旧的仅返回nodes/grid的`fit`接口拒绝此方法以防坐标被丢弃。CLI只允许`--mode seq --grid dp`，不改默认拟合方法，不把新方法加入既有68来源扫描配置。

先完整验证源和节点的逐通道单轴结构，支持通道置换及多个输出共用输入轴。把每个标签的half-up区间交原frac±4096、0..65536和固定端点；用有效坐标q的前缀最大下界与后缀最小上界构造完整单调可行域，将原单调q逐点clamp到该域。成功才称精确；不可行明确回退原结构整数DP，源非可分离则明确回退原通用补支撑，记录实际分派。每级目标始终是本级独立原表，没有照片、最终复合或残差标签。

`cache.py`绑定新增模块源码、默认参数及完整算法政策；统一缓存继续校验四源/方法/环境、保存模型SHA和实际route，防止新方法误命中旧模型，或模型序列化丢失自定义坐标。现有SLUTv1与原生内核不变。模型字段不增，但坐标函数族扩大，不能称规范几何插值只提高算术精度。

集中合同由`verify_separable_calibration.py`一次覆盖11项：下降/常量及通道置换、共享轴可行与冲突、端点冻结、不扩大偏移、逐码区间非空但全局单调冲突、节点结构破坏、无源证明回退，另精确重现已完整验证Filmic17/33模型SHA。该合同只证明解析与分派基础，不代替本阶段CLI、缓存、四级或原生验收。

冻结计划`experiments/filmic-chain-calibrated-v1.json`：三个版本一次生成并冻结，分别为supported DP的17³、33³和calibrated17³。首先只计算三条256码曲线的四级RGB8串联；仅新17³每级精确、参考非恒定且链mean比原17³严格改善，才各一次完整256³/100图/独立整数oracle/标量/AVX2/C99。若失败不换来源或追加容量。完整门槛为新17³全部mean/RMS/p99/max为0，所有字节一致。

环境：Windows11 26200 x64/Ryzen9 8945HX，Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0；Numba4线程，OMP/BLAS/MKL1，统一CLI子进程显式NUMBA_NUM_THREADS=4。原生使用已有GCC15.2 Release程序ba088c68…，三后端各1线程。目的为统一入口、独立原表语义、容量和精度验证，不做速度比较。

复现（仓库根目录，PYTHONUTF8=1且上述线程环境）：

```powershell
artifacts/error-study-py312/Scripts/python.exe scripts/run_filmic_chain_calibrated.py prepare --output artifacts/filmic-chain-calibrated-v1
artifacts/error-study-py312/Scripts/python.exe scripts/run_filmic_chain_calibrated.py accept --output artifacts/filmic-chain-calibrated-v1
```

prepare实际通过三个独立`python -m lutlab fit --inputs … --mode seq --grid dp --method … --m …`调用统一入口，再用相同内容身份查询不可变缓存；不会绕开CLI用临时内存模型冒充已发布模型。完整命令、stdout/stderr和缓存manifest全部保留。

## 实际结果：原链已经精确，停止完整验收

三个统一CLI调用均成功，缓存与模型身份核对通过；新17³每级实际route均为exact_monotone_calibrated，四级各自标签均精确。原17³和33³每级则都还有至少一处码值误差。

但三条链的解析全域mean/RMS/p99/max都为0：原始同家族串联的可达颜色与后级舍入已吞掉局部误差。本轮“相对原17³整链mean严格改善”的触发条件不成立，所以没有执行完整模型映射、百图或原生四级验收。不能将该链的零误差计作新方法收益，也不为追求通过而更换本轮来源。已停止并保存全部12模型、CLI stdout/缓存manifest和分析证据。

这是区分局部精度与最终链精度的直接反例。后续另立等距后缀控制阶段，检验首级误差能够传到最终输出时的新方法；该阶段与本轮计划、身份和报告分开。

照片历史已见且不参与生成坐标，不能称盲测。RGB欧氏码值距离非CIEDE2000，官方数据/Threshold未知，不宣称官方成绩、SOTA或实板；本阶段不覆盖性能和官方格式确认，不替换默认。
