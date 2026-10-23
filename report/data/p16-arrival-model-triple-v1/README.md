# 三模型同87同场原始证据

本目录保存冻结计划、四worker全部原始轮次和partial快照、预检及两候选既有完整域验收JSON。raw-evidence.zip使用STORE，所有原始字节原样保存；models.zip为三链实际SLUT/sidecar，未复制50MB全域流或照片，完整身份在计划中。

execution-sources.zip保存九个实际执行依赖原字节。identity.json同时记录执行SHA与旧Git blob SHA；少数历史CRLF/LF差异显式保留，不改历史源。新脚本及计划应与本commit blob SHA相同。87源码身份指向3210857，当前工作区另有90尚未归档的修改，不能把当前90源误标成87实测。

独立复算：`python -X utf8 scripts/audit_p16_model_triple.py report/data/p16-arrival-model-triple-v1/raw-evidence.zip`。审计不加载DLL、不追加计时；末work每组SHA，非每内轮。原地纯apply剔除前置memcpy，含copy数组也完整保留。首次prepare/首批百图无构造AA，独立描述，不混作稳态。

结论见docs/stages/2026-10-24-p16-arrival-model-triple.md；历史旧两模型80档证据仍保留，不与本场90档结果相除。
