# 直接颜色表、二维分块与同源编译器研究

**整体300%吞吐目标尚未达到。** 修订53—55完成72组完整RGB8 API配置逐字节等价，但均未通过预先冻结的单线程周期筛查，没有新增整轮墙钟成绩。最新有效整轮仍为[#50](https://github.com/WyEhNf/flash-chroma/pull/50)的40相对23：纯映射1/4线程2.6444倍／3.1200倍，真实输出3.3066倍／4.3069倍。单线程纯映射缺口保留，不选用历史更快单点，也不乘算阶段收益。

分支`codex/skylake-direct-tiles-20261021`依赖[#52](https://github.com/WyEhNf/flash-chroma/pull/52)及`7f3a4790907ee64c25155c1683c24e743762c296`。实际阶段提交见[交付元数据](../../report/data/skylake-direct-tiles-v1/delivery-metadata.json)。当前为Draft研究，原23、公共默认、模型及只读AGENTS.md未改。

## 改动及静态依据

| 修订 | 实现 | 表／四级句柄 | 结果 |
| --- | --- | --- | --- |
| 53 directtile | 从44的RGB32直接表出发，4×2×2输入颜色共享64字节行，AVX2整数MADD计算地址 | 64MiB／78,378,292字节 | 单线程周期增加约90%，停止 |
| 54 tilexy | 回到40的u8 ID＋palette，交换R位3..5与G位8..10，每行8×8×1颜色 | 16MiB／28,046,644字节 | miss下降，但单线程周期增加约24%，停止 |
| 55 clangload | 40的像素TU源码逐字节不变，仅该TU改用Clang22；其余GCC | 16MiB／28,046,644字节 | 指令减少约9%，单线程周期约增1.6%，停止 |

53使用9个向量索引操作，不含RGB24展开与加载。高R/G经AND和PMADDWD，部分和最大131056；低位经PMADDUBSW/PMADDWD，部分和最大7、8，总和15。各位段互不重叠，不饱和、不溢出。24位索引是双射，构造器使用逆置换；独立验证器按R/G/B坐标加权读取64MiB表，另检查RGB32最高字节为0。它组合44的去依赖与49的颜色分块，但本次结果不能支持继续扩大表。

54固定使用`t=((c>>5)^c)&0x38; index=c^t^(t<<5)`，两次移位、三次XOR、一次AND。这个置换自逆，仅涉及位3—10，因此2KiB块、4KiB页、2MiB THP页编号都不变。地址低6位为`(R&7)+8*(G&7)`，每个对齐缓存行恰含一个8×8×1颜色块。独立解码采用分通道加法表达式，不调用生产XOR表达式。一次选定尺寸和轴，没有扫描布局后挑最快值。

两版地址公式、逆置换、运算界与边界经另一agent只读核对，未并发运行数值或计时。53/54均准确读取每8像素24字节，沿用40的NT64、NTA前瞻、65536工作块、读64像素后写192字节及普通尾部前SFENCE。没有为了提速放宽越界、原地别名或只读源合同。

55只编译当前`channel_avx2.cpp`为Clang对象，源码与40同SHA；dispatcher、模型准备、OpenMP、核心及原23/16/4回退仍由GCC构建，原三个回退对象与参考逐字节相同。使用已安装Ubuntu Clang22.1.2，编译器SHA `97b50a720cf5b662ebd3f5e7f64f995dc5f13999132124faaef37d7ddd6afbba`，显式选择GCC15头目录。CMake记录完整自定义命令，专用构建器核对编译器身份并归档，未更换系统默认工具。此前Clang21静态研究的是旧插值内核，本次首次研究40的直接字节表/NT打包内核。[Clang工具链文档](https://clang.llvm.org/docs/Toolchain.html)说明组件与运行库的组合；本次混合对象仍通过实际完整域验证，不以工具链说明替代ABI测试。

三版对象分别1953／1846／1339条静态指令；没有外部调用、PEXT、硬件gather、AVX512或浮点FMA。这些静态数量不等于每像素成本或性能。部分历史计划字段和54验证入口首行沿用来源名称，实际布局由新策略、格式号16／17／9及独立解码检查确定；已测源保持原字节。

## 环境、精度与完整记录

环境为Ryzen9 8945HX、Windows11上的WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库，Release。AVX2 TU固定`-mavx2 -mtune=skylake -ffp-contract=off`；55仅当前TU用Clang22.1.2。无native、AVX512、fast-math或全局ISA泄漏。CPU0/2/4/6来自来宾拓扑与线程绑定，不保证宿主固定物理核；未锁频、控温、独占宿主或测试实际Skylake。

每版独立解码16,777,216颜色，并执行两库×单/四级×标量1/AVX2请求1/4线程：12组in-place和12组真实输出完整域，共72组。每版另有2208个有限in-place、4416个输出/别名、736个保护页、1280个64种目标对齐及44条新API拒绝检查通过。每次完整域块262144像素，覆盖四个工作块。当前固定模型全部逐字节一致，精度不下降；没有重新拟合或声称相对官方LUT零误差。

四级gold SHA `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，单级SHA `7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`。所有参考23库SHA `b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。55物理表与40完全相同；53/54只改变物理编码，构造仍仅使用原四个稀疏模型与逐级RGB8，不读取gold、照片或完整源LUT。其他模型矩阵、分配失败注入、实际Skylake未新增验证。既有误差口径为RGB欧氏距离，不是CIEDE2000；100图是已见数据。

性能筛查在首次像素前约定：相对同场40，1线程周期比≤0.95且4线程≤1.05，才进入整轮墙钟。整体纯映射及真实输出1/4线程三倍、最差配对和准备成本门槛不变。每个角色/线程只预热一次、计数一次；每版4项，合计12项，没有同版重复画像或择优。

| 同场40→候选 | 1线程周期/像素 | 4线程合计周期/像素 | 1线程指令/像素 | 1线程generic miss/像素 |
| --- | --- | --- | --- | --- |
| 53 | 3.3907→6.4507 | 4.2253→7.4884 | 5.4010→5.5637 | 0.11067→0.14404 |
| 54 | 3.2474→4.0368 | 4.7030→4.4699 | 5.4010→5.9036 | 0.10675→0.05747 |
| 55 | 3.6033→3.6625 | 5.4906→4.3482 | 5.4010→4.9161 | 0.10976→0.10092 |

54/55四线程筛查通过，单线程失败；53两档失败。每版保存`screen-decision.json`，均跳过整轮墙钟。参考在不同画像中明显变化，不能跨行比较绝对值或将周期比当作吞吐。54的miss下降和55的指令下降均未带来单线程收益，停止当前候选；不据此宣称所有编译器或布局都无效。

逐TID四事件cycles/instructions/generic cache的running/enabled≥0.99，计数求和、团队、前后单CPU集合、输出SHA与实际THP容量全部复核。generic cache没有标为精确L3事件；计数含少量ct/启停及OpenMP结束自旋，不是精确内核延迟。输入100张1024×768 RGB8共235,929,600字节，SHA `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`；输出SHA `f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，源与哨兵不变。没有IO、解码、冷启动或官方端到端新成绩。

## 档案与复现

[研究复核](../../report/data/skylake-direct-tiles-v1/research-audit.json)核对冻结源、二进制、72组全域、12项计数与停止决定。[档案核验](../../report/data/skylake-direct-tiles-v1/archive-check.json)通过72份原始文件、3,901,123字节、9份测量源码ZIP的681项源成员和57项二进制成员。另保留53/54先行离线审计，未重复原生映射。后补README、交付元数据、静态检查及操作前刷新不在原始清单内。

原始大流按冻结计划同SHA恢复；模型复用`report/data/skylake-palette-v1/fixed-models.zip`。40的原构建/完整域复用既有同SHA档案。53/54使用公共构建入口，55使用核对Clang身份的入口。以下是55原冻结流程，输出必须尚不存在；复现实验应在独立副本使用新输出并保存新构建/计划身份，不覆盖旧证据：

```sh
python3 scripts/build_skylake_clangload.py --plan experiments/skylake-clangload-v1.json --output artifacts/skylake-clangload-linux-build-v1
python3 scripts/inspect_skylake_clangload.py --plan experiments/skylake-clangload-v1.json --build artifacts/skylake-clangload-linux-build-v1 --output artifacts/skylake-clangload-linux-static-v1
python3 scripts/verify_skylake_clangload_linux.py --plan experiments/skylake-clangload-v1.json --build artifacts/skylake-clangload-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-clangload-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/profile_skylake_clangload_pmu.py --policy experiments/skylake-clangload-pmu-v1.json --output artifacts/skylake-clangload-pmu-v1
python3 scripts/audit_skylake_direct_tiles.py --output artifacts/new-direct-tiles-audit.json
```

计数策略绑定实际build/full SHA，不把新构建冒充原回执。归档中的本机Ubuntu/glibc2.43库仅作证据，目标服务器应重新编译。

首次交付静态检查因PR52原文末尾空行触发格式规则而停止，尚未产生阶段提交。保留[失败记录](../../report/data/skylake-direct-tiles-v1/static-preflight-failure.json)和检查源，只对该原文设置末尾空行属性，保留档案字节；随后重新核对全部阶段Git blob及冻结源，没有重跑数值或计时。

## 协作与待办

完整检查46个PR、2个独立issue、2个Discussion、140组REST意见及0个审查线程，分页完整。既有正文、评论与审查记录相对已读检查点无变化，新增#52正文与原发送文本逐字核对，两项常规CI成功。创建前再刷新见[协作记录](../../report/data/skylake-direct-tiles-v1/pre-create-remote-check.json)；问题链接、状态与祖先见[完整核对](../../report/data/skylake-direct-tiles-v1/remote-check.json)。#7/#9的337a3dd、#27的876e15b8、#29的397cc367及main b19c5a0均已包含，不以CI替代这些修复的证据。#37历史整合和Discussion #4关于模型/实现区分继续遵守。

整体3倍、实际Skylake、[#8](https://github.com/WyEhNf/flash-chroma/issues/8)的官方派生表许可/预算/Threshold及实板、独立GUI #40仍待处理。保持Draft，不合并、不关闭。下一步应依据40与55机器代码研究指令依赖/输出组织或减少访存等待；本阶段没有该后续方案的成绩。
