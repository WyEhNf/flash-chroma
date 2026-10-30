# Flash Chroma 本地工作台

在仓库根目录启动：

```powershell
.\start-gui.ps1
```

启动器优先使用本机已经准备好的 `artifacts/camera-raw-env-v1/Scripts/python.exe`，以隐藏后台进程运行服务并打开浏览器。默认地址 `http://127.0.0.1:8765/`；端口占用时自动选择空闲端口，实际地址和PID写入 `artifacts/gui-jobs/server.json`。仅监听本机，不上传RAW或处理结果。也可在终端运行 `python -X utf8 gui/server.py --open`，Ctrl+C停止服务。

界面可以直接查看三组真实素材的既有结果，选择SDR/HDR、参考/原生/误差或拖动分割比较，播放/拖动52帧BRAW。显示的数值来自完整帧回执，单位是归一化误差×255的8bit等效代码值，HDR不是nits或感知色差。PNG画面仅用于预览：SDR Rec.1886转换到sRGB；HDR经PQ解码、Rec2020→709及固定Reinhard映射到SDR屏；误差图是导出RGB差异放大8倍，不替代未裁剪参考误差统计。

“处理首帧”实际重新执行官方CPU解码、Log、四级LUT及所有已处理像素的原生/标量字节核对。“处理完整素材”处理实际所有帧，会先核验磁盘空间；52帧6K需要数十GiB中间文件空间。两种操作均生成独立的 `artifacts/gui-jobs/<任务ID>/`，保留原始验证结果和失败/取消片段。新任务一次仅运行一个。任务日志展示真实子进程输出，任务成功以完整结果文件为准。

可导入单帧 `.ari`、`.R3D` 或 `.braw`，品牌须匹配。文件浏览限制在工程目录，工程外文件可粘贴完整路径。ARRI导入只支持单帧.ari，不支持MXF/ARRIRAW序列；自有素材的帧数/尺寸由工具读取。RED输出Log TIFF16后归一化float32，不能称为未量化的原生float32。四级调色参数固定为本次已验策略，界面不提供未实现的可调旋钮。

“导出”执行FFV1编码并完整回读四份SDR/HDR reference16/runtime8文件。6K结果使用实验FFV1 v4以避开本机v3内存分配失败，小尺寸使用v3；存储gbrp16le不会增加RGB8模型的有效精度。HDR预览和实验容器均不等于HDR生产母版验收。

查看既有结果的Windows服务需要Python、NumPy与Pillow；本机已具备NumPy2.4.6/Pillow11.1.0。重新处理还需要现有WSL2环境、Python3.14.4、OCIO2.6.0、OpenEXR3.5.2、tifffile2026.10.15、固定修订78库及`artifacts/camera-raw-workflow-v1/`中的官方ART/REDline/BRAW工具。来源与精确身份见[真实RAW阶段报告](../docs/stages/2026-10-23-camera-raw-workflow.md)。缺失依赖时任务明确失败，不以旧结果冒充新运行。

当前本机验证：三家18种首帧PNG及5项接口边界共23项通过；已从浏览器完成ARRI重新处理与四份视频导出，并核对四路RGB的SHA与原验证结果完全相等。BRAW时间轴已在界面定位到第52帧，导入浏览器和分割线已操作检查。

后续联调遇到WSL启动失败（`Wsl/Service/E_UNEXPECTED`及空输出退出1），本机Windows拒绝重启`WslService`，需要操作者在管理员终端恢复服务；故障根因尚未定位。此时GUI仍可浏览既有54帧及执行Windows导出，新RAW任务会失败并显示提示，不能把旧结果当成新任务。RED/BRAW的新GUI解码与取消进程组验证尚未完成；前序命令行工作流的成功不能代替本GUI验收。恢复环境后可运行下面的真实集成检查，它会创建独立RED/BRAW首帧及取消任务，保留所有文件：

```powershell
python -X utf8 gui/smoke_test.py --views-only --output artifacts/gui-jobs/view-verification-repro.json
# 完整集成还需要已有ARRI GUI处理及导出成功记录和正常WSL。
python -X utf8 gui/smoke_test.py --output artifacts/gui-jobs/integration-verification-repro.json
```

PQ常数和D65原色定义参考[Colour ST2084实现](https://github.com/colour-science/colour/blob/v0.4.6/colour/models/rgb/transfer_functions/st_2084.py)、[BT2020](https://github.com/colour-science/colour/blob/v0.4.6/colour/models/rgb/datasets/itur_bt_2020.py)、[BT709](https://github.com/colour-science/colour/blob/v0.4.6/colour/models/rgb/datasets/itur_bt_709.py)。预览转换不改变原始像素或评价模型，不产生新的精度/性能验收结论。
