# 2³输入/RGB基值差分：唯一离线筛查失败

[阶段说明](../../../docs/stages/2026-10-23-skylake-brick2-rgb-base.md)。固定2×2×2输入块，直接RGB基值加2+2+1差分；完整RGB8及100图离线重建零差，但异常池5,728,896B、总异常8包33.826314%、最差图72.789510%，三个事前资源门槛均失败，停止该方案。

`evidence.zip`保存五份冻结原件原字节：分析脚本、协议、启动、分析结果、退出回执。`manifest.json`绑定成员大小/SHA与核验器身份；不把后补说明、审计、远端快照计入冻结五件。**主表和异常池二进制未保存，原结果仅含其大小/SHA，不能由此声称独立重哈希二进制。**

仅需此目录即可从ZIP复核证据链和统计，不解包或执行原分析、不需NumPy/照片：

```powershell
python report/data/skylake-brick2-rgb-base-profile-v1/verify_archive.py
```

本次`audit.json`另包含六输入完整SHA、100图分片及原artifacts逐字节比较；复现这些额外检查需恢复原件/协议输入并选新输出：

```powershell
python report/data/skylake-brick2-rgb-base-profile-v1/verify_archive.py --repository . --compare-originals --rehash-inputs --output artifacts/skylake-brick2-rgb-base-audit-reproduction.json
```

审计只复算已有原因/跨度/逐图包统计及门槛，没有独立重建colorword、pool或再次解码色域/照片。原分析通过的是离线编码重建，不是候选原生完整域。此阶段新增运行时、编译、候选C ABI、性能及模型调用均为0；没有实际Skylake或三倍吞吐新成绩。
