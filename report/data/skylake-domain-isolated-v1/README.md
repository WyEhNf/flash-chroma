# 修订16：逐单元证明及隔离快路径的完整本机验收

[阶段说明](../../../docs/stages/2026-10-20-skylake-domain-proof.md)给出算法、第一版失败、实际环境、统计及边界。相对缓存修订4，1/4线程apply配对中位比0.929333/0.949019，通过预声明本机门槛；不是Skylake成绩或总体显著性。

`contract-*`、`cache-contract-*`、`domain-contract-*`和`full-*`分别保存基础、全部缓存槽、证明/拒绝状态、完整实际256³/100图验收；全程相同冻结模型与二进制，零字节差。实际证明界与独立NumPy32768单元一致，模型持久容量1800836字节保持。

`performance-*`保留四进程全部80轮100图；每个原始记录含5条完整输出SHA，`configuration-audit.json`独立核对16配置/80哈希及源/模型/表容量，`gate-recalculation.json`从原始轮次复算全部门槛。四线程一个copy+apply进程微退化仍在原始记录中，没有删样本。

`static-results.json`、`complete-static-analysis.zip`及`objects-and-controller.zip`保存新循环、原回退对象相同证明、全部MCA与唯一顺序控制器；构造/入口成本由实际基准承担，不称为零。`binaries-and-core.zip`与`build-measured-source.zip`绑定真实库和源码，`cache-fixture-bytes.zip`保存有限窄带模型/侧表，原模型输入仍沿用既有归档。

实际Windows11 26200 / Ryzen9 8945HX / GCC15.2 / AVX2，CPU0/2/4/6、1/4线程；未锁频控温。新逐轮哈希协议不与旧内部5轮绝对耗时混用；公共默认、质量模型、核心/CLI/GUI/C99与AGENTS.md不变。
