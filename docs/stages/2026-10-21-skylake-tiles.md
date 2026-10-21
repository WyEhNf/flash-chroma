# 同容量颜色分块与索引成本研究

目标仍为精度不降、达到修订23的300%吞吐，**整体尚未完成**。本阶段没有新增墙钟提速成绩：47与49均未通过预先冻结的单次周期筛查，因此没有启动完整性能矩阵或重复计数择优。最新完整墙钟结果仍是[#50](https://github.com/WyEhNf/flash-chroma/pull/50)的40：独立配置协议纯映射1/4线程2.6444倍／3.1200倍，真实输出3.3066倍／4.3069倍，单线程纯映射未过3倍。

工作分支`codex/skylake-bmi2-tiles-20261021`依赖`07c6e16e2adbd10c02172898c0ab7fce99b92ad9`；本阶段真实提交号在[交付元数据](../../report/data/skylake-tiles-v1/delivery-metadata.json)中记录。原23、公共默认、四个模型与只读AGENTS.md未改。

## 研究变量与实现

| 修订 | 实现 | 执行范围 |
| --- | --- | --- |
| 47 tilebmi2 | 16MiB u8 ID表按4×4×4颜色分块，两个PEXT重排索引，保留40的GPR查表、NTA、NT64写与65536工作块 | 构建、静态、默认/强制线性各完整域、一次配对PMU；筛查失败 |
| 48 tilevector | 同布局，通用AVX2直接掩码计算8个地址，再提取lane做GPR查表 | 仅构建；首次像素前经符号运算检查被49替代，未运行静态入口、全域、PMU或墙钟 |
| 49 tilemadd | 同布局，以整数向量加权和计算索引，继续GPR查表与40输出 | 构建、修正后的静态、默认/强制线性各完整域、一次配对PMU；筛查失败 |

新源分别在`experiments/skylake-{tilebmi2,tilevector,tilemadd}-runtime`，对应JSON冻结实际源码SHA。所有表只从原四个稀疏模型及逐级RGB8构造，不读取照片、完整源LUT或gold。三版句柄均28,046,644字节，表仍16MiB；23为11,269,404字节。两种已执行实现的分块表SHA完全相同，强制线性表SHA也完全相同，单独比较索引实现。

每条64字节缓存行保存一个4立方体的64个输入颜色。输入小端码`c=R|(G<<8)|(B<<16)`，47地址为`(pext(c,0xfcfcfc)<<6)|pext(c,0x030303)`；24个基向量映射为24个不同单比特，地址为双射且最高3位不变，即2MiB页分组不变。构造器使用独立位段逆变换，验证器按立方体编号及块内坐标解码全部16M颜色。

47在通用dispatcher中检查`__builtin_cpu_supports("bmi2")`，BMI2只编译进独立TU。无BMI2或构造时`JSHC_CHANNEL_FORCE_LINEAR_INDEX=1`，选择原40线性表及AVX2内核。[Intel支持说明](https://www.intel.com/content/www/us/en/support/articles/000102715/processors/intel-xeon-processors.html)说明Haswell及后续Xeon的BMI2能力，实际部署仍采用CPUID；[GCC文档](https://gcc.gnu.org/onlinedocs/gcc-11.2.0/gcc/x86-Built-in-Functions.html)说明运行时特征检查。强制回退是同库控制流测试，不冒充无BMI2硬件实测。49默认和回退均只需通用AVX2。

48直接掩码式需6个AND、4个移位、5个OR。尚未执行像素时，符号检查找到9个向量操作的等价加权式，因此保留48构建和未执行草案，另建49，不消耗48完整域及计数。49用shuffle/word shift/PMADDWD合并R/G高位，AND/PMADDUBSW/PMADDWD合并低位，再合并B高位。R/G高位输入≤63，系数64/4096，和≤262080；低位两个16位部分和≤15/48，最终≤63，不发生饱和或溢出。这里是整数乘加，没有浮点FMA扩展。符号操作数目不等同机器吞吐。

## 实际环境与精度验收

实际为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库，Release。普通AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`；47的可选TU额外`-mbmi2`，49禁止BMI2。没有native、AVX512、浮点FMA或fast-math。用户已确认SKU未知，按通用AVX2继续；没有实际Skylake、宿主独占、锁频或控温验证。

47和49分别用同一二进制执行默认分块及强制线性，两种模式各独立解码16,777,216颜色，另各执行12组in-place及12组真实输出完整RGB8比较，本阶段共96组完整域API配置，均逐字节一致。每次全域输入262144像素覆盖4个65536块。四次验收各有2208个有限in-place比较、4416个输出/别名比较、736个保护页、1280个64种目标对齐比较和44条新API拒绝检查。单级和四级均覆盖标量1线程及AVX2请求1/4线程。

四级gold SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，单级为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`；沿用固定模型及已有独立oracle流，没有重新拟合。当前固定输出完全不变，所以精度不下降；没有声称相对官方LUT零误差。历史误差为RGB欧氏距离，非CIEDE2000；照片已见。

三次构建的参考23库SHA均为`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。静态核对47/49原三个回退对象与同场参考逐字节相同，线性主内核对象与旧40逐字节相同。49实际有VPMADDWD/VPMADDUBSW，PEXT、PDEP、硬件gather均为0；两套像素内核均无外部调用。目标服务器须重编译，归档Ubuntu/glibc2.43库仅为本机证据。

## 单次计数与停止决定

每版先验要求相对同场40：1线程周期比≤0.88、4线程≤1.05，才能进入完整墙钟评估。只执行一次，每项一次预热、一次计数，共8项画像；画像不包含墙钟提速评分。逐TID用户态cycles/instructions/generic cache四事件，running/enabled均≥0.99。明确固定CPU0/2/4/6、主CPU0、OMP_PLACES与PROC_BIND，核验实际团队、前后TID绑定及实际THP覆盖；没有改变系统设置或安全缓解。

| 同场配对 | 1线程周期/像素 | 4线程周期/像素 | 1线程指令/像素 | 1线程generic miss/像素 |
| --- | --- | --- | --- | --- |
| 40→47 | 3.7042→4.8165 | 3.5004→4.7668 | 5.4010→9.9331 | 0.13448→0.06001 |
| 40→49 | 3.3281→3.5643 | 3.8662→3.9000 | 5.4010→6.4081 | 0.11208→0.03649 |

47的周期比约1.300／1.362；49约1.071／1.009。49减少了索引指令成本，generic miss也显著减少，但同场1线程周期仍高于40，未过冻结筛查，停止本版分块路线。不能从不同画像的绝对周期相除推导47→49速度；也不能把PMU周期比写成完整墙钟吞吐。[Intel优化手册15.16.4](https://cdrdv2-public.intel.com/814198/248966-Optimization-Reference-Manual-V1-049.pdf)提供缓存局部性影响gather取舍的依据，本机结果不代表Skylake实测。

计数数据为100张固定1024×768图，输入235,929,600字节，SHA为`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`；全部画像输出SHA为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，源及哨兵不变。generic cache事件不保证某一级缓存语义；含少量ct/计数启停和OpenMP结束自旋，不等于精确内核延迟，没有专用stall事件证明。

49首次静态检查在像素执行前失败：对全文搜索`pext`误命中150条`vpextr*`，并非发现BMI2。保存[原分析源、对象汇编与失败](../../report/data/skylake-tiles-v1/skylake-tilemadd-static-failure-v1/failure.json)，新`inspect_skylake_tilemadd_fixed.py`按准确助记符检查，static-v2通过后才首次全域与计数；库、模型和测量代码未改。原static-v1未产生通过回执，48相关入口则始终未执行。

## 复现、协作和交付

[独立研究复核](../../report/data/skylake-tiles-v1/research-audit.json)核对冻结源、默认/回退表SHA、96组全域、8项计数和停止决定。[档案核验](../../report/data/skylake-tiles-v1/archive-check.json)通过71份原始文件（4,144,739字节）、9份测量源码ZIP的678项源成员及60项二进制成员；后补README、刷新和静态交付不在原始清单内。原40参考构建及全域复用前阶段同SHA档案；两个50MB域流及235MB照片按计划恢复，模型复用`report/data/skylake-palette-v1/fixed-models.zip`。

在仓库根目录、同SHA输入恢复且输出目录尚不存在时，原冻结流程为：

```sh
python3 scripts/build_skylake_tilemadd.py --plan experiments/skylake-tilemadd-v1.json --output artifacts/skylake-tilemadd-linux-build-v1
python3 scripts/inspect_skylake_tilemadd_fixed.py --plan experiments/skylake-tilemadd-v1.json --build artifacts/skylake-tilemadd-linux-build-v1 --output artifacts/skylake-tilemadd-linux-static-v2
python3 scripts/verify_skylake_tilemadd_linux.py --plan experiments/skylake-tilemadd-v1.json --build artifacts/skylake-tilemadd-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-tilemadd-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/verify_skylake_tilemadd_linux.py --plan experiments/skylake-tilemadd-v1.json --build artifacts/skylake-tilemadd-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-tilemadd-linux-fallback-full-v1 --affinity-cpus 0,2,4,6 --force-linear-index
python3 scripts/profile_skylake_tilemadd_pmu.py --policy experiments/skylake-tilemadd-pmu-v1.json --output artifacts/skylake-tilemadd-pmu-v1
python3 scripts/audit_skylake_tiles.py --output artifacts/skylake-tiles-delivery-v1/research-audit.json
```

现有路径已存在，不能覆盖重跑；新环境应创建新计划/构建/输出并保留新SHA，不修改历史计划绕过绑定。48的构建只说明编译通过，不用它代替像素或性能验证。其他模型全面矩阵、实际Skylake及完整端到端性能未新增验收。

创建前已完整检查44个PR、2个独立issue、2个Discussion、134组REST意见、0审查线程，分页完整；与前阶段已读正文及意见比较无变化，新增#50全文和空评论/reviews均已读，其两项常规CI成功。操作前再刷新，结果见[协作记录](../../report/data/skylake-tiles-v1/pre-create-remote-check.json)。[#7](https://github.com/WyEhNf/flash-chroma/issues/7)/[#9](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)的337a3dd、[#27](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)的876e15b8及[#29](https://github.com/WyEhNf/flash-chroma/pull/29)的397cc367仍是祖先，详细状态见[检查清单](../../report/data/skylake-tiles-v1/remote-check.json)。

整体3倍、实际Skylake、[#8](https://github.com/WyEhNf/flash-chroma/issues/8)的官方派生表许可/内存预算/Threshold及实板、GUI #40独立事项仍未完成，保持Draft，不合并、不关闭事项。下一步可研究原40线性布局的输入加载成本；不继续扫描本版分块参数，不以减小generic miss替代吞吐验收。
