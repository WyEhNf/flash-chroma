# 输入亮度选择精确7bit本地palette：唯一普查前设计

Agent：`/root/memory`；Operator：当前16题用户；Status：Proposed，仅静态设计。当前只冻结计划/源码，不执行普查、导出、构建或性能。固定a399四级模型及其已验原M16D16B ROM，不更改拟合输出或默认行为。root明确授数值窗后只执行一次完整域普查。

## 唯一假设与门槛

固定`bank=(R+2*G+B)>>6`，R/G/B为输入RGB8原始无符号码；加法必须先扩到至少16bit，最大1020，bank自然0..15。只允许16个bank和7bit本地ID，不扫描其它亮度系数、阈值、分区、位宽、输出排序或例外路径。每个bank使用其全部输入对应的最终RGB集合；若各bank都至多128个RGB，就存在精确本地编号，精度可逐字节保持100%。如果任一个bank超过128，方案失败并停止，不缩窄输入/改位数重试。

这不是先把230色量化到128色，而是根据已知输入计算16路上下文；同一个RGB可在多个bank占槽，所有palette副本须计入容量。bank只由输入得出，可与bitstream取数并行计算，仍增加算术、7bit定位/可变移位及更大的palette工作集；减少map/pool层数不保证速度，M16T已有强负例。

## 查重范围与区别

读取旧`artifacts/skylake-palette-bank-readonly-v1/analyze.py`：其bank为**输出globalID>>4**，统计8像素是否同16色组来考虑条件PSHUFB；不是从输入计算本地codebook。已读原palette生成、3bit加例外池、当前有损7bit `profile_palette_bitpack.py`/`memory_bitpack.c`、连续4bank字典和近期tag实现。原3bit保存块内ID差值；有损7bit通过Ward/maximin缩减全局颜色；连续4bank压块ID并保留global palette；它们都不同于本次输入亮度精确7bit。

在`experiments/scripts/docs/stages`以input-cued/codebook/luminance/brightness/亮度bank/局部调色/bank与palette等词检索并查相关源，未发现等价实现；不能据此断言全部历史或学界业界不存在。读取历史分析只用于辨别机制，不使用其照片统计选择当前key；本次输入仅原精确ROM，不读照片/gold。

## 唯一普查与可复算证据

源为`artifacts/p16-memory-rom-v2/rom-4.bin`，5918672B，SHA`904f768b4729e1a71c8b03ddaa953b4ad183baee65498b6741068cbbc218ab22`；从原map/pool解出每个精确globalID，再按原palette得到RGB。遍历顺序为`code=R|(G<<8)|(B<<16)`，262144输入为一chunk，只遍历完整16M逻辑域一次。完整ID流SHA应为`a020c67a…`；原230合法RGB互异必须验证，因此ID支持数与RGB支持数一致，并另按实际palette值计数。

保留16×230的完整bank/globalID联合频数、每bank输入数/独立RGB数/独立ID数及RGB集合、全局实际命中色数、全部失败bank列表、源/逻辑摘要和进程峰值。独立对输入`R+B+2G`的三个有限序列卷积，核对16个bank域大小与16777216总数，防止R/B地址错置、溢出或漏域。此独立输入核对不读取输出，也不改key。无照片/gold、mapper计时、新ROM或本地编号写盘；资源wall仅用于调度，不作速度结论。

通过只说明布局可表示精确输出，不是压缩decoder或性能通过；root随后决定是否实现唯一版本。失败则封存当前方案，无native/性能、备用key或追加筛查。输出目录仅固定`artifacts/p16-luminance-palette-census-v1`，存在即拒绝覆盖，不追加独立择优运行。预计一线程2–5秒，工作集<100MiB，分块数组与4096桶计数，不保留64MiB全RGB输出。

## 若通过后才考虑的单版格式和运行时成本

预定研究格式`L7BK v1`：32B头（magic/version/16bank/7bit/table长度/key枚举/保留），16×LE16有效count共32B，16×128×LE RGB32 palette共8192B，按原code顺序的固定7bit直表14680064B，末尾4B零guard。总ROM **14688324B**，不另保留原256global palette。每bank count1..128，其余槽清零；每个有效RGB仍须<=ffffff。每条7bit ID只在所属输入bank的count内合法，prepare须核全部域，不能只检查全局ID<128。

建议独立借用model为`const uint8_t* blob; size_t blob_bytes; const uint8_t* table; const uint8_t* palettes`，预期Windows x64 **32B**，常驻投影 **14688356B**。这是未实现ABI/容量投影，须用真实`sizeof`、ROM长度和native边界验收替代后才能宣称实际节省；不能继续套用旧1056B ctypes结构，也不在计数中遗漏两份或漏算复制palette。C99用显式LE，ROM可不对齐，不依赖调用方padding、堆、C++或OMP；loader/导出/prepare峰值和栈必须另列。

唯一概念解码为`bit=7*code; local=(LE16(table+(bit>>3))>>(bit&7))&127; RGB=LE32(palettes+4*(128*bank+local))`。LE16最多跨字节；最后输入code的读取进入显式guard，不读出ROM。bank运算从原输入求值，不查额外map或pool；RGB仍有bitstream→palette两层依赖，palette地址另外依赖亮度加法/移位。本设计没有吞吐预测，不挪用旧有损7bit的速度或质量结果。

若获后续native授权，除8组C99/scalar/AVX1/4原地/分离完整域与百图SHA外，还须覆盖bank边界63/64等、和0/1020、R/G/B全范围、所有16个bank及合法local127、7bit八种起始bit位置、末bitstream/末palette/guard、源/目标/ROM保护页、非对齐、零长、重叠/格式拒绝及借用生命周期。新普通C99不等于已执行大端/WASM/MCU；只有质量通过再另冻同场fast78/80/旧线性ID/新本地palette的四模式100..50性能门槛。旧50%有效反例与A/A失败都保持，不因本机制可精确而豁免速度。
