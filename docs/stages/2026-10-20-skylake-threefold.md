# 相对修订23的三倍目标：修订24—30研究检查点

Agent：Codex；Operator：WyEhNf；Task：精度不降，继续优化到当前吞吐的300%；Status：In Progress（本检查点为WIP/Draft，三倍目标没有完成）。

本阶段直接以已验修订23（8355402）为参考，尝试七个独立候选。全部通过固定模型完整RGB8色域等价验证，但没有候选同时达到1/4线程三倍吞吐，不能用历史阶段收益相乘或选取一次最快轮次宣布完成。用户已明确最终型号尚不确定，按通用AVX2继续；没有AVX512依赖。

工作分支为`codex/skylake-threefold-20261020`，基于[PR #46](https://github.com/WyEhNf/flash-chroma/pull/46)的83554020bee6b3313292d40d41d8f3a29b8b87de。刷新后的main仍为b19c5a0，已经包含。阶段提交以本PR实际头为准；每次构建/验证/性能另有源码、输入、计划和库SHA，不以提交时间推定执行身份。

## 七条路线及结果

表中为候选/23的**配对耗时比**，小于1表示更快，三倍吞吐要求≤1/3。每个候选只运行一次预先冻结的四进程测试，全部原始轮次保留。Windows与WSL分别直接比较当轮23，不能跨环境比较绝对时间或叠乘收益。

| 修订／环境 | 方法 | apply，1／4线程 | 旧copy＋apply，1／4线程 | 新输出接口，1／4线程 | 四级句柄字节 |
| --- | --- | --- | --- | --- | ---: |
| 24／Windows | 32MiB精确16bit，普通页，对齐词gather再提取奇偶 | 0.728272／0.833798 | 0.757447／0.891266 | 未提供 | 44,823,868 |
| 25／Windows | 16MiB字节ID，普通页，字节偏移gather＋调色板 | 0.569640／0.626203 | 0.609154／0.738153 | 未提供 | 28,046,648 |
| 26／WSL | 64MiB RGB32，实际THP，一次gather | 0.641360／0.803998 | 0.715198／0.900872 | 未提供 | 78,378,292 |
| 27／WSL | 16MiB字节ID，实际THP，对齐词gather＋调色板 | 0.569274／0.602745 | 0.670452／0.808280 | 未提供 | 28,046,644 |
| 28／WSL | 32MiB精确16bit主体THP，scale=2 gather；真实输出API | 0.621626／0.720581 | 0.718645／0.854484 | 0.519740／0.342202 | 44,823,872 |
| 29／WSL | 相同16bit表，八个独立标量载荷替代gather | 0.555397／0.666140 | 0.656349／0.862421 | 0.479268／0.373694 | 44,823,872 |
| 30／WSL | 16MiB ID，4×4×4颜色共缓存行，实际THP | 0.539994／0.637160 | 0.633718／0.842519 | 0.438003／0.336039 | 28,046,644 |

23四级句柄为11,269,404字节，所有候选暂保留原表和完整回退，因此增加容量很明显。24/28/29用R的8bit加G−R、B−R相对各自最小值的两个4bit精确编码，只在差值跨度可表示时启用。25/27/30保存完整颜色的精确8bit调色板ID，仍读取230项调色板。26保存每个颜色完整RGB32。25/28的末尾保护词保障非对齐gather合法，29保留相同保护词；24/27/30按对齐词提取值，无额外尾词。

构造仅根据原四个稀疏模型、原Q16及逐级RGB8生成全域标签，不读取完整源LUT、照片或旧gold。布局/证书/调色板条件不符时保留23/16/4和标量路径。四包交错用于增加独立请求，参数在计时前固定；没有按计时挑选展开数或tile大小。新增分配失败路径未注入。

30的4³颜色块恰好64字节。预先只读照片地址分析中，每32像素访问行平均25.811787→20.499063；它只描述包内几何复用，没有模拟包间缓存、TLB或新增地址指令。真实计时如表，不能把20.6%的行数下降当作同等提速。29则明确检验独立载荷能否绕过gather瓶颈，不能把其804条完整汇编指令与其他函数的条数直接换算性能。

## 计时范围与新输出接口

所有性能均为Ryzen9 8945HX本机。Windows11 26200、MinGW GCC15.2、Python3.12.14/NumPy1.26.4；WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库。Release为-O3/-DNDEBUG，独立AVX2 TU为-mavx2/-mtune=skylake/-ffp-contract=off，没有全局native、AVX512、FMA或fast-math。新像素内核无外部调用；每个新库的原16/4/23回退对象分别与同场参考一致。**这不是Skylake实机成绩**，未锁频控温，所有进程比值都在原始回执中。

CPU0/2/4/6为同L3的四个物理核。四个串行新进程AB/BA/BA/AB，线程顺序1,4／4,1／1,4／4,1，每配置5轮完整100张1024×768 RGB8图。原生单次repeats=1；235,929,600字节源预载，IO/解码/分配/SHA在计时外，逐轮完整输出SHA必须相同。每进程先取5轮中位，同进程相除，再取四个比值中位。七候选共有560轮旧接口记录。

旧接口先memcpy再in-place映射，保留apply和copy＋apply两个时间。该内存复制在WSL四线程时已占参考总时间的较大部分，单纯将映射压到零也不能稳定满足其三倍目标。28开始新增真正可调用的`jshc_cc_apply_to`，直接从只读源生成目标；23的新增适配器验证后memcpy再调用原23，参考原运行时源未改。新`jshc_cc_bench_to`在两库使用相同代码，包含真实API的参数验证和全部复制/映射，不把计时器中的复制凭空删去。

28—30每轮另测该接口，按“进程序号＋轮序号”的奇偶平衡先后顺序，额外240轮。旧apply、旧copy＋apply、新输出三者分列，逐次验证完整输出及源只读，绝不将新接口时间覆盖到旧copy字段。新接口四线程接近三倍，只能说明该接口的局部结果；旧接口三倍与纯映射三倍都尚未满足，整体目标仍在进行。

所有策略仍保留纯apply≤1/3、任一apply进程≤0.9、准备＋已预热首100图中位≤1等门槛。24—27另以旧copy＋apply≤1/3判断；28—30把新接口≤1/3另列，旧copy原数值全部保存。**各版accepted_on_this_host均为false**。24四线程准备＋首组中位比1.004926、26为1.016848，也有轻微回退。30某进程准备＋首组比1.019122，中位0.788743；不能写成每个进程均不退化。“准备＋已预热首组”排除中间预热，不是冷启动。

大页只通过对象自身2MiB对齐分配及MADV_HUGEPAGE建议；每个候选计时候选句柄在前后读取smaps核对实际AnonHugePages。26/27/30全部主体大页，28/29为32MiB主体大页加4字节普通页尾保护。Windows只读探测表明当前令牌没有SeLockMemoryPrivilege，没有更改权限或安全设置。依据为[Windows大页文档](https://learn.microsoft.com/en-us/windows/win32/memory/large-page-support)、[Linux THP文档](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)及[Intel gather文档](https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/intrinsics-for-gather-operations.html)。建议成功与实际使用大页分开记录；普通页环境的速度不能由本次THP结果推定。

## 正确性、精度及限制

24/25执行基础55组与6条非法侧表、缓存55组/24,000槽、域证书8状态/24条拒绝、独立16M表重建及1344次有限比较/6条只读拒绝、m17/18/25/33正负斜率48组，Windows两库单/四级8组完整256³与100图，全部零差。24签名测试在首次执行前将后缀改为有色灰阶，以实际触发新16bit路径，v1/v2策略与生成器均保留；没有原生失败后改源码补测性能。

26/27为WSL同AMD上的528次有限后端/偏移比较、12组完整256³，以及完整新表独立重建和9条诊断/复制拒绝，全部通过。28—30在此基础上新增1056次分离/同址有限比较、44条非法参数/重叠/溢出拒绝，以及另12组完整输出接口256³，共24组完整域配置。所有完整表均用独立旧输出流解码核对；30的坐标检验不复用C++逆地址算法。每轮性能输出完整SHA、源不变和保护区均通过。26—30未重新执行多网格正负斜率矩阵；分配失败、其他OS/编译器、实际Skylake尚未验证。

全部16,777,216输入颜色的逐字节等价保证固定模型精度不下降。单级输出SHA为7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146，四级为3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22，100图为f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528。本阶段没有重新拟合、修改模型或放松误差；既有RGB欧氏误差继续适用，不是CIEDE2000或官方Threshold验收。百图为已见数据，不能称盲测。

## 证据、复现与协作

[原始档案](../../report/data/skylake-threefold-v1/README.md)约9.85MB，235份原始成员；31份源快照/2062项源成员及121项二进制成员的标准库审计通过。[独立性能复算](../../report/data/skylake-threefold-v1/performance-audit.json)核对全部800轮身份、输出、配对公式和实际大页，没有重新计时。二进制/对象在各build目录的ZIP；构造/验证生成器另存ZIP，大输入流复用原同SHA资料，不称完整无数据运行包。

主实现为`experiments/skylake-{direct16,byteindex,paged32,pageindex,fused16,load16,tileindex}-runtime`，相应v1/validation/perf计划分别冻结。新目录均保留独立版本，不覆盖已验23。Linux以30为例，按测量源ZIP原字节恢复旧依赖后，在新输出目录依次运行：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-tileindex-v1.json --output artifacts/new-tile-build --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
python3 scripts/verify_skylake_tileindex_linux.py --plan experiments/skylake-tileindex-v1.json --build artifacts/new-tile-build --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/new-tile-full --affinity-cpus 0,2,4,6
```

性能须先保存引用新build/full结果SHA的新策略，然后用`bench_skylake_tileindex_linux.py --policy 新策略 --output 新目录`；不得改旧回执或绕过身份检查。旧源存在Git换行归一化，应从measured-source.zip恢复实际字节，不修改旧计划SHA掩盖差异。归档可用标准库独立检查：

```sh
python3 -I -S scripts/audit_skylake_threefold_archive.py --archive report/data/skylake-threefold-v1 --output artifacts/new-archive-audit.json
```

创建Draft前全量获取40个PR、2个独立issue、2个Discussion及122组REST评论/review/行内记录，GraphQL审查线程0，分页完整。与上一阶段已读快照比较，既有正文、相关意见和Discussion没有变化；新增PR46正文已读，仍为Draft且无评论/review/审查线程。[协作核对](../../report/data/skylake-threefold-v1/remote-check.json)保存完整范围、原始链接及祖先：337a3dd（[#9基线/环境](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[#7内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7)）、876e15b8（[#27保护](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)）、397cc367（[#29相等mean](https://github.com/WyEhNf/flash-chroma/pull/29)）实际包含；相关公共实现未改，历史集成证据仍见[#37](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)，不冒充本轮重跑。

[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)要求区分模型误差与实现正确性，继续遵守；[#8](https://github.com/WyEhNf/flash-chroma/issues/8)接口/实板/预算与GUI #40仍独立。官方派生表许可、预算、Threshold及真实Skylake性能仍未验收，不关闭相关事项。后续继续研究更紧凑的精确块字典和存储路径；这一Draft只是保存可审查的检查点，不是完成声明。
