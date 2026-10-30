# 用等距后缀核对四级精度改善

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成。本地研究，不PR、不推送。

前阶段预声明Filmic04→05→06→07链的原17³/33³解析整链误差已经全0，局部误差被后级吞掉，已按原口径停止而非换源重选。为检验真正的误差传播，另立本阶段计划`experiments/filmic-isometric-chain-v1.json`：Filmic06→循环通道(G,B,R)→逐通道反相→交换R/G。四张完整原LUT各不相同、独立拟合，每级输入输出RGB8。

后三段是非中性且保持RGB欧氏距离的已知控制，不冒充自然ISP家族；整个后缀是对首级输出反相并倒序通道。因此首级误差不能被它吞掉，完整链误差分布应与对应首级误差相同。这是有可解释黄金结果的四模型运行时验收，不是从大量自然链中挑出有利结果。

比较原supported DP17³、原supported DP33³、新calibrated17³，共三个固定版本。新17必须各级解析精确、参考非恒定且整链mean严格优于原17才一次完整256³/100照片/独立整数oracle/标量/AVX2/C99验收；完整验收要求mean/RMS/p99/max全部0，字节一致。任何失败如实保留，不改源、节点、偏移或容量追补。

通过真实`python -m lutlab fit`统一入口和不可变缓存得到模型；新政策只对完整验证的逐通道单轴来源解析half-up区间及实际单调可行域，不能精确时明确回退，默认方法和既有68来源扫描不变。与单LUT历史相比，此阶段增加真实四张独立原表、置换/下降曲线、逐级RGB8及C99比赛入口的覆盖；不能把单级五后端计数和本轮三后端混写。

测试目的为受控四级链精度、运行时正确性、统一入口/缓存与容量；不测性能。Windows11 26200 x64/Ryzen9 8945HX，Python3.12.14/NumPy1.26.4/SciPy1.15.2/Numba0.60.0；Numba4、OMP/BLAS/MKL=1，CLI子进程NUMBA_NUM_THREADS=4。GCC15.2 Release原生程序SHA ba088c68…，三后端各1线程。

复现（仓库根目录，PYTHONUTF8=1并设置上述线程环境）：

```powershell
artifacts/error-study-py312/Scripts/python.exe scripts/run_filmic_chain_calibrated.py prepare --plan experiments/filmic-isometric-chain-v1.json --output artifacts/filmic-isometric-chain-v1
artifacts/error-study-py312/Scripts/python.exe scripts/run_filmic_chain_calibrated.py accept --plan experiments/filmic-isometric-chain-v1.json --output artifacts/filmic-isometric-chain-v1
```

## 完整验收结果

统一CLI三个调用和缓存校验均成功，四张实际完整原表SHA各不相同。新17³四级实际route均为exact_monotone_calibrated；源06首级模型SHA精确复现d8186ab6…，其余三级也各自精确。

|版本|全域mean|全域p99|全域max|百图mean|最差单图p99|百图max|四模型文件字节|
|---|---:|---:|---:|---:|---:|---:|---:|
|原DP17³|0.114535154|1|1.732050808|0.125110668|1.414213562|1.732050808|75196|
|原DP33³|0.057927017|1|1.732050808|0.063910818|1|1.732050808|448252|
|解析17³|0|0|0|0|0|0|75196|

同一新17³的完整域、百图RMS/CVaR也均为0；相对两个基线各100图五项指标都改善。原基线指标恰与单级Filmic06一致，符合等距后缀的黄金推导，未将另一条自然链的零误差算作收益。

三个版本各一次完整256³映射，Numba与独立uint64四面体逐级RGB8输出一致；每版标量/AVX2/C99共9份完整原生回执零字节差异。新17³额外实际AVX2百图拼接流核验通过。新完整流SHA b27f34aa9a5326210752e63db78987d07b76729a066f8d050d5ff5b880eba9f5，等于四张原表逐级RGB8参考流。

完整指标、300条逐图、12模型、统一CLI原始命令/stdout/stderr、缓存manifest及数值源快照归档`report/data/filmic-isometric-chain-v1`。本阶段运行身份1fef653d185b544406e8e382f6c78291c5c29c45f5afd2b1dc14ae660b63e242。文件容量相对原33³减少83.22%，不据此推断运行时间，速度与程序内存见独立性能阶段。

所有照片历史已见，未用于生成坐标；RGB欧氏码值距离非CIEDE2000，官方Threshold/数据未知。模型字节相同不代表同一几何插值函数族；不宣称通用四级精确、官方通过、SOTA或实板结果。
