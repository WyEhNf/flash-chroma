# P4单版六角色同场性能：静态预注册

Agent：`/root/memory`；Operator：16题用户；Status：静态，尚未性能冻结/执行。质量b41c503e…唯一通过不等速度或WASM合格；原alias三次STOP保持。

固定六角色：ref78/ref80、原linear AVX/Clang C99、新P4 AVX/Clang C99。全用同一原a399，fast78/80容量各28046644B，linear16779328B，新P4实测12633164B。主速度分母每worker/模式选78/80耗时较小者；旧linear只辅助，不能拿慢分母授档。

四个新进程顺序运行，worker编号0..3；每个进程六模型全部驻留，共用同一photos只读源与目标地址。角色顺序按worker旋转，奇数镜像；线程顺序偶数1/4、奇数4/1，原地/分离顺序偶数in/out、奇数out/in。输入均是完整235929600B的100图串联，不择图或改数据。每次调用前都把源复制到目标，复制和全输出SHA在timer外，所有角色相同。每次native调用记录整数perf_counter_ns、调用前后CPU号、真实source/target地址、返回值及完整输出SHA。

每模式（1/4线程×原地/分离）先ref80一轮warm、两轮A-before，然后六角色各warm1+measured5完整100图，最后ref80两轮A-after。每模式5控制+36角色=41调用，每worker164、四worker656；全部调用输出均核f3c0d907…。没有重跑、缩轮或选择最好worker。首次native/输出身份错误STOP；AA失效本身不取消既定剩余测量，原始全部保留并把该模式所有角色档位清空。

AA以两次控制的精确平均耗时后/前，必须每worker均处于[0.8,1.25]。主保留率=该worker的min(median78,median80)/候选median，5轮中位以原始整数ns独立Decimal复算。逐模式四worker最劣值按100/90/80/70/60/50授最高满足档；不四舍五入过线。全四模式若任一失效则没有global四模式资格，任一有效低50则明确反例。mean/p99/max质量在本阶段沿已全输出一致的100%保留单列，不把数学误差写成0。

所有native worker和六个独立RSS进程固定SetProcessAffinityMask(0x55)，读回必须相同，记录system mask和调用CPU。它是前瞻的允许集，不是逐OMP线程绑定/锁频，也不证明旧未绑定漂移因果；不与旧绝对ms拼接或恢复3B。OMP环境4、dynamic false、OpenBLAS1。每次同场角色参数/ROM/DLL/SHA固定，未设置成功则启动前STOP。

四worker后，六角色各一次fresh RSS，不分配照片数组/不跑图像；同imports、流式SHA预检，before/prepared/closed的Private/WS/peak及实际capacity分别记录。原WinRO loader供linear/P4，准备时scan已含正常格式检查；容量不以ZIP或physical PFN替代。Python/库/OMP与OS成本包含在进程数，不把绝对RSS减成纯模型RAM；C99静态.su与全调用链另列。

正式启动仍需root明确排他grant。冻结前核质量计数/SHA/实际ABI及所有源输入；正式计划不得执行中改。这个单版没有参数/页尺寸/编译器/ISA扫描，不追加WASM或对象跨编译到速度门之后。
