# Filmic06直接单调约束的独立证据

本目录对应artifacts/filmic-direct-monotone-v1，与首轮静态计划分开。仅修正17³三处input134，放宽的是静态中点充分区间，原±4096总偏移、实际单调、节点/idx/grid/端点保持。

evidence.zip保存独立run、全部768码解析结论、完整结果、100条逐图记录及原始字节审计。唯一新模型为m17-direct-monotone.slut。五个实际单级后端全域及AVX2实际百图一致，全部误差为0。

run.py是实际小阶段入口快照，应恢复至记录的artifacts/filmic-direct-monotone-v1/run.py路径运行，不能直接从本归档目录执行。计划依赖首轮同SHA文件；大参考和像素流不入库，来源及SHA保留在plan和回执中。

严格可分离Filmic06特例，不代表其他来源、一般3D LUT或四级比赛链。没有官方Threshold通过或默认升级结论。
