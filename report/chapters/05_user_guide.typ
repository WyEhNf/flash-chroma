#import "../helpers.typ": meta

= 团队使用指南与复现顺序

== 开箱、构建和测试

进入 `~/problem_probe/16`，先安装 Pixi，使用项目已锁定的主环境。Windows 队员以 Arch/Ubuntu WSL2 执行主线；原生 macOS ARM 在清单中，但必须由持有该平台的队员自行实测 C++26/Zig/Rust 构建。`pixi run test` 编译当前默认 Zig 16 lane、C++26 和 Rust 对照核，并执行 C++ 全色及 Python 测试。不要将不同机器的性能时间并排宣称速度提升。

```bash
cd ~/problem_probe/16
pixi install -a
pixi run test
pixi run verify-data
```

首次没有数据时，`competition-check` 会先获取完整 Kodak 图像、构造 29/100 张图和指定的模拟场景，再测试、核验和筛选；下载失败不会静默退回合成数据。首次构造可能需较长时间及约 1.8 GiB 磁盘空间。已有旧数据且缺清单时，可在确认来源后执行 `pixi run adopt-data`；该操作只为现有文件建哈希，不提供上游来源证明。

== 跑候选、精度与吞吐量

官方 Threshold 未公布，下面的 `2.0` 仅用于复现实验，不能原样作为比赛门槛。官方明确统计粒度后用 `--metric mean|p99|max` 指定；如裁判允许单级复合，再显式加 `--allow-composite`。

```bash
pixi run competition-check --scenario isp-0 --threshold 2.0 --metric mean --threads 20
pixi run select --scenario isp-0 --m 17 25 33 --profiles tetra errorgrid residual residual_tail --threshold 2.0 --threads 20 --reps 5
pixi run validate --scenario isp-0 --threshold 2.0 --threads 20 data/models/isp-0/residual_ls_tetra_int_m17/stage{1,2,3,4}.slut
pixi run zig-perf --widths 4 8 16 --blocks 1024 4096 8192 --schedules static dynamic,1 --threads 4 20 --reps 3 data/models/isp-0/residual_ls_tetra_int_m17/stage{1,2,3,4}.slut
```

`select` 为缺少缓存的候选自动调用拟合，再做真实内核验证。`validate` 留下每图数据、全色统计、最差颜色和模型 SHA；失败时进程返回非零。`zig-perf` 是长时间测量，应在机器负载稳定时独立运行，不能和其他 CPU 工作并行。`jshc bench` 的 `set_ms_p50_rep` 是完整 100 图轮次中位数；`apply_ms_mean` 是每张图跨轮最佳时间的平均，数值更乐观，不能用它排序提交方案。

单个方法可用 `pixi run fit --scenario isp-0 --mode residual --m 17 --method ls_tetra_int` 生成；`--grid error` 选择误差驱动非均匀网格。复现历史基线时，当前代码重新拟合的 m=17/25/33 共 12 个 `.slut` 与存档 `bench_models` 逐字节相同，日志 `d4e6375c`、`5ce1f5e1`、`62445746`。官方数据到手后须重新拟合，不要提交当前模拟表。

== 查日志、回退和团队同步

```bash
pixi run logs
python -m lutlab.runlog show 52e23c0b
```

`logs/runs/<UTC>-<任务>-<ID>/` 下 `run.json`、`selection.json`、`validation.json`、`sweep.json` 和 `stdout.log` 保存完整口径；`competition-check` 另有 `test.log`。`logs/` 的 Git 历史独立于主代码仓库，主代码 `git reset` 不会撤销一次实验，也不会把旧日志自动推送给队友。团队应单独备份或共享日志仓库与生成数据清单；对比结果时核对模型哈希、数据哈希、代码提交、线程数、重复次数和阈值。新方法若失败，回到有完整哈希与门禁的上一候选，而非凭文件名“stage1.slut”猜版本。

== 从官方赛题包过渡

先登记官方四个 LUT 的字节尺寸、位深、索引顺序及 SHA，再用少量人工颜色构造黄金查表样例，确认参考实现与主办方样例一致。按官方文件格式做适配时，先保持 `io.py`/C++ 的一致性和损坏文件拒绝；随后用公布的 Threshold 和判定粒度替换本地参数，重新跑全色或主办方指定集，再测 100 图。若官方把拟合、PNG I/O 或模型初始化计入性能，必须另建同边界计时，当前 `set_ms_p50_rep` 不足以描述端到端提交时间。

官方数据和接口未收到之前，不应对 `PROBLEM.md` 的未明确部分作静默假设。最少需要四阶段模式过线；单阶段复合只在书面规则明确后参与选型。保留 `stress-0`、`warp-0` 测试用于发现失败模式，但不能以它们代替官方盲测。

== 重建本报告

本报告用独立 `report/pixi.toml` 安装 Typst 与 Noto CJK 字体。生成器在*已提交代码和独立日志固定*后读取 `logs/`，写入 CSV、固定时间戳的原始文件归档、SHA 索引和图；它不修改实验日志。此版本固定主扫描运行 ID #meta.selected_run_id；重新做新一轮官方扫描时，应明确更新 `scripts/build_typst_data.py` 的固定 ID，不能偷偷把旧表换成新日志。

```bash
pixi run python scripts/build_typst_data.py
pixi run --manifest-path report/pixi.toml compile
pdfinfo report/exploration.pdf
```

若只想阅读，`report/exploration.pdf` 已是编译好的 A4 文档；`report/data/DATA_INDEX.md` 列出归档与 CSV 的 SHA-256。`report/data/run_records_exact.tar.gz` 可离线取回本报告取数时的运行记录。图像本体和 LUT 本体不在报告包内，仍应依照 `data/manifest.json` 单独保存或重新构造并核验。
