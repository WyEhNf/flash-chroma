# 后缀准备AVX2的精简证据

实际执行日期2026-10-24（Asia/Shanghai），阶段说明见[工作说明](../../../docs/stages/2026-10-24-p16-simd-prepare.md)。本目录保留87相对冻结85的完整整数正确性、独立prepare确认原件和只读复算。

`correctness.json`覆盖完整16,777,216输入色、所有直接表词、原地/真分离1/4、504组有限合同、11项拒绝及单级回退。`confirm`保存冻结计划、40次交错create的四进程原始数组与结果；中位耗时比0.9229996630504755，门槛通过。`identity.json`记录库/源/构建flags及五个复用对象`.text`逐节相同。`manifest.json`包含本目录除清单自身的每个文件哈希。

只读复算如下，不加载原生库，也不追加性能轮次：

```powershell
python -X utf8 scripts/audit_p16_speed_evidence.py report/data/p16-prepare-simd-v1/confirm
```

前一阶段85计划对应提交`dee46cd`的脚本身份；本阶段确认脚本增加可配置事前门槛和源码SHA检查，应按各冻结计划使用对应Git版本，不能修改旧计划哈希使其适配新脚本。旧原件保留在`p16-speed-prepare-outplace-v1`，两场prepare比不跨场相乘。无新稳态吞吐、RSS或Intel服务器结果。
