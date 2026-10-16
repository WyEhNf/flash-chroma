# 极速焕彩：第 16 题算法探索与可复现实验工程

**2026-10-16 同步检查点：** 当前矩阵控制器已停止，原计划已尝试4,471/7,917项，其中4,465条有效色域观测、6项拟合阶段失败；留出尚未启动。完整停止快照见[检查点](datasets/problem16-v1/matrix-checkpoint.json)。R51新增观测已在无活动写入器时归并，总账本4,602条；既有质量冠军保持不变。此状态不代表全量测试完成。

本仓库针对 **【2026 Hackathon 决赛】第 16 题「极速焕彩」**：把四个 `256³` RGB 整数 LUT 稀疏化到边长 `17–33` 的网格，在图像上执行四级整数色彩映射。当前采用 Python 离线拟合、独立可构建的 C++17 运行时、运行时检测的 AVX2 加速与标量回退；Zig、C++ SIMD、Rust 是可选对照后端。

**当前统一入口：`python -m lutlab`。** 支持任意四张原始 LUT 的 `fit --inputs ... --grid dp --method ls_tetra_jitter`，以及 CPU/CUDA 共用的 `apply`、`cube`、`verify`、`bench-models`、`validate`、`accept` 和严格配对 `compare`。先设置 `PYTHONPATH=python`；CPU 程序用 `JSHC_BIN`，可选 CUDA 程序用 `JSHC_CUDA_BIN` 或显式 `--executable`。接口、完整复现及本机 100 图结果见 [R19 统一交付与严格验收](docs/r19-delivery-results.md)。旧入口继续可用，历史时间不与当前结果混排。

**R20正确性审计：** `validate`现在实际执行图片路径，并逐字节核对图片输出与全色映射，补上16位RGB源文件可能被Pillow隐式降位后误认的验收缺口。八组CPU/CUDA的100图及全色域验收记录、容量比较和剩余问题见[R20审计](docs/r20-correctness-audit.md)与[小型证据归档](report/data/r20/README.md)。

**R21可选边界拟合：** `ls_tetra_boundary`完整覆盖输入边界，七组已测模型平均误差均下降，但五组最大误差增加，故仅作为显式`dp_boundary`候选。相同加权系统的CSR组装经7对比较快2.775倍；这不是图片映射加速比。[方法及原始证据](docs/r21-boundary-fitting.md)。

**R22结构化拟合与完整流程优化：** 对全部LUT字节证明可分离后，`ls_tetra_structured`使用一维整数最小最大误差DP，并展开为普通三维节点。九组CPU/CUDA全色及100图验收完成；仍有三个示例均值门禁失败。默认jitter的CSR优化保持28张旧模型字节一致，完整四表拟合7对配对加速1.366倍。[方法、失败诊断与证据](docs/r22-structured-fitting.md)。

**R23 CUDA内存与测速路径核验：** `bench`的设备图像缓冲峰值由900 MiB降至450 MiB；新增驻留测速结果的逐字节核对。全色与分组1/7/100的100图结果一致；7对比较未证明速度提升。[构建、比较及证据](docs/r23-cuda-memory.md)。

**R24完整节点支撑研究：** `ls_tetra_supported`在均匀全色域目标下观察所有网格节点，消除数据项零支撑。11组CPU/CUDA验收及7对完整拟合比较完成；精度收益有限且拟合整体变慢，故不替换默认方法。[结构保证、反例与证据](docs/r24-supported-fitting.md)。

**R25精确全色域拟合：** 可选C++17离线库用uint64组装全部256³颜色，`ls_tetra_full`保持既有四级运行时及模型格式。11组固定尺寸mean均下降；两个裁剪失败在合法m33容量下通过本地示例均值门槛。当前通过模型的100图CPU/CUDA宿主往返中位数为88.659/67.1277 ms，仍不是官方成绩。[构建、严格比较、剩余问题与证据](docs/r25-full-domain-fitting.md)。

**R26箱约束研究：** 新候选验证连续KKT条件，并精确比较量化后模型的全色域未舍入平方误差。13组实际验收没有新增通过场景，最终mean仅四组改善，故不替换R25、不追加性能扫描。[数值保证、反例与证据](docs/r26-box-constrained-fitting.md)。

**R27阶梯插值与可达布点：** 显式候选`adaptive_full`保持四张独立m³表，压力源全色mean由4.1478降至0.3767，100图最差mean由6.2241降至0.7870；固定配置10/13通过示例门槛。当前模型100图CPU16/CUDA宿主往返86.864/67.7566 ms，OCIO同模型四线程接入另作实测。[方法、反例及证据](docs/r27-step-interpolation.md)；[最新完整PDF报告](output/pdf/problem16-latest-tested-report.pdf)。

**R28数据与case账本：** 200条完整四级LUT链、320张分类合成图、23组探针已完成完整审计；常量链与重复最终变换单独标记。`corpus`、`casebook`子命令维护数据、失败、mean/max最优与容量Pareto。9策略×3尺寸×200case的5400候选矩阵已开始；首个case的27项结果不能代表类别sweet zone。[范围与状态](docs/r28-corpus-program.md) · [数据目录](datasets/problem16-v1/README.md)。远端补充的五张Kodak自然照片保留独立来源与引用队列。

**R30/R31端侧运行时：** 新增独立无堆分配、无I/O和无浮点的[C99库](portable/README.md)，支持行步长、分块、原地处理和经证明的常量/曲线/节点捷径。3组完整RGB立方体与冻结原生结果一致；AArch64大小端模拟执行的12个完整输出流也一致。实体手机性能、功耗及新库配对速度尚未测量。[集中验收及边界](docs/r30-portable-runtime.md)。现有C++默认AVX2路径保持原实现。

**R32格式门禁：** CPU补齐网格元数据检查，CPU/CUDA在竞赛入口检查PNG原始RGB8类型。集中拒绝全部30/27个适用负样本；有效模型完整色域及每后端100合成图+5自然照片保持一致。[修复与复用证明](docs/r32-format-contract.md)。

**R33/R34新算法与阶段比较：** 一箱一节点的单调选择让17/33箱控制在合法m内零误差；两级前瞻仍以各自原表为节点标签，stress-13/m33的全色域max由38.4187降至2.2361，mean降至0.30875。实际100图最差mean1.0，五张照片在CPU/CUDA/C99上逐字节一致。7对同资源比较确认AVX2相对标量加速2.0709倍，未证明新模型映射提速。[算法及拒绝的候选](docs/r33-monotone-bins.md) · [严格阶段结果](docs/r34-candidate-results.md)。这些结果只覆盖预声明先导case；原5400矩阵与新策略的类别留出研究仍未完成。PDF仍为R27冻结报告。

**R35结构化运行时接入：** 新增显式`tetra_c99`、`tetra_structured_avx2`及统一`plan`诊断。完整节点/前缀证明用于常量、曲线、单节点和通用路径。两个构建的完整独立参考门禁、9个真实完整色域输出流和每新内核100+5图像均通过；尚无新内核配对速度结论。桌面桥接副本与缓存计入运行内存。[部署与验收](docs/r35-structured-runtime.md)。R36的2517项扩展计划已预声明，两套训练阶段完成并冻结联合规则前均不执行留出。

**R39/R40结构化性能与case选择：** 3模型×3后端的9项比较共162次计时已完成，统一16线程、固定100图，双侧符号检验对九项作Holm校正。结构AVX2相对普通AVX2在新压力与17箱模型上分别加速1.96477/3.17268倍，通用clip模型未证明显著改善。九项配置已绑定正确性证据登记到case账本，区分观测最快、证实最快和耗时/模型内存Pareto。[全部结果、内存代价及边界](docs/r39-structured-performance.md)。默认auto仍保持原有选择，矩阵留出研究和实体手机性能尚未完成。

**R41矩阵恢复：** 修复Windows控制器路径键导致的启动错误，基线和扩展均已有实际运行的开发/校准/回归进程。联合规则工具可检查完整4,680项训练覆盖；正式冻结与留出评估仍待完整训练完成。[恢复证据位置、规则口径及操作命令](docs/r41-matrix-resume.md)。

**R42类别训练对照：** 固定快照包含2083项训练记录，42/180组已完成双seed全13策略对照。mean与max经常选择不同策略，多个指标存在并列最优，并观察到m增大后最终误差反而增大的case；覆盖不足组不排名。[实际比较与边界](docs/r42-training-comparison.md)。这不是留出sweet zone结论。

**R43 ROM部署：** 新增`python -m lutlab.portable_export`，生成保留原四表字节与来源的C99只读数组，固件无需模型文件系统或Python。m17/m33两套编译数组及完整色域结果均匹配冻结原生输出，四种freestanding目标对象编译通过，三线性模型明确拒绝。[部署接口、资源开销与验收](docs/r43-rom-export.md)。本轮没有实体手机性能测量。

**矩阵里程碑：** R36开发720、校准720、回归357项均已完成，控制器正常退出；扩展留出720项尚未启动。R29基线仍在运行，两矩阵训练齐备并冻结联合规则前不查看留出输出。

**R44/R45适用区域与图像边界：** 四个新策略的180组训练对照全部齐备，组合策略相对adaptive_bins在9组改变指标，其余171组四指标相同；恒定最终链单独标记。[类别差异与容量反例](docs/r44-new-policy-regions.md)。三个代表源已完成6条完整色域流、600次标准图与五照片多后端核对；其中一个源的100图最差mean仍为14.0382，保留本地精度失败。[实际图像结果及待导入状态](docs/r45-representative-images.md)。这些结果不替代全13策略与留出评估。

**R47混合阶段容量：** 18个曲线训练源各枚举81种四级尺寸，1458个完整解析配置与54个既有均匀原生结果一致；45条新原生色域流完成CPU/CUDA/C99部署核对。9源的mean优于各自全13策略×3尺寸参照，5源同时节省节点存储；135条类别／预算指南已在任何留出输出前冻结。[精确方法、来源包装及边界](docs/r47-mixed-capacity.md)。原7917项矩阵保留，混合研究729个留出配置尚未评价。

**R50矩阵续跑与总账本归并：** 按完整case分片的执行器通过一次集中验证，复用52条记录、仅新增2条完整色域流，模型、输出SHA、全部误差及23组探针与原数值版本一致。旧控制器保存检查点并受控退出，新控制器以最多4个普通子进程续跑。R45/R47的45条记录已正式导入，总账本中9个混合训练源降低最优mean，另4个同误差节省节点存储。[实际凭据与边界](docs/r50-case-shards-and-canonical-import.md)。全量训练、规则冻结与留出比较尚未完成。

**R51求解器恢复与噪声边界：** 新增显式离线`python -m lutlab.robust_fit`，不放宽容差，以有界续算恢复一个随机对抗m33拟合；四个成功配置保持旧模型字节，恢复模型在CPU/CUDA/编译C99的完整色域输出一致。其mean128.839、max413.079仍高，保留已有mean与尾部最优策略。五配置追加独立边界标签，原失败及7917项分母不改。[全部指标、部署与限制](docs/r51-bounded-cg-recovery.md)。

**2026-10-15 R17 历史阶段：** 原生 Windows/AMD 8945HX 已完成阶段验收。新增真实 Q16 精化、内容绑定的模型缓存、明确范围的误差门禁，以及四级寄存器融合 AVX2。[阶段优化与实测](docs/r17-optimization-results.md) · [R17构建说明](docs/r17-delivery.md) · [算法推导](docs/r17-algorithm.md)。统一入口和基础部署见R19，新增拟合与当前实测见R25；[R19验收归档](report/data/r19/README.md)保留其冻结阶段的摘要、原始记录及模型。下文保留上游历史报告与数据获取背景，现有成果不能推算官方成绩。

**目前结论：有条件可选。** 本地 `isp-0` 模拟场景上已有通过示例门槛的四级候选；官方 LUT 格式、色差阈值及其统计口径、计时边界、单级复合是否合法仍需确认。本仓库的“通过”和速度数字都不是官方验收结果。

## 完整报告

**[阅读R27完整报告 PDF](output/pdf/problem16-latest-tested-report.pdf)**：R27完整精度、100图配对性能、内存、三个评分项和OpenColorIO/AdaInt/SVDLUT对比。后续数据与端侧阶段见上方文档，尚未合入这份冻结PDF。官方数据与阈值未取得，不据此判定官方分数。

**[历史中文探索报告 PDF](report/exploration.pdf)**（11 页，已纳入 Git；在 Codeberg 默认 `main` 也能打开）。它从题面和首个版本讲起，说明 20 条技术路线、历史24个候选的精度与速度、失败场景、可移植 SIMD 实验、三人分工及最终选题判断。

需要核对数字时看 [报告数据索引](report/data/DATA_INDEX.md)：其中有原始运行记录归档、696 条逐图结果、最坏颜色和 SHA-256。要修改或重建版式，请看 [Typst 源与复现说明](report/README.md)。这是固定实验记录的报告；后来代码或官方数据有变化时，须重新验证，不能直接沿用其中的性能结论。

## 获取仓库

主要仓库为[GitHub flash-chroma](https://github.com/WyEhNf/flash-chroma)，旧Codeberg保留上游历史。GitHub的R27及五张照片更新已纳入本地；后续R28–R31工作是否已发布，以实际Git提交和远端状态为准。原生Windows的CMake构建见[统一交付入口](docs/r19-delivery-results.md)，新独立C库见`portable/`。原有Pixi清单仍仅覆盖Linux与macOS ARM，不能据此认定macOS设备已经验收。

```bash
git clone https://github.com/WyEhNf/flash-chroma.git
cd flash-chroma
git status --short --branch
```

安装 [Pixi](https://pixi.sh/latest/installation/) 后，在仓库根目录运行：

```bash
pixi install --locked
pixi run --locked test
```

`test` 编译当前 CMake 配置选中的后端，并执行 C++ 全 `2²⁴` 色空间对照和 Python 测试；**无需先下载图像或生成 LUT**。额外后端由 `JSHC_ENABLE_CPP_SIMD/ZIG/RUST` 开关启用，默认关闭。旧 Pixi 清单仍安装这些工具链，纯 CMake 路线无需全部安装。`--locked` 要求清单与 `pixi.lock` 一致；本轮未更改锁文件或复验 Pixi 安装。

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
pixi run --locked fit --scenario isp-0 --m 18 --method ls_tetra_int --mode seq
pixi run --locked select --scenario isp-0 --m 18 --profiles tetra \
  --threshold 2.0 --metric mean --constraint-scope both --threads 4 --reps 3
```

这里的 `2.0` 只是本地演示门槛，比较使用未舍入统计量和严格 `<`。`--metric` 可选 `mean`、`p99`、`max`；`--constraint-scope` 明确指定图片、全色域或两者。实际内核由 `auto` 按可用能力选择；查看 `jshc info`。比较候选时看整组时间中位数 `set_ms_p50_rep`，不要把不同机器、线程数或历史“每图最佳”数字混排。

拟合输出在 `data/models/<scenario>/<variant>/<identity>/batch-<id>/`，包含完整 manifest 与四个模型，命令输出具体路径；输入清单为 `data/eval.txt` 和 `data/bench.txt`。缓存核验输入 LUT、参数、源码和模型内容，不复用旧的无 manifest 目录。生成数据和构建产物被 Git 忽略。旧图像可用 `adopt-data` 固定当前字节，但不能据此证明来源；详见 [DATA.md](DATA.md)。

## 按需选择命令

所有命令都从**仓库根目录**执行。`pixi run <任务> --help` 可查看任务底层程序的参数；任务定义以 [pixi.toml](pixi.toml) 为准。

| 目的 | 命令或入口 | 结果与注意事项 |
| --- | --- | --- |
| 构建和测试 | `pixi run --locked test` | 构建所选后端，运行一次阶段验收；无须 `data/`。 |
| 生成或核验数据 | `pixi run --locked gen-data --scenarios isp-0` / `pixi run --locked verify-data --scenario isp-0` | 生成图像、LUT 和清单；核验哈希及四级精确复合。 |
| 拟合单个模型 | `pixi run --locked fit --scenario isp-0 --m 18 --method ls_tetra_int --mode seq` | 原子发布四个 `.slut` 文件及 manifest。 |
| 传统精度/性能检查 | `pixi run --locked evaluate ...` / `pixi run --locked bench ...` | 用于迭代；严格提交门禁请用 `validate` 或 `select`。 |
| 严格门禁 | `pixi run --locked validate --threshold 2.0 <四个 .slut 路径>` | 基于真实可执行输出；失败返回非零，并写逐图记录。 |
| 候选筛选 | `pixi run --locked select --scenario isp-0 --m 17 18 --profiles tetra q16 --threshold 2.0 --threads 4 --reps 3` | 输出独立主线的 Pareto 候选及推荐；不推断总分。 |
| 一条命令复核 | `pixi run --locked competition-check --scenario isp-0 --m 18 --profiles tetra --threshold 2.0 --threads 4` | 构建、阶段测试、核验数据及候选；已验收的二进制可用 `--executable` 和 `--skip-tests`。 |
| 可移植 Zig 调参 | `pixi run --locked zig-perf --help` | 需先显式启用并编入 Zig 后端；不属于本轮默认验收。 |
| 历史路线探索 | `pixi run --locked -e ml routes` | 含 ML 路线，依赖 `ml` 环境；不代替当前严格门禁。 |
| 查看运行记录 | `pixi run --locked logs` | 从独立日志仓库列出运行 ID、状态和关联代码提交。 |

保守主线要求独立四级。`--allow-residual` / `--allow-composite` 显式启用研究路线，并在结果中单列；启用研究不表示官方认可该语义。`--existing-only` 只接受经验证的缓存；`--skip-cube` 不代表通过全色域约束。

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
| [docs/r17-optimization-results.md](docs/r17-optimization-results.md) | 当前优化、阶段验收、性能及明确失败的结果。 |
| [experiments/r16-five-directions.md](experiments/r16-five-directions.md)、[AUDIT.md](AUDIT.md) | 上游历史实验报告及代码审计。 |

更多背景按需查 [TOOLCHAIN.md](TOOLCHAIN.md)、[ROUTES.md](ROUTES.md)、[EVALUATION.md](EVALUATION.md)。报告中的 24 候选结果来自固定的 `isp-0` 本地实验；模型、机器和评测口径变动后必须重新测量。

## 独立日志与团队交接

`logs/` 是**另一个 Git 仓库**，主仓库会忽略它。日志包装写入 `run.json`、`stdout.log` 和相关 JSON；R17 的拟合、验证、选择和 workflow 入口不自动提交日志。历史日志在 Codeberg 的 [`experiment-logs` 分支](https://codeberg.org/Mooooonk/problem_probe_16/src/branch/experiment-logs)，新 clone 可单独取回：

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
