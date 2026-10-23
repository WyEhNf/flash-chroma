# 修订84混合RGB解码：完整精度通过，四线程性能失败

Agent：Codex /root、/root/base_delta_delivery；Operator：WyEhNf；Status：Failed / Draft。

一次构建和完整24配置RGB8运行时验证通过，输出逐字节不变。首轮四新进程A/A有效，纯apply单/四线程为3.045947／0.951626倍，真正分离输出为3.511375／4.679473倍。四线程纯apply耗时高于23约5.0833%，同时失败三倍及任一进程≤0.9门槛；不确认、不重测、不采用。新增16MiB常驻表，四级句柄44,823,940B，准备成本计入首100图。

[阶段说明](../../../docs/stages/2026-10-23-skylake-brick2-hybrid.md)解释机制、固定模型、正确性范围、环境、限制及协作检查。实际为Windows11宿主Ryzen9 8945HX、WSL2 Ubuntu、GCC15.2及Python3.14.4，通用AVX2/Skylake调度、四物理核固定绑定，未执行真实Skylake。

`evidence.zip`保存235份原字节：唯一构建及对象、参考/候选ELF、完整日志与源码ZIP，根/独立静态、全部完整RGB8验证、48批计时与A/A原始数组、静默记录、确认跳过决定、三项胶水失败版本和修复说明、准备/归档辅助代码，以及操作前完整75份PR正文及意见快照。manifest逐项绑定大小和SHA。根静态`results.json`的假失败原件保留，最终使用`results-v2.json`；独立结果首轮即通过。

`build.json`、`full.json`、`performance.json`、`static.json`及`independent_static.json`为对应结果的原字节便利副本。后补归档核验、操作前末次刷新、暂存blob交付回执和本说明位于ZIP之外，避免自引用。计时样本、候选和门槛均不因交付而修改。

从仓库根目录复算归档、原始计时、A/A和三倍门槛：

```powershell
python -X utf8 report/data/skylake-brick2-hybrid-v1/verify_archive.py
```

入口仅在临时目录运行ZIP内Python标准库核验器，不加载ELF、不重新测速、不要求大输入。原生复现命令见阶段说明及ZIP内构建/运行记录；需恢复同SHA固定模型、单级oracle、cube和百图，旧build中绝对路径也需匹配。孤立克隆本档案不能自动重建这些大输入，不能把静态重算当作新主机性能验证。
