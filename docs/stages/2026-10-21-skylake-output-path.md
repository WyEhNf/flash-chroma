# 稀疏预取与输入输出编排研究

**整体300%吞吐目标尚未达到。** 修订56—58完成72组完整RGB8 API配置逐字节等价，但均未通过冻结的增量周期筛查，没有新增整轮墙钟成绩。最新有效整轮仍为[#50](https://github.com/WyEhNf/flash-chroma/pull/50)的40相对23：纯映射1/4线程2.6444倍／3.1200倍，真实输出3.3066倍／4.3069倍。单线程纯映射缺口保留，不采用历史更快单点，也不乘算阶段收益。

分支`codex/skylake-sparse-prefetch-20261021`依赖[#53](https://github.com/WyEhNf/flash-chroma/pull/53)及`6753b12ff84f8b6d6e01f7c632847db9163ff0da`。实际阶段提交见[交付元数据](../../report/data/skylake-output-path-v1/delivery-metadata.json)。当前为Draft研究，原23、公共默认、模型和只读AGENTS.md保持原状。

## 实现与静态依据

| 修订 | 改动 | 固定保留的路径 |
| --- | --- | --- |
| 56 sparsehint | 每64像素只对前方128像素起的四个颜色发出ID表T0提示，间隔16像素 | 40的线性ID、GPR读取、NTA、NT64及65536工作块 |
| 57 qwordpack | 按四组输出位置预排字节，再以三条选择操作拼接96字节 | 40的输入和查表树、普通尾部、NTA、NT64及SFENCE |
| 58 splitpack | 57输出加两个独立XMM输入展开，避免50的先合并YMM再拆分 | GPR的ID/调色板读取、精确8像素尾部、NT64及SFENCE |

三版仍是16MiB线性u8 ID表加RGB32调色板，格式9，四级句柄28,046,644字节；物理表SHA与40相同，未改变模型或准备算法。表只由原四个稀疏模型按逐级RGB8构造，不使用gold、照片或完整源LUT。

56不是39的全量查表预取：每轮只增加四次提示。最后一次4字节输入读取从像素`p+176`开始，`p+178<=pixels`保证包含多出的下一像素R字节；形成未来指针位于该保护条件内。未来读取在当前64像素输出之后，不受原地写影响。v2计划在首次构建前增加178与242附近以及八像素截断后的边界长度，v1计划未执行。没有扫描距离或提示密度。

57参考[Google libyuv的RGB32转RGB24实现](https://chromium.googlesource.com/libyuv/libyuv/+/refs/heads/main/source/row_gcc.cc)中零尾qword组合思路，独立推导四种预排索引P0=`[0,1,2,4,5,6,3,7]`、P1=`[2,4,5,6,3,7,0,1]`、P2=`[5,6,3,7,0,1,2,4]`、P3=`[3,7,0,1,2,4,5,6]`。得到A=`[a0,a1,a2,0]`、B=`[b1,b2,0,b0]`、C=`[c2,0,c0,c1]`、D=`[0,d0,d1,d2]`，分别用blend 0xc0、半区选择0x30、blend 0x03构成三个32字节输出。普通尾部仍用原pack。GCC把半区选择等价编译成`vblendps 0xf0`，只是按位选择，没有浮点计算。

58仅替换57的`read_wide`：load16(p)和load8(p+16)，用PALIGNR12生成后半，两个XMM分别PSHUFB，再各提取四个索引。精确读取24字节，没有采用51的额外4字节读取；前四索引在表达式上无需等待跨lane合并。保留每64像素全部读取后写入192字节，普通尾部前SFENCE。

另一agent只读核对了字节标签、源码及实际反汇编。每64像素原地主体静态指令40／57／58为345／321／297，分离输出为346／322／298。57的五个常量、58的六个常量均在循环外加载，两个主体均没有栈访问或向量spill。58没有重建输入YMM合并链，但仍有48次VPEXTRD。静态减少不等于周期或吞吐改善，详见[汇编核对](../../report/data/skylake-output-path-v1/assembly-audit.json)。三个原回退对象均与参考逐字节相同，当前对象没有外部调用、PEXT、gather、AVX512或FMA。

## 验证环境及结果

实际环境是Ryzen9 8945HX、Windows11上的WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库，Release。AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`；不使用native、AVX512或fast-math。绑定来宾vCPU0/2/4/6，不保证宿主固定物理核；没有锁频、控温、独占宿主或实际Skylake测量。

每版独立解码16,777,216颜色；两库×单/四级×标量1/AVX2请求1/4线程，执行12组in-place与12组真实输出完整域，共72组。56另通过2976个有限in-place、5952个输出/别名、992个保护页比较；57/58各为2208、4416、736。每版另有1280个全部目标对齐比较和44个新API拒绝检查。全部字节及哨兵零差，当前固定模型精度不下降；未重新拟合，不声称相对官方LUT零误差。

四级gold SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，单级为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`。所有参考23库SHA为`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。构建、输入、完整域和源码身份均在回执中绑定。

首次像素前冻结筛查：同场40为参考，1线程周期比≤0.95且4线程≤1.05，才进入整轮墙钟。每版每角色/线程一次预热、一次计数，三版共12项。纯映射及真实输出1/4线程均三倍的整体门槛、最差配对、准备成本和独立确认要求不变。

| 同场40→候选 | 1线程周期/像素 | 4线程合计周期/像素 | 1线程指令/像素 | 周期比1／4线程 |
| --- | --- | --- | --- | --- |
| 56 | 3.91837→3.84052 | 4.45359→4.63419 | 5.40104→5.63486 | 0.980132／1.040551 |
| 57 | 4.33612→4.12352 | 5.22775→5.36690 | 5.40104→5.02645 | 0.950968／1.026617 |
| 58 | 3.92734→3.89640 | 4.10331→4.41148 | 5.40104→4.65182 | 0.992124／1.075103 |

56/57单线程失败，58两档失败。57的4.903%改善没有舍入成5%通过；58减少约14%指令仍未改善足够周期，不能将静态操作减少直接换算为速度。所有决定保留，均跳过整轮墙钟，没有重复同源画像或择优。各行参考发生变化，只比较同场配对，不跨行比较绝对值。

逐TID四事件的running/enabled≥0.99、计数求和、实际团队、前后单CPU集合及16MiB全部THP均已离线核验。generic cache不标为精确L3事件；周期含少量启停、ct调用及OpenMP结束自旋，受本机频率和虚拟化影响。输入为100张1024×768 RGB8，共235,929,600字节，SHA `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`。输出SHA `f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。源和哨兵保持，无新端到端、IO、解码或冷启动成绩。

## 失败记录、档案与复现

56首次PMU入口因策略绑定旧v1计划而在计数前拒绝；保留原准备源与失败记录，修正为v2计划后复用原二进制，只执行一次有效计数。57首次静态入口要求特定`vperm2i128`助记符，遇到等价`vblendps`而在任何像素执行前拒绝；保留原检查源和反汇编，另建v2检查入口，没有改变C++或重编译。两项均完整归档，未删除失败后重新命名为首次成功。

[研究复核](../../report/data/skylake-output-path-v1/research-audit.json)检查冻结源、二进制、72组完整域和12项计数；保留56/57先行复核。[档案核验](../../report/data/skylake-output-path-v1/archive-check.json)通过79份原始文件、3,983,716字节、9份源码ZIP的678项成员和57项二进制成员。后补报告、58汇编审计、交付元数据及操作前刷新不在原始清单中。

大流按计划同SHA恢复，模型复用`report/data/skylake-palette-v1/fixed-models.zip`。40原构建及完整域复用既有同SHA档案。58原执行命令如下；复现实验应在独立副本使用新的输出和身份记录，不覆盖旧证据：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-splitpack-v1.json --output artifacts/skylake-splitpack-linux-build-v1
python3 scripts/inspect_skylake_splitpack.py --plan experiments/skylake-splitpack-v1.json --build artifacts/skylake-splitpack-linux-build-v1 --output artifacts/skylake-splitpack-linux-static-v1
python3 scripts/verify_skylake_splitpack_linux.py --plan experiments/skylake-splitpack-v1.json --build artifacts/skylake-splitpack-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-splitpack-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/profile_skylake_splitpack_pmu.py --policy experiments/skylake-splitpack-pmu-v1.json --output artifacts/skylake-splitpack-pmu-v1
python3 scripts/audit_skylake_output_path_complete.py --output artifacts/new-output-path-audit.json
```

PMU策略绑定实际build/full SHA，新构建必须重新绑定，不能冒充原记录。归档Ubuntu/glibc2.43二进制只作本机证据，目标服务器应重新编译。

## 协作检查与后续

完整检查47个PR、2个独立issue、2个Discussion、143组REST意见及0个审查线程，分页完整；既有正文/意见相对已读检查点无变化，新#53全文与原发送文本逐字核对。依赖#53两项常规CI成功，但不代替数值或性能验证。创建前再次刷新见[操作前协作记录](../../report/data/skylake-output-path-v1/pre-create-remote-check.json)，关联问题和修复祖先见[完整核对](../../report/data/skylake-output-path-v1/remote-check.json)。main b19c5a0、#7/#9的337a3dd、#27的876e15b8、#29的397cc367均已包含。

本阶段仅交付Draft，不合并。issue8关于派生表、内存预算和Threshold的约束，以及实际Skylake性能仍未确认；未新增分配失败注入、其他模型矩阵或GUI40工作。下一步应针对ID→调色板依赖与访存并行性提出可验证的单一改动；当前结果不支持继续只凭指令数量挑选候选。总目标保持active。
