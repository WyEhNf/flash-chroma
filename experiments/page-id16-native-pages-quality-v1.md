# Native页指针单版：构建前冻结的验证边界

Agent：/root/memory。状态：新候选，仅构建与元数据调用已获授权；有限native、完整域、照片、性能与跨平台运行分别待协调授权。原P4、copy4、ROM、对象和历史结果不编辑。

本文件冻结后续验证的入口、有限计数和停止规则。验证器执行源码在后续native授权前另冻结；当前没有以本文件代替已执行质量。只允许一个4096槽候选，不依据结果调参或扩变体。构建首错/机器码门失败保留STOP，不修改后覆盖重采。

## 新入口与表示

新类型按值嵌入旧base，再借用4096个native页指针。新prepare只在完整验证后写槽、最后发布view；任何正常失败都保持caller view和槽原字节。新clear只清view，不改表、ROM或其它共享副本。ROM仍可非对齐；view与槽必须满足本构建的C99 offsetof保守对齐探针。调用者必须提供真实可访问对象，纯C不探测任意失效地址或写权限。

新核心入口`jshc_p4_pages_apply`，新可选OMP入口`jshc_p4_pages_apply_parallel`只有threads参数，无AVX/kernel选项。新prepare/clear/validate和layout元数据各有独立符号。库会链接原`page_core.o`供旧prepare/validate使用，但新验证必须绑定新入口，记录旧、新地址及Python入口尝试次数。旧AVX不链接到新DLL，不计作新视图路径覆盖。

完整路径固定5种：独立C99 DLL的core分离，主DLL OMP C99的1T/4T×原地/分离。有限与图像guard另加独立core原地，共6种。所有full/photos进入新view，实际函数符号/地址绑定失败即STOP。

## 固定有限合同及计数

有限长度固定22项：0,1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4095,4096,4097,65535,65536,65537。起始偏移0,1,3,7；22×4×6=528，加合法零长NULL输入输出6项，合计**534**。每次独立u64 oracle逐字节比较且检查可写跨度外哨兵。

**IO拒绝243项**，拒绝须在读取图像/写目标前发生，完整target不变：

| 项目 | 数量 |
| --- | ---: |
| 旧10种：NULL源/目标、源目标双向部分重叠、源/目标与base重叠、源/目标与ROM重叠、pixels乘3溢出、源地址范围溢出；每种6路径 | 60 |
| 新5位置×源/目标×6路径：view+40、view+47、槽首、槽末字节、槽首前2字节的3B跨界 | 60 |
| OMP非法threads=-1,0,257 | 3 |
| clear后的零view，6路径 | 6 |
| NULL view，6路径 | 6 |
| view错位1..7，6路径 | 42 |
| 伪造槽表指针错位1..7，6路径 | 42 |
| 槽指针NULL/地址范围溢出，各6路径 | 12 |
| 槽表指针指向ROM/view，各6路径 | 12 |
| 合计 | 243 |

格式拒绝固定21种：16次独立内容变异（magic/version/shift/count0/count257/logical/unique0/unique4097/reserved1/reserved2/palette-alpha/unused-palette/first-map4096/last-map65535/pool-id/guard）和5种独立长度（0,31,9247,合法长度-1,合法长度+1），沿用旧P4对应单页合法夹具。分别用零view及已准备view两状态，共**42 prepare拒绝**；view和整个槽表原字节保持。

其它prepare错误固定32种×两状态=**64拒绝**：count=0/1/4095/4097/SIZE_MAX(5)，NULLview(1)，NULL槽(1)，NULLblob配0/实际长度(2)，view/槽/blob范围溢出(3)，view错位1..7(7)，槽错位1..7(7)，view/槽/ROM三对对象的完全及部分重叠(6)。同样保存所有可访问实对象的前后字节，不能借拒绝测试触碰无效指针。每个格式/其它逻辑拒绝在已准备状态后额外以原view重放固定图像，**53旧状态输出重放**单独计数，不混入534。

生命周期固定**4场景**：只读view副本可apply；clear副本归零且ROM/槽不变；原view继续apply；重复clear幂等。clear拒绝NULL及错位1..7共**8项**。这两个数是场景/拒绝数量，不冒充内部API调用总数。

夹具固定实际3082页、单页单色、单页全256色、4096页/合法最大pageID4095；独立验证每fixture全部4096个槽的实际地址，**16384槽等式**。prepare必须覆盖原垃圾槽，不读取其初始值。最高合法serialized ID是4095，65535作为格式拒绝；没有把旧block1024的65535合法边界搬到P4。

图像NOACCESS guard固定18长度（0,1,2,3,7,8,9,15,16,17,31,32,33,65535,65536,65537,131071,131072）×6路径=**108项**。对四夹具分别做精确ROM末端NOACCESS×5完整路径=**20项**，精确native槽表末端NOACCESS×5=**20项**；必须命中最后map槽、页内4095、最后pool页及palette255。ROM偏移0..7×5完整路径=**40非对齐项**。ROM允许byte对齐不放宽槽表本机对齐；guard都真实用VirtualAlloc/VirtualProtect，不能仅用哨兵代替。

## 完整域、逐图、资源与授权顺序

每个完整路径处理全部256³；固定外部R高位枚举，使用独立u64 oracle并检查SHA `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。每路径独立100图逐图u64校验，并核总输出SHA `f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，照片输入SHA `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`。不读gold选择参数。

5完整域/5×100图/534有限/243 IO/42格式/64其它prepare/53旧态重放/4生命周期/8clear/108图像guard/20ROMguard/20槽表guard/40非对齐/16384槽等式各自计数并断言，禁止使用执行过程中累积总数推定入口覆盖。quality记录真实DLL SHA、函数地址、sizeof/对齐、ROM/表/view容量、栈及进程峰值；后者包含Python/库/oracle/夹具，不能称prepare峰。OMP≤4、BLAS1，可与其它非计时质量并行，明确环境。

当前允许：冻结→唯一generic x64 Clang C99构建+GCC可选OMP胶水→实际机器码门→只调用4个layout元数据函数。模型APIprepare/apply/clear/validate均不在本次允许范围。门要求新apply实际使用native指针加载，旧热路径已加载pageID的左移12消失，仍报告三次依赖读取。prepare左移12是允许的离线填表步骤，不能错误检查整个对象禁止它。sizeof和对齐实测不能替代有限native。

后续若另获授权，先有限与guard（首错STOP）；再完整域/逐图（首错STOP）；通过后才另冻结性能。四模式自身双阶段与外围AA、所有worker/phase最劣、主分母同场更快78/80和100..50档均保持；任一有效低50则拒绝全局50，4T限定不救全局。不得自动WASM/跨目标编译或性能。
