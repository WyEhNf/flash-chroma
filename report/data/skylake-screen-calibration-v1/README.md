# 同库筛查校准档案

两份`results.json`记录固定次数的同库A/A负对照；`audit.json`复算描述性范围，`manifest.json`保存全部原件长度和SHA，`archive.py`拒绝覆盖。所有A/B使用同一65库和同一句柄，不存在新候选吞吐成绩。

```sh
python3 scripts/calibrate_skylake_same_library_pmu.py --policy experiments/skylake-same-library-calibration-v1.json --output artifacts/new-same-library-calibration
python3 scripts/calibrate_skylake_native_batch.py --policy experiments/skylake-native-batch-calibration-v1.json --output artifacts/new-native-batch-calibration
```

策略绑定原65构建、完整域和库SHA，依赖模型及照片按原路径/SHA恢复。64份短调用样本每次计数后独立SHA；16份长批次样本保存640个内层时间，每批次末SHA而非每内轮SHA。两种时长不同时间段测量，无锁频控温，不能外推Skylake或据此重写旧失败。[阶段说明](../../../docs/stages/2026-10-21-skylake-screen-calibration.md)列出目的、覆盖、结果和限制。
