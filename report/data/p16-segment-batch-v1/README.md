# 90显式分段接口：完整证据

raw-evidence.zip为STORE原件，保存四进程全部正式/AA/partial、冻结性能计划，以及两模型完整RGB8、合同、照片与driver质量JSON和冻结质量计划。控制失败不删轮、不重选。末轮caller-owned实际输出逐组SHA，不等于每内轮哈希。

execution-sources.zip保存实际Python依赖及由目标/core/driver的obj.d提取的项目C++执行源/头，identity.json记录执行SHA与相应Git blob SHA，历史CRLF/LF差异不修改。当前runtime是90，不冒充87源码；87源绑定3210857既有归档。build-files.zip保存原始flags/link/rsp/make/depend；models.zip为两链实际模型/sidecar，不复制照片或50MB oracle。

复算：`python -X utf8 scripts/audit_p16_segments.py report/data/p16-segment-batch-v1/raw-evidence.zip`，不加载DLL、不追加计时。审计检查432配置/1296组实际SHA/108配对统计、所有控制与档位；stage及HEAD另逐blob核身份。

结论/所有36行/假设和退化见docs/stages/2026-10-24-p16-segment-batch.md。连续和真实非连续不可跨布局相除；旧bulk的pack/scatter全部在内轮计时；新API验证、任务构造分配、OMP调度全计。新模型prepare与产品端到端不在本场稳态内，未用热像素收益隐藏准备。
