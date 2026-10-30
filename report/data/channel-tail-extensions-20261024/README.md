# max负结果与运行时资格

[阶段报告](../../../docs/stages/2026-10-24-tail-max-extensions.md)说明完整边界。`max-run/summary/contract.json`为冻结两扫、训练完整支撑结果和独立gain合同；`negative-fit.zip`保留所有16批及未升格模型；`last-stage-probe.json`为正式incumbent116个max颜色的末级局部证书；`runtime-eligibility.json`为85/87实际构造信息，0映射/0性能调用。`source.zip`及manifest保存原脚本和SHA。

复现均在首阶段工作目录、原Python3.12环境，设置Numba4及BLAS/MKL/OMP环境1，输出另选不存在的路径：

```powershell
python scripts/verify_channel_max_nodes.py --output artifacts/channel-max-contract-v1/results.json
python scripts/run_channel_max_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --initial artifacts/channel-tail-nodes-v1/severe_first/model.npz --output artifacts/channel-max-nodes-v1
python scripts/probe_cinema_last_stage.py --cache-root F:/Hackathon/projects/16-lut-color --initial artifacts/channel-tail-nodes-v1/severe_first/model.npz --cube artifacts/channel-tail-accept-v2/severe_first.rgb --output artifacts/cinema-last-stage-probe-v1/results.json
python scripts/inspect_tail_runtime_eligibility.py --cache-root F:/Hackathon/projects/16-lut-color --libraries F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_compile.dll F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll --candidate artifacts/channel-tail-nodes-v1/severe_first --output artifacts/tail-runtime-eligibility-v1/results.json
```

85/87 DLL、GCC依赖与构建源码由速度分支另行保存，本目录只存实际读取的SHA与只读资格回执；不能把未打包的DLL当作已随本包交付。
