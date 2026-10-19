# 缓存直接写回的集中验证与负性能结果

[阶段说明](../../../docs/stages/2026-10-20-skylake-packed-store.md)说明数学等价、真实Windows/AMD环境、8组完整色域/百图、性能范围和停止决定。参考/候选均含坐标差与缓存，修订6/9，准备后模型容量同为1797764字节。

`contract-*`、`layout-contract-*`、`cache-contract-*`、`prior-cache-*`保存55+6、88+32、55组原缓存及77组交互合同；交互两库各25400合法合成槽与独立uint64相同。`full-results.json`保存实际模型单级/四级、标量/AVX2完整域、百图、实际缓存合法槽和命中覆盖，未重新拟合。

`performance-worker0..3.json`为唯一80轮原始数据，`performance-results.json`及`gate-recalculation.json`分列原门槛和只读复算。1线程apply中位下降2.5964%，未达3%；4线程增加3.7437%、最差进程增加28.1315%，共五条门槛失败，不删样本或重测。`configuration-integrity.json`只读核对全部16配置实际版本、布局、表和容量一致，无新原生调用。

`cfg-analysis.zip`包含首次通用检查拒绝、初步及完整CFG清点、全部两处路径、完整MCA日志/源和控制器。候选一处循环的无条件回跳必须计入；不能把通用线性检查器漏掉的路径当作不存在。静态周期估计虽改善，实测仍失败。`initial-inspector-refusal.json`解释检查器适用范围和未重编译的后续处理。

冻结计划、源码原字节、实际库/依赖、构建、准备及全部验证/性能命令均保留。无Skylake实测、官方数据/Threshold或派生缓存许可，不变更默认或现有四方案服务器包。
