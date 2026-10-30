# R连续精确后缀缓存：完整正确，唯一性能比较未通过

[阶段说明](../../../docs/stages/2026-10-20-skylake-r-contiguous.md)给出目的、实际环境、固定口径、全部结果与限制。参考修订4、候选修订13，表值/范围/容量相同；1/4线程配对中位耗时下降3.29%/6.84%，一个四线程进程回退3.24%而超过2%，所以不采用、不重测。

`performance-*`保存唯一80组及各进程全部轮次；`gate-recalculation.json`独立从原轮次复算同一失败。`contract-*`、`cache-contract-*`、`layout-contract-*`及`full-*`分别保存基础55+6、缓存55/24000合法槽、209600真实存储槽与20条失败保护、8组完整256³及100图零差。`performance-configuration-audit.json`另从全部16个真实计时配置核对修订、容量和固定输出。

`cache-layout-profile-summary.json`及`profiles.zip`保存固定已见100图的2490个访问键和16种基址余数剖面：半字压缩没有足够局部性收益而未实现，R连续排列逐块行数明显减少；不把行数当cache miss或实测提速。

`initial-static-results.json`保留最初交叉错配而拒绝的静态门槛。`dispatch-proof-summary.json`、`validation-plan-v2.json`与`complete-static-analysis.zip`保存View静态断言、16组分派证明及逐语义配对修正；修正在任何候选加载或计时前完成，C++未改/未重编译，未改变实测门槛。两种MCA消费同一AVX2，不启用AVX512。`build-*`、`binaries-and-core.zip`、`fixture-bytes.zip`及`controllers.zip`保留原字节源码/库、夹具与命令。各清单SHA绑定实际字节，Git换行不同时应恢复源码快照。

默认和旧四方案服务器包不变；未取得Skylake实测或官方规则许可，没有新拟合、精度或SOTA结论。
