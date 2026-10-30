# 赛事入口接入连续性能偏好与硬预算

Agent：Codex `/root`、`framework_strategy`、`framework_contract`、`history_storage_audit`；Operator：本会话要求“接入”的项目用户；日期：2026-10-30；状态：本机开发、验证与交付完成，Draft，正式赛事条件仍待验收。

## 目标和实现

此前 hpp 已有 `fc::select`，赛事 main/run.ps1 只能手填 m/表示。本阶段将连续 A/B/C 偏好实际接入赛事入口：读取本次四张 LUT，生成候选，核对完整RGB域质量与实际后端输出，按需要校准无图片的合成速度，调用选择器，再固定一个计划运行整批图片。权重各在0..1且非全零，先满足硬约束，再在Pareto前沿上按归一化权重选型。连续的是偏好，执行计划仍为离散候选。

- [preference_selection.hpp](../../framework/preference_selection.hpp)：现场候选、完整域原表参考与Scalar对照、单线程合成校准、前后A/A、拒绝原因、所选模型/资源与JSON。四级 m 可分别指定，固定网格/拟合/后端按请求使用。候选默认Sparse/RGB24，U8/U16可以显式加入，容量拒绝按候选保存而不阻断其他可用模式。
- [安装脚本](../../scripts/install_framework.py)：主机单hpp聚合、C++长选项、PowerShell参数、报告新文件保护、选中后重新prepare并比对实际Info/预算；框架节点副本用新vector交换，避免选小m仍保留旧m33的capacity。图片文件长度预检也移到选型完成后，选型连图片文件都不打开。原手动路径保留，`auto`仍表示结构证明，不借此悄悄自动搜索。
- [现场指南](../framework-quickstart.md)：参数、默认候选、计量口径、拒绝与复现命令。偏好模式使用CandidateSizes/Modes替代位置参数m/mode，Grid/Fit/Backend继续生效。CLI默认17/25/33三个统一m，也可指定混合m或缩小集合。
- [轻量C++合同](../../tests/framework_preference_contract.cpp)、[Python入口合同](../../tests/test_framework_preferences.py)、[真实框架验证器](../../scripts/validate_framework_preferences.py)、[归档脚本](../../scripts/archive_framework_preferences.py)：分别覆盖评分/预算/小模型输出、真实解析/单hpp自包含、真实四表四图与手动入口、原字节证据。

对应实现与归档提交见本阶段PR提交记录；基线为 `c192a340e8e01d2a6d01cfc35dc39443c9802207`。原 core.hpp SHA仍为 `9e5fa9ac474c6f9f60c05c19ad859353bf9b6fe88983cc01c3bee21cf1e11953`，没有更改RGB24热核、C99数值核心或旧历史计时。

交付期间维护者通过[#101](https://github.com/WyEhNf/flash-chroma/pull/101)将研究栈合入main `7811144ceb3fe5f2d81c76d370a06d1d89134f4e`。已fetch并读取该PR正文及完整意见，确认它与上述基线在framework/src/include、安装器、旧部署脚本、single_header/CMakeLists及AGENTS均无差异。本阶段分支同步该主干后直接向main提交PR；不把维护者的合并记作本Agent执行，也不跨源码差异继承测试。[刷新记录](../../report/framework-preferences-remote-refresh-20261030.json)保留完整读取内容。

## 使用方式与适用范围

用户原 `FlashChroma` 目录已更新，仍只有一个聚合hpp。可运行：

```powershell
Set-Location 'F:/Hackathon/极速焕彩测试框架/FlashChroma'
.\run.ps1 -Preference '0.6,0.3,0.1' -Grid framework -Fit chain_ls -SelectionReport 'selection.json'
```

已编译EXE可直接改参数而不重编译，例如：

```powershell
.\main_flash_chroma.exe '..\data' 33 auto auto framework 4 chain_ls --preference '0.2,0,0.8' --candidate-sizes '17;33' --max-runtime-mib 1 --selection-report 'compact.json'
```

`MaxMeanError`约束均匀完整RGB域的mean，`MaxPixelError`约束该域max。前者不是正式逐图阈值；后者才对任意图片mean提供保守上界。底层兼容字段worst_image_mean在此存完整域max上界，JSON明确不是照片实测值。`MaxMsPerMP`只约束固定算法合成输入、fresh输出分配+apply的毫秒/百万像素，不能当作正式图像TimeCost承诺。

`MaxRuntimeMiB`限制所选运行器的自有容量记账：模型、arena、对象、框架节点副本、shared管理估算；`MaxWorkspaceMiB`单列运行工作区。sidecar是对象内子集，不重复累计。这些均不是RSS、精确分配器开销或准备峰值；原框架密集参考表/图片、原始uint16表、候选/拟合/校准暂态另计。其它候选与暂态在选型返回前释放，返回结果在最终prepare复核后释放。公开C++选择模块默认只含m17/33，CLI默认含m25，避免混写默认值。

速度权重0且无时间预算时跳过计时，结果的时间资格仍未验证；否则各候选两次预热、前A/A、正式重复、后A/A，默认5次、漂移上限5%。默认剔除不稳定时间；显式AllowUnstableTime才允许provisional选择，未测时间仍不能豁免。无可行或非法请求时明确非零退出，不退回超预算档。无缓存标定复用、无图间或同一批次中热切换；每次启动会重新准备。当前两m实际选择进程约22～27秒，含LUT读取、拟合、完整域检查及四图参考等，不能把这个墙钟当映射耗时。

## 实际环境、验证与结果

实际 Windows11 26200 x64、Ryzen9 8945HX、MinGW GCC15.2.0，C++17 Release/O3、静态链接、OpenMP关闭；Python3.12.14，psutil5.9。真实集成的算法AVX2单线程，子进程绑逻辑CPU16；无锁频/独占保证，固定合成校准不是跨候选随机化的受控优化比较。

1. 新增C++定向CTest 1/1通过，2409项合同：任意连续分界权重、归一化、硬预算优先、无解/非法请求、人工时序漂移门控、选中小型Stage的257像素独立解析输出；不读取赛事图片或执行性能测量。
2. 新增Python32/32通过，含仅复制一个hpp的独立临时目录编译、实际GLOBALS解析、NaN/Inf/负数/全零权重、预算/重复/未知选项及报告路径保护。首次默认G盘temp权限拒绝，fixture未能执行，改用工作树内新basetemp后通过；首次失败经过记录在测试回执中，未单独归档完整pytest失败输出，通过场日志保留。
3. 原框架相关Python28/28回归通过。生成源码中7个原加载/参考/色差/时钟函数逐字相同，成功apply计时片段逐字保留；输出申请仍在计时内，图片预检在选择之后。聚合头与生成来源逐字匹配、无私有工程include。
4. [真实四表集成](../../report/data/p16-framework-preferences-20261030/evidence/integration/summary.json)8个独立进程全部达到预期状态：三种偏好、各自所选配置的手动运行、零RAM无解、非法权重早拒绝。三种成功选择的实际表示均通过每候选完整16,777,216输入与Scalar逐字节核对；四图Delta与对应手动配置逐项相同。全部输入、源码和EXE前后SHA一致。

| 实际偏好 | 本场选中 | 完整RGB域mean | 自有容量记账B | 时间资格 |
| --- | --- | ---: | ---: | --- |
| `1,0,0` | m33 Sparse | 0.6956392451 | 1,472,479 | 未请求时间，provisional不代表质量失败 |
| `0,0,1`，1MiB上限 | m17 Sparse | 1.1004212857 | 230,751 | 未请求时间 |
| `0,1,0` | m33 DirectRGB24 | 0.6956392451 | 51,804,191 | 前后A/A通过，provisional=false |

本场四个速度候选前后A/A漂移0.0592%～1.2399%，均在5%内；选中m33 RGB24的合成结果为7.059733ms/MP。这是该固定合成输入、当前机器和本次运行的选型观测，不是正式照片速度或与历史最好版本的加速比。原四图m33逐图mean为1.467711/1.562505/1.592951/1.303775；m17为2.305356/2.354718/2.152527/2.421103，不混写完整域mean。

5. 另外实际执行PowerShell偏好入口：m17 Sparse、sample、1MiB限制、JSON输出及原四图成功；独立probe目录编译，不替换集成场的已计量二进制。交付使用的仍是上述集成EXE。

复现真实场：

```powershell
python -X utf8 -u scripts/validate_framework_preferences.py --exe 'F:/Hackathon/极速焕彩测试框架/FlashChroma/main_flash_chroma.exe' --data 'F:/Hackathon/极速焕彩测试框架/data' --output artifacts/preferences-new-run --affinity 16 --fit chain_ls
python scripts/archive_framework_preferences.py --verify
```

输出目录必须为新目录。固定输入不齐或CPU16不存在时应改为实际可用环境，并登记新身份。完整原始JSON、逐候选AA/正式样本、stdout/stderr、失败回执和源码见[归档清单](../../report/data/p16-framework-preferences-20261030/manifest.json)。

## 交付与边界

聚合hpp为167,856B，SHA256 `9b4b6650bbbc0985a6ab1afc4c99aaf0bfe8b098a809ee00f067161988923cda`；EXE SHA256 `2a750aaca11435edf7c284d0ffcdd86b73d59d90ec47f96a8a5bce678ad04aa2`。ZIP为841,454B，逐成员回读通过；[交付收据](../../report/data/p16-framework-preferences-20261030/evidence/delivery-package-receipt.json)绑定实际EXE、源头、ZIP及备份路径。导入仅Windows系统DLL，无MinGW/OpenMP DLL依赖。旧FlashChroma已完整备份到同框架目录下 `FlashChroma-before-preferences-20261030`。

打包首次在PE工具本地化输出的UTF8解码处失败，保留中止回执；随后按原始字节读取并只解析ASCII DLL名，完成核验。没有因此重编译、修改算法或补跑性能择优。源码/模型FNV只作本次进程内指纹，归档与实际交付另以SHA256绑定，不接受外部目录指标继承资格。

本阶段接通的是连续偏好、预算与赛事入口，未实施历史审计中其它非均匀网格、全链离散优化、分输出坐标或精确对象共享策略。正式阈值/目标服务器、规定GCC13.2、额外Direct缓存许可与实板仍待验收；无Direct许可时可将CandidateModes收窄为sparse。主机框架聚合头仍含标准库/拟合/异常，不是裸机零堆交付。

创建PR前读取并刷新#95/#96/#99/#100正文、完整评论/reviews/行内线程及#7/#8全文/评论，均无新增意见，另检索相关更新记录。#96旧verify编排/目录绑定两项P2仍未修复；新入口现场生成证据、不读旧目录，不把绕开称作修复。#7既有修复仍为祖先，#8接口/实板继续保留，Discussion4缺少可用读取接口的缺口不作无阻塞结论。[本轮协作快照](../../report/data/p16-framework-preferences-20261030/evidence/collaboration.json)和[独立静态审查](../../report/data/p16-framework-preferences-20261030/evidence/review.md)可核对。按[AGENTS阶段规范](../../AGENTS.md)提交工作分支及Draft PR，不合并或关闭议题。
