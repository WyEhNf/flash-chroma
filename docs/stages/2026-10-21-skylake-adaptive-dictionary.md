# 双表示分派与首次受控长批次失败

Agent：Codex /root；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对修订23吞吐至少三倍；Status：In Progress。**整体目标尚未完成。** 新72完整精度通过，首次性能系列纯映射单/四线程中位耗时比为0.361319/0.511916，均未达1/3；单线程A/A控制也失败。因此完整系列不接受，保留所有样本，按冻结规则跳过确认，不更新默认。

本阶段从Draft [PR #66](https://github.com/WyEhNf/flash-chroma/pull/66)头`50f75249df28f262debde15cf5522449a6712bae`创建`codex/skylake-adaptive-dictionary-20261021`。候选72同时保留65的16MiB线性ID表和70的8MiB块字典：原地分派请求`workers>1`时使用字典，其余原地及真实分离输出使用线性表。线性内核保留57的预排qword输出与65的四ID先行，字典内核沿用70；65536像素连续静态工作块、NTA输入、NT64输出、SFENCE、原23回退均保持。模型、逐级Q16/RGB8舍入及公共默认不变。

字典仅对原四个稀疏模型生成的线性表去重，不读取照片、完整源LUT或gold。262144个64字节块映射到88387个唯一块：1MiB偏移表加5656768字节块池，实际载荷6705344字节，8MiB分配余下1683264字节为零。字典超预算或分配失败保留线性路径；线性失败保留23。新增三个只读dictionary ABI，原direct ABI继续导出线性格式9。字典格式20。四级持久句柄36435276字节，对照23为11269404；单级272883对272835。容量包含两个AlignedTable元数据及两表，不是RSS；临时准备诊断不含哈希节点、桶或分配器元数据。分配失败注入未新增执行。

构建前[冻结72源码及计划](../../experiments/skylake-adaptive-dictionary-v1.json)。实际Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库，Release SIMD使用`-mavx2 -mtune=skylake -ffp-contract=off`；无native、AVX512或fast-math。最终服务器型号未知，按用户确认保留通用AVX2。静态像素对象无外部call、硬件gather、PEXT/PDEP或AVX512。来宾CPU0/2/4/6及OpenMP1/4线程固定，但不保证宿主固定物理核；没有锁频、控温、宿主独占或Skylake实机证据。

独立16,777,216种颜色表/整数oracle、12组原地和12组真实输出完整RGB8配置全部逐字节一致。另通过2208次有限原地、4416次分离/同址、736次保护页、1280次目标对齐、44次API拒绝、原direct与新增dictionary各9次拒绝检查。验证器独立解析全部偏移和块池，核对唯一块、64字节对齐、全部块被引用、尾零及完整逻辑表，和线性表0字节差。逻辑SHA为`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`；字典物理SHA为`4199f19bb887207c2d9d870dce5fabcb7f89fb6e297f90d72b363680b74f177f`。四级完整域输出SHA仍`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。固定模型精度不下降，没有重新拟合；其他模型全面矩阵未新增。

完整域后[冻结长批次策略](../../experiments/skylake-adaptive-dictionary-long-perf-v1.json)：四个串行新进程，角色ABBA，线程顺序1/4、4/1、1/4、4/1。每worker每角色各创建一句柄，每线程先候选同句柄A/A，再直接比较23/72；每批1线程16内轮、4线程64内轮，保留全部数组。先批内均值，再四worker候选/参考比中位。16个A/A批次与32个比较批次共1920内轮，48次预热和48次批末完整100图SHA检查，**非每内轮独立SHA**。实际团队、每TID绑定、源及哨兵不变均核对。两表前后诊断先落盘再断言，16MiB线性和8MiB字典分别要求恰好同容量VMA、2MiB对齐及全部THP覆盖，本次均满足。

| 首次系列接口 | 1线程中位耗时比 | 4线程中位耗时比 |
| --- | ---: | ---: |
| 纯映射apply | 0.361319 | 0.511916 |
| 真实分离输出 | 0.262407 | 0.205963 |
| 旧copy+apply | 0.514353 | 0.784158 |
| 准备+首组真实输出 | 0.723647 | 1.009989 |

纯映射四对分别为单线程0.329964/0.348929/0.421840/0.373709，四线程0.480506/0.564919/0.524128/0.499705。准备+首组包括预热后的首个测量，不是冷启动。未经控制认可的这些比值只作为原始观测，不提升为可靠优化成绩或和旧结果拼接。

| A/A纯apply | 四worker B/A | 中位比 | 事前控制 |
| --- | --- | ---: | --- |
| 1线程 | 0.940246/0.888837/0.871974/0.795283 | 0.880406 | 中位及单对均失败 |
| 4线程 | 0.867539/1.014387/0.992784/1.007523 | 1.000154 | 通过 |

事前控制要求中位位于`[1/1.10,1.10]`，所有对位于`[1/1.25,1.25]`；不事后放宽。三倍门槛仍要求两接口各1/4线程均≤1/3、最差纯映射对≤0.9、准备+首组≤1。当前单线程控制失败且性能门槛失败，不能归因所有差异为算法，也没有证据采用双表分派。[SHA绑定确认决定](../../report/data/skylake-adaptive-dictionary-v1/confirmation-decision.json)明确跳过唯一独立确认，新增确认调用0，不重测择优。

另存一次只读调色板bank分析，未实现或运行新的原生候选。固定100图共9830400个连续8像素包，所有ID高4位相同占37.56655%，其中原本全ID相同16.87949%，新增覆盖20.68706%；仍有62.43345%包须普通回退。因此停止仅针对共同16项bank的PSHUFB提案。该统计不是硬件性能或不可优化证明。Windows CPython/NumPy2.4.6离线分析由实际环境回执标识，输入及直接表SHA校验通过，离线调色板解码100图输出SHA与冻结输出相同。此前双PEXT分块已是47失败实验，不重复实现。

[107份原始文件与独立数组复算](../../report/data/skylake-adaptive-dictionary-v1/README.md)保存构建、源码ZIP、完整域、静态对象、首轮性能和只读分析。基准输入为100张1024×768 RGB8照片，共235929600字节，SHA`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`；批末输出SHA为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。映射计时包含API验证、映射、对齐、尾部、fence和线程工作，不含IO、解码、分配、SHA或准备。数据已见，不声称官方Threshold或端到端实机成绩。

复现需在仓库根目录按冻结SHA恢复模型、照片和独立首级oracle，在独立副本及新输出目录运行；不覆盖既有档案：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-adaptive-dictionary-v1.json --output artifacts/skylake-adaptive-dictionary-linux-build-v1
python3 scripts/verify_skylake_adaptive_dictionary_linux.py --plan experiments/skylake-adaptive-dictionary-v1.json --build artifacts/skylake-adaptive-dictionary-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-adaptive-dictionary-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_adaptive_dictionary_long_linux.py --policy experiments/skylake-adaptive-dictionary-long-perf-v1.json --output artifacts/skylake-adaptive-dictionary-long-perf-v1
```

归档Linux库为Ubuntu/glibc2.43本机证据，目标服务器应重编译。107份清单不含后补README、阶段说明和操作前远端刷新。所有源和已测脚本按原字节提交。

创建前fetch GitHub、读取60个PR正文并比对前阶段59份，仅新增66、旧正文一致；刷新66正文、完整评论、review/行内线程及7/8意见。main和337a3dd、876e15b8、397cc367修复已包含。[协作回执](../../report/data/skylake-adaptive-dictionary-v1/remote-check.json)记录最后刷新范围；Discussion接口仍不能刷新，沿用前序快照，不宣称没有新意见。以Draft交付，不合并或关闭事项。整体三倍目标、目标Skylake速度、官方派生表许可/预算/Threshold继续待验证。
