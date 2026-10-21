# 精确块字典原始档案

`manifest.json`绑定22份原始文件的长度与SHA。`audit.json`复算完整RGB8、物理字典、持久容量、单线程周期比与PMU缺失范围。`archive.py`拒绝覆盖档案。`failure-receipt.json`保留原执行退出码、联合断言和缺失配置；没有补造完整`results.json`或4线程比值。

冻结构建/验证命令（新输出目录）：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-block-dictionary-v1.json --output artifacts/new-block-dictionary-build
python3 scripts/verify_skylake_block_dictionary_linux.py --plan experiments/skylake-block-dictionary-v1.json --build artifacts/new-block-dictionary-build --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/new-block-dictionary-full --affinity-cpus 0,2,4,6
```

PMU入口`scripts/profile_skylake_block_dictionary_pmu.py --policy experiments/skylake-block-dictionary-pmu-v1.json --output artifacts/new-block-dictionary-pmu`绑定原build/full/library SHA，新构建须重新绑定，不能冒充原结果。原样本不可覆盖或重复挑选。本阶段单线程失败、四线程系列未完成，未执行整轮墙钟。

实际AMD/WSL2、GCC15.2与通用AVX2；归档glibc2.43库仅作本机证据，目标Skylake须重新编译。[阶段说明](../../../docs/stages/2026-10-21-skylake-block-dictionary.md)记录目的、覆盖、失败和限制。
