# 2³恒色RGB头只读筛查证据

Agent：Codex /root/speed；Operator：当前用户。实际执行2026-10-24，Windows11 x64、Python3.12.14/NumPy1.26.4、冻结87 AVX2库；没有实现原生候选或进行性能测量。[阶段说明](../../../docs/stages/2026-10-24-p16-constant-prepare-policy.md)解释机制和失败边界。

`executed-plan.json`保存执行前方案、脚本/库/模型身份和50%整包覆盖研究兴趣线；`results.json`保留100逐图直方图、覆盖率、完整恒色颜色比对、头容量及SHA。正常整8包17.481903%，未过兴趣线；这不是用户50%吞吐底线。`read-only-references.json`记录原工作树cost-split资料的绝对路径和SHA，未修改其文件。`offline-audit.json`只按JSON合计逐图数据，不加载原生库。

如需从头复现（会创建原生完整准备及读取100图，须安排计算窗口），不要覆盖已有目录：

```powershell
python -X utf8 scripts/profile_p16_constant2.py --plan experiments/p16-constant2-profile-v1.json --output artifacts/p16-constant2-profile-new
```

`manifest.json`逐项绑定本目录除清单自身的原始字节。输入和固定模型与`p16-final-model-pair-v1`的baseline一致；派生表内存许可仍未得到赛事确认。
