# 五个指令级研究候选的静态证据

Agent：Codex；Operator：WyEhNf；Status：Completed（五候选均停止，未进行数值或性能验收）。

完整说明见[阶段报告](../../../docs/stages/2026-10-20-skylake-instruction-study.md)。实际构建环境Windows11 / Ryzen9 8945HX / MinGW GCC15.2；LLVM-MCA21.1的Skylake模型只用于静态资格，不代表目标硬件速度。

| 文件 | 内容 |
| --- | --- |
| `geometry.zip` | 中值网络修订17；周期改善不足3% |
| `evex256.zip` | EVEX-256修订18；rsp减少但周期模型恶化 |
| `grid33.zip` | 常量地址修订19；两家族rsp增加 |
| `grid-geometry.zip` | 一次固定组合修订20；rsp与38-gather周期失败 |
| `domain-delta.zip`、`domain-delta-manifest.json` | 获证坐标差21对较快16；18→15gather但周期/rsp失败，另列第五项身份与门槛 |
| `summary.json` | 输入/构建/分析SHA、预设门槛复算与工具修正说明 |
| `manifest.json` | 六项原始归档的SHA与字节数；说明文件与后续交付核对另列 |
| `remote-snapshot.zip` | 37个PR、2个issue、2个Discussion及完整相关意见快照，无凭据 |
| `independent-audit.json`、`independent-audit-v2.json`、`independent-audit-v3.json`、`independent-audit-v4.json` | 标准库独立核对6个清单文件、178项源成员、MCA日志与四项拒绝结论 |

每个候选ZIP内包含`plan.json`、`build/`（源码ZIP、编译命令与日志）、`static/`（结果/反汇编/原始MCA日志）、`objects/`、`binaries/`、实际`analysis-script.py`与一次性`setup-script.py`。重建先解压源码ZIP恢复原字节，再按日志明确映射工具与输出路径；输出必须用新目录。仓库新检出可能归一化行尾，不能通过更新旧SHA伪造实测身份。

归档只是复算既有结果，新增拟合、像素核和性能调用均0。源码的数学等价意图、CPU能力探针、静态模型、对象同字节，均不替代运行正确性或实测性能。五原型不进入默认或服务器候选集合。

`remote-check.json`记录操作前118组快照对比一致。API临时克隆字段不进入交付快照；剔除后独立audit-v2再次通过，四个数值/静态ZIP保持原字节。

第五项以独立扩展manifest增加，不改写前四个数值ZIP；最终audit-v4同时复核原六项清单和新增第五个ZIP，共234项源成员；v3第五项的家族显示键修正为18_to_15，数值不变。
