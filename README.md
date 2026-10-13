# 极速焕彩：第 16 题算法探索与可复现实验工程

本仓库针对 **【2026 Hackathon 决赛】第 16 题「极速焕彩」**：把四个 `256³` RGB 整数 LUT 稀疏化到边长 `17–33` 的网格，在图像上执行色彩映射，并同时考察色差、速度和规则合规性。它包含 Python 离线拟合、C++17 驱动、默认 Zig `@Vector` 推理内核、C++26 `<simd>` / Rust `core::simd` 对照内核、测试与独立 Git 实验日志。

**目前结论：有条件可选。** 本地 `isp-0` 模拟场景上已有通过示例门槛的四级候选；官方 LUT 格式、色差阈值及其统计口径、计时边界、单级复合是否合法仍需确认。本仓库的“通过”和速度数字都不是官方验收结果。先读 [图文探索报告](report/exploration.pdf) 可快速了解已试路线、失败案例和完整数据来源。

## 从 Codeberg 开始

Codeberg 的默认 `main` 保留较早的存档版本；**当前可运行的 Zig 默认实现和本 README 在 `codex/zig-default-pixi` 分支**。Rust 的 Pixi 依赖也只在此分支，不需要合入 `main`。建议在 Arch/Ubuntu WSL2 或 Linux 上执行；`pixi.toml` 还声明了 macOS ARM 平台，但需在实际机器上验证构建。原生 Windows 不在该 Pixi 清单的平台范围内。

```bash
git clone https://codeberg.org/Mooooonk/problem_probe_16.git
cd problem_probe_16
git switch --track origin/codex/zig-default-pixi
git status --short --branch
```

安装 [Pixi](https://pixi.sh/latest/installation/) 后，在仓库根目录运行：

```bash
pixi install --locked
pixi run --locked test
```

`test` 会配置并编译 C++、Zig、Rust 内核，执行 C++ 全 `2²⁴` 色空间的逐字节一致性测试和 Python 测试；**无需先下载图像或生成 LUT**。首次安装需要下载编译器及 Python 依赖，磁盘占用较大。`--locked` 要求清单与 `pixi.lock` 一致，避免上手时意外改锁文件。想运行 PyTorch 路线时再安装额外的 `ml` 环境：`pixi install --locked -e ml`。

没有 Pixi 的备选方式是 Ubuntu 24.04 [Dockerfile](Dockerfile)：

```bash
docker build -t jisu-huancai:latest .
docker run --rm -it -v "$PWD":/workspace jisu-huancai:latest pixi run test
```

容器构建也需要网络；仓库的 `.dockerignore` 排除本地大型数据、构建缓存和独立日志。

## 跑通一个完整候选

以下命令只构造 `isp-0` 这一组**模拟**四级 LUT，适合首次熟悉流程。`gen-data` 会从 Kodak 图像源下载 24 张自然图，另造 5 张压力图和 100 张测速图；首次构造需要联网、时间及约 GB 级磁盘空间。下载失败会报错，**不会自动把 29 图验证悄悄改成纯合成数据**。需要明确做离线纯合成试验时，另加 `--allow-synthetic-only`，但这种结果不可与本报告的 29 图结果比较。

```bash
pixi run --locked gen-data --scenarios isp-0
pixi run --locked verify-data --scenario isp-0
pixi run --locked fit --scenario isp-0 --m 17 --method ls_tetra_int --mode residual
pixi run --locked validate --scenario isp-0 --threshold 2.0 --metric mean --threads 4 \
  data/models/isp-0/residual_ls_tetra_int_m17/stage{1,2,3,4}.slut
pixi run --locked bench --scenario isp-0 --m 17 --method ls_tetra_int --mode residual --threads 4 --reps 3
```

这里的 `2.0` 只是本地演示门槛；`validate` 要求**每张图**的未舍入统计量严格小于阈值。`--metric` 可选 `mean`、`p99`、`max`，必须根据官方规则选定。它通过实际 `jshc cube` 输出检查图像色差，并默认统计全部 `2²⁴` RGB 颜色。`bench` 默认使用 `tetra_zig_simd`（Zig 16 lane），对 100 张图运行 3 轮；比较候选时看整组时间中位数 `set_ms_p50_rep`，不要把不同机器、线程数或历史“每图最佳”数字混排。

拟合结果位于 `data/models/isp-0/residual_ls_tetra_int_m17/`；输入清单为 `data/eval.txt` 和 `data/bench.txt`。`data/` 与 `build/` 被 Git 忽略，新的 clone 要自行生成或从可信备份恢复。若已有完整图像却缺 `manifest.json`，可在核对来源后运行 `pixi run --locked adopt-data` 建立本地哈希清单；该操作不能证明图像上游来源。数据布局详见 [DATA.md](DATA.md)。

## 按需选择命令

所有命令都从**仓库根目录**执行。`pixi run <任务> --help` 可查看任务底层程序的参数；任务定义以 [pixi.toml](pixi.toml) 为准。

| 目的 | 命令或入口 | 结果与注意事项 |
| --- | --- | --- |
| 构建和测试 | `pixi run --locked test` | 构建三个语言的内核，运行 C++ 和 Python 测试；无须 `data/`。 |
| 生成或核验数据 | `pixi run --locked gen-data --scenarios isp-0` / `pixi run --locked verify-data --scenario isp-0` | 生成图像、LUT 和清单；核验哈希及四级精确复合。 |
| 拟合单个模型 | `pixi run --locked fit --scenario isp-0 --m 17 --method ls_tetra_int --mode residual` | 输出四个 `.slut` 文件；`--mode composite` 只生成单级备选。 |
| 传统精度/性能检查 | `pixi run --locked evaluate ...` / `pixi run --locked bench ...` | 用于迭代；严格提交门禁请用 `validate` 或 `select`。 |
| 严格门禁 | `pixi run --locked validate --threshold 2.0 <四个 .slut 路径>` | 基于真实可执行输出；失败返回非零，并写逐图记录。 |
| 候选筛选 | `pixi run --locked select --scenario isp-0 --m 17 --profiles tetra residual errorgrid --threshold 2.0 --threads 4 --reps 3` | 缺模型会自动拟合；逐个过门禁后才测速，无合格获胜者返回状态码 2。 |
| 一条命令复核 | `pixi run --locked competition-check --scenario isp-0 --m 17 --profiles residual --threshold 2.0 --threads 4` | 自动准备缺失数据、构建、测试、核验，再做完整精度及 100 图筛选；耗时较长。 |
| 可移植 Zig 调参 | `pixi run --locked zig-perf --help` | 比较 lane、分块、调度和线程；需显式给出模型路径。 |
| 历史路线探索 | `pixi run --locked -e ml routes` | 含 ML 路线，依赖 `ml` 环境；不代替当前严格门禁。 |
| 查看运行记录 | `pixi run --locked logs` | 从独立日志仓库列出运行 ID、状态和关联代码提交。 |

默认自动筛选**排除** `composite` 单级复合，即使其数值误差达标。只有收到官方明确许可，才对 `select` / `competition-check` 显式加 `--allow-composite`。`--existing-only` 可防止筛选器自动拟合；`--skip-cube` 只适合缩短探索，不应当作完整全色验证。两种设置的实际适用命令以各入口的 `--help` 为准。

## 代码、数据和报告在哪里

| 路径 | 作用 |
| --- | --- |
| [PROBLEM.md](PROBLEM.md)、[DECISION.md](DECISION.md) | 原题整理、待确认规则、三人团队锁题判断。 |
| [python/lutlab](python/lutlab) | 模拟数据、LUT 格式、插值/拟合、精度门禁、候选筛选和日志。`PYTHONPATH` 由 Pixi 设置。 |
| [cpp](cpp)、[zig](zig)、[rust](rust) | `jshc` 命令行驱动与三种可移植 SIMD 实现。`build/jshc` 支持 `apply`、`ref`、`cube`、`bench`、`info`。 |
| [tests](tests) | Python 测试；C++ 内核测试在 `cpp/tests/`。 |
| `data/`、`build/`、`.pixi/` | 本机生成的图像/LUT/模型、二进制、依赖环境；均不进入主 Git。 |
| [report/exploration.pdf](report/exploration.pdf)、[report/README.md](report/README.md) | 已编译的中文完整报告、Typst 源和重建说明。 |
| [report/data/DATA_INDEX.md](report/data/DATA_INDEX.md) | 跟随主 Git 的原始运行记录归档、逐图 CSV、最坏颜色与 SHA-256 索引；不含约 1.8 GiB 图像/LUT 本体。 |
| [experiments/r16-five-directions.md](experiments/r16-five-directions.md)、[AUDIT.md](AUDIT.md) | 当前五项发展工作的详细实验报告及代码审计。 |

更多背景按需查 [TOOLCHAIN.md](TOOLCHAIN.md)、[ROUTES.md](ROUTES.md)、[EVALUATION.md](EVALUATION.md)。报告中的 24 候选结果来自固定的 `isp-0` 本地实验；模型、机器和评测口径变动后必须重新测量。

## 独立日志与团队交接

`logs/` 是**另一个 Git 仓库**，主仓库会忽略它。每次调用日志包装的任务会写 `logs/runs/<UTC时间>-<任务>-<ID>/run.json`、`stdout.log` 和相关 JSON，并在日志仓库自动提交；记录里有主仓库提交、分支、参数、机器和锁文件哈希。当前历史日志在 Codeberg 的 [`experiment-logs` 分支](https://codeberg.org/Mooooonk/problem_probe_16/src/branch/experiment-logs)，新 clone 可单独取回：

```bash
# 仅在尚无 logs/ 时执行；它会成为被主仓库忽略的独立 clone
git clone --branch experiment-logs --single-branch \
  https://codeberg.org/Mooooonk/problem_probe_16.git logs
pixi run --locked logs
pixi run --locked python -m lutlab.runlog show 52e23c0b
```

`runlog show` 的 ID 可取前缀；完整筛选结果在对应目录的 `selection.json`。报告还随仓库保存了取数时的[原始运行记录归档](report/data/DATA_INDEX.md)，因此只读报告不必克隆 `logs/`。新实验结束后，主仓库代码和日志要**分别** `git push` 与 `git -C logs push`；主仓库的回退不会回退实验记录。更多约定见 [docs/LOGGING.md](docs/LOGGING.md)。

继续开发前，先看 `git status --short --branch` 与 `git -C logs status --short --branch`，确认所处代码与日志分支；修改实现后先提交代码，再跑要归档的测试或 benchmark。比较新旧运行时核对代码提交、输入清单哈希、模型哈希、内核、线程数、重复次数和阈值。`main` 用于保留旧版；当前 Zig/Rust 工具链工作留在 `codex/zig-default-pixi` 分支，旧架构特化版本另在 `archive/*` 分支和版本标签中。

## 接入正式赛题包时

先确认官方 LUT 的位深、字节序与索引顺序，构造少量人工颜色的黄金样例；再确认 `Threshold` 是逐图均值、p99、最大值还是别的规则，以及 I/O、拟合与映射各阶段如何计时。完成格式适配后，重新生成正式数据清单和模型，使用官方阈值跑 `validate` / `competition-check`，最后在目标机器重新 benchmark。当前 `isp-0`、`stress-0` 等只是模拟场景；尤其压力场景的误差不能用常规 ISP 的结果替代。规则待确认项和风险在 [DECISION.md](DECISION.md) 中。
