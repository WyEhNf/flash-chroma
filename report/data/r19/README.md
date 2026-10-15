# R17–R19 验收归档

本目录随源码入库，保留可直接核对的小型证据。性能均为Windows/Ryzen 9 8945HX及RTX 5070 Laptop上的固定合成输入结果，不能当作官方成绩。

- [精度摘要](accuracy-summary.csv)：六组独立四级模型的全色域统计、100图最差均值和示例门禁。
- [严格配对摘要](paired-summary.csv)：八项预定比较，每项七对AB/BA。
- [原始证据压缩包](r17-r19-evidence.zip)：原始JSON、逐图结果、完整配对时间、整数模型、测试日志、部署依赖记录及源码快照。
- [压缩包和逐文件SHA256](evidence-index.json)：校验归档内容及来源。
- [完整交付说明](../../../docs/r19-delivery-results.md)：统一入口、独立最佳已测CPU/GPU确认、计时和内存口径、题面要求与未通过项。

压缩包中的关键记录按原始项目相对路径保存：

| 路径 | 内容 |
|---|---|
| `artifacts/r19-delivery/acceptance-suite.json` | 六组模型及全部验收命令 |
| `artifacts/r19-delivery/acceptance-*.json` | 各组100图、全色域、来源绑定和CPU/CUDA一致性 |
| `artifacts/r19-delivery/paired/comparison.json` | 全部112次主机到主机计时及预检 |
| `artifacts/r19-delivery/paired/best-cpu-gpu-confirmation.json` | 额外七对独立CPU16/CUDA确认；配对比值中位1.291× |
| `artifacts/r19-delivery/paired/ocio-accuracy.json` | OCIO非均匀网格的float32/Q16差异与真值误差 |
| `artifacts/r19-delivery/delivery-manifest.json` | 冻结的源码、构建、完整资产SHA |
| `artifacts/r19-delivery/models/` | 六组整数模型及拟合manifest |
| `artifacts/r18-portable/acceptance.json` | 纯C++17、全部加速关闭的完整验收 |
| `artifacts/r19-delivery/deployment.json` | 隔离PATH后的CPU运行包验证 |
| `report/data/r19/hardware/` | 实际CPU特性与构建环境探针 |

需要展开查看时，可解压到新目录：

```powershell
Expand-Archive report/data/r19/r17-r19-evidence.zip -DestinationPath recovered-evidence
```

记录中的绝对路径是原始运行上下文。大约1.48GB的完整输入LUT、图像、原始像素输出及本机运行程序保存在本地资产中；归档不重复装入这些文件。源码中的阶段脚本可重建模拟输入和实验，详见交付报告。官方Threshold、阈值统计口径、正式数据与计时边界尚未提供；示例均值门禁5/6通过，其中裁剪m17失败，所有六组都不满足全色max<2。

更新归档时，先冻结源码和数值证据，再执行 `python scripts/archive_r19_review.py`。该步骤只归档和核对字节，不重新运行数值或性能实验。
