# 固定κ3两cell的187原生正确性与容量边界

代理 `/root/tail` 按当前会话用户授权，将已完整质量验收的Velvia原3e5f两cell/κ3表示落实为独立原生研究库。此阶段完成构建、完整色域和照片的运行时正确性、小合同及逻辑容量统计；未做正式性能、RSS或构造峰值测试。新表示非stock SLUT，题面许可未知，不切默认；前一阶段真实RGB8邻接跳变增大的代价继续有效。

revision187从speed分支87源码派生，采用相同基核与构建flags，冻结87 DLL不变。三控制为冻结87原3e5、187关闭bubble的原3e5、同一187开启bubble的固定候选。派生DLL的SHA为`65e929e44e4abf5cd3a848fa2bd2b08edc41cc27dd750e5a4d5da3553e98b211`，不能冒充原87 SHA。

实现保留87的65536像素外层OpenMP调度。开启功能时在块内按4096子块捕获命中位置与计算好的Q32结果，调用原底层标量或AVX2基核后覆盖；不逐块调用exported apply创建额外OMP区，不复制完整输入，不读gold或历史输出准备修正表。关闭功能保持旧基核块调用。开启功能的分类、额外子块调用、Q32计算与覆盖都是候选成本，未来配对计时必须包含。

typed配置严格要求version1、κ3、两固定cell31725/31726及mask1/1。只接受单级33³且完整分输出侧表，版本/值/空指针/缺侧表/多级/m17均拒绝，失败不能偷偷沿用旧输出。配置须在无并发apply时设置，调用者负责外部同步；本轮使用两个独立187句柄，运行中不改配置。原地和分离输入输出均支持，部分重叠拒绝。

| 已执行运行时正确性覆盖 | 结果 |
| --- | --- |
| 三控制×scalar1/AVX2的1和4线程×原地/真分离 | 18配置完整16,777,216色，零字节差 |
| 三控制×原地/真分离×100图，AVX2/4 | 600新鲜输出SHA，逐字节符合完整流 |
| 空、1..17、31/32/33、4095/4096/4097、65535/65536/65537长度；密集/无命中/混合输入 | 243配置，原地及偏移分离/同址输出均零差，前后哨兵保持 |
| 无效typed/模型形状拒绝 | 11项通过，失败后已启用状态保持 |
| 无效分离输入输出范围/部分重叠拒绝 | 11项通过 |

密集模式的每个像素均命中，包括4096条记录全部填满，不能根据照片中612色罕见就省略数组上界。87和187关闭的全域SHA均为945d4b90…，187开启为f38217d6…，完整SHA与各配置逐项记录在证据中。目标数学输出保持前阶段全域mean0.886487398719、p99√40、max√1604；该阶段未再选cell、斜率、节点或轴。

| 容量观察 | 实测/静态结果及含义 |
| --- | --- |
| 三个句柄accounting | 均272,859B，suffix cache均disabled；不代表进程RAM相同 |
| 一条命中记录sizeof | 6B，4096条数组每线程24,576B |
| GCC `-fstack-usage` 的block自身栈帧 | 24,864B，另原地OMP worker自身144B、分离外层worker自身256B |
| 实际调用链栈/RSS/构造峰值 | 尚未测；被调基核、ABI调用和OpenMP运行时栈不能被上述单帧数字替代 |

四线程命中数组合计98,304B；这项新增暂态必须列入后续内存观察，不能只说句柄不增。记录数组上界与编译静态帧均不是RSS差值。

首轮构建失败：基础子目录的CMake SOURCE flags没有传播到新target，部分AVX2 TU缺少对应许可，报`target specific option mismatch`。保留v1冻结和原失败CMake；只补父目录中与87一致的AVX2/BMI1 flags，v2重新冻结后GCC15.2.0 Release构建成功，数值模型与κ不变。已有复制源码中的缩进告警保留，没有把失败或告警删除后声称一次通过。

环境Windows11 26200/AMD64、Ryzen9 8945HX，MinGW-w64 GCC/G++15.2.0、C++17、OpenMP4.5，AVX2与BMI1 TU明确许可，无AVX512；Python3.12.14/NumPy1.26.4，BLAS1、OMP4。构建2线程；正确性测试实际scalar1、AVX2的1/4，不推断其他硬件或标量平台性能。完整compile commands、构建日志、实际DLL、所有GCC栈文件、模型序列化字节、构建前冻结身份及源码ZIP见[精简证据](../../report/data/velvia-bubble-native-20261024/README.md)。

```powershell
& $py scripts/prepare_velvia_bubble_native.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/velvia-bubble-native-v2
cmake -S experiments/velvia-bubble-runtime -B artifacts/velvia-bubble-native-build-v1 -G 'MinGW Makefiles' -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe -DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe -DCMAKE_MAKE_PROGRAM=E:/mingw64/bin/mingw32-make.exe -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build artifacts/velvia-bubble-native-build-v1 --target jshc_velvia_bubble -j 2
& $py scripts/check_velvia_bubble_native.py --cache-root F:/Hackathon/projects/16-lut-color --frozen artifacts/velvia-bubble-native-v2 --library artifacts/velvia-bubble-native-build-v1/libjshc_velvia_bubble.dll --output artifacts/velvia-bubble-native-check-v1
& $py scripts/archive_velvia_bubble_native.py --output artifacts/velvia-bubble-native-archive-v1
```

`$py`为原冻结Python环境；输出目录须不存在。尚待同一187关闭/开启的正式配对性能，以及关闭功能相对冻结87的控制，防止共同固定成本掩盖退化。密集命中正确不能替代密集命中速度；后续需将该压力项单列，再判100..50%保留档。
