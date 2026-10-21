# RGB通道差直表：完整精度通过，周期筛查未过

**相对修订23的整体三倍吞吐目标仍未达到。** 目前已完成整轮墙钟验收的最优40，相对23的纯映射吞吐为单线程2.6444倍、四线程3.1200倍；真实输出为3.3066倍、4.3069倍。本阶段60没有新的墙钟成绩，不能由局部硬件计数推断三倍目标已经实现。

本阶段从[PR #57](https://github.com/WyEhNf/flash-chroma/pull/57)的`7643bea227af63cecdea79b05fd6abcb7773ffa1`开独立分支`codex/skylake-chroma-delta-20261021`。候选仅更换40的16MiB无损字节ID表物理排列和对应地址计算：输入`(R,G,B)`映到`(R,(G-R)&255,(B-G)&255)`，表构造按`G=(R+差G)&255`、`B=(G+差B)&255`恢复原RGB。向量输入仍精确读取24字节/8像素，索引使用AVX2逐字节减法，后续仍是GPR ID/调色板加载、64像素读后写192字节、NT输出、NTA输入提示和65536像素工作块。单级、模型、插值/舍入、公共默认及只读`AGENTS.md`没有改动。新格式18与旧格式9/17区分。

只读扫描冻结的100张1024×768 RGB8照片，基准40平均每64像素涉及49.4153条直表缓存行；本布局44.5090条，旧54位交换42.3426条。通道差约减少9.93%的地址行集合，且向量索引仅需移位、字节减、掩码三条操作/8像素；这只构成一次实测假设，不是硬件miss或吞吐结论。独立整数遍历全部16,777,216色验证映射双射、地址最大`0xFFFFFF`。该布局改变2MiB页编号，不沿用旧54“页编号不变”的结论。

## 验证

实际环境为Windows 11宿主、WSL2 Ubuntu Linux 6.18.33.2、Ryzen 9 8945HX、GCC 15.2、Python 3.14.4；来宾vCPU绑定0/2/4/6，不能保证是宿主独占物理核。Release SIMD翻译单元采用`-mavx2 -mtune=skylake -ffp-contract=off`，没有`-march=native`、AVX-512或fast-math。静态核验原参考回退对象逐字节同一，候选像素对象无外部调用、gather、PEXT或AVX-512，实汇编含`vpsubb`。

从原四张稀疏模型构造表，独立按全RGB8正向公式读取全部16,777,216个ID并与已验逐级整数输出流逐字节比较，零差；原地和分离输出共24组完整域API配置均通过。有限输入2208组原地、4416组分离/同址，保护页736组、目标对齐1280组、API拒绝44组、直表拒绝9组均通过。候选四级句柄28,046,644字节，直表16,777,216字节并在本机实际由透明大页覆盖。正确性仅针对冻结模型和RGB8整数契约；没有重新拟合或声称官方评分绝对误差为零。

首次计数前在[冻结策略](../../experiments/skylake-chroma-delta-pmu-v1.json)约定：同场40的1线程周期比≤0.95、4线程≤1.05，才进入相对23整轮墙钟；每个角色/线程各一次预热和一次计数，不重复挑选。100图输入235,929,600字节、SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。全部计数运行比例≥0.99。

| 同场40→60 | 周期/像素 | 指令/像素 | 通用cache miss/像素 | 周期比 |
| --- | ---: | ---: | ---: | ---: |
| 1线程 | 3.41009→3.24477 | 5.40104→5.52975 | 0.10458→0.06465 | **0.951522** |
| 4线程合计 | 4.19254→4.13529 | 5.44802→5.59276 | 0.11799→0.08354 | 0.986344 |

单线程比事前门槛高0.001522，故**本版筛查失败**。miss减少与周期小幅改善是本机一次计数观测，不能舍入成通过或归因为特定缓存级；没有做整轮墙钟、复测择优或Skylake实机测量。原始构建、源码快照、汇编、全域验证、每线程计数及离线复核见[归档](../../report/data/skylake-chroma-delta-v1/README.md)。目标继续研究；官方派生表许可、内存预算和实板表现仍以[issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)跟踪。本研究保持Draft，不合并。

复现须在新输出目录依次运行：`python3 scripts/build_skylake_runtime.py --plan experiments/skylake-chroma-delta-v1.json --output <新构建目录>`，`python3 scripts/inspect_skylake_chroma_delta.py --plan ... --build ... --output ...`，`python3 scripts/verify_skylake_chroma_delta_linux.py --plan ... --build ... --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output ... --affinity-cpus 0,2,4,6`，最后以同SHA构建/完整域证据生成独立计数策略，再调用`python3 scripts/profile_skylake_chroma_delta_pmu.py --policy ... --output ...`。所需输入SHA、绝对库路径和计数顺序在冻结JSON中；归档保留实际运行字节。不能覆盖原证据再称首次计数。
