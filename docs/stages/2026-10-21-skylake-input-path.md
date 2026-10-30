# 线性输入读取与小调色板gather研究

**整体300%吞吐目标仍未完成。** 本阶段50—52三个候选精度全部不变，但均未通过预先冻结的增量周期筛查，没有新增整轮墙钟分数。最新完整墙钟仍为[#50](https://github.com/WyEhNf/flash-chroma/pull/50)中的40：独立配置协议纯映射1/4线程2.6444倍／3.1200倍，真实输出3.3066倍／4.3069倍；单线程纯映射未过3倍。没有用历史通过点或单项指标宣布完成。

工作分支`codex/skylake-vector-input-20261021`依赖[#51](https://github.com/WyEhNf/flash-chroma/pull/51)及`ee529bedec7537da5843080c2f1f07bab4e8e7d6`，真实阶段提交见[交付元数据](../../report/data/skylake-input-path-v1/delivery-metadata.json)。原23、模型、公共默认及只读AGENTS.md未改。

## 三项独立变量

| 修订 | 相对来源与改动 | 结果 |
| --- | --- | --- |
| 50 vectorinput | 从40出发，每8个RGB24以16+8字节精确读取、align/shuffle形成8个索引，再提取lane做GPR查表 | 指令减少约0.25/像素，本次1线程周期只改善约2.2%，未过5%筛查 |
| 51 vectorwide | 从50出发，仅宽循环改为读取[0,16)与[12,28)，减少一次align；尾部仍精确24字节 | 指令进一步减少，本次1线程周期约持平，4线程增加约8%，停止 |
| 52 palettegather | 独立从40出发，大16MiB表仍GPR读取，仅对1024字节调色板执行AVX2 gather | 指令和周期均增加，停止 |

源分别在`experiments/skylake-{vectorinput,vectorwide,palettegather}-runtime`，计划`experiments/skylake-*-v1.json`冻结实际源码SHA。三版16MiB u8 ID表、230项有效调色板、NTA、NT64输出、65536工作块均保留；句柄28,046,644字节，参考23为11,269,404字节。三版完整表SHA与旧40相同，表只从四个稀疏模型及逐级RGB8生成，不读取照片、完整源LUT或gold。

51宽读取的跨度为28字节，最后4字节不参与索引，两个16字节操作数有4字节重叠。它只在原有`p+72<=pixels`的64像素循环和`p+40<=pixels`的32像素循环使用，额外4字节仍在当前线程块内；8像素尾部保持精确24字节读取，不跨线程块读取。完整保护页/边界检查另行确认实际机器代码的访问。

52没有叠加50/51或前阶段颜色分块。旧40实汇编已把调色板读取写成`vpinsrd`内存操作数；52先装配ID向量，再执行gather及掩码初始化，源码层少几个显式load不保证机器指令减少。[离线汇编描述](../../report/data/skylake-input-path-v1/skylake-palettegather-lowering-v1/results.json)保留原40和52的SHA及样例，只描述ISA表达，不声称已测得微操作融合、端口或专用延迟事件。[Intel GDS说明](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/gather-data-sampling.html)提示缓解可能影响gather延迟，本任务未调整安全设置，本机AMD结果不能推定Skylake同幅表现。

## 环境与精度

实际为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu、Linux6.18.33.2、GCC15.2、Python3.14.4标准库，Release。独立AVX2 TU使用`-mavx2 -mtune=skylake -ffp-contract=off`，无BMI2要求、native、AVX512、浮点FMA或fast-math。没有实际Skylake、锁频控温或宿主独占验证。CPU0/2/4/6及L3/NUMA拓扑来自来宾，来宾绑定不保证宿主物理核调度固定。

每版独立解码16,777,216种颜色，另有12组in-place＋12组真实输出完整RGB8比较，本阶段共72组完整域API配置逐字节一致。每版2208个有限in-place比较、4416个输出/别名比较、736个保护页、1280个64种目标对齐比较和44条新API拒绝检查通过。每次全域输入262144像素覆盖4个工作块，单级/四级均覆盖标量1线程与AVX2请求1/4线程。

四级gold SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，单级为`7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`。所有构建参考23库SHA为`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。当前固定输出完全相同，所以精度不下降；没有重新拟合，没有声称相对官方LUT零误差。历史误差口径为RGB欧氏距离，非CIEDE2000，照片已见。

静态核对原三个回退对象与参考同字节，像素内核无外部调用。50/51无硬件gather；52共26处静态palette gather。静态总指令数分别1552/1505/1800，动态指令数和性能仍须分别测量。原始源、库、编译命令和汇编均归档；Ubuntu/glibc2.43库仅作本机证据，目标服务器须重编译。

## 预定筛查与全部负结果

本阶段研究增量输入/第二层加载收益，事前要求相对同场40：1线程周期比≤0.95、4线程≤1.05，才考虑整轮墙钟评估。这个5%筛查与前阶段复杂分块的12%筛查目的不同，均在首次各自计数前冻结；**整体3倍墙钟验收没有改变**。每项一次预热、一次计数，各版1/4线程两角色共4项，总12项。没有重复画像或整轮择优。

| 同场配对 | 1线程周期/像素 | 4线程周期/像素 | 1线程指令/像素 |
| --- | --- | --- | --- |
| 40→50 | 3.7250→3.6441 | 3.7510→3.8885 | 5.4010→5.1505 |
| 40→51 | 3.1854→3.1884 | 3.6352→3.9345 | 5.4010→4.9007 |
| 40→52 | 3.1989→4.2800 | 3.5556→5.1652 | 5.4010→6.2599 |

三版都未过1线程筛查，51/52也未过4线程筛查，均保存`screen-decision.json`并跳过整轮性能。参考周期在不同画像中变化明显，不能跨行相除推导50→51或其他墙钟提速。指令减少不构成性能通过。

逐TID用户态cycles/instructions/generic cache四事件running/enabled均≥0.99，实际团队、前后TID单CPU集合及THP覆盖通过。显式OMP_PLACES与PROC_BIND，主线程CPU0。计数包含少量ct/启停及OpenMP结束自旋，不等于精确内核延迟，generic cache不标作L3或Skylake事件。没有停用服务、修改perf权限、安全缓解或系统大页策略。

数据为100张固定1024×768 RGB8图，共235,929,600字节，输入SHA为`e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，全部画像输出为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，源及哨兵不变。没有新增文件IO、解码、分配、冷启动或真实服务器端到端成绩。

51执行前的准备程序曾因Windows反斜线路径键而KeyError，未启动构建或像素，保留[失败记录](../../report/data/skylake-input-path-v1/skylake-vectorwide-preflight-v1/failure.json)。50已冻结验证计划保持原字节，离线审计规范化路径后核对同一SHA；51新计划统一正斜线，然后才首次构建和数值执行。没有修改50测试源或重新计数。

## 档案、复现和协作

[研究复核](../../report/data/skylake-input-path-v1/research-audit.json)核对冻结源、同一物理表、72组全域、12项单次画像及停止决定。[档案核验](../../report/data/skylake-input-path-v1/archive-check.json)通过72份原始文件（3,803,717字节）、9份测量源码ZIP的678项源成员及57项二进制成员。后补README、静态与操作前刷新不在原始清单内。40参考构建/全域复用既有同SHA档案；大流按冻结计划恢复，模型复用`report/data/skylake-palette-v1/fixed-models.zip`。

交付静态检查曾拒绝PR51原文中的合法Markdown双空格换行，随后提交命令没有在失败后停止；该实现提交当时尚未推送。[失败及顺序记录](../../report/data/skylake-input-path-v1/static-preflight-first-failure.json)与原检查源保留。只为该原文档案设置行尾空格属性，保持原文和测量字节；最终改为相对阶段base核对全部Git blob，全部检查通过后才推送发布，没有重跑数值测试。

仓库根目录的原冻结流程示例（先恢复同SHA输入，输出必须尚不存在）：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-palettegather-v1.json --output artifacts/skylake-palettegather-linux-build-v1
python3 scripts/inspect_skylake_palettegather.py --plan experiments/skylake-palettegather-v1.json --build artifacts/skylake-palettegather-linux-build-v1 --output artifacts/skylake-palettegather-linux-static-v1
python3 scripts/verify_skylake_palettegather_linux.py --plan experiments/skylake-palettegather-v1.json --build artifacts/skylake-palettegather-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-palettegather-linux-full-v1 --affinity-cpus 0,2,4,6
python3 scripts/profile_skylake_palettegather_pmu.py --policy experiments/skylake-palettegather-pmu-v1.json --output artifacts/skylake-palettegather-pmu-v1
python3 scripts/audit_skylake_input_path.py --output artifacts/skylake-input-path-delivery-v1/research-audit.json
```

现有目录不能覆盖重跑；新环境创建新计划/构建/输出并保留新SHA，不修改历史计划绕过绑定。其他模型全面矩阵、实际Skylake与官方端到端验收未新增验证。

创建前完整检查45个PR、2个独立issue、2个Discussion、137组REST意见、0审查线程，分页完整；与前阶段已读全文/意见比较无变化，新增#51正文与本地原发送文本逐字核对，两项常规CI成功。操作前刷新见[协作记录](../../report/data/skylake-input-path-v1/pre-create-remote-check.json)。[#7](https://github.com/WyEhNf/flash-chroma/issues/7)/[#9](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)的337a3dd、[#27](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)的876e15b8及[#29](https://github.com/WyEhNf/flash-chroma/pull/29)的397cc367均已包含，详细链接和状态见[检查记录](../../report/data/skylake-input-path-v1/remote-check.json)。

整体3倍、实际Skylake、[#8](https://github.com/WyEhNf/flash-chroma/issues/8)的官方派生表许可/预算/Threshold及实板、GUI #40独立事项仍待处理，保持Draft，不合并、不关闭。停止本版输入加载和小调色板gather；下一步可研究直接RGB32表与缓存行布局能否同时抵消大表未命中和索引成本，目前没有该组合的执行或成绩。
