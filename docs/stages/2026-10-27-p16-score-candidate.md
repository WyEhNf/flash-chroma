# 第16题：同步研究后的CPU评分候选

Agent：Codex /root及研究、验证子代理；Operator：本会话用户；日期：2026-10-27（Asia/Shanghai）。当前交付为可复现的评分候选，官方总分与Xeon Gold6140性能尚未验收。

## 最终选择与依据

默认冻结 **373a模型＋修订100扫描线准备器＋修订293线性direct＋AVX2四线程**。显式均值优先档改为 **max_first**；max48/max41保留在研究数据中，不进入两档精简发布包。两档均逐级保留RGB8整数输出和Q16四面体舍入，同一profile用于全部图片，不能逐图换模型或参数。

当前要求关注逐图全像素平均误差、百图总耗时及运行内存，机器内存宽裕。因此保留成熟AVX2路径，省去页字典热解码；发行构建关闭AVX-512。此前两版AVX-512实现正确但本机更慢，本轮没有新证据支持替换默认。最新预取/写入变体也未通过A/A控制，不采用它们的偶然最好时间。

按题面40分精度、40分速度、20分工程方向，先过逐图均值门槛，再比较完整批处理代价。官方Threshold、精度换分细则和速度分母均未取得；不存在可据此精确计算的“最高总分”。这里给出证据最充分的保守默认和一个均值更低的可选档，不能证明未知LUT或正式数据上的全局最优。

| profile | 百图全像素平均ΔE | 最差单图平均ΔE | Model真实capacity | 结论 |
| --- | ---: | ---: | ---: | --- |
| default / 373a | 0.695486159059 | 1.119051322056 | 18,715,824B | 保守默认，普通u8 direct |
| max_first | 0.679090181058 | 1.084102390342 | 35,495,456B | 四者平均误差最低，显式均值优先 |
| max48 | 0.679109463497 | 1.084102390342 | 35,533,672B | 平均值略高于max_first |
| max41 | 0.680936007872 | 1.093054287108 | 35,673,508B | 更小max不能代表更低平均误差 |

max_first相对default平均误差降低约2.3575%。数值由本轮独立执行四张原始密集LUT、对78,643,200个像素求RGB欧氏距离复核；不是沿用模型自报的误差。100张图片已参与历史研究，不能当作盲测。表中显示值有舍入，实际门禁对每图未舍入mean严格检查`<T`，总均值按像素数加权，p99/max仅诊断。本轮未提供T，全部记录均明确没有官方过线或分数结论。

## 仓库同步与实现范围

工作树：`F:/Hackathon/worktrees/p16-unified-avx512-20261026`，分支：`codex/p16-score-candidate-20261027`。获取origin和github后，在原统一头`4a8b27f`上合入最新联合研究`b685a3b2210eb1cfe021da3dff3b724c9e0a53d4`及其pipeline祖先`3d4d6d9`，保留历史，合并提交为`082f3d975566dd4ac409b7981891372308fd1337`。本轮实现提交为`dd55bb6`。

最新pipeline的逐级tri/tetra研究使用Numba，单级最优不能直接证明串接最优。原24模型不在本机，也没有对应C++恢复器。当前入口显式限定`tetra_q16`，拒绝tri/matched声明，防止误把拟合basis相异的节点送入四面体库。静态选择依据见[研究汇总](2026-10-27-p16-score-selection.md)。

具体交付：

- [运行与打包入口](../../scripts/p16_submission.py)：内容寻址对象、SHA检查、混合m17..33、四级固定策略、按来源保留许可；未知用户模型必须明确声明basis。新输出目录拒绝覆盖。
- [两档发布包与操作说明](../../submission/README.md)：可搬移manifest与对象，不依赖历史绝对路径；原MIT许可保持原字节。完整四候选清单在[data](../../data/p16-score-models/manifest.json)。
- 百图入口实际生成caller-owned输出区；可选写出PNG。优先AVX2，缺少AVX2时用标量，CPU-only。记录输入/输出/库/源文件/环境身份，批次前后复核模型SHA。
- 可提供四张原密集LUT进行独立精度校验；逐图mean未严格过调用者T时退出码2。没有参考表或T时不推断官方合格。
- [包级全域验证器](../../scripts/verify_p16_submission_package.py)、[固定配对脚本](../../scripts/bench_p16_score_pair.py)及12项合同测试。psutil改为可选；缺失时RSS明确不可用，模型/图像容量仍报告。
- Pixi增加`build-score`、`score`、`score-package`，不改变依赖或锁文件；默认Linux CI另编译CPU发行库并重放发布包的两条完整RGB8预测流。

## 实际验证与证据

本机：Windows11 10.0.26200 / AMD Ryzen9 8945HX（16核32线程）；MinGW GCC15.2，C++17 Release、OpenMP、AVX2/BMI；Python3.12.14 / NumPy1.26.4 / Pillow10.4.0 / psutil5.9.0。CPU-only；完整正确性覆盖1/4线程，性能固定进程亲和0/2/4/6、四线程、OMP_WAIT_POLICY=PASSIVE、BLAS/MKL=1，没有锁频或逐OMP线程绑核。不能把本机数据标成Intel6140结果。

本轮原生库SHA256为`afdb1a891bb49a0d9945161e3512b76343e4ace57fa5b0e22e100177cf32e524`，修订102、capabilities=7。构建参数`P16_ENABLE_AVX512=OFF`；bit8为编入与CPU/OS条件的合取。原回执的`avx512_cpu_os_available:false`在这里表示本库不能执行该后端，不能据此声称硬件不支持AVX-512。[构建回执](../../report/data/p16-score-candidate-20261027/build-receipt.json)冻结39份源文件及实际编译命令/依赖。

| 测试目的 | 实际对象与覆盖 | 结果 |
| --- | --- | --- |
| 原生一致性 | 6个固定模型；AVX2的1/4线程、原地/分离输出；与独立预测流比较 | 12组、24条完整RGB8流，1536次原生调用，全部通过 |
| 边界与合同 | 6048个有限长度/偏移/哨兵比较；混合m17/18/25/33独立u64 oracle；72个非法请求与未编入AVX512拒绝 | 通过；拒绝不写输出 |
| 实际图像输出 | 48个百图批次，与独立预测流逐图比较 | 4800个逐图SHA全部匹配 |
| 新交付入口精度 | default/max_first/max48/max41，每档100图，四张原密集LUT逐级独立查表 | 上表四组精度复现，输出SHA与冻结预测流一致 |
| 打包/策略 | 真实SLUT、混合m、去重/篡改、搬移、均值严格门禁、16位PNG拒绝、无psutil、自有许可、basis拒绝 | 12 passed（7.49s） |
| 最终发行包 | 两档发布包，完整RGB8各一条、每档6个短尾/标量比较及一次未编入后端拒绝 | [通过](../../report/data/p16-score-candidate-20261027/final-package-check.json) |
| 原生源码归档可用性 | 上轮83文件源码ZIP重新解压后以AVX512关闭配置CMake | 配置成功；未把它称为从副本重新编译/测速 |

[raw-evidence.zip](../../report/data/p16-score-candidate-20261027/raw-evidence.zip)保存全部原始正确性JSON、固定周期耗时、四组实际入口逐图误差/哈希、执行计划及执行源码快照；[evidence-manifest.json](../../report/data/p16-score-candidate-20261027/evidence-manifest.json)列出ZIP与各成员SHA。原始质量计划仍引用本机大型独立cube/照片；这些未再次上传。可公开复现的两档包验证不需要它们，照片与密集参考表精度复核则需自行取得相同来源。

执行时HEAD为同步提交082f3d9且实现尚在工作区，不能仅以HEAD代表当时源码。质量验证运行于psutil可选化之前，ZIP中`quality/executed-*`保留实际旧封装；四档入口运行于可选化之后、pack默认清单路径最终调整之前，其实际脚本在`run-default/executed-*`保存。最后仅调整默认打包清单路径/已知Cinema识别，数值映射未改；最终两档包另经完整域验证。新源码快照在ZIP的`executed-sources/`，不能用它覆盖旧执行来源。

## 批次时间与取舍

原生热映射、新句柄读入/准备至首批完成、应用读图至首批输出分别计时；离线密集LUT拟合不包含在SLUT准备时间中。四档新入口均保留首次输出、1次预热和7轮热批次；每轮输出均核SHA。未启用PNG写盘，应用wall包括输入文件/像素哈希、解码与双缓冲分配，第一批输出在内存可用即停止。

| 本轮入口单场描述 | 百图apply中位/ms | 创建至首批wall/ms | 读图至首批输出/s |
| --- | ---: | ---: | ---: |
| default | 37.4289 | 104.5274 | 2.6447548 |
| max_first | 43.4661 | 151.8813 | 2.6873762 |
| max48 | 40.9763 | 134.9063 | 2.7508923 |
| max41 | 43.7720 | 163.2036 | 2.6660775 |

以上只是入口单进程的描述性观测，不能据此取得新速度排名。先前分组基准出现不一致后，本轮又固定8个ABBA/BAAB周期，测热apply与新句柄至首批，共128个百图调用，全部核SHA。预设A/A全部周期比值必须处于[0.90,1.10]：

| 配对B/A | 中位比值 | 周期最小..最大 | 判定 |
| --- | ---: | ---: | --- |
| 热apply A/A | 1.08398 | 0.85159..1.39121 | 控制失败 |
| 热apply max_first/default | 0.99250 | 0.85095..1.39645 | 无性能升级资格 |
| 首批wall A/A | 1.01818 | 0.64565..1.31622 | 控制失败 |
| 首批wall max_first/default | 1.50024 | 1.14619..1.83775 | 描述性观察，不能授档 |

保留全部失败周期，不删除慢轮或事后收窄门槛，也不把昨日17ms当成本轮重测结果。当前选择保守默认的依据是成熟路径与较小Model；更准档的采用要在真实Threshold与目标机批次结果下决定。

## 内存、包体及新LUT边界

两档10条模型/sidecar记录原始914,936B，经完整文件SHA去重为6对象569,531B，包体下降37.75%。这是准确对象去重的磁盘/发布收益，不能写成运行内存降低37.75%。运行仅加载一档，default的direct约16MiB、精度档约32MiB，另计节点、suffix与Model实际capacity。

100张1024×768 RGB8输入加分离输出共471,859,200B；模型和Python/allocator另计。回执给出创建前/首批后/基准后/销毁后RSS与进程峰值，不能将RSS等同算法纯内存。四个原LUT只读映射约201MB属于计时外的独立精度验证，不计入生产Model。机器内存足够，不为减少发布包而增加逐像素差分解码。

当前两档是固定Cinema回归示例，不能应用到另一套LUT。新的四张原表应使用现有通用fit入口起步，比较各级m/网格/拟合器并验证最终四级误差，冻结参数后再打包。四级m可不同，格式和原生混合m合同已验证；默认示例的m33不是任何新LUT的最优定理。当前尚未自动将逐级tri/matched研究转成统一C++后端，也未把遗留accept的max/both默认当作新的mean门禁。

## 复现入口及协作状态

```bash
pixi run --locked build-score
pixi run --locked score-package
pixi run --locked python scripts/verify_p16_submission_package.py --package artifacts/p16-score-package --library build-score/libjshc_unified.so --output artifacts/package-check.json
pixi run --locked score run --package submission/p16-cpu --library build-score/libjshc_unified.so --images assets/photos/eval.txt --image-root . --output artifacts/score-run --threads 4
```

Windows实际使用MinGW Makefiles、GCC路径及`artifacts/p16-score-cpu-build`输出；完整配置记录在构建回执。100图、四张原表和新LUT用法见[交付说明](../../submission/README.md)。本轮完整6模型旧计划依赖绝对路径，实际质量入口为`python scripts/verify_p16_unified.py --library artifacts/p16-score-cpu-build/libjshc_unified.dll --plan experiments/p16-score-quality-v1.json --output artifacts/p16-score-quality-v1 --build-receipt artifacts/p16-score-cpu-build/build-receipt.json`，默认覆盖scalar/avx2/avx512请求及1/4线程；不宣称仅克隆仓库即可取得全部大型历史输入。

操作前刷新全仓86条issue/PR索引及相关正文/完整conversation/review/行内线程，核对[#92](https://github.com/WyEhNf/flash-chroma/pull/92)、[#93](https://github.com/WyEhNf/flash-chroma/pull/93)头未变化且无意见；沿引用复核[#7](https://github.com/WyEhNf/flash-chroma/issues/7)、[#8](https://github.com/WyEhNf/flash-chroma/issues/8)、[#5素材意见](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072)、[#9修复意见](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)及[#12](https://github.com/WyEhNf/flash-chroma/pull/12)/[#37](https://github.com/WyEhNf/flash-chroma/pull/37)最终验收。337a3dd/876e15b8/397cc367实际为当前祖先，未改相关修复或冒称重新完成历史验收。完整快照见[coordination.json](../../report/data/p16-score-candidate-20261027/coordination.json)。

Discussion4当前连接器拒绝该端点，保留读取缺口；#8最终接口迁移/实板、正式Threshold/评分以及6140吞吐未完成。只提交Draft，不执行合并、关闭issue或删除旧研究分支。新增Linux CI的实际状态以PR检查为准，CI功能正确性也不代表目标机速度资格。
