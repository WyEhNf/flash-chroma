# R19：统一入口、严格性能比较和题面规格验收

日期：2026-10-15。本轮源码、文档和小型验收归档随当前提交交付。完整生成数据与本机运行包由最终manifest追踪。

后续[R20正确性审计](r20-correctness-audit.md)补齐了验证器的实际图片执行路径，复核本页六组统计不变，并新增了裁剪场景的容量比较。本页及其归档保留为冻结阶段证据。

[R25精确全色域拟合](r25-full-domain-fitting.md)记录后续原生离线库、新模型的质量/容量验收和当前100图CPU/CUDA比较；其输入模型和批次不同，不能与本页时间直接组成加速比。

统一入口已经接通；六组模型完成实际 CPU/CUDA 全色域及 100 图验收。独立七对确认中，本轮已测的最快 CPU 配置为 **0.8102 ms/图**，GPU 完整普通主机内存到普通主机内存为 **0.6065 ms/图**，配对加速比中位 **1.291×**。这些是本机固定模拟输入的稳态结果，不是官方成绩。

## 一个入口执行完整流程

从仓库根目录使用 `python -m lutlab`。入口包括 `fit`、`apply`、`cube`、`verify`、`bench-models`、`validate`、`accept`、`compare`、`select` 和 `check`；每个子命令都有 `--help`。普通 CPU/CUDA 应用接口本身只需 Python 标准库及对应本地程序；拟合、质量统计及可选 OCIO 对照另需相应依赖。

本轮已验收的实际程序为 `build-r18-cpu/jshc.exe` 和 `build-gpu/jshc_gpu.exe`。在当前工作区指定它们：

```powershell
$env:PYTHONPATH = 'python;artifacts/r18-tools/python'
$env:JSHC_BIN = (Resolve-Path build-r18-cpu/jshc.exe).Path
$env:JSHC_CUDA_BIN = (Resolve-Path build-gpu/jshc_gpu.exe).Path
python -m lutlab info --backend cpu
python -m lutlab info --backend cuda
```

正式四张输入表可直接传给拟合入口，无须采用预置场景目录。当前适配格式为每表 `256³×3` 字节、B 轴最快的原始 RGB8；四个实参顺序即映射顺序：

```powershell
python -m lutlab fit --inputs lut1.lut256 lut2.lut256 lut3.lut256 lut4.lut256 `
  --model-dir models/my-transform --m 18 --method ls_tetra_jitter --grid dp
```

输出是带 manifest 的完整四阶段不可变批次。缓存身份绑定四个输入的字节、源码、求解器版本及实际参数，包括 DP、分层取样、CG 和整数精化控制；输入文件位置不影响缓存身份。`dp_guarded` 可显式选择，因最终四级误差没有稳定改善而未强推。

本轮交付的模型清单已经保存，可直接执行以下实际示例：

```powershell
$suite = Get-Content artifacts/r19-delivery/acceptance-suite.json -Raw | ConvertFrom-Json
$case = $suite.cases | Where-Object { $_.scenario -eq 'isp-0' -and $_.m -eq 18 }
$models = $case.models
python -m lutlab verify --models @models --images artifacts/r17-acceptance/bench.txt `
  --backend cpu --kernel tetra_avx2_scalar_gather --threads 16 --batch
python -m lutlab bench-models --models @models --images artifacts/r17-acceptance/bench.txt `
  --backend cuda --batch --reps 5
```

`apply --input ... --output ...` 和 `validate --reference ... --images ... --threshold ...` 同样使用 `--backend cpu|cuda`。GPU 通过公共 Python 适配器调用可选 CUDA 程序；选择 CUDA 后失败会报错。CPU 的 C++17 构建保持独立，部署和 GPU 构建命令见 [CPU 要求核对](r18-requirements.md) 与 [GPU 说明](r18-gpu.md)。

## 严格性能协议与结果

固定真实机器：Windows 11，Ryzen 9 8945HX（16 核/32 线程）和 RTX 5070 Laptop（CC12.0，约8 GiB）；CPU 为 MinGW GCC15.2，GPU 为 MSVC14.44/CUDA13.2。CPUID、OSXSAVE、XCR0 与实际 GPU 执行均已确认。不能将该机器等同于题面举例的 i7-14700。

固定四级独立 ISP m18 DP+jitter 模型、100 张 1024×768 RGB8 合成帧及所有文件 SHA。计时前，对六种 CPU 配置和两种 GPU 配置分别导出全部100图输出，执行长度、SHA256和实际逐字节比较，全部一致。校验、写盘和 hash 与计时分离。

八项预定比较各七对，AB/BA 交替，每轮打乱比较顺序；每次执行完整100图，不采用逐图最佳值拼成绩。OpenMP 动态团队关闭、固定4096像素块；由 OS 调度线程，不声称做了核心绑定。保留所有原始时间、命令、输入/模型/程序哈希，以及可选宿主进程观测。随后独立再做七对，确认已测最快 CPU 配置与 GPU 的直接差距。

| 比较 | 参考中位 ms/100图 | 候选中位 ms/100图 | 配对加速比中位 | bootstrap 95%区间 | 候选更快 |
|---|---:|---:|---:|---|---:|
| 标量4线程 → AVX2逐图4线程 | 674.283 | 258.528 | 2.630× | 2.580–2.641 | 7/7 |
| AVX2逐图1线程 → 4线程 | 825.391 | 257.498 | 3.249× | 3.107–3.310 | 7/7 |
| AVX2逐图4线程 → 整批4线程 | 255.091 | 231.032 | 1.094× | 1.089–1.127 | 7/7 |
| AVX2整批4线程 → 标量gather整批4线程 | 228.676 | 220.847 | 1.033× | 1.024–1.042 | 6/7 |
| 标量gather整批4线程 → 16线程 | 225.562 | 79.709 | 2.774× | 2.701–2.920 | 7/7 |
| AVX2整批4线程 → CUDA整批 | 227.944 | 61.388 | 3.709× | 3.599–3.855 | 7/7 |
| CUDA逐图提交 → 整批提交 | 70.159 | 60.731 | 1.144× | 1.115–1.182 | 7/7 |
| OCIO适配路径4 worker → AVX2逐图4线程 | 1297.657 | 259.916 | 4.988× | 4.873–5.272 | 7/7 |
| 独立确认：标量gather整批16线程 → CUDA整批 | **81.020** | **60.648** | **1.291×** | **1.257–1.312** | **7/7** |

每行使用本行配对中的中位数；“配对比值的中位数”不要求等于“两组中位数之比”。区间来自固定种子的一万次配对比值重采样，只表示本机这批样本的不确定性，未做跨输入、跨机器或多重比较保证。标量gather的3.3%增益有一次反向，单侧符号检验p=0.0625；默认 `auto` 仍为原AVX2，不据此做通用CPU结论。

CPU主计时包括普通主机输入复制和四级映射。GPU主计时包括普通主机输入→固定内存复制、H2D、四级映射、D2H/同步及普通主机输出复制。两者均不含分配、拟合、模型加载、解码和输出编码。GPU另有 pinned-transfer 和 resident 指标，均不用于上表主机到主机加速比。此前37.393ms/100图的GPU数据属于较窄的 pinned-transfer 范围；本表已补足普通主机复制。

内存也有真实成本：CPU逐图路径观测峰值工作集约245MB，整批路径约479MB；GPU基准宿主进程约1.077GB。GPU基准显式分配的图像设备缓冲可达900MiB，包含同时保留的transfer/resident两套；这不是必要的最小部署内存，也不是进程峰值显存。m18四表节点69,984B、CPU运行时模型约204,736B、GPU设备模型117,888B。进程峰值与模型载荷分别报告。

业界基线采用实际 [OpenColorIO 2.6](https://opencolorio.readthedocs.io/en/v2.6.0/releases/ocio_2_6.html)，每级均为UINT8输入/输出，使用Q16轴坐标构造shaper并调用四面体插值。非均匀网格下，它的float32结果有60,011/16,777,216个颜色与Q16不同；相对完整真值的平均ΔE为0.975464，本实现为0.975933，p99和max相同。上表比较的是明确的Python buffer适配路径，包含线程任务成本，不能据此声称超过OCIO所有部署方式或获得全行业SOTA。算法与近期论文的任务差异、AdaInt/Sort-Select-Damp等一手来源见 [算法说明](r18-algorithm.md)；NPP仍只有调研证据。

## 题目规格验收

一次固定验收覆盖3组模拟场景×m17/m18。每组从公共fit入口生成模型，逐字节核对冻结研究模型；核验四个完整LUT的SHA各异，并对全部16,777,216颜色确认真值确是原四表的精确串联。再验证模型manifest绑定来源、m范围和整数语义，实际运行CPU/CUDA全色映射及100图。

| 场景 | m | 全色mean ΔE | 全色p99 | 全色max | 100图中最差单图mean | 示例mean<2门禁 |
|---|---:|---:|---:|---:|---:|---|
| isp-0 | 17 | 1.059107 | 3.316625 | 12.083046 | 1.452216 | 通过 |
| isp-0 | 18 | 0.975933 | 3.162278 | 14.142136 | 1.299161 | 通过 |
| clip-7 | 17 | 1.483448 | 6.082763 | 34.000000 | **2.230224** | **失败** |
| clip-7 | 18 | 1.408871 | 6.000000 | 26.000000 | 1.826548 | 通过 |
| warp-7 | 17 | 1.485228 | 4.123106 | 11.789826 | 1.543941 | 通过 |
| warp-7 | 18 | 1.426867 | 3.741657 | 9.695360 | 1.528122 | 通过 |

六组CPU/CUDA全色输出SHA完全相同，结构和来源契约全部通过。示例门禁是“100张图各自mean<2且全色mean<2”，5/6通过；所有组都不满足全色max<2。报告同时保存mean/p99/max的门禁诊断，未把示例均值通过改称逐像素通过。

clip-7/m17在先前5图测试中通过，100图扩展后失败；其全色max也从旧模型29恶化到34。因此不能仅按平均误差选择该模型。ISP m18相对旧同尺寸模型的全色平均误差下降24.54%；扩大m并不保证max更小，表中ISP m17的max也优于m18。

阶段检查：当前CPU内核测试程序SHA与已通过的完整CTest完全一致，继续复用6.37秒的全色oracle验收；新增CPU verify经过八配置100图逐字节预检。11项Python检查全部通过（9.93秒，含实际CUDA集成）；全部加速项关闭的C++17构建完整CTest通过（3.62秒）。公共 `python -m lutlab apply` 对标准图CPU/CUDA像素一致。

## 证据和复现

仓库内可直接查看[精度摘要CSV](../report/data/r19/accuracy-summary.csv)、[配对性能摘要CSV](../report/data/r19/paired-summary.csv)和[验收归档索引](../report/data/r19/README.md)。索引链接的压缩包保留R17–R19原始JSON、日志、整数模型和源码快照；下列`artifacts/`链接指向原始本机布局，可从归档中恢复相应记录。约1.48GB的完整生成资产继续由manifest和复现脚本追溯。

- [六组验收清单](../artifacts/r19-delivery/acceptance-suite.json)：链接每组完整来源、100张逐图结果、全色热点、各口径门禁与CPU/CUDA哈希。
- [严格配对原始记录](../artifacts/r19-delivery/paired/comparison.json) 与 [最快已测CPU/GPU独立确认](../artifacts/r19-delivery/paired/best-cpu-gpu-confirmation.json)。
- [公共入口单图验收](../artifacts/r19-delivery/public-command-check.json)、[Python检查](../artifacts/r19-delivery/pytest.log)、[便携构建](../artifacts/r18-portable/acceptance.json)。
- [CPU本地部署包](../artifacts/r19-delivery/runtime-cpu/)：EXE及四个运行DLL合计3,282,321B；隔离PATH后100图输出与参考逐字节一致，[依赖和部署证据](../artifacts/r19-delivery/deployment.json)保留来源及SHA。
- [最终源码及资产manifest](../artifacts/r19-delivery/delivery-manifest.json)。生成的大型LUT和图像资产需随manifest另行保留；源码zip不重复装入这些数据。

完整阶段命令保存在报告JSON，核心复现如下；无需每次改动后重跑整个批次：

```powershell
python scripts/r19_delivery_acceptance.py --cpu build-r18-cpu/jshc.exe --cuda build-gpu/jshc_gpu.exe
python -m lutlab compare --models @models --images artifacts/r17-acceptance/bench.txt `
  --reference artifacts/r17-algorithm/isp-0/composite.lut256 `
  --cpu-executable build-r18-cpu/jshc.exe --cuda-executable build-gpu/jshc_gpu.exe `
  --output artifacts/r19-delivery/paired --pairs 7
python scripts/r19_confirm_best_cpu_gpu.py
```

本轮严格测试已停止追加扫描。官方Threshold、统计粒度、正式输入容器/位宽、最终硬件和计时边界仍未提供，因此官方精度硬门槛及正式分数尚不能判定；本地合成测试低于题面举例的1.5秒/图也不表示获得速度满分。
