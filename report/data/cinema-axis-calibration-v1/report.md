# Cinema四级链：实际到达频数与整链尾部保护

同一冻结候选完成256³和100张完整1024×768 RGB8照片验收。仅第1级模型更新，其余模型逐字节不变；每模型112063字节，m33，采用单调校准Q16坐标表，插值函数族已扩大。基线由run计划绑定，可能已含前一阶段改善，不能一律称PR16。

|版本|范围|mean|RMS|p99|最大误差|CVaR1%|
|---|---|---:|---:|---:|---:|---:|
|baseline|cube|1.097405|1.510090|4.358899|8.774964|5.056274|
|baseline|photos|0.900428|1.398568|5.196152|8.774964|5.076521|
|candidate|cube|1.016505|1.410656|4.123106|8.124038|4.778482|
|candidate|photos|0.850501|1.321702|5.196152|8.124038|4.826946|

照片p99为最差单图p99，CVaR为平均逐图CVaR。逐图完整明细见photos.csv，全部变化及60/20/20分组在完整结果中。

完整门禁：{"accepted": true, "failed": []}。独立整数oracle与标量/AVX2/C99完整流同SHA：78ebea523d67db084c045369697a8dd3b906b37e35517d6cf52c3fd7349a096f，零字节差异。

100图各指标变化：{"mean": {"better": 99, "equal": 0, "worse": 1}, "rms": {"better": 99, "equal": 0, "worse": 1}, "p99": {"better": 67, "equal": 32, "worse": 1}, "max": {"better": 72, "equal": 28, "worse": 0}, "cvar_1pct": {"better": 99, "equal": 0, "worse": 1}}；不宣称每图每项支配。完整包络回执：{"original_input_colours": 16777216, "violations": 0, "caps_file_sha256": "8c89f3ffb2bd1eccd2ed9961022e57766bf88919789194b4651cab2c5ffd74f5"}。

训练从60图全部47185920像素和原始完整cube的固定稀疏前缀到达频数构造，另保留0.10本级均匀测度。唯一拟合标签为第1原表；原始整链参考仅用于硬约束，后缀缓存执行固定其余稀疏阶段。

环境：Windows11 x64/Ryzen9 8945HX/Python3.12.14/NumPy1.26.4/Numba0.60.0，Numba4线程，BLAS/MKL/OMP=1；原生GCC15.2 Release三后端各单线程，程序SHA由run计划及回执绑定。不比较运行时性能。

复现：用evidence.zip内实测源码和run.json内计划执行run_cinema_rounded.py的fit/accept。模型在models.zip；大频数、质量、包络数组与RGB流留在本地artifacts，SHA已冻结，异机需恢复同字节原表/照片和历史证据并重建。

RGB欧氏码值距离，非CIEDE2000。所有照片历史已见，20审计只表示本阶段未反馈，不称盲测。官方数据/Threshold未知，不宣布官方通过或SOTA；无新速度、GPU、实板结论。默认不升级，未创建PR。
