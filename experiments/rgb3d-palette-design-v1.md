# 输入RGB高3位的512个三维bank与6bit精确palette：单版静态预注册

Agent：`/root/memory`；Operator：当前16题用户；Status：Proposed，仅静态，尚未执行freezer或普查。94排他性能窗期间不运行Python/NumPy、ROM读取、构建、质量、ZIP或Git。待root另授数值窗，先冻结本设计/脚本SHA再唯一普查；不修改失败的亮度16bank/7bit方案、旧证据或默认。

## 固定key、索引和停止规则

输入R/G/B为0..255无符号码。固定`bank=(R>>5)|((G>>5)<<3)|((B>>5)<<6)`，用R高3位作bank低3位、G高3位作中3位、B高3位作高3位，共512。对于原表`code=R|(G<<8)|(B<<16)`，等价的同一key为`((code>>5)&7)|((code>>10)&56)|((code>>15)&448)`；各字段不重叠，无加法溢出，code0到ffffff映射bank0到511。每bank恰32×32×32=32768输入，总数512×32768=16777216。

每bank按全部输入的最终RGB集合独立编号。仅在**512个bank全部至多64色**时，固定6bit本地ID存在且可完全无损。任一bank>64即整个本机制STOP；不改3高位、key位序、bank数量、位宽、局部细分、异常池、输入范围或选择性fallback。先只做唯一全域census，不生成本地ID表/新ROM，不构建native或测试速度。全部可行也仅有存在性，不自动进入实现。

这与亮度16/7bit是另一个预定独立机制，不复写旧门槛或重复同一key择优。按输入空间上下文选择本地palette仍是无损编码，不是RGB网格采样或量化滤镜。每一个原24bit输入均有独立6bit entry，不用高3位低分辨率颜色近似。跨bank重复RGB最多占512×64槽，全部副本计入容量。

## 查重及已读历史的界限

查阅当前旧palette生成、3bit加例外ID包、有损全局7bit、连续4bank局部块字典、luma16/7bit和M16T。又读旧2³输入砖的RGB基值/短差分、header15和84混合格式，以及4³缓存行布局记录。它们分别是块内差分/例外、输入小砖地址重排或块ID局部化，仍不同于512个32³输入域的固定64项本地精确RGB codebook。旧同16色bank只读研究用输出ID>>4选择PSHUFB条件，也不是输入key。

在`experiments/scripts/docs/stages`以rgb/bank/codebook/局部palette/高3位/512与64等词检索，未在已读范围找到等价的512×64设计；不能据此断言全部历史或业界不存在。没有读取照片或gold来选本次bank参数，没有搬用这些历史方案的吞吐数字。

## 整数编码与完整容量账本

预定`C6BK v1`布局依次为32B头、512项LE16有效count共1024B、按原code顺序的6bit直表、4B零guard、512×64个LE RGB32 palette。头固定bank_count512、local_bits6、key枚举、table长度12582912、palette_slots64及保留0。有效count1..64，其余palette槽清零，有效RGB<=ffffff。

| 部件 | 字节 |
|---|---:|
| header | 32 |
| counts512×LE16 | 1024 |
| 16777216×6bit / 8 | 12582912 |
| 明确拥有的零guard | 4 |
| 512×64×RGB32 palette | 131072 |
| **完整ROM投影** | **12715044** |
| Windows x64借用model预期 | 32 |
| **常驻投影** | **12715076** |

model拟定四字段：blob指针、size_t blob_bytes、table指针、palettes指针；不复制原global palette或全部本地palette，不沿用1056B ctypes对象。当前只是布局/ABI投影，必须实际导出和sizeof后才能计为部署节省。32bit目标model预计16B也不是已编译验证。

table起点1056；guard起点12583968，4字节；palette起点12583972，最后一个4B RGB32词结束于ROM末端12715044。这样最后palette词可由真实ROM尾NOACCESS保护检验，bitstream短载荷另由明确guard拥有。ROM本身不要求对齐，C99读取显式LE，不依赖外部padding或主机端序。所有整形地址计算须用已验证宽度及size_t，长度/重叠失败无写和借用生命周期沿既有标准。

概念查找为`bit=6*code; local=(LE16(table+(bit>>3))>>(bit&7))&63; value=LE32(palettes+4*(64*bank+local))`。最高bit起点100663290在uint32范围内。6bit只有**0/2/4/6**四种byte内起始位置，不是7bit的8种；最后code的ID从最后byte bit2开始，LE16读取需要一个明确guard byte。4B guard也给可能的32bit读取留足3B，但当前不因此默认改变单版读取宽度。

输入bank的若干移位/掩码/或可与bitstream读取并行，仍有`6*code`定位、可变移位、ID到128KiB palette的依赖与额外工作集。没有map→pool，但不保证L1命中、分支或速度；M16T已说明理想读数不能代替实测。所有准备期/导出临时、model和ROM副本、loader/RSS及栈应另列，零堆C99不是零ROM/RAM。

## 唯一census及有限合同设计

数据只用固定a399原16B ROM5918672B，SHA904f768b…，由原map/pool解完整globalID；原palette230项互异，实际命中221项已由a020 ID流与3c9c RGB流逐色完整频数独立证明。保持230项合法输入契约，不用最高ID+1=223冒充221色，也不重读完整RGB流/照片/gold。

脚本固定一线程、262144输入分块，一次完整16M输出分类。先以20个输入边界值三维笛卡尔积8000例及2越界拒绝，核独立分通道key与位段key；正式全域也逐项核两种同一key相等、bank范围0..511。所有512个bank输入数应恰32768；完整ID SHA必须a020…，没有删除输入或只看已见照片。

保留512×230完整联合频数，每bank输入数/不同globalID数/实际RGB集合/6bit可行标志，最大色数和所有失败bank，而非只看平均或分位数。逐bankRGB集合与ID集合分别核对互异前提；全局命中色数与合法槽数分列。支持文件不是实际本地ID表/压缩ROM。预计资源wall2–5秒、一线程峰工作集<100MiB（Python/NumPy/6MiB源/分块与1MiB频数），需实测记录；不是mapper速度或核心RAM。

如果任一bank超64，阶段只封存负例，不输出ROM/native/perf；若全部通过，再由root决定单版实现/导出/质量。后者另需验证local63、512个bank及palette末槽、31/32等每轴边界、0/255、原code全范围、四种bit位置、末bitstream/guard/末palette、源/目标/ROM只读及NOACCESS保护、非对齐/零长/同址/部分重叠/格式拒绝/生命周期。C99、desktop scalar、AVX1/4原地/真分离8组完整域与逐图精度，再另冻结同场fast78/80速度四模式100/90/80/70/60/50；精度与速度独立六档，质量100%不能豁免速度50%底线。

若进入实现，正向合成夹具可令所有bank count=64、局部ID固定`(R&31)|((G&1)<<5)`，保证每bank都实际覆盖0..63，最后code=ffffff会命中bank511/local63；不能只用`code&63`并误称每bank都覆盖64项，因为R高位与bank已有相关性。另一count=1夹具验证所有ID0/空余palette槽清零。前者最后palette词可设ffffff，并使整个ROM最后字节紧贴NOACCESS。格式负例包括count0/65/ffff、任意高字节RGB非零、unused槽非零、guard非零/截断、key枚举或保留位错误和某bank局部ID等于其count；这些是待实施合同，当前没有运行。

当前仅静态文件，无冻结SHA、源数据普查、实际ROM/ABI/guard、候选ISA、拟合误差/性能或WASM/实板结论；官方对研究派生表的许可仍未确认。
