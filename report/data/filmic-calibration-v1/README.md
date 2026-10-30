# Filmic06静态坐标校准的精简证据

本目录对应artifacts/filmic-calibration-v1，保留原始report.md快照、冻结计划、四模型、实测源码快照和完整元数据。原报告中的“本目录”及大文件路径指原artifacts目录。

evidence.zip包含run/preparation/full-results、summary、400条逐图CSV、原始字节审计及两尺寸的全部逐码区间/重建诊断。另存896字节source-curves.npy，保留完整三轴原始RGB8标签，便于小合同复现。manifest.json逐项绑定复制文件和ZIP成员SHA，归档完整性检查0差异。

完整参考50MB、完整像素流及原生百图流不入库；其SHA、命令和来源保留在证据中。新克隆需按冻结来源合同恢复这些大文件，不能把本归档假装成已携带全部像素。

33³在原静态区间中完整域及百图全部零误差；17³仍有三处通道码值被静态边界阻断。后续direct-monotone阶段另存，不回写这一阶段的判定。
