# R15 — Zig 默认内核与 Pixi 多语言工具链

## 版本边界

- 基线：`969d046`（`archive/r14-multi-lang-simd`，同时也是当前 `main` 的原始指针）。
- 开发分支：`codex/zig-default-pixi`；Rust 依赖和本次变更只提交到该分支。
- 配置提交：`408a842`。

## 改动

1. Pixi 默认和 `ml` 环境锁定 Zig 0.17、Rust 1.99；Linux 锁定 GCC/G++ 16.2，以编译 C++26 `<simd>`。Rust `portable_simd` 的 `RUSTC_BOOTSTRAP=1` 只用于 Rust 对象文件构建命令。
2. CMake 分别生成 C++26、Zig 和 Rust 对象文件，链接到同一个 C++17 驱动。移除了强制 `x86-64`、`native` 目标选项和架构相关编译标志。
3. `jshc` CLI、Python benchmark API、Python CLI 和路线脚本的主 benchmark 默认选择 `tetra_zig_simd`。历史 `tetra_avx2` / `tetra_asm` 参数仍解析为 C++ SIMD 兼容别名。
4. 路线脚本的吞吐量循环纳入 C++26、Zig、Rust 三种实现以便同条件对照。

## 验证（Arch Linux WSL，Pixi linux-64）

- `pixi install -a --locked`：成功安装 `default` 与 `ml` 环境。
- `pixi run test`：C++ `kernels` 测试通过（覆盖 2^24 RGB 立方体、三种 SIMD 与标量逐字节一致性、尾部与级联）；Python 3 项测试通过。
- 不传 `-k` 的 `jshc bench` 单图单级 smoke test 返回 `kernel: tetra_zig_simd`；显式 `-k tetra_zig_simd` 同样返回该内核。详见独立日志仓库 `logs/` 中的 `zig-default-smoke` 运行记录。

这次单图运行仅验证默认路径，不作为稳定的吞吐量结论。历史性能数字属于先前版本。macOS 工具链未在本机验证。
