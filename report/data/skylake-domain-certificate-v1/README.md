# 完整输入域的单元区间证书

[阶段说明](../../../docs/stages/2026-10-20-skylake-domain-proof.md)解释有符号斜率、坐标区间及RGB8 floor/ceil处理。`global-results.json`保留全局界需11码的失败；`cell-results.json`和`all-cells.npz`保留全部32768个可达单元及其区间，固定原缓存范围下零未证明单元。

`observed-results.json`只重读已验16777216色首级流，确认全部缓存命中及实际极值；不把观察代替通用构造证明。`sources-inputs-preflights.zip`保存三个分析源、小型模型/侧表、原错误字段与输入/输出含义拒绝、冻结脚本字段拒绝及其修正记录，没有新映射或性能调用。

实际Windows11/AMD、Python3.12.14/NumPy1.26.4。原生成器/流SHA及所有输入身份在结果内；数学通过不是新C++或目标服务器通过，后者见独立合同/完整域记录。
