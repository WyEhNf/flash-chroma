# 16题：调用者页指针视图的独立质量阶段

Agent：`/root/memory`；Operator：当前16题研究用户；Status：唯一核心构建、有限合同及完整输出质量完成；速度协议仅静态，整体研究继续。原9387738及所有旧ROM/ABI/源/对象/失败原件保持。

本版把P4每像素的LE16页ID加载后左移12/合并pool地址，提前到prepare，缓存4096个本机页指针。新C99实际生成页指针→pool byte→palette DWORD的三次串行读取，旧热路径shl12消失；没有减少一次数据依赖load，没有硬件pointer-prefetch或提速的实测解释。代价是首级表由8KiB扩大到32KiB，可能增加缓存压力，性能未执行、不授档。

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

本阶段只交付质量和实际容量，六乘六速度矩阵不升级。六角色近邻配对性能是独立未冻结静态稿，必须另review/grant；当前无正式速度、WASM或实板成绩。PR91由root在下一检查点统一刷新，仍Draft、未合并。
