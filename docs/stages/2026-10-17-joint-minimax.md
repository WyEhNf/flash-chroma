# 联合质量目标与源参考独立核验

Agent：Codex；Operator：WyEhNf；Task：PR31后续算法/误差原因研究；Status：In Progress（执行前冻结）。

## 问题及改动

PR31已得到完整验收的四节点解，max52、历史缺口1579。但其目标是先规定max≤52、再最小L1，不能说明该箱没有更低max或相同max下更好的缺口/SSE。另一个仍需区分的问题是：原热点附近参考B从0到130的陡变，是否由Hald转换造成。

本阶段沿PR31头5422b05，从已测模型`3f9706867425a36ccba62ed6abf79c49e1ef2e805ed109b9b7d09eb2b9a72be6`继续，同一反例导出的四节点B通道±4整数箱，保持全部原历史/固定101组、完整域mean/RMS/p99端点/max/CVaR和缺口不升。只求一个冻结问题，不进行逐级max试探或参数/网格/方法矩阵。

新增`joint_minimax.py`按整数目标`(全域max平方,历史缺口,全域SSE,L1)`字典序直接优化，起点作为已验证可行解。未固定“下降一级”的目标，因此同max下仍可改进缺口/SSE。沿用Q16区间/逐图必要界，再加质量目标下界剪枝；每条剪枝需此前可行回执和完整终端覆盖证书，精确叶子仍走全部原保护，不用内部目标替代最终验收。

历史缺口下界的理由：每个阈值的代价等于正部`max(d²−t,0)`中最小`N−budget`项之和，逐项误差增加不能降低该和。把每个待定像素的平方误差替换为独立区间最小值，就给出该组代价的必要下界；未影响像素及未活跃组沿用旧频数。全域SSE直接使用同一逐色下界，L1用已固定前缀。字典序下界不优于已验证可行解才能剪枝，不能把L1提前成主要目标。标准库验证器另用Counter/整数权重复算目标界、叶子、遍历和完整覆盖，结论只限冻结箱与固定保护。

频数只依赖图片/取样与颜色；节点变动不改变颜色频数。复用PR30同几何idx/frac的完整支撑/频数，核旧模型几何和旧局部字节，随后用PR31完整流核新基线，重新写入支撑与单元的基线哈希/输出；不把旧模型字节或旧指标冒充新测量。

## 源参考审计

`audit_hald_reference.py`使用Pillow独立解码原RGB8 TIFF，不调用项目的tifffile/source_lut/NumPy/Numba解析或插值。Hald节点以`r+n*g+n²*b`线性像素序寻址；三线性坐标用整数商余，8角权重分母恒为255³，RGB8 half-up由整数有理数直接计算，不受浮点半值误差影响。要求未旋转RGB方图，原图和参考SHA保持。

R-fast约定与[FFmpeg 9.0原生Hald读取循环](https://www.ffmpeg.org/doxygen/9.0/vf__lut3d_8c_source.html#l01327)一致：按B/G/R嵌套遍历像素并写入RGB索引。这里只引用布局依据，没有运行FFmpeg或做其精度/性能比较，不推断源作者色彩空间。

审计范围一次覆盖原7857色完整热点支撑，加三个已冻结探针[251,251,42]/[255,255,42]/[255,255,49]的±1邻域和8个RGB角点。保存3个原始8角像素、有理权重/分子、缓存字节、SHA、Python/Pillow版本。若不一致则保存结果并停止优化，不更换参考或放宽阈值。隔离标准库复核范围/缓存流/源码SHA和3份有理见证，但不冒称在-S环境重新解码TIFF；不覆盖全部256³、其他源LUT或第三方色彩意图。

## 阶段验证、环境与复现

冻结源/计划后集中6项合同：新目标2项分别验证直接降到箱内可达更低max、同max下允许历史缺口改善（含严格相等mean）；Hald身份/通道置换解析对照1项；回归原区间联合3项。一次正式优化，最多4节点/10000赋值；只对一个新最优模型一次256³/100图/独立NumPy整数oracle/原生scalar和AVX2终验，不变则复用父终态。20历史审计只最终观察，已见数据不称盲验。

环境：Windows11 10.0.26200、Ryzen9 8945HX16核32线程、RAM33605316608字节；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0；BLAS/MKL/OMP1，Numba4。Pillow实际版本在审计结果记录。新优化为NumPy整数有限分支，源审计为Pillow解码/标准库整数，目的为算法精度、源语义和严格证明，不作性能比较。原生既有GCC15.2 Release单线程scalar/AVX2，程序SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`。

```powershell
# python使用artifacts/error-study-py312/Scripts/python.exe，并设置上述UTF8/线程环境。
python -m pytest tests/test_joint_minimax.py tests/test_hald_reference_audit.py tests/test_joint_interval.py -q
# 移除NUMBA_NUM_THREADS，由runner设置4。
python scripts/run_joint_interval.py --plan experiments/joint-minimax-v1.json --output artifacts/joint-minimax-v1
python -I -S scripts/verify_extreme_cell.py --input artifacts/joint-minimax-v1 --output artifacts/joint-minimax-v1/verification.json
python -I -S scripts/report_extreme_cell.py --study minimax --input artifacts/joint-minimax-v1 --output report/data/joint-minimax-v1 --roundtrip artifacts/joint-minimax-roundtrip-v1
```

## 协作与限制

已fetch，main仍dec1020且为祖先；工程修复337a3dd保留，AGENTS.md只读，默认/冠军、运行时、embedded、格式与硬件后端不改。创建/更新中文Draft PR前刷新相关正文/完整评论/review/行内线程、#7/#8与主题检索，Discussion4访问缺口保留，不合并/关闭。Operator为WyEhNf。

官方数据/Threshold仍未知，距离为RGB欧氏码值，非CIEDE2000；单级有限箱结论不代表四级ISP或实板收益。源区间必要界42与当前52不是同一类最优声明。本阶段结果、拒绝、来源和CI执行后补记。
