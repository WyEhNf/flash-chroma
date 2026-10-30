# 分输出通道坐标实验归档

唯一固定9块DP候选在原选择样本入围：相对2dd，cube mean下降5.9062%、照片mean下降3.9146%，cube p99下降；相对实际iter003起点，本轮增量仅0.3883%/1.2745%。没有把前阶段累计收益全归新表示。

[报告](report.md)、[计划](plan.json)、[运行身份](run.json)、[选择结果](selection.json)、[优化记录](optimizer.json)、[清单](manifest.json)保存完整口径。channel-coordinates.npz是实验表示，包含nodes/shared_idx/channel_frac[3,3,256]/grid和来源SHA；不是SLUT。measured-source.zip保存实际来源；contract-results.json及contract-source.zip保存集中合成合同；initial.slut/baseline.slut分别绑定优化起点与固定验收基线，prior-selection.json保留前阶段进度。

模型frac payload增加6144字节，可能需要更多运行时权重计算；压缩NPZ不能与未压缩SLUT比较后声称更小。没有C++、新全域流、完整独立oracle、100图或性能测试。训练完整域缓存重算只是拟合不变量，不替代这些终验。候选已交主代理另行决定原生落地/验收，本轮不继续加扫。

集中合同覆盖m17/m33复制与独立u64；m17九种通道/轴各65537状态的成本/cap、单调/端点和当前其它输出缓存。真实训练cap0。20张guard逐图并非全不退化，且历史已见，不称盲测；完整数据见报告。旧2dd固定坐标严格下界不能外推到此新表示。

复现需要计划中同SHA的原frozen-samples.npz和envelope-caps.npy，不重新解码照片。精简归档不重复大型训练缓存或50MB原表。没有修改既有模块、根driver、核心或默认，也没有提交推送PR或官方/SOTA结论。
