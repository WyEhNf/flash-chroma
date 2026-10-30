# 修订53—55原始证据

三版完整RGB8等价，单线程预定筛查均失败，未进入整轮性能。整体300%目标未完成；详细方法、环境、结果和限制见[阶段报告](../../../docs/stages/2026-10-21-skylake-direct-tiles.md)。

`manifest.json`固定72份原始文件（3,901,123字节）；9份`measured-source.zip`核对681项源成员，构建ZIP核对57项二进制/对象。`research-audit.json`独立核对72组完整域、12项单次计数；`interim-research-audit.json`保留53/54完成时的先行复核。`screen-decision.json`记录每版停止决定，没有被省略的整轮计时。

`construction-and-validation-generators.zip`保存构造、验证和顺序执行工具；仅用于溯源，不在原测量目录重跑覆盖。模型复用`report/data/skylake-palette-v1/fixed-models.zip`，大输入流依各计划SHA恢复。55仅像素TU用Clang22.1.2，版本、路径、SHA及显式旗标分别在build/计划/CMake中。

`remote-snapshot.zip`是创建前完整协作快照，`expected-pr52-body.txt`保留前一阶段原发送文本。README、交付元数据、静态检查和最后操作前刷新在原始清单生成后添加，不混入原始计数。归档校验不调用像素核：

```sh
python3 -I -S scripts/audit_skylake_direct_tiles_archive.py --archive report/data/skylake-direct-tiles-v1 --output artifacts/new-direct-tiles-archive-check.json
```
