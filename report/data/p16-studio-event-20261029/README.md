# 工作台与赛前集成证据

[阶段说明](../../../docs/stages/2026-10-29-studio-event-ready.md)。

- manifest.json记录原始回执和最终源码快照的逐成员SHA/尺寸。
- raw-evidence-and-source.zip保留原字节；包含初次启动器观测失败及随后成功回执，不覆盖历史记录。
- http-verification.json、event-verification.json、cpp-verification.json、frontend-verification.json可直接阅读。
- package-receipt.json与package-self-check.json描述已生成的本机v2调试包及真实运行；159MB素材包留在本机artifacts，不上传到代码仓库。
- verify不重跑图像/拟合/性能：python scripts/archive_studio_event.py --verify。

正式Threshold、协议与目标机未知；本机功能测试不能替代赛事精度/速度或实板验收。早期回执保留其当时源码SHA；最终计数门禁55项、打包7项和复制回调6态另有各自证据。
