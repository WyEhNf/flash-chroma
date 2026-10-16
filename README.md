# flash-chroma · 极速焕彩

将四张 `256³` RGB8 LUT 拟合为四张边长 `17–33` 的稀疏 LUT，并在图像上执行逐级整数色彩映射。Python 负责离线拟合和验收，C++17 负责运行时；默认构建提供标量回退、运行时检测的 AVX2 后端、OpenMP 和独立的完整色域拟合库。

本项目源于 2026 Hackathon 第 16 题。仓库中的数据与报告包含模拟场景和历史实验，不能据此推断官方验收结果或比赛分数。题目与待确认规则见 [PROBLEM.md](PROBLEM.md)、[DECISION.md](DECISION.md)。

## 获取与验证

主开发环境为 **Linux x86_64**；Windows 使用 WSL2。安装 [Pixi](https://pixi.prefix.dev/latest/installation/)，在仓库根目录运行：

```bash
git clone https://github.com/WyEhNf/flash-chroma.git
cd flash-chroma
pixi install --locked
pixi run --locked test
pixi run --locked lutlab info
```

`test` 构建到 `build/`，执行 C++ 全 `2²⁴` RGB 色域对照和全部 Python 契约测试，包括完整色域拟合库的独立验证。**不需要下载图像、生成实验数据或运行 benchmark。** `correctness` 是 `test` 的兼容别名，CI 与本机使用同一个入口。

默认环境只安装 CPU 构建和测试依赖。可选功能按需使用：

| 用途 | 命令 | 构建或依赖范围 |
| --- | --- | --- |
| 默认完整正确性门禁 | `pixi run --locked test` | `build/`；C++17、AVX2、OpenMP、完整色域拟合库 |
| 验证纯标量回退 | `pixi run --locked test-scalar` | `build-scalar/`；禁用 AVX2 与 OpenMP |
| 验证可选 SIMD 后端 | `pixi run --locked -e simd test-simd` | `build-simd/`；额外安装 Zig、Rust、C++ SIMD 工具链 |
| 绘图、历史报告数据生成 | `pixi run --locked -e plots python scripts/build_typst_data.py` | 额外安装无 GUI 的 Matplotlib；需要对应历史日志 |
| 机器学习路线探索 | `pixi run --locked -e ml routes` | 额外安装 PyTorch CPU；需要实验数据 |

GitHub Actions 对 PR（含 Draft）、`main` push 和手动触发运行默认、标量回退及 Docker 正确性检查。CUDA 与可选 SIMD 不属于当前 CI 门禁；配置、覆盖和原生 CMake 用法见 [TOOLCHAIN.md](TOOLCHAIN.md)。

## 使用四张实际 LUT

统一接口为 `python -m lutlab`，Pixi 提供自动构建的 `lutlab` 任务。以下四个输入文件由调用者提供，必须符合仓库的原始 RGB8 LUT 格式：

```bash
pixi run --locked lutlab fit \
  --inputs stage1.lut256 stage2.lut256 stage3.lut256 stage4.lut256 \
  --grid dp --method ls_tetra_jitter --mode seq
```

命令输出模型批次目录和四张 `.slut` 路径；随后把这些路径按阶段顺序传给 `apply`、`cube`、`verify`、`validate` 或 `accept`。例如查看图片映射参数：

```bash
pixi run --locked lutlab apply --help
pixi run --locked lutlab validate --help
pixi run --locked lutlab accept --help
```

模型批次以输入内容、算法参数、源码及环境指纹标识，不应手工覆盖已发布批次。四级独立模型是默认语义；残差或单级复合研究需要显式授权开关。当前采用欧氏 RGB 距离，阈值、统计口径和计时边界须按实际任务确认。

已有带来源和哈希记录的 [100 张日常照片](assets/photos/README.md)，包含 Kodak、DPED 和 DIV2K 子集，可显式传入 `assets/photos/eval.txt`。它们不自动替换模拟数据清单，也不替代全色域验收；各来源的使用范围见样本说明。

## 模拟数据与实验

模拟场景只用于本地研究。以下命令会下载 Kodak 图片并生成图像、四级 LUT 与清单，占用较多时间和磁盘空间；它们不属于首次构建或 CI：

```bash
pixi run --locked gen-data --scenarios isp-0
pixi run --locked verify-data --scenario isp-0
pixi run --locked fit --scenario isp-0 --m 18 --method ls_tetra_int --mode seq
pixi run --locked select --scenario isp-0 --m 18 --profiles tetra \
  --threshold 2.0 --metric mean --constraint-scope both --threads 4 --reps 3
```

这里的 `2.0` 仅为本地示例，比较使用未舍入统计量和严格 `<`。数据来源与重建说明见 [DATA.md](DATA.md)。性能比较应固定模型、输入、机器、构建参数、线程数和计时边界；CI 通过只证明所覆盖的正确性条件。

## Docker

```bash
docker build -t flash-chroma .
docker run --rm flash-chroma
```

镜像固定 Pixi 版本，仅按锁文件安装默认环境，并运行同一 `test` 门禁。本机构建目录、Pixi 环境、实验数据与日志不进入构建上下文。直接运行镜像即可验证，不必挂载整个仓库覆盖容器中的依赖和构建产物。

## 项目导航

| 路径 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Agent 交流、授权、语言与证据规范 |
| [TOOLCHAIN.md](TOOLCHAIN.md) | 当前构建配置、测试入口、依赖环境与 CI |
| [python/lutlab](python/lutlab) | 拟合、模型格式、验收与统一 CLI |
| [cpp](cpp)、[gpu](gpu)、[zig](zig)、[rust](rust) | CPU、可选 CUDA 和可选 SIMD 实现 |
| [tests](tests)、[cpp/tests](cpp/tests) | Python 契约与 C++ 内核正确性测试 |
| [docs/README.md](docs/README.md) | 技术文档、R17–R27 历史实验与报告索引 |
| [docs/LOGGING.md](docs/LOGGING.md) | 独立实验日志与团队交接 |
| [report/README.md](report/README.md) | 冻结报告、数据证据与重建边界 |

`data/`、`build/`、`build-*/`、`.pixi/`、`logs/` 与 `artifacts/` 是本机产物。历史报告中的分支名、硬件和性能数字描述对应实验阶段；当前开发流程以本 README、工具链说明与仓库配置为准。
