# 历史精度能力迁入现框架

本阶段把历史网格、坐标、拟合和整链整数搜索迁入目前赛事入口，保留LUT-only、单线程及逐级RGB8量化。目标是提供可组合、可回退的能力，不承诺在不同参考LUT上复现旧Cinema百图0.67909。

实施分支：`codex/p16-precision-migration-20261030`。起点：`0bf54234`。不改原赛方模板和数据，不改其他工作树。

预设验证范围：运行时以独立标量几何和完整色域验证sidecar/混合三线性、四面体与RGB24一致性；拟合以固定原四LUT完整256³域的mean、SSE、p99、max、CVaR01判定；照片仅在冻结模型后作100图回归，不参与训练选型。格式和部署通过单头生成与现有契约测试验证。性能仅测同机单线程，不推断官方平台。

环境：Windows x64，GCC 15.2，C++17 O3，OpenMP关闭；Python 3.12.14，NumPy 1.26.4。GCC13.2及官方设备未验证。实际命令、硬件、哈希与结果在完成验证后补入。

迁移范围：曲率CDF及弦SSE动态规划非均匀轴；共享/分输出Q16坐标；混合容量；匹配三线性/四面体拟合；独立LS、链末层LS、box约束QP、Lp6 IRLS及尾部加权；四阶段真实整数RGB联合节点与坐标搜索；联合(prefix,target)支撑质量和精确后缀；固定完整域锚点及可选逐色保护。

边界：历史照片质量改为原LUT完整色域均匀质量，不导入旧模型或照片统计。搜索有固定预算，不声称求到全局最优。三线性Sparse采用Scalar；DirectRGB24可使用现有AVX2查表。旧palette U8/U16不接受混合三线性。准备峰值与运行内存分别报告。

已完成实现与本机验证；以Draft PR交付，不申请合并。默认sample与现有chain_ls保留，新增能力通过`-Fit history`显式启用。依赖已完成的偏好入口PR #103，最终基线同步至`04a0e8b2`。提交由本分支Git记录及PR关联，运行源码和当前源码分别归档。

## 能力与具体边界

| 历史机制 | 当前迁移与入口 | 验收和限制 |
| --- | --- | --- |
| 曲率、DP、误差轴 | `precision_geometry.hpp`生成三条轴，adapter支持自定义轴 | 整数节点轴；曲率CDF和DP代理不保证整链最优，保留原两种网格 |
| 精确/一般坐标校准 | 完整源与节点张量结构证明、轴置换/共享的单调舍入可行域；共享及每输出9216B sidecar搜索 | 非结构表明确回退；所有新坐标进入实际恢复器，旧LS拒绝静默忽略sidecar |
| 混合m与matched basis | 每级m、tetra/tri元数据；三线性匹配box拟合；显式容量列表、ABC选择器 | full验证列出四个25/33混合候选；不声称穷举所有组合。三线性Sparse实际Scalar，RGB24仍可AVX2 |
| 连续拟合 | 原独立/末层链LS，加通用27邻居box-QP、投影KKT、Lp6 IRLS和尾部再加权 | 原四LUT目标；固定320扫/1e-7阈值，不收敛候选不发布 |
| 真实整数节点 | 四级依次用真实Q16/RGB8和RGB联合26方向、步长1/2/4搜索 | 默认每级32热点节点、1扫；优化最终链距离而非只看连续SSE |
| 整链联合支撑 | 完整域按(prefix RGB,gold)合并并保留整数mass；重放精确后缀 | 未使用任何照片频数；支持前/中/末层，支撑频数总量固定256³ |
| 双loss与逐色cap | `Options.local_fidelity_weight`可增加本级源保真损失，`Guard.pointwise`启用阶段起点逐色非退 | 默认双loss权重0；二者由合同验证，不宣称在Test四表上获得额外收益 |
| 尾部与预算交换 | 固定chain_ls锚点；mean/SSE/max、历史线性p99及ceil(N/100) CVaR；Q24均值/尾部证书 | 搜索可花掉此前相对固定锚点获得的预算；不会重设更宽锚点。中途max下降不保证以后保持该更低值 |
| minimax/CVaR/整数箱 | 不同真实终点目标，冻结节点变量整数箱完整穷举 | 默认末级单节点RGB的±1箱，至多27叶；大箱超预算直接拒绝。只在声明箱和证书允许的候选内比较，不宣称全局最优 |

`precision::Options`逐项开关、预算、目标及guard在hpp中公开。历史照片训练质量、固定Cinema成品和旧收益没有导入；频率迁移诊断不是独立优化器。历史部分浮点轴/连续误差代理改为当前RGB8/Q16实际语义，不宣称逐行复刻所有旧研究脚本。

## 同源精度回归

四份原始缓存/原表身份、100照片SHA和全部逐图数据见[归档](../../report/data/p16-precision-migration-20261030/manifest.json)及[对照](../../report/data/p16-precision-migration-20261030/comparison.json)。100张1024×768 RGB8与既有chain-framework执行清单逐一匹配。旧Cinema的0.679090仍属于另一组LUT，不是本组比较基线。

| 指标，RGB8欧氏距离 | chain_ls基线 | history迁移后 |
| --- | ---: | ---: |
| 完整256³域mean | 0.695639245063 | 0.658143555016 |
| 完整域SSE | 40474576 | 36241723 |
| 完整域RMS | 1.553213676515 | 1.469753389335 |
| 完整域p99 | 6.082762530298 | 6 |
| 完整域max | 50.209560842533 | 50.209560842533 |
| 完整域CVaR01 | 10.053580781808 | 9.300069190689 |
| 100图平均mean | 1.484947205138 | 1.497479283713 |
| 最差单图mean | 2.385774487957 | 2.404070930315 |

完整域mean下降约5.39%，但百图平均mean上升约0.84%，50图改善、50图退步，最大单图mean增量0.922464。**这是能力迁移和完整域改善，不能称作照片精度全面升级。** 不依据本次照片结果重选预算/模型，不替换默认档。

full预先列出47个候选步骤，20步接收。Uniform优于Framework；曲率均值更低但max越界而拒绝；DP/混合容量及三线性未最终入选。末级三线性、chain_box、两轮IRLS和tail加权未在320扫内达到KKT阈值，候选保留测量但未发布；这5项不得计作已收敛或精度提升。Test2/3/4不满足精确单调结构，明确回退。最终四级均m33/tetra，后三层各9216B分输出坐标；模型总计475900B，RGB24额外约48MiB。完整域max曾在中途下降，有限箱最终使用已获得的预算回到固定锚点上限，属于预声明保护语义。

## 验证、环境与交付

Windows11 26200 x64、AMD Ryzen9 8945HX 16核/32逻辑核、GCC15.2、C++17 O3静态链接、OpenMP=0。算法单线程，正确性/拟合阶段并行进行过其他构建，不授予稳定性能收益；没有测量准备峰值RSS。full准备墙钟观测459.92秒，不是正式映射计分耗时。Python3.12.14/NumPy1.26.4；原四表约384MiB及搜索临时支撑不包含在运行模型RAM中。

- CMake定向7/7：adapter默认/禁AVX2、fit、fit numerics、preference、precision、RGB24；新增precision独立禁AVX2编译/运行也通过。
- Python原完整框架组60/60；新增history参数用例后重跑相关入口37/37。合计覆盖61个独立用例，不能把重复执行加成97个。
- 新合同覆盖195076个RGB平方误差的Q24上下界、独立混合tri/tetra/非均匀/sidecar算术、短尾与相位、原地/重叠/预算、联合mass守恒、box KKT、全域增量重放、双loss、精确单调及整数箱。
- 冻结模型：Sparse Scalar与RGB24实际后端遍历所有16,777,216输入逐字节一致；独立NumPy从序列化模型重放全部50,331,648输出字节，独立原表引用及100图全部指标复算通过。
- 赛方单hpp目录`F:/Hackathon/极速焕彩测试框架/FlashChromaHistory`实际执行`run.ps1 -Mode direct_rgb24 -Grid framework -Fit history -Count 4`成功；四图打印均值独立复核至打印精度，HistoryReport最终指标与full相同。无照片准备、原C/C++模板和data未改。
- 单hpp 235781B；ZIP 956939B逐成员回读一致，只有Windows系统DLL。旧FlashChroma目录未替换。代码格式化前后benchmark的`.text`机器节SHA相同；运行前源码存入final-sources，格式化后的源码存入sources，不能混称同一源码SHA。
- `scripts/generate_flash_chroma_header.py --check`通过；归档脚本对冻结来源、源/模型/报告SHA及同图基线进行检查，支持`--verify`只读复核。

首轮run1为未补齐最终历史p99/CVaR证书、误差轴、精确单调和整数箱的中间版本，源码与结果完整保留，最终使用v2。独立Python初次读取中文JSON时命中Windows默认GBK解码失败，补显式UTF8后通过，失败日志保留。初次smoke漏传include目录编译失败，补`-I include`后通过。读取正在运行EXE的节时objcopy尝试回写受Windows文件锁拒绝；节数据已导出，执行EXE未改变，最终采用只读PE解析核对。赛方模板原有unused N警告保留；迁移头的缩进警告经格式化消除，不改原模板。

## 复现

```powershell
$py = 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe'
& E:/mingw64/bin/g++.exe -O3 -DNDEBUG -std=c++17 -static -I include -I framework framework/precision_benchmark.cpp -o benchmark.exe
# 四个cache参数分别为Test1/Test2/Test3/Test4的u16le缓存；最后两个参数是新输出目录与固定候选预算。
.\benchmark.exe <cache1> <cache2> <cache3> <cache4> <100图bin目录> <新输出目录> full
& $py -X utf8 scripts/verify_precision_migration.py --run <新输出目录> --cache <缓存目录> --photos <照片目录> --output <新独立回执.json>
& $py -X utf8 scripts/install_framework.py --framework <赛方框架目录> --output <新交付目录> --compiler E:/mingw64/bin/g++.exe
& $py -X utf8 scripts/archive_precision_migration.py --verify
```

手动history固定输入容量；ABC模式可用`-Preference '1,0,0' -CandidateSizes '33;17,25,33,33' -Fit history`按每个容量重新生成完整候选，运行时再择优。高级C++可显式设置`capacities`、guard和预算，偏好入口禁止内部再次换容量，以免误报所选计划。

## 协作检查与未完成项

创建前获取远端，读取/刷新#103正文、完整comments/reviews/行内线程，读取历史审计#100及#96版本化review、相关#7/#8正文与完整评论，并按precision/精度/拟合/framework检索。#103头为04a0e8b2，作为本PR目标；#96已被维护者合入，但其旧verify容量中断与bind_evidence目录指标绑定两个P2仍无修复证据，本次不修改也不宣称修好。#7的337a3dd/876e15b8/397cc367实际包含在祖先；#8接口/实板待办保留。Discussion4读取缺口不等于没有问题。不执行merge或关闭事项。

GCC13.2、官方阈值/服务器/正式百图、额外缓存/sidecar许可、真实嵌入式设备仍未验收。原通用C99核与RGB24热核未改；新增混合插值适配器属于宿主C++部署，不能自动转授裸机资格。远端CI以本PR当前实际结果为准。

Agent：Codex /root；Operator：本会话要求迁入所有历史精度能力的用户；Status：本机实现和验证完成，Draft交付。
