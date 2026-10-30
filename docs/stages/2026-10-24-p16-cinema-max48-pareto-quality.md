# max48见证对三个固定基线的独立质量资格

Agent：`/root/tail`。Operator：本任务用户。状态：独立完整域与100图质量资格完成；速度50%底线尚未证明，未切默认。旧minL1相对max_first的六项预算失败和STOP保持。

741e55f见证的mean虽然略高于局部max_first，却低于已经完整验收的综合best及共同a399基线，max也更低。因此本阶段另立协议，冻结同一个候选，直接对a399、综合best和max_first三个分母验证，不把旧局部失败改判，也没有求解、拟合、改节点或使用100图择优。

候选首级NPZ SHA `741e55f55c674384543511dc20b98ecd7d6a1ed4c1b9bb17406cabd7cc86bea0`、SLUT SHA `59c333adb5480244ea0e22808f625259a94a21d3b7e53c28656f7362990627f4`，后三层904e/95cb/5b8及85b0侧表固定。三个原完整流分别为a399的3c9ce8d9、综合best的373a2fcb、max_first的143e5cc0；完整SHA和模型字节记录在identity与frozen。新候选完整流SHA `de4a98d5f3b3d430e349e83146d211296a4e6b3e2a9664a5806b321384a3c3f9`，100图输出SHA `b61b35171a12b9e4cabf45f4f27c04e94489859161488b8543360c527d11bef8`。

## 验证覆盖

执行前对新driver通过独立AST，冻结119份源文件和29项固定输入。119份包含整个lutlab目录的保守快照，含尚未执行的窄域helper；“冻结包含”不表示这些文件均在本阶段实际执行。实际依赖包括Q16四级oracle/Numba、SLUT和分输出侧表读取、原生加载器和只读诊断。

完整16,777,216输入逐级独立uint64与Numba相等，四张原始lut256逐级RGB8真值与ec79参考相等。四模型分别执行同一个冻结87DLL的scalar1、AVX2-1、AVX2-4，各有原地和真正分离输入输出，共24完整域配置，全部逐字节等于各自完整oracle；分离输入逐次核未改变。100张历史照片四模型实际AVX2-4共400次逐图执行再与完整流索引交叉，零不一致。原60图完整重建47,185,920像素，并与旧L1的完整支撑观测精确一致；100图总78,643,200像素。100图只验不调，不声称盲测。

## 聚合质量和逐图代价

| 范围 | 模型 | mean | p99 | max | RMS | 最差1% CVaR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 全域 | a399 | 0.981110597 | 3.741657387 | 8.124038405 | 1.368970526 | 4.655382041 |
| 全域 | 综合best | 0.822502847 | 3.464101615 | 7.549834435 | 1.225513544 | 4.095497757 |
| 全域 | max_first | 0.799073807 | 3 | 7.071067812 | 1.197668459 | 4.029054534 |
| 全域 | 本候选 | 0.799665898 | 3 | 6.928203230 | 1.198763758 | 4.042947782 |
| 100图 | a399 | 0.810320559 | 3.741657387 | 8.124038405 | 1.263042774 | 4.666741983 |
| 100图 | 综合best | 0.695486159 | 3.464101615 | 7.549834435 | 1.156600954 | 4.321238008 |
| 100图 | max_first | 0.679090181 | 3.464101615 | 7.071067812 | 1.135171882 | 4.304139590 |
| 100图 | 本候选 | 0.679109463 | 3.464101615 | 6.928203230 | 1.135212195 | 4.304630062 |

相对a399，完整域、100图合并、原60图及每一张照片的五指标全不退，最劣逐图保留100%。相对综合best，三项聚合的五指标也全不退，但逐图仍有代价：mean/RMS各99好1差，p9928好70平2差，max76好23平1差，CVaR77好23差。最劣来自`div2k-0811`的p99由sqrt12升到sqrt17，保留84.016805%，只过80/70/60/50档；mean最差是`div2k-0868`的0.111678977→0.115349355。`dped-sony-092`的p99由sqrt17升到sqrt22，`div2k-0823`的逐图max由sqrt41升到sqrt48，全部保留在原始逐图结果。

相对max_first，23张照片mean/RMS小幅退化、77平；p99全100平，max5好95平，CVaR14差86平；最劣逐图保留99.689698%。旧六项原全域/训练mean、RMS、CVaR失败没有被公共分母的改善抹去。报告对三个分母均保留100/90/80/70/60/50六档，没有只展示有利分母。

非官方实验阈值严格`每图max<T`：

| 模型 | T=4/5/6 | T=7 | T=7.5 | T=7.7/8 | T=8.2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| a399 | 0/0/0 | 17 | 17 | 96/96 | 100 |
| 综合best | 0/0/0 | 28 | 30 | 100/100 | 100 |
| max_first | 0/0/0 | 96 | 100 | 100/100 | 100 |
| 本候选 | 0/0/0 | 100 | 100 | 100/100 | 100 |

这些T沿用研究对照，不是官方阈值、官方得分或通过许可的声明。

## 首级忠实度和运行时代价

这是整链联合目标。首级对原table1的独立全域mean：a399为0.332375912，综合best/max_first为0.660506730，本候选0.661249797；首级max分别sqrt66、sqrt59、sqrt70。新候选首级p99仍sqrt3，CVaR由综合best的2.325511291升到2.344832758。整链改善不表示四张源表各自更忠实；基线综合best本身已有首级与整链之间的取舍。

同87库实际模型计账容量a399为18,579,204B、综合best18,715,680B，两者仍format9直接表；max_first为1,938,464B、whole-cache palette603，候选1,976,676B、palette604，两者均失去direct并走精确fallback。不能把少掉16MiB直表当成综合内存优化成功，或据同库质量通过推断速度≥50%。此处capacity为库的计账，prepare诊断原值也保留；没有本阶段进程RSS或正式配对吞吐结论。

独立离线审计复算16组整数直方图、24完整流身份、300逐图比较/六档/T和全部冻结字节，全部通过，没有重复原生像素。环境是Windows x86-64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4/Numba0.60.0、冻结87 SHA58591a72；Numba/OMP4线程、BLAS1，质量共享主机。未使用AVX512。旧L1失败仍在原阶段，`overall_upgrade=false`。

主要文件为`experiments/p16-cinema-max48-pareto-quality-v1.json`、`scripts/qualify_cinema_max48.py`及独立审计。归档`report/data/p16-cinema-max48-pareto-quality-20261024`包含完整源快照、四实际模型链、直方图及原始逐图报告；50MiB新完整流留在artifacts，以固定SHA和模型/源可复现，不放Git。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/qualify_cinema_max48.py --cache-root 'F:/Hackathon/projects/16-lut-color' --library 'F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll' --frozen artifacts/cinema-max48-pareto-quality-frozen-v1.json --output artifacts/cinema-max48-pareto-quality-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_max48_quality.py --output artifacts/cinema-max48-pareto-quality-audit-v1.json
```

后续可对这一固定点另验原生表示/速度，但任一有效最劣吞吐低50%仍不得综合升级。侧表及针对固定后缀的整链联合语义的官方许可尚未知，PR保持研究边界。
