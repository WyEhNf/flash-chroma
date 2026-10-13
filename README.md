# 极速焕彩 —— 【2026 Hackathon 决赛】第 16 题可行性探测与工程脚手架

本项目是针对华为海思出题的 **【2026 Hackathon 决赛】第 16 题：极速焕彩** 构建的完整算法探索、Zig `@Vector` 默认推理内核、严格单元测试及跨平台一键开发环境。C++26 `<simd>` 与 Rust `core::simd` 可用于对照实验。

---

## 核心结论速览

- **选题可行性判定**：🟡 **有条件可选**；需先确认官方阈值、LUT 格式和单级等价方案口径。详见 [DECISION.md](DECISION.md)
- **历史执行速度表现**：先前版本在 `i7-13700H` 上测得约 **`1.2 ms/张`**（四级）和 **`0.38 ms/张`**（单级）；这些数据不代表当前 Zig 默认实现的实测速度。各内核的新结果应以同一机器上的 benchmark 日志为准。
- **精度与压缩表现**：4 个 $256^3$ LUT（192 MB）压缩至 $m=17$（58.9 KB，压缩比 **3,417×**）或 $m=33$（431.2 KB，压缩比 **466×**），通过**四面体精确稀疏最小二乘 + 8 色棋盘格整数精化 + 多级残差传播补偿 / 等价预复合**，在常规 ISP/胶片场景下将平均色差 $\Delta E$ 控制在 **`0.8 ~ 1.3`** 以内。

---

## 文档导航

| 文档 | 内容说明 |
| :--- | :--- |
| [PROBLEM.md](PROBLEM.md) | 从官方 HTML 快照完整提取的赛题原文、公式转写、晶体空间插值示意图及潜在规则歧义备注 |
| [DECISION.md](DECISION.md) | 有条件的选题结论、规则确认问题清单、3 人本科生团队分工表 |
| [TOOLCHAIN.md](TOOLCHAIN.md) | 一键环境安装（`pixi.toml` + `Dockerfile`）、C++/Python 混合架构说明、独立 Git 实验日志系统说明 |
| [DATA.md](DATA.md) | 29 张精度评测图（24 张 Kodak 真彩 + 5 张极限合成图）、100 张吞吐量测试图及 6 组四级 LUT 仿真管线设计 |
| [ROUTES.md](ROUTES.md) | 朴素 / 经典 / 现代 / 前沿共 **20 条具体算法路线**（含 Lagrange、B-Spline、多项式、Tucker 低秩、RBF、MLP、SIREN）原理与全维度评估 |
| [EVALUATION.md](EVALUATION.md) | 完整实验数据汇总表、C++ 吞吐量基准测试结果、版本迭代历史与 Commit 可回溯记录 |
| [AUDIT.md](AUDIT.md) | 当前分支的代码、文档、日志核查结果和待办优先级 |
| [experiments/r16-five-directions.md](experiments/r16-five-directions.md) | 精度门禁、候选筛选、尾部拟合、复现流程、Zig 参数实验的完整报告 |

---

## 快速上手（One-Click Setup）

```bash
# 1. 一键安装 Zig、GCC 16/C++26、Rust、CMake/Ninja、Python 3.12 及科学计算/PyTorch 依赖
pixi install -a

# 2. 编译并运行 C++ 与 Python 测试；默认推理内核为 tetra_zig_simd
pixi run test

# 3. 生成完整测试数据集与 6 大四级 LUT 场景
pixi run gen-data

# 4. 运行全套技术路线大横评与 C++ 100 张图像吞吐量基准
pixi run -e ml python -m lutlab.routes

# 5. 查看独立 Git 日志仓库中的实验记录
pixi run logs

# 6. 官方阈值公布后，一条命令完成数据准备、构建、测试、完整精度门禁与 100 图筛选
pixi run competition-check --scenario isp-0 --threshold <官方阈值> --threads 20
```

赛题尚未说明阈值作用于每张图的均值、p99 还是最大像素；使用
`--metric mean|p99|max` 明确指定口径。本地示例 `2.0` 仅供实验，不代表官方验收。
`pixi run verify-data` 可核验输入哈希；`pixi run zig-perf` 可复跑可移植性能扫描。
