# 真实 RAW 工作流的本地 GUI

Agent：Codex `/root`、`/root/red_workflow`；Operator：WyEhNf。基于 `19ea512cd1cbf7b6d2e73bfa295649d4c4104e61`，工作分支 `codex/camera-workflow-gui-20261023`，目标为前序 Draft #83 头分支。本阶段增加交互界面与隔离任务调度，不修改既有生产内核、固定模型和精度/性能门槛。

界面已提供，现有三家54帧结果可直接浏览。ARRI的GUI重新解码、四级映射和导出已完成实际端到端验证；RED/BRAW的新GUI解码验证在本机WSL启动故障处受阻，不能宣称整个GUI全部通过。以Draft交付这一明确边界，不把前序命令行52帧成功替代新GUI执行。

## 已实现的操作

| 部分 | 行为与主要文件 |
| --- | --- |
| 本地界面 | `gui/static/`：真实素材库、参考/原生拖动分割、参考/原生/误差模式、SDR/HDR切换、逐帧时间轴和最高10fps预览、结果选择、四级LUT、全结果误差与日志 |
| 服务 | `gui/server.py`：只监听127.0.0.1，图片按帧读取/缩小并限量缓存；一次一个隔离任务，显示真实子进程日志，保留所有旧结果和失败输出 |
| 处理 | `gui/worker.py`：复用既有变换图和固定修订78库，官方CPU解码、Log与两条四级链，262144像素分块，原生4线程/标量1线程，全已处理像素核对 |
| 导入 | 单帧.ari、.R3D、.braw；工程内目录浏览或粘贴本机完整路径；源码读取真实尺寸/帧数，首帧与完整素材分别选择，独立目录写入 |
| 导出 | 复用已验FFV1编码/完整回读脚本，四份SDR/HDR reference16/runtime8；小尺寸v3，6K使用实验v4，不增加RGB8有效精度 |
| 启动 | `start-gui.ps1`：隐藏后台服务，浏览器打开；重复启动复用现有服务，端口占用选空闲端口，实际地址/PID写入忽略目录 |
| 验证 | `gui/smoke_test.py`：既有真实PNG/接口边界模式，以及需正常WSL的真实首帧/导入/取消集成模式 |

启动及操作详见[GUI说明](../../gui/README.md)。默认本地地址 `http://127.0.0.1:8765/`；也可执行 `python -X utf8 gui/server.py --open`。服务使用NumPy和Pillow，处理工具/数据需按[上一阶段说明](2026-10-23-camera-raw-workflow.md)恢复，缺失依赖不会用旧结果冒充新运行。

预览与评价严格分开：SDR Rec.1886转sRGB预览；HDR经PQ解码、Rec2020到709及固定Reinhard映射供SDR屏查看。正常HDR画面标记“HDR→SDR预览”，不称原生HDR显示；误差图显示裁剪RGB16导出与RGB8的代码差×8，HDR标为“PQ代码差×8”。右侧MAE/max仍来自所选完整结果对未裁剪float32参考的台账，单位是误差×255的8bit等效代码值，不能当作nits/感知色差。改变预览不改变原始文件或评价数值。

四级参数只读显示，不添加无后端实现的旋钮。新任务不修改旧54帧结果；首帧结果明确标子集，总素材帧数与处理帧数分别保留。源帧率未知的单帧ARRI仅用24fps作为导出时间基，文案明确不代表源元数据。

## 实际验证与证据

环境为Windows11 / Ryzen9 8945HX，GUI Python3.13.12、NumPy2.4.6、Pillow11.1.0；WSL侧Python3.14.4、OCIO2.6.0、OpenEXR3.5.2、修订78 AVX2普通路径4线程，参考4线程、标量核对1线程。ARRI ART1.0.0 Windows CPU；导出Windows FFmpeg7.1、1线程。没有新增性能比较、完整RGB域执行或Skylake实机测试。

| 检查 | 实际结果 |
| --- | --- |
| 三家首帧×SDR/HDR×参考/原生/误差PNG | 18种均为真实RGB图像，尺寸与范围有效 |
| 接口边界 | 非法帧、无效会话、外部Host/Origin和静态目录越界共5项拒绝；连同PNG共23项通过 |
| ARRI GUI首帧任务 | `20261023-181501-c1d5d7`：官方重新解码→Log→四级链，原生/标量全像素一致；SDR/HDR×reference16/runtime8四路SHA与上一阶段同帧完全相等 |
| ARRI GUI导出 | `20261023-181626-fa5881`：四份FFV1完整回读RGB字节一致，色彩标记核对通过 |
| 交互检查 | 真实三家缩略图、ARRI运行/导出按钮、BRAW时间轴定位52/52再回首帧、分割线52%键盘调整、HDR/误差模式、工程内ARRI文件浏览 |
| 静态检查 | Python AST、JS语法、HTML ID/引用；[交付回执](../../report/data/camera-workflow-gui-v1/delivery-checks.json)另记录Markdown链接、空白、Git规范化一致及GUI/启动器/归档原始字节检查 |

公开[验证汇总](../../report/data/camera-workflow-gui-v1/verification.json)和[证据归档](../../report/data/camera-workflow-gui-v1/evidence.zip)仅包含源码快照、JSON/日志及来源SHA，不分发RAW、处理像素、视频、带素材画面的GUI截图或厂商二进制。当前源码与已执行历史源码不同处均保留快照；ARRI实跑结果内的worker SHA可在归档找回。界面截图仅保存在本地 `artifacts/gui-jobs/gui-preview.png`。

本轮实际发现并修正：首次`setsid`缺少`--wait`导致外壳过早返回，改为等待真实worker；ART默认日志改在独立job目录；参考REDline本版元数据查询可退出1，现仅该查询接受0/1并严格验证字段，实际像素解码仍要求0；新导入结果绑定回写目录、取消进程启动登记加锁/PID公布后再终止独立组、Windows WSL UTF16错误解码；修复时间轴oninput先暂停重绘导致取回旧值的问题，并在浏览器实际定位末帧验证。启动器初次把venv包装PID与实际服务PID混同的就绪检查也已纠正；中间静态语法错误和启动失败日志保留，不计成功。

## 当前阻塞与未覆盖

真实集成检查的RED任务 `20261023-182413-01a13f` 在WSL外壳启动失败，尚未进入worker/RAW解码。前一取消任务 `20261023-182406-b3eed5` 没有worker PID事件，只能证明没有被标记为处理成功，**不能声称已经实测终止了运行中的Linux进程组**。因此RED/BRAW新GUI解码、导入新素材再运行、完整52帧GUI重跑和实际运行进程组取消仍待验证。

诊断显示唯一Ubuntu实例Stopped，随后`wsl --exec /bin/echo alive`仍空输出退出1；先前输出包含`Wsl/Service/E_UNEXPECTED`。在无运行实例时执行WSL关闭后仍失败；重启WslService被Windows拒绝，需操作者管理员权限恢复。未修改WSL网络/内存配置、用户服务权限或停止其他应用，不推断为OOM或归因于取消操作。GUI显示新RAW任务暂不可用，既有结果浏览和Windows导出仍可继续。

待恢复环境后执行GUI说明中的完整集成命令，再按实际结果补充Draft。当前代码对取消/导入登记的静态修正不算已完成动态验收。前序RGB8相对float32画质误差、实验FFV1 v4、全面三倍和实际Skylake等限制保持。

## 协作与阶段交付

操作前fetch，读取#83完整正文和全部comment/review/线程，刷新全部77份完整PR正文，GUI/界面/可视化检索关联到既有issue8。#83头仍19ea512，main仍b19c5a0；既有337a3dd/876e15b8/397cc367祖先修复保留。issue7绑定修复与issue8接口/预算/实板未决事项沿前序记录继续，不修改C99核心。Discussion接口读取缺口保留，不合并或关闭事项。源记录随归档保存，最终中文PR列明本阶段提交和实际Draft状态。
