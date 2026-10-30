# 速度阶段精简证据

Agent：Codex /root/speed；Operator：当前用户；完整阶段说明见[工作说明](../../../docs/stages/2026-10-23-p16-speed-prepare-outplace.md)。首轮日期2026-10-23，prepare确认与86性能为2026-10-24（Asia/Shanghai）；历史路径中的23保留。

- `p16-speed-direct-v1`：85与80完整表/全域/边界正确性、首轮四进程原始数组及统计。单线程同句柄控制漂移到1.236468，稳态控制失败，只作描述，不采纳稳态加速。
- `p16-speed-prepare-confirm-v1`：完整40次create及原始比值。约8秒与86编译重叠，`measurement-validity.json`明确环境无效，不采纳；保留`results.json`原字节，其中数值门槛true不能单独视作有效确认。
- `p16-speed-prepare-confirm-v2`：同一冻结协议、同一对DLL，40次完全串行交错create。中位候选/80耗时比0.458296，完整prepare确认通过。它不修复首轮稳态控制失败。
- `p16-speed-generic-to-v1`：86清error字符串修正前完整正确性，无性能运行。
- `p16-speed-generic-to-v2`：最终86完整正确性及四进程原始数组。A/A控制有效，真分离1/4耗时比0.991371/1.026643，未达到双档改善3%，不采用。
- `build`：实际flags和DLL/源身份，五个85复用像素/计时对象的COFF `.text`与80精确相同。大二进制及16MiB表不入此精简归档，原件仍在本工作树artifacts；机器/模型绝对路径用于复现定位，不是外部可访问下载链接。

`manifest.json`为本目录全部原件清单，不包含清单自身；`offline-audit.json`记录只读JSON复算。独立复算命令如下，不执行任何本地颜色内核：

```powershell
python -X utf8 scripts/audit_p16_speed_evidence.py report/data/p16-speed-prepare-outplace-v1/p16-speed-direct-v1 report/data/p16-speed-prepare-outplace-v1/p16-speed-prepare-confirm-v1 report/data/p16-speed-prepare-outplace-v1/p16-speed-prepare-confirm-v2 report/data/p16-speed-prepare-outplace-v1/p16-speed-generic-to-v2
```

容量为句柄/已知vector容量记账，不是RSS；没有断言在i7-14700、Skylake或正式比赛接口实测。精度证据为固定模型完整RGB8输出等价，未重新拟合或重新选用照片改善的模型。

85/86执行身份对应提交`dee46cd`。后续87阶段为新计划增加了脚本SHA核对，重现旧计划时应恢复本提交的脚本；不要改旧计划哈希或用新版脚本替代旧执行身份。旧原件清单在本说明补充前形成，说明补充不改任何数值证据。

87交付时修复了首提交44份归档文件的Git换行规范化问题，恢复为artifacts原始CRLF字节，使blob SHA与已记录原件清单相同；源码身份核对与`dee46cd`全部精确一致，不是数值重算或修改原始计时。最终检查必须逐blob核对清单，不能只核对磁盘文件。
