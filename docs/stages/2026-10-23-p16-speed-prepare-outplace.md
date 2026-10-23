# 第16题速度研究：直接编译ID与通用分离输出

Agent：Codex /root/speed；Operator：当前用户；分支：`codex/p16-speed-20261023`；共同起点：`16ae431`。本阶段保持最新Cinema a399分输出坐标模型及其后三层模型，研究准备管线和实际输入/输出边界。没有AVX512，没有拟合新模型，没有推送、PR或升级公共默认。

## 直接编译ID（85）

80先构造完整256³ RGB中间流，经原逐级RGB8映射后再反查palette ID，形成异常块表及16MiB直表。85复用80所有稳态像素TU，改变准备过程：把已构造的有界后缀缓存转成同序u32 palette ID；以R低地址直接产生八个输入，执行原首级精确插值和后缀ID gather，紧密写出八个ID。省掉50MiB完整RGB、16MiB逆查表、旧异常编码及最终RGB→ID遍历。

域证明、首级分输出坐标、后三层共享以及palette≤255仍为前提。临时分配与直表分配在发布前完成；无资格或分配失败走原80构造及原精确回退。发布后的编译函数为`noexcept`。分配失败注入、无AVX2实机和嵌套OpenMP未执行，不能把源级回退审阅当成这些环境已验。

palette诊断在85的成功直编路径返回`enabled=1, blocks=0`，明确没有旧异常块格式；直接表仍为原format9。旧异常导出为空、enabled为0。没有改变SLUT v1和逐级RGB8。该研究诊断差异须由使用者明确识别，未接公共CLI或GUI。

| 容量记账 | 80 | 85 |
| --- | ---: | ---: |
| 四级句柄 | 28,046,644 B | 18,579,204 B |
| palette准备已知临时峰值容量 | 94,095,920 B | 18,262,016 B |
| 单级无派生表句柄 | 272,859 B | 272,859 B |

容量不是RSS、分配器峰值或系统峰值。85保留16MiB派生表，官方是否允许这类等价表及其预算仍须确认，不能由本阶段代答。

完整4,194,304词直接表及256项palette与80逐项相同，直表SHA为`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`。随后对完整16,777,216色，以原四级标量为oracle，新AVX2原地1/4及真正分离输出1/4均零字节差，输出SHA均为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。因此固定模型的mean/p99/max均原样保留。另有504组边界/偏移/双侧哨兵/同址与真正分离、11项拒绝及单级无直表回退通过。

第一轮性能为四个新进程AB/BA/BA/AB，线程次序1/4交错，每配置七次完整100图，先在各进程取中位，再算配对比，最后取四个比的中位。源和输出SHA不在原生计时内。prepare固定使用四线程，第一轮Python Chain构造包含本地文件读取、原生准备及Python文件hash；后续独立确认改用底层create移出Python hash。

| 首轮边界 | 1线程候选/80耗时比 | 4线程候选/80耗时比 |
| --- | ---: | ---: |
| 纯apply | 0.991218 | 1.048864 |
| copy+apply | 0.990073 | 1.043299 |
| 真正分离输出 | 1.027181 | 1.026487 |

首轮prepare四个比为`[0.507424, 0.410382, 0.523024, 0.486136]`；prepare加首次冷调用100图的真正分离4线程比为`[0.678481, 0.522817, 0.628554, 0.608020]`。这些描述支持单独确认prepare。**单线程同句柄控制存在1.236468漂移，稳态控制失败；不宣称稳态受控加速成功，也不以准备收益覆盖四线程纯apply约4.9%的描述性退化。**首轮全部原始数组保留，不删除样本、不重跑择优。

独立prepare确认采用新的冻结计划`experiments/p16-direct-prepare-confirm-v1.json`，四个新进程，每个进程五组交错底层create；计时包含文件读取、解析校验、模型/缓存/直表准备，不含Python hash、DLL加载、destroy或只读导出。不同于清空系统缓存的磁盘冷启动，它使用本地热文件缓存。门槛在执行前冻结为中位耗时比≤0.75、任意进程≤0.9。独立确认不能修复首轮稳态控制失败。

2026-10-24（Asia/Shanghai）实际执行了两份独立确认原件。v1虽然数值中位0.456051，但调度失误使其与86的configure/build重叠约8秒，**环境无效，不采纳**；原始结果不改写，另附`measurement-validity.json`明确拒绝，不能只读其数值`passed_prepare_gate`字段。v2保持同协议和同一对冻结DLL，全体其它协作分支静默，计时进程结束前只等待对应session，没有编译/JIT/原生验收并发。

v2每进程各五次create，四个候选/80中位比为`[0.463137, 0.453455, 0.463239, 0.445528]`，总中位**0.458296，即完整prepare耗时降低54.1704%**，预冻结中位0.75/任意进程0.9门槛通过。它确认准备管线收益，仍不构成85稳态通过。另按COFF节独立核对，85复用的五个原像素/计时对象`.text`与80逐节完全相同，见归档身份；对象相同也不能代替真实吞吐测量。

## 通用分离输出（86）

使用当前已验四级专门化，而不是旧未专门化后端作分母。对照把预加载源完整memcpy后调用原映射；候选把源地址与目标地址传入相同的四级专门化插值循环，直接从源读取并写最终目标，保留4096像素块、线程调度、每级RGB8、精确尾部、同址委托及部分重叠拒绝。其它级数或布局也按原共享/非共享分派执行。该候选不依赖直接表，模型容量不增加。

完整16,777,216色的原地/真正分离输出1/4与原标量oracle均零差，输出SHA同上；504组有限合同、11项拒绝及单级回退通过。四级句柄均1,058,292 B，单级均271,563 B。只有AVX2，不要求BMI1。测试中的通用候选实验revision仍为2，另有`jshc_cc_outplace_revision=86`，实际身份以DLL SHA区分。

性能计划最初为`experiments/p16-generic-outplace-perf-v1.json`，空输入/同址成功分支补充清空error字符串后，在新v2目录重新完整验证并绑定`experiments/p16-generic-outplace-perf-v2.json`；v1未计时，原正确性原件保留。86 DLL最终SHA为`128c1b615bcc87afd7e813609fcd6b92278d267189614ed2857bdb7644a00b26`。本次独立于85。执行前冻结真分离1/4耗时比中位≤0.97、任意进程≤1.05，同句柄控制所有比0.9..1.1及各组中位0.95..1.05。未达到门槛不采用，不用其它接口较快替代真实输出边界。

2026-10-24完整执行四进程、每配置七轮完整100图，同句柄控制范围0.953857..1.051401，各组中位也通过冻结门槛，控制有效。所有配置和轮次的照片输出SHA一致，源只读检查通过。

| 86 / 当前四级专门化 | 1线程耗时比 | 4线程耗时比 |
| --- | ---: | ---: |
| 纯apply | 0.996077 | 1.021413 |
| copy+apply | 0.980327 | 1.037055 |
| 真正分离输出 | 0.991371 | 1.026643 |

真分离1线程只改善0.8629%，4线程增加2.6643%，未达冻结双档至少3%改善，**86不采用**。冷首100图真分离4线程加prepare的四对比为`[0.930346, 0.892742, 0.775242, 0.946049]`，完整保留，但不能替代稳态接口门槛。没有PMU、锁频或温控证据，不把额外指针、缓存状态或编译器调度写成已证明的退化根因。

## 实际环境、依据与复现

实际环境为Windows11 26200 x64、AMD Family25 Model97（Ryzen9 8945HX宿主）、GCC15.2 Release `-O3 -DNDEBUG`、Python3.12.14、NumPy1.26.4、Pillow10.4。进程限定CPU0/2/4/6，原生请求1/4线程，OpenMP动态线程关闭；没有锁频控温或证明宿主完全独占，不作为Intel i7-14700、Skylake、Linux或官方分数的实测。准备和纯映射不含图片解码与文件输出，完整100图为1024×768 RGB8，235,929,600输入字节；结果是整组摊销，不是逐图尾延迟。

80原像素TU使用`-mavx2 -mtune=skylake -ffp-contract=off`，三个pair/normal TU另加`-mbmi`；新编译TU只用AVX2。80使用显式`-std=c++17`，85使用GCC15.2默认gnu++17，没有使用GNU语言扩展。86两库显式C++17。generic dispatcher保持基线ISA，未使用AVX512/FMA/fast-math。

研究依据为[Intel缓存分块说明](https://www.intel.com/content/www/us/en/developer/articles/technical/cache-blocking-techniques.html)及[Advisor内存访问模式优化](https://www.intel.com/content/www/us/en/docs/advisor/cookbook/2024-1/optimize-memory-access-patterns.html)：减少中间数据遍历和内存流量是可检验假设，不能由字节数直接推断加速。本阶段首先省掉没有被稳态路径使用的中间格式，再单独验证准备总耗时。线程语义参考[OpenMP执行模型](https://www.openmp.org/spec-html/5.2/openmpse3.html)，不把外层并行区数量视作实际像素吞吐。

```powershell
cmake -S experiments/p16-direct-compile -B artifacts/p16-speed-direct-build-v1 -G 'MinGW Makefiles' -DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe -DCMAKE_MAKE_PROGRAM=E:/mingw64/bin/mingw32-make.exe -DCMAKE_BUILD_TYPE=Release
cmake --build artifacts/p16-speed-direct-build-v1 --target jshc_direct_compile jshc_skylake_andn_normal jshc_channel_copy jshc_channel_to -j 1
```

运行脚本为`scripts/study_p16_direct_compile.py --mode verify/bench`，需显式提供`--data-root`、`--baseline`、`--candidate`与新`--output`；通用候选另加`--generic`。完整模型哈希、绝对路径、DLL身份及复现参数见精简证据。确认入口为`scripts/confirm_p16_direct_prepare.py --plan experiments/p16-direct-prepare-confirm-v1.json --output <新目录>`。运行时不会自动覆盖已有性能证据。

精简原件与独立复算见[证据归档](../../report/data/p16-speed-prepare-outplace-v1/README.md)，包括85首轮稳态控制失败、prepare受污染v1与有效v2、86修正前正确性及最终完整验证/性能；没有隐藏失败。静态归档审计只读JSON并重新计算全部原始比值、SHA和控制，不加载原生库、不追加性能轮次。

本阶段结论是85完整prepare优化成立，85稳态收益尚未证实，86真分离输出优化失败、不采用。没有将85替换80/78稳态或将86替换当前通用后端。下一候选87拟把仍为标量的后缀缓存准备改用原精确AVX2通用内核，需另建身份、完整验证和同场prepare比较；本阶段不把提议当已完成。未执行Linux、目标Intel、真实无AVX2硬件、分配失败注入或RSS测量。提交SHA由本分支Git交付记录及父任务报告列出。
