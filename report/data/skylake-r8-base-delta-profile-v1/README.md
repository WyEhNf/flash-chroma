# 局部RGB基值加固定5bit差分：只读筛查失败

[阶段说明](../../../docs/stages/2026-10-23-skylake-base-delta-profile.md)记录编码、门槛、输入身份、复现与覆盖边界。原始分析在2026-10-21完成，本目录在2026-10-23归档并独立核对，未重新执行原始分析。

`original/`保存八份原件的逐字节副本；`manifest.json`绑定源路径、归档路径、大小与SHA。`independent-audit.py`仅使用Python标准库重哈希输入并复算已有JSON；`independent-audit.json`保存实际核对结果。后补文档、清单与独立审计不计入八份原件。

原始方案全部16,777,216色及100图重建零差，但异常池30,245,024B超过2MiB，照片异常8像素包53.458903%超过5%，最差图97.978719%超过20%，96图超单图门槛。三项资源门槛全部失败，因此没有原生实现、编译或性能测试，不能把此结果计入加速成绩。

审计重哈希六项输入、十项历史来源及上一只读结果，另逐片验证100图输入SHA；重新加总原因位图/交集、跨度及逐图异常直方图，确认门槛失败。没有第二次重建大色域/照片，也没有重建原分析内存中的主表或异常池；原精度结果与当前独立核对范围明确分开。

另一个7bit拆平面设想只复用已有跨度直方图得到异常池至少15,210,464B的下界，已超过2MiB，未实施或新跑profile。它不是调整原5bit门槛后重试。

仅复现独立核对，需恢复清单所指原件及协议所指输入，并使用新的输出路径：

```powershell
python report/data/skylake-r8-base-delta-profile-v1/independent-audit.py --repository . --output artifacts/skylake-r8-base-delta-audit-reproduction.json
```

原始分析环境为Windows11 10.0.26200、AMD64 Family25 Model97 Stepping2、Anaconda Python3.13.12和NumPy2.4.6；当前独立审计在相同Windows/Python环境仅用标准库完成。没有实际Skylake验证，整体三倍目标未完成。提交、远端协作检查及Draft PR由根代理另行交付。
