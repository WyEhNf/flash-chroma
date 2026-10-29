# 赛事框架现场操作指南

交付工程位于 `F:\Hackathon\极速焕彩测试框架\FlashChroma`，由安装脚本新建。用户原有 `C`、`C++` 和 `data` 保留不变。核心交付是 `flash_chroma_framework.hpp` 与调用它的 `main.cpp`；该头文件已经合并运行库、框架适配、严格读取和拟合实现。编译、运行这份工程不需要 Python。仓库中的 Python 脚本用于安装、重复测量和独立核验。

## 一条命令运行

在 PowerShell 中执行：

```powershell
& 'F:\Hackathon\极速焕彩测试框架\FlashChroma\run.ps1'
```

默认配置为四级 `m=33`、`Mode=auto`、后端自动选择、均匀取整网格、`Fit=sample`、四张原样图。脚本先编译，编译失败不会运行旧程序。指定编译器时可设置 `$env:FLASH_CHROMA_CXX = 'E:\mingw64\bin\g++.exe'`，也可使用 PATH 中的 `g++`。当前本机验证使用 GCC 15.2；交付构建参数包含 `-O3 -std=c++17 -static -DFLASH_CHROMA_ENABLE_OPENMP=0`。赛方指定的 GCC 13.2 下载失败，尚未完成该工具链验证；本机 15.2 的结果不能代替它。

只编译用 `-BuildOnly`。更换数据目录用 `-Data '你的data目录'`；该目录需包含 `LUT/Test1.3DL` 至 `Test4.3DL`，以及 `image/1.bin` 至请求的末张图片。每张图片必须是 **1024×768、连续 RGB8、恰 2,359,296 字节**，不能将 PNG/JPEG 改名成 bin。

```powershell
Set-Location 'F:\Hackathon\极速焕彩测试框架\FlashChroma'
.\run.ps1 -GridSizes 33 -Mode sparse -Backend auto -Fit sample
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Backend auto -Fit sample
.\run.ps1 -GridSizes '17,25,33,33' -Mode sparse -Fit sample
.\run.ps1 -Data '..\data' -GridSizes 33 -Mode direct_rgb24 -Fit chain_ls -Count 4
```

`-Count 100` 要求完整的 `image/1.bin` 至 `100.bin`，不会把四张样图重复当成一百张。数据来自已存在目录，安装和运行不修改原 LUT 或图片。

如需直接编译，在交付目录使用：

```powershell
g++ -O3 -DNDEBUG -std=c++17 -static -DFLASH_CHROMA_ENABLE_OPENMP=0 main.cpp -o main_flash_chroma.exe
.\main_flash_chroma.exe '..\data' 33 sparse auto uniform 4 sample
```

直接调用的位置参数依次为 `data、m或四个m、mode、backend、grid、图片数、fit`。其他机器编译时，`Backend=auto` 会检查可用指令集；显式 `avx2` 在不支持的机器上会拒绝。

## 先选精度模型，再选执行表示

四级 `m` 均允许 17..33，可逐级不同；`uniform` 与 `framework` 是两种不同节点坐标，不能仅因 m 相同就认为模型相同。默认 `uniform` 按均匀坐标取整，`framework` 保留原框架的步长构造，方便比较。

三种 `Fit` 均只使用 LUT 和算法枚举的完整 RGB 域。图片、图片直方图、图片特征和最终评测误差均不参与拟合。

| Fit | 行为 | 现场用法 |
|---|---|---|
| `sample` | 在指定网格采样源 LUT；默认基线 | 先确认数据、精度与运行链路 |
| `independent_ls` | 每一级独立优化 m³ 节点，使用完整域最小二乘及整数误差核验 | 与 sample 对比四级组合后的真实精度，不能只看单级改善 |
| `chain_ls` | 固定前三层采样模型，以原四级链的完整域输出为目标优化第四层 | 对比最终四级误差与准备耗时 |

拟合输出中的 `candidate_used` 表示完整域验收后是否采用候选；未满足保护条件时保留原节点。保护条件检查所用完整域的均值和平方误差，不承诺每张照片或最大像素误差都改善。预处理不计入框架映射计时，但会延长程序启动；比较时仍应记录它。

| Mode | 执行与资源取舍 |
|---|---|
| `auto` | 全量证明四级均可按通道分离时走精确曲线；否则使用稀疏四面体。它不会自动搜索最快表示 |
| `sparse` | 显式关闭结构捷径，逐级执行稀疏模型；m33 AVX2 的当前样例运行时自有内存约 1 MiB |
| `direct_rgb24` | 只根据模型预生成完整颜色映射，加快逐像素执行；m33 AVX2 当前样例自有内存约 49 MiB |
| `direct_u8` / `direct_u16` | 用有限容量调色板；完整色域输出颜色超过容量时明确拒绝，不能静默截断 |

上表内存为模型、arena 和对象之和，不是整个赛事进程的 RSS。原框架还保留密集参考表、输入输出图片和节点副本；LS 预处理另有临时内存。`sidecar_bytes` 是对象内子集，不能重复相加。算法固定单线程，构建关闭 OpenMP，不使用 GPU/NPU。进程可能存在系统或运行库辅助线程，总线程数不能单独代表算法是否并行。

桌面速度候选优先比较 `m33 + direct_rgb24`；内存较紧时比较 `m33 + sparse`，再按实际阈值试其他 m。当前第二轮原四图受控矩阵已验证，同一 m33 模型的 sparse/DirectRGB24 输出逐字节一致；该矩阵先生成参考再计候选，和原框架每张图后计算参考的缓存历史不同，最终选择应再执行下面的原程序复核。这里不把某个模式写成对未知 LUT 的无条件最优或官方最优分。

## 直接复核最终交付程序

以下命令在项目仓库 `F:\Hackathon\worktrees\p16-frontier-header-20261027` 内执行。需要 Python 3.11+ 和 psutil；独立像素核验另需 NumPy。先通过交付目录的 `run.ps1 -BuildOnly` 编译，随后固定输入和源文件，测试期间不重新编译。

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
python scripts/check_framework_delivery.py `
  --exe 'F:\Hackathon\极速焕彩测试框架\FlashChroma\main_flash_chroma.exe' `
  --data 'F:\Hackathon\极速焕彩测试框架\data' `
  --output "artifacts/delivery-check-$stamp" --count 4 --reps 5 --affinity 16 `
  --config sparse33,33,sparse,avx2,uniform,sample `
  --config direct33,33,direct_rgb24,avx2,uniform,sample `
  --config chain33,33,direct_rgb24,avx2,uniform,chain_ls
```

每轮配置顺序按固定种子随机排列，每次使用独立进程。脚本保留原始 stdout/stderr，要求每次退出 0、图片数量与顺序完整、计时/误差有限、同一配置各图的误差跨重复一致。结果位于 `summary.json`；性能比较使用原程序 `TimeCost` 之和的批次中位数及范围，`child_wall_ms` 含 LUT 读取与准备，不能当作映射耗时。

CPU 16 是本机示例，其他机器需选择实际可用逻辑 CPU。脚本在启动后立即绑核，并每 0.1 秒记录各 TID 的累计 CPU 最大值、线程数和 RSS。报告区分“曾观测多少线程”和“额外线程是否累计过 CPU 时间”，不据此猜测线程来源。此流程没有 A/A 预检，不能将重复成功写成 A/A 稳定性证明。所有 exe/main/hpp/run.ps1、LUT 和图输入都做前后 SHA 核验，源变化即拒绝成功。

## 需要全面比较时使用受控矩阵

以下使用每次唯一的新目录；脚本拒绝覆盖旧证据。只在空闲机器上串行跑性能，不同时启动另一个 benchmark、拟合或大规模验证任务。源码变动后必须重建 runner，旧构建会因来源不匹配而拒绝运行。

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$build = "artifacts/framework-build-$stamp"
$cache = "artifacts/framework-cache-$stamp"
$matrix = "artifacts/framework-matrix-$stamp"
$oracle = "artifacts/framework-oracle-$stamp"
python scripts/benchmark_framework.py build --compiler 'E:\mingw64\bin\g++.exe' --output $build
python scripts/benchmark_framework.py cache --exe "$build/framework_benchmark.exe" `
  --framework 'F:\Hackathon\极速焕彩测试框架' --output $cache
python scripts/benchmark_framework.py run --exe "$build/framework_benchmark.exe" `
  --cache "$cache/manifest.json" --images artifacts/framework-sample-images-20261029.txt `
  --output $matrix --matrix extended --affinity 16 --warmup 5 --aa-reps 15 --reps 9 --write-outputs
```

`images` 文件每行一个 bin 路径，相对路径以列表目录为基准。上面的现有列表指向原四图；换数据时需新建列表。四张原图和自有一百图要分别报告，自有图不会因数量达到 100 就成为官方测试集。

矩阵先做 A/A；失败返回 3 并保留质量、原始样本，不进入候选计时。`summary.json` 的 `observed_frontier` 是本机、当前样图、候选集合中观察到的精度/速度/内存前沿，不是对所有参数的全局最优证明。结构开关候选如果实际均 `structured=false`，同后端的细小耗时差不能宣传为结构优化收益。

`--candidate` 可重复指定，覆盖默认矩阵。字段为 `id,m1,m2,m3,m4,grid,structure,backend,representation,block,budget[,fit]`；backend 的 0/1/2 是 Auto/Scalar/AVX2，representation 的 0/1/2/3 是 Sparse/DirectU8/DirectU16/DirectRGB24。例如：

```text
sample33,33,33,33,33,uniform,0,2,3,65536,134217728,sample
chain33,33,33,33,33,uniform,0,2,3,65536,134217728,chain_ls
```

精度阈值公布后，在 `run` 命令增加 `--threshold <赛方数值>`。当前脚本按“每图平均 RGB 欧氏距离严格小于阈值”判断，官方若规定其他边界或聚合规则，需要先对齐规则。没有阈值时合格状态为空，不输出官方通过/满分结论。不要把 RGB 欧氏距离称为 CIEDE2000。

最后使用独立文本 oracle 核验落盘输出；这一步不计性能：

```powershell
python scripts/framework_contract_check.py prepare `
  --framework 'F:\Hackathon\极速焕彩测试框架' --output $oracle
python scripts/framework_contract_check.py verify --oracle "$oracle/manifest.json" `
  --candidate-dir "$matrix/native/outputs/m33-direct-rgb24-2" `
  --output "artifacts/framework-verify-$stamp.json"
```

使用自定义候选时将目录末尾换成对应 id；已提供阈值时 `verify` 同样追加 `--threshold`。更换原 3DL 后要重新创建缓存和 oracle，不能继续使用旧数据的身份凭证。输出文件保留全部像素并进行哈希；独立核验成功只证明当前输入的语义与精度，不代替原框架计时或赛方最终评分。
