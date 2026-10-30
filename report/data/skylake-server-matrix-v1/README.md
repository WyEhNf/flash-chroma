# 原版、无损坐标差、精确缓存及组合的同场证据

[阶段说明](../../../docs/stages/2026-10-20-skylake-server-matrix.md)给出真实环境、计时范围、全部比较、失败与复现方法。本轮实际为Ryzen9 8945HX的WSL2/Linux，不是Skylake服务器。

`correctness.json`保存4224次有限独立整数比较、64条布局失败保护、24组完整256³及16组100图调度的零差结果；实际两个缓存全表185600槽与独立uint64导出SHA一致。`cache-gold-generation.json`及`frozen-small-packet.zip`保留独立导出来源和小输入；没有拟合新模型。

`worker0..3.json`是唯一四进程320轮100图组的全部原始数据，含2000个逐图区间/角色/线程；`performance.json`分列整批、逐图、1/4线程和四种直接比较。只有原版→缓存四场景全过门槛。组合四线程整批worker3五轮持续明显变慢，坐标差四线程逐图也失败；不删样本、不重测，`results.json`的程序完成不表示全部性能门槛通过。

`recalculation.json`为Windows Python3.12.14标准库只读复算，无新增像素/原生/性能调用。`policy.json`绑定集中验证，`performance-policy.json`另绑定验证回执；各worker绑定后者，两份SHA按原语义保留。`binaries.zip`存实际四库及计时器，系统依赖的实际路径/SHA见worker。两个构建的原字节源码ZIP、派生计划和全部构建日志均保存；原生源码与历史已验计划相同，不将历史辅助脚本身份冒充当前版本。

`packet-identity.json`保存本地188MB传输ZIP及三个未入Git大流的SHA。其余固定源码/小输入在`frozen-small-packet.zip`；包内同名参考库的绝对加载路径、含空格目录、唯一OpenMP运行库和实际线程落点均已核对。模型、照片的来源和用途约束继续适用，未宣称官方数据/Threshold或派生缓存许可已取得。
