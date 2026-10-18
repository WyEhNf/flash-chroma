# a399完整准确性与真实四级性能

[阶段报告](../../../docs/stages/2026-10-19-cinema-current-anchor-accept.md)给出全部核心指标、逐图退化、约束来源与部署边界。

- `full-results.json`：完整色域、百图逐图、合并像素/分组、top128及单级/实际四级独立oracle与原生一致性。
- `accuracy.csv`、`groups.csv`、`per-image.csv`、`regressions.csv`：同范围af974比较，所有逐图退化如实列明。
- `runtime-results.json`、`performance.csv`：同库实际四级、四串行进程原始统计；候选精度更好但约慢46%。
- `summary.json`：静态复算与PR16历史累计比较，引用来源SHA，不新跑模型或计时。
- `post-review-audit.json`：旧100图完整流指标及依赖文件来源补核，没有重跑新模型。
- `evidence.zip`：完整run、冻结政策、实测源码ZIP、直方图、性能worker原始五轮和实际已载DLL路径、来源补核。
- `models.zip`：a399 NPZ、新节点base及必须配套的9216字节侧表、原后三模型和af974首级。base单独不能表达新模型。
- `runtime.zip`：实际已验packed DLL、4个GCC依赖、构建/编译信息；不包含被放弃的地址复用DLL。

大约50MB完整RGB流和原完整LUT/照片留在项目本地缓存与SHA清单中，未重复打包。复现命令见[commands.txt](commands.txt)；已有输出不覆盖，新机器应重建并固定新DLL SHA。完整准确性、运行时正确性、性能与来源补核的目的不同，不能相互替代。未PR、推送或升级默认，实验格式与官方接受状态仍不明确。
