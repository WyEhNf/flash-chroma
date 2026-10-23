# 16题内存独立分支：512个三维输入bank的6bit精确palette失败

Agent：`/root/memory`；Operator：当前16题用户；Status：Failed（固定6bit色数容量门槛）。工作分支`codex/p16-memory-20261023`，Draft PR由root统一维护。不改旧亮度16bank/7bit、tag/字典失败或默认，没有native/性能。

## 固定协议与实现范围

预先固定输入`bank=(R>>5)|((G>>5)<<3)|((B>>5)<<6)`，RGB各高3位组成512个32×32×32输入域，每域32768色；所有512域的最终RGB集合都须<=64，才可6bit无损编号。任一超过64就停止，不能改key、bank数、bit数、局部分区、异常池或输入范围。它是精确逐色ID表示，不是把RGB采样到8³近似滤镜。

已读历史原palette/3bit差分、有损7bit、连续4bank、输入2³砖的RGB差分与84混合、4³缓存行布局；它们不等价于512个32³域各64项输入codebook。检索范围及整数/有限合同见[冻结设计](../../experiments/rgb3d-palette-design-v1.md)，不声称全历史/业界首创，不使用历史照片统计选参数。

94正式性能窗内只写静态文件；root明确释放后，先执行标准库freezer，绑定设计及脚本原字节，计划SHA **`17a12d05ee40bb18604055f533101076771761dfb4502953a74e90c0aa0fbf10`**，再运行唯一完整域普查。未预先查看本次bank色数，也未基于结果改门槛。

唯一数据为a399原M16D16B ROM5918672B，SHA`904f768b…`，原230项合法palette保持。按原R低/G中/B高逻辑码从map/pool解完整ID，分262144输入chunk，完整ID SHA **`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`**。不读照片/gold或新精度模型，不导出本地ID/新ROM、不构建候选或测速度。

## 实际完整域结果：54个bank失败

8000个轴边界笛卡尔积及2个越界拒绝，共8002有限索引合同通过；完整域逐项核对分通道公式与code位段公式相同，全部512个bank各32768输入。原230合法RGB互异，正频数实际221色，不将最高ID+1的223当作独立色数；这个范围已在上一阶段由3c9c RGB流逐色频数核对。

| 项目 | 原始结果 | 判定 |
|---|---:|---|
| 完整输入覆盖 | 16777216，每bank32768 | 通过 |
| 独立bank色数最小/平均/最大 | 1 / 38.234375 / **95** | 平均不替代最坏门槛 |
| 超过64的bank | **54 / 512** | 固定6bit失败 |
| 最大bank | **153**，R/G/B高3位=1/3/2 | 95>64 |
| 新ROM/ABI/guard/native/性能 | **0次** | 按门槛停止 |

完整失败bank如下，另外全部512行RGB集合与512×230联合频数原件封存：

`73,74,75,76,77,78,79,81,82,89,90,98,99,106,107,108,114,115,122,123,129,137,145,153,154,161,162,163,169,170,201,202,209,217,225,226,233,234,241,249,265,266,273,281,289,297,305,313,330,337,345,353,401,465`。

退出0只说明单次普查完整结束，`gate_passed=false`。没有删除失败bank，不能只用458个可容纳bank或平均38.23色声称本方案可行。固定6bit机制停止，不产生100..50精度/速度新候选；质量100%存在性的条件本身未成立，不借旧有损7bit速度放宽。

## 容量、有限合同与资源口径

冻结前推导的完整`C6BK`布局为header32B、512项LE16 counts1024B、6bit直表12582912B、零guard4B、512×64 RGB32 palette131072B，ROM **12715044B**；四字段借用model预期Windows x64 **32B**，常驻投影 **12715076B**。这是不可行布局投影，未实际导出、sizeof、验末端或测RSS，不能算内存收益。

bank索引直接由输入计算，但仍有6×code定位、0/2/4/6四种byte内移位及本地palette依赖，128KiB palette不保证缓存命中。设计明确table后有4B自有guard，末palette词结束于ROM边界；如以后另立实现，真实ABI、local63、所有bank、31/32等边界、count1/64/非法、源/目标/ROM保护及8组C99/scalar/AVX完整域需另验。当前只有普查索引合同，不能冒充运行时格式或移植验证。

实际环境Windows11 26200/AMD64、Ryzen9 8945HX、Python3.12.14/NumPy1.26.4，OMP/BLAS/Numba各1线程。root授权非性能窗，与root289/tailbox质量可并行。普查内部资源wall1.043秒，不是mapper吞吐；峰工作集71622656B、峰private提交52793344B，包括Python/NumPy、原ROM、分块、频数和JSON临时，不是核心RAM或prepare专属峰值。未执行候选编译器/ISA、WASM或实板。

## 归档、复核与交付

[精简清单](../../report/data/p16-rgb3d-palette-census-v1/manifest.json)保留原始run、结果摘要、`census-raw.zip`三原件及`frozen-source.zip`原字节；ZIP只用于传输，不按其大小计RAM。[离线审计](../../report/data/p16-rgb3d-palette-census-v1/git-byte-audit.json)从512×230频数重算每bank实际RGB集合、54失败、最大95、全域数、全局221和静态容量，并核全部暂存SHA/CRC，没有重新扫描完整ROM或重复census。

主要文件为`scripts/profile_rgb3d_palette_banks.py`、`freeze_rgb3d_palette_census.py`、`archive_rgb3d_palette_census.py`、`audit_rgb3d_palette_census.py`。实际命令为`python -X utf8 scripts/profile_rgb3d_palette_banks.py --output artifacts/p16-rgb3d-palette-census-v1`；原目录存在即拒绝，不覆盖原件或追加择优普查。提交可由本文件Git历史定位，root统一更新Draft PR。

当前只否定本固定512bank/6bit方案，不证明其它精确上下文编码不可能。若未来基于已封存频数另立不同位宽，必须是独立协议/格式/质量与性能，不重写这54项失败，不将未实现投影写成成绩。
