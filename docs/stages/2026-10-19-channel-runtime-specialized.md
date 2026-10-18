# 固定四级分通道首级的AVX2专门化候选

Agent：Codex；Operator：WyEhNf；状态：唯一候选构建、有限正确性合同、完整native等价和冻结受控性能门禁全部通过。仅本地归档，未PR或推送，未替换默认。

本阶段处理已验Cinema新首级a399模型的运行成本。此前同机实际四级测量显示，新表示相对普通af974首级约慢46%；这是不同精度模型的成本背景，不能拿此前绝对耗时计算本轮后端加速。本轮只比较同一a399首级及同一933a/95cb/932f后三模型上的两份运行库。没有新拟合、模型或数据调整。

唯一候选从已验packed v3原始源码复制到`experiments/channel-runtime-specialized/channel_avx2.cpp`，没有使用已失败的同包方向地址复用代码。将原`transform`的共享性改为编译期模板参数，在每个批入口只判断一次“四级、首级分通道、后三共享”，在八像素循环内展开`false/true/true/true`四次转换。其它级数或共享布局保留逐级动态分派。Q16公式、gather、两端点、高低轴/中值、RGB8舍入、24字节读写、标量尾部、内存布局、CPUID/OS派发均沿用原实现；`Rgb`继续经引用，不引入Win64过对齐结构按值传递。没有强制inline、额外候选或参数扫描。

新建独立构建脚本`scripts/build_channel_specialized.py`，原CMake、标量壳、静态核心、原v3源码与DLL均不修改。仅新AVX2翻译单元带`-mavx2`；标量dispatcher和链接命令没有该标志。复用的静态核心SHA为`64abb6eb38d929dc81c07b5a34be1408bbadecfee76fd31801cdfe94a0916ef6`。构建产物使用独立basename `jshc_channel_specialized.dll`，ABI1/revision2；身份由文件名、源码与DLL SHA区分，不把revision未变解释为原二进制未变。

执行前冻结计划`experiments/channel-runtime-specialized-v1.json`，SHA `20480d26995b21897d7b6eee778d77b68ddc1d4b87e2765980547bf84c10c839`。测试环境为Windows11 26200 x64、Ryzen9 8945HX 16核32线程/32GB、MinGW GCC15.2.0、Release `-O3 -DNDEBUG -std=c++17 -fopenmp`、Python3.12.14/NumPy1.26.4；OMP动态线程关闭，BLAS/MKL/OMP环境线程1，合同显式请求标量1及AVX2 1/4线程。本阶段目的仅为新热路径和fallback的整数正确性与边界验证，不测精度收益或性能。

一次构建成功：`artifacts/channel-native-specialized-v1/jshc_channel_specialized.dll` SHA `507b51a31421e3b2ed8b71d9140d79aac2e6cd7435be888754b8acf4bc497372`；`build.json` SHA `66b05e3986e3988813a03ab5f534469ea3715ee200cb3f4efa5a8852fe512ded`，保存实际命令、编译器字节、静态核心、源码和主库及四份GCC依赖SHA。

唯一集中合同`scripts/verify_channel_specialized.py`成功：44组＝4布局×11长度，每组覆盖3种后端线程与0/1/2/3字节偏移。混合尺寸17/18/25/33，首级真实不同的三路坐标、后三普通表触发新热路径；另核四级混合共享、四级相等侧表全共享、三级分通道fallback。长度0/1/7/8/9/15/16/17/4095/4096/4097覆盖向量和4096批边界，输入含0/255端点及邻近码。各级以独立uint64 oracle同步RGB8输出作真值，所有输出与首尾哨兵零差；实际已载主库与四个GCC依赖路径/SHA一致。ABI异常合同继承原封标量壳的已验记录，不声称本次重新测试异常或计时接口。证据在`artifacts/channel-native-specialized-contract-v1/results.json`及其源码ZIP。

复现命令：

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'; $env:PYTHONDONTWRITEBYTECODE='1'
$env:OMP_NUM_THREADS='1'; $env:OMP_DYNAMIC='FALSE'; $env:OPENBLAS_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:NUMBA_NUM_THREADS='4'
artifacts/error-study-py312/Scripts/python.exe scripts/build_channel_specialized.py --plan experiments/channel-runtime-specialized-v1.json --output artifacts/channel-native-specialized-v1
artifacts/error-study-py312/Scripts/python.exe scripts/verify_channel_specialized.py --plan experiments/channel-runtime-specialized-v1.json --library artifacts/channel-native-specialized-v1/jshc_channel_specialized.dll --output artifacts/channel-native-specialized-contract-v1
```

上述输出目录不允许覆盖。原计划之后，根代理唯一完成实际a399模型的完整native等价：256³首级及实际四级的标量1/AVX2请求4逐字节零差，100图逐图及聚合SHA完全重现已验独立oracle流；没有新拟合或精度选型。四级输出SHA为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，百图输出SHA为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。完整等价在`artifacts/cinema-specialized-native-v1`，原精度口径和模型仍引用此前当前锚点完整验收。

随后唯一性能比较使用同a399首级及同933a/95cb/932f后三模型，两种后端均加载相同base、9216字节侧表和100图，不使用af974作本轮性能分母。四串行新进程AB/BA/BA/AB，线程顺序[1,4]/[4,1]/[1,4]/[4,1]，每组5次完整100图；预加载235929600字节，各配置预热核SHA。apply与copy+apply分列，排除文件IO、解码/编码、模型加载和hash。

| 请求线程 | apply时间下降 | apply配对比 | copy+apply时间下降 | copy+apply配对比 | 最差进程apply比 |
|---|---:|---:|---:|---:|---:|
| 1 | 10.704820% | 0.892951798503 | 10.541961% | 0.894580387217 | 0.900179106380 |
| 4 | 7.764286% | 0.922357137578 | 6.974270% | 0.930257303044 | 0.931044210949 |

两种比值均先计算每进程5轮中位数之比，再取四进程比值中位数，尤其copy+apply不是两端汇总中位数相除。预冻结门槛为1和4线程apply比均≤0.97、任何进程≤1.02、copy+apply比均≤1，全部通过。绝对apply摊销为1线程13.443810→11.955870 ms/图、4线程4.901260→4.483010 ms/图；它们只是四进程中位数的描述，不用这两个数相除代替配对统计。所有进程均更快，模型内存1058292字节/序列化输入457468字节不变。这里下降百分比指时间，不等同吞吐提升百分比。

本次只读归档逐份核构建/源码ZIP、完整native身份、同模型/后三阶段、4份worker原始SHA、各80轮次、实际已载新主DLL及共用GCC依赖SHA，并重算apply和copy+apply的原统计及全部门槛。没有新的native、像素映射、性能或拟合调用。`report/data/channel-runtime-specialized-v1`保存原run/results/worker日志、CSV、门禁复算、源码、两主DLL/4依赖与实际静态核心ZIP和SHA清单；只引用`report/data/cinema-current-anchor-accept-v1/models.zip`，不重复模型。详见[本阶段归档](../../report/data/channel-runtime-specialized-v1/README.md)。

原v3源码/CMake/默认均未修改，独立builder可复现研究库；没有后续硬件变体、强制inline或参数扫描。未锁频、控温或绑核，四进程范围不是置信区间，不宣称统计显著或跨机器收益；100图摊销ms/图不是单图或尾延迟。上一阶段v3新表示相对af974约慢46%的成本结论仍只适用于那组测量，不能跨阶段用绝对耗时或乘比值推算相对af974的最终配对速度。

四张真实创意LUT仅数值串联，没有色彩域匹配证据，不称真实ISP。独立输出Q16侧表仍为实验表示，未获官方格式许可，未接公共CLI/GUI/C99；无官方测试集和Threshold，不给官方分数。
