# 293/294 max41性能预案：新增冷热门，不预先授档

这是新增质量门通过前的静态草案，尚无正式冻结或计时。只研究固定max41模型，不把数学候选全部重测一遍。若293的域资格或294/完整质量失败，停止本预案。

六角色固定为87-a399、87-best、293-best、294-best、293-max41、294-max41。两个候选各用87-a399、87-best、同runtime-best作三个主分母；另保留293-best/87-best、294-best/87-best与294-max41/293-max41三组辅助配对，共九组。辅助分母不能替主分母救50%线。

四个fresh worker串行，进程允许CPU 0/2/4/6在任何NumPy/native/OpenMP导入前设置，不做逐TID绑定、不锁频。固定同一235929600B百图RGB输入与source/work地址，全部角色模型同时驻留。每个热pair/模式预热两角色各2轮，然后按ABBA/BAAB（四worker镜像）分别两phase，每组3轮，计时外核实际末组完整输出SHA。模式为in/out各1/4线程，原地同时保存纯apply和copy+apply。任一角色任一相关metric的phase2/phase1超[0.85,1.15]，该pair/模式清档；比例取同worker/同phase中位耗时之比，不合并phase。全局档取所有主分母、四模式与四worker×两phase的最差有效值，任一有效<50%保留为负例，任何所需AA失效均不能授全范围档。

冷范围补充N1与N100两个独立profile：每角色每N固定5+5 fresh句柄，phase2镜像角色顺序；路径数组、工作区填充值在连续wall之外；native create起点至第一个完整N图Out4返回使用连续perf_counter_ns，另存create段与首组native内部耗时。输出SHA在连续wall之外。各metric独立核自身双phase AA，连续wall资格只由连续wall AA及同场三个主分母判定，不把prepare中位数下降当wall通过。N1与N100必须分别给档；如果单图冷profile<50或AA失效，不能宣称所有冷/热场景共同达到50。

预计热144 pair-cells，288预热组末SHA+576计时组末SHA；冷四worker×六角色×两N×10句柄=480实际SHA，总1344。native调用为热576预热+1728 timed，加冷480，共2784；native内部计时数组每组repeats与实际末输出的区别须明确。每个pair末及每worker起止另核原输入完整SHA。首次身份/native/输出错误保留并STOP；AA失效不缩轮、不补跑。

六个无图片fresh RSS进程，保持同三DLL imports并记录prepare前/后/close后WS、PrivateUsage及peak，真实Model capacity另列。所有worker和RSS均在计时外保存实际四个GCC依赖模块路径/SHA/数量，不从磁盘目录存在或历史observer外推。正式冻结绑定全部源、实际库、依赖、完整质量、模型、输入与输出预期；单次执行后独立Decimal/Fraction复算六档。

边界：这不是新官方分数、指定Intel硬件或未见图泛化证明，也不是所有可能合成输入的最差速度。N100 warm与cold profile不得拼接成N1资格。未做分配失败、无AVX2或异常注入的覆盖应照实列出。
