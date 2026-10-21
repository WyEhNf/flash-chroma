# ANDN内存输入与分入口编译的精确运行时研究

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：固定模型完整RGB8精度不降、通用AVX2、相对修订23吞吐至少三倍；Status：Failed（75—78），整体In Progress。**78精度及A/A通过，但纯映射仅2.970394/2.525664倍，未达整体三倍。** 按冻结规则跳过确认，不重测择优、不采用。

本阶段分支`codex/skylake-andn-load-20261021`从Draft [PR #70](https://github.com/WyEhNf/flash-chroma/pull/70)的`02479a4e518c49b1c6bf6aac264f1c3251d889a6`继续。阶段提交以本PR实际头为准。75、76、77、78各有独立源码目录、计划、构建身份及静态证据，未覆盖或修改前一版失败原件。

75把原65/72宽循环的32位输入MOV加AND24替换为mem32 ANDN，常量为`0xff000000`，AT&T操作数顺序为内存、掩码、目标，结果为`(~mask)&input32`。表、四ID先行、调色板、输出预排、NTA/NT/SFENCE保持。[Intel SDM的ANDN定义](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf)和[GCC15 Extended Asm](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/Extended-Asm.html)是语义及约束依据。精确4字节内存输入使用`aligned(1),may_alias`类型和`cc`描述；24字节精确尾部不调用ANDN读取。

研究假设是减少指令与退休槽，扩大可在途的独立工作。[uops.info原始测量](https://uops.info/html-instr/ANDN_R32_R32_M32.html)指出Skylake的base+disp形式执行2个微操作、占1个退休槽，整数端口受p1/p5限制；后端输入、ID、调色板读取次数均未减少。静态少指令不等于吞吐提高，也不能证明加载队列或ROB是当前瓶颈。

各版均只在独立ANDN像素TU启用`-mbmi`，其余AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`。构造时一次检测`__builtin_cpu_supports("bmi")`；不支持则使用72原字节线性TU。新增只读enabled接口报告CPU和表是否允许该句柄走ANDN，null及无直表的单级返回0；它不是标量调用实际执行ANDN的声明。没有强制环境开关。唯一16MiB表仅从原模型构造，不读取照片、旧完整域或gold。

75静态失败：不透明`uint32_t`输出使GCC在每条ANDN后加入自MOV零扩展，宽循环指令没有减少。原地64/32环为321/170条，分离为322/171条；分离宽循环还有真实`%rsp`上界读取。没有加载候选库、执行像素或计时。静态脚本首版仅因Windows默认GBK解码UTF-8计划失败，原脚本与回执保留；修正只显式指定UTF-8，没有修改源码、计划或对象。

76将输出变量改为`uintptr_t`，模板仍用`%k0`执行32位ANDN，准确描述x86-64清除目标高32位的完整寄存器结果，读取宽度仍4字节。自MOV消失，原地64/32环降为257/138条，分离降为258/139条；后者仍从`-0x8(%rsp)`读取入口第五参数`pixels`，包括64环的预取/循环比较及32环结束比较。因此同一无栈门槛仍失败，未执行像素或计时。未执行的验证/性能脚本保存在76前置目录，没有生成性能策略或完整域回执。

77仅继续缩短循环状态的生命周期：用当前源/目标游标和`remaining`替代长期原始基址、`p`及总像素数。归纳不变量为`remaining = 初始pixels - p`、两游标各为初始地址加`3*p`；前缀每次处理1像素后`+3/-1`，主体每次64后`+192/-64`，32/8尾部分别`+96/-32`及`+24/-8`。72/40/8条件及406预取条件与旧式逐迭代等价。64像素仍全部读取/组装后才输出三条完整缓存行，初始对齐、合法预取地址、精确尾部及fence位置保持。冻结计划含完整边界推导。

77原地64环254条但出现三次真实rsp剩余计数访问，仍静态失败。分离64环255条且无栈。GCC把两处32像素尾部化为最多执行一次的直线区段；原回边识别器没有将其当作通过，保留原失败结果，另用独立脚本明确审计原地135条、分离136条直线区间。每区间均有32条mem ANDN、无栈、自MOV为0、四ID先行及先读后写。该补充没有挽救原地64环失败，没有执行像素或性能。

78分别保留76已无栈的原地specialization和77已无栈的分离specialization，每个独立TU只编译一个实际使用入口，删除该TU另一入口。数值算法、表、常量、边界、线程调度及两种run写法均不改。这是编译可达路径组织的修正，没有依据性能样本选择路径；此前三版原生像素调用均为0。

78实际重新构建后，原地64/32为257/138条，分离64/32为255/136条；对应原线性321/170、322/171条。四区段均无热区栈访问、无额外零扩展、64/32条正确mem32 ANDN、四ID先行、全部读取后写入，ISA和编译范围检查通过。32直线计数范围为首ANDN到末输出；这是静态结构比较，不把指令数比当作速度比。首版检查器把分离直线尾最后一次ANDN覆写已死亡掩码误作恒定性失败；保留原脚本/结果，v2逐条追踪每次消费时的真实值及后继用途，确认各次输入均为`0xff000000`，尾部最后使用后没有后续ANDN。没有改源码、对象或无栈等门槛；后续性能身份单显式绑定v2通过回执。

实际构建环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu Linux6.18.33.2、GCC15.2、Python3.14.4标准库；Release无native、AVX512、BMI2或fast-math。尚未在Skylake实机或真实缺BMI1硬件执行。源码和只读回退审计不能冒充后备硬件执行。

78的独立16,777,216色物理表重建、12组原地和12组真实输出完整RGB8均逐字节通过，字节及哨兵差异为0；有限原地2208、分离/同址4416、保护页736、目标对齐1280、API拒绝44、direct拒绝9及新只读null检查1均通过。实际enabled为single=0、chain=1。单级记账272859、四级28046644字节，分别比23多24和24+16MiB，不是RSS。直表SHA仍`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`，四级完整输出仍`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。完整回执SHA为`d349abe0d6021c5c03bdde3fd8204c3b69344be4e93fc6d57d38b3bfe820733b`。没有重新拟合、完整其他模型矩阵、分配失败注入或缺BMI1硬件测试。

完整域后首次冻结[受控长批次](../../experiments/skylake-andn-split-long-perf-v1.json)，策略SHA为`b306490389e48d028e479c91977822d6e593f3bad24f62d705ed66a3f64c857a`，验证身份SHA为`5b5a629e343e515942d82fa4437465f1db671ef2b97cebe3f969f2564b9885a4`，绑定静态v2 SHA`6405a5ba175a9db75a18270ecdcca567c21a152e7e7842da362ac5c5a0139932`。独立审计SHA为`274e3403df21f272f1e2dfdb4b95fe059c8137161665b07f2d28f4f82540b021`，包含dispatcher无BMI/EVEX泄漏核对。胶水复核确认原ABBA、线程顺序、16/64内轮、A/A、三倍和唯一条件确认门槛保持，性能源码ZIP额外保存所绑定静态回执。

首次四个串行新进程完成：每角色一句柄，两线程档先candidate同句柄A/A、再原23和78的legacy/outplace；ABBA、线程1/4交错，每批16/64内轮，共1920内轮、48次预热及48次批末完整100图SHA，非逐内轮SHA。批内均值形成每进程配对比，再取四对中位。全部actual team/TID绑定、源/哨兵、前后实际ANDN启用、16MiB精确VMA/2MiB对齐/全THP通过。固定100张1024×768 RGB8共235929600字节，输入SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，批末输出SHA`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。

| 接口 | 单线程中位耗时比／吞吐 | 四线程中位耗时比／吞吐 |
| --- | ---: | ---: |
| 纯映射apply | **0.336656／2.970394倍** | **0.395935／2.525664倍** |
| 真实分离输出 | 0.263826／3.790373倍 | 0.200252／4.993720倍 |
| 旧copy+apply | 0.496153／2.015507倍 | 0.707083／1.414261倍 |
| 准备+首组真实输出 | 0.600927 | 0.671948 |

纯apply单线程四对0.332952/0.399794/0.340359/0.329743，四线程0.378969/0.392103/0.418212/0.399768。单线程中位仍大于1/3，不舍入为通过；四线程四对均高于1/3。最差进程≤0.9、两档真实输出及准备+首组均通过；准备+首组是预热后首个测量加准备，不是冷启动。

A/A单线程四对1.002033/1.116762/0.991423/1.037664，中位1.019849；四线程1.011654/1.014765/1.012167/1.046158，中位1.013466。两档均满足原中位`[1/1.10,1.10]`及任一对`[0.8,1.25]`，控制有效。两个纯apply门槛失败，故唯一确认跳过，新增确认调用0。没有重测、与旧40/65/74场次拼接，或把分离输出达标当成整体达标；本轮未直接配对原线性内核，不能断言ANDN相对它的独立收益或性能瓶颈已被证明。

计时包含真实API检查、映射、对齐、尾部、fence和线程工作，排除IO、解码、分配、SHA及模型准备。保持原空闲前置和CPU0/2/4/6约束，未改变系统安全、频率或大页设置，未锁频控温。所有原始数组、静态失败和检查器修正均按原字节归档；归档脚本独立重算1920轮及各项中位，不产生新像素或计时。

78结束后另做唯一固定2×2×2输入砖块的只读筛查，未构建新原生或测性能。230项palette来自既有cache-gold，不能用完整输出仅出现的221项代替；coarse/fine分别为`PEXT(c,0xfefefe)`和`PEXT(c,0x010101)`的数学索引，未执行PEXT原生指令。每8输入以base8+8×3bit的u32表示，需例外614/2097152块，最大ID跨度11，全16,777,216色编码重建零差。固定照片异常8包占0.00314107，通过事前≤0.05；64像素主词表平均行集合41.320387，对原49.415259的比为0.83618679，未达到事前≤0.80，计入4912字节例外池为0.83672256。停止此方向，不扫其他尺寸或实现计时。环境为Windows11、Anaconda Python3.13.12、NumPy2.4.6，区别于上述Linux原生验证；集合统计不是硬件miss或吞吐结果。脚本、协议、全部统计及输入SHA在[补充只读档案](../../report/data/skylake-andn-split-v1/skylake-brick2-packed-profile-v1/manifest.json)，不改主清单163份原件。

复现应在独立副本、按冻结SHA恢复输入后使用新输出目录，不能覆盖历史原件：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-andn-split-v1.json --output artifacts/skylake-andn-split-linux-build-v1
python3 artifacts/skylake-andn-split-static-v1/inspect-v2.py
python3 scripts/verify_skylake_andn_split_linux.py --plan experiments/skylake-andn-split-v1.json --build artifacts/skylake-andn-split-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-andn-split-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_andn_split_long_linux.py --policy experiments/skylake-andn-split-long-perf-v1.json --output artifacts/skylake-andn-split-long-perf-v1
```

218份提交中的实验/脚本/档案已通过`git cat-file --batch`与工作区逐字节比较，四计划全部源SHA、163份主档案大小/SHA及补充3份profile身份通过，`git diff --cached --check`通过。档案中未执行脚本的原有EOF空行保持原字节，通过目录属性免除该项格式告警，没有为通过检查修改冻结记录。远端核对范围、原始链接、已包含修复、issue当前状态及Discussion缺口见[协作回执](../../report/data/skylake-andn-split-v1/remote-check.json)，不以历史评论覆盖最新正文。

78计划SHA为`c62d97a402705692977250f0e626c9587a7190e97cf9a9b44f4d6a22840532d8`，构建SHA为`2f951a5c2daa035716c2715f6d2803282e8434a8b9d645d8c0ecb7170144cbe6`，候选库SHA为`51ed7ccd99817c61e89487db8f4afe1970932f637050515ae937280c0cd1532b`。归档.so只作本机证据，服务器应重编译。官方派生表许可、内存预算、Threshold及真实Skylake表现仍待验证；Discussion刷新接口缺口继续披露，保持Draft，不合并或关闭事项。
