# 16题内存独立分支：原线性ROM的真正只读部署加载

Agent：`/root/memory`；Operator：当前16题用户；Status：Completed（模式限定），唯一提交微实验、完整质量及正式场完成。原地1T控制失效，其余三个模式有资格，四模式整体50未证。分支`codex/p16-memory-20261023`；Draft PR由root维护。

## 机制与边界

保持原a399、原M16D线性8bit ROM、旧Clang C99/AVX桌面DLL及1056B ABI完全不变。新点只在Windows加载层。原`study_memory_rom.loadrom`为取得`ctypes.from_buffer`地址使用`ACCESS_COPY`；[Python文档](https://docs.python.org/3.12/library/ctypes.html)要求该接口支持可写buffer，[mmap文档](https://docs.python.org/3.12/library/mmap.html)区分只读和COW。[Microsoft MapViewOfFile文档](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile)说明COW会为整个视图计提交额度；直接用`PAGE_READONLY/FILE_MAP_READ`可避免这一保留。这是待验证的部署机制，不是新增压缩格式或更换计算算法。

原ROM SHA`146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5`，16778272B；旧DLL SHA`442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723`。模型容量仍为**16779328B**，没有把提交额度、物理RAM、工作集、文件容量或ZIP混为一谈。新loader是Windows专属；portable C99源码未变，不宣称跨平台改善。

## 预冻结与唯一提交实验

在任何新映射观察前，AST/所有执行源及输入SHA被冻结到计划`95b289d4f0a40baa1974fd902a6ceb59f7986c5bc67216f8ae8714468d1cc855`。唯一驱动会话53279正常exit0；没有改源或补跑。Windows11 26200/AMD64、Ryzen9 8945HX、Python3.12.14/NumPy1.26.4，OMP/BLAS/Numba环境1线程；质量明确请求1/4 native线程。root授权非性能窗，未计吞吐。

三个fresh进程同imports、相同旧DLL和流式SHA预检在before之前：原ACCESS_COPY、相同新owner的WinAPI-COW、WinAPI-RO各一次。原函数源不改，仅在构造器返回和prepare前观察地址及状态后立即还原。每页只读一个字节及末字节，不复制ROM。预定门槛是映射后、prepare后和逐页读取后三个时点，各自相对before的PrivateUsage增量，RO均比两个COW对照至少省1MiB；否则停止完整质量。

| 角色 | 刚映射Private增量B | prepare后B | 逐页后B | close后B |
|---|---:|---:|---:|---:|
| 原ACCESS_COPY | 16814080 | 16814080 | 16814080 | 0 |
| 新WinAPI-COW | 16818176 | 16818176 | 16818176 | 0 |
| 新WinAPI-RO | 32768 | 32768 | 32768 | 0 |

三个时点的保守净省均为**16781312B**，通过原门槛。系统commit原数值另存，受其它进程影响仅作辅助。prepare后工作集原COW52948992B、新COW52994048B、RO52965376B，基本相同，不能称减少约16MB物理RAM或工作集。

三进程首/末页VirtualQuery均为MEM_MAPPED，COW真实Protect=8（PAGE_WRITECOPY），RO=2（PAGE_READONLY），没有靠接口名字猜测。close后PrivateUsage全部回baseline；新owner句柄均157→157。原ACCESS_COPY进程句柄157→158的+1观察保留，原因未查明，不写成三组均无句柄变化；新owner合同通过也只限本轮。

## 生命周期与完整质量

所有者管理文件、section、view；打开期间禁止其它写共享。prepare失败或close先清零借用model，再释放资源；关闭幂等，关闭后不再暴露地址。构造各失败位置清理顺序、清理本身失败时保留资源供显式重试均有注入合同；真实缺失/零长/畸形文件及写共享拒绝另验。调用者不得与native apply并发close，此owner没有提供并发锁。

通过门槛后执行RO的C99/AVX各1/4线程、原地/分离共**8完整256³**输出SHA`3c9ce8d9…`和**8完整100图**SHA`f3c0d907…`，输入照片SHA`e13278cf…`匹配，保持原a399所有误差和逐图结果。580有限/同址/非对齐/零长、39真实格式/IO拒绝、144输入/目标双保护页、24只读ROM尾guard通过。actual/count1/count256三夹具覆盖全部256合法palette和最后ID255/ffffff；不是截短实际palette来省内存。

Windows文件view本身按页取整，EOF后字节未必立刻NOACCESS；因此ROM字节精确末端保护页是另用相同原ROM内容复制进只读VirtualAlloc夹具的native边界检查，不能冒称是文件映射EOF保护。新增loader的真实只读保护由VirtualQuery独立验证。

失败合同前后句柄158→158；quality峰工作集108490752B、峰private95674368B，包含Python、照片块和合成夹具，不能当纯核心RAM或prepare专属峰。该质量没有新增编译、改ISA或改变ROM。新RO不能仅凭同一计算库或质量通过继承旧COW速度资格，实际模式资格另见下面唯一正式场。

## 唯一正式协议与宿主前置观察

预注册8角色：fast78/80、原ACCESS_COPY/新WinAPI-COW/新WinAPI-RO各AVX/C99；主分母仍每worker较快78/80。四新进程0x55允许集、轮转/反序、原地/分离1/4线程、1预热+5完整百图，共848调用及8RSS。A/A单对[.8,1.25]且中位[1/1.1,1.1]，失败模式全部清空。RO/原COW及RO/新COW仅辅助配对，不用慢分母授档，不按结果补跑。

完整质量之后，此正式协议与源/输入闭包另冻结为`902d0421bb99382d7ed5179949ad5f6f4f2bc0639e9ff612cc0db241ab0bde29`。root另授窗口后，第一份启动前宿主检查因两长期GUI `server.py`进程触发STOP，**没有启动driver或native调用**。核对PID35472/138924及凭据服务基线后，原样保留v1，再用v2记录新PID类别/路径匹配/1秒CPU增量；新候选为空才启动唯一正式会话36165，exit0。不杀未知进程，也不称宿主绝对独占；仅本研究组数值、构建、ZIP/Git工作静默。该前置STOP不是性能失败后重跑，902d源/owner/ROM/DLL/轮次全程未改。

独立60位Decimal由原五轮秒数字面值复算848次调用、四worker最劣、AA及六档，通过冻结审计。全部warm/final输出摘要相等；没有增加计时或择优样本。

| 模式 | AA worker0 | worker1 | worker2 | worker3 | 中位 | 有效性 |
|---|---:|---:|---:|---:|---:|---|
| 原地1T | 1.110928 | .998260 | .941633 | **1.358290** | 1.054594 | 失效，全部档清空 |
| 原地4T | .996817 | 1.070320 | 1.084103 | 1.156368 | 1.077211 | 有效 |
| 分离1T | .815285 | .951957 | 1.098563 | 1.139426 | 1.025260 | 有效 |
| 分离4T | 1.017473 | .949746 | 1.096533 | 1.039571 | 1.028522 | 有效 |

下表为每模式四worker**最劣吞吐保留%**，均以同worker较快78/80为分母。首列为失效模式的原始描述值，不能据此授档或当作有效低50反例。

| 角色 | 原地1T（失效raw） | 原地4T | 分离1T | 分离4T |
|---|---:|---:|---:|---:|
| 原ACCESS_COPY AVX | 87.359860 | 94.693713 | 81.024579 | 87.512546 |
| 原ACCESS_COPY C99 | 51.895784 | 65.393850 | 59.802048 | 59.186962 |
| 新WinAPI-COW AVX | 76.478942 | 78.457458 | 75.678186 | 93.427005 |
| 新WinAPI-COW C99 | 48.930651 | 62.566186 | 53.711236 | 60.643004 |
| 新RO AVX | 80.368522 | **85.549118** | **82.082670** | **93.038857** |
| 新RO C99 | 50.207411 | **67.707850** | **52.194756** | **61.889692** |

精度六档100/90/80/70/60/50均通过，因为输出保持原a399。RO AVX三个有效模式各进80/80/90速度档及其以下档；RO C99各进60/50/60及以下档。若仅要求这三个有效模式同时成立，AVX最劣82.082670%达80，C99最劣52.194756%达50；若要求全部四模式，原地1T失效使整个联合36格均**未证**，不是有效数值低50的严格失败。尤其不能将RO C99 raw50.207411%取作补齐原地1T，也不以历史COW结果恢复RO资格。

## 辅助配对与提交额度

下表用control耗时/RO耗时，列四worker最劣与中位百分数，大于100表示RO更快；原地1T只描述，不作正式配对结论。这些较慢控制不影响主档位。

| 模式 | RO对原AVX 最劣/中位% | RO对新COW AVX | RO对原C99 | RO对新COW C99 |
|---|---:|---:|---:|---:|
| 原地1T（失效raw） | 89.822379/95.948644 | 96.083516/105.611101 | 91.286054/96.123952 | 102.609325/104.298254 |
| 原地4T | 89.262496/99.697893 | 101.835436/108.683161 | 97.541248/102.264058 | 96.228958/103.852502 |
| 分离1T | 91.958310/96.822138 | 94.291635/99.430896 | 87.279212/106.722370 | 97.176606/100.604501 |
| 分离4T | 99.605990/102.326777 | 93.522833/101.297743 | 95.830993/100.671106 | 96.680524/104.994841 |

因此，保持同一计算库不保证各worker耗时完全相同；这次有效配对仍有最多约12.72%的单worker吞吐退化，不能写成无速度代价或把差异归因到未隔离的缓存/调度因素。

八fresh RSS同正式imports及0x55，照片数组分配前读取；与早先三fresh微实验导入群不同，不能拼绝对峰。

| 角色 | before private B | prepared private B | before WS B | prepared WS/峰WS B | 模型容量B |
|---|---:|---:|---:|---:|---:|
| fast78 | 22769664 | 55648256 | 36093952 | 66404352/133505024 | 28046644 |
| fast80 | 22654976 | 54599680 | 36020224 | 65191936/133394432 | 28046644 |
| 原AVX | 22810624 | 40030208 | 36102144 | 53538816/53538816 | 16779328 |
| 原C99 | 22716416 | 39936000 | 36057088 | 53547008/53547008 | 16779328 |
| 新COW AVX | 22814720 | 40038400 | 36065280 | 53571584/53571584 | 16779328 |
| 新COW C99 | 22925312 | 40144896 | 36196352 | 53612544/53612544 | 16779328 |
| RO AVX | 22888448 | 23330816 | 36130816 | 53555200/53555200 | 16779328 |
| RO C99 | 22724608 | 23162880 | 36081664 | 53583872/53583872 | 16779328 |

正式RSS的RO AVX提交增量442368B，对两个COW对照增量保守少16777216B；RO C99增量438272B，少16781312B。实际PAGE_READONLY仍被逐角色核实。WS相近、模型容量相同，不能把这项提交收益列成更小capacity的联合前沿。

## 原件、复现与未完成事项

[发布manifest](../../report/data/p16-memory-readonly-v1/manifest.json)保留三fresh五阶段、完整质量、宿主STOP/重分类前置、两个冻结计划/执行源、八角色所有原轮次/CPU端点/地址/八RSS、Decimal及辅助配对。旧ROM/DLL按原SHA复用；ZIP不当RAM。暂存/HEAD原字节与CRC另审，不补运行。

```powershell
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/run_readonly_rom_quality.py --output artifacts/p16-readonly-rom-quality-v1
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/bench_readonly_rom.py --build F:/Hackathon/worktrees/p16-memory-20261023/artifacts/p16-memory-build-v2 --roms F:/Hackathon/worktrees/p16-memory-20261023/artifacts/p16-memory-rom-v2 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --output artifacts/p16-readonly-rom-perf-v1 --repeats 5
```

这是已执行唯一场次的命令，保留输出目录，不覆盖补跑。新loader四模式整体50尚未证、其它系统/目标机/素材未测；不自动扩移植或重复这轮。portable C99和官方派生表许可边界不变，Draft供审阅而非默认合入或部署推荐。
