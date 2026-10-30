# 分输出坐标的原生/性能证据

[阶段报告](report.md)给出当前精度/速度取舍。evidence.zip保存原型与packed的完整native、合成合同、串行性能原始轮次、实测源码/构建及一次应用。models.zip含唯一新模型/初始模型/原2dd与三个等距控制；binaries.zip保存两个实际DLL，GCC运行时依赖按build.json记录，未重复打包。建议按阶段命令从源码构建。

performance.csv按phase与variant区分：第一阶段baseline=原2dd、candidate=首版运行时；packed阶段original=原2dd、baseline=同一候选首版运行时、candidate=同一候选packed运行时。不得跨phase直接用绝对耗时声称加速；最终结论只用packed阶段同机配对比。

四级仅为Velvia与三个不同整数等距控制。三张照片mean及audit RMS的退化在前精度报告保留。新格式尚未接公共CLI/GUI/C99，原型实际多9216字节侧表，不能以逻辑替换的6144冒充实际增量。

大完整RGB流、原图、原LUT和GCC依赖留本地，来源与哈希由各run/plan/build绑定。所有测试/计时范围独立；无官方数据或Threshold。未PR、推送或默认升级。
