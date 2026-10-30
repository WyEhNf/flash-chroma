# 自动检测指令集与题定命令的纯C++交付

Agent：Codex `/root`、`framework_contract`、`framework_strategy`、`history_storage_audit`；Operator：本会话项目用户；日期：2026-10-30。状态：代码、当前本机构建/运行与交付完成；目标GCC13.2/真实旧CPU/嵌入式实板未验收，保持Draft。

## 目标与实现

按用户最新要求，默认hpp自行识别编译目标及可安全执行的后端，不再要求手动设置嵌入式宏或额外ISA构建参数。正式验收入口只保留main.cpp和hpp，从编译到运行使用下发main注释中的命令：

```powershell
Set-Location 'F:/Hackathon/极速焕彩测试框架/FlashChroma'
g++ -O2 -std=c++17 -o lut3d main.cpp
./lut3d ../data
```

- [目标与指令集逻辑](../../src/flash_chroma_cpp.inc)：默认freestanding、无宿主OS的ARM/AArch64/RISC-V为Embedded，Android为Mobile，其余宿主为Desktop。非x86不编译AVX2。显式TARGET或EMBEDDED宏仍是可选覆盖；冲突配置明确编译拒绝，所有翻译单元须一致。
- x86运行时先检查CPUID XSAVE、OSXSAVE、AVX三位，才执行XGETBV；再检查XMM/YMM状态与leaf7 AVX2。仅全部满足才选AVX2，其余Auto降为Scalar。新增纯特性谓词用于验证负例，不凭“i7”型号名判断。AVX2函数保留target("avx2")隔离；BMI入口另经BMI能力检查，不把扩展指令带入通用分派路径。
- [C++核心生成器](../../scripts/generate_flash_chroma_header.py)和[赛事导出器](../../scripts/install_framework.py)：同一hpp可供宿主框架和嵌入式Runtime使用；嵌入式整段裁掉宿主文件IO、拟合、自动测速和容器依赖，保留C++执行器与基础选择器。标准C++头与目标运行库仍由工具链提供。标量核保持同源数值语义，没有为外观重写整数算法，也不需要外部项目.c/.h。
- 新`--contest`入口只导出两个C++文件。默认m33、framework网格、chain_ls、单线程、DirectRGB24、BackendAuto；直表无法建立时退回相同模型Sparse，不降模型精度。原LUT读取、读图、参考、Delta与时钟8个函数文本（统一换行比较）及成功计时片段保留。联合准备仅使用本次四张LUT，第一次打开图片前完成。
- [嵌入式示例](../../single_header/embedded_example.cpp)不定义EMBEDDED或AVX2宏，依目标工具链自动识别；ROM模型与图像缓冲由调用者持有，支持分行/分块。`fc::is_embedded()`查询构建目标；像素映射为整数Q16，基础选择器仍含double，不能称整个头完全无浮点。

正式目录`FlashChroma`现仅两个源文件。上一阶段带扩展参数/脚本的完整调参工程保存到同父目录`FlashChromaTools-20261030`，没有删除原成果；其O3计时不转授给本阶段O2入口。纯C++嵌入式目录`FlashChromaEmbedded`只含同一个hpp和embedded_example.cpp。`C`、`C++`、data及原.vscode文件均未修改。详细操作见[现场指南](../framework-quickstart.md)。裸机不提供原main所用文件/容器运行库时，使用Runtime接入设备BSP；不能声称原宿主测试main可以直接替代裸机固件。

## 验证与范围

实际环境：Windows11 26200 x64 / Ryzen9 8945HX / MinGW GCC15.2.0、Python3.12.14。无全局PATH/编译器修改。正式主程序没有-mavx2、-march=native、-fopenmp、额外链接库或外部.c/.cpp编译输入。

1. [C++合同](../../tests/framework_auto_detection_contract.cpp)：64种CPU/OS必要位组合及64组无关位噪声、本机独立CPUID核对、Auto实际后端与解析像素输出；与[嵌入式合同](../../tests/framework_embedded_cpp_contract.cpp)定向CTest共2/2通过。
2. [Python合同](../../tests/test_framework_auto_detection.py)与[单hpp裁剪合同](../../tests/test_framework_embedded_cpp.py)：当前21例分别覆盖通过。首轮18通过、1项不合理的“freestanding强开宿主标准库”测试假设失败；修正该测试后只重跑它与新增2个正式导出静态合同，3/3通过，不写成一次全套21/21。无宏freestanding、host显式覆盖、bare ARM/RISC-V宏推导、非法强开、独立目录仅hpp+cpp及原8函数文本一致均覆盖。
3. [题定命令验证器](../../scripts/validate_cpp_submission.py)在正式两文件的独立副本中实际执行O2/C++17命令，仅传data路径。真实四表、四张1024×768 RGB8样图全部完成；程序输出compiled=3、available=3、actual_backend=2（AVX2）、representation=3（RGB24）、threads=1。逐图第二个Delta为1.467711/1.562505/1.592951/1.303775，与上一阶段同模型一致。源、原LUT、图片和EXE前后SHA全部一致；没有把旧O3耗时当新成绩。[原始回执](../../report/data/p16-cpp-environment-20261030/evidence/gcc15-exact.json)。首次同指令运行也原样保存，后一次用于补齐严格的构建/源/输入/二进制回执，不作性能择优。
4. 最终嵌入式示例按-ffreestanding/-fno-exceptions/-fno-rtti/-fno-builtin编译，不定义设备宏；对象nm无未定义符号。最终同一hpp的双TU仅一处IMPLEMENTATION本机链接也通过，见[最终头文本/链接合同](../../report/cpp-environment-final-contract-20261030.json)。标准库内部C链接声明不等于项目C交付接口，不能据标准stdint.h/cstring名称误判需要额外项目C源。

本机无QEMU，WSL虽有GCC15/Clang22，但透传CPU同样具有AVX2。无AVX2、OS禁YMM和bare ARM/RISC-V场景分别是必要位/平台宏逻辑验证，不是对应旧CPU、虚拟CPU或实板执行。不声明i7实机速度、ARM机器码、功耗或全局最优。

题面指定的GCC13.2已从官方release核实版本并尝试一次续传，180秒后超时，仍为不完整包；没有解压或运行，没有第二次尝试。回执保留完整预计长度、部分文件SHA和失败原因，不能把该SHA当完整发行包身份，也不能称13.2验收完成。本阶段真正使用15.2，原构建/启动参数已按题定口径验证。[工具链尝试](../../report/data/p16-cpp-environment-20261030/evidence/gcc13-acquisition.json)。

## 交付、复现与限制

同一hpp为170263B，SHA256 `1115e8e7050a3d7648fddaf08303e09e4929ea3d571bb1af94de3d2815d99315`。正式main SHA为`3c544d3af4002263687ec063e43101d0e03dcd399f5048fd9733faa51893dba7`。本机CPP ZIP 46085B、嵌入式ZIP 42826B，均只含两个C++源文件，逐成员回读通过，见[最终交付核验](../../report/data/p16-cpp-environment-20261030/evidence/final-delivery-verification.json)。源码/当前生成器与实物逐字节相同；临时测试头因Windows默认写入CRLF导致原始SHA不同的情况单独记录，不伪称其原字节相同。

可在仓库中重建新的验证副本（输出与回执路径须尚不存在）：

```powershell
python scripts/validate_cpp_submission.py --source 'F:/Hackathon/极速焕彩测试框架/FlashChroma' --compiler 'E:/mingw64/bin/g++.exe' --data 'F:/Hackathon/极速焕彩测试框架/data' --output 'F:/Hackathon/极速焕彩测试框架/Cpp-new-check' --receipt artifacts/cpp-new-check.json
python scripts/archive_cpp_environment.py --verify
```

[证据清单](../../report/data/p16-cpp-environment-20261030/manifest.json)保留最终源码、原始日志/失败原因、实际build/run参数及两套C++交付。未改C99独立交付头或RGB24热核数学；本次不是新的百图受控性能实验。下发示例实际循环四张，不能据MAX_IMAGES=100注释称跑完正式百图。最终Threshold、服务器、GCC13.2、额外Direct缓存许可及设备实板仍待验收；若规则禁止直表，可在main的Options中选择Sparse后仍用完全相同的编译指令。

本阶段基于#103头`04a0e8b2868df6ec9c88a3d3c2468b2e11263e79`，对应实现/归档提交以本PR提交列表为准。发布前按AGENTS核对相关PR正文、完整意见/线程及已知事项；#96旧验证/目录绑定两项P2不由本阶段修复，#8实板/接口待办与Discussion4读取缺口继续保留，不合并或关闭事项。
