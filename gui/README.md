# Flash Chroma Studio 本地工作台

在仓库根目录启动：

```powershell
.\start-gui.ps1
```

默认 `/` 和 `/studio` 打开当前单头文件运行库的图片调色工作台；原 RAW 工作流保留在 `/raw`。默认地址为 `http://127.0.0.1:8765/`，端口占用时自动选择空闲端口，实际地址和 PID 写入 `artifacts/gui-jobs/server.json`。仅监听本机，素材与处理结果保存在本地。

启动器先尝试显式设置的 `FLASH_CHROMA_PYTHON`，再查找当前工作树及 Git 主工作树的 `artifacts/error-study-py312/Scripts/python.exe`，随后才考虑旧 `camera-raw-env-v1` 和系统 Python。它会实际检查 NumPy、Pillow 及选中原生库是否可加载，以隐藏后台进程运行服务，再打开浏览器。再次启动时，只有工程路径、Studio API 版本、服务/Studio/目录的启动来源 SHA 及原生库 SHA 均匹配才会复用服务；旧 RAW 服务或不同构建会保留，新版本另选可用端口启动。

```powershell
# 后台启动但不打开浏览器；Port 0表示由系统分配空闲端口。
.\start-gui.ps1 -Port 0 -NoBrowser

# 显式指定本次使用的单头原生库，路径无效或加载失败时明确报错。
$env:FLASH_CHROMA_LIBRARY = 'F:\path\to\libflash_chroma_bridge.dll'
.\start-gui.ps1
```

本机优先发现 `artifacts/single-header-perf-build/libflash_chroma_bridge.dll`，随后检查 `build-single-header` 及已有的 `artifacts/single-header-build`。没有可加载库时须先构建：`cmake -S single_header -B build-single-header`，再运行 `cmake --build build-single-header --config Release`；Windows MinGW 可按本机工具链增加生成器和编译器参数。页面及 `/api/health` 会返回实际库路径、摘要与能力，不能用旧库的测量冒充当前构建结果。

工作台从 [`studio_catalog.json`](studio_catalog.json) 读取20张代表图片、18个创意LUT，以及15套创意组合和2套Cinema固定模型预设。可选择图片与风格，创意组合支持逐级启停或调整强度；Cinema链保持固定只读。界面提供原图/结果分割、差异图和当前配置，并下载保持输入尺寸的 RGB PNG。三个连续偏好参数表达精度、速度和内存取舍，最终配置仍在当前实现支持的离散模型和执行策略中选择；创意组合使用参数策略，未取得完整百图Pareto最优资格。偏好百分比不是精度百分比，也不承诺未知设备或新图片的评分。

照片预览、PNG 编码和浏览器交互属于应用流程。界面中的运行记录用于说明本次实际操作，不作为 6140 性能成绩或官方阈值通过结论。四级关闭应复现输入 RGB；不同组合及各级开关的实际效果由下面的 HTTP 检查验证。所有修改请求仍要求本地 Host/Origin 与会话 Token，图片和结果接口使用目录内的固定 ID，不接受任意文件路径。

```powershell
# 对已经启动的新服务执行串行真实渲染、四级调整、原尺寸PNG及安全边界检查。
# 每次使用新的输出文件；不触发旧RAW解码或性能评分。
python -X utf8 gui/studio_smoke_test.py --url http://127.0.0.1:8765 --output artifacts/gui-jobs/studio-verification.json --preset layered-film
```

该检查要求至少16张代表图片、12个真实LUT和12套四级组合，实际调用当前本机原生库，验证不同组合输出变化、四级关闭还原、四个阶段各自生效、性能偏好改变实际网格、Cinema固定模型、完整尺寸 PNG 下载及原生像素SHA，以及 Token/Origin/Host、非法参数和路径越界拒绝。具体成功记录与执行环境以本阶段实际生成的验收文件为准，脚本存在不等于已经运行通过。也可直接运行 `python -X utf8 gui/server.py --open --studio-library <原生库完整路径>`，Ctrl+C 停止服务。

## 旧 RAW 工作流与历史验收

以下为 `/raw` 的既有功能、依赖及历史验证；它使用独立的官方解码工具链和原 RAW 实验运行时，不与本阶段 Studio 的单头图片处理结果混合计分。

界面可以直接查看三组真实素材的既有结果，选择SDR/HDR、参考/原生/误差或拖动分割比较，播放/拖动52帧BRAW。显示的数值来自完整帧回执，单位是归一化误差×255的8bit等效代码值，HDR不是nits或感知色差。PNG画面仅用于预览：SDR Rec.1886转换到sRGB；HDR经PQ解码、Rec2020→709及固定Reinhard映射到SDR屏；误差图是导出RGB差异放大8倍，不替代未裁剪参考误差统计。

“处理首帧”实际重新执行官方CPU解码、Log、四级LUT及所有已处理像素的原生/标量字节核对。“处理完整素材”处理实际所有帧，会先核验磁盘空间；52帧6K需要数十GiB中间文件空间。两种操作均生成独立的 `artifacts/gui-jobs/<任务ID>/`，保留原始验证结果和失败/取消片段。新任务一次仅运行一个。任务日志展示真实子进程输出，任务成功以完整结果文件为准。

可导入单帧 `.ari`、`.R3D` 或 `.braw`，品牌须匹配。文件浏览限制在工程目录，工程外文件可粘贴完整路径。ARRI导入只支持单帧.ari，不支持MXF/ARRIRAW序列；自有素材的帧数/尺寸由工具读取。RED输出Log TIFF16后归一化float32，不能称为未量化的原生float32。四级调色参数固定为本次已验策略，界面不提供未实现的可调旋钮。

“导出”执行FFV1编码并完整回读四份SDR/HDR reference16/runtime8文件。6K结果使用实验FFV1 v4以避开本机v3内存分配失败，小尺寸使用v3；存储gbrp16le不会增加RGB8模型的有效精度。HDR预览和实验容器均不等于HDR生产母版验收。

查看既有结果的Windows服务需要Python、NumPy与Pillow；本机已具备NumPy2.4.6/Pillow11.1.0。重新处理还需要现有WSL2环境、Python3.14.4、OCIO2.6.0、OpenEXR3.5.2、tifffile2026.10.15、固定修订78库及`artifacts/camera-raw-workflow-v1/`中的官方ART/REDline/BRAW工具。来源与精确身份见[真实RAW阶段报告](../docs/stages/2026-10-23-camera-raw-workflow.md)。缺失依赖时任务明确失败，不以旧结果冒充新运行。

旧 RAW 界面归档验证：三家18种首帧PNG及5项接口边界共23项通过；已从浏览器完成ARRI重新处理与四份视频导出，并核对四路RGB的SHA与原验证结果完全相等。BRAW时间轴已在界面定位到第52帧，导入浏览器和分割线已操作检查。

后续联调曾遇到WSL启动失败及主机提交空间不足。现已应用1GB/4核/F盘2GB交换的CPU配置，三家首帧重新解码、12路输出SHA、新导入及启动窗口真实worker取消已通过；旧失败记录保留。配置、内存采样、备份和回滚见[WSL内存阶段](../docs/stages/2026-10-23-wsl-memory-budget.md)。该预算下完整52帧、长时间稳定性及运行中解码子进程的取消仍未验收；完整任务还需要足够磁盘。下面的真实集成检查会创建独立RED/BRAW首帧及取消任务，保留所有文件：

```powershell
python -X utf8 gui/smoke_test.py --views-only --output artifacts/gui-jobs/view-verification-repro.json
# 完整集成还需要已有ARRI GUI处理及导出成功记录和正常WSL。
python -X utf8 gui/smoke_test.py --output artifacts/gui-jobs/integration-verification-repro.json
```

PQ常数和D65原色定义参考[Colour ST2084实现](https://github.com/colour-science/colour/blob/v0.4.6/colour/models/rgb/transfer_functions/st_2084.py)、[BT2020](https://github.com/colour-science/colour/blob/v0.4.6/colour/models/rgb/datasets/itur_bt_2020.py)、[BT709](https://github.com/colour-science/colour/blob/v0.4.6/colour/models/rgb/datasets/itur_bt_709.py)。预览转换不改变原始像素或评价模型，不产生新的精度/性能验收结论。
