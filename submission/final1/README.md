# final1：精度与映射速度的历史折中版本

本目录只需一个 `main.cpp`，原头文件已原样内嵌，无自定义 hpp 依赖。四级 33³ FrameworkStep，chain_ls 末级拟合后执行 prefix_nodes 前中层整数节点优化，使用 DirectRGB24 与自动 AVX2 pair32 分派。每次启动从四张输入 LUT 生成模型，运行器单线程。

```sh
cd submission/final1
g++ -O2 -std=c++17 -o lut3d main.cpp
./lut3d data 4
```

数据目录应包含 `LUT/Test1.3DL` 至 `Test4.3DL` 和 `image/1.bin` 至 `4.bin`。第二参数可选 1..100；省略参数时默认 `data` 和四图。图片、原始大 LUT 和编译后二进制不入库。

共享服务器测速使用现有调度器，锁住一个物理 P 核并绑定其逻辑 CPU：

```sh
cd ~/workspace/zmx/final1
python3 ../run_on_pcore.py -- ./lut3d data100 100
```

调度器不是 C++ 运行依赖，也可用对应 `~/locks/N.lock` 的 `flock` 与 `taskset`。不要绕过公共锁直接进行性能比较。

已验证服务器 i9-14900K / Ubuntu 24.04 / GCC 13.3 / `-O2 -std=c++17`：完整 RGB8 域平均欧氏误差 **0.679296814**；100 张照片的逐图 mean 平均值 **1.481250064**；五轮百图 TimeCost 均值的中位数 **0.975453 ms/图**（范围 0.950348–0.987877）。`out=img` 复制计入 TimeCost；读图、参考映射、色差和约 21.17 秒拟合/搜索/Direct 准备在外。误差不是 CIEDE2000，照片集不是独立留出集，不宣称未知数据上的最优。

最新单文件等价性、分段用时及相对原框架的逐函数变更见[单文件报告](../../docs/stages/2026-10-30-final1-single.md)。上述五轮耗时为相同算法的原两文件版本实测，新的分段诊断单列，不能混成同一场次。完整历史选择依据见[原阶段报告](../../docs/stages/2026-10-30-final1.md)及[原始证据](../../report/data/final1-20261030)。重建检查：在仓库根目录运行 `python scripts/package_final1.py`。目前尚未完成正式评分规则、额外 Direct 缓存许可和规定 MinGW 13.2 的验收。
