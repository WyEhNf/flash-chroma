# 二维ID布局、四ID先行与普通写组合未通过验收

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：固定模型RGB8精度不降，通用AVX2下相对修订23的纯映射和真实输出在1/4线程均达到三倍吞吐；Status：Failed（候选73），整体任务In Progress。**73完整精度通过，首次性能系列及测量控制失败，未采用，整体三倍目标尚未完成。**

本阶段基于Draft [PR #68](https://github.com/WyEhNf/flash-chroma/pull/68)头`90f2b68fcdea30edec07deabdebb64cd849ba93c`，分支为`codex/skylake-tilexy-t0-20261021`。[源码与构建计划](../../experiments/skylake-tilexy-t0-v1.json)在构建前冻结。73保留72的16MiB线性ID表和逐字节相同的线性内核，新增16MiB二维表；仅原地AVX2且`workers>1`使用54的8×8×1颜色布局、65的四ID先行及68的T0普通写。65536像素块及`schedule(static)`保留，单线程、嵌套OpenMP与全部分离输出走线性路径。模型、逐级Q16/RGB8舍入和公共默认不变。

第二表直接对模型生成的线性ID作自逆置换：`t=((c>>5)^c)&0x38; index=c^t^(t<<5)`，不读取照片、gold或历史输出。新增三个只读tilexy接口报告格式17；原direct接口仍为格式9。第二表分配失败回线性，线性分配失败保留23。普通写使用原`pack/output_four`，没有把57的NT预排值送入普通输出，也没有NT或SFENCE。独立静态审计确认四ID先于该组调色板加载，64/32/8像素热循环分别378/188/53条指令，无栈引用或循环内常量加载；两个像素对象无外部call、gather、BMI2、AVX-512寄存器或EVEX编码。空asm只约束编译顺序，不是硬件栅栏或性能证明。

实际环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库、glibc2.43。Release SIMD使用`-mavx2 -mtune=skylake -ffp-contract=off`，无native、AVX-512或fast-math。绑定来宾CPU0/2/4/6并核对实际OpenMP团队、TID单CPU集合；来宾空闲不等于宿主独占或固定物理核，没有锁频、控温和实际Skylake证据。最终SKU未知，继续保留通用AVX2。

[完整域结果](../../report/data/skylake-tilexy-t0-v1/skylake-tilexy-t0-linux-full-v1/results.json)覆盖两库、单级/四级、标量1线程和AVX2请求1/4线程：12组原地加12组真实输出，各遍历16,777,216种RGB8，全部字节和哨兵零差。另通过2208次有限原地、4416次分离/同址、736次保护页、1280次目标对齐、44次API拒绝，以及direct和tilexy各9次拒绝检查。独立解析以分通道加权式逆置换全部16,777,216个ID，与实际线性导出零差；预期输出使用此前已验独立u64/完整流，本阶段没有重算或重新拟合oracle。固定模型精度未下降，不扩大为其他模型全面验证。

线性逻辑SHA为`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`，二维物理SHA为`f9e24d3c02ead4561072c95492f01da8be0362e3f326e3dd4da566810d3ec0ab`，四级完整域输出SHA仍为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。四级句柄记账44,823,884字节，对照23为11,269,404；单级272,883对272,835。差额包含两个AlignedTable元数据及两张各16MiB表，不是RSS。性能阶段两表前后诊断均要求各自VMA恰好16MiB、2MiB对齐及完整THP覆盖，均通过；未新增分配失败注入。

首次性能策略生成器在写入validation身份后因`KeyError: confirmation_policy`停止，尚未写性能策略，也没有原生或性能调用。[preflight回执](../../report/data/skylake-tilexy-t0-v1/skylake-tilexy-t0-preflight-v1/failure.json)保留原源和失败。v2只核对已有validation完全相同，将模板字段改为`confirmation`后冻结策略；首轮性能在v2之后首次执行，不是失败后的基准重测。

[冻结长批次策略](../../experiments/skylake-tilexy-t0-long-perf-v1.json)沿用72口径：四个串行新进程、角色ABBA及交错线程顺序，每角色各建一句柄；每线程先候选同句柄A/A，再直接比较23/73的legacy和outplace。每批1线程16内轮、4线程64内轮，先批内均值再取四worker候选/参考比中位。16个控制批次和32个比较批次共1920内轮，48次完整100图预热和48次批末SHA；**不是每内轮独立SHA**。源、哨兵、团队和绑定均核对。准备+首组使用预热后的首个实测outplace，不能称冷启动。

以下是控制失败系列保留的原始观测，不能作为可靠优化成绩，也不与旧场次收益相乘：

| 接口 | 1线程中位耗时比 | 4线程中位耗时比 |
| --- | ---: | ---: |
| 纯映射apply | 0.3641525656874 | 0.4871891371647 |
| 真实分离输出 | 0.2962958967227 | 0.2036207917090 |
| 旧copy+apply | 0.539969 | 0.768521 |
| 准备+首组真实输出 | 0.667718 | 0.797872 |

| A/A纯apply | 四worker的B/A | 中位比 | 控制结论 |
| --- | --- | ---: | --- |
| 1线程 | 1.038490 / 0.795068 / 1.036134 / 0.881878 | 0.959006 | 单对0.795068低于0.8，失败 |
| 4线程 | 1.009560 / 1.027380 / 1.042768 / 1.030730 | 1.029055 | 中位及全部单对通过 |

控制门槛事前固定为中位`[1/1.10,1.10]`、每对`[1/1.25,1.25]`；四线程控制有效不能挽救整个系列。两接口各1/4线程中位耗时比仍要求≤1/3，另保留最差纯映射对≤0.9及准备+首组≤1。73的两档纯映射均未达三倍，且单线程控制失败。[确认决定](../../report/data/skylake-tilexy-t0-v1/confirmation-decision.json)因此跳过唯一独立确认，新增确认原生调用0，不重测、不择优、不采用。现有计数也不能把失败直接归因为写等待。

[110份原件及独立复算](../../report/data/skylake-tilexy-t0-v1/README.md)包含源码ZIP、库、完整域、静态审计、preflight失败及全部首轮数组；`audit.json`独立复算1920内轮和配对门槛。固定照片为100张1024×768 RGB8，共235929600字节，SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`；批末输出SHA为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。映射计时含API、对齐、尾部、fence及线程工作，不含IO、解码、分配、SHA或模型准备；不代表官方Threshold或端到端服务器成绩。

复现须在独立副本按冻结SHA恢复模型、照片和首级oracle，并使用不存在的输出目录；以下为原执行路径，不得覆盖现有档案：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-tilexy-t0-v1.json --output artifacts/skylake-tilexy-t0-linux-build-v1
python3 scripts/verify_skylake_tilexy_t0_linux.py --plan experiments/skylake-tilexy-t0-v1.json --build artifacts/skylake-tilexy-t0-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-tilexy-t0-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_tilexy_t0_long_linux.py --policy experiments/skylake-tilexy-t0-long-perf-v1.json --output artifacts/skylake-tilexy-t0-long-perf-v1
```

候选库SHA为`368a88f4435e10c8578f33154faad4d57d6ede5e5b49a6a9da747d97e06d57e7`；归档库仅是本机Ubuntu/glibc2.43证据，目标服务器需重编译。110份原件清单不含后补README、阶段说明及远端刷新回执。创建PR前对相关正文、评论、review与行内线程的检查范围、状态和限制，以本阶段`report/data/skylake-tilexy-t0-v1/remote-check.json`实际回执为准。74的PREFETCHW工作另行交付，不属于73测量结果；整体三倍目标、实际Skylake性能及官方派生表许可/预算/Threshold继续待验证。
