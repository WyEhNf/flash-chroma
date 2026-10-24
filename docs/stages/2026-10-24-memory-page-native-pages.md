# 16题：调用者页指针视图质量通过，唯一正式性能拒绝50档

Agent：`/root/memory`（质量与正式执行）、`/root/memory_delivery`（交付复核）；Operator：当前16题研究用户；Status：唯一核心构建、有限合同、完整质量与1920调用/六RSS正式采样及独立Decimal审计完成；新候选全情形50档拒绝，整体研究继续。原9387738及所有旧ROM/ABI/源/对象/失败原件保持。

本版把P4每像素的LE16页ID加载后左移12/合并pool地址，提前到prepare，缓存4096个本机页指针。新C99实际生成页指针→pool byte→palette DWORD的三次串行读取，旧热路径shl12消失；没有减少一次数据依赖load，没有硬件pointer-prefetch的实测解释。代价是首级表由8KiB扩大到32KiB。唯一正式场存在有效45.226356%吞吐反例，并有相关AA失效，全部速度档不授；不能把失败归因于未经测量的缓存、频率或迁移。

## 真实表示与生命周期

不重新普查、导出或改变P4 ROM；新`jshc_p4_pages_view`按值保存旧40B base并借用caller页表，旧`jshc_p4_model`仍40B。纯C99核不malloc，不增加ISA、restrict或预取；可选GCC OMP胶水只有新C99入口，未链接原AVX对象作为新视图路径。

| 部分 | 实测字节 |
| --- | ---: |
| 原P4 ROM | 12633124 |
| caller 4096个native指针 | 32768 |
| 新view | 48 |
| 完整capacity | 12665940 |
| 比原P4增加 | 32776 |
| 比linear容量减少 | 4113388 |

本机view及槽要求8B对齐，由C99 offsetof保守探针实测；ROM允许byte非对齐。prepare在全部范围/对齐/交叠及原ROM验证后才写4096槽、最后发布view；失败不修改caller原view/槽。clear只归零view，不擦除或释放共享表/ROM；prepare/clear不得与apply并发。原ROM和caller表在使用期间须不可变。任意伪造或失效地址、写权限不能靠纯C探测。

native指针表是进程内表示，不能跨ASLR/进程/32与64位序列化复用。32位尺寸仍只是设计投影，未编译或运行；WASM、ARM、RISC-V、大端对象和实机均未执行，不因C99语法通过就扩张到这些速度结论。

## 冻结和机器码误判

构建前计划`65838f3968302872b8fbd7dfb734cb3d8ca7a1cd2410f02c9885a8e5bb41a997`绑定33源24输入，先冻结所有有限/完整预期计数。Clang21.1.0严格C99 generic x64、无AVX编译唯一新core，SHA `ac60efa6170af82cf9d285697f3b2a82123a32a908be8e29a4e680d0aedbb6bd`。

原观察器误要求字面scale8：Clang实际把`8*(code>>12)`折为`(code>>9)&0x7ff8`，再scale1读QWORD，原gate因此false并STOP。没有重编核心或回写原false；另授独立观察器`ae1dbf8d0e5e110f31653704f49456a12f36478b405385b2e83106f9a0195cca`逐地址验证8主lane+尾部真实页指针数据流，只首次编OMP胶水、链接及4项layout测量。

实际apply 0x3a3读view+40，0x3b0读页指针，0x3bb读pool byte，0x4bd读palette DWORD。新主DLL SHA `b326a9f3cc6dfa933964b65bf345bf15887d56c62904ad569554b42cf2e93ced`，独立C99 DLL `11860791a48ea49e85c32e1e8277bf7b5ad98fbae3ffc58c5102bbf9da9a80bf`。新core `.su`为prepare104B/validate72B/apply120B，OMP入口128B/工作函数96B；只是各函数静态帧，不是总调用链或四线程峰。

## 有限合同、夹具修正和独立日志审计

原有限计划`42767efa…`在`slots-view`夹具STOP：测试创建bad副本却把表指向另一个原model，未构成声明的自身交叠。原C不承诺侦测这种外部伪造表；不能把该返回当核心漏洞或通过。原v1没有在异常前持久化累计入口，是记录器缺口，原stdout/stderr/退出码完整保留。

独立V2 `907c17b1bf079bf700fd6e7191bf03231ac8be89a86ae3a01b5792ee3215c8a9`绑定42源46输入，只修6路径的表=self地址，并增加逐模型调用前/返回、逐receipt追加flush JSONL及finally累计/入口/峰；不改C/ROM/DLL/原四脚本/预期计数。硬fault可能跳过finally，已flush尝试不能当成功返回。

| 检查 | 实际通过数 |
| --- | ---: |
| 有限/u64索引及哨兵 | 534 |
| IO拒绝 | 243 |
| 格式拒绝，两种旧态 | 42 |
| 其它prepare拒绝，两种旧态 | 64 |
| 失败后旧态输出重放 | 53 |
| 生命周期场景/clear拒绝 | 4 / 8 |
| 图像NOACCESS/ROM尾/页指针表尾 | 108 / 20 / 20 |
| ROM非对齐 | 40 |
| 四fixture全部4096槽等式 | 16384 |

5完整路径为独立core分离及OMP1/4×原地/分离；有限和图像guard另加core原地。单页/全256palette/最大4096页/实际3082页均覆盖，最高合法页ID4095，65535拒绝。没有借额外guard放宽外部图像读取。

纯日志审计另保留两个机械STOP：第一次`finally=1`是Python语法错误，审计主体未执行；修字典literal后，“短标签全局唯一”断言因两项不同count0重放失败。原格式count0与prepare参数count0本来各有一次合法拒绝后重放；V3按Counter核它恰好2次，其余(kind,label)唯一，原53项不变。没有native重采或修改raw。

V3独立审计SHA `b9d9cfe79516203cef75d9afd3feabad6ebe57709ca364c7bee531c1faf46d31`通过19871条JSONL：1175尝试、1175逐一返回、17520 receipt和1finally。主DLL prepare124/clear29/OMP655；独立C99 prepare1/clear1/core365，均真实新入口。12个prepare交叠地址关系、4ROM尾/4槽尾对齐及ROM实际余数0..7另核。self字段及16384槽值没有原样dump，依据是冻结赋值/已完成断言，不冒充审计器重新读取内存。

## 完整域与百图

另冻结`c345f5bbc3118bff60854bba07e7b96ff5a782209a96466641655c75e7b10dc1`，46源52输入，唯一session47120 exit0。5路径各64块覆盖256³、各100照片逐字节和SHA一致，820新apply（core164/OMP656）、2prepare/2clear；各库4个layout getter另计，不混成模型调用。

oracle是已验证原M16D的独立u64索引/字节映射，**不是本轮重跑四级uint64插值**。完整输出SHA `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，百图 `f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，原输入e13278cf…；因此原模型mean/p99/max全部保持、精度保留100%而不是数学误差零。

独立完整日志audit SHA `9d0da2e2debc6073b8de2771f16bd52b57d550a3a27b4f06f88f277e625314e4`首次通过820配对、64块/100图、每模式164次、独立新符号/库/借用地址/源目标关系和原SHA。它读取既有日志，不重新生成图像或native；也不从block摘要反推原像素。

环境为Windows11 10.0.26200、Ryzen9 8945HX/x64、Python3.12.14/NumPy1.26.4；OMP≤4/BLAS1。有限阶段PeakWorkingSetSize157569024B/PeakPagefileUsage102223872B，完整阶段126791680B/71684096B，含Python、库、双映射/实例、oracle、夹具/照片和日志，不是prepare专属峰、纯模型物理RAM，也不拿两阶段绝对峰差当算法节省。PrivateUsage和结束WS另见原快照，不拿结束值充当峰值。逐图片核不分配堆。

## 复现与交付

已执行的freeze/build/finite/full入口依次为：`freeze_page_id16_native_pages_build.py`、`build_page_id16_native_pages.py`（原gate STOP）、`freeze/finalize_page_id16_native_pages_observer_v2.py`、`freeze/run_page_id16_native_pages_finite.py`（原fixture STOP）、`freeze/run_page_id16_native_pages_finite_v2.py`、`audit_page_id16_native_pages_finite_v3.py`、`freeze/run_page_id16_native_pages_full.py`、`audit_page_id16_native_pages_full.py`。解释器固定`F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe`，workdir为本工作树；完整命令、参数、版本和stdout/stderr见[发布manifest](../../report/data/p16-page-native-pages-quality-v1/manifest.json)的原件ZIP。

原质量提交只交付质量和实际容量，未提前授速度档。随后另授唯一六角色近邻配对正式场，结果如下；旧质量/失败原件未改，WASM或实板仍未执行。PR91由root在下一检查点统一刷新，仍Draft、未合并。

交付补记：6434cc8提交前的额外泛化字节检查在未冻结`.gitattributes`正常CRLF→LF处停止，但后续命令未检查退出码，提交仍继续，属于交付门流程错误，历史保留。另授HEAD针对性核验实际6434cc829611891cc838d748b605221c6342698f的65路径、46冻结源、5计划和92 ZIP成员全部通过，未冻结attrs/docs规范化单列，没有冻结SHA被Git改写，无需改源/renormalize。证据见发布包`head-source-audit.json`；之后stage/audit/commit逐步确认code0再进行依赖操作，没有借此重采native或改变质量结论。

## 唯一六角色近邻正式场

计划SHA `3a78b8c93efdfcb2649955b924888f647a35f0e1f8631a217e75faa55f3ae606`绑定55源码、76输入身份。没有重新编译核心/胶水/DLL、重新生成ROM、调整编译器或重复采样。原P4 AVX、旧copy4 C99和linear C99作为辅助对照，主分母固定ref78/ref80两个近邻配对；任何一个更快主对照的有效低50都不能用慢对照挽救。

四个fresh worker均保持六模型热驻留、同一只读master及相同工作地址。每个worker有四模式×五对照=20个pair-cell；每cell四次预热加ABBA/BAAB四组各五次计时，共24次。实际总1920次apply，其中1600计时；每cell只在两角色各最后预热及四计时组末做完整百图输出SHA，共480次，不能写成1920次输出摘要。起止及20个cell末master完整SHA共88次，并逐次核VirtualQuery整段READONLY及NumPy不可写。

原地记录apply和copy_apply两metric，后者包含copy、实际观测间隙gap和apply，不能称纯native memcpy+apply。分离只记录apply，没有虚构copy_total。SHA、模块与CPU观测均在apply计时外。四进程按已冻结镜像角色/模式/线程顺序运行；每pair两角色自身两次组中位数比须在闭区间[0.85,1.15]，任一失败只清该pair/metric，不中止剩余固定轮次、不补采。原地最终需要两个metric同时有效过线。

2026-10-24 UTC 04:53:35.0914898至04:57:54.1432215，session84142、driver及全部十个进程exit0。短间隔进程预检记录本组活跃research=0，长期baseline进程及未知进程未杀；不能声称宿主绝对没有其它活动。独立Decimal60审计首次exit0，SHA `7148d9e1368b27196412cccaa041feb6cd0f07599d6731eb06fbccb8cb44f7fa`，1920调用/1600计时/480输出SHA/88输入SHA/240自身AA/120 pair-metric全部与JSONL、实际调用返回、输入保护/地址/角色/库/容量/版本/环境一致。

240自身AA有36项失效，120 pair-metric有32项失效，其中主对照13项。每个主metric需八个pair（四worker×两个主对照）全有效，本轮六metric全部不足，因此全部清档。下列raw最劣包含失效pair，**只用于保存原记录，不是有效速度结论**。

| 模式 | metric | 有效主pair / 8 | 全部pair raw最劣保留% | 档位 |
| --- | --- | ---: | ---: | --- |
| 1线程原地 | apply | 6 | 27.029509 | 无效清档 |
| 1线程原地 | copy_apply | 5 | 30.182366 | 无效清档 |
| 1线程分离 | apply | 5 | 43.385198 | 无效清档 |
| 4线程原地 | apply | 6 | 53.715009 | 无效清档 |
| 4线程原地 | copy_apply | 6 | 66.318794 | 无效清档 |
| 4线程分离 | apply | 7 | 51.509978 | 无效清档 |

失效项不能掩盖有效反例：以下三个主pair的两角色自身AA均有效，其中最劣45.226356%直接否定全情形50，而不是仅因其它AA失效“尚未证明”。

| worker / 模式 | 主对照 | 两次配对保留% | 有效最劣% |
| --- | --- | --- | ---: |
| 0 / 1线程原地apply | ref80 | 49.329709 / 50.157726 | 49.329709 |
| 2 / 1线程原地apply | ref78 | 54.599915 / 49.888468 | 49.888468 |
| 2 / 1线程原地apply | ref80 | 46.526733 / 45.226356 | 45.226356 |

辅助比较也未形成速度收益：相对copy4，四线程原地apply/copy_apply以及分离apply各自四worker均有效，但最劣只保留88.029409/91.253047/86.352810%；相对linear四线程分离也有效、仅78.195492%。其它辅助metric包含失效pair，不能提取最好worker宣称加速，也不能恢复旧copy4的全局资格。实际机器码少ALU并未在该有效辅助证据中成为收益；没有测出缓存/时钟/分支因果。

精度输出仍完全相等、保留100%，但速度全情形50失败，故本候选六乘六矩阵36格全空；较低精度门槛不改变精确输出候选的速度失败。这里“空”只表示本候选无新资格，不擦掉原linear/P4 AVX/块字典历史，不表示所有实现不存在可行点。

## 正式环境和六fresh内存

所有worker与RSS在任何NumPy/native/OMP导入前，从固定plan验证Python3.12.14和环境并设置进程CPU允许集0x55=[0,2,4,6]，随后验证NumPy1.26.4。OMP_NUM_THREADS=4、OMP_DYNAMIC=FALSE、OMP_THREAD_LIMIT=4、OMP_WAIT_POLICY=PASSIVE，OpenBLAS/MKL/NumExpr各1；UTF8/IO编码固定。导入前后及清理后环境均实录并与冻结值相等。不是逐OMP线程绑核或锁频，不从此建立旧未绑定波动的因果结论。

每个进程分别在setup前、prepare后、close后记录实际模块路径/摘要/数量。四热worker按ref78先载入，实际四依赖来自`p16-memory-build-v2`；六RSS是独立进程，各自首次载入对应角色。ref80 RSS的gomp `0ee0eacd…`和gcc `b1339579…`确实不同于其余五RSS的gomp `fc756927…`/gcc `46c950eb…`，路径各属原角色目录。stdc++/winpthread也逐项记录，不把磁盘六目录当同时六份加载，不强认RSS使用同一个runtime。模块观察/清理后仍驻留的DLL或OMP线程资源不是RO owner句柄泄漏证明。

下列都是各fresh进程同imports下、prepare后快照和当时累计峰，含Python/NumPy/CRT/DLL/映射/loader及SHA预检；不是纯模型物理RAM、prepare专属峰或与旧阶段跨场相减的收益。没有图片缓冲。

| 角色 | capacity B | before WS B | prepared WS B | prepared PrivateUsage B | prepared PeakWS B | prepared PeakPagefile B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ref78 | 28046644 | 36683776 | 66813952 | 55734272 | 133902336 | 123011072 |
| ref80 | 28046644 | 36798464 | 67051520 | 55914496 | 134135808 | 123224064 |
| linear C99 | 16779328 | 36765696 | 54259712 | 24694784 | 54259712 | 24694784 |
| copy4 C99 | 12633164 | 36843520 | 50180096 | 24809472 | 50180096 | 24809472 |
| 原P4 AVX | 12633164 | 36708352 | 49975296 | 24596480 | 49975296 | 24596480 |
| native-pages C99 | 12665940 | 36810752 | 50094080 | 24735744 | 50094080 | 24735744 |

新view仍48B、caller表32768B、原ROM12633124B。每像素heap scratch为0，既有`.su`静态帧不等于OMP总栈峰，Windows句柄/页表/解释器对象不藏进模型capacity。close后的WS/Private/累计峰及句柄数全部保存在六份原RSS，不用close的较小WS充当运行峰。

性能原件已封存至`report/data/p16-page-native-pages-performance-v1`：源ZIP为59成员，包含原55执行源/plan及单列的两交付脚本、**未执行**WASM静态稿；raw ZIP为33成员，包含完整30份四worker/六RSS/driver/summary和3份UTC调用回执、日志、进程预检。两ZIP写后CRC、唯一成员和逐项原字节回读通过；固定summary SHA、十进程身份、角色容量、末环境和四份公开副本均另核。交付器和独立index/HEAD字节核先review再执行，每一步exit0后才进行依赖stage/commit；不覆盖原raw或重采native，Git交付状态以实际本阶段提交与其审计收据为准。WASM最大ROM高端起点更正为67108864−16786468=50322396B，低于48MiB但高于47MiB，低区小于24MiB仍不重叠；只是文本修正，没有编译、运行或速度授档。
