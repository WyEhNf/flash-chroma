# 有界精确后缀缓存的原始证据

同一冻结模型逐字节一致；Windows/AMD本机1/4线程映射耗时分别下降52.3631%/52.2767%，预设本机门槛通过。额外准备容量742544字节，准备成本另列；Skylake实机与官方对派生缓存的许可仍未取得，不修改默认。

目的、测试环境、方法、误差口径及边界见[阶段说明](../../../docs/stages/2026-10-20-skylake-suffix-cache.md)。本目录保存原有55组合同、新55组缓存合同、实际171056合法缓存槽的独立u64核验、单级/四级完整256³、100图输出身份、四进程80轮次、两Windows主库/依赖/核心、汇编及源码快照与门槛复算。Linux另有同源码构建、标准库528个有限后端/偏移比较和12组完整256³回执；同AMD主机，不是Skylake。

复现时取本阶段提交，并从`*-measured-source.zip`恢复测量时的原始字节，用新的输出目录运行。源码SHA也包含换行符，跨系统checkout的换行转换不能直接冒充相同字节；源码ZIP保留实测字节。归档的绝对路径需按本机实际位置重新构建并绑定build/contract/full的SHA，不能沿用另一环境的构建身份。模型复用PR42的`report/data/cinema-current-anchor-accept-v1/models.zip`，输入SHA与相对位置见`plan.json`。

Windows入口顺序：

```powershell
python scripts/build_skylake_runtime.py --plan experiments/skylake-suffix-cache-v1.json --output artifacts/skylake-suffix-cache-build-v1 --cmake "C:/Program Files (x86)/CMake/bin/cmake.exe" --compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator "MinGW Makefiles"
python scripts/verify_skylake_packed.py --plan experiments/skylake-suffix-cache-v1.json --build artifacts/skylake-suffix-cache-build-v1 --output artifacts/skylake-suffix-cache-contract-v1
python scripts/verify_skylake_suffix_cache.py --plan experiments/skylake-suffix-cache-v1.json --build artifacts/skylake-suffix-cache-build-v1 --contract artifacts/skylake-suffix-cache-contract-v1/results.json --output artifacts/skylake-suffix-cache-cache-contract-v1
python scripts/accept_skylake_runtime.py --plan experiments/skylake-suffix-cache-v1.json --build artifacts/skylake-suffix-cache-build-v1 --contract artifacts/skylake-suffix-cache-contract-v1/results.json --cache-contract artifacts/skylake-suffix-cache-cache-contract-v1/results.json --output artifacts/skylake-suffix-cache-full-v1
python scripts/bench_skylake_runtime.py --policy experiments/skylake-suffix-cache-perf-v1.json --output artifacts/skylake-suffix-cache-perf-v1
```

性能策略须在完整验收后、计时前绑定本地build/full/topology身份；不得在计时后改变阈值、范围或顺序。四进程分别预热所有输出，创建成本加首个测量轮的结果仍是预热后的比较。测量环境细节以`*-run.json`与`performance-worker*.json`为准。

Linux入口仅需Python标准库、CMake、G++、OpenMP。构建命令见`linux-build-build.json`；验证命令为：

```sh
python3 scripts/verify_skylake_linux_stdlib.py --plan experiments/skylake-suffix-cache-v1.json --build artifacts/skylake-suffix-cache-linux-build-v1 --single-oracle-stream artifacts/skylake-suffix-cache-full-v1/first-stage.rgb --output artifacts/skylake-suffix-cache-linux-verify-v1
```

单级oracle流由上面的Windows完整验收产生，其SHA必须匹配既有独立uint64验收；约50MB像素流未提交。Linux入口不重新计算独立oracle、不测试照片性能。

`manifest.json`核对本目录原字节与SHA。两平台二进制分别打包；汇编为静态证据，不能作为Skylake周期数。全部输出保持既有RGB欧氏误差，未执行新拟合或改变精度选型。
