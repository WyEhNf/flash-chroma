# 88显式准备策略的完整原始证据

Agent：Codex /root/speed；Operator：当前用户。2026-10-24实际Windows11 x64、Ryzen9 8945HX、GCC15.2 Release、Python3.12.14/NumPy1.26.4。进程允许CPU集合0/2/4/6，不代表逐OpenMP TID绑定；无锁频控温或Intel目标实测。[阶段说明](../../../docs/stages/2026-10-24-p16-constant-prepare-policy.md)说明目的、全部12场景结果及失败边界。

`raw-json.zip`以STORE方式原字节保存11份JSON（冻结执行计划、完整域验证、汇总、四进程原始和partial轮次）。`raw-members.json`逐项绑定未压缩成员大小和SHA，未删除5项A/A控制失败的场景。另直接保存计划、正确性和汇总供审阅；内容与ZIP成员逐字节相同。288次底层冷句柄create含文件读/解析/原生校验/缓存和表准备，文件缓存为热态。

两策略完整RGB8零差；12场景7项控制有效、5项失败。全部有效场景的suffix-only纯稳态吞吐保留均低于50%，因此未采用为普遍替换或默认。小作业端到端收益单列，不能豁免纯映射底线；所有失败控制原件都保留，没有追加择优重测。

`identity.json`记录DLL/源SHA、构建身份和五个复用像素/计时COFF对象`.text`相同；`88-flags.make`、`88-link.txt`和`88-includes.rsp`为构建生成文件原件。没有注入分配失败或在无AVX2硬件执行新策略。固定a399模型可复用`../p16-final-model-pair-v1/fixed-models.zip`的baseline模型；没有把两方向模型混成一个比较。

只读复算不加载原生库、不追加性能：

```powershell
python -X utf8 scripts/audit_p16_prepare_policy.py report/data/p16-prepare-policy-v1/raw-json.zip
```

从头正确性与性能复现需要计算窗口，按顺序执行且使用新目录：

```powershell
python -X utf8 scripts/study_p16_prepare_policy.py --plan experiments/p16-prepare-policy-v1.json --output artifacts/p16-prepare-policy-new --mode verify
python -X utf8 scripts/study_p16_prepare_policy.py --plan experiments/p16-prepare-policy-v1.json --output artifacts/p16-prepare-policy-new --mode measure
```

`offline-audit.json`保存原始JSON独立复算结果；`manifest.json`绑定本目录除清单自身的全部原始字节。构建源在本阶段提交，旧87冻结DLL没有覆盖。研究ABI显式开放策略1供复核，原`jshc_cc_create`仍完整准备。
