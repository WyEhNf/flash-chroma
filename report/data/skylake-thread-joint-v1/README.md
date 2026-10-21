# 71原始完整域与受控长批次档案

`manifest.json`绑定102份原始文件的长度与SHA。`audit.json`从四份worker原始数组独立复算1920内轮、配对比及A/A控制；`confirmation-decision.json`绑定首次失败结果，确认执行为0。`archive.py`拒绝覆盖既有档案。

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-thread-joint-v1.json --output artifacts/new-thread-joint-build
python3 scripts/verify_skylake_thread_joint_linux.py --plan experiments/skylake-thread-joint-v1.json --build artifacts/new-thread-joint-build --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/new-thread-joint-full --affinity-cpus 0,2,4,6
python3 scripts/bench_skylake_long_controlled_linux.py --policy experiments/skylake-thread-joint-long-perf-v1.json --output artifacts/new-thread-joint-long
```

性能策略绑定原plan/build/full/validation/script SHA，新构建须重新绑定，不能冒充旧回执。原照片和大RGB流按计划中的SHA恢复。所有原件不可覆盖或反复择优；独立确认只按首次执行前冻结的条件决定。

完整RGB8及有限/保护页/对齐/API检查通过，但首次纯映射1/4线程均未达三倍，A/A控制通过，整体失败并跳过确认。48批次末完整输出SHA，非1920内轮逐轮独立SHA。实际AMD/WSL2、GCC15.2通用AVX2，不外推Skylake；归档glibc2.43库只作本机证据，目标端应重新编译。[阶段说明](../../../docs/stages/2026-10-21-skylake-thread-joint.md)列出环境、目的、结果和限制。
