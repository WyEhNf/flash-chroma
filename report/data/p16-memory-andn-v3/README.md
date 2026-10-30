# 线性ROM ANDN阶段证据

实际阶段见[说明](../../../docs/stages/2026-10-24-memory-rom-andn.md)。`build.json/full.json/contract.json`绑定实际构建及15完整域、有限、保护页合同；`performance.json`保留全部比值，`acceptance.json`明确A/A失败情形不得升级正式优选；`performance-raw.zip`保存4worker全部轮次、driver源SHA及独立RSS进程。`measured-source.zip`保存冻结计划、实际源、两份生成ANDN源及stack帧记录；`new-libraries.zip`仅新增两库，对照78/80和依赖复用前阶段已测包。`manifest.json`绑定原始成员；此README和阶段说明后补。

单线程原地/输出控制失败保持，不把raw JSON自动生成的档位视为接受。四线程两接口控制通过；精度始终位精确。未重跑计时或另选样本，大ROM和照片不上传。
