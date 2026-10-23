# 三家真实 RAW 的四级 LUT 工作流验证

Agent：Codex `/root`、`/root/red_workflow`；Operator：WyEhNf。基于提交 `4dc79c5d00c787a71ad392e634a78b48924e3abe`，工作分支 `codex/camera-raw-workflow-20261023`，交付目标为前序 Draft #82 的头分支。本阶段验证现实工作流的适用性，没有修改生产运行时、旧模型、完整 RGB8 精度门槛或三倍性能门槛。

三家共 54 帧真实 RAW 已完成完整分辨率解码、Log、调色及 SDR/HDR 两条四级 LUT 链。每条输出分支覆盖 **1,128,231,168 像素**，原生与同模型标量结果全部逐字节一致。**相对解析 float32 参考的误差非零，当前 RGB8 链不能据此通过高精度 SDR/HDR 画质验收。** 原生调用均走普通 AVX2 fallback，旧照片场次的专用直接表加速没有触发。

最终台账见 [summary.json](../../report/data/camera-raw-workflow-v1/summary.json)，源材料身份见 [source-manifest.json](../../report/data/camera-raw-workflow-v1/source-manifest.json)。模型、配置、逐帧指标、工具日志、失败记录和执行时源码快照按原字节保存在 [evidence.zip](../../report/data/camera-raw-workflow-v1/evidence.zip)，成员 SHA 见 [manifest.json](../../report/data/camera-raw-workflow-v1/manifest.json)。第三方 RAW、解码/调色像素、视频、SDK 和工具二进制仅保留在本地 `artifacts/camera-raw-workflow-v1/`。

## 素材与真实解码边界

| 素材 | 实际相机/尺寸 | 帧数与帧率 | 实际解码输出 |
| --- | --- | --- | --- |
| ARRI 官方 FTPS 单帧 `L001C028_140110_R6MS.0018267.ari` | Alexa Plus 4:3 XT / ALEV III，2880×1620 | 1，24 fps | ART CMD 1.0.0 Windows CPU，AWG3/D65/linear，EXR ZIP float32；OCIO 再编码 LogC3 EI800 |
| Blackmagic 官方图库《The End of the World – Train》 | Pocket Cinema Camera 6K，6144×3456 | 完整 52，25 fps | 官方 BRAW SDK 3.3 API，经 MDK 公开再分发；WSL CPU / AVX2 / 4线程，Gen5 Film / Blackmagic Design gamut，关闭 post LUT，RGB float32 |
| FFmpeg 原始 R3D 测试样例 `F099_C001_0317IH.R3D` | EPIC-X / DRAGON 6K S35，6144×3160 | 1，元数据仅打印 `23.976` | 官方 REDline 65.0.22 / R3DSDK 9.1.1，WSL CPU 4线程，全分辨率 RWG / Log3G10 TIFF16，再归一化 float32 |

ARRI 与 RED 都只有一帧，不代表连续运动片段性能。RED 来自公开 FFmpeg 样例库；当前 RED 官方样片页要求登录，未绕过登录。工具仍使用官方 REDline。RED 成功命令沿用源元数据的色彩版本 2（FLUT），显式指定 RWG / Log3G10，**没有声称 IPP2 解码**；TIFF16 → float32 → uint16 的 58,245,120 个通道代码值全部可往返，但参考起点已经是 Log TIFF16，不能称为未量化的原生 float32 解码。`23.976` 不能证明精确帧率为 24000/1001。

BRAW 的部分去马赛克在相机内完成，剩余处理由官方 SDK 完成，不把 BRAW 说成未经任何相机预处理的 Bayer 平面。SDK 3.3 是本次实际版本；当前官网 SDK 6 下载要求填写身份资料，本次没有虚构注册。ARRI Linux 包下载 403 后改用官方 Windows 包。三家素材与衍生像素不随仓库分发，不假定具有公开再发布许可。

来源：[ARRI 样片](https://www.arri.com/en/learn/camera-systems/camera-sample-footage-reference-image)、[ARRI Reference Tool](https://www.arri.com/en/software/postproduction-software/arri-reference-tool)、[Blackmagic 图库](https://www.blackmagicdesign.com/products/blackmagicpocketcinemacamera/gallery)、[BRAW API 3.3 再分发](https://sourceforge.net/projects/mdk-sdk/files/deps/braw/)、[MDK 头文件](https://github.com/wang-bin/mdk-braw/tree/0cd1517ed9d720d416afa2d65e0a80a045096ce4)、[FFmpeg R3D 样例](https://samples.ffmpeg.org/r3d/F099_C001_0317IH.R3D)、[REDline 官方安装包](https://downloads.reddigitalcinema.com/software/redline/linux/beta/65.0.22/REDline_Build_65.0.22_Installer.sh)。精确哈希在最终来源清单；ARRI 公开 FTPS 访问信息没有落盘。

## 四级链路与三种结果

空间去马赛克及摄影机 Log 编码在四级逐像素 LUT 之前。每个输出分支依次执行：

1. 摄影机 Log / gamut → ACEScct。
2. ACEScg 中 +0.25 档曝光及 RGB 增益 `[1.02, 1, 0.98]`，返回 ACEScct。
3. ACEScct 中以 18% 灰（0.4135884024924423）为中心的 1.08 对比度和 0.92 饱和度，CDL 不夹紧。
4. ACES 2.0 输出变换：SDR Rec.1886 / Rec.709 100nit，或 HDR Rec.2100-PQ / Rec.2020 1000nit。

这是可复现的全局示例调色，不是逐镜头人工调色。双输出共享前三种变换，因此每家需要五份不同 LUT，三家合计七份唯一模型；每条实际运行链仍为四级。配置固定为 OCIO 2.6.0 内置 `studio-config-v4.0.0_aces-v2.0_ocio-v2.5`，不随默认配置升级。生成配置与 LUT 附 OpenColorIO 及 Config-ACES 的许可声明。

解析 float32 参考在阶段间不裁剪、不量化；第二套结果使用各阶段独立均匀采样的 33³ float CUBE / 四面体插值；第三套使用节点 RGB8 的 33³ SLUT，Log 输入和每级输出均遵守既有 RGB8 契约。没有把两个输出合成单个 LUT，也没有烘焙完整 256³ 派生表。七份 CUBE 的全部 35,937 节点序列往返检查均通过，不能以此替代插值精度验收。

## 精度结果与实际快速路径

下表是整帧所有通道对**未裁剪解析 float32 输出**的 MAE / 最大绝对误差，单位统一为归一化误差 ×255 的“8bit 代码值”。HDR 的 PQ 代码值误差不是 nits，也不是感知色差。

| 素材/输出 | RGB8 原生 MAE / max | float33 CUBE MAE / max |
| --- | ---: | ---: |
| ARRI SDR | 1.5710 / 14.7978 | 0.2313 / 6.1473 |
| ARRI HDR | 0.7341 / 4.1297 | 0.0650 / 0.7114 |
| Blackmagic SDR | 1.2989 / 24.5284 | 0.1713 / 24.0081 |
| Blackmagic HDR | 0.8308 / 10.0054 | 0.0589 / 12.1201 |
| RED SDR | 1.7600 / 60.2478 | 0.3961 / 60.3352 |
| RED HDR | 0.8311 / 41.3630 | 0.1495 / 42.4778 |

六个分支的 native / scalar 均零字节差，只证明相同离散模型语义不变。RGB8 输入、节点和逐级量化均与高精度参考有差异；33³ float LUT 也存在局部峰值，不能把全部误差只归因于 8bit。参考前三阶段实际范围及越界通道数见归档 `quality-diagnostics.json`；BRAW 有少量负 ACEScct，RED look 有一个负通道样本。模型节点还有更多负值/超1值；均匀域采样、节点裁剪和非线性插值都需要独立研究，本次没有隔离每项的因果贡献。

参考 RGB16 文件会在最终写盘时裁剪到 [0,1] 并量化。解析 SDR 输出大于1的通道样本数为 ARRI 9,860、BRAW 7、RED 541；不能把上表未裁剪误差称作导出文件之间的误差。BRAW 和 RED 台账另有 `runtime_vs_export16_error`；ARRI 原执行版本未记录这一单独口径，未补造。超范围计数单位为通道样本，不能称为像素数。

使用历史四线程最好候选修订78，库 SHA256：`51ed7ccd99817c61e89487db8f4afe1970932f637050515ae937280c0cd1532b`。所有新链的 sidecar 均为 NULL，cache / domain / palette / direct / ANDN split 特化均未启用；实际运行普通 AVX2 路径。每链四份 SLUT 合计 448,252B，普通新模型不能满足旧照片链的共享前缀和预算条件。不能将旧场次修订78的 2.525664× 套到本次，更不能称同版已达到全面三倍。

## 环境、覆盖与计时

本机为 Windows11 / Ryzen9 8945HX，映射在 WSL2 Ubuntu Linux6.18.33.2 / GCC15.2 / Python3.14.4，NumPy2.4.6、OCIO2.6.0；OpenEXR3.5.2 / tifffile2026.10.15 分别读取 ARRI / RED 中间格式。自研库为既有 AVX2/BMI1 门控版本，未使用 CUDA。BRAW 显式选择 CPU/AVX2，OCIO 默认 CPU 路径的具体 ISA 本轮未独立审计。**没有实际 Skylake 服务器结果。** ART 解码在 Windows，RED/BRAW 解码及映射在 WSL，视频导出有 Linux / Windows 两个 FFmpeg 版本，不能跨环境推断加速。

ARRI 整帧执行一次；BRAW/RED 用 262,144 像素 tile 全覆盖，分别每帧81/75块。参考使用4个 Python 工作线程调用释放 GIL 的 OCIO API；七个变换在 262,144 像素探针上对串行/并行 float32 字节核对通过。原生每 tile 4线程，标量每 tile 1线程，只作正确性验证。BRAW 52帧 RAW 解码一次完成；后续四级映射因用户中断分39+13帧执行，续跑前核对全部39份已完成输入及156份输出 SHA，原检查点和中断片段保留，不称单次连续性能场次。

| 素材 | SDR 原生 apply 秒 | HDR 原生 apply 秒 |
| --- | ---: | ---: |
| ARRI 1帧 | 0.012138 | 0.012810 |
| BRAW 52帧 | 4.129188 | 4.162036 |
| RED 1帧 | 0.076722 | 0.075549 |

这些是本地单次诊断调用之和，仅计原生 apply，排除 Python 缓冲拷贝、Log→RGB8量化、解码、I/O、编码、标量核对。回放包含两条替代实现和验证，并曾有辅助任务活动；没有受控 A/A、ABBA 重复或稳定频率保证。表格不是端到端生产 FPS、相对修订23性能结论或 Skylake 成绩。ART 进程wall约0.952s；BRAW解码并写盘60.538s，其中写盘回调58.423s，差值不能推断纯去马赛克时间；RED成功命令没有独立生产wall计时。

## 输出与复现

本地每家输出 SDR/HDR × reference16/runtime8 四个 FFV1 MKV。ARRI、RED及BRAW SDR用v3；BRAW HDR因本机v3内存分配失败，改用**实验FFV1 v4**完成像素导出验证，不能当作已验收的生产容器兼容性。存储格式为全范围 `gbrp16le`、RGB identity matrix；参考有效16bit，原生有效8bit，装入16bit容器不会恢复损失的精度。SDR信令为BT709 primaries/TRC，显示输出变换采用Rec.1886；HDR信令为BT2020/PQ。没有额外的HDR母版显示器/MaxCLL元数据或校准显示器验收，不把这些验证文件当作广播交付母版。

ARRI 在 `video-arri-v2/`（Linux FFmpeg7.0.2）；RED 在 `video-red-v2/`（Windows FFmpeg7.1）；BRAW 在 `video-blackmagic-v1/`（首份复用Linux已完成编码，Windows完整回读，后续Windows编码；SDR编码/回读1线程，HDR 2线程）。回执中 `reused_existing_encode=true` 的 `command` 是未执行的备选命令，实际旧编码参数看同目录原始 encode.log 与冻结脚本。已完成检查点续跑时复核当前原RGB串联SHA和视频SHA，保留原完整回读回执及其来源SHA，不反复解码已验证视频。每个最终视频均曾解码回原输入 RGB 格式，验证所有帧、长度与串联 SHA 完全一致，再核对色彩标记；每份输出的文件 SHA 与执行日志均单列。

此前 TIFF/EXR 不支持、OCIO CDL 构造API误用、Linux包403、BRAW整帧大数组进程异常结束、FFmpeg原色矩阵选项名称及Windows色彩标记丢失均保留失败证据。WSL重负载编码/回读曾异常结束，没有可证明的OOM诊断，不声称已确认根因。之后采用串行Windows进程并限制线程，BRAW HDR v3仍分别在24帧和队列限额后的2帧报`Cannot allocate memory`，不是完整输出，原文件/日志保留。[FFV1源码](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1/libavcodec/ffv1enc.c)的v3最坏包预分配为宽×高×37×4，6K时截至约2GiB；v4使用宽×高×3×4，BRAW约255MB。后续HDR使用v4及输入/输出队列限额1，仍做完整像素验证，不声称已隔离Windows全部内存分配机制。Windows7.1需用 [setparams](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1/doc/filters.texi)同步帧色彩属性，本地小探针和完整实际输出验证通过；它不改变像素值。失败输出不算入最终12份。

最小复核不需要下载第三方像素或运行库，在仓库根目录执行：

```powershell
python -X utf8 scripts/archive_camera_raw_workflow.py --verify
```

完整像素回放需要先按 `source-manifest.json` 恢复原素材和工具，遵守各自许可。归档内 `red-input-verification.json` 有成功 REDline 完整 argv、cwd 和动态库路径；`arri-decode-v3.json` 有成功 ART argv；BRAW源码 `decode_braw_cpu.cpp` 固定CPU/AVX2/4线程，编译时使用 MDK 上述提交的 SDK3.3 头文件、`BRawAPILoader.cpp` 与 `Variant.cpp`，宏 `BRAW_VERSION=330`，运行时使用本地 API3.3 和私有 libc++18。不是安装系统驱动/全局库。Python运行环境需OCIO2.6.0、NumPy2.4.6、OpenEXR3.5.2、tifffile2026.10.15；Linux扩展置于忽略目录 `artifacts/camera-raw-workflow-v1/linux-site/`。原生修订78库需按前序 [ANDN split阶段](2026-10-21-skylake-andn-split.md)恢复固定 SHA，不能用最新修订替代。

已有输入和库时，以下在WSL仓库根目录执行；输出必须使用新目录，避免覆盖原证据：

```bash
python3 experiments/camera-raw-workflow/pipeline.py bake --output artifacts/camera-raw-workflow-v1/models-repro
python3 experiments/camera-raw-workflow/pipeline.py run --models artifacts/camera-raw-workflow-v1/models-v2 --camera arri --reference-threads 4 --output artifacts/camera-raw-workflow-v1/run-arri-repro
python3 experiments/camera-raw-workflow/stream_pipeline.py --models artifacts/camera-raw-workflow-v1/models-v2 --output artifacts/camera-raw-workflow-v1/run-braw-repro
python3 experiments/camera-raw-workflow/stream_pipeline.py --camera red --camera-manifest artifacts/camera-raw-workflow-v1/red-camera.json --models artifacts/camera-raw-workflow-v1/models-v2 --output artifacts/camera-raw-workflow-v1/run-red-repro
```

冻结策略的 RED 项保留最初 `pending_source`，实际成功来源由 `red-camera.json` 补充并以 SHA 绑定，不修改已烘焙模型的策略身份。`models-v2/manifest.json` 记录的是原执行绝对路径；异机恢复时需按仓库相对位置放置模型并显式处理路径，不宣称孤立克隆可直接运行原始绝对路径回放。当前源码与实际执行历史版本不同处均留有快照，逐项绑定见 `tool-source-inventory-final.json` 和各回执。

导出示例（Windows，Python需UTF8模式；实际FFmpeg路径按清单恢复）：

```powershell
python -X utf8 experiments/camera-raw-workflow/encode_outputs.py --run artifacts/camera-raw-workflow-v1/run-red-v1 --ffmpeg artifacts/camera-raw-env-v1/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe --threads 1 --context 0 --output artifacts/camera-raw-workflow-v1/video-red-repro
python -X utf8 experiments/camera-raw-workflow/audit_results.py --run artifacts/camera-raw-workflow-v1/run-arri-v1 --run artifacts/camera-raw-workflow-v1/run-blackmagic-stream-v1 --run artifacts/camera-raw-workflow-v1/run-red-v1 --video artifacts/camera-raw-workflow-v1/video-arri-v2 --video artifacts/camera-raw-workflow-v1/video-blackmagic-v1 --video artifacts/camera-raw-workflow-v1/video-red-v2 --output artifacts/camera-raw-workflow-v1/summary-repro.json
```

## 审计与尚未完成的目标

独立只读审计 [agent-final-audit.json](../../report/data/camera-raw-workflow-v1/agent-final-audit.json)通过553项，复算322组误差台账、核对216份RGB输出长度及39+13续跑身份；它不重复像素映射或视频解码。最终原始导出回执和独立 `audit_results.py` 汇总补齐12份视频。JSON/AST、链接、空白、ZIP CRC/SHA和冻结暂存blob检查见 [verification-final.json](../../report/data/camera-raw-workflow-v1/verification-final.json)。

交付静态检查首次把保留原字节的Windows CRLF误报为行尾空白；为该证据目录补充Git `cr-at-eol`属性后重新检查，不归一或改写原始回执。最终交付检查回执在ZIP生成之后独立发布，避免自指哈希。

操作前核查前序#82的完整正文、comment/review/审查线程、全部现有PR正文及相关issue7/8；源记录保留在归档 `remote-initial.json` / `remote-final.json`。既有337a3dd、876e15b8、397cc367修复祖先保留，issue7绑定问题已含修复；issue8接口、预算、实板等未决项继续保留。Discussion接口无法读取的缺口明确记录，没有据此执行合并或关闭。本阶段以Draft交付，提出PR不代表已审查或合并。

本次最重要的新结论是：真实素材可完整通过既有离散运行时，但其精度契约和照片专用快速路径不能直接满足高精度HDR工作流。后续需要独立设计更高精度I/O/中间结果、合理域/shaper及采样误差控制，并在这些新模型上重新做性能与画质验收。当前没有实现这些改变，也没有完成同版全面三倍或实际Skylake验收。
