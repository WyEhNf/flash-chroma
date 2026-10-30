# 2026-10-29 照片工作台与赛前调试集成

Agent：Codex /root（studio_backend、studio_review、studio_smoke 并行协作）

Operator：本会话授权开发、优化和整合的用户

Task：给当前单头版本提供精细前端，并整理为次日赛事可快速换数据、调参和排错的交付物

Status：本机功能集成；正式协议、Threshold、目标机及旧入口待修复事项仍保留

## 目标与本阶段变化

本阶段基于 `fb7e195215f14df9f635394d75cde0e0e69c82c9`，实现提交为 `b3d9dab022098971e1e9b06ed1e9126ab86184ed`，工作分支为 `codex/p16-studio-ui-20261028`，目标是 PR #95 的分支。没有修改 `.hpp/.h` 的数值核心，也没有重新宣称已消除上一阶段性能差距。

| 方面 | 完成内容 | 主要文件 |
| --- | --- | --- |
| 可视化操作 | 三栏照片工作台，原图/结果分割、差异显示、缩放平移、四级启停/强度、连续偏好、实际配置和原尺寸PNG导出；请求在用户意图变化时立即失效，避免旧结果覆盖新参数 | `gui/static/studio.html`、`studio.css`、`studio.js` |
| 代表素材 | 20张照片覆盖人物、风景、城市、暗光、日常色彩和纹理；18份真实Striped Purple CUBE，15套创意组合及2套固定Cinema模型 | `gui/studio_catalog.json`、`scripts/prepare_studio_catalog.py` |
| 真实计算 | 创意组合实际生成稀疏模型并调用单头CPU库；固定Cinema显示真实四级模型；每次核对独立C99，参考缺失时明确没有精度资格 | `gui/studio.py`、`gui/server.py`、`tests/test_studio.py` |
| 赛前入口 | `init / doctor / fit / run`，四张新密集LUT来源绑定、混合m重新拟合、配置路径定位、逐图流式运行、严格mean门、失败保留及不覆盖输出 | `scripts/p16_event.py`、`tests/test_p16_event.py`、`start-event.ps1` |
| 批次门禁 | 无limit时图数必须等于expected_images；doctor数量不符未就绪；只有无limit且实际=expected=100才标competition_size_batch；任何显式limit均是调试子集 | 同上 |
| 接口适配 | 只依赖hpp和C++17的连续RGB8读写示例，固定四级、可选sidecar、参数/长度/溢出及覆盖拒绝；准备、映射、I/O和wall分列 | `single_header/event_run.cpp`、`single_header/CMakeLists.txt` |
| 本机交付 | 隐藏启动、源码/库身份匹配才复用服务；明确Python覆盖路径；打包源码、样例、模型、实际DLL/EXE及MinGW依赖，逐成员SHA校验 | `start-gui.ps1`、`scripts/package_p16_event.py` |

用户使用入口为[赛前指南](../event-quickstart.md)和[工作台说明](../../gui/README.md)。创意工作台导出的JSON不能直接充当正式竞赛配置；赛事入口对此显式拒绝。连续偏好映射到支持的网格/执行方案，界面如实说明创意组合采用参数策略，没有给这些组合赋予已测Pareto最优资格。

## 实际环境与身份

- Windows 11 10.0.26200、AMD64、AMD Ryzen 9 8945HX；CPU-only。本阶段没有验证Xeon Gold6140。
- Python 3.12.14、NumPy 1.26.4、Pillow 10.4.0、SciPy 1.15.2。单头原生库为MinGW GCC 15.2.0、C++17/C99、Release、AVX2/OpenMP；实际功能运行主要为4线程，另覆盖1线程请求。
- 实际DLL SHA256：`39a1d80ec8974bb190d3fd99689bb378f8120171bcb6ba5ed7bdec1a62c44b17`。头文件链接回执中的hpp SHA为 `f09079b092233d5376100dec7895fef80eb34f1c50b5bc0324f9a42e76346fa8`，C头SHA为 `9fbf8ed51374982f9c59ec6433ea4634e80441735ba709c7ef7df652b72f61f6`。
- 模型、照片和源文件的实际SHA、命令、库路径及运行后端以[本阶段归档](../../report/data/p16-studio-event-20261029/)为准。包与验证回执中的绝对路径仅说明本机那次执行位置。

## 已执行验证

这些测试分别验证格式/参数契约、实际数值执行、输出下载和交付闭环，不能相互替代为正式精度或受控性能结论。

| 范围 | 实际结果 | 原始证据 |
| --- | --- | --- |
| 最终Python定向契约 | `tests/test_studio.py tests/test_p16_event.py` 共55项通过，包含非法格式、四级参数、原像素、失败保留、来源绑定、99图拒绝与显式limit100仍为debug | `studio-event-final-tests.log` |
| HTTP集成 | 84项检查、10次串行真实渲染通过；不同预设变化、四级关闭还原、四级分别生效、detail m33/compact m17、固定native、完整1024×768 PNG像素SHA及Host/Origin/token/路径边界 | `studio-http-smoke-20261029.json` |
| 固定/创意预设 | 三套192px真实预设均通过原生/C99核对 | `studio-backend-real-presets.json` |
| 赛前闭环 | init/doctor、既有模型2图、新四表混合m[17,25,25,33]实际fit及2图run、T=0故意失败退出2；5份PNG回读SHA一致 | `event-cli-20261029/verification.json`及同目录原始记录 |
| PowerShell转发 | init→doctor→1图run真实通过 | `event-wrapper-smoke-20261029/wrapper-verification.json` |
| 隐藏启动与复用 | 从停止本会话旧进程开始，用start-event启动8876；再次执行复用同一PID；health确认当前服务/Studio/catalog及DLL SHA | `studio-launcher-verification-20261029.json` |
| 打包契约 | 7项检查通过，覆盖包成员篡改、ZIP多余成员、路径越界和已有输出拒绝；包目录另做真实自检 | `event-package-tests-20261029.log`及`package-self-check.json` |
| C++接入层 | GCC15.2 Release构建；2帧19×11、block13与FFI及独立C99逐字节相同；共8项正常/非法参数/不覆盖检查通过 | `event-cpp-smoke-20261029/results.json` |
| 素材及静态检查 | 20图/18LUT/17组合路径、文件和像素SHA、灰阶LUT全节点、许可引用通过；JavaScript与PowerShell语法及HTML ID引用检查；6种复制状态验证待处理时不携带旧actual_config | 对应catalog和frontend检查回执 |

复现命令（`python`须为上面记录的同一依赖环境，Windows DLL须可加载）：

```powershell
python -X utf8 -m pytest tests/test_studio.py tests/test_p16_event.py -q
python -X utf8 scripts/prepare_studio_catalog.py --check
.\start-event.ps1 -Mode studio -Port 8876 -NoBrowser
python -X utf8 gui/studio_smoke_test.py --url http://127.0.0.1:8876 --output artifacts/studio-recheck.json --preset layered-film
```

重新运行使用新的输出文件/目录。C++复现命令、编译参数和运行器探针脚本随原始证据归档；新LUT的fit/run命令见赛前指南。第一次浏览器联调暴露的identity浮点/节点uint8错误已经修复，后续真实渲染和定向回归通过，不能把首次失败略作成功。

浏览器实际操作检查过默认渲染、代表图切换、人像组合、强度改变后的自定义状态、性能面板及细节偏好。随后浏览器工具明确返回该origin的权限拒绝，已停止所有进一步浏览器操作，没有换浏览器或其他方式绕过。未取得可归档截图，也未完成移动视口的实际浏览器验收；后续验证限源码、命令行和既有HTTP功能测试。

## 调试包及现场使用

最终交付为 `p16-event-ready-20261029-v2.zip`：159126441B（约151.76MiB），369个清单成员加MANIFEST，共370项；ZIP SHA256为 `c4dafa88ed4aa64d2cdc992eb9927e87f3234eea69f0d82fdc0da47aa5139641`。首次无v2后缀快照保留，不作为最终交付。包构建与完整性结果在归档的 `package-receipt.json`，其中列出目录、ZIP、字节数、成员数和SHA。包保留100张已有1024×768评测PNG、20张代表图、18份CUBE、17套组合、模型对象、源码和MinGW原生依赖；样例不包含四张密集原LUT。Python复用本机已安装环境，未打包解释器，不承诺另一台机器免依赖。照片、LUT和运行依赖各自保留来源及许可；本机照片包不随代码PR上传。

在包目录执行 `start-local.ps1` 打开工作台；`-Mode doctor` 自检，`-Mode run -Config event-demo.json -Output probe-01 -Limit 1` 跑样例。包的SELF-CHECK从包目录真实执行doctor和单图原生/C99映射，不依赖原工作树里的密集LUT。样例threshold=null且source_luts为空，不能产生质量过线结论。

包内启动器也已实际以8877端口、NoBrowser启动，确认无主窗口、health的root及库路径位于v2包，再次调用复用同PID；仅停止本次包服务后，完整包和ZIP复核仍通过。第一次验收脚本读取WMI进程命令行被系统拒绝，失败回执原样保留，改用Get-Process、实际health及服务记录核对身份后通过；两次记录为 `event-package-launcher-20261029{,-v2}.json`。工作树8876服务继续保留。

正式输入按指南新建配置、填写四张原表及图片、fit后使用新run-config.json运行。当前适配明确要求每份50331648B的uint8[R,G,B,C]、B轴最快；正式格式或位深不同应改输入适配层。填入正式Threshold后按每图未舍入mean严格小于T验收，完整批次移除limit。

## 协作记录与未完成事项

创建PR前检查仓库完整issue/PR索引和空第二页；读取相关 #95、#84、#40 的正文、评论/review/行内线程，以及 #7/#8 正文和完整评论。新发现的[#96跨LUT审查](https://github.com/WyEhNf/flash-chroma/pull/96)也已读取正文、完整评论/线程和版本化review.md。fetch后目标仍为fb7e195；历史修复337a3dd、876e15b8、397cc367均在本分支祖先中。

| 事项 | 本次处理及剩余边界 |
| --- | --- |
| #96旧验证器强制direct及超容量中断 | 本阶段没有修复旧verify_flash_chroma.py。新event入口默认Sparse，显式direct由实际prepare判资格，不自动枚举旧profile白名单；发生错误留下failure，不声称其他表示已验证 |
| #96旧部署目录指标未绑定原始证据 | 本阶段没有修复旧run_flash_chroma.bind_evidence。新入口不读取旧catalog质量/时间或选择结果，对本批输入实际重算；不能据此关闭旧问题 |
| #7旧Casebook内核绑定 | 历史修复337a3dd已包含，保留原issue状态；与#96新缺口分开记录 |
| #8接口决策/目标资源/实板 | 本阶段增加接入层，不把桌面功能测试当作实板、功耗、实时性或最终接口迁移完成 |
| Discussion4 | 接口不能读取，保留协作缺口；没有执行依赖完整审查的合并或issue关闭 |
| 正式验收 | 官方数据、Threshold、文件协议和评分计时边界未知；未执行正式百图、新链完整色域或Xeon6140性能 |
| 旧RAW流程 | 保留/raw路由和代码；本阶段未重新解码/导出旧三厂商RAW，离线包不包含相应大素材/解码工具 |
| 性能与质量优化 | 本次优化流式内存和现场操作路径；功能计时没有A/A、绑核和重复稳定性资格，不宣称底层加速或已追平历史库。混合m新拟合两图mean约3.337只作功能观察，无Threshold通过资格 |

交付保持Draft，供维护者审查；没有合并PR或关闭issue。对应实现提交及最终交付状态见本阶段PR的Commits和归档来源清单。
