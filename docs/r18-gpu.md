# R18 CUDA 后端与统一运行接口

本后端真实运行于本机 NVIDIA GeForce RTX 5070 Laptop GPU（计算能力 12.0、36 SM、约 8 GiB 显存）。已确认驱动 582.05，CUDA Driver API 版本 13.0，Toolkit/Runtime 13.2，Visual Studio 2022 的 MSVC 14.44。它是独立 CUDA 可执行程序，由公共 Python 运行适配器调用；CPU 程序无需混合链接 MSVC 和 GCC 产物。

这里的硬件和性能证据只覆盖本机。官方测试数据、阈值和最终计时边界仍未提供；后端逐字节一致不等于已通过官方精度门槛。

## 构建与部署

Windows 上实际验收的构建入口：

```powershell
./gpu/build-windows.ps1
```

默认生成 `build-gpu/jshc_gpu.exe`。脚本通过 `vswhere` 找到 x64 MSVC 工具链，再调用 CUDA Toolkit 的 `nvcc`；`cl` 无需预先进入 PATH。`-Architecture 120` 默认生成本机 `sm_120` 原生 cubin，不要求较旧驱动 JIT Toolkit 13.2 的新版 PTX。部署到其他计算能力的设备时，应使用相应架构重新构建和验收。脚本保存 `command.txt`、`build.log`、`nvcc-version.txt` 及包含源码、编译命令和二进制 SHA256 的 `build-manifest.json`。

`gpu/CMakeLists.txt` 是独立 CMake 入口，根 CPU CMake 不依赖 CUDA。该入口已提供，但本阶段实际构建证据来自上面的 Windows 脚本。

公共接口为 `python/lutlab/runtime.py`：

```python
from lutlab import runtime

models = [f"models/stage{k}.slut" for k in range(1, 5)]
print(runtime.capabilities("cuda"))
runtime.apply(models, "input.png", "output.png", backend="cuda", competition=True)
runtime.cube(models, "all-colors.raw", backend="cuda", competition=True)
runtime.verify(models, "bench.txt", backend="cuda", batch=100,
               competition=True, output="outputs.raw")
result = runtime.bench(models, "bench.txt", backend="cuda", batch=100,
                       reps=5, competition=True)
```

`backend="cpu"` 使用 `JSHC_BIN` 或 `build/jshc[.exe]`；`backend="cuda"` 使用 `JSHC_CUDA_BIN` 或 `build-gpu/jshc_gpu[.exe]`。所有方法也接受显式 `executable=`。选中的后端缺失时会报错，不会悄悄换用另一后端。`capabilities` 查询实际二进制和设备，而不根据 PATH 或 CUDA 安装目录推测可用性。

CPU 参数为 `kernel`、`threads`。CUDA 支持 `kernel="auto"` 或 `"cuda_q16_fused4"`，`device=0`、`block=256`；非零 `threads` 会被拒绝。`batch=False/1` 表示逐图提交，`batch=True/100` 表示整组提交；CUDA 还可显式指定 1 到 100 的组大小。输出继续保留后端原始字段，并附带实际命令、stdout/stderr、二进制和模型哈希以及整个子进程的 wall time。

## 整数语义与输入边界

CUDA 每个线程处理一个像素，将四级四面体插值融合为一个 kernel。每一级读取 `.slut` 保存的 Q16 轴表，采用与 CPU 相同的比较顺序、整数乘加和 `(+32768) >> 16` 舍入，随后以 RGB8 结果进入下一级。融合没有跳过中间量化，也没有把四个模型复合成稠密查找表。

CUDA 只接受四个 SLUT v1、RGB8 节点模型，每级 `17 <= m <= 33`；检查完整文件尺寸、浮点网格有限且递增、覆盖 0 到 255，以及轴表索引和分数范围。模型文件自身不能证明其拟合过程属于独立、残差或复合语义，提交合同仍由上层验证器检查来源声明。

`apply` 读取 RGB8 图片并输出 PNG；拒绝 16-bit 和非三通道来源。`--competition` 额外要求 1024×768。`bench`、`verify` 始终要求恰好 100 张 1024×768 RGB8 图片。`pixels` 接受紧密 RGB8 原始字节，供非整块长度验收。`cube` 输出全部 256³ 个输入颜色，输入索引顺序为 B 最快。

`verify` 映射一次，不产生性能成绩；可输出按图片列表顺序紧密拼接的 RGB8 原始数据。CPU/CUDA 共用 `images`、`output_bytes`、`output_checksum_fnv1a64`、`per_image` 字段。FNV-1a64 使用标准 offset `14695981039346656037` 和 prime `1099511628211`，每图索引从 0 开始。严格比较还应对原始输出做 SHA256 或逐字节核验。

## 三种计时边界

| 字段 | 计入的工作 | 未计入的工作 |
| --- | --- | --- |
| `set_host_wall_ms_reps` / `set_host_wall_ms_p50` | 普通已解码 host RGB8 复制到 pinned 内存；H2D；四级 kernel；D2H 和同步；pinned 输出复制到普通 host RGB8 | 解码、分配、模型加载、哈希和输出编码 |
| `transfer_wall_ms_reps` / `set_transfer_wall_ms_p50` | 已在 pinned host 内存的 H2D、四级 kernel、D2H 和同步 | 每次普通 host 与 pinned 之间的两次复制，以及解码、分配、模型加载 |
| `resident_event_ms_reps` / `set_resident_event_ms_p50` | 已在 GPU 上的原始 100 图所需 kernel 序列 | H2D、D2H、host 复制、初始化和解码 |

CPU 对比应使用第一行，并对齐 CPU 的普通 host 输入复制到工作输出后原地映射的整组 wall time。第二、三行只能用于拆解 GPU 成本，不能直接当作相同端到端任务的加速比。batch=1 的整组数字也不是单张独立请求的延迟：同一 CUDA stream 可提交全部图像，再等待整组完成。

每次重复都读取不可变的原始图片；输出不会成为下一次重复的输入。普通 host 路径完成后核对其全组 checksum 与前一 pinned-transfer 路径一致，`bench -o` 导出普通 host 输出。预检则使用 `verify -o`，无需为正确性预检顺带运行性能循环。

`decode_ms`、`model_setup_ms`、`host_pinned_staging_ms` 单列初始化成本，其中 staging 字段包含 pinned 分配和首次复制。`cold_transfer_wall_ms` 是 transfer 第一轮；`cold_host_wall_ms` 是 host scope 第一轮，但发生在 transfer 阶段之后，不能解释为整个进程或设备的冷启动。`process_wall_ms` 和适配器的 `process_wall_seconds` 包含整个 benchmark 的全部重复与初始化，不是单次 100 图时间。

## 内存与利用率

`model_device_bytes` 是节点和轴表的设备分配；`image_device_buffers_bytes` 是显式图像设备缓冲，包括 benchmark 同时保留的 transfer 与 resident 两套缓冲。普通输入、普通输出和 pinned host 内存分别记录；这些数字不是驱动、分配器或整个进程的峰值显存。

适配器可选使用 `psutil` 每 25 ms 观察宿主进程，不要求普通用户安装监测依赖。`observed_peak_working_set_bytes` 在 Windows 优先采用 OS 的 `peak_wset`，其他平台为采样 RSS；它是主机内存。`host_cpu_percent` 是整个子进程的采样 CPU 时间，100% 表示一个逻辑 CPU，包含初始化、解码和哈希，不能解释为映射阶段利用率，更不是 GPU 利用率。缺少监测依赖时字段为 null。GPU 利用率和峰值显存需要另行采样，不从这些字段推导。

## 本阶段集中验收

本次构建 SHA256 为 `93de0dd41e18b83ad91e720a63ed417d8b69a16507ff9a17b94dd53ffda96780`。记录保存在 `artifacts/r18-unified/gpu/`，没有覆盖先前 v2/v3 证据。

- `tests/test_runtime_contract.py` 一项真实 CPU/CUDA 进程集成通过：m17/18/26/33 非均匀随机节点链、257 像素 PNG 与独立 Python Q16 一致，16-bit RGB 和错误比赛分辨率被拒绝，适配器保存命令与模型身份。配置 `JSHC_CUDA_BIN` 后该项必须真实执行 CUDA；便携 CPU 环境不强制安装 CUDA。
- 冻结 R17 m18 四级模型与 CPU 标量全色域逐字节一致；独立随机 m17/18/26/33 非均匀四级模型也一致，共 33,554,432 个全色域输入。
- 1、257、4099 像素长度与独立 Python Q16 结果一致。

新增 host scope 的性能仅应在统一静默窗口取得，旧 v3 的 transfer/resident 数字不能填入新字段。NVIDIA NPP 目前只有接口和布局调查，没有实现或可用基准成绩。
