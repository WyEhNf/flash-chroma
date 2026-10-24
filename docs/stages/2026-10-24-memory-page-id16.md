# 16题：4KiB页字典的真实容量与双阶段速度门

Agent：`/root/memory`；Operator：当前16题研究用户；Status：单版原生质量与唯一正式性能已完成，整体研究继续。默认路径和旧模型没有改动。

固定4KiB页、LE16页ID的新P4格式实际常驻12,633,164B，较原linear的16,779,328B减少4,146,164B。唯一正式场的全部112项稳定性控制有效，AVX四模式最劣吞吐53.8961%，进入100%精度/50%速度档。C99四模式都有效低50，严格拒绝；AVX通过不能为C99速度或WASM背书。Windows页别名的unknown STOP保持，不由本格式覆盖。

## 固定同源与一次实现

模型始终是当前a399首级分输出坐标及933a/95cb/932f后三级。沿用[已封存普查](2026-10-24-memory-page-alias-census.md)的4096逻辑页与3082 unique页，不重新普查、重排或选择页尺寸，不读照片或gold选择表示。旧原ROM、旧Clang C99/AVX DLL和78/80参考均不改。导出仅从旧alias容器提取已冻结页分类/原字节；它不依赖alias API成功或其未知额外句柄结论。

P4访问链是输入code→LE16 page ID→pool字节ID→palette RGB，增加一次确定的页ID索引来省去重复页。没有紧密位解码、近似量化或Windows虚拟页别名。C99显式读取LE字节、借用ROM内palette，支持非对齐ROM；核心无堆/C++/OpenMP/SIMD依赖。AVX2只复用旧LE16/1024 IO框架的一版读写流，不使用AVX512。

| 部分 | 实际B | 说明 |
| --- | ---: | --- |
| P4ID头 | 32 | 版本、shift12、palette count、逻辑长度、unique数和保留位 |
| RGB32LE palette | 1024 | 保留全部256合法项，高字节必须0 |
| LE16页ID | 8192 | 4096项，实际值必须小于3082；65535拒绝 |
| 原字节unique pool | 12623872 | 3082×4096，含最后合法字节 |
| 显式guard | 4 | 全零且计入文件，不放宽外部src/dst范围 |
| 文件合计 | 12633124 | 实际导出长度与SHA已核 |
| x64借用Model | 40 | 五个自然宽度字段，真实sizeof，不复制palette |
| 总常驻capacity | 12633164 | ROM与实际ABI合计；不是ZIP大小或实测物理RAM |

相对本内存分支同场78/80的28,046,644B也减少实际容量；不能换用速度分支85/87的另一容量作百分比分母。prepare只验证/借用，没有新的pool副本；逐图片堆scratch为0。离线导出、Python oracle、Windows映射和依赖库启动的开销另报，核心零堆不等于整个进程零分配。`.su`记录prepare32B、验证40B、C99 apply136B、AVX apply272B、OMP适配器128B/工作函数96B，均是单函数静态帧，不是调用链或四线程总栈峰值。WASM32 20B ABI只是静态推导，未实测，也未授跨平台运行资格。

## 唯一质量及独立离线核

质量计划`b41c503e0d8164bac0a685c1035349ce41e04532eaf60dced61cfe87928dd515`在16份执行源和12份输入冻结后执行一次，session10343 exit0。导出约2.105s、串行构建约5.857s、质量约12.451s只作流程耗时记录，不是正式吞吐。

独立C99 DLL、C99/AVX1/4线程、原地/分离共九个完整域路径及九个完整百图路径均与独立u64 oracle位等价；100张图逐图摘要也全相等。有限合同890项、IO拒绝113项、格式拒绝21项、src/dst NOACCESS尾边界180项、ROM末尾guard36项、0..7非对齐72项均通过。特殊ROM覆盖palette count1/256、ID255、最大4096页、最后map/pool，以及越界4096/65535；Model与blob部分重叠无写拒绝，关闭后Model清零。外部缓冲区不假定padding。

真实P4 ROM SHA为`a953eef0d1a70763a4bca053d4d70dc00dae6e40cc8eecdd1ac48648dfa15173`；主DLL SHA为`a4b442de7e2e9c579349736a5285f928fc9b379e357ab2db12b6b968061f0b92`，独立C99 DLL SHA为`fb43c43ab1942b6a33a5169df3283835f0a0588ac1251ca604c0002db26f4447`。另授离线审计只读取既有原件，重新核全部源/输入、真实文件/ABI、构建产物及完整逻辑ID回放；回放仍为`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`。

精度保留为100%：mean/p99/max与a399逐项完全相同，误差增幅均0；完整域、合并百图及逐图的零误差项也保持零。这里是相对当前模型输出的精确保留，不是相对数学参考本身误差为零。

质量进程峰WS148,602,880B、峰PrivateUsage94,142,464B含Python、独立oracle、边界夹具、所有加载库与OMP，不是loader准备峰。质量中的模型清零与映射关闭通过；进程总句柄155→254包含DLL/OMP启动，不能据此声称全部新增句柄是泄漏或全部已回基线。

## 环境与已执行命令

宿主只读查询为AMD Ryzen 9 8945HX、16核心/32逻辑CPU；Windows 11 10.0.26200、AMD64，Python3.12.14、NumPy1.26.4。C99使用Clang21.1.0，`--target=x86_64-w64-windows-gnu -std=c99 -pedantic-errors -O3 -ffp-contract=off -march=x86-64 -mtune=generic -mno-avx -mno-avx2 -mno-avx512f`；可选AVX/OMP适配器由GCC15.2.0构建，AVX目标为`-mavx2 -mno-avx512f -mtune=skylake`。全部串行编译，完整命令、版本和依赖摘要在raw的build记录。不使用`-march=native`。

以下是在工作树`F:/Hackathon/worktrees/p16-memory-20261023`中已执行的主入口；输出目录拒绝覆盖，不应在原目录上重跑以替换证据。运行时正确性、离线数据完整性、正式吞吐分别独立判定。

```powershell
$p4Python = 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe'
& $p4Python scripts/run_page_id16_quality.py --output artifacts/p16-page-id16-runtime-v1
& $p4Python scripts/audit_page_id16_quality.py --input artifacts/p16-page-id16-runtime-v1 --output artifacts/p16-page-id16-runtime-v1/quality-audit.json
& $p4Python scripts/freeze_page_id16_performance_v2.py
& $p4Python scripts/observe_page_id16_modules.py --freeze
& $p4Python scripts/observe_page_id16_modules.py --output artifacts/p16-page-id16-module-observer-v1
& $p4Python scripts/run_page_id16_performance_v2.py --output artifacts/p16-page-id16-performance-v2
& $p4Python scripts/audit_page_id16_performance_v2.py --input artifacts/p16-page-id16-performance-v2 --output artifacts/p16-page-id16-performance-v2/summary.json
```

## 正式协议：保留旧草稿，增加各角色自己的控制

原41/cell、656调用的v1仅为静态草稿，从未执行，原文件不改。root在计时前指出外围ref80 A/A不足以证明各候选自身稳定，故另冻结v2计划`b54be80781190763245429eb8743433063ccf3d04bb448f5afd0f8a2999f2608`：28份源、37份输入，包含实际四个DLL目录中各四个依赖的磁盘SHA。

固定六角色ref78/ref80/linear AVX/linear C99/P4 AVX/P4 C99。四fresh新进程，各全部模型同驻留、同输入输出地址；进程允许集固定0x55=[0,2,4,6]，记录每次CPU端点。这不是逐OMP线程绑定或锁频，也不推翻旧未绑定反例。每cell先ref80预热1次+before2次，然后每角色phase1预热1次+timed5次，phase2按全角色镜像顺序再预热1次+timed5次，末尾ref80 after2次。总77/cell、308/worker、1232调用，其中960 timed，另六fresh RSS。

各worker/cell的外围after均值/before均值，以及六角色各自phase2五次中位数/phase1五次中位数，全都必须在闭区间[0.8,1.25]。任一失败即该cell六角色全部清档；不能合并10样本救线。主比值是同worker/同phase较快78/80耗时除以候选同phase耗时，取四worker×两phase的最劣。P4/匹配linear只是辅助比值。首次身份、native或输出摘要失败STOP，A/A无效保留原轮，不补跑。

启动前只读1秒预检未发现活跃本组计算；长期Python138924/35472和git138404 CPU增量为0，未知其它node不杀、不输出完整命令行，也不宣称宿主绝对独占。唯一正式session35288 exit0，全部1232调用、六RSS保留，所有调用完整百图SHA正确。16个外围和96个角色控制共112项全部通过。独立60位Decimal审计，再以Fraction有理数独立复核，不重新调用native。

| 角色 | 1T原地% | 1T分离% | 4T原地% | 4T分离% | 全四模式档 |
| --- | ---: | ---: | ---: | ---: | --- |
| 原linear AVX | 79.367081 | 90.582240 | 93.518120 | 94.043930 | 70 |
| 原linear C99 | 54.962846 | 59.417324 | 64.233636 | 60.292035 | 50 |
| P4 AVX | 53.896116 | 55.353582 | 69.343619 | 73.325512 | 50 |
| P4 C99 | 37.645815 | 39.704735 | 46.633821 | 47.803361 | 拒绝50 |

全部数值均是八个worker/phase比值最劣，非合并中位数。P4 AVX相对原linear同kernel辅助保留率为58.383894/60.022108/67.518511/72.843085%，说明省4.15MB容量伴随明显吞吐下降；不能以旧linear较慢分母代替78/80让档位升高。P4的53.8961%是真实过50，未四舍五入救线；C99的四个有效低值也全部保留。

## 本场36格与限制

以下均要求原地/分离、1/4线程四模式同时有效。`L`是本场原linear AVX16,779,328B、最劣79.367081%；`Q`是新P4 AVX12,633,164B、最劣53.896116%，两者均精度100%。`—`仅表示本场没有更小已测内存候选通过，不断言不存在其它方案。表按这两个候选的较小容量填写。

| 精度底线＼速度底线 | 100% | 90% | 80% | 70% | 60% | 50% |
| --- | --- | --- | --- | --- | --- | --- |
| 100% | — | — | — | L | L | Q |
| 90% | — | — | — | L | L | Q |
| 80% | — | — | — | L | L | Q |
| 70% | — | — | — | L | L | Q |
| 60% | — | — | — | L | L | Q |
| 50% | — | — | — | L | L | Q |

这不覆盖旧palette场的同场80档L或有损60档P，也不删除10.8MB旧1024B块的历史50档。不同控制环境不能拼成同场全局最优；新P4容量并不小于10.8MB旧块。本阶段贡献是该固定页表示在加强双阶段控制后完整通过50，而不是最小容量理论前沿或普遍加速。

## 实际依赖加载与fresh内存

四目录的磁盘依赖SHA不同，不等于四份都加载。计时前另有绑定本v2 SHA的只读模块观察，协议`9d0781e17d8f1c8108fe26e26dcfd159d1d2bd5817f9446e8d09876408a7d73c`。同v2 imports和六角色准备顺序的一次fresh中，准备前四依赖均0，ref78后各1个，此后各阶段及模型close后仍各1个。实际路径均来自`p16-memory-build-v2/`；libgomp实际SHA为`fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88`，不是ref80目录磁盘的另一份。该观察不改环境或更换DLL，也不能外推六个仅创建自身角色的RSS进程依赖路径。枚举返回模块为借用快照，依照[Microsoft文档](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocessmodulesex)不CloseHandle。

| 独立fresh角色 | prepare WS B | prepare PrivateUsage B | 进程峰WS B | 进程峰PrivateUsage B |
| --- | ---: | ---: | ---: | ---: |
| ref78 | 64962560 | 54370304 | 133160960 | 122478592 |
| ref80 | 64905216 | 54267904 | 133111808 | 122421248 |
| linear AVX | 53313536 | 22962176 | 53321728 | 22962176 |
| linear C99 | 53379072 | 23072768 | 53387264 | 23072768 |
| P4 AVX | 49127424 | 22933504 | 49135616 | 22933504 |
| P4 C99 | 49152000 | 22982656 | 49160192 | 22982656 |

同imports/no图片下P4可见WS比linear少约4.2MB，private相近；这些值含Python、流式身份SHA、库启动和映射。全进程峰含prepare之外的读入/校验，不能称纯prepare峰、unique物理RAM或ROM容量。只读部署避免COW提交与本格式压缩是两个独立因素。系统commit噪声保留在原件，不作收益门。

源、实际ROM/DLL/依赖、对象与栈、完整raw和审计见[发布目录](../../report/data/p16-page-id16-v1/manifest.json)。C99虽为标准源码且已通过本机质量，但速度全失败，暂不扩WASM/对象/实板测试，也不修改已冻结核心追结果。下一假设必须另立版本和计时前协议；旧alias三STOP、3B有效低50反例及本C99失败保持。
