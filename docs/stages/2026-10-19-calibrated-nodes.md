# 在校准坐标上继续降低首级量化误差

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成。本地研究，不创建PR或推送。

当前已验收链相对PR16全域mean降低20.42%、p99降低12.10%，百图mean降低17.72%，但最差逐图p99仍为5.196152。先用两组各16384点作剩余误差归因：均匀随机无放回seed2026101903；另一组按原60训练图完整原色频数有放回抽样seed2026101907。没有使用20审计图或百图尾部名单选择训练测度。

`scripts/explain_cinema_remaining.py`绑定已验收run、选择、四模型与完整流SHA，探针输出逐字节对应完整流，另各4096点核独立整数oracle。它记录每级向量分解、精确替换、固定基线尾部及最坏8色轨迹，不拟合、不运行完整验收。精确替换是反事实诊断，不能当作可部署模型或误差下界；各级收益存在交互，不能相加。

均匀探针首级精确替换mean1.022199→0.890435，p99 4.123106→3.464102，CVaR1% 4.868229→3.973521；训练照片频数探针mean0.853654→0.694286，p99 4.358899→3，CVaR1% 5.019904→3.492854。第三阶段精确替换仍让照片探针p99/CVaR变差，第二阶段mean/CVaR也变差。由此仅继续第一阶段，不扫描阶段组合。

前阶段固定节点校准了坐标，节点与坐标可能存在交互。冻结本阶段计划`experiments/cinema-calibrated-nodes-v1.json`：以当前完整已验收模型为严格基线，固定其idx/frac/grid及其他三级，只做一次4扫RGB8节点±1优化。目标仍为本级T1原表真实误差与固定稀疏后缀对同一T1标签的保持误差，两项1:1；质量仍为0.10本级均匀+0.45cube+0.45完整60训练照片。整链原表参考只检查逐色`max(49,基线误差²)`包络。

测试环境：Windows11 10.0.26200 x64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0，Numba4线程，OMP/BLAS/MKL各1。诊断目的为小样本因果归因；节点阶段为离线精度提议，不是性能测试。源码/数据/模型/程序SHA在plan和run内保存，独立源码zip绑定实际执行文件。

复现命令（仓库根目录，先设置上述线程环境及PYTHONUTF8=1）：

```powershell
artifacts/error-study-py312/Scripts/python.exe scripts/explain_cinema_remaining.py --run artifacts/cinema-axis-calibration-v1 --output artifacts/cinema-after-axis-attribution-v1.json
artifacts/error-study-py312/Scripts/python.exe scripts/run_cinema_rounded.py fit --plan experiments/cinema-calibrated-nodes-v1.json --output artifacts/cinema-calibrated-nodes-v1
```

全部候选冻结后只做一次固定262144色和20×4096照片样本选型。两种mean均须额外降低3%，RMS/p99/max及最差单图p99不退化，且至少一种合并p99严格改善。没有入围者则停止，不执行全域/百图；只有入围才一次完整256³、100图与整数oracle/标量/AVX2/C99验收，完整门禁保持此前标准。

## 实际结果：没有入围，不执行完整验收

四扫全部完成，完整训练目标0.676946→0.650049，改动坐标数依次5027/1828/601/159。最佳照片样本对应第4扫：颜色选择mean1.018027→1.012399（约0.55%），照片样本mean0.864485→0.852882（约1.34%）；两种合并p99均保持4.123106。四个候选均未达到两mean各额外3%及p99严格改善门槛。没有完整256³、百图、原生后端或性能测试，不用样本改善替代完整验收。

已停止本阶段扫数，不把未入围节点用于下一阶段。冻结证据与全部模型见`report/data/cinema-calibrated-nodes-v1`，另外的剩余误差归因也随报告归档。它说明已校准坐标后的节点有限邻域只有小幅收益，不证明其他节点或函数族没有更好解。

RGB欧氏码值距离不是CIEDE2000；官方数据/阈值缺失，不宣称官方通过、SOTA或新硬件加速。模型容量相同不证明运行时间相同；既有速度测量只覆盖上一已验收版本。
