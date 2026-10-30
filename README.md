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

嵌入式目标另提供 [C99 / FreeRTOS / Linux 方案（WIP）](embedded/README.md)：不依赖堆分配、文件系统或 C++ 运行时，直接读取 `.slut` 模型。默认门禁含桌面全 RGB 色域互操作验证；独立嵌入式工作流交叉构建并在 QEMU 中验证 Cortex-M3/FreeRTOS、RV32/FreeRTOS 和 Cortex-A53/Linux。实板尚未验证。

## 使用四张实际 LUT

也可启动[本地色彩工作台 GUI](docs/stages/2026-10-18-local-gui.md)：`pixi run --locked gui`（已有 Python 环境可用 `PYTHONPATH=python python -m lutlab gui`）。界面支持图片选择/上传、四级 `.lut256`/`.slut` 配置、稀疏拟合、分割对比、误差热图和模型/图片导出；内置数值示例。默认仅监听本机，不需要前端构建。误差只统计当前图片，且必须具备全部完整 LUT 参考。

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

[hack image/LUT 压力子集](datasets/problem16-hack-v1/README.md)提供独立的边界配方、同像素多重集图片及小型整数回放，通过 `python -m lutlab hackset` 构造和核对；拟合矩阵与全色域压力评价仍需显式执行。

当前统一入口是[合并数据集 v1](datasets/problem16-unified-v1/README.md)：原语料、历史控制、两批压力子集和自然照片合计登记 274 个 LUT case、455 份不同图片内容。`python -m lutlab dataset` 提供命名空间查询、分队列核对和原合成图恢复；保留旧划分和 7,917 项计划，不自动转移历史验收资格。

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

## 真实 RAW 工作台（实验）

本地GUI可浏览三家摄影机的真实结果，拖动比较参考/原生画面，查看逐帧SDR/HDR预览、误差和任务日志，并创建独立处理/导出任务。Windows在仓库根目录执行 `.\start-gui.ps1`。依赖、运行范围和当前WSL限制见 [GUI说明](gui/README.md)及[阶段验证](docs/stages/2026-10-23-camera-workflow-gui.md)。这不改变现有RGB8精度合同或代表高精度HDR/三倍性能已验收。

本机现有[WSL低内存配置与验证](docs/stages/2026-10-23-wsl-memory-budget.md)：1GB、4核、F盘交换，三家首帧的12路输出与原结果SHA一致，空闲后虚拟机自动释放；完整52帧仍需额外空间与单独验收。

## Docker

```bash
docker build -t flash-chroma .
docker run --rm flash-chroma
```

镜像固定 Pixi 版本，仅按锁文件安装默认环境，并运行同一 `test` 门禁。本机构建目录、Pixi 环境、实验数据与日志不进入构建上下文。直接运行镜像即可验证，不必挂载整个仓库覆盖容器中的依赖和构建产物。

## 当前研究成果与检查点

本次已整合 R28–R51 的分类语料、策略比较、C99/结构化 AVX2 后端、ROM 导出与阶段证据。[研究进展](docs/research-progress-r28-r51.md)保留各阶段的已测结论；性能收益仅适用于其声明的输入、机器和资源。

2026-10-16 同步快照：原矩阵已尝试 **4,471/7,917** 项，包含 4,465 条有效色域观测、6 项拟合阶段失败，不能全部称为通过。控制器因一个 case 任务退出而停止，检查点已保留；完整训练、联合规则冻结和留出评价尚未完成。[机器可读检查点](datasets/problem16-v1/matrix-checkpoint.json)。

- 200 条四级 LUT 链、320 张分类合成图及 23 组探针已完成数据审计；逐 case 台账分别维护质量、容量和已验证的速度选择。
- 混合阶段容量在 18 个已测曲线训练源中，让 9 个源降低最优 mean，另 4 个在相同 mean 下节省节点存储。[方法与边界](docs/r47-mixed-capacity.md)。
- 独立 C99 核心与 ROM 导出支持端侧部署。[部署说明](portable/README.md)。实体手机速度与功耗尚未测量。
- 有界 CG 续算恢复一个拟合失败，并通过 CPU/CUDA/C99 完整色域一致性核对；该噪声模型误差仍高，没有替换精度冠军。[全部指标](docs/r51-bounded-cg-recovery.md)。

远端新增的 100 张自然照片保留独立来源与清单。历史 R28–R51 结果仍绑定各自图集，不能视作已对新照片队列全量重测。现有完整 PDF 仍为 R27 冻结范围，后续阶段见文档与证据归档。

## 项目导航

| 路径 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Agent 交流、授权、语言与证据规范 |
| [TOOLCHAIN.md](TOOLCHAIN.md) | 当前构建配置、测试入口、依赖环境与 CI |
| [portable](portable/README.md) | 无堆分配的 C99 映射核心与 ROM 部署 |
| [python/lutlab](python/lutlab) | 拟合、模型格式、验收与统一 CLI |
| [cpp](cpp)、[gpu](gpu)、[zig](zig)、[rust](rust) | CPU、可选 CUDA 和可选 SIMD 实现 |
| [tests](tests)、[cpp/tests](cpp/tests) | Python 契约与 C++ 内核正确性测试 |
| [embedded](embedded/README.md) | 独立 C99 运行时，Cortex-M3/RV32 FreeRTOS 与 Cortex-A53 Linux 的 QEMU 门禁（WIP） |
| [docs/README.md](docs/README.md) | 技术文档、R17–R51 阶段实验与报告索引 |
| [docs/LOGGING.md](docs/LOGGING.md) | 独立实验日志与团队交接 |
| [report/README.md](report/README.md) | 冻结报告、数据证据与重建边界 |
| [assets/LUT](assets/LUT/README.md) | 68 份外部 LUT、来源锁定与授权信息 |
| [现成 LUT 研究报告](artifacts/local-lut-study/20261016/report.md) | PR #9 的 22 种配置、单级及四级研究摘要与适用边界 |
| [本轮同步与后续建议](docs/stages/2026-10-16-sync-pr-roadmap.md) | 主干整合、验证记录与后续阶段验收建议 |
| [工程对齐阶段](docs/stages/2026-10-16-engineering-alignment.md) | 基线/续跑/账本修复、C99 共同契约及验证边界 |
| [误差来源研究](docs/stages/2026-10-16-error-causes.md) | 四例全色域归因、固定表示下界、加权/整数精化及照片退化 |
| [PR #9 基线勘误](report/data/pr9-baseline-correction/correction.json) | 保留原始测量，另存 8/68 行派生基线修正 |

`data/`、`build/`、`build-*/`、`.pixi/`、`logs/` 与通常的 `artifacts/` 内容是本机产物；`artifacts/local-lut-study/20261016/` 中已纳入版本控制的精简研究证据是例外。历史报告中的分支名、硬件和性能数字描述对应实验阶段；当前开发流程以本 README、工具链说明与仓库配置为准。
