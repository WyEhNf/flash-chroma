# 相对修订23的三倍目标：字典、载荷、输出与硬件计数

Agent：Codex；Operator：WyEhNf；Task：精度不降，当前吞吐达到300%；Status：In Progress（本阶段为WIP/Draft，整体三倍目标未完成）。

修订31—37继续直接比较23。37的**四线程真实输出接口**配对耗时比0.330218，吞吐3.0283倍；其纯apply仅2.3099倍／1.7786倍，1线程新接口2.6133倍，旧copy＋apply也未达三倍。不能把这个单项结果当作整体完成。七个候选均通过固定模型完整RGB8色域逐字节等价验证，性能门槛均为false。

阶段分支为`codex/skylake-load-packing-20261020`，基于[PR #47](https://github.com/WyEhNf/flash-chroma/pull/47)的b55a444cac7ac7e4438eefa524e723a983be9e92；刷新main仍为b19c5a0，已包含。旧23、公共默认、模型和AGENTS.md未改。阶段提交以本PR实际头为准，实际执行身份另由各计划、源、构建、二进制与输入SHA绑定。

## 路线与完整结果

以下为每进程5轮中位、同进程候选／23相除、四进程配对比的中位。小于1更快，三倍吞吐需≤1/3。所有数字只来自该候选自身与23的同场比较，不能将不同协议绝对时间相除或乘算历史收益。

| 修订 | 方法 | apply，1／4线程 | 旧copy＋apply，1／4线程 | 真实输出，1／4线程 | 四级句柄字节 |
| --- | --- | --- | --- | --- | ---: |
| 31 | 4MiB u16索引＋8字节ID块字典，三层gather | 0.850789／0.851604 | 0.879754／0.906294 | 0.689636／0.451660 | 15,988,040 |
| 32 | 相同块索引，字典直接存RGB32，减少一次gather | 0.718846／0.700587 | 0.777655／0.835874 | 0.633602／0.396933 | 17,560,880 |
| 33 | 16MiB线性字节ID，独立标量ID/调色板载荷，AVX2打包 | 0.430196／0.550277 | 0.531384／0.763265 | 0.402568／0.382293 | 28,046,644 |
| 34 v2 | AVX2宽输入及三次32字节RGB24输出 | 0.655756／0.769637 | 0.716544／0.850005 | 0.583792／0.413687 | 28,046,644 |
| 35 | 小端输入码重排表，省去bswap，宽标量载荷 | 0.451224／0.573864 | 0.543661／0.760948 | 0.453521／0.397208 | 28,046,644 |
| 36 | 同一小端表，普通整数拼装三个u64输出 | 0.510498／0.698159 | 0.594588／0.845772 | 0.495034／0.433110 | 28,046,644 |
| 37 | 完整缓存行非临时输出，发布前SFENCE | 0.432927／0.562248 | 0.527789／0.770616 | 0.382663／0.330218 | 28,046,644 |

23四级句柄11,269,404字节。31/32额外48字节元数据，33—37为24字节；原表和完整回退均保留。31实际39,239个不同8颜色块，索引4,194,308字节含尾保护，字典78,478个u32，capacity 524,280字节；32字典313,912个u32，capacity 2,097,120字节。实际模型只有221种最终颜色，但构造仍使用原缓存可得的230项精确调色板，不读取旧gold来建立表。超过65535个不同块时回退，相关阈值/分配失败未注入测试。

31减少大索引容量，却增加依赖查表；32去掉调色板层后仍未达到目标，因此停止扩展该字典路线。33用三个精确8字节输入载荷及字节反转提取RGB24，再做八个独立ID/调色板读取。35把表地址改为`R | G<<8 | B<<16`，宽循环可用32bit输入载荷加mask，边界仍严格读24字节。36通过整数移位/或操作直接拼装RGB24；它经原AVX2资格入口调度，核心本身是普通整数SWAR，不声称其提速来自向量数学。

37先用精确标量前缀将目标对齐到64字节，再一次预读64像素，六次32字节非临时写恰好覆盖192字节（三条完整缓存行）。已流写的路径在普通尾部及返回/OpenMP barrier之前执行SFENCE；普通前缀/尾部不与流写主体混用同一缓存行。宽输入仍限制在当前4096像素线程块内，所有输出只覆盖自己的有效RGB24范围。这里使用的对齐与fence合同见[Rust官方intrinsic文档](https://doc.rust-lang.org/core/arch/x86_64/fn._mm256_stream_si256.html)，缓存行连续写原则参考[Intel优化手册](https://www.intel.com/content/dam/doc/manual/64-ia-32-architectures-optimization-manual.pdf)；这不是把手册中的旧处理器性能数据外推到Skylake。实际对象含12条vmovntdq和2条sfence（两入口合计），没有外部调用、AVX512或FMA。

## 环境、绑定修正与保留的失败

实际环境仍为本机Ryzen9 8945HX（16核32线程）/Windows11上的WSL2 Ubuntu，Linux6.18.33.2、GCC15.2、Python3.14.4标准库。Release为-O3/-DNDEBUG，独立TU为-mavx2/-mtune=skylake/-ffp-contract=off；没有全局native、fast-math、AVX512或新增权限。用户明确按通用AVX2继续；**没有Skylake实机成绩**，未锁频控温。

所有性能仍固定CPU0/2/4/6四同L3物理核，AB/BA/BA/AB四个串行新进程，线程顺序平衡，各配置5轮100张1024×768图。每次原生repeats=1，235,929,600字节预载；IO/解码/分配/哈希不计时，逐轮完整输出SHA、源不变和保护区全部核对。apply、旧copy＋apply和真实source→destination接口继续分列，真实接口的验证、前缀、尾部及fence都在计时内。构造仍4线程，准备墙钟与“准备＋已预热首100图”另存；后者不是冷启动。

31—33保留旧协议：整个进程允许CPU0/2/4/6，实际团队探测必须在不同物理核，但没有每线程固定位置。34 v1第4进程一开始就未通过团队探测，只有worker0—2共60轮旧模式和60轮新输出；**不以这三个进程生成结论**，日志、源ZIP与失败说明完整保留。

随后先做32次4/1线程绑定探测，再冻结34 v2和35—37的新协议：OMP_PROC_BIND=TRUE，OMP_PLACES={0},{2},{4},{6}，主线程固定CPU0。每档探测实际线程CPU顺序，并在测量前后保存每个TID的单CPU允许集合；它们覆盖四个不同物理核。34 v2四个worker全部测完后，父进程汇总误插入worker局部变量`cpus`而NameError。这个错误只影响汇总，没有改变原生调用、计时、逐轮校验或四份回执。

34 v2测量源保持原字节，没有为修汇总而重新计时；独立工具从四份完整原始记录复算到`offline-results-v1.json`，明确标记original_aggregation_completed=false。35—37在首次计时前修正该汇总层问题。另提供34未来复现的`bench_skylake_pack32_pinned_fixed_linux.py`与v3-recipe，**本阶段没有执行v3计时**。历史v2入口保留错误以对应冻结源，不是推荐复现入口。所有失败都没有覆盖或删轮。

本阶段七个完整比较共560轮旧模式＋560轮真实输出；失败v1另有120轮部分记录，只归档不参与接受判定。[独立标准库审计](../../report/data/skylake-load-packing-v1/performance-audit.json)核对全部身份、输出、实际线程/大页及配对公式。各候选任一进程/准备回退都保留，例如36四线程旧copy有一进程比1.174916，37准备加首组有一进程1.076882；不能把中位改善写成每进程不退化。

## 完整域、内存边界与精度

31—33分别通过528次有限后端/偏移比较、1056次分离/同址比较和44条新API非法/重叠/溢出拒绝；34—36为960/1920次有限比较、44条拒绝及320次不可访问尾页/只读源比较；37扩展为1536/3072次有限比较、44条拒绝、512次保护页比较及1280次全部64种目标偏移/独立源/原地别名比较。保护页检查会让真实读越界或写只读源直接失败，不以尾哨兵替代读边界检查。

每版都独立解码完整新表，31/32另核对整个字典及6条只读接口拒绝；小端表以独立坐标转置验证，不复用C++地址算法。每版两库×单/四级×标量1/AVX2请求1/4的12组完整256³in-place，以及另12组完整新接口输出，全部逐字节相同。运行时输出一致，原回退对象在同场参考/候选间逐字节相同；没有重新执行其他网格/大调色板的完整矩阵，没有注入分配失败或在其他CPU验证。

全部16,777,216输入逐字节等价，因此当前模型精度不下降。四级输出SHA仍为3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22，100图为f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528。没有拟合、放宽误差或改变逐级RGB8量化；既有指标是RGB欧氏距离，不是CIEDE2000，百图为已见数据，不称盲测或官方Threshold验收。构造只使用原稀疏模型，gold仅用于独立验证。

## 结构筛选与硬件计数

两项只读筛选在进入新内核前停止：固定8³恒色砖块的128KiB粗表只覆盖已见照片14.1586%的完整8像素包；固定整数投影77R+150G+29B经**完整色域恒色认证**后仅覆盖1.7336%的包。同一个投影值可能对应多种最终颜色，不能以近似灰度替代精确RGB。预先选择的研究兴趣门槛为50%完整包覆盖，两个候选均未进入性能测试；不是对其他参数或三倍目标不可达的证明。

未安装perf或降低perf_event_paranoid。只读探测显示当前值2，允许打开本进程用户态cycles/instructions/cache-references/cache-misses。随后冻结一次探索性画像：23/33/35/37各1/4线程，四事件一组，每个参与TID单独计数；每配置一次预热、一次计数，完整100图输出SHA通过。总8次计数没有墙钟提速输出，不能替代ABBA验收。所有running/enabled≥0.99，前后TID一致，8项组计数求和独立复核通过。

| 画像 | 1线程 周期／像素 | 1线程 退休指令／像素 | 4线程 合计CPU周期／像素 | 4线程 退休指令／像素 |
| --- | ---: | ---: | ---: | ---: |
| 23 | 15.2340 | 4.4594 | 11.6845 | 4.5099 |
| 33 | 6.0001 | 7.2073 | 7.6910 | 7.2800 |
| 35 | 6.1021 | 5.3178 | 7.1738 | 5.3845 |
| 37 | 5.6494 | 5.4343 | 6.6276 | 5.5048 |

35退休指令少于33，但单线程周期接近，说明继续削减指令本身不足以解释结果；优先研究缓存/预取路径是**推断**，不是已定位的唯一瓶颈。频率、虚拟PMU和少量启停/ct开销影响周期，四线程结束后的短暂自旋也可能被计入。泛化cache事件通常与末级缓存有关，但映射依CPU而变，也可含预取/一致性活动；不冒充精确L3 miss或由周期反推出新墙钟成绩。定义及限制参考[perf_event_open手册](https://man7.org/linux/man-pages/man2/perf_event_open.2.html)。

## 归档、复现与协作

[原始档案](../../report/data/skylake-load-packing-v1/README.md)约9.30MB，235份原始文件。23份源快照/1687项源成员及133项二进制成员审计通过；完整560＋560轮、失败60＋60轮、两种失败、32次绑定探测、8项PMU画像和两项停止的结构分析都保留。生成器ZIP只用于溯源，不应在现有测量工作树重跑以覆盖冻结策略；复现应使用独立副本、新构建/输出与新SHA策略。

七套独立实现在`experiments/skylake-{dictionary,rgbdictionary,loadindex,pack32,loadle,swar,stream}-runtime`，各v1/validation/perf计划冻结源与数据。Linux以37为例：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-stream-v1.json --output artifacts/new-stream-build --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
python3 scripts/verify_skylake_stream_linux.py --plan experiments/skylake-stream-v1.json --build artifacts/new-stream-build --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/new-stream-full --affinity-cpus 0,2,4,6
```

通过后保存引用新build/full SHA的策略，再运行`bench_skylake_stream_pinned_linux.py --policy 新策略 --output 新目录`。旧依赖有Git换行归一化，先从measured-source.zip恢复实际字节，不改旧SHA绕过检查。原始大流不打包，小模型复用前轮固定包；PMU入口不需要外部perf程序，不能在正式配对计时同时运行其他画像/大流计算。归档独立复核：

```sh
python3 -I -S scripts/audit_skylake_load_packing_archive.py --archive report/data/skylake-load-packing-v1 --output artifacts/new-load-packing-audit.json
```

创建Draft前完整读取41个PR、2个独立issue、2个Discussion、125组REST评论/review/行内，GraphQL审查线程0，分页完整。既有正文与意见未变；新增47正文与先前发送文本逐字相同、头b55a444，无评论/review/线程。两项常规workflow成功不代替显式实验验收。[协作核对](../../report/data/skylake-load-packing-v1/remote-check.json)保留原始链接、状态及b19c5a0/337a3dd/876e15b8/397cc367/8355402/b55a444等修复祖先；[#9](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[#7](https://github.com/WyEhNf/flash-chroma/issues/7)、[#27](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)、[#29](https://github.com/WyEhNf/flash-chroma/pull/29)相关公共实现未改，历史集成仍见[#37](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)，不冒充本轮重跑。

[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)的模型/实现区分继续遵守；[#8](https://github.com/WyEhNf/flash-chroma/issues/8)接口/实板/预算与GUI #40仍独立。官方派生表许可、内存预算、Threshold及实际Skylake性能未验收，不关闭相关事项、不合并此Draft。下一步根据硬件计数，研究输入流缓存提示和受控预取；整体目标保持进行中。
