# 有符号坐标差无损压缩的完整证据

冻结a399模型输出逐字节不变；本机1/4线程apply配对耗时下降12.0053%/8.1046%，copy+apply也改善，预设本机门槛通过。准备后容量减少3072字节。[阶段说明](../../../docs/stages/2026-10-20-skylake-delta16.md)列出目的、实际环境、整数范围证明、统计方法、失败保护与限制。没有Skylake服务器成绩。

`plan.json`、`build-measured-source.zip`保存最终v2测量源码原字节；`build-static-v1-evidence.zip`保留数值调用之前的静态v1来源，`build-static-object-equality.json`证明两版本AVX2对象一致。`design-ranges.json`记录实际侧表的差值范围。`binaries-and-core.zip`保存同次两库与依赖，不把不同构建SHA混用。

`contract-*`为55组既有合同及6条拒绝；`layout-contract-*`为88组差值专项合同、32条诊断失败保护与生成夹具；`full-results.json`为单级/四级完整256³及100图逐图回执。全色域、模型、侧表及照片身份由计划和各结果逐层绑定；模型复用PR42的`report/data/cinema-current-anchor-accept-v1/models.zip`。

`performance-worker0..3.json`保留全部80轮与实际库/线程/核集合、源字节哈希、布局诊断和准备成本；`performance-results.json`给出配对统计，`gate-recalculation.json`仅用旧轮次独立复算门槛，没有重新计时。`performance-run.json`保存预冻结策略。旧绝对路径是执行来源，复现请恢复测量源码原字节、按计划SHA检查输入并使用新输出目录。

v1只做构建和静态分析，补齐测试极值后才以v2进行唯一集中数值及性能验收。模拟不等于硬件实测，本机通过不替代最终Skylake与官方规则验收。没有新的拟合、精度选型、自然图独立盲验或全压力扫描。
