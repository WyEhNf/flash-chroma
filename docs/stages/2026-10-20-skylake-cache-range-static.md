# 缓存范围检查的数学简化：静态收益不足，未执行数值或性能

Agent：Codex；Operator：WyEhNf；Task：减少缓存边界判断及YMM活跃值；Status：Completed（静态研究停止，不采用，原型未通过运行验收）。

参考为已通过本机门槛的“无损坐标差+有界缓存”后端，候选只改变AVX2缓存判断和未命中恢复，不改模型、表预算/余量、建表或插值。参考的运行包装及AVX2对象与上一阶段候选逐字节相同。实现独立在`experiments/skylake-cache-range-runtime`，私有`jshc_cache_range`描述符和C ABI修订7；已验组合源码、公共默认、冠军、CLI/GUI/C99、AGENTS.md未变。

## 证明条件与实现

合法首级四面体插值的四个Q16权重非负、总和65536，R输出是四个R节点的凸组合。节点为整数，half-up后仍在首级全部节点的R最小/最大值之间。构造器正好用该全节点范围生成缓存R维，所以两个R比较在此条件下冗余；不能把缓存R范围改为较窄的样本估计后继续使用此证明。

G−R/B−R仍须检查。对`offset=(G−R)−dg_min`及B对应量，RGB8与缓存边界保证偏移在[−510,510]；span在[0,510]。有符号16位压缩无损，负数的16位表示按无符号解释至少65026，大于span。因此无符号饱和减法`subs_epu16(offset,span)`为零，恰等价于原偏移在[0,span]。以相同顺序打包两个span，最后测试整个256位结果为零，可合并8像素的G/B上下界判断。

指令语义核对本机GCC15.2头文件，以及[LLVM的有符号压缩/无符号饱和减法说明](https://clang.llvm.org/doxygen/avx2intrin_8h.html)、[Intel的VPTEST说明](https://www.intel.com/content/dam/develop/external/us/en/documents/cpp_compiler_classic.pdf)。算法的上述范围证明由本阶段推导，不能用有符号饱和减法或仅看符号位的movemask替代。

主路径在首级后直接以三个偏移保存Rgb，命中则直接计算索引；未命中时还原`R=rOffset+rmin`、`G=gOffset+gmin+R`、`B=bOffset+bmin+R`后计算原后三层。目的是少保存旧RGB和六条边界常量，实际是否减少寄存器压力以汇编为准。

## 静态检查与停止决定

目的为数学条件、构建/对象及生成代码潜力，不加载候选、不映射像素或计时。实际环境Windows11 26200 x64 / AMD Ryzen9 8945HX，Python3.12.14标准库、MinGW GCC15.2、LLVM-MCA21.1.0。Release AVX2 TU仍为`-mavx2 -mtune=skylake -ffp-contract=off`，没有全局march、AVX512、FMA或fast-math。按冻结计划同时构建两库后检查全部两处同形全命中循环，不选择较好的一处。

| 指标 | 参考两处循环 | 候选两处循环 |
| --- | ---: | ---: |
| 指令数 | 262 / 267 | 249 / 254 |
| gather | 15 / 15 | 15 / 15 |
| 含rsp操作数 | 38 / 43 | 36 / 41 |
| 循环内调用 | 0 / 0 | 0 / 0 |
| MCA 100次Total Cycles | 23829 / 23829 | 24332 / 22533 |
| MCA 100次Total uOps | 38500 / 38400 | 37400 / 37300 |
| MCA Block RThroughput | 86 / 83.5 | 85 / 82.5 |

指令各少13条，但模型总周期一处增加2.11%、另一处减少5.44%，吞吐下界仅改善约1.16%/1.20%，实际栈操作只少2处。未形成一致且足够明确的时间收益依据，故停止于静态阶段。没有执行任何有限数值合同、完整256³、100图或性能比较；数学推导和编译成功不替代实现正确性，也不能据此断言真实硬件更慢。MCA不包含真实缓存/GDS、分支预测、准备或系统干扰。

为未来目标硬件验收准备了`verify_skylake_cache_range.py`：计划使用R范围[32,223]、G−R范围[1,9]、B−R范围[−2,2]，分别验证边界内外1码、两个向量半区、非对齐/尾部/4096块边界及未命中RGB恢复。后缀使用整数网格上的可逆仿射变换，避免错误索引被相同输出掩盖。该程序**未运行**。原差值/交互合同辅助程序仅新增显式`reference_delta16`口径，以支持两端已经编码时检查相同布局/容量；新分支同样未运行，不改旧默认分支或冒用旧数值回执。

冻结计划为`experiments/skylake-cache-range-v1.json`。构建用统一`build_skylake_runtime.py`，静态入口为`inspect_skylake_cached.py --reference-gathers 15 --candidate-gathers 15`；旧18/15默认保持。准确命令、源码原字节、两库/对象、完整汇编、全部MCA原日志及头文件SHA见[原始证据](../../report/data/skylake-cache-range-static-v1/README.md)。历史实验继续使用各自源码ZIP，不把新辅助脚本换行/哈希冒充历史来源。

本判定族不继续扫变体或参数，除非目标硬件给出新的实测依据。接下来将已验的组合方案纳入服务器同次比较；静态停止原型不进入服务器默认评测矩阵。具体Skylake/官方规则仍待验收，现有组合的本机收益保持原结论。

后续[直接写回阶段](2026-10-20-skylake-packed-store.md)在修订6/9上执行并通过了辅助合同“参考也已编码”的分支；这只补充该辅助分支的实际运行证据。修订7本体及其边界原型仍未加载或通过数值验证，本阶段静态停止不变。
