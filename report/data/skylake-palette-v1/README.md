# 修订22对16：原始证据与复现边界

[阶段报告](../../../docs/stages/2026-10-20-skylake-palette.md)解释原理、完整结果、代价和未验收事项。Windows/AMD唯一80轮配对apply吞吐提升84.99%/90.62%，copy+apply为79.46%/66.71%；完整输出保持一致。这些不是Skylake实测。

- `performance/worker0..3.json`保存全部原始轮次、实际库/依赖、CPU集合与逐轮SHA；`results.json`为预定配对统计，`audit/results.json`独立标准库复算，不重新计时。
- `base-contract`、`cache-contract`、`domain-contract`、`packed-contract`、`signed-contract`、`fallback-contract`分别记录通用合同、新编码独立全表重建、正负斜率及6249色拒绝回退。`full`是Windows完整256³/100图，`linux-full`是WSL/AMD的12组完整域与528次有限比较。
- `windows-build`和`linux-build`含构建日志、参数、测量源ZIP、实际二进制和对象；`static`保存完整新函数反汇编及ISA检查。`linux-fallback-object-proof.json`另核对两个旧回退对象身份。
- `profiles`只有只读结构剖面，包含低收益投影、游程和调色板覆盖，没有新增候选计时。`failed-full-v1`、`failed-fallback-contract-v1`保留两次验证器失败、源快照和修复说明，不冒充成功回执。
- `fixed-models.zip`按原路径保存四个小稀疏模型和首级坐标侧表。`large-input-identities.json`给出三个大流身份；它们可从已有`skylake-domain-server-v2`完整本地包按SHA取出。这个5.4MB证据目录是小档案，不是无需额外数据的完整服务器包。
- `remote-check.json`及`remote-snapshot.zip`保存创建Draft前相关协作意见、分页与修复祖先检查，剔除API临时克隆元数据字段。`manifest.json`核对112份原始文件，不自包含，也不包含后加的说明/独立审计回执。

源码ZIP保留测量时原字节。packed验证器初版的一个源键是Windows绝对路径，实际ZIP成员名映射见`archive-audit.json`；不能因此改写旧SHA。构建/运行目录是历史真实路径，跨机器应使用新的目录和回执，不宣称本机DLL/.so可直接在另一系统运行。

只读核对归档的入口：

```sh
python3 -I -S scripts/audit_skylake_palette_archive.py --archive report/data/skylake-palette-v1 --output artifacts/palette-archive-audit-new.json
```

完整复现先按ZIP和大流清单恢复输入与源字节，再运行阶段报告中的构建/验证命令。性能脚本需要NumPy/Pillow/psutil；Linux完整输出验证只需Python标准库。旧性能策略绑定Windows构建与完整验收，服务器必须重新固定自己的构建、环境和正确性回执，不能篡改旧策略或回执来代替移机实验。
