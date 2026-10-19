# 布局双库服务器包与WSL正确性证据

[阶段说明](../../../docs/stages/2026-10-20-skylake-layout-server.md)记录目标、环境、一次Linux验证及未执行范围。原生修订4/13源不变，Windows80组的回退失败保持；本阶段没有正式性能比较或Skylake实测。

`correctness.json`包含3432次有限比较、候选209600物理槽、20条失败保护、12组完整256³、8个调度配置各两轮100图的零差结果、命中/回退证据及实际团队/已加载库。`results.json`明确`performance_measured=false`、采用判定为空。计时器调度验证经过原生时钟，但时长没有用于性能比较。

`bundle-manifest.json`及`fixed-small-packet.zip`保留119文件的完整清单、源码与小型独立金标准；缺少235929600字节照片及两个50331648字节完整流，不能只解压小包就运行，可按`archive-verification.json`列出的相同路径/SHA从旧四方案包补齐。可直接传输的完整ZIP在本地`artifacts/skylake-layout-server-v2.zip`，188665684字节，SHA `7545e222bedc5eacddd39082c92583902ea810ef1dbf11984ea85b8227359730`，不把原始大流提交Git。

`linux-builds-and-binaries.zip`保存实际Linux库、原生计时器、构建参数及原字节源快照；根目录的构建/验证命令回执保留stdout/stderr。`import-preflight.zip`保留v1在任何构建/原生调用前因漏带绑定脚本的拒绝、原v1源和v2导入通过；v2增加了目标端传递导入闭包检查，没有修改或重试v1包。`archive-verification.json`由只读归档器核对源、覆盖和哈希，不新调用内核或性能。未来显式160组性能分支尚未执行。
