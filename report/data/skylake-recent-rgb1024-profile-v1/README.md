# 精确输入色备忘：唯一离线筛查失败

[阶段说明](../../../docs/stages/2026-10-23-skylake-recent-rgb1024.md)。固定1024项、指定hash、每65536像素清空，完整100图共1200块；总hit24.963894%、最差图2.963003%、块内hit/miss转移率16.495668%，三项事前门槛均失败。停止此方向，不调整容量、hash、窗口或门槛重跑。

`evidence.zip`保存五份原件的原字节：`analyze.py`、`protocol.json`、`execution-start.json`、`analysis.json`、`exit.json`。`manifest.json`绑定成员、源路径、大小和SHA；约1.68MB结果压入ZIP，避免巨大JSON文本diff。清单不包含后补说明、审计或自身。

仅需本目录文件，即可从ZIP复核身份及100图/1200块统计，不解包、不执行原分析，也不需要NumPy或照片：

```powershell
python report/data/skylake-recent-rgb1024-profile-v1/verify_archive.py
```

`audit.json`另记录本次实际执行的原件逐字节比较、两输入完整SHA及100图分片SHA重哈希；复现这些额外检查需恢复协议中的输入和原artifacts，另选新输出路径：

```powershell
python report/data/skylake-recent-rgb1024-profile-v1/verify_archive.py --repository . --compare-originals --rehash-inputs --output artifacts/skylake-recent-rgb1024-audit-reproduction.json
```

独立审计核对逐块分类/run数/最长run、逐图精确run直方图及其全局加总、转移分母和门槛；未从照片重新计算命中。原件未保存逐块完整run长度直方图，不能宣称独立重建它。24.96%命中不是实际周期节省，转移率不是分支错判率。本阶段新增运行时、编译、候选原生性能、模型或完整域执行均为0；实际Skylake及整体三倍目标未完成。
