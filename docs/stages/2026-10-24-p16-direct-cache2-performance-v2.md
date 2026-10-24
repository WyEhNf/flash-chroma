# 293/294 双线程策略正式性能：局部热吞吐通过，完整冷热资格未通过

Agent：`/root/speed`，Operator：本会话用户。任务：第16题精度模型运行时的同场交叉验收。状态：Draft；唯一正式采样及独立 Fraction/50位 Decimal 审计已通过，未合并。对应提交为同时包含本文、四份测量源码及本阶段证据目录的中文阶段提交。

本阶段固定已验的 max41 数学模型，比较87、293和294运行时。主口径 U 下，293-max41 的 N100 热范围48个主配对全部 A/A 有效，最劣通过60%档、未通过70%档；N1/N100 冷连续 wall 存在 A/A 缺口，因而没有获得完整冷热50%资格。294在 U 下未取得任何完整范围档。辅助 P 下保留294的一个有效低于50%反例，P的局部正例不能替U恢复资格。这些结果不构成整体速度升级。

## 固定对象、环境与计数

最终预注册是[双策略协议V2](../../experiments/p16-direct-cache2-performance-protocol-v2.md)，旧draft未执行。冻结计划 SHA 为 `1e3fd982f22675519fe6d578fb54ddaf4766a4e3b7593dd60062d792c7400781`，包含222份源码身份和43份输入身份。六角色为87-a399、87-best、293-best、294-best、293-max41、294-max41；每个max41运行时分别对87-a399、87-best和本运行时best作三个主分母，另有三组辅助配对，共九对。

Windows 11 26200、AMD Ryzen 9 8945HX，GCC15.2，已有Release/AVX2及BMI1产品，未使用AVX512。Python3.12.14、NumPy1.26.4；进程在NumPy/native/OpenMP导入前限制CPU集合0/2/4/6，OMP线程上限4、dynamic关闭、wait policy为PASSIVE，BLAS线程1。U不逐TID绑定；P另用已验helper把同pool的OMP tid0..3分别固定到CPU0/2/4/6，并在结束前用原saved record恢复0x55。两策略各四fresh worker及六fresh RSS进程，串行顺序为U4worker→U6RSS→P4worker→P6RSS。

四个GCC依赖按winpthread、gcc、std、gomp顺序以`E:/mingw64/bin`完整路径显式预载并保留模块句柄。实际HMODULE枚举在产品加载后、准备后及结束时均要求每个basename唯一，路径和SHA精确相等；加载前允许0或1个符合身份的实例。唯一libgomp SHA为 `fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88`，helper SHA为 `fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f`。每个预热组、热计时组和冷作业前后均记录四成员真实OS TID/mask，任何API、身份或输出错误即停止；本次全部通过。U/P各worker实际helper调用676/680次，RSS进程5/9次；helper调用未计入图像apply。

输入为固定235,929,600B百图RGB8，SHA `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`。每策略1,344个末输出SHA、2,784次图像apply和6个RSS进程，合计 **2,688个实际像素SHA、5,568次apply、12个RSS进程**，全部相等。N1/N100期望来自已有实际首图/整百图像素SHA，三模型的`derived_pixels`均为false，没有串接逐图SHA文本，也没有为本阶段重跑旧全域质量。

唯一控制器于2026-10-24 12:33:25.4723236+08:00开始，12:46:46.4116883+08:00结束，持续800.9393647秒，退出码0。2秒进程CPU差值预检、开始/结束时刻和控制器日志完整保存；预检中的未知GUI及遗留credential/git进程没有被终止。未锁频、未监测PMU，不声称主机绝对独占，也不作频率因果解释。

## 时间边界与判定

N100热范围固定原地/真分离各1T/4T。每pair两角色各预热2次，随后ABBA或BAAB四组，每组三次native apply，四worker采用固定镜像顺序。每个角色在phase1/2各有三份原始耗时，只比较同worker、同phase的中位数。A/A为phase2/phase1中位耗时，闭区间[0.85,1.15]；原地apply和copy+apply任一相关A/A失败就清除该cell资格，全部样本仍保留。六档固定100/90/80/70/60/50，任何有效低50为反例，任何必需A/A失效则不得授完整范围档。

|冷指标|原始字段与边界|判定用途|
|---|---|---|
|prepare|`create_ns`：直接native create返回前后差值，包含该create实际文件读取/校验及表准备|各自五次/phase的中位数和独立A/A，不能代替热吞吐或wall资格|
|firstApply|`first_apply_seconds`：第一次N图真分离Out4的native内部耗时|独立A/A与比例完整保留，不能与prepare拼成另一个wall|
|连续wall|`wall_ns`：直接native create入口前至紧接的首次N图Out4返回后|N1/N100分别按自身wall A/A授档；metadata、SHA和helper均在此wall之外|

每worker全部热cell完成后，六个热句柄全部销毁，再进入N1/N100冷范围。每个N、角色、phase固定五个fresh句柄；每次核完实际输出SHA即销毁，冷范围没有额外热候选驻留。路径数组、source/work/target预触页在wall外，create与首次apply之间没有Chain包装、输入哈希或诊断。P的pool形成/绑定早于模型create，因此“冷”指fresh模型句柄，不包含fresh进程首次OpenMP成本。

## 主U与辅助P分别报告

下表仅汇总原独立审计已经输出的主分母资格，未追加采样、补轮或重选结果。“无完整档”包括必需A/A缺口；不能把未证实写成有效低50。

|策略/候选|N100热主cell|N1冷wall主cell|N100冷wall主cell|完整冷热资格|
|---|---|---|---|---|
|U / 293-max41|48/48 A/A有效，0有效低50；60档通过，70档不通过|12中4个A/A失效，0有效低50|12中1个A/A失效，0有效低50|50%尚未证明|
|U / 294-max41|48中14个A/A失效，0有效低50|12中7个A/A失效，0有效低50|12中4个A/A失效，0有效低50|未取得完整档|
|P / 293-max41|48中4个A/A失效，0有效低50|12中2个A/A失效，0有效低50|12/12 A/A有效，60档通过，70档不通过|不能恢复U；P完整冷热亦未获50档|
|P / 294-max41|48中12个A/A失效，另有1个有效低50|12中2个A/A失效，0有效低50|12/12 A/A有效，60档通过，70档不通过|保留有效反例，不能恢复U|

P / 294-max41 的有效反例是worker3、pair4、真分离1T，对87-best。两phase速度保留率原始精确分数为62161/134175和65423/132025，最差62161/134175<1/2；双方A/A通过。该反例不会被其他cell的A/A失败抹除。所有主/辅助配对、各phase、失败A/A以及prepare/firstApply/wall的独立统计，均留在完整`statistics.json`与`fraction-audit.json`，没有按较优策略或较优phase拼接。

## 表表示、容量与RSS边界

六角色每次热构造、每次冷构造及RSS构造均核冻结稳定表示；冷角色另与同worker热状态核对。所有cache enabled、domain eligible、reachable32768、unproven0、direct enabled字段均保持。仅构造耗时和allocator地址模64从稳定身份投影中排除，原值仍完整保存。

|角色|Model容量B|实际表示|
|---|---:|---|
|87-a399|18,579,204|230色u8，direct format9|
|87-best|18,715,680|234色u8，direct format9|
|293-best|18,715,824|234色u8优先，wide disabled|
|294-best|18,715,824|234色u8优先，wide disabled|
|293-max41|35,673,508|wide format16，613色，33,554,436B表＋2,452B palette，guard4B|
|294-max41|52,448,272|wide format18，50,331,652B RGB24表，guard4B；wide自身palette_size为0，legacy palette诊断颜色数613|

12个无图片fresh RSS进程各只准备一个指定角色，记录prepare前/后/close后的WorkingSetSize、PrivateUsage和进程PeakWorkingSetSize；所有原值保留。Model容量是对象/vector账单，不等于RSS或准备总峰值。P的helper/pool背景常驻，不能把不同fresh进程背景差解释为算法节省。本阶段未对RSS另作聚合或声称节省。

## 证据、封存与未完成项

四份测量源码为[freezer](../../scripts/freeze_direct_cache2_perf_v2.py)、[support](../../scripts/p16_cache2_perf_support_v2.py)、[driver](../../scripts/run_direct_cache2_perf_v2.py)与[独立审计](../../scripts/audit_direct_cache2_perf_v2.py)。正式命令是`python -X utf8 scripts/run_direct_cache2_perf_v2.py --plan artifacts/p16-direct-cache2-perf-frozen-v2/plan.json --output artifacts/p16-direct-cache2-perf-v2`，完成后唯一执行`python -X utf8 scripts/audit_direct_cache2_perf_v2.py artifacts/p16-direct-cache2-perf-v2`。已有不可覆盖输出目录，这些命令不应直接重复执行。

原[V2归档器](../../scripts/archive_direct_cache2_perf_v2.py)的唯一执行在创建输出目录/ZIP之前因protocol路径键`KeyError`退出1：freezer对protocol使用`str(relative_to)`形成Windows反斜线键，四脚本为正斜线键；归档器直接按正斜线取键未命中。真实工具回执转录明确标注不是现场本地stderr，旧两post原字节保留，没有修改后覆盖执行。正式采样与独立Fraction结果不受该封存胶水错误影响。

新[机械V3归档器](../../scripts/archive_direct_cache2_perf_v3.py)和[独立Git核对器](../../scripts/audit_direct_cache2_perf_git_v3.py)仅将source键的反斜线规范为正斜线，拒绝规范后重复键，原计划SHA及各测量源SHA不变。目标为`report/data/p16-direct-cache2-perf-v3`，仍消费唯一V2 formal/raw，未重测或重算native/统计。固定71份原始范围是本版frozen plan/expected、全部formal raw/statistics/fraction、launch预检/时刻/日志、四测量源码和最终protocol；另将旧两post、真实失败转录及新V3两post一并纳入，静态预期76成员。外部模型、DLL、照片及222份历史依赖不复制，不重跑历史native。

V3归档器已唯一执行成功，76个成员的ZIP CRC和逐成员字节SHA全部通过；八worker原始SHA/身份与results引用、expected与plan、launch可用身份，以及六复制文件与原件字节均通过。[封存身份](../../report/data/p16-direct-cache2-perf-v3/identity.json)和[逐成员清单](../../report/data/p16-direct-cache2-perf-v3/members.json)保留完整来源。Git核对器从ZIP独立核这些链接、无重复规范键及本阶段20路径显式白名单，不接触其他阶段文件；index/HEAD核对与中文阶段提交由后续独立回执记录。本次只修复封存路径键，未重新native、采样或统计，原V2失败与所有性能资格缺口仍保留。

数学质量沿已验24完整输出流及800逐图比较，本次末SHA只证明对应正式输出一致；不把它当官方ΔE阈值或未见照片验证。未注入bad_alloc/无AVX2故障，未验证指定Intel主机，未取得官方派生缓存许可。完整冷热资格仍缺失，保留所有无效项与低50反例；下一步由root决定，不以辅助P或局部N100结果替代用户的严格底线。
