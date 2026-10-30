# 16题精确16bit直接ID：完整质量通过，性能待测

Agent：`/root/tail`；任务：精度方向；状态：正确性完成、速度与真实内存峰值未完成。保持Draft，不切换默认。

后续正式[六角色性能阶段](2026-10-24-p16-direct-u16-perf.md)已完成：两新模型有效最劣31%–34%，严格低于50%拒绝本实现。以下保留质量阶段当时的范围；质量通过不等于综合升级。

第二级两只固定候选已在[模型阶段](2026-10-24-cinema-second-nodes.md)验证mean/p99/max，但整个cache有603/703种颜色，冻结87不能建立旧8bit直接表。本阶段保留模型节点、轴、sidecar和逐级RGB8语义，从87另建revision287。旧8bit成功时完全优先；否则整个cache palette≤65536且原完整域证明成立时，一次首级AVX编译生成uint16 ID与动态RGB32 palette。超过阈值保留精确fallback。没有实际可达集合第二遍，没有读取gold或历史输出构造运行时。

主要源为`experiments/p16-direct-u16-runtime/`，预注册为`experiments/p16-direct-u16-plan-v1.md`，冻结与验收为`scripts/check_direct_u16_native.py`。format16与新增96B Info明确区分旧format9；通用快照接口的entries是原始u32词数8,388,609，实际输入项数仍16,777,216。真正uint16数组另有4B owned guard；末地址scale2 gather多读2B在guard内。标量读取合法u16对象；AVX2仅声称已验x86小端，不声称ARM可移植。新vector保证2B对齐，本场两个实际地址mod64均0；独立guard测试特意使用mod64=60。旧87的对齐分配器不同，未来速度差不能只归因位宽。

环境为Windows11/AMD Ryzen9 8945HX、GCC15.2、CMake Release、C++17、AVX2/BMI既有后端、OpenMP1/4线程，Python3.12.14/NumPy1.26.4；质量执行时与其他质量任务共享host，不计性能。无AVX512。第一次构建因同一TU重复包含两份历史结构头失败，保留v1冻结源和失败日志；移除多余include后冻结v2，构建通过。归档工具第一次对旧基础文件做Git逐字节检查时发现CRLF差异，改为明确记录actual/Git双SHA和仅换行等价，未重跑像素。前置源表漏列的两个基础C/头文件由实际编译`.d`补入ZIP，逐a083aeab Git内容补核，不冒称这两项已在前置清单单独冻结。

|对象|format|完整域配置|全域/照片差异|模型容量B|新表/调色板B|
|---|---:|---:|---:|---:|---:|
|287 max_first|16|6|0|35,495,456|33,554,436 / 2,412|
|287 p99_first|16|6|0|35,495,856|33,554,436 / 2,812|
|287旧best|9|6|0|18,715,824|旧8bit16,777,216 / 内联|
|冻结87旧best|9|6|0|18,715,680|旧8bit16,777,216 / 内联|

每六配置覆盖scalar/1、AVX2/1、AVX2/4与原地/真分离，逐字节比较既有独立oracle。三只287模型各100图×两路径共600输出，全部相等，既有精度收益及逐图代价完全继承模型阶段。旧best新增144B仅为Handle/诊断元数据，不能由此推断速度不变。max/p99临时峰诊断分别34,435,724/34,436,124B，包含最终表、palette和临时ID；不含已驻留模型/cache，不能冒充进程RSS。新增内核`.su`为48B，编译核448B、OMP outer144B；这些静态帧不包括所有上层栈/OpenMP运行时，未测真实RSS峰值。

有限合同全部通过：真实255色旧8bit、256色wide；整cache165,677色精确回退与非四级回退；65535 ID保真、65536拒绝；独立子进程的最后输入0xffffff、恰好24B源/目标后接不可访问页及表末guard；729短模式/后端组、8诊断拒绝、每模型11无效分离范围拒绝。分配失败尚未注入，未用正常执行冒充覆盖。

证据见`report/data/p16-direct-u16-native-20261024-v2/`：9份原件、67项实际源码、13个模型路径成员、编译依赖/参数/栈/失败日志、独立矩阵和SHA复核。DLL SHA为`5ec24854848159541c55f58aff831bec5de401d794cf3dfe3fddf64e3ebcb508`，冻结v2清单SHA为`f32220b758c0adc8705089073718d7537e8303a8622616dd47bf92a893085e47`。

复现：先运行`check_direct_u16_native.py --freeze --cache-root F:/Hackathon/projects/16-lut-color --output <新冻结目录>`；以本阶段CMakeLists配置MinGW Release，构建`jshc_direct_u16 p16_direct_u16_contracts`；再运行同脚本，提供`--frozen <清单> --library <DLL> --contracts <EXE> --cache-root ... --output <新验收目录>`。具体实际构建参数见build-evidence.zip的compile_commands/CMakeCache。归档与独立核对使用`archive_direct_u16_native.py --output <新目录>`，不会重跑映射。

下一步是预先冻结六角色同场性能：87/287各a399及旧best、287两新候选，保留两个老路径控制；新候选分别对87a399、87旧best和287旧best报告最劣保留率、全部10%档与50%硬线。尚无速度通过结论，新增约16MiB表内存是明确代价；sidecar/额外表官方许可仍未知。
