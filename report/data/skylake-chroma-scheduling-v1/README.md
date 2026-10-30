# 66—69原始研究档案

`manifest.json`绑定100个原始文件的长度与SHA；`audit.json`从原始结果复算各版PMU筛查、67墙钟及失败门槛。`archive.py`拒绝覆盖既有档案。归档含库、构建中间文件ZIP、冻结源码ZIP、完整域和原始轮次，不包含可按原SHA恢复的照片与大RGB流。

各版模型与输入身份见`experiments/skylake-{chroma-batch4,chroma-batch4-io,inplace-t0,interleaved}-v1.json`。在独立新输出目录构建、验证：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-interleaved-v1.json --output artifacts/new-interleaved-build
python3 scripts/verify_skylake_interleaved_linux.py --plan experiments/skylake-interleaved-v1.json --build artifacts/new-interleaved-build --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/new-interleaved-full --affinity-cpus 0,2,4,6
```

66/67/68的命名分别为`chroma_batch4`、`chroma_batch4_io`、`inplace_t0`。PMU策略为对应`experiments/skylake-*-pmu-v1.json`，新二进制须先更新build/full/library身份后才能复现，不能伪装原回执。67唯一完整墙钟命令：

```sh
python3 scripts/bench_skylake_chroma_batch4_io_quiet_linux.py --policy experiments/skylake-chroma-batch4-io-quiet-perf-v1.json --output artifacts/new-chroma-batch4-io-wall
```

67的单/四线程纯映射门槛失败；66/68/69增量筛查失败未运行整轮墙钟。首次原件不覆盖，不重复择优。实际为AMD/WSL通用AVX2验证，归档glibc2.43库仅为本机证据，目标Skylake应从源码重新构建。[阶段说明](../../../docs/stages/2026-10-21-skylake-chroma-scheduling.md)给出环境、覆盖、计时口径和限制。
