# 末级联合优化与严格图级阈值复算

[阶段报告](../../../docs/stages/2026-10-24-cinema-last-stage.md)给出相对a399和severe_first的结果、逐图代价、末级独立源退化与未完成性能门禁。`accuracy-results.json`为87完整域/100图及uint64独立四级验收；`fit-run/summary.json`冻结目标与完整源质量；`comparisons.json`为两套逐图直接比较、60/20/20组和非官方严格max<T通过数；全部退化及阈值各存CSV。

`models.zip`含冻结完整四级模型、首级必须配套侧表、NPZ源表示；`fit-evidence.zip`含唯一八批及日志缺import的v1失败记录；`runtime-eligibility.json`含真实87构造回执，不能替代吞吐测试；`source.zip`及manifest保存源SHA。87 DLL与依赖由速度分支保存，本目录不重复。

在原冻结数据缓存及Python3.12环境下，设置Numba4与BLAS/MKL/OMP环境1，输出须另选不存在的目录：

```powershell
python scripts/run_cinema_last_stage.py --cache-root F:/Hackathon/projects/16-lut-color --first-folder artifacts/channel-tail-nodes-v1/severe_first --cube artifacts/channel-tail-accept-v2/severe_first.rgb --output artifacts/cinema-last-stage-v2
python scripts/accept_channel_tail_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --models artifacts/cinema-last-stage-v2 --modes candidate --baseline-cube artifacts/channel-tail-accept-v2/severe_first.rgb --suffix-stage4 artifacts/cinema-last-stage-v2/candidate/stage4.slut --library F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll --library-sha256 58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158 --output artifacts/cinema-last-stage-accept-v1
python scripts/archive_cinema_last_stage.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/cinema-last-stage-archive-v2
```

完整输出50MB流只作本地离线证据，不作为新的稀疏模型；历史照片非盲测。本阶段未切默认、未宣称官方阈值或指定服务器成绩。
