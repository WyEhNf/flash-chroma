# 分输出坐标的独立原生研究库

这是一条可执行的实验路径，不改变现有SLUT v1、公共运行时或默认算法。一个m³ RGB8节点张量与一个shared idx继续决定同一个输入立方体，三个输出通道分别使用自己的Q16权重。每级三个输出同时完成half-up到RGB8，再作为下一独立阶段输入。库接受1..4级，尺寸可以混合，但本地比赛研究要求每级17..33。

模型以`channel_coordinates_v1_experimental` NPZ保存。C ABI适配时加载一个普通SLUT提供grid/idx/nodes，再附恰好9216字节的little-endian `uint32[3 output][3 axis][256 code]`。两文件一起才表达新模型；不得把base单独分发为等价SLUT。若将原frac替换为三份，逻辑净增6144字节；当前适配器保留base原frac，实际多整个9216字节。NPZ压缩文件大小不能与未压缩SLUT直接比较。

可选构建开关`JSHC_ENABLE_CHANNEL_RESEARCH=ON`生成`jshc_channel_research`共享库，默认OFF。示例沿本机已确认GCC15.2工具链：

```powershell
cmake -S . -B build-channel-research -G 'MinGW Makefiles' -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe -DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe -DCMAKE_MAKE_PROGRAM=E:/mingw64/bin/mingw32-make.exe -DCMAKE_BUILD_TYPE=Release -DJSHC_ENABLE_CHANNEL_RESEARCH=ON -DJSHC_ENABLE_CPP_SIMD=OFF -DJSHC_ENABLE_EMBEDDED=OFF -DBUILD_TESTING=OFF
cmake --build build-channel-research --target jshc_channel_research -j 4
```

只有`channel_avx2.cpp`编译为AVX2，分派器和标量保留baseline ISA。能力位同时依赖编入和原有CPUID/OSXSAVE/XGETBV；明确请求不支持的后端会失败。ABI版本1，当前算法revision2。准备模型时把idx与17位frac合并，不丢65536端点；AVX2在三个通道间复用立方体两端点，shared阶段经完整侧表相等证明后只算一套几何。没有每像素分配、CPUID或全量256³回查表。

`channel_native.py`显式核库SHA，使用`with library.chain(...)`管理句柄；创建后读取来源hash失败也会清理句柄。调用者不能在apply同时destroy同一句柄，输入必须连续、可写RGB8。`jshc_cc_model_bytes`是对象和已准备模型容量核算，不是进程峰值RSS。基准另预加载235929600字节的100图源和同大小工作区，复制与apply分别记录。

直接应用现有冻结候选：

```powershell
artifacts/error-study-py312/Scripts/python.exe scripts/apply_channel_model.py artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz --image assets/photos/kodak/rgb8-1024x768/kodim03.png --library artifacts/channel-native-runtime-v3/jshc_channel_packed.dll --library-sha256 7ceb30d7913a8cf032e1828c25c3fe062082be8e9d531d105282ba8d1794b072 --output artifacts/channel-application-example --kernel avx2 --threads 4
```

图片参数应使用本地清单中的实际路径；输出目录必须不存在。该研究入口支持任意有效RGB8尺寸，比赛契约仍为1024×768。结果目录提供PNG、输入/模型/库hash及私有适配缓存，没有原表时不猜精度。完整验收与性能入口分别为`scripts/accept_channel_native.py`、`scripts/bench_channel_native.py`，各自使用已冻结计划；旧实验必须用对应ZIP源码复现。

目前只验证本机Windows11 x64/Ryzen9 8945HX，标量及AVX2/OpenMP。尚未接入现有C99、GUI、统一公共CLI或移动端，不声称官方认可此格式，也不将四级等距控制链的结果推广到自然ISP链。
