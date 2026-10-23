# 16题内存第十阶段：17bit 块 ID 的 16+1bit 分平面表示

Agent：`/root/memory`；Operator：本次 16题研究请求的用户；分支：`codex/p16-memory-20261023`。本阶段固定原 a399 模型，不叠加其它方向的新精度模型。新分平面完整域与边界全部正确，但四情形最劣吞吐仅保留 34.22/45.21/42.07/49.22%，均低于 50% 底线；容量相同的旧紧密 17bit 在四线程分离输出保留 54.71%。本阶段作为无损表示的负结果封存，不推荐替换旧格式。

## 目标、改动与容量

前一紧密 17bit 格式合并八 worker 后，只有四线程分离输出通过 50% 吞吐线。新格式 `M16S` 把同一个 17bit 块 ID 分为 2MiB LE16 低平面和 128KiB 高位平面；palette、107707 个 16B pool、节点和模型顺序均不变。两个平面可独立读取，合并后仍有 pool/palette 依赖；预期是减少 `17*block` 和跨字节移位，但多一次 map 读取可能抵消收益。

执行前的依赖、布局与边界推导保留在 [冻结设计](../../experiments/compact-dictionary-split-design.md)。新源码位于 `experiments/split-dictionary-runtime/`；原 32bit、3B、紧密 17bit DLL 均不重编译。生成器只替换 lookup 和独立 namespace；像素循环其余文本在发布审计时比较。

| 项目 | M16S 实测字节 |
| --- | ---: |
| 头部及 palette | 1056 |
| LE16 低平面 | 2097152 |
| 1bit 高平面 | 131072 |
| 原 16B 字典 pool | 1723312 |
| 实际磁盘 ROM | 3952592 |
| Windows x64 model 对象 | 1056 |
| ROM 借用常驻容量 | 3953648 |
| C99 prepare 静态栈报告 | 1152 |
| C99 apply 静态栈报告 | 64 |
| AVX2 像素函数静态栈报告 | 272 |
| 桌面适配器/OMP worker 静态栈报告 | 160 / 128 |

同容量紧密 17bit 的 ROM 和 model 字节完全相同；不能声称本轮又压小内存。对当前最快 78/80 的 28046644B 常驻，容量约减少 85.90%。这是实际解压 ROM 加 model 的容量，不是压缩 ZIP 大小。prepare 和运行 scratch 只列编译器 `.su` 静态函数报告，不冒充 Windows 调用链实测峰值。

离线导出完整逻辑 ID 的 Python/NumPy 进程峰值工作集为 81358848B、峰值 private commit 为 68063232B；这包含导出器和所有临时数组，不能计入核心常驻或称为 loader 峰值。C99 核心不调用堆，ROM 是调用方不可变借用；桌面 DLL/OMP 的运行库分配不属于零堆承诺。

## 已执行的正确性和环境

Windows 11 26200、AMD Ryzen 9 8945HX、AMD64、GCC/G++ 15.2，Python 3.12.14、NumPy 1.26.4。C99 核心使用 `-O3 -std=c99 -pedantic-errors -Wall -Wextra -fstack-usage`；桌面适配器为 C++17/OpenMP，只有像素 TU 增加 `-mavx2 -mtune=skylake -ffp-contract=off`，未使用 AVX512、`-march=native` 或 LTO。环境为 `OMP_NUM_THREADS=1`、`OMP_DYNAMIC=FALSE`、`OMP_WAIT_POLICY=PASSIVE`、`OPENBLAS_NUM_THREADS=1`、`NUMBA_NUM_THREADS=1`；显式完整域 AVX2 单/四线程分别验证。CPU 型号另由本机 `Get-CimInstance Win32_Processor` 核对；正式性能由 root 串行安排排他窗口，未锁频、绑核或控温，不外推其它 CPU。

冻结计划 SHA 为 `46b971e07a722a497de3e041f30570d82670734241a7b45cbcb8993fb081a2b4`。ROM SHA 为 `4846058639722811656bd93af7afb977e2dbad5918e6bdb502929cded5d74b1f`；桌面 DLL SHA 为 `c09b9053c75c44170b1c70436704cd56d5f1d8cd13d3dbdbcafd19ff5d208bb3`，独立 C99 DLL SHA 为 `a8992fa11714a7ade8dcd81e05f4cafead5aca94d84ac97a4293991e2659f78d`。

先离线重建全部 `256^3` 个 ID，SHA 仍为 `a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`。随后独立 C99、桌面 scalar、AVX2 单/四线程四个完整 RGB 域输出全部等于原 a399 的 `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，所以 mean/p99/max 和逐图误差保持原值，精度保留率 100%；a399 全域误差仍为 mean 0.9811105967、p99 3.7416573868、max 8.1240384046。本阶段没有重新拟合或以少量照片代替完整域等价验证。

另外通过 364 个有限长度/偏移/原地/分离及非对齐 ROM 检查、24 个格式/范围/部分重叠/坏高位索引拒绝、60 个图像末端保护页检查、12 个 ROM 末端检查。最后一个低平面项与高位项被强制指向最后一个 pool 块，用独立 palette 字节构造期望结果，并将 ROM 末端紧贴 `PAGE_NOACCESS`，覆盖最后一个 pool 字节。所有失败 prepare 清零和重叠 prepare 保持 ROM 的契约均通过。

## 同场性能、六档和限制

已按冻结计划执行同场七角色：78、80、原 32bit、原 3B、原紧密 17bit、新 AVX2 分平面、新 C99 分平面。四新 worker 轮转/反序、双接口和单/四线程、各预热一次加五次完整百图；同 worker 的较快 78/80 为分母，四 worker 最劣值决定六档。每角色预热和最后一次百图均再次核对原输出 SHA。A/A 单对须为 0.8..1.25 且中位 `1/1.1..1.1`；本场四组全部有效，中位分别为原地1线程 0.9740165、原地4线程 1.0336231、分离1线程 1.0403817、分离4线程 0.9861113。

性能数据是固定 `100×1024×768` RGB8 照片按原顺序连接的 235929600B；输入 SHA `e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd`，过滤后 SHA `f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。每一轮通过一次 API 调用处理整个百图批次；输入恢复复制不在计时内，不冒充逐图独立调用延迟。

下表全部为四 worker 最劣吞吐保留率，精度均为 100%。旧三个字典使用原二进制，实际载入路径再次通过 `GetModuleFileNameW` 核对；不能把表中旧控制的历史跨场变化解释为本轮布局效果。

| 同场表示 | 常驻B | 原地1 | 原地4 | 分离1 | 分离4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 原 32bit AVX2 | 5919728 | 62.8992% | 75.4574% | 74.1194% | 82.5748% |
| 原 3B AVX2 | 4871152 | 53.3753% | 66.7521% | 63.9862% | 74.4745% |
| 原紧密 17bit AVX2 | 3953648 | 37.5835% | 47.3779% | 46.1015% | 54.7095% |
| 新分平面 AVX2 | 3953648 | 34.2189% | 45.2121% | 42.0739% | 49.2153% |
| 新分平面 C99 / 桌面 OMP | 3953648 | 22.1324% | 28.8683% | 27.0374% | 33.0287% |

新分平面四线程分离的中位保留率为 50.8133%，但最劣为 49.2153%，因此严格拒绝。不会以中位数越线代替最劣门槛，不重跑取较好的 worker。额外 map 读取没有换来实际速度收益；具体同 worker 的旧紧密格式耗时/新分平面耗时另外列入 `layout-pairs.json`，不靠跨场绝对毫秒归因。

| 相对同容量旧紧密17bit的吞吐比 | 四worker中位 | 最劣worker |
| --- | ---: | ---: |
| 原地1 | 91.8515% | 90.2780% |
| 原地4 | 95.3757% | 93.2793% |
| 分离1 | 92.2846% | 90.4023% |
| 分离4 | 91.5331% | 85.9268% |

六档结果只比较这七个固定角色；表内为过线者中容量最小的表示，不合并先前独立 Clang/store 等场次。`参考` 为 28046644B，`32` 为 5919728B，`3B` 为 4871152B，`17` 为 3953648B。分离输出的 100% 行没有一个固定 DLL 在全部 worker 都等于每 worker 的较快端点，原始表如实为 null，不能虚构一个单库 100% 通过。

| 速度/精度底线 | 原地1 | 原地4 | 分离1 | 分离4 |
| --- | --- | --- | --- | --- |
| 100% | 80参考 | 78参考 | 无固定单库通过 | 无固定单库通过 |
| 90% | 参考 | 参考 | 参考 | 参考 |
| 80% | 参考 | 参考 | 参考 | 32 |
| 70% | 参考 | 32 | 32 | 3B |
| 60% | 32 | 3B | 3B | 3B |
| 50% | 3B | 3B | 3B | 17 |

## RSS口径纠正与复现

本场冻结 wrapper 在每个子进程开始时验证完整输入 SHA；该阶段把 235929600B 照片文件整块读入。它不在计时范围内且随后释放，但会污染进程的峰值工作集。原七个 RSS 记录完整保留在正式性能原件，不能称为 prepare 峰值，也不改写或重跑本场性能。

发现这个口径后，另行冻结 `split-dictionary-rss-v1.json`，在七个独立新进程中用 1MiB 分块流式 SHA 验证相同源和输入，加载相同导入群，复用相同 setup 和 RSS-only worker；不构造照片数组。补充原件单独保存，工作集和峰值仍包括 Python/NumPy、导入模块、系统 CRT、库和输入身份预检；不是扣净运行库的核心 RAM。两个进程群的绝对峰值不拼接成收益。

以下均是这组流式补充进程的原值 B，峰值来自同一进程生命周期，不能单独归因某个 prepare 函数。新格式和紧密 17bit 之间约 0.1MiB 的进程差异不当作模型容量收益。

| 角色 | prepare前工作集 | prepare后工作集 | 峰值工作集 | 峰值private commit |
| --- | ---: | ---: | ---: | ---: |
| 78 | 35401728 | 64667648 | 132943872 | 121085952 |
| 80 | 35426304 | 64700416 | 132952064 | 121372672 |
| 原32bit | 35323904 | 42082304 | 42082304 | 28221440 |
| 原3B | 35446784 | 41164800 | 41164800 | 27406336 |
| 原紧密17bit | 35508224 | 40296448 | 40296448 | 26537984 |
| 新分平面AVX2 | 35405824 | 40194048 | 40194048 | 26464256 |
| 新分平面C99/桌面适配器 | 35360768 | 40148992 | 40148992 | 26365952 |

本阶段未执行 M16S 的 WASM/ARM 实板验证。四线程 C99 性能是桌面 OpenMP 适配器下的核心吞吐；独立 C99 DLL 只声明本阶段完整域和边界正确性。官方对派生 ROM 的许可未知，不声明赛事合法或官方成绩。

复现命令在本分支 worktree 执行，`PY` 指向现有 Python 3.12，先保持上述线程环境；生成目录及输出目录须为新路径。冻结计划已经存在时不覆盖，直接使用记录的源码和计划。

```text
PY -X utf8 scripts/generate_split_dictionary.py
PY -X utf8 scripts/freeze_split_dictionary.py --old-build artifacts/p16-compact-dictionary-build-v1 --old-roms artifacts/p16-compact-dictionary-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color
PY -X utf8 scripts/export_split_dictionary.py --output artifacts/p16-split-dictionary-rom-v1
PY -X utf8 scripts/build_split_dictionary.py --output artifacts/p16-split-dictionary-build-v1
PY -X utf8 scripts/verify_split_dictionary.py --build artifacts/p16-split-dictionary-build-v1 --roms artifacts/p16-split-dictionary-rom-v1 --output artifacts/p16-split-dictionary-verify-v1
PY -X utf8 scripts/bench_split_dictionary.py --build artifacts/p16-split-dictionary-build-v1 --roms artifacts/p16-split-dictionary-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --output artifacts/p16-split-dictionary-perf-v1
PY -X utf8 scripts/rss_split_dictionary.py --build artifacts/p16-split-dictionary-build-v1 --roms artifacts/p16-split-dictionary-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --output artifacts/p16-split-dictionary-stream-rss-v1 --freeze
PY -X utf8 scripts/rss_split_dictionary.py --build artifacts/p16-split-dictionary-build-v1 --roms artifacts/p16-split-dictionary-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --output artifacts/p16-split-dictionary-stream-rss-v1
```

原件位于 `artifacts/p16-split-dictionary-{rom,build,verify,perf,stream-rss}-v1`。精简原字节、两群 RSS、逐轮百图、实际二进制和 ROM 发布到 [证据目录](../../report/data/p16-split-dictionary-v1)；SHA/CRC、原 DLL 来源、像素循环不变和统计档位由 `audit_split_dictionary.py` 静态复算通过：13 个原件（含 manifest）、57 个 ZIP 成员、28 行统计。去掉 lookup 并归一 namespace 后的整个 AVX2 源文本逐字节相同，SHA `556673c3e1773c0dcb77eaf141131064da8bc69d34c1e0ac81c88b53206363be`。
