# 构建、依赖与正确性测试

当前支持的 Pixi 平台为 Linux x86_64，Windows 队员使用 WSL2。主环境不再提供 macOS 依赖。原生 Windows 和 CUDA 的历史构建记录保留在技术文档中，不属于 Linux CI 的验证承诺。

## 单一默认入口

```bash
pixi install --locked
pixi run --locked build
pixi run --locked test
```

`build` 使用 `CMakePresets.json` 的 `default` 配置，在 `build/` 中构建。`test` 依赖 `build`，先运行 CTest，再运行 Python 测试；任一步失败都会返回非零。`correctness` 只是 `test` 的别名。`test-cpp` 与 `test-py` 可分别执行两部分，二者都使用同一次默认构建。

默认门禁包括：

- C++ 全 `2²⁴` RGB 色域与独立整数 oracle 对照、非均匀网格、边界、向量尾部、四级串联和线程一致性。
- Python/C++ 位精确一致性、模型格式和缓存、拟合约束、实际图片路径、输入位深及全色域验证契约。
- 完整色域离线拟合库与独立 Python 正规方程组装的对照。
- 嵌入式 C99 契约，以及桌面序列化模型的四级全 RGB 色域逐字节互操作对照。

CMake 生成 `build/test-artifacts-Release.json`，记录运行时和拟合库的实际目标路径。测试运行器通过 `JSHC_BIN`、`JSHC_FULL_FIT_LIB` 显式绑定这些产物；拟合库缺失或加载失败不能变成测试跳过。默认门禁不读取下载数据，不执行性能扫描。

## 依赖分层

| Pixi 环境 | 内容 | 典型命令 |
| --- | --- | --- |
| `default` | Python 3.12、NumPy、SciPy、Pillow、pytest、CMake、Ninja、G++/Binutils、日志所需的 Git | `pixi run --locked test` |
| `simd` | 默认依赖，加 GCC/G++ 16、Zig、Rust | `pixi run --locked -e simd test-simd` |
| `plots` | 默认依赖，加 `matplotlib-base`，不额外安装 Qt GUI 前端 | `pixi run --locked -e plots python scripts/generate_plots.py` |
| `ml` | 默认依赖，加 PyTorch CPU | `pixi run --locked -e ml routes` |

日常开发和 CI 不使用 `pixi install -a`。运行选定环境的任务即可按需安装，所有精确包版本与构建均记录在 `pixi.lock`。只有有意修改依赖时才运行 `pixi lock`；提交清单和锁文件后，用 `pixi lock --check` 检查一致性。

`report/pixi.toml` 是独立的 Typst/字体环境，保留 Linux 与 Windows，用自己的锁文件管理；不进入默认数值环境。报告重建依赖见 [report/README.md](report/README.md)。

## CMake 配置

| Preset | 目录 | 配置 |
| --- | --- | --- |
| `default` | `build/` | Release、测试、完整色域拟合库；启用 AVX2 编译与 OpenMP 查找；关闭可选 SIMD |
| `scalar` | `build-scalar/` | 继承默认配置，禁用 AVX2 和 OpenMP |
| `simd` | `build-simd/` | 继承默认配置，启用 C++ SIMD、Zig 与 Rust |

任务显式设置各后端开关，避免本机残留 CMake cache 改变默认门禁。构建默认并行度为 2，可直接向 CMake 覆盖：

```bash
pixi run --locked cmake --preset default
pixi run --locked cmake --build --preset default --parallel 4
pixi run --locked python scripts/check_correctness.py
pixi run --locked test-scalar
pixi run --locked -e simd test-simd
```

AVX2 只在独立翻译单元中启用；运行时根据 CPU 和操作系统能力选择内核，能力不足时回退。OpenMP 在默认配置中为可选依赖，查找结果显示在 CMake 输出中。`scalar` 验证完全不依赖这两项的路径。

C++ SIMD 需要支持 `<simd>` 或 `<experimental/simd>` 的编译器/标准库。Rust `portable_simd` 后端仍使用构建命令局部的 `RUSTC_BOOTSTRAP=1`；它是显式可选研究后端。不要把可选环境的产物写入 `build/`。

无 Pixi 时，可在自行准备的 CMake ≥3.24、Ninja、C++17 编译器及 Python 数值依赖环境中使用同一 preset。多配置生成器可按以下方式构建：

```bash
cmake -S . -B build-custom -G "Ninja Multi-Config" \
  -DBUILD_TESTING=ON -DJSHC_ENABLE_FULL_FIT=ON
cmake --build build-custom --config Release --parallel 2
PYTHONPATH=python python scripts/check_correctness.py --build-dir build-custom --config Release
```

只需要 C++ 运行时可关闭测试和离线拟合库：

```bash
cmake -S . -B build-runtime -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF -DJSHC_ENABLE_FULL_FIT=OFF
cmake --build build-runtime --parallel 2
```

不允许在源码根目录直接配置构建。开发者的局部 preset 放入被忽略的 `CMakeUserPresets.json`。

## 产物选择

默认 CLI 查找 `build/jshc`，完整色域拟合方法查找 `build/` 中的共享库；旧 `build-fit/` 仅作为兼容回退。使用自定义构建时显式设置 `JSHC_BIN` 和 `JSHC_FULL_FIT_LIB`，或向支持的命令传入 `--executable`。更换模型或构建后重新验收，不能沿用另一产物的测试结果。

锁文件与相关源码参与模型缓存身份计算。依赖清理后旧批次仍保留，但可能不再命中新身份；应按新环境重新拟合与验收，不要手工改写旧 manifest。

`pixi run --locked lutlab ...` 是统一 CLI 的自动构建包装。`competition-check` 还会核验或生成数据、执行候选选择与性能测量，属于实验工作流，不能替代无数据依赖的 `test`。

## GitHub Actions 与 Docker

[正确性工作流](.github/workflows/correctness.yml) 在 PR（含 Draft）、`main` push 和手动触发时运行：

1. Linux 默认门禁 `pixi run --locked test`。
2. Linux 无 AVX2/OpenMP 门禁 `pixi run --locked test-scalar`。
3. Docker 镜像构建及容器中的默认门禁。

独立的 [嵌入式工作流](.github/workflows/embedded.yml) 使用 ARM 裸机 GCC 和 `qemu-system-arm`，构建 Cortex-M3 / FreeRTOS 静态任务测试固件并运行 QEMU 门禁。运行时独立构建只要求 C99，不使用桌面 Pixi 环境；工具链、模型存储预算与当前覆盖范围见 [embedded/README.md](embedded/README.md)。

CI 固定 Pixi 版本，按锁文件只安装默认环境，不运行 benchmark，不下载实验数据。CUDA 与可选 SIMD 需在具备相应环境的机器上单独验证。

项目镜像统一命名为 `flash-chroma`，并设置同名 OCI title。Dockerfile 固定 Pixi 0.81.0 的基础镜像版本与 digest，只安装默认锁定环境，不再重复安装宿主发行版的编译器、Python 和 CMake。Binutils 由锁定环境提供，归档和链接不借用宿主工具。构建上下文排除所有层级的 `.pixi/`、`build/`、`build-*/`、测试缓存和本机实验目录。

```bash
docker build -t flash-chroma .
docker run --rm flash-chroma
```

报告和历史性能数字的复现要求见 [文档索引](docs/README.md)，统一报告目录为 `report/`。
