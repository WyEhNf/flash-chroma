# 工具链、一键环境与独立日志系统说明 (`TOOLCHAIN.md`)

本文档说明 `~/problem_probe/16` 为 **【2026 Hackathon 决赛】第 16 题：极速焕彩** 构建的可复现开发环境、构建工具链、Git 版本追踪规范以及独立实验日志仓库。

---

## 1. 跨平台一键环境配置（3 人团队零摩擦同步）

针对 3 人本科生团队（可能混合使用 Windows + WSL2、Ubuntu Linux 或 macOS）环境不一致的痛点，项目同时提供 **Pixi 锁文件方案（主推）** 与 **Ubuntu 24.04 Docker 容器方案（备选/兜底）**。

### 方案 A：Pixi 一键安装（推荐，毫秒级激活）

配置文件：[pixi.toml](pixi.toml) 与锁文件 [pixi.lock](pixi.lock)。
Pixi 会从 `conda-forge` 安装 Zig 0.17、Linux 上的 GCC/G++ 16（用于 C++26 `<simd>`）、Rust 1.99（仅本实验分支）、`CMake`、`Ninja` 以及 `Python 3.12`、`NumPy`、`SciPy`、`Pillow` 和 `Pytest`。`ml` 环境额外安装 PyTorch CPU。Rust `portable_simd` 目前需要构建命令局部设置 `RUSTC_BOOTSTRAP=1`。

```bash
# 1. 克隆仓库后一键安装全部环境（default 与 ml）
pixi install -a

# 2. 编译 Zig/C++26/Rust 内核并运行 C++ 与 Python 全部单元测试
pixi run test

# 3. 生成标准测试集（24 张 Kodak 真彩自然图像 + 5 张极限合成压力图 + 100 张吞吐量测试图 + 6 组四级 256^3 LUT 场景）
pixi run gen-data

# 4. 运行单次稀疏化拟合、精度评测与 C++ 吞吐量基准测试
pixi run fit --scenario isp-0 --m 33 --method ls_tetra_int --mode residual
pixi run evaluate --scenario isp-0 --m 33 --method ls_tetra_int --mode residual
pixi run bench --scenario isp-0 --m 33 --threads 0

# 5. 运行全套技术路线大横评（朴素 / 经典 / 现代 / 前沿 / 高阶基函数 / 低秩 Tucker / RBF / MLP / SIREN）
pixi run -e ml python -m lutlab.routes

# 6. 查看独立实验日志
pixi run logs
```

### 方案 B：Ubuntu 24.04 容器化方案（Dockerfile）

配置文件：[Dockerfile](Dockerfile)。以 `ubuntu:24.04` 为基座，内置完整构建链与 Pixi 锁环境：
仓库的 `.dockerignore` 排除本机 `.pixi/`、生成的 `data/`、`build/` 与独立 `logs/`，避免将数 GB 本机文件复制进镜像。

```bash
docker build -t jisu-huancai:latest .
docker run --rm -it -v "$PWD":/workspace jisu-huancai:latest pixi run test
```

---

## 2. Zig/C++26/Rust SIMD + C++17/Python 混合架构设计

为兼顾**算法快速迭代（稀疏化求解）**与**极致执行速度（40 分性能分 + 20 分工程可移植分）**，代码库采用清晰的二层解耦架构：

1. **离线/预处理稀疏化层（Python `lutlab`）**：
   - [io.py](python/lutlab/io.py)：定义二进制 `.lut256`（完整 $256^3 \times 3$ LUT，48 MB/个）与紧凑 `.slut`（稀疏 $m^3 \times 3$ 晶体表 + 预计算 256 项 `idx`/`frac` Q16 定点轴查找表）。
   - [interp.py](python/lutlab/interp.py)：与 C++ 逐比特完全一致（Bit-Exact）的 Q16 四面体插值镜像与精确稀疏权重矩阵构造器。
   - [fit.py](python/lutlab/fit.py)：涵盖最近邻采样、亚像素采样、盒式滤波、可分离张量最小二乘（Hat / Lagrange 三次 / B-Spline 二次与三次）、精确四面体稀疏最小二乘（CG + Jacobi 预条件）、IRLS $L_p$ 极小极大逼近、**8 色棋盘格整数坐标下降精化（Integer Coordinate Refinement）**及**曲率自适应非均匀网格（Adaptive Knot Placement）**。
   - [cascade.py](python/lutlab/cascade.py)：多级串联误差传播补偿（Cascade Residual Absorption）、四级复合单级等价映射、3D 多项式拟合、Tucker HOSVD 低秩分解、3D RBF 径向基网络、超轻量残差 MLP 与 SIREN 隐式神经 LUT。
2. **在线推理核心（C++17 `jshc` 调度，默认 Zig `@Vector`）**：
   - [lut.hpp](cpp/include/jshc/lut.hpp) / [lut.cpp](cpp/src/lut.cpp)：零外部动态库依赖的纯 C++17 核心。
     - **Q16 纯整数四面体插值**：利用预计算的 256 项 `off[axis][x]` 与 `frac[axis][x]` 表，支持均匀或非均匀网格。
     - **16 像素并行**：默认 `tetra_zig_simd` 使用 Zig `@Vector(16, i32)`；显式 `tetra_zig_simd4`、`tetra_zig_simd8`、`tetra_zig_simd16` 可复跑 lane 宽度实验。`tetra_cpp_simd` 使用 C++26 `<simd>`；`tetra_rust_simd` 使用 Rust `core::simd`。这些内核不使用手写汇编或架构特化 intrinsic。旧 `tetra_avx2` / `tetra_asm` 名称保留为 C++ SIMD 内核的兼容别名。
     - **L1/L2 Cache 分块四级流水融合（Block-Fused Cascade）**：以 `4096` 像素（`12 KB`）为单位在线程私有栈缓冲区中连续完成 4 个色彩空间的串联映射，避免 4 次读写主存，完美契合 CPU L1 Data Cache（48 KB）。
       `JSHC_BLOCK_PIXELS=1024|4096|8192` 与 `OMP_SCHEDULE=static|dynamic,1|guided,1` 用于无架构特化调参；默认块为 4096，调度为 `dynamic,1`。
   - [main.cpp](cpp/src/main.cpp)：支持 `apply`、`ref`、`cube`、`bench`、`info` 五大子命令，输出高精度分阶段计时 JSON。

---

## 3. 独立实验日志系统（Independent Run-Log System）

实现文件：[runlog.py](python/lutlab/runlog.py)。

为了确保在频繁 `git commit` / `git reset` / 分支切换时**绝对不会丢失任何一次实验日志**：
- `logs/` 目录在首次运行时自动初始化为一个**完全独立的 Git 仓库**（`logs/.git`），并在主代码仓库的 [.gitignore](.gitignore) 中被排除。
- 每次调用 `Run(name, params)` 上下文管理器时：
  1. 自动在 `logs/runs/<UTC时间戳>-<任务名>-<8位UUID>/` 下创建独立目录；
  2. 自动捕获主代码仓库当前的 `git commit SHA`、分支名、工作区是否 dirty，若存在未提交修改则自动保存 `code.diff` 快照及 SHA256；
  3. 实时双写终端输出到 `stdout.log`，将全部超参数、硬件环境（CPU 型号、核心数）与评测指标写入 `run.json`；
  4. 追加单行摘要至 `logs/index.jsonl`，并在 `logs/` 独立 Git 仓库中自动执行一次 `git commit`。
- 也可通过环境变量 `JSHC_LOG_DIR=/path/to/external_logs` 将日志仓库挂载到任意工作目录之外的路径。
- `run.json` 额外记录 `pixi.lock` 的 SHA-256；`competition-check` 的子进程测试输出保存在 `test.log`。
