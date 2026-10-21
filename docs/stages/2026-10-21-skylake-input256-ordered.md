# 分阶段输出与编译器顺序约束

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23至少三倍吞吐；Status：Failed（82静态、83首轮性能）/ Draft，整体目标尚未完成。基于Draft [PR76](https://github.com/WyEhNf/flash-chroma/pull/76)头`e2752a80d981ca6901ded376364176f1ee1e40b5`，本阶段统一保存82静态失败及83独立修复，不执行或重测失败的81/82。

81一次YMM输入减少载荷次数，却因保留八个预排输出而产生真实栈spill。本阶段保持输入整形和四ID，改变64像素主体的输出存活范围：前32像素先形成三段最终32B值，三结果x寄存器空asm确保计算完成，只NT写前64B，第三段pending保留；后32像素全部读取、ID及palette完成后，补写pending与后96B。仍每次推进64像素，六次NT共192B，整个64循环结束后一次SFENCE，原精确24B尾与72/40入口不变。

首两写入只触及完整首64B缓存行；第二组源载荷起点96/120/144/168，不回读已NT写入的首行。不同于先把96B全部写完再读下一组，这避免半行NT之后读取同一行。最大宽读仍200/104B，小于保护窗口216/120B。源码待输出目标为pending+4，实际是否减压以对象为准。历史40/57/59先完成r0..r7才输出，并非本分段组合；输入整形已有34，未称新机制首创。

单线程原地及全部真正分离输出保留79两个pair48 TU；缺BMI1沿原精确linear回退。新多线程路径只需AVX2，按实际workers>1分派，嵌套/非OMP为1，无环境强制。三个旧像素TU及真正分离函数/Handle原字节不变，没有新增表或拟合，资格getter不能作为每次调用执行计数。

82在三结果屏障后直接写首两NT，唯一构建无栈，却被GCC调度成`0x3f4 NT+32 → 0x3f9 load+96 → 0x3ff NT+0`。首两写内部逆序不影响字节覆盖，root初筛额外报了声明顺序过严；独立结果只把“第二组输入早于两NT全部完成”列为冻结调度门槛失败。六输出字节标签及地址正确，未发现静态字节精度错误；仍按预定停止，不加载库或执行像素/性能。82计划SHA`20fedf0f1f0427ab7a9d078f5842fd24fe3943e7b8b8eeedc3846a1593f3009e`，build`9a15636424ac4a59ce2cc3d694387ef504360c14ef78105b667c2b0abee9f601`，库`e92a45af9a42a55c5da54663b2e8c910cccc86ee342b9c43878f87d0131fcc66`，独立结果`961dcc2658d6110d319cc23435935523439db4b3d5c9bcf3d69e69b43e7ae4f5`。

83新建独立源码/计划，仅在首两NT之后增加空memory asm及身份改名。此屏障只约束编译器，不是硬件SFENCE；原三结果/四ID屏障不变。83事前明确首两NT按地址集合{0,32}判断，后四按{64,96,128,160}判断，组内顺序不限，但两NT必须都早于第二组输入，后四必须晚于第二组全部input/ID/palette。没有在82结果上放宽门槛后执行82。

83计划SHA`1078b7b725e790daf2ba017720df6422a45939e0d55f5f1ab0ee0c1bfda757e5`，72项冻结源；新TU`84fe8415273fd458298bac2b6b0ab49dc985aff3f8fa7d1c1367d9315925c7a0`，build`4fd056a3cc7e95db07cb8de05b87036991d48769155277d5edbd26942339c0ff`，候选库`547c1faf97809199b2525137f2ae564c77676344b3525f6839f309271cd8b27f`，参考仍23的`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。实际环境Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu Linux6.18.33.2、GCC15.2、Python3.14.4标准库，Release、AVX2及Skylake调优，仅两个旧pair TU加BMI1，不是真实Skylake。

83主静态结果`189fb18219a6e0c1e6142286c184db6c2c7b4b97146378a629a08119a4ba936f`及独立结果`a7d29c800fa3260d3b7ee2e710c016b55b1026cc6882d511b27a5c06f5925bce`均通过。64/32完整区段281/151条，无栈、无热常量重载，8/4次载荷折叠内存VPERMD；输入及全部六输出RGB标签、实际地址和分组依赖通过，pending全程保留寄存器。三个旧对象.text等79，泛型/新TU无BMI或EVEX，源/构建/ISA隔离通过。

完整正确性结果SHA`26aa6a13f3d72b76a062550a42c9b2884198a828d1a4c6dbdfc79da4fbe6cde0`通过独立16,777,216色表、24组完整RGB8原地/分离、2208finite、4416分离/同址、736guard、旧1280align、44分离拒绝/9直表拒绝及null检查。额外65793像素跨两块，实际aligned64base+offset严格0..63，64次输出/哨兵一致；完整域每批262144像素四块，实际workers4覆盖新路径。只依赖资格getter/块数及冻结分派作覆盖说明，不虚构内核内计数。模型记账reference single272835/chain11269404，candidate single272859/chain28046644不变，不是RSS或官方预算。

未执行81胶水的全字符串版本替换曾把报告常量1280误改1281；82未执行初件也继承，均保留。83性能脚本直接从已验80定点替换身份，实际循环/协议和1280比较+640控制内轮保持；该纠正发生于任何本阶段性能执行之前，不是修改计时数组或门槛。82/83验证胶水派生及修正源均保存。

83完整域后冻结验证身份`56c75d1e63585e71698c66149276175927dd04ae451616af65cac4bb66607079`和首次长批次策略`c980b2e9cb62768edfc6747ddcfee00a76110d8a9c3d4353b5019dda201edc6d`，与80比较所有门槛/ABBA/A/A/16与64内轮/quiet/绑定/THP/唯一条件确认不变。首轮四串行新进程已完整完成，结果SHA`cb806cbf976167f04b87233d00c55f7c9a8ef1f59bdf172e7abc8db6935a598e`；每角色/worker一句柄复用两档线程，共1920内轮、48预热与48次批末SHA，非每内轮独立SHA。批内均值形成worker候选/参考比，再取四比中位：

| 接口 | 1线程耗时比 / 吞吐 | 4线程耗时比 / 吞吐 |
| --- | ---: | ---: |
| 纯apply | 0.333838 / **2.995468倍** | 0.477574 / **2.093918倍** |
| 真正分离输出 | 0.299521 / 3.338669倍 | 0.263971 / 3.788295倍 |
| 旧copy+apply | 0.448274 / 2.230781倍 | 0.720269 / 1.388370倍 |
| 准备+首组分离输出 | 0.638039 | 0.829819 |

纯apply单进程比1t`[0.337072,0.342422,0.330604,0.321178]`，4t`[0.457658,0.510384,0.484312,0.470836]`；A/A中位0.968368/0.992533，全部单对落在原0.8—1.25门槛，控制有效。输出、源与哨兵、实际团队/TID绑定及前后精确16MiB VMA/全THP通过。两档纯apply均未到三倍，1t不可把2.995468舍入成达标；准备项只要求原中位，4t某进程1.060300仍完整披露，不改统计口径。按冻结规则跳过确认，新增系列/原生调用0，未默认采用。没有同场直接比较79/80/83，不能跨场归因输入重排的独立效果。

补充唯一R连续8色/3bit只读分析完整逆映射/重建零差，但例外324748块、最大ID跨度26；照片例外8包0.2350073超事前0.05，64像素主词平均49.307863对原49.415259比0.99782667超事前0.80，含例外池1.10909797。停止、不构建原生、不扫描参数。结果SHA`b73099cb170363ee50a266714363f4b74cecf1c86a3f4472dfb0cf87f05e0dc1`，独立汇总审计`3bbce656706bd84a6cfa23444e67b3840cf4ccd8f4ff0e731da2315214f4eeb9`；后者未重读大cube/photos，采用冻结脚本及既有证据交叉核对大输入，限制保留。Windows11/Anaconda Python3.13.12、NumPy2.4.6；行集合不是硬件miss或吞吐。使用已验输出只作离线可行性，未来运行时仍禁止读照片或gold构造。23/42为B连续3bit，62为R连续5bit，没有夸称完整组合未被实现。

另一条安全word gather主ID表加标量palette组合只审阅历史，未实现：27/34已采用安全`gather(code>>2,4)`、变量移位及255掩码读取16MiB表，34已有单YMM输入，后续为palette gather。没有当前四ID/输出的完整组合实测，但该替换不减少8个ID地址、行或页集合，还引入公共gather/移位依赖与向量压力，证据不足以投入新候选。[Intel官方GDS说明](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/gather-data-sampling.html)明确受影响CPU的缓解增加gather结果消费延迟；本机不是该平台，未修改微码、缓解或系统设置，也不推测实际Skylake影响数字。

[166份原件及原始批内数组复算](../../report/data/skylake-input256-ordered-v1/README.md)完整保留，1920轮复算一致。82源码/构建/两份静态失败、83冻结源/构建/两份静态通过/完整域/全部长批次，以及只读R8分析和独立审计均归档；无失败样本替换。两套各72项源、202份暂存冻结blob与工作区逐字节一致，语法与空白检查通过；交付结果自身排除自引用。归档/交付解释器Windows11/Anaconda Python3.13.12标准库。

复现按前序说明恢复固定输入、大流、模型及脚本支持并核对SHA，使用新目录，不覆盖原失败证据：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-input256-ordered-v1.json --output artifacts/skylake-input256-ordered-linux-build-v1
python3 -P artifacts/skylake-input256-ordered-static-v1/check.py
python3 scripts/verify_skylake_input256_ordered_linux.py --plan experiments/skylake-input256-ordered-v1.json --build artifacts/skylake-input256-ordered-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-input256-ordered-linux-full-v1 --affinity-cpus 0,2,4,6
python3 artifacts/prepare_input256_ordered_perf.py
python3 scripts/bench_skylake_input256_ordered_long_linux.py --policy experiments/skylake-input256-ordered-long-perf-v1.json --output artifacts/skylake-input256-ordered-long-perf-v1
```

操作前fetch GitHub，读取70份完整PR正文与前69份比较仅新增76，其余相同；76完整正文/评论/review/行内为空，updated issue无新增。main b19c5a0及337a3dd/876e15b8/397cc367均包含，issue7修复保留，issue8正式接口/预算/实板继续跟踪。Discussion接口不能读取，保留缺口，不合并或关闭事项。整体三倍目标仍未完成，未锁频控温或证明宿主独占；真实Skylake、缺BMI硬件、官方许可/预算/Threshold仍未验证。
