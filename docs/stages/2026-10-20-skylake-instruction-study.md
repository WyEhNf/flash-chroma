# 中值网络、EVEX-256与33³地址专门化：四个候选的静态停止结果

Agent：Codex；Operator：WyEhNf；Task：结合最新远端与本地进度，在不降低精度的前提下研究Skylake性能；Status：Completed（本轮有界研究与归档完成；四候选不采用，目标服务器实测仍未执行）。

本轮没有新增可采用的提速。实现了三个新方向，并基于寄存器压力的相反信号做了一次固定组合，均未通过运行前冻结的静态资格。没有执行它们的像素核、拟合、完整色域或性能测试，不能称为正确但更慢；这些原型只是保留研究依据。公共运行时及默认模型没有变化，已有精度不会因本轮原型而下降。

开始时本地为`860d6bf`，工作区干净；fetch后远端main为`b19c5a0`，相对本地增加两提交。本地包含PR #42/#43的精度与运行时研究，不能把main较早的普通模型当作更弱基线夸大新收益。已阅读远端[双尺寸误差归因](../../artifacts/lut-cause-study/20261018/report.md)，其20个对照解释Filmic/Emerald的采样位置、节点量化与训练支撑，没有新增运行时提速。本工作分支通过`93499f2`纳入main；唯一冲突为`.gitattributes`末尾，保留双方的原字节归档规则，没有覆盖任一研究。

所有新方向都固定原节点、33³模型、Q16坐标和逐级RGB8 half-up。参考为无后缀缓存的坐标差修订5，候选修订依次为17/18/19/20。没有借改变拟合、舍入、LUT来源或新增颜色表获得速度。参考实际固定四级路径有35次gather；非压缩首级对应38次。非共享坐标不能无条件复用三通道的顶点排序，已有反例继续有效。

实际构建和分析在Windows11 26200 x64 / Ryzen9 8945HX（16核32线程）进行，Python3.12.14标准库、MinGW GCC15.2、LLVM-MCA21.1。Release为`-O3 -DNDEBUG`，AVX2 TU显式`-mavx2 -mtune=skylake -ffp-contract=off`，不启用FMA、fast-math或全局march。静态分析没有线程吞吐量或图像计时；CPU/OS能力探针输出`AVX2=1 AVX512F=1 AVX512VL=1`，仅说明本机可用能力，不是候选数值验证。

下表周期是LLVM-MCA的100次循环模型。geometry/grid33/组合用`skylake`；EVEX用`skylake-avx512`，该模型下参考仍为44732。含rsp操作数是汇编计数，不是实测spill次数、cache miss或时间。

| 候选 | 实际路径 | 热循环指令 | 含rsp操作数 | MCA周期，参考→候选 | 预设条件与结论 |
| --- | --- | ---: | ---: | ---: | --- |
| 中值网络17 | 35 gather | 575→541 | 41→30 | 44732→43633（−2.46%） | 至少3%周期改善；未达到 |
| EVEX-256 18 | 35 gather | 575→527 | 41→0 | 44732→55132（+23.25%） | 至少5%周期改善且不增加rsp；周期失败 |
| 常量地址19 | 35 / 38 gather | 575/570→548/549 | 41/38→49/49 | 44732/56434→40733/50847 | 两族至少3%改善且rsp不增；两族rsp失败 |
| 固定组合20 | 35 / 38 gather | 575/570→535/531 | 41/38→46/41 | 44732/56434→38641/56529 | 同上；rsp失败，38-gather周期也失败 |

中值网络把`x+y+z-high-low`替换为`max(min(x,y),min(max(x,y),z))`，同时复用`y>x`掩码选择高低轴。等值坐标只会交换零重心权重的顶点，数学上可保持插值；数学推导没有代替实际实现验证。指令少约5.91%，但周期仅改善2.46%，按冻结条件停止。计划中的“原8次gather”是文字笔误，实际分析命令明确35/35且回执为35；保留原计划与构建SHA，没有事后改写。

EVEX保持每包8像素、256位整数，独立TU加`-mavx512f -mavx512vl -mavx512bw -mavx512dq -mprefer-vector-width=256`，把AVX2向量掩码gather改成EVEX的全开k掩码gather。[Intel的VL说明](https://www.intel.com/content/www/us/en/developer/articles/technical/the-intel-advanced-vector-extensions-512-feature-on-intel-xeon-scalable.html)提供了短向量仍能使用扩展寄存器的依据。实际汇编使用YMM16至26，整个新TU无ZMM；dispatcher没有YMM/ZMM/k寄存器，原AVX2回退对象与参考同SHA。候选确实消除了热循环栈操作数，但总周期模型更差；吞吐下界180.5→154.5的改善不能覆盖此失败，也不能据此宣称真实硬件更慢或更快。

实验dispatcher按GCC CPU/OS能力检测F/VL/BW/DQ，存在`JSHC_EVEX256_DISABLE`时回退原对象。它尚未经过运行合同，不能当成已验证的跨CPU入口。此方向仅适用于实际支持相应ISA的Skylake-SP/X等SKU，不能替代所有Skylake的AVX2路径。256位也不承诺免降频，[GDS会影响AVX2/AVX-512 gather](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/resources/gds-mitigation-performance-analysis.html)，服务器必须记录微码/缓解状态；本轮未修改安全缓解。

常量地址只在四级均`sr=1089、sg=33`、首级非共享且后三共享时使用。`idx*1089=(idx<<10)+(idx<<6)+idx`，`idx*33=(idx<<5)+idx`，并固定stride与末角偏移；其他网格/布局直接调用原AVX2对象。它不新增轴表或端点哨兵，区别于已停止的共享轴预计算。两条路径的向量乘法均44→36，总周期模型下降，但栈操作和吞吐下界恶化，未过预设条件。

中值网络降低栈操作、常量地址增加栈操作，构成一次组合的具体依据。组合严格采用两个已冻结改动，没有继续改排序表达式、常量分解、网格、块大小或编译参数。35-gather模型周期下降13.62%，但rsp仍41→46；38-gather周期反增0.17%，因此组合也停止。没有据固定模型恰好只用压缩路径而删掉另一条失败家族。本轮结束这三个方向的变体搜索。

业界实现还核对了[OpenColorIO的Lut3D CPU分派](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/src/OpenColorIO/ops/lut3d/Lut3DOpCPU.cpp)：其分ISA后端组织值得参考，但float像素接口不能直接替换本项目逐级Q16/RGB8合同。[GCC文档](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/x86-Options.html)也区分调度目标和可用ISA，单独更改mtune不能解锁高寄存器。CUDA需可用的[NVIDIA GPU执行环境](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html)；当前最终条件只确认Skylake服务器，没有GPU条件，因此本轮优先推进CPU方案，未新增CUDA测试或声称GPU收益。

复现应先从归档内`build/measured-source.zip`恢复测量时原字节，包括参考依赖，再构建到新目录；不要重算旧计划SHA掩盖换行变化。以下为实际入口，`<name>`依次为`geometry`、`evex256`、`grid33`、`grid-geometry`：

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/build_skylake_runtime.py --plan experiments/skylake-<name>-v1.json --output artifacts/skylake-<name>-build-v1 --compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator 'MinGW Makefiles'
```

EVEX改用独立`build_skylake_evex256.py`，未放宽原builder的ISA限制。geometry使用原`inspect_skylake_avx2.py --reference-gathers 35 --candidate-gathers 35`；EVEX使用`inspect_skylake_evex256.py`；常量地址与组合使用`inspect_skylake_grid33.py`。分析均传同一`--plan/--build`、新`--output`、`--objdump E:/mingw64/bin/objdump.exe`和`--mca 'C:/Program Files/LLVM/bin/llvm-mca.exe'`，完整命令在各ZIP的回执中。

第一次EVEX静态入口把CMake本项目对象误当作保留完整源目录的对象而拒绝定位；修正分析工具后检查同一个构建，C++与计划未变，目录v1保留为空、有效结果为v2。grid33分析脚本随后仅改为从plan读取目标名；归档按已记录SHA精确恢复原版脚本，没有重做分析。所有这些都是工具/归档检查，没有数值或性能调用。

主要交付为四个`experiments/skylake-*-runtime`目录、四份冻结计划、四个独立工具及[完整静态证据](../../report/data/skylake-instruction-study-v1/README.md)。四个ZIP保留源、编译命令/日志、DLL/依赖、对象、反汇编、原MCA日志与实际分析脚本；`summary.json`复算四项停止条件。此前20个原生候选、11次性能/9次静态停止，加本轮4个静态停止，累计24个原生候选、11次性能/13次静态停止；局部性等纯剖面不混入此计数。

另用独立标准库入口`artifacts/error-study-py312/Scripts/python.exe -I -S -X utf8 scripts/audit_skylake_instruction_study.py --output report/data/skylake-instruction-study-v1/independent-audit.json`完成档案核验：6个清单文件、178项源成员SHA、实际分析脚本、原始MCA日志与JSON数值、四项原拒绝门槛均可复现。剔除临时克隆元数据字段后以新回执`independent-audit-v2.json`再次核对通过，原数值ZIP不变。通过只代表静态证据完整性，不补发数值正确性或性能结论；新增像素/拟合/性能调用仍0。

协作检查获取37个PR、2个独立issue、2个Discussion、113组完整REST评论/review/行内记录；GraphQL审查线程0，Discussion #4无评论，核对分页完整。快照在`remote-snapshot.zip`，明确剔除API仓库元数据的临时克隆字段；正文、评论和数值证据不变。阅读相关正文、意见及引用，核实337a3dd（PR #9基线/环境与issue #7绑定）、876e15b8（保护）和397cc367（相等mean）均为祖先；这些修复涉及的公共代码本轮未改，验证沿用[#37实际集成验收](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)，没有把本轮静态检查冒充重跑回归。

[#38](https://github.com/WyEhNf/flash-chroma/pull/38)/[#41](https://github.com/WyEhNf/flash-chroma/pull/41)的双尺寸数据与归因、[#39](https://github.com/WyEhNf/flash-chroma/pull/39)建议、[#42](https://github.com/WyEhNf/flash-chroma/pull/42)/[#43](https://github.com/WyEhNf/flash-chroma/pull/43)精度与性能证据分别引用，不跨机器拼接速度比。[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)要求的实现正确性与模型误差分开；[#8](https://github.com/WyEhNf/flash-chroma/issues/8)接口迁移、资源预算与实板、GUI #40继续独立。没有发现本阶段新增相关阻塞意见，不合并PR或关闭issue。

当前仍保留此前经本机完整验证的[坐标差](2026-10-20-skylake-delta16.md)和[获证缓存路径](2026-10-20-skylake-domain-proof.md)，不把它们的独立收益相乘，也不称Skylake实测。已有[固定输入服务器包](../../report/data/skylake-domain-server-v2/README.md)可用于目标端验收。Skylake SKU/系统/入口与GDS状态、官方数据/Threshold、分输出坐标及派生缓存许可尚未取得；此次未请求访问权限，也未擅自改默认。四个未获资格原型不加入服务器候选矩阵。后续有真实目标端条件或新的瓶颈证据时再开启新阶段。
