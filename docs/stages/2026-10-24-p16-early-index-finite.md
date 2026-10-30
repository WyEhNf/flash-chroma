# 第16题速度研究：准备索引展开的有限阶段（修订101）

Agent：`/root/speed`。分支`codex/p16-speed-20261023`，父提交`59ef3db622824e357835db69dc9a18ed129ef9a0`。本阶段仅交付静态整数证明、唯一构建/机器码与唯一私有有限合同。没有新整链全域、照片或性能；不能从768B栈帧或有限通过推断速度、精度提升或50%资格。

## 目标与改动

以100固定B批扫描线prepare为父。将cache索引`(R-r0)*Wg*Wb+(G-R-dg0)*Wb+B-R-db0`精确展开成`R*(Wg*Wb-Wb-1)+G*Wb+B+bias`，`bias=-r0*Wg*Wb-dg0*Wb-db0`。每channel仍先按原四面体Q16独立舍入RGB8，R/G结果分别加入索引后离开源码局部作用域，尝试缩短RGB结果活跃期。

公开apply kernel、节点、四面体排序、舍入、5/9总gather、ID/palette、默认/2²⁶门与prepare256批不变。生产包装器只改变两处私有调用名与revision101。原100九个对象（包含原97八对象和100扫描线prepare）实际逐SHA全同；100执行源/库/证据未改。

静态证明覆盖全部原接受cache的更大方盒：R/G/B和r0在0..255，dg0/db0在−255..255，Wg/Wb在1..511。alpha在[−1,260609]，bias在[−66716415,130560]，按源码顺序R乘积、加入bias、加入G乘积、加入B均在int32内部；最终保守界[−66716670,66716415]。证明负alpha及正/负bias，标量bias先用int64再转int32。安全整数界不能代替原domain证明：只有实际合格RGB才允许gather。

完整证明、入口前置、所有权及未测试范围在`experiments/p16-early-index-draft/静态预注册.md`，最终计数在`experiments/p16-early-index-有限预注册.md`。当前constructor的目的direct表和全部来源独立所有，固定完整B批仍唯一新入口；其他合法参数回100再沿其旧fallback，不承诺原非法范围。

## 唯一构建与实际负证据

环境Windows x64、Ryzen9 8945HX、GCC15.2、CMake4.2、Release/C++17，AVX2、`-mtune=skylake -ffp-contract=off`，唯一`-j1`生产DLL/私有EXE构建。构建前219来源冻结SHA为`0803366eafad0bcfd00c69398572fcab518871ff57141fe2b50d6cf47b209e78`。

DLL SHA `c9bc60e9e34d60ee69a0ec3b0405256afe97a5b10c689bbee61dc63dcc787ed6`；有限EXE `6d6bffa20d5eb028d0931ad1fefbd63b3c352817f38691d16293ad66518aff22`。新object `48aceb20f4ce82972892ee7e04f262cc684be5341c1c25bea495ad7d2a8bdccf`。九旧对象逐字节核对通过。

实际shared/nonshared仍5/9 gather，新TU无call、无aligned YMM rsp存储，外部仅父100 void fallback。跨TU全部void、内部向量helper强制inline，未新增已证的Win64 hidden-YMM-return故障形式。

实际`.su`为768B，父100为704B，增加64B；缩帧预期没有成立。帧包含Win64保存XMM6..15的160B以及批/行常量和中间值，不能把768B全部称内环spill，更不能由帧变化定量断言快慢。本阶段不做MCA或计时，也不按静态结果另换一版。

## 唯一有限合同与计数

构建/机器码回执先由root审阅，再另授有限native一次执行。原100的12 Views保留，另8合法手工cacheView覆盖alpha−1且bias正/负/零、R255/G0/B0、1×511、511×1、511×511窄R盒和黑端点。手工表有合法输出域、owned储存且不超262144词预算；不冒称原halo启发式实际会生成这些极值盒。

20 Views各B=0/127/255三完整批、八个固定合法fallback，六目的偏移0/1/3/7/15/31。显式候选1320+父100参考220=1540调用；独立四项uint64 oracle和父100各3,938,560像素，候选23,631,360像素。1540输出canary、1540输入只读检查、180个axis地址mod32=4全过。负alpha6 Views、正bias2、零bias2全部实核。

额外93,312纯地址例只比较旧/新int64代数与每步int32运算，包含预算外/不相容证明方盒，但不创建View、不执行gather。所有实际gather先由独立oracle断言域合法，20 View表均在预算内。按三个prepare入口计入fallback嵌套推导为3620，1540则是显式harness口径；3620不是插桩事件测量。

唯一有限执行计划SHA `50628d4a1dc17e8855bb7b2131255dd096d01fd9fedb5a58041473a7a668526d`；结果SHA `c556195cf63409db32d094c3f1ce55c1437ca8644c33328f7ee21f5919409bad`，exit0。原件计数与上述全部相符，没有改源重跑。

## RSS缺口与结论边界

外部observer只启动冻结runner一次，预先声明未采到时保留缺口、不重跑。结果`sample_count=0`、原生PID未捕获，RSS与peak_wset均null；有限合同成功不等于内存测量成功。观察回执SHA `a847eadbdddcee174685a255acba8fd88cdcd88826205ca05bdc6deefede18ed`，observer源和runner stdout/stderr原样保存。

纯结构预算“新增峰值<16MiB”不是实测RSS，不用它填补null。未保留可确诊父子进程链，不能断言缺采样的具体原因。不得为改善采样再执行原合同。

本阶段有限整数与地址合同通过；新的完整链/全色域、真实照片、正式速度、OOM/noAVX2硬件、其他CPU/编译器均未执行。没有给101授予任何性能档位，也未替代100的窄N100受控结论。完整新链是否值得推进由root根据当前边界另定。

## 交付

主要源为`experiments/p16-early-index-runtime/compile_index_avx2.cpp`、独立包装器及`finite_contract.cpp`；生成/构建/冻结/机器码/执行/观察脚本为`scripts/*p16_early_index*.py`。原执行/观察/build/objdump、实际产品和源闭包在[有限阶段证据](../../report/data/p16-early-index-finite-v1/identity.json)。增量index/HEAD按原执行字节核对，仅`.gitattributes`与本文按text归一LF。阶段由独立speed分支提交，由root统一更新Draft PR89；不自行推送或合并。
