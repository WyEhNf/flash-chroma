# Filmic06：固定整数节点下的解析坐标校准

Agent：Codex；Operator：WyEhNf；状态：本地阶段完成。未提交、推送、创建PR或替换默认模型。

## 结果与范围

精确重建PR41的Filmic06完整参考及17³/33³结构整数DP模型后，只改变权威Q16轴坐标。33³在本轮原约束内做到完整RGB域及100张原有照片误差全部为零；17³的百图mean下降90.68%，仍有静态搜索边界造成的残余误差。

这是PR41同源、同解释、严格可分离的Filmic06特例，不是通用三维LUT或四级链普遍归零。全部指标为RGB8欧氏距离，非Lab/CIEDE2000。官方数据及Threshold仍未知。

| 模型 | 全域mean | 全域RMS | 全域p99 | 全域max | 百图mean | 百图RMS | 最差单图p99 | 百图max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PR41同字节17³ | 0.114535154 | 0.342326598 | 1 | 1.732050808 | 0.125110668 | 0.359975191 | 1.414213562 | 1.732050808 |
| 静态区间校准17³ | 0.011691964 | 0.108253175 | 1 | 1.732050808 | 0.011658709 | 0.108416677 | 1 | 1.732050808 |
| PR41同字节33³ | 0.057927017 | 0.242061459 | 1 | 1.732050808 | 0.063910818 | 0.255717051 | 1 | 1.732050808 |
| 静态区间校准33³ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

17³全域mean下降89.79%，百图mean下降90.68%；100图mean、RMS、CVaR均改善，p99为60改善/40持平，max为51改善/49持平，没有逐图退化。33³的100图全部五项指标均降至零。逐图记录见per-image.csv，完整原始回执见full-results.json。

## 来源和方法

原本的本地大模型缓存缺失。本轮按PR41合同重建，不修改或寻找其他源解释：3DL近恒等10bit shaper视为恒等，B最快，12bit输出缩放，三线性展开并clip/half-up为RGB8。完整参考经全部256³验证同轴可分离。网格采用24 probes的adaptive_dp_grid，节点经verified_axis_separable整数DP拟合。

恢复的三个历史SHA全部精确匹配：

- 源3DL：0846de8be0c34616b5d3375940ad9e6ab526cce760b5b1d3c5f1f3e97d2e2c4f。
- reference.npy：4662f6e49689e67cc801b9822808bbb17f0aaeacbc07ddf9f6e59a658e27559f。
- m17/baseline.slut：8ebe30d069d6a4e30a0413ba66f4c8ed8bd1c8c8cde1b630f150ed82d52cb750。
- m33/baseline.slut：225d8f66a2ecf196f464a9208507b2e5716c3cc4693488aab60bd177e13d0986。

设当前单元两节点为A/B、Q=65536、目标码值为t。half-up恰好得到t的条件为：

    (t-A)*Q-Q/2 <= (B-A)*frac <= (t+1-A)*Q-Q/2-1

分别处理正斜率、负斜率和常量，解析求整数闭区间。与0..65536、原frac±4096、静态相邻有效坐标中点区间及冻结首尾取交集；存在精确值时选择距原frac最近者，否则选择原固定区间内最小输出码值误差，再最小化坐标改动。没有放宽约束、扫描网格或根据照片调参。

静态中点区间保证同轴所有合法组合都单调。RGB8节点、idx和float32网格元数据保持逐字节不变；只修改frac。33³改15个坐标，最大偏移313；17³改27个坐标，最大偏移298，均小于4096。

这里改变的是单调可分离坐标政策，扩大了原几何插值函数族。它不是提高Q16算术精度，也不是修复运行时错误。PR41“原几何权重由浮点改Q16没有产生最终字节差异”的结论不被本轮推翻。±4096表示1/16单元坐标，不是1/16个RGB码值。本地SLUT权威表合同允许表示这种政策，不能据此宣称官方已认可。

## 17³残余原因

每个轴仅输入134未精确，三轴情况相同：

- idx=11，节点192/201，目标192，原frac=4855。
- 精确frac区间为[0,3640]，本轮静态区间为[3641,6068]。
- 静态下界与精确区间只差一个Q16单位；保留原frac输出193。
- 不考虑静态中点时，达到精确值的最小必要偏移为1215，仍小于4096。但本轮不自动改变静态边界。

因此残余是本轮保守搜索区间的限制，不能当作保持节点和总偏移条件下的普遍不可表示证明。后续若改为直接协调检查真实单调性，必须另立身份和计划；不能把其结果追记为本轮静态计划成功。

## 阶段验证

环境：Windows11 10.0.26200 x64，AMD Ryzen9 8945HX、32逻辑CPU，CPython3.12.14，NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0、Pillow10.4.0、tifffile2023.4.12。Numba4线程，BLAS/MKL/OMP=1。既有GCC15.2 Release CPU程序，原生每次1线程；本轮不编译、不测速度。

先执行一次集中合同：48组正/负/常量斜率对全部65537个Q16值独立枚举；四模型各2312个RGB探针核对Numba、独立u64四面体及闭式曲线；检查固定字段、格式、单调区间与逐码误差不退化。3项集中合同通过。

两尺寸都满足预先声明的解析全域mean下降至少3%、RMS/p99/max不升，才对各自唯一候选执行一次完整验收。没有根据完整指标重选：

- 四模型完整256³实际输出同时等于独立u64四面体及可分离闭式输出，完整误差统计与解析卷积一致。
- 四模型各验证五个实际单级原生后端：tetra_scalar、tetra_avx2、tetra_avx2_madd、tetra_avx2_scalar_gather、tetra_avx2_exact_float，共20份完整色域回执，全部0字节差异。
- 四模型实际映射100张1024×768 RGB8照片，核对每个输出像素与完整流一致，保存400条逐图记录。两个校准模型额外通过AVX2实际百图拼接流SHA核验。
- C99和structured后端要求四个模型，本阶段没有伪造四级输入，也不声明验证这些后端的比赛链。单级图片CLI为普通模式，外层严格检查原照片格式和尺寸。

程序SHA：ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a。照片manifest SHA：10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c。100张照片均为历史已见，未用于本轮坐标生成，不称盲测。

## 文件与复现

- python/lutlab/separable_calibration.py：独立解析模块，不修改通用拟合器或内核。
- scripts/run_filmic_calibration.py：prepare/accept阶段入口。
- experiments/filmic-calibration-v1.json：提前冻结的两尺寸、边界与验收计划。
- 本目录run.json、measured-source.zip、preparation.json、各尺寸analysis.json、full-results.json、summary.json、per-image.csv：来源、全部逐码解、完整实测与逐图证据。

原目录已存在，复现必须用新输出目录，不能覆盖本轮成果：

    artifacts/error-study-py312/Scripts/python.exe scripts/run_filmic_calibration.py prepare --output artifacts/filmic-calibration-reproduction
    artifacts/error-study-py312/Scripts/python.exe scripts/run_filmic_calibration.py accept --output artifacts/filmic-calibration-reproduction

本轮run identity：86d269a6a337d435ba34afb80490b86c5d732241ddb30a1b00ae54d93402ddb7。
full-results.json SHA：6981e8c42ababb4ceb1b7d6a24fdc5d9563f7a31f32f5e4f643fbc04482504d9。

校准模型SHA：

- m17/calibrated.slut：c48ab143ffb79d8059b92e5fce38d65d3d5785c252788780d9e5c547b435a442。
- m33/calibrated.slut：49231a3755bc2897f0d32f9ccb7578e11479d2e22cd0516a520915818f7cced0。
- 33³完整输出SHA为cae93328f20bdac943b1bcf07ea1f0bc17df888040985d78a6a66d58fcbb4c09，恰等于原完整参考RGB字节流SHA。

没有改动共享核心、默认策略或AGENTS.md，未提交commit、推送或创建PR。源解释、严格可分离前提和单级范围是本阶段结果的必要边界。
