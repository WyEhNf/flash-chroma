# 同模型精确ROM的六档内存与可移植性研究

Agent：Codex `/root/memory`；Operator：本会话项目用户；Task：16题方向3；Status：本阶段完成，整体研究继续。分支`codex/p16-memory-20261023`基于共同HEAD `16ae431`。未改公共默认、模型、既有API或只读AGENTS.md；PR由根代理统一交付。

本轮使用当前最优Cinema a399首级、原9216字节分输出坐标及933a/95cb/932f后三模型。冻结稀疏模型生成精确ID表，再生成独立借用ROM表示。没有用旧PR16、普通af974、完整源LUT、照片或gold生成新表；gold仅在构造后检验。速度分母取每个同场进程中78/80的较快端点，拒绝用较慢specialized库掩盖退化。specialized仍作为同模型小内存参照实测。

精度保留定义为`min(mean基线/mean候选, p99基线/p99候选, max基线/max候选)`，零基线要求候选仍为零；速度保留是`基线耗时/候选耗时`。两者底线分别设100/90/80/70/60/50%。本轮全部有效表示对完整RGB8精确等价，故精度六档均满足，逐图误差也完全不变。完整域mean/p99/max仍为0.9811105967231599 / 3.7416573867739413 / 8.12403840463596，百图mean仍0.810320559；不是相对原滤镜零误差。

## 实现与实际容量

新增`experiments/memory-rom/memory_rom.c`提供独立C99借用接口。32字节头、256项RGB32调色板及线性ID/去重块载荷都按小端序列化；C99逐字节读u32，不要求文件或节点对齐，也不要求主机小端。准备时验证所有偏移、块范围和ID，不分配堆。调用者保持ROM映射不变和存活，可让多个模型实例共享同一只读映射。原有公开SLUT/C99格式不变，新M16D格式只是研究导出格式，不能当作官方已许可格式。

固定16/64/256/1024字节块去重，查询为`pool[offset[input>>bits]+(input&mask)]`，一条间接依赖换取较小常驻表。AVX2候选从78普通线性像素源码生成，只替换ID函数及命名空间，保留输入边界、NT输出、SFENCE、65536像素静态块和尾部。它不含BMI1专门化，因此不能把速度差都归因于容量。所有源及生成源与实测库已归档。

| 表示 | 磁盘ROM字节 | ROM＋模型结构常驻容量字节 | 对28,046,644字节基线节省 | 唯一块 |
| --- | ---: | ---: | ---: | ---: |
| 原78/80 | 输入SLUT及侧表457,468 | 28,046,644 | 0% | 不适用 |
| 线性ROM | 16,778,272 | 16,779,328 | 40.17% | 不适用 |
| 16字节块ROM | 5,918,672 | 5,919,728 | 78.89% | 107,707 |
| 64字节块ROM | 6,706,400 | 6,707,456 | 76.09% | 88,387 |
| 256字节块ROM | 8,268,320 | 8,269,376 | 70.52% | 31,270 |
| 1024字节块ROM | 10,800,160 | 10,801,216 | 61.49% | 10,482 |
| specialized同模型参照 | 原输入457,468 | 1,058,292 | 96.23% | 不适用 |

ROM常驻容量按真实文件映射长度＋1056字节模型结构计，包含序列化调色板和结构中的主机序调色板，未减去重复小表。C99与AVX2共享相同ROM容量。没有把载荷长度当作原vector容量，也没有把零堆写成零常驻内存。ROM磁盘体积比紧凑SLUT输入大，属于用离线预编译换运行速度；模型生成、导出和字典构建峰值没有降低证明。

## 同场性能与六档选择

环境Windows11 26200 x64、Ryzen9 8945HX，Python3.12.14/NumPy1.26.4；GCC15.2 Release，AVX2 TU显式`-mavx2 -mtune=skylake -ffp-contract=off`，无AVX512/native/fast-math；只有原78对照的两个ANDN TU另带`-mbmi`。复用既有静态核心SHA`64abb6eb38d929dc81c07b5a34be1408bbadecfee76fd31801cdfe94a0916ef6`并单列身份。OMP_DYNAMIC=FALSE、OMP_WAIT_POLICY=PASSIVE，分别请求1/4线程；未锁频、控温或绑核，不外推Skylake。

固定已见100图1024×768，共235,929,600字节。四串行新进程轮转及反转角色顺序、交错线程顺序。每角色/线程/接口一次预热＋5次完整百图，计时排除准备、copy、IO、hash；原地在每轮计时前恢复输入，真实输出直接读只读源。每组首尾SHA核对，非每内轮hash。11角色42组配置共840个计时轮次，另80 A/A尾部控制80轮；没有把这些吞吐摊销写成单图或p99延迟。所有输出SHA仍`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。

| 候选 | 原地1线程，中位/最劣保留 | 原地4线程，中位/最劣 | 输出1线程，中位/最劣 | 输出4线程，中位/最劣 |
| --- | ---: | ---: | ---: | ---: |
| 线性ROM | 80.42% / 74.82% | 94.39% / 65.54% | 100.08% / 92.08% | 102.27% / 101.22% |
| 16字节块 | 55.00% / 50.10% | 67.88% / **45.90%** | 64.16% / 55.21% | 76.36% / 67.12% |
| 64字节块 | 51.42% / 50.22% | 74.98% / **49.36%** | 66.79% / 62.83% | 76.11% / 67.94% |
| 256字节块 | 59.85% / 52.19% | 67.32% / **46.36%** | 70.17% / 66.39% | 70.84% / 63.32% |
| 1024字节块 | 60.78% / 57.03% | 74.96% / 52.29% | 69.83% / 60.32% | 80.26% / 77.55% |

四类A/A的四进程比中位分别1.0104/0.9792/0.9647/0.9958，所有单对位于0.8..1.25，中位位于1/1.10..1.10，事前控制均通过。主档位使用四进程中最劣吞吐保留，边界附近不四舍五入抬过线。没有以中位数掩盖16/64/256字节块四线程原地越50%底线。

下表为本轮已测候选中满足速度底线的最小常驻表示；精度各列同时保留100%。`基线`表示维持本轮78/80的同场速度参考点，28.05MB；它是参考定义，不能把按worker取较快端点解释成一个自动切换实现。不同硬件或接口必须重测。

| 速度底线；精度底线任取100..50% | 原地1线程 | 原地4线程 | 输出1线程 | 输出4线程 | 四种运行情形同时满足 |
| --- | --- | --- | --- | --- | --- |
| 100% | 基线 | 基线 | 基线 | 线性16.78MB | 基线 |
| 90% | 基线 | 基线 | 线性16.78MB | 线性16.78MB | 基线 |
| 80% | 基线 | 基线 | 线性16.78MB | 线性16.78MB | 基线 |
| 70% | 线性16.78MB | 基线 | 线性16.78MB | 1024块10.80MB | 基线 |
| 60% | 线性16.78MB | 线性16.78MB | 64块6.71MB | 16块5.92MB | 线性16.78MB |
| 50% | 16块5.92MB | 1024块10.80MB | 16块5.92MB | 16块5.92MB | 1024块10.80MB |

纯C99普通循环在本轮各情形的最劣吞吐保留约23%–43%，**全部越50%速度底线，当前不能推荐为满足双底线的运行方案**。它提供真实无堆、无SIMD依赖的可移植执行及位精确验证，性能资格明确不通过。specialized实际只有约3%–5%的当前最佳吞吐，虽常驻仅1.06MB，也不得因低内存而选用。

## RSS、scratch与验证范围

独立新进程各只准备一个角色，在分配图片前读取Windows GetProcessMemoryInfo。原78准备后工作集66,400,256字节、历史峰133,496,832；80相应66,301,952/133,406,720。线性ROM53,379,072/53,379,072；16字节块42,573,824/42,573,824；64/256/1024块分别43,290,624、44,924,928、47,448,064字节且各自峰相同。它们包含Python、NumPy、库与映射，不是纯模型RSS，也没有扣掉运行库来制造收益。完整PrivateUsage、加载前读数及其他角色保留在原始档案；RSS来自各自新进程，不能相加或与较早WSL读数混算。

运行mapper额外堆scratch为0，图片由调用者持有；本机GCC`.su`给C99 prepare帧1168字节、apply帧64字节、validate帧8字节，AVX2输出入口帧224..240字节、并行worker帧128字节、dispatcher帧160字节。这是静态单帧计量，不是调用链/OMP运行库/线程栈总峰值，不能直接相加当RSS。C99库41,248字节、AVX2适配库181,155字节，动态运行库另列。

5容量×C991线程/AVX2请求1/4线程的15配置完整16,777,216颜色全部逐字节匹配已验独立整数oracle流；3850组有限合同覆盖0/1/7/8/9/31/32/39/40/63/64/65/71/72/73/405/406/4095/4096/65535/65536/65537像素、5种RGB偏移、原地/输出及尾哨兵；独立C99 DLL也参与有限对照。另完成304个ROM非对齐/Windows保护页对照、23项畸形格式或无写IO拒绝，及主验证的6项拒绝。非对齐ROM以1/3/7/31字节偏移实跑。保护页覆盖原地末尾和只读输入末尾的合法访问，未靠额外填充隐藏越界。

构建v1生成的AVX2源缺`<cstdint>`导致编译失败；修复后独立v2构建通过。导出v1错误按最大已访问ID223截断调色板，漏计7个合法未访问颜色，prepare据合同拒绝；v2保留完整230色并通过全部门禁。失败原件保留，不覆盖或声称首轮通过。旧70在旧强求提速协议下的失败仍成立，本轮只是按新50..100%需求重新实测新的紧凑表示。

## 复现、资料与后续

[小型证据](../../report/data/p16-memory-rom-v1/README.md)保存原始轮次、RSS、源/生成源、库、哈希、失败记录及命令。大ROM不入库，可从冻结稀疏模型重建；没有上传照片。源码是可复现的构建入口，Windows默认路径可通过参数覆盖：

```powershell
$env:PATH='E:/mingw64/bin;'+$env:PATH
$env:OMP_NUM_THREADS='1'; $env:OMP_DYNAMIC='FALSE'; $env:OMP_WAIT_POLICY='PASSIVE'; $env:OPENBLAS_NUM_THREADS='1'
$py='F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe'
& $py -X utf8 scripts/build_memory_rom.py --data-root F:/Hackathon/projects/16-lut-color --output artifacts/new-memory-build
& $py -X utf8 scripts/study_memory_rom.py export --baseline <同源80库绝对路径> --data-root F:/Hackathon/projects/16-lut-color --output artifacts/new-memory-rom
& $py -X utf8 scripts/study_memory_rom.py verify --library artifacts/new-memory-build/jshc_memory_rom.dll --roms artifacts/new-memory-rom --data-root F:/Hackathon/projects/16-lut-color --output artifacts/new-memory-full
& $py -X utf8 scripts/verify_memory_rom_contract.py --library artifacts/new-memory-build/jshc_memory_rom.dll --roms artifacts/new-memory-rom --output artifacts/new-memory-contract
& $py -X utf8 scripts/bench_memory_rom.py --build <新build绝对路径> --roms <新ROM绝对路径> --ref80 <同源80库绝对路径> --data-root F:/Hackathon/projects/16-lut-color --output artifacts/new-memory-perf
```

设计参考[Chilimbi/Hill/Larus关于缓存布局与压缩的研究](https://www.microsoft.com/en-us/research/publication/making-pointer-based-data-structures-cache-conscious/)，将更小工作集和多一层依赖分别实测；[MARISA原项目](https://github.com/s-yata/marisa-trie)的静态紧凑字典与借用映射说明支持部署表示可与训练对象分离的思路，本轮没有引入MARISA依赖，也不套用其字符串压缩率。C99表示依据[WG14 N1256](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf)的整数及字符字节规则，实际仍要求8位字节和uint32_t/uintptr_t存在。

有损节点/轴位宽的质量曲线、真正wasm32执行和进一步纯C99吞吐研究另阶段推进。当前只实跑Windows x64，不宣称ARM实板、big-endian或官方Threshold通过。ROM构造失败明确返回错误；其独立API没有破坏原78/80创建失败回退或诊断生命周期。官方派生缓存许可、部署预算及接口认可继续待定，不自动接CLI/GUI。
