# 293/294固定max41：冷热门及两种线程策略预注册

Agent：`/root`，Operator：本会话用户。本文件在正式驱动编写和计时前建立，替代尚未执行的draft-v1作为执行口径；旧稿保留。本阶段只研究已经完整正确性验证的293/294 max41及同运行时best，不重新拟合，不采用AVX512。

## 比较对象和共同门槛

固定六角色：87-a399、87-best、293-best、294-best、293-max41、294-max41。293-max41及294-max41分别对87-a399、87-best和自身运行时best作三个主分母。另有293-best/87-best、294-best/87-best、294-max41/293-max41三组辅助配对，共九对。辅助配对不能替代主分母授档。

精度沿用已经通过的24完整输出流、800逐图输出及独立物理表验证；正式性能的每个末输出仍须完整SHA相等。实际cache/domain/palette/wide选择和Model capacity在计时外逐角色记录，不能从旧observer目录推断。模型、235929600B百图RGB、库、依赖和执行源在执行前一起冻结。两种线程策略各自单独授档，不能取二者较好值作为普通部署结论。

## 两种线程策略和进程范围

U为主口径：四个fresh worker串行，NumPy/native/OpenMP导入前设置进程CPU集合0/2/4/6（0x55），不逐TID绑定。P为辅助口径：另四个fresh worker串行，进程集合相同，在准备模型前经已验唯一libgomp控制器把OMP tid 0/1/2/3分别绑定CPU 0/2/4/6。U和P均先形成同一个4线程pool并观察身份；P的pool预热及绑定不包含在模型create连续wall内，所以这里的冷启动是fresh模型句柄，不能称fresh进程首次OpenMP成本。

控制器固定`p16-omp-affinity-control-build-v2`、SHA `fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f`；实际唯一libgomp须为`E:/mingw64/bin/libgomp-1.dll`、SHA `fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88`。Record为72B。所有4成员OS TID固定，U的成员mask均0x55，P成员mask均单比特且实际CPU匹配。每一热预热组/计时组以及每一次冷create→firstOut4之前和之后，在计时外检查4成员身份；任何API/身份/mask/native/输出错误立即保存并STOP，不补跑。1T路径只用main tid，4T切换后仍必须恢复观察相同4成员。P在结束前按原saved record恢复，核恢复结果。控制器调用不算图像apply次数，但实际调用数单独保留。

两个策略的worker各自拥有固定source/work/target地址，六热模型同时驻留；不同fresh进程地址不要求相同，不将U/P差值解释成同地址因果实验。没有锁频、PMU、指定Intel硬件或全输入最差速度证明。

## 热范围

固定N100，inplace/outplace各1T/4T，共四模式。每个pair先两角色各预热2次，只对各角色最后预热输出做一次完整SHA（每pair两份末SHA）；然后四组ABBA或BAAB，每组3次native apply，末输出完整SHA（每pair四份）。四个worker用预先固定的镜像角色/pair/mode顺序，不能根据计时结果改顺序。原地每次先copy原始输入，分别记录纯native apply与copy+apply；outplace只记录纯native apply。Python建数组、SHA、诊断、JSON均在计时外。

四组使A/B在phase1和phase2各有3个原始耗时。每角色、每metric的AA使用phase2/phase1中位耗时，闭区间[0.85,1.15]。任一相关metric失败，整个pair/模式清档并保留原样本。有效配对比较只在同worker/同phase中取中位耗时比；不合并phase。候选速度保留率为denominator_ns/candidate_ns，档位100/90/80/70/60/50，低于50保留为负例。原地资格同时要求apply和copy+apply，不能只挑一种。

单个策略：四worker×九pair×四模式=144cells；预热末SHA 288、计时末SHA 576，共864。图像native apply为预热576、timed1728，共2304。任一有效主分母/模式/worker/phase<50%足以否定该范围；任一所需AA失效也不能授全范围资格。各局部有效结论完整报告，不用一次AA失败抹除其他负例。

## 冷范围

每个worker先完成全部热cell，再关闭六个热句柄，然后分别执行N1和N100冷范围，不在冷范围保留额外热模型。六角色每个N固定phase1五个、phase2五个fresh句柄，phase2镜像角色顺序；四worker同样预先镜像。每个冷输出核验后立即销毁该句柄，下一角色开始前无其他候选句柄驻留。路径数组与source/work/target预触页在wall之外。连续`perf_counter_ns`从直接native create入口之前到第一次完整N图Out4返回之后，不插入observer/模型info/SHA；另外保存create段和首组native内部耗时。首组输出完整SHA在wall外。每个角色的三metric分别独立AA；连续wall资格只由连续wall本身AA决定，不以prepare或首组内部指标救wall。

单个策略：四worker×六角色×两N×十句柄=480实际create/first apply/SHA。每个N分别对三个主分母按同worker/phase比较，最差值决定此N档；不能把N100资格拼接为N1资格。create/首组内部耗时只独立描述及按自身AA报告，连续wall是冷场景主门。

## RSS、模块身份与总数

每策略六个无图片fresh RSS进程，按同策略导入三DLL并建立同pool；只准备一个指定角色，记录prepare前/后/close后的WS、PrivateUsage及进程peak，Model capacity另列。P额外保留线程控制器常驻带来的背景，不将不同fresh进程绝对基线差解释为算法节省。每个worker和每个RSS进程均实际枚举四个GCC依赖模块的唯一路径、SHA和数量，保存加载前/准备后/结束状态；不能用磁盘目录或旧observer代替。开始和结束核冻结身份，计时外核原输入完整SHA，每pair末及每worker起止核source不变。

每策略1344末SHA、2784图像apply、6 RSS；U+P共2688末SHA、5568图像apply、12 RSS。冷模型create不属于热apply计数；热常驻六create和RSS六create另行记录，不混入480冷句柄。只有全部源码和计数独立审核后才能冻结，再单次执行。首失败保留、AA失败不缩轮、不补跑；独立Decimal/Fraction复算所有AA、比例、六档及最差值。

## 边界

RGB代理精度不是官方未公布阈值的ΔE判分；100图都已见过。这里未执行分配失败、无AVX2或其他故障注入，不将正确性通过等同官方得分。正式采样期间其他agent暂停构建、数值、打包、Git和大量哈希，只做静态文本工作。所有失败和不完整窗口继续保存，不能用P或局部N100正例替U/N1恢复资格。
