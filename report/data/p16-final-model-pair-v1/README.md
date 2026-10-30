# 最终模型同87后端配对原件

2026-10-24（Asia/Shanghai）执行，[阶段说明](../../../docs/stages/2026-10-24-p16-final-model-speed.md)记录计时边界、控制与退化。`executed-plan.json`绑定原模型/源码/DLL身份；`preflight.json`保存由独立全域oracle产生的100图预期SHA；`worker0..3.json`保存全部原始计时、输出、准备与资格；`results.json`不丢最劣进程。

结果为A/A有效、50%底线通过，最劣吞吐保留87.3558%，因此通过80%档，90/100%未过；“无明显退化”也未通过。`fixed-models.zip`保存七个不同模型/侧表原字节及原路径/SHA映射，不含100图或50MB完整流。完整流及87二进制按计划SHA在对应artifacts中恢复，不是外部下载链接。

只读复算不加载库、不追加轮次：

```powershell
python -X utf8 scripts/audit_p16_model_pair.py report/data/p16-final-model-pair-v1
```

`offline-audit.json`为实际复算输出；`manifest.json`绑定除清单自身的归档原件。模型配对结果不与先前prepare54%/7.7%相乘，不作为正式比赛或目标Intel结果。
