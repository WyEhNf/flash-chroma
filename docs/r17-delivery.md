# R17 交付与复现入口

本轮交付采用可独立构建的 C++17 主线，Python 负责稀疏化、输入校验与候选报告。题面要求 `17 <= m <= 33`、四级整数颜色映射；当前文件适配器使用 RGB uint8、`[r,g,b,channel]` 顺序的完整 LUT 和 SLUT v1 稀疏文件。官方输入格式、阈值及判定粒度仍需等待正式说明。本文不提供官方通过或评分保证。

## 构建与阶段验收

需先准备 C++17 编译器、CMake 和 Python；Python 依赖为 NumPy、SciPy、Pillow、pytest。Zig、Rust、C++ SIMD 扩展均为可选后端。默认 CMake 构建可以包含独立编译的 AVX2 实现，运行时检测硬件及操作系统是否支持；`auto` 使用当前可执行的默认内核。查看当前构建事实：

```powershell
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --parallel
& .\build\jshc.exe info
```

Windows 多配置生成器通常将可执行文件放在 `build/Release/jshc.exe`。若使用已加入 PATH 的 MinGW 编译器，可在首次配置时显式添加 `-G "MinGW Makefiles"`；不同生成器使用不同构建目录。Linux/macOS 对应可执行文件名为 `jshc`。

纯标量回退可以单独配置，以验证不依赖 SIMD 或 OpenMP 的交付路径：

```powershell
cmake -S . -B build-scalar -DCMAKE_BUILD_TYPE=Release -DJSHC_ENABLE_AVX2=OFF -DJSHC_ENABLE_OPENMP=OFF
cmake --build build-scalar --config Release --parallel
```

统一阶段验收时明确指定要测的产物。以下 PowerShell 设置仅影响当前终端：

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "python")
$env:JSHC_BIN = (Resolve-Path .\build\jshc.exe).Path
ctest --test-dir build -C Release --output-on-failure
python -m pytest -q tests
```

应在完成一组有意义的改动后执行阶段验收。内核正确性证据与性能数据必须来自同一明确记录的二进制；源码修改后不能继续沿用旧二进制的验证结论。

## 模型与缓存

保守默认是四张完整 LUT 各自独立拟合、每一级量化为 uint8。示例：

```powershell
python -m lutlab.cli fit --scenario isp-0 --m 18 --method ls_tetra_int
python -m lutlab.cli fit --scenario isp-0 --m 18 --method ls_tetra_q16
```

`ls_tetra_q16` 是新增候选，不能仅凭名称假设其优于基线。它的真实整数接受诊断与求解器诊断保存在拟合信息中。不同网格大小、网格模式和拟合方法要经过相同门禁比较。

缓存目录结构为：

```text
data/models/<scenario>/<variant>/<identity_sha256>/batch-<id>/
  manifest.json
  stage1.slut ... stage4.slut
```

身份绑定四个完整 LUT 的全部字节 SHA-256、有效参数、拟合函数默认值、相关源码和依赖版本，以及整数格式和阶段语义。命中时还验证阶段数、完整文件格式与每个模型 SHA-256。旧目录中仅存在四个文件不构成有效命中，旧无 manifest 模型不会被自动认领为新缓存。

新批次在同一文件系统的临时目录内写完、落盘、复读后原子发布。并发拟合只能复用一整批通过校验的模型，不拼接阶段文件；损坏批次和旧版本保留，后续创建新批次。拟合异常或输入/代码中途改变时不发布新批次。缓存完整性证明来源与文件一致，不代表误差已经达标。

## 门禁、候选与性能口径

先准备并核验场景与图像数据，再选择少量候选。下面的 `2.0` 仅为本地示例阈值：

```powershell
python -m lutlab.selection --scenario isp-0 --m 17 18 --profiles tetra q16 --threshold 2.0 --metric mean --constraint-scope images --threads 4 --reps 5 --executable $env:JSHC_BIN
```

每张图按未四舍五入的统计量做严格 `< threshold` 比较。`--constraint-scope images`、`cube`、`both` 明确区分图像集约束与全色域约束；全色统计存在不等于通过全色阈值。只有全色域 `max` 小于阈值，才能对固定 LUT 链的任意输入像素给出相同误差上界。`--skip-cube` 仅允许与图像约束组合。

选择结果分别提供：

- 保守独立四级候选的精度、速度、模型内存 Pareto 集，以及速度、均值精度、尾部、内存和基线推荐。
- 研究候选自己的 Pareto 集与推荐，不能替代保守提交主线。
- 完整模型路径与 manifest、逐图及全色误差、拟合耗时、二进制与输入依据、原始整组计时。

兼容字段 `winner` 表示保守独立候选中的速度推荐，不是推断出的总分冠军。基线按实际测得的尾部和均值选择，不以较大的 m 代替精度证据。没有官方完整评分公式时不合成总分。

`residual` 需要显式 `--allow-residual`，`composite` 需要显式 `--allow-composite`。许可表示启用研究路线，不代表官方已经接受跨级残差语义或单级复合。

模型内存报告区分节点载荷、序列化文件、运行时对象和 vector 容量，并单列线程工作区和预加载图像。运行时模型数组字节不是进程峰值 RSS。拟合时间不包含在已加载模型的映射耗时中；整组时间包含图像复制和映射，具体范围以基准 JSON 的 `timing_scope` 为准。数值接近的候选应保留，单次顺序扫描不证明差异显著。

`python -m lutlab.workflow` 可以配置 CMake、执行一次阶段测试、核验输入并输出上述报告。`--executable` 或 `JSHC_BIN` 使用已有产物；`--skip-tests` 供已经单独验收同一产物后复用。缺少标准图像数据时该入口会按现有数据流程生成/下载，离线交付应事先准备好数据。运行日志保存在 `logs/`，本轮这些入口不会自动提交日志仓库。

固定模型的最终实测入口为 `scripts/phase_acceptance.py`。它使用明确标记的合成图像与 AB/BA 交替整组计时，输出只描述所测机器、输入和产物，不推算官方服务器成绩。最终数字与证据以阶段验收报告为准。
