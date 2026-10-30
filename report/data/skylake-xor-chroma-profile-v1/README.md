# 相邻通道异或布局只读筛查

Agent：Codex /root；Operator：WyEhNf；Status：Failed（两项布局门槛）。

单次固定布局 `h=R|((G xor R)<<8)|((B xor G)<<16)`，原R低16MiB表作为同输入对照。100张1024×768 RGB8，从每图像素0起取连续64像素窗口，共1,228,800窗。新布局平均51.754069行，旧49.415259行；比1.047329717，最差图1.323871689，超过事前0.80/1.05门槛。停止，不构建原生或扫描变种。`pass=true`仅指统计完成和索引数学证明；`native_implementation_warranted=false`才是方案决定。

Windows11 / Anaconda Python3.13.12 / NumPy2.4.6，CPU AMD64 Family25 Model97。全部16M索引的正逆和范围零差；100图逐图输入SHA通过。页编号改变，不沿用旧页布局结论。该证明不是RGB8映射精度，不是cache miss或吞吐实测；native/performance/compiler调用均0。

`manifest.json`包含9份原始文件：分析、事前协议、开始/退出、stdout/stderr、结果及两个准备/执行辅助。`audit.json`从原JSON重新求直方图、100行总和、比值、最大值与门槛，并核对源/协议/日志及三输入SHA；没有重跑原统计或独立重新生成行集合。`archive.py`为当时归档辅助原字节，需放回artifacts原路径才能解析根；不应向已执行目录重复运行。

历史唯一运行命令：`python artifacts/run_xor_chroma_profile.py`。复现统计应在隔离检出恢复同SHA照片、manifest及旧R/B profile，先恢复两个辅助至artifacts，再生成尚不存在的目录；禁止覆盖本次原件。缺少大输入的单独克隆不能完整复跑。

整体单/四线程三倍目标、实际Skylake、官方派生表许可/预算及Threshold仍未完成。另见[阶段说明](../../../docs/stages/2026-10-23-skylake-base-delta-profile.md)。
