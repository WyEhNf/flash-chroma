#import "../helpers.typ": meta

= 工程架构、数据和回溯系统

== 从原始 LUT 到最终图像

代码分为离线稀疏化和在线映射两层。`python/lutlab/data.py` 生成或核验输入图像与完整 LUT；`fit.py` 和 `cascade.py` 产出 `.slut`，其中包含节点、非均匀轴位置以及按原始浮点网格计算的 `idx/frac` Q16 表；`io.py` 和 `interp.py` 提供 Python 精确镜像。在线 `jshc` 的 C++17 层负责 PNG 读取、OpenMP 分块、四阶段流水及输出；默认插值内核是 Zig `@Vector(16, i32)`。C++26 `<simd>` 与 Rust `core::simd` 用于可移植性和速度对照。当前工作分支有 Rust Pixi 依赖，主分支没有；旧 AVX2/汇编尝试保存在归档提交/分支，当前主线不依赖架构特化代码。

`jshc cube` 对全部 16,777,216 种 RGB 颜色输出裸字节。`validation.py` 对比精确四阶段复合表，进一步在每张评测图上计算均值、RMS、p99、最大值和失败原因。`selection.py` 将拟合方法与实际插值内核成对评测：`ls_tri` 配 `tri_float`，四面体方法配 Zig。它只给通过用户指定阈值且规则许可的候选做吞吐量测试，按完整 100 张图的重复轮次中位数选方案。对于 Docker、macOS 和官方 CPU，本仓库还没有同等范围的实测结果。

== 数据集、真值和文件完整性

本地精度集是 24 张 Kodak 原图统一重采样后的图像，加 5 张覆盖色立方体、色相渐变、随机颜色、记忆色和中性灰边界的合成图，共 29 张。性能集从这些照片生成 100 张 1024×768 RGB 图。`isp-0/isp-1`、胶片、扭曲、裁剪和阶梯量化压力场景共六类模拟四阶段 LUT；`isp-0` 是本轮当前 24 候选全色验收的唯一场景。合成图和模拟 LUT 增强了覆盖，却不能代表未知的正式评测分布。

数据生成器默认要求 24 张 Kodak 原图全部获取；失败直接报错。只有显式 `--allow-synthetic-only` 才会生成降级数据。`data/manifest.json` 固定来源模式、种子和 155 个原图/图像/列表文件的 SHA-256；列表路径相对于项目根目录。`verify-data` 还检查 29/100 数量、尺寸与 RGB 模式、四个完整 LUT 的哈希，并重新复合验证 `composite.lut256` 的内容。约 1.8 GiB 图像和 LUT 本体由主仓库忽略；报告只存原始清单，不复制大型文件。

== 测试边界与曾经发现的问题

C++ 测试对 m=17/25/33、全部 2²⁴ RGB 输入核对标量、C++26、Zig 4/8/16 lane 与 Rust 的位精确结果，并覆盖长度不满向量宽度的尾部及多线程级联。Python 测试补足 `.slut` 往返、序列化 Q16 表、损坏文件拒绝、缓存隔离和拟合行为。最终本地 `pixi run test` 的 CTest 1/1、Pytest 5/5 通过。

审计曾发现三个会污染结论的缺陷：Python 读取 `.slut` 后重算浮点轴表，少数 Q16 分数差 1；自适应与普通网格复用同一缓存目录；C++ 对损坏文件可能在检查前做越界指针运算。它们分别在 `866ca68` 与后续提交中修复，并把失败测试和修复复测保留在独立日志。基准输出还区分“各图跨轮取最短均值”和“完整 100 图最佳/中位轮次”，避免把前者当持续吞吐量。报告图 `docs/plots/cpp_throughput.png` 标识为历史数据，不用于当前默认 Zig 16 lane 排名。

== Pixi、容器与独立日志

主 `pixi.toml` 锁定 Zig 0.17、Linux GCC 16.2 的 C++26、Rust 1.99、Python 3.12、CMake/Ninja 和科学计算包；ML 附加环境有 PyTorch。WSL/Linux 是已实测开发平台，macOS ARM 在清单中但尚无团队机器复验。Ubuntu 24.04 Dockerfile 作为备选，`.dockerignore` 排除数 GiB 的 Pixi、数据与日志；当前 WSL 没有 Docker，镜像未实测。`report/pixi.toml` 为 Typst 和 Noto CJK 字体创建独立环境，不改动算法锁文件。

`logs/` 有自己的 Git 仓库，主代码回退不会删除日志。本报告取数时共有 #meta.run_count 份 `run.json`，其中 #meta.failed_run_count 份明确记录为失败；取数日志 Git 为 `#meta.logs_git_commit`。每条记录包含命令参数、代码 SHA、脏工作区标记、CPU、运行时间、Pixi 锁哈希及原始输出/附属 JSON。`report/data/run_records_exact.tar.gz` 按原相对路径和原始字节归档本次所有日志文件；`manifests_exact.tar.gz` 固定输入清单，`experiments_exact.tar.gz` 固定历史实验 JSON。它们不包含被忽略的大型图像；第 6 章给出 SHA-256。
