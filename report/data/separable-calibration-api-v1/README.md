# 通用精确单调坐标入口的集中合同

结果为11项通过，包括轴置换/共享轴、下降/常量、端点/偏移保护、逐码可达但全局单调冲突、完整节点张量检查，以及Filmic17/33历史零误差模型SHA精确复现。没有新增其他来源全域或百图测试。

run.json绑定实测模块和合同脚本SHA及实际环境；results.json保留明确失败见证和两个模型SHA；measured-source.zip保存对应源码。当前核心集成由根代理处理，未修改默认方法扫描。

复现入口为scripts/verify_separable_calibration.py。其小型历史夹具来自上一个filmic-calibration-v1精简包：将两个baseline模型、source-curves.npy和evidence.zip中的preparation.json按记录恢复至artifacts/filmic-calibration-v1，即可执行合同，不必恢复50MB完整参考或百图流。也可先用原prepare入口按同SHA来源重建这些夹具。合同目录已存在时不覆盖。
