# Cinema完整联合支撑与整体预算证据

与[阶段说明](../../../docs/stages/2026-10-24-cinema-arrival-budget.md)对应。`evidence.zip`保留七组前缀检查、两个独立冻结试验的run/progress/summary、完整861行联合支撑、真实模型、独立合同、uint64/native/百图终验、两份只读审计器初稿失败、所测87 DLL及实际执行源码。`manifest.json`逐成员列原字节SHA/尺寸，并列不重复上传的大输入。`source-identity.json`区分工作区实际执行字节与既有HEAD源码；旧继承CRLF/LF差异保留在ZIP，不修改旧源或伪称字节相同。

`accuracy-results.json`是原始终验副本；`unit-summary.json`保留第一次mean-only候选不升级；`budget-summary.json`是最终候选；`independent-audit.json`含全部逐图退化；`prefix-summary.json`明确没有检出59下界；`runtime-eligibility.json`只证明87资格，未计吞吐。`execution-receipt.json`补实际命令与模型SHA。`publication-audit.json`核原件/ZIP；暂存Git blob还需独立复核。

在专用Python3.12.14/NumPy1.26.4/Numba0.60环境中，设置PYTHONUTF8=1及BLAS/MKL/OMP=1后运行。下列路径均为本次实际Windows工作区，替换位置时应按run中的SHA恢复输入；每个输出目录必须新建，脚本拒绝覆盖：

```powershell
python scripts/check_integer_rgb_ball.py
python scripts/certify_cinema_prefix_bound.py --cache-root F:/Hackathon/projects/16-lut-color --first-folder artifacts/cinema-last-stage-v2/candidate --cube artifacts/cinema-last-stage-accept-v1/candidate.rgb --output artifacts/cinema-prefix-bound-v1
python scripts/check_cinema_prefix_certificate.py artifacts/cinema-prefix-bound-v1 --output artifacts/cinema-prefix-bound-v1/independent-check.json
python scripts/check_channel_arrival_nodes.py --output artifacts/cinema-arrival-last-unit-v1-contract.json
python scripts/run_cinema_arrival_unit_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --first-folder artifacts/cinema-last-stage-v2/candidate --cube artifacts/cinema-last-stage-accept-v1/candidate.rgb --contract artifacts/cinema-arrival-last-unit-v1-contract.json --output artifacts/cinema-arrival-last-unit-v1
python scripts/run_cinema_arrival_budget_nodes.py --previous artifacts/cinema-arrival-last-unit-v1 --output artifacts/cinema-arrival-last-budget-v1
```

完整流与百图恢复命令见execution-receipt；它使用`accept_channel_tail_nodes.py`的`--suffix-stage4`、`--baseline-cube`及冻结87库参数。随后运行：

```powershell
python scripts/audit_cinema_arrival_budget.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/cinema-arrival-budget-audit-v1.json
```

首次在旧目录直接重跑会被拒绝，这是原件保护。未提供Python依赖、源四原表和100张PNG的新副本；按原项目缓存/manifest恢复。GCC DLL的运行依赖沿原87阶段绑定，不把本ZIP的单DLL当作独立可运行发行包。尚无新吞吐、实板或官方成绩。
