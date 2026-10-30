# Native页指针：六角色近邻配对正式静态协议

状态：仅静态稿；没有AST/身份冻结、formal预检或计时。当前质量已通过，原build误gate、finite夹具及两个独立审计STOP永久保留。本协议不恢复copy4既有失败资格。

## 固定角色、数据与环境

六角色按加载顺序固定ref78、ref80、linear_c99、copy4_c99、p4_avx、pages_c99。前两为同源a399当前固定最快基线；linear为原合格Clang线性C99，copy4为原P4 copy4 C99，p4_avx为原P4已测AVX incumbent，最后为本次新48B view+4096 native页指针的C99/OMP入口。所有模型在同一进程同时prepare并保持驻留到全部调用完成；不把慢parent/incumbent作为主分母。

新候选A分别和五个其它角色B构成5个独立pair。全部比较固定原100图连续235929600B，输入SHA e13278cf…、输出f3c0d907…；每次调用处理完整100图。固定master只读映射和target工作地址，所有角色共享相同输入/输出地址；原地先把输入copy到target再同址apply，分离直接master→target，不凭空增加copy_total。原地apply与copy+apply分别报告、分别设门，不能用copy稀释内核退化；分离只有apply。

4 fresh worker串行，各从显式--plan先核Python3.12.14和冻结env，再以stdlib ctypes/WinAPI设置并读回进程允许集0x55=[0,2,4,6]，之后才导入NumPy及本仓native/OMP桥；NumPy导入后立即核1.26.4版本及env未变。RSS同样执行此早期bootstrap，逐进程保存实录，审计器重新核对。main parser也required接受--plan并核resolve与bootstrap相同。每worker/RSS在全部model close和末模块观察后另存required_environment结束实录，不符保留STOP；审计分别核NumPy前/后和阶段末，含WAIT_POLICY/THREAD_LIMIT，不用base.env的缺省字段代替。runner使用stdlib-only，按协议给每个子进程传全部冻结env，不让NumPy在driver中提前初始化。

冻结env为OMP_NUM_THREADS=4、OMP_DYNAMIC=FALSE、OMP_THREAD_LIMIT=4、OMP_WAIT_POLICY=PASSIVE、OPENBLAS_NUM_THREADS/MKL_NUM_THREADS/NUMEXPR_NUM_THREADS=1、PYTHONUTF8=1、PYTHONIOENCODING=utf-8。环境不符先STOP，不在bench静默改值继续；全部角色同约束。这不是逐OMP线程绑定、锁频或对旧迁移的因果诊断；不和未绑定历史绝对ms直接合并。CPU0/2/4/6均是实际允许集，不根据速度挑核。每调用保存copy前CPU、native前后CPU及地址；未知其它进程不杀、不宣称宿主绝对独占。

## 四组×五次的明确含义及调用数

这里“四计时组×5 round”指一个ABBA或BAAB的**四个位置组，每组连续5次完整百图调用**，不是再重复20套ABBA。每角色在本pair恰好两组、各5 timed，便于自身第二组/第一组稳定性校验。

每pair/cell先镜像预热A,B,A,B或B,A,B,A（各角色2次），之后四timed组ABBA或BAAB，各5次；全部预热和计时保留native返回。每角色第2次warm末及四timed组末核完整输出SHA，恰好6项/cell；其余中间调用不额外hash，不能声称逐调用1920次SHA。每pair/cell24调用（4warm+20timed），四模式为1T/4T×in/out：

| 项目 | 数量 |
| --- | ---: |
| 每worker pair/cell | 5×4=20 |
| 每worker完整百图调用 | 20×24=480 |
| 四worker全部调用 | 1920 |
| timed调用 | 4×4×5×20=1600 |
| warm调用 | 320 |
| 原地调用metric | apply_ns、copy_apply_ns |
| 分离调用metric | 只有apply_ns |
| 自身AA项 | 40原地pair-cell×2角色×2metric+40分离pair-cell×2角色×1=240 |
| 完整100图输出SHA | 80pair-cell×6=480 |
| fresh无图RSS进程 | 6 |

worker偶数以1T→4T、in→out；奇数反向。对每cell，pair控制列表按worker左旋后，奇数再反向；ABBA/BAAB由(worker+是否4T+是否out)奇偶固定，互为镜像。没有结果依赖次序、丢弃round或追加采样。

## 逐调用记录与AA

原地先记录copy前CPU，t0→copy master到target→t1；记录native前CPU，t2→执行固定入口→t3；记录native后CPU。copy_ns=t1-t0，apply_ns=t3-t2，copy_apply_ns=t3-t0，gap_ns=t2-t1（包括CPU/clock观测间隙）全部保留。分离只记native前后CPU与apply_ns，copy三字段为空，不生成第二统计metric。SHA和模块枚举在计时外，仅约定480个组末核完整百图SHA；全部1920个native返回与允许集检查，身份/native/SHA首次失败保存STOP，不补跑。AA失效则仍执行剩余预定轮次，保存失效不重采。

每pair、每metric、A和B各自两组5次中位数g1/g2；自身AA=g2/g1，闭区间[.85,1.15]。任一角色AA失败，只清该pair/cell/metric，保留其它pair及另一metric自身的独立判定。没有跨pair总体AA、平均phase或慢角色替代主控制。

同pair第i出现组的吞吐保留率r_i=median(B_i)/median(A_i)，i=1,2。主底线要求ref78与ref80两个pair在所有四worker的相关mode/metric均有效，并取两个pair、两组、全部worker的最小r。它等价于同时满足两个本地配对基线的严格共同底线；不把不同pair的绝对ms先拼成一个最快分母。另三辅助pair分别报告自己AA和最劣r，不能救主底线。

每mode/metric独立授100/90/80/70/60/50最高已满足档；任何所需主pair失效，该mode/metric全部清档；任何有效主ratio低50如实保留反例。四模式联合同时要求4项apply加2项原地copy+apply，共6个metric-cell全有效且最劣过线，再与精度100/90/80/70/60/50构成36格。逐metric/模式限定结果另列，绝不以4T限定救全局。这里精度是输出精确等价保留100%，不是原数学误差零。

## 实际模块、RSS与容量

每worker记录准备前、六角色全部准备后、全部关闭后的实际libgomp/libgcc/libstdc++/winpthread绝对路径/SHA/数量；准备后/关闭后每名必须各1份且属于冻结输入，不能把磁盘多个目录当作实际加载证明。六个RSS角色各自独立fresh，使用相同imports和流式身份预检，不分配图像；同样三时点模块观察并保存baseline/prepare/close的WS、PrivateUsage、Peak及句柄。模型close不会卸载DLL，不承诺总句柄回导入前值。

磁盘六个父目录的四依赖只读存在性核对24/24通过；这不是本轮已加载观察。hot进程按ref78首加载，RSS各自独立，ref80的libgomp/libgcc磁盘摘要与其它目录不同也完整冻结保留。实际观察可为各自不同路径/SHA；检查标准是该进程每名唯一且属于冻结输入，不强认全部RSS都加载ref78或同一gomp，不更换库/环境追求统一。

新实际capacity=ROM12633124+caller页表32768+view48=12665940B；旧P4/copy4=12633164、linear=16779328、ref78/80=28046644。代码/宿主owner/模块/OS和进程峰分别报告；RSS包含imports、SHA和模块元数据，不称prepare专属峰、纯物理RAM或此次减少代码容量。

当前API与ABI、ROM、所有旧对象/DLL和新唯一对象/DLL都不变，不编译、不重新导出、不新拟合，不更换依赖追结果。初步预计1920完整百图调用约6–10分钟（待实际记录），每workermaster映射235.93MB+target235.93MB+六模型/库等，峰预计<900MiB；若实际超出只记录，不改变数据/轮数。正式运行需root完整review源码并另grant。
