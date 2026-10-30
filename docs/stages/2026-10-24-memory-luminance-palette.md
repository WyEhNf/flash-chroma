# 16题内存独立分支：固定亮度16bank/7bit精确palette普查失败

Agent：`/root/memory`；Operator：当前16题用户；Status：Failed（固定无损格式的色数容量门槛），没有native或性能。工作分支`codex/p16-memory-20261023`，Draft PR由root统一维护；不改默认或旧模型/原件。

## 唯一假设、查重与执行边界

固定`bank=(R+2*G+B)>>6`，输入RGB8先扩到至少16bit，和0..1020自然映射0..15；若每个bank的最终RGB集合都至多128色，则7bit本地ID可无损表示。该机制按输入计算codebook，不对原230色近似。预注册只允许此key、16bank与7bit；任一bank超过128就失败停止，不改系数、分区、阈值、位宽、输入范围或加例外路径。

查重读取旧`skylake-palette-bank-readonly-v1/analyze.py`：它按**输出ID>>4**统计8像素同16色bank以考虑PSHUFB，不是输入亮度选择精确本地palette。旧3bit ID差分、连续4bank局部块字典和现有Ward/maximin全局有损7bit也不等价。在`experiments/scripts/docs/stages`相关源及词检索范围内未发现同等实现；不是全历史或业界首创声明，历史照片统计没有用于选择当前key。冻结[设计原件](../../experiments/luminance-palette-design-v1.md)记录完整范围、门槛与如果通过才考虑的ABI/guard成本。

计划SHA **`c6a236ceaf6511e2940128e90acfb3b6eefcc33811a413a1d599fd90c3c76376`** 在任何ROM读取/统计前冻结。静态freezer只用标准库写源码/设计SHA，随后报告root；root明确授权后执行唯一普查。源为既有M16D16B ROM5918672B，SHA`904f768b…`；不读取gold、照片、其它模型，不生成新的压缩ROM或本地ID表。

## 唯一完整域结果

遍历原R低/G中/B高逻辑ID顺序全部16777216输入，按262144输入分块。从原map/pool取精确globalID并按原palette计最终RGB。原230合法项互异，独立RGB计数与globalID支持数一致。完整逻辑ID SHA **`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`** 保持；另用只含输入key的离散卷积独立核对各bank域大小及总数。

| bank | 输入色数 | 独立最终RGB数 | 7bit门槛 |
|---|---:|---:|---|
| 0 | 23408 | 21 | 可容纳 |
| 1 | 157552 | 69 | 可容纳 |
| 2 | 422768 | 94 | 可容纳 |
| 3 | 819056 | 113 | 可容纳 |
| 4 | 1299600 | **132** | 失败 |
| 5 | 1689744 | **145** | 失败 |
| 6 | 1948816 | **157** | 失败 |
| 7 | 2076816 | **173** | 失败 |
| 8 | 2073744 | **190** | 失败 |
| 9 | 1939600 | **201** | 失败 |
| 10 | 1674384 | **198** | 失败 |
| 11 | 1278096 | **155** | 失败 |
| 12 | 797552 | **134** | 失败 |
| 13 | 407408 | 89 | 可容纳 |
| 14 | 148336 | 38 | 可容纳 |
| 15 | 20336 | 1 | 可容纳 |

bank4..12共9个超过128，最大201。因此该**固定方案不具备7bit无损表示**，无需借照片速度或有损精度来放宽判定。普查完成退出0表示完整统计执行成功，`gate_passed=false`；没有实现/速度资格，100..50档均不新增候选。没有追加其它亮度key、bank数量、8bit变体、例外路径或重复运行。

本次原域联合频数的全局实际命中为**221个互异RGB**，原合法palette仍是230。该数有完整16×230频数支持；不因为实际命中较少就截短原ROM/API的合法230项。对此前“223实际命中”的说法，root另授一次独立只读核对：脚本执行前SHA`5a552f83eef662ff0f535d33c009334b9bd0516ff40059745f9bd26ec352b106`，流式读取原有50331648B完整RGB流并核SHA`3c9ce8d9…`，独立聚合RGB24。

独立结果也是**221色**，与`a020…`逻辑域和230项palette正频数项的**逐色集合及每色完整频数都相等**，有9个合法palette项未命中：ID14、16及223..229。最高命中ID222，所以`maxID+1=223`只是索引前缀长度，不是正频数项数；不能漏掉前缀中的14、16两个空洞。这解释了数值区别，但没有据此声称已审计所有旧223表述的计算来源。RGB原流R高顺序、ID表R低顺序不同，完整256³范围和最终频数一致；这里不是通过混用不同模型解释221/223。故该固定域的223表述须更正为221，保留原错误记录及新证据，不回写旧冻结原件，不把palette槽数、合法项数、unique块数和实际命中色数混为一谈。

## 容量、算术与环境

冻结前说明了完整预定格式：32B头、16×LE16 count的32B、16×128 RGB32 palette的8192B、7bit直表14680064B、末端4B零guard，总ROM **14688324B**。四个pointer/size_t字段不可变借用model预期Windows x64 **32B**，常驻投影 **14688356B**；没有原global palette副本。这些是**不可行候选的布局投影**，未导出文件、编译ABI、验证guard或测RSS，不能算实际内存收益。

即使色数门槛通过，解码仍需`7*code`定位与可变移位、输入亮度加法/移位以及本地palette读取；亮度可与bitstream读取并行计算，但不能据此预称快。原有损7bit数据属于另一模型/解码路径，不挪作本机制吞吐。本次在色数门槛已失败，未执行native完整域、C99/AVX/guard、性能或WASM/实板验证。

普查实际环境Windows11 26200/AMD64、AMD Ryzen9 8945HX，Python3.12.14/NumPy1.26.4；OMP/BLAS/Numba各1线程，没有候选ISA或编译器后端。root授权非性能窗，speed94构建质量与tail静态审计可并行；记录的0.804秒只是Python进程内资源wall，不是mapper吞吐。峰工作集59064320B、峰private提交41140224B，包括Python/NumPy、原ROM和分块数组；不冒充运行时核心RAM、prepare峰值或压缩收益。

独立RGB流核对资源wall0.621秒，峰工作集47321088B、峰private提交32440320B，也包含Python/NumPy；没有以这次读取速度代替任何候选mapper性能。

## 文件、复核与限制

`scripts/profile_luminance_palette_banks.py`只执行一次固定普查，输出完整联合频数、各bank RGB集合和SHA；`freeze_luminance_palette_census.py`只静态冻结源码/设计。复现原命令为`python -X utf8 scripts/profile_luminance_palette_banks.py --output artifacts/p16-luminance-palette-census-v1`，原输出目录存在即拒绝，不再次运行覆盖原证据。

归档在[证据清单](../../report/data/p16-luminance-palette-census-v1/manifest.json)，包含冻结设计/计划/源码、完整联合频数、唯一普查及独立RGB核对原件。[离线审计](../../report/data/p16-luminance-palette-census-v1/git-byte-audit.json)只重算小频数支持与独立输入域公式，并核对暂存原字节，不重读完整ROM或重新分类16M亮度输出。原RGB流额外读取是单独授权的221/223核对，不是对失败亮度key重复筛查；没有改变分区或门槛。

阶段没有可部署产物，不修改内存联合前沿，不宣称一般输入上下文压缩都不可行；结论只限预先固定的16bank/7bit方案。主要提交由本文件Git历史定位，Draft PR仍供审阅，不等于赛事许可或正式目标机成绩。
