# 16题288复用既有apply调度：质量及实际RSS完成，吞吐待测

Agent：`/root/tail`；任务：精度方向速度底线；状态：正确性完成、正式吞吐待测，保持Draft。前阶段287两候选有效最劣31%–34%，仍按[正式负例](2026-10-24-p16-direct-u16-perf.md)拒绝；本阶段尚未以新内核救线。

后续[八角色正式阶段](2026-10-24-p16-direct-u16-ilp-perf.md)已完成：有效子集吞吐改善，但22项AA失败使整体仍未证50%，不升级综合best。以下保留质量阶段本身的范围。

固定两只第二级候选及旧best，保持287的完整cache≤65536资格、32MiB uint16表+4B guard、动态palette、prepare、vector分配器、Handle结构和format16。288仅复制87实际四种apply核，将byte索引读取换为合法uint16读取：无BMI使用linear、单线程原地pair48、多线程原地normal_mt、真分离pair48_to。保留既有四包ILP、目标对齐、prefetch、NT/普通写及发布屏障，CPU有BMI才进入相应核。后续若有收益，只能说明整体apply调度有效，不能狭义归因ILP，亦不能归因为allocator或位宽变动。旧87/287源和DLL未改。

静态核对旧read/read_wide/scalar_one与287 gather解包的输入地址均为`R | G<<8 | B<<16`，跨64位输入字的第三/第六像素组合相同。新独立guard程序覆盖0xff/0x100/0xffff/0x10000/0xffffff及65535 ID，高位65536编译ID拒绝。四调度mode×11长度×原地/分离共88组guard均过，包含32/64包边界、4096全块和4097尾部，恰好源/目标后接不可访问页；当前CPU BMI可用，未跳过模式。新实现保留guard容量，即使合法u16标量读取不需要287 gather的额外2B。

在Windows11 x64/Ryzen9 8945HX/GCC15.2、CMake Release C++17 AVX2/BMI、OpenMP1/4上构建成功，无AVX512。与另一质量任务共享host，所有seconds只作过程记录。源码和预注册在构建前冻结，实际35项仓内编译器`.d`依赖均已前置冻结，包括287初期漏列的基础C/头文件，本次无事后补项。独立质量24完整域配置（含冻结87旧best六配置）逐字节0差；三只288模型600逐图输出0差；729短模式/后端组、8诊断拒绝、每模型11无效分离拒绝及255/256切换/大palette回退全过。分配失败未注入，继续明列未覆盖。

两新候选另与冻结287的整个32MiB表及palette逐字节相等，guard包含在表快照内，模型容量也相同：max_first 35,495,456B、p99_first 35,495,856B；两边本场实际地址mod64均0，不能推断未来分配必然相同。完整表SHA分别`09c3ae1b…`和`31ece1ec…`，全SHA在results.json。模型输出仍继承[第二级阶段](2026-10-24-cinema-second-nodes.md)的精度与逐图代价，没有重新拟合或按百图选择kernel参数。

另以六个全新进程补测287/288构造内存，不读照片/完整oracle、不apply。先导入Python/NumPy/psutil并加载DLL，再记录构造前后RSS、Windows进程历史peak_wset及销毁后值。

|后端/模型|构造后RSS增量B|OS进程峰值B|
|---|---:|---:|
|287 max_first|35,897,344|74,936,320|
|287 p99_first|35,921,920|75,005,952|
|287旧best|19,132,416|59,777,024|
|288 max_first|35,926,016|74,977,280|
|288 p99_first|35,897,344|74,989,568|
|288旧best|19,144,704|59,801,600|

这些是实际单进程working set及历史峰值，含模块、allocator、OpenMP；增量受分配器/页面状态影响，不能当精确净table，更不是全系统RAM。新四核静态`.su`分别为linear208/linear_to224、pair48224、pair48_to240、normal_mt224B，wrapper8B、prepare编译核448B；不把这些帧简单相加冒充线程栈峰值，也不把模型容量与RSS混用。

源为`experiments/p16-direct-u16-ilp-runtime/`；预注册`experiments/p16-direct-u16-ilp-plan-v1.md`；质量脚本`check_direct_u16_ilp_native.py`、RSS脚本`inspect_direct_u16_rss.py`。`prepare_direct_u16_ilp.py`只生成初始复制源，后续guard/验收增强以本提交源码为准。证据`report/data/p16-direct-u16-ilp-native-20261024/`含9原件、76源码、实际构建/栈、模型ZIP及六RSS原件。DLL SHA为`d95332e9ac8b56a9d589bf176a5b020e2d60a176d1f360594a0300b5efae5b9f`，冻结清单SHA为`532049b63900adfd06d2248e1c1164ef4676fc8288daa5cb6ecaf09cbdfdcd30`。

复现先`check_direct_u16_ilp_native.py --freeze --cache-root F:/Hackathon/projects/16-lut-color --output <新冻结目录>`，CMake MinGW Release构建`jshc_direct_u16_ilp p16_direct_u16_ilp_contracts`，再同脚本给`--frozen <JSON> --library <DLL> --contracts <EXE> --cache-root ... --output <新目录>`。具体构建参数见build-evidence.zip。RSS为`inspect_direct_u16_rss.py --frozen <JSON> --library <DLL> --sha256 <冻结SHA> --output <新目录>`，每次生成三个独立子进程原件。归档脚本不会重跑质量或性能。

下一步另冻结八角色同场性能：87a399/87旧best、288a399/288旧best、287max/p99、288max/p99；旧路径控制、新候选分别对原87两个基线，以及同场288/287同模型因果比较均保留。50%硬线不放宽，不能拿历史31%与新场相除。官方sidecar/额外表许可未知，ARM/官方服务器未执行，10bit方案尚未实现。
