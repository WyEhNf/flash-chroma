# final1 冻结源码与复现

这里保存生成算法时实际读取的十个模块、上一交付入口 `base_main.cpp`、最初框架 `original_main.cpp`，以及实际执行的 `verify_and_benchmark.cpp` 原件。保留原字节用于复核；历史源码中的原注释不作事后改写。维护源可以含 hpp，最终交付仅 `submission/final1/main.cpp`。

- `common/framework`：历史精度迁移分支的拟合、几何、搜索与适配模块。
- `common/include/flash_chroma.hpp`：最新运行库，包括 DirectRGB24 pair32。
- `prefix_joint/candidate.hpp`：已验证的 prefix_nodes 研究候选。
- `final_pipeline.hpp`：将末级 chain_ls、前中层优化和运行库串联的交付入口。
- `base_main.cpp`：生成时的上一版入口，仅作为来源，正式入口在 `submission/final1`。

仓库根目录运行 `python scripts/package_final1.py`，会在内存重建并逐字节比较单文件交付；`--output 新目录` 可导出一份仅含 main.cpp 的新包。内部 `generate_legacy()` 用于追溯原两文件哈希。脚本只依赖 Python 标准库，最终运行不依赖 Python。

`stage_timing.cpp` 是额外诊断入口：包含正式 main 后调用相同函数，单独计量读取、参考表、采样、拟合、节点搜索、Direct 构建和百图各阶段。正式 main 不插入这些计时语句。Linux 的 `run_single_validation.py` 在公共 P 核锁内编译、比较新旧预处理字节、检查输入 SHA，并运行分段诊断及正式四图；脚本保留服务器实验目录约定，见新阶段报告。

在 Linux 仓库根目录编译原验收器：

```sh
g++ -O2 -std=c++17 -I submission experiments/final1/verify_and_benchmark.cpp -o verify_and_benchmark
```

验收命令为 `./verify_and_benchmark DATA EXPECTED BANK NEW_RESULTS`。DATA 下需有原四张 `LUT`、`official4` 和 `photos100`；EXPECTED 需有冻结 prefix_nodes 的四份 `.slut` / `.fractions` 及 `domain.rgb`；BANK 需有 `chain33`、`prefix_nodes`、`geometry_output`、`history` 四套冻结模型。NEW_RESULTS 必须不存在。输入身份见[原验证回执](../../report/data/final1-20261030/evidence/validation-receipt.json)。这些大输入和模型库留在服务器原测试目录，未复制入 Git，孤立克隆不能直接重跑数值测试。

本次测试的服务器原目录：`~/workspace/zmx/final1-selection-20261030`。DATA 为 `~/workspace/zmx/p16-framework-bench-20261030-1200/data`；EXPECTED 为 `~/workspace/zmx/precision-attempts-20261030-0753/results/prefix_nodes`；BANK 为原目录的 `bank`。从服务器原目录使用公共 `run_on_pcore.py` 调度并提供一个新的结果目录即可复现。历史调度脚本原件在报告的 `original-reproduction` 中，含当时的绝对路径，仅作审计归档。

验收器先重新拟合并比对四级模型，再全 16,777,216 色对照历史输出和原框架参考，验证 104 张图片，执行五轮百图实际 apply，最后执行固定表地址 ABBA 与 A/A 控制。后一个控制绕过运行器检查，仅隔离模型与地址影响，不能冒充正式 TimeCost。
