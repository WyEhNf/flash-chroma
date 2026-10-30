# 局部RGB差分与异或地址布局的失败筛查

Agent：Codex /root、/root/base_delta_delivery；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对修订23至少三倍吞吐；Status：Failed（编码资源门槛）/ 独立证据核对通过 / 待根代理提交Draft PR。基于[PR77](https://github.com/WyEhNf/flash-chroma/pull/77)头`c3efa63a48cd29db36e3b0bc23580bb545996eeb`，工作分支`codex/skylake-base-delta-profile-20261021`。本阶段归档2026-10-21已有压缩失败，并新增一次异或布局只读筛查；运行时源码及默认候选不变。实际提交以本阶段Draft PR头为准。

## 目标与固定方案

既有16MiB逐色ID表还需依赖palette读取RGB，拟研究能否保留相同主表大小，以局部RGB基值和短差分直接恢复输出。分析对象为固定模型的已验完整输出，不是重新拟合；未来任何候选建表仍须直接使用原模型，不能依赖gold、照片或预期输出。

输入地址固定为`code=R|(G<<8)|(B<<16)`，每8个连续R为一块，`q=code>>3`、`k=code&7`。块内取`baseR=min(R)`、`baseDG=min(G-R)`、`baseDB=min(B-R)`，合成`baseRGB=(baseR,baseR+baseDG,baseR+baseDB)`。正常块要求合成基值三个通道均在0..255且不是ffffff，八个像素的差分分别满足`dR<=3`、`dDG<=3`、`dDB<=1`，差分均非负。

每块一个64bit词，低24bit存合成RGB基值，高40bit存八个`dR|(dDG<<2)|(dDB<<4)`；固定2+2+1bit，不截断或近似。正常恢复为`baseRGB24+(d&3)*0x010101+((d&12)<<6)+((d&16)<<12)`。不满足条件的块用低24bit ffffff作标记，高40bit保存连续池序号，池中逐块保留八个精确little-endian RGB32，共32B。全白基值也须走例外。

主表仍为16,777,216B，`((code>>3)*8)>>6 == code>>6`，与原byte ID表逐色主表行编号完全相同。这只尝试消除正常路径的palette依赖，不减少行集合，也不能从离线统计推断吞吐。移位、乘加、异常检查、寄存器压力均未通过原生实现验证。

冻结协议SHA`4a6dd2693d75ce092c509400d164c63c409099eb54da55c54550c6354aca1192`；分析脚本SHA`c88f0113f4c1d6e68b4185cdb55f2140f04aa5ecacaf8e2aa390dc45269516ef`；冻结脚本SHA`0f9d1f0d5c07e7aa15085ee436e93d537a32bd787e17a2d415a1ed2e85dba871`。协议于2026-10-21 15:00:01 UTC冻结；同目录唯一执行回执为15:00:32至15:00:48 UTC。采用文件`x`模式禁止覆盖，失败停止，不扫描位数、块尺寸、通道顺序或偏移，不重试择优。

## 原始结果与事前门槛

结果SHA`31dcb62f0ca647b64554206e46ed761bcbb10e0b83475159af3681ab266d4783`；退出回执SHA`89909f3a06ace5fc4e83af330460e73cdfe7232bc1fa07f886c70561f49ec946`。进程退出0仅表示分析完整结束，`gate_passed=false`，不是方案通过。

| 项目 | 事前要求 | 原始结果 | 判定 |
| --- | --- | --- | --- |
| 全部RGB8重建 | 全部16,777,216色零差，输出SHA、逆映射、行编号、正常通道无进位 | 全部零差、SHA一致 | 通过 |
| 100图重建 | 逐图像素/字节零差，合并输出SHA一致 | 全部零差、SHA一致 | 通过 |
| 总异常8像素包率 | ≤5% | 5,255,224 / 9,830,400 = **53.458903%** | 失败 |
| 任一图异常8像素包率 | ≤20% | 最差索引31 div2k-0814：**97.978719%**；96图超限 | 失败 |
| 异常池 | ≤2,097,152B | **30,245,024B** | 失败 |

完整域2,097,152块中正常1,151,995块、例外945,157块；主表加池共47,022,240B。例外原因可重叠：`dR>3`有931,518块，`dDB>1`有242,230块，合成baseG越界10,108块、baseB越界2,535块；baseR越界、全白基值及`dDG>3`均为0，不能直接相加当作例外总数。原结果同时保留128项原因位图和7×7交集。

原始完整域重建按R=0..255遍历，每片完整G/B笛卡尔积；`cube[R,G,B]`被转换为实际地址`[B,G,R]`。源通道转int32再计算有符号DG/DB，打包采用uint64。正常恢复检查每个通道的真实基值加增量是否超过255后，才依据输出字节检查；并非掩码后自证无进位。100图均为1024×768 RGB8，异常包固定从各图像素0起不重叠8像素；不扫描对齐偏移。照片例外像素率为34.044306%，与53.458903%的异常包率含义不同。

完整输出SHA等于cube SHA，照片合并输出SHA为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。本次只核对冻结原精度结果与算法覆盖，未第二次编码/解码色域或照片。失败方案没有候选原生、编译、性能或确认系列调用；不能报告任何新增加速倍数。

## 输入身份与环境

| 输入 | 字节 | SHA256 |
| --- | ---: | --- |
| `artifacts/cinema-current-anchor-accept-v1/cube.rgb` | 50,331,648 | `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22` |
| `artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb` | 235,929,600 | `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd` |
| `assets/photos/manifest.json` | 101,681 | `10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c` |
| `artifacts/skylake-matrix-cache-gold-v1/cache-gold.u32` | 742,400 | `f223e56756ed281372b0ebd858b254110c04ca1f5b2afb6d091c40df3a1ffe90` |
| `artifacts/skylake-palette-bank-readonly-v1/palette.u32` | 1,024 | `53cedaeca7403d5afd1b96133339be866840059685abdd3846aad7fe10998fbe` |
| `artifacts/skylake-matrix-cache-gold-v1/generation.json` | 2,058 | `c2afd9e81688e8609b52a4862917e0315b05692a0783a512e1bc73d4fd16be95` |

cache-gold只核对原始230色集合、palette填充及cube使用其中221色；本方案直接编码RGB，不对221色重新编号。历史范围记录SHA`5ff8da38c49e8d4ec208177f901c1f8bbb5b3f68cf344ae27f56675762f78a72`列出十项小源码/阶段文件并核对其身份：24/28/29为全局逐色16bit差分的不同加载，26为64MiB RGB32直表，62仍是局部palette ID差分。该范围未发现直接等同方案，不声称全部历史或业界不存在同类方法。

原始分析实际环境为Windows11 10.0.26200、AMD64 Family25 Model97 Stepping2、Anaconda Python3.13.12、NumPy2.4.6、小端；无需编译器，不启用候选AVX2或设备后端，不存在原生线程性能比较。当前独立审计为相同Windows/Python环境的标准库。没有真实Skylake执行；离线失败不支持跨CPU性能结论。

## 独立审计与归档

[八份原件及清单](../../report/data/skylake-r8-base-delta-profile-v1/README.md)逐字节保留分析/冻结脚本、历史范围、协议、准备回执、启动回执、结果和退出回执。`manifest.json`不包含后补文档或审计自身；清单中的八份SHA同时与原artifacts文件比较，未改动原件。

`independent-audit.py`不导入或执行原始脚本，仅AST解析并审阅固定格式、映射与覆盖范围，独立重哈希六项输入（含大cube/photos）、上一R8结果及十项历史来源；另外逐片核对100图输入与manifest/逐图结果SHA。它从原因位图重新求7项原因及7×7交集，核对三组511项跨度直方图总数和阈值尾部，复算100图异常像素/8包直方图、加权总数、最差图、96张超限列表及完整gate。独立审计通过，结果SHA`6d494b5d1cc03d472d93ffbbe5dd5bf62e29d133584a85f00afe90385d3955ae`，方案gate仍失败。

范围限制：没有从原cube独立重算全域跨度或重建主表/池，也没有从照片重算异常直方图或输出。原profile的主表、线性RGB32和异常池只存在于当时内存，八份原件中仅保留其SHA及大小；不把这些SHA当作已经归档的二进制。单目录独占回执不能证明其他未记录路径没有执行。当前核对证明身份与汇总自洽，不构成第二次完整精度执行或性能验证。

历史执行命令为`python artifacts/skylake-r8-base-delta-profile-v1/analyze.py`，只在原回执记录的2026-10-21执行；此阶段未调用，失败目录不得重跑。仅复现当前审计需先恢复协议所指输入与清单所指原artifacts文件，并选择新的输出路径：

```powershell
python report/data/skylake-r8-base-delta-profile-v1/independent-audit.py --repository . --output artifacts/skylake-r8-base-delta-audit-reproduction.json
```

## 7bit拆平面设想的资源下界

另一个尚未实现的设想把主词低8bit存baseR，高56bit存八个3+2+2bit差分，再用2MiB独立元数据平面存baseDG4/baseDB3及例外标志。目标仍为去掉palette依赖，但先只读取已有三组跨度直方图，不执行新profile、参数扫描或原生实现。

已有数据中R跨度>7的块475,327，DG跨度>3为0，DB跨度>3为31,783。任意实现都至少有475,327块不能被这些固定位数容纳，因此32B例外块的池至少**15,210,464B**，已经超过2MiB门槛。仅这三个差分原因的并集介于475,327和507,110块；无联合直方图不能确定交集，也不能把差分并集上界当作完整格式的精确异常池。固定18MiB平面加池下界为34,084,832B，已大于32MiB。

据此停止该设想，未创建运行时、冻结新的大分析协议或做照片异常率统计；不是在5bit失败结果上改位数重试。这里没有收益预测或新增性能成绩。

## 新增一次相邻通道异或布局筛查

固定`h=(code xor (code<<8))&0xffffff`，即`R,G xor R,B xor G`，逆为`(h xor (h<<8) xor (h<<16))&0xffffff`。它区别于41的`code xor code>>10`和60/61/66/67的模减，不声称新算法首创。未来向量输入若展开成[R,G,B,B]，一次dword左移8及xor即可生成最高字节0的索引；仍增加输入整形和寄存器成本，没有实现候选。

首次统计前协议SHA`0e577bf06e4c4205ff222f2c7a50a4e72b36c9b00cd1d046fe3c8b1859d5f180`，脚本`61c79f9a4cdaae8dd0fb7cf00c0b893d0e1fa982c23ee07aa9b0180e748bf114`；唯一执行有开始、stdout/stderr及退出回执。预定平均行比≤0.80、任一图≤1.05，失败停止，不扫其他移位/轴/变种。

Windows11 / Anaconda Python3.13.12 / NumPy2.4.6，固定100图与此前R/B profile同SHA；从每图像素0取连续64像素，共1,228,800窗。原R低总行60,721,470及完整65桶直方图与历史完全一致。新布局总行63,595,400、平均51.754069，对原49.415259比**1.047329717**；最差图**1.323871689**，两门槛均失败，停止原生实现。全16M索引正逆/范围零差，100图输入SHA通过；页编号改变。此项只证明索引可逆和行集合，不是像素映射、硬件miss或吞吐。

[九份原件、SHA及复算](../../report/data/skylake-xor-chroma-profile-v1/README.md)保留。归档复算检查100行加权总数、两个65桶直方图、逐图比例、最大值、原门槛及脚本/协议/输入/日志身份；未重算大行集合。编译、候选像素及性能调用均0，没有新增提速成绩。

## 远端检查与交付

操作前fetch GitHub，main仍b19c5a0且为祖先，337a3dd/876e15b8/397cc367修复均实际包含；没有改动相关公共实现，历史验证沿PR37。读取72份完整PR正文，与上阶段70份逐字比较结果见remote-snapshot.json；新增77/78，旧正文没有变化。77及新78正文、全部comment/review/行内为空；78的Numba固定四级专门化亦未通过性能采用，不跨环境归并成绩。issue7/8完整正文与评论刷新，7绑定修复保留，8正式接口/预算/实板继续跟踪。当前连接器无Discussion读取接口，保留缺口，不把无法读取当作无意见，不合并或关闭事项。

本阶段以中文工作分支/commit/Draft PR交付，仅报告两个只读失败与证据核对。既有整体单/四线程三倍验收、实际Skylake、官方派生表许可/预算/Threshold仍未完成，不默认采用或宣称可合并。
