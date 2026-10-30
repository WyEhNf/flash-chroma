# 16题内存第十一阶段：连续bank的LE16局部字典

Agent：`/root/memory`；Operator：本次 16题研究请求的用户；分支：`codex/p16-memory-20261023`。本阶段固定原 a399 模型，只改变精确派生 ROM 表示。首先冻结 2/4/8/16 个连续输入 bank 的离线容量剖析，唯一选中 4bank 后才实现 native；没有构建或计时其它 bank 数。完整域与边界通过，精度保留100%；常驻4248656B，分离输出单/四线程分别最劣保留51.8512%/57.9143%，可进入模式限定的50档。原地单线程失败，四线程A/A无效，不形成全情形推荐。

## 离线选择及跨bank重复代价

剖析计划 `banked-dictionary-profile-v1.json` 的 SHA 为 `1e895cbedaba306befe564085f37d33ffc5f183f25d56a09407915850a2b3545`。只读取原已验 M16D 16B 字典，按输入 RGB24 地址高位连续均分 1048576 个块，不读取 gold、照片或原滤镜来选择 bank。每 bank 局部 unique 必须不超过 65536，才能保留 LE16；所有四档独立重建全部 16MiB 逻辑 ID，SHA 均为 `a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`。

| bank数 | 各bank unique | 额外重复pool B | pool总B | ROM B | 按旧1056B model剖析的常驻B | 可LE16且小于3B门槛 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2 | 72171 / 50252 | 235456 | 1958768 | 4056984 | 4058040 | 否：第一个bank溢出 |
| 4 | 31453 / 48504 / 46303 / 8075 | 426048 | 2149360 | 4247584 | 4248640 | 是：唯一最小容量 |
| 8 | 3794 / 29564 / 28445 / 28008 / 28401 / 25798 / 4670 / 5549 | 744352 | 2467664 | 4565904 | 4566960 | 是，但更大 |
| 16 | 最大17055，完整16项见原件 | 1146848 | 2870160 | 4968432 | 4969488 | 否：超过3B |

冻结规则要求在可行且严格小于已合格 3B 常驻 4871152B 的档中选最小实际容量，并列按较少 bank；因此只实现 4bank。所有行均计入 2MiB map、`4×bank数` 字节 ROM base 元数据、1056B ROM 头/palette 和 1056B 旧 model，没有遗漏两份 palette，也没有用 ZIP 大小替代 RAM。离线进程峰值工作集为 67260416B，峰值 private commit 为 54038528B，含 Python/NumPy 和全部四档临时对象，不是运行时 RAM。

上表只对 unique 数实测，并由固定布局公式计算字节数；2/8/16 未生成 native ROM 或二进制。2bank 一行是编码溢出情况下的假设 LE16 字节数，不能当作可用载荷。唯一4bank实际生成的ROM文件大小在下节独立核对。

## 唯一native实现和真实ABI

新格式 `M16B v1` 固定 4bank，每个 bank 覆盖连续 262144 个 16B 输入块。每块只读取一次 LE16 局部 ID；`bank = RGB24 >> 22` 选择对应 pool base，最终偏移为 `base[bank] + 16*localID + (RGB24 & 15)`。map 为 2097152B，随后 16B LE32 元数据和四个连续 pool；pool 保留原16B块，只因跨bank重复而增加 426048B。

按 root 审阅意见，base 缓存使用独立 `uint32_t bases[4]`，不复用 palette 末槽。新 model 实测 **1072B**，比离线选择假设多 16B；ROM 仍为 4247584B，完整常驻为 **4248656B**，比已合格 3B 再少 622496B，约 12.78%。旧 profile 原值不回写；这 16B 不改变已冻结选择排序。

独立 ctypes 适配器先查询 native `jshc_mem_model_size`，只接受 1072B 对象，不能把旧 1056B 对象传给新 prepare。prepare 验证四个 pool base 连续/有序、每个 pool 非空且局部块数不超过65536、所有 map 局部索引和 pool palette ID；256 项合法 palette 契约保持。ROM 不可变借用、失败清零、out/ROM 重叠无写拒绝、零长度和部分重叠拒绝沿用原契约。C99 显式 LE16，不要求 ROM 对齐或外部 padding；桌面 AVX2 使用 `memcpy2`，只有 lookup 和 bases 参数传递改变，原像素/存储算法保持。

唯一4bank离线导出进程峰值工作集70914048B、峰值private commit54517760B，包含Python/NumPy及序列化临时对象，与四档profile进程分列。GCC `.su` 静态栈报告为C99 prepare1168B、apply64B；AVX2原地256B/分离272B；桌面适配器160B、OMP worker144B。这些是各函数编译器报告，不是调用链实测峰值。核心没有堆调用；桌面库/OMP/进程启动分配不包含在零堆承诺内。

## 已执行质量与环境

Windows11 26200 x64、AMD Ryzen9 8945HX，Python3.12.14/NumPy1.26.4、GCC/G++15.2。C99 为 `-O3 -std=c99 -pedantic-errors -Wall -Wextra -fstack-usage`；C++17/OpenMP 适配器只有像素 TU 增加 `-mavx2 -mtune=skylake -ffp-contract=off`，无 AVX512/native/LTO。环境 `OMP_NUM_THREADS=1`、`OMP_DYNAMIC=FALSE`、`OMP_WAIT_POLICY=PASSIVE`、`OPENBLAS_NUM_THREADS=1`、`NUMBA_NUM_THREADS=1`，显式完整域 AVX2 单/四线程分别执行。

native 计划 SHA 为 `efb7074f38da3c354df64394177a450cedcbb46ef02e2ce26c50aa430d6f6ea2`。实际 ROM SHA 为 `8492d8b7376d86d9442ef53023574aa8345333a16cc7dd8dceba34998e659cfd`。C99、桌面 scalar、AVX2 单/四线程四次完整 `256³` 输出 SHA 均为原 a399 的 `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，精度及逐图输出保留100%；原全域误差仍 mean0.9811105967、p993.7416573868、max8.1240384046。

实际桌面DLL SHA为 `ef2469eeba143e5787d7c6d3fe3ea0b73eb3acdbb5ce7d20feb3a98fce5e3733`，独立C99 DLL为 `c16b67e7af4034fb4bd93a38d83b54d08d8ab7b74abca3edb98f7780a47c6921`。新主DLL使用独立文件名，计时加载时再核 `GetModuleFileNameW` 实际路径，原32/3B/17bit控制不重编译。

另通过 370 个有限/非对齐/原地/分离比较、27 个格式/索引/范围/部分重叠拒绝、60 个图像保护页及12个 ROM末端组。正向构造完整256项palette，把252..255四个最高合法 ID 写入最后一个 pool 块，对照独立期望RGB，确认独立bases不会覆盖合法颜色；最后map项指向最后pool的检查另有ROM末端 `PAGE_NOACCESS`。

## 正式性能与有效性边界

冻结同场七角色为 78、80、原32bit、原3B、原紧密17bit、新4bank AVX2、新4bank C99。四新worker轮转/反序，单/四线程和原地/分离各预热1+5次完整百图；百图235929600B按原顺序连接，一次API处理完整批次，输入恢复不计时。每worker较快78/80耗时除候选，最劣worker按100/90/80/70/60/50六档；A/A单对0.8..1.25且中位1/1.1..1.1，失败清空该情形正式档位。

已按计划完整执行一次，没有补跑。原地1、分离1、分离4的A/A中位分别0.9402967、0.9838120、0.9980085，均有效。原地4中位1.0273605虽在门槛内，但worker3单对为1.4933552，超过1.25，因此原地4的**所有100..50档全部清空**。四进程原始五轮和A/A全部保留，不能只检查中位。

下表为四worker最劣吞吐，精度均100%。`*`列是A/A无效下的描述值，不作为任何档位证据。

| 角色 | 常驻B | 原地1 | 原地4* | 分离1 | 分离4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 原32bit | 5919728 | 60.7975% | 46.4836%* | 62.7121% | 71.0483% |
| 原3B | 4871152 | 39.8454% | 42.0583%* | 54.1228% | 64.0268% |
| 原紧密17bit | 3953648 | 30.4800% | 30.5206%* | 39.7522% | 45.2847% |
| 4bank AVX2 | 4248656 | 37.7324% | 39.1750%* | 51.8512% | 57.9143% |
| 4bank C99/桌面OMP | 4248656 | 20.4569% | 31.1932%* | 28.3329% | 31.8943% |

新4bank原地1的中位52.0138%也不能代替最劣37.7324%。分离1和分离4全部四worker过50，但未过60；因此只有这两个模式可以用4248656B进入50档。相对当前最快78/80的28046644B，常驻约减少84.85%；相对同场分离模式也合格的3B再少12.78%，代价是配对吞吐中位分别保留旧3B的94.9725%/91.4019%，最劣worker为87.3086%/89.8941%。这不是不降速的内存收益。

六档只依据本场七角色和有效控制，不拼接历史最好值。`参考`为28046644B；`32`为5919728B，`3B`为4871152B，`4bank`为4248656B；原地4整列无资格。分离输出的100档没有单一DLL在所有worker均达到每worker较快端点，不虚构固定库100%通过。

| 速度/精度底线 | 原地1 | 原地4 | 分离1 | 分离4 |
| --- | --- | --- | --- | --- |
| 100% | 80参考 | A/A无效 | 无固定单库通过 | 无固定单库通过 |
| 90% | 参考 | A/A无效 | 参考 | 参考 |
| 80% | 参考 | A/A无效 | 参考 | 参考 |
| 70% | 参考 | A/A无效 | 参考 | 32 |
| 60% | 32 | A/A无效 | 32 | 3B |
| 50% | 32 | A/A无效 | 4bank | 4bank |

## 旧3B的有效反例与推荐范围收缩

前一[独立确认](2026-10-24-memory-dictionary-confirmation.md)合并八worker，在当时冻结协议下原3B全部四情形最劣50.4771/67.4356/61.7006/70.4853%，通过事实及原件保持。本次依然直接载入同一原3B DLL，却在A/A有效的原地1里出现worker0 **39.8454%**；其它worker为50.9625/60.4009/65.7617%。因此**取消跨场稳健全情形50推荐**，不再用旧八worker过线覆盖这个新有效反例。

本场worker0原地1较快参考80中位48.5562ms，旧3B中位121.8614ms，4bank中位128.6856ms；这三个值都对应相同完整百图调用。该worker的A/A比为1.1667120，按冻结单对0.8..1.25/整体中位门槛仍有效。原二进制来源、全部角色源、DLL实际加载路径及数据SHA均复核，当前没有证据解释这种变化；不能归因角色集合、lookup位宽或某个未测主机因素，也不靠重跑挑较好结果。

为研究变动而写的[可证伪诊断设计](../../experiments/dictionary-drift-diagnostic-design.md)目前只静态提出，未执行，不属于本阶段通过项，不产生新速度档位或恢复推荐。

SHA预检使用已经流式实现的 `study_memory_rom.sha`，RSS-only worker不分配照片数组；进程峰值仍包括Python/NumPy、导入模块、库、输入预检及准备，不是纯函数RAM。C99四线程仍依赖桌面OMP适配器，独立C99 DLL只证明完整域与边界，不宣称实板速度。本阶段未做WASM/ARM实板，官方对派生ROM的许可未知。

| 同场独立RSS角色 | 准备前工作集B | 准备后工作集B | 峰值工作集B | 峰值private commit B |
| --- | ---: | ---: | ---: | ---: |
| 78 | 35377152 | 64573440 | 132800512 | 121061376 |
| 80 | 35454976 | 64577536 | 132804608 | 120995840 |
| 原32bit | 35569664 | 42160128 | 42160128 | 28520448 |
| 原3B | 35594240 | 41107456 | 41107456 | 27463680 |
| 原17bit | 35545088 | 40263680 | 40263680 | 26521600 |
| 4bank AVX2 | 35581952 | 40480768 | 40480768 | 26845184 |
| 4bank C99/桌面适配器 | 35667968 | 40660992 | 40660992 | 26963968 |

复现入口依次为 `profile_banked_dictionary.py --freeze`、同脚本剖析、`generate_banked_dictionary.py`、`freeze_banked_dictionary.py`、`export_banked_dictionary.py`、`build_banked_dictionary.py`、`verify_banked_dictionary.py`、`bench_banked_dictionary.py`。原件路径为 `artifacts/p16-banked-dictionary-{profile,rom,build,verify,perf}-v1`；生成和冻结步骤仅用于新目录/首次创建，已保存计划不可覆盖。精简原字节、唯一4bank ROM、二进制及完整轮次位于 [证据目录](../../report/data/p16-banked-dictionary-v1)，由 `audit_banked_dictionary.py` 复算唯一选择、额外16B ABI、序列化全部ID、旧DLL来源、A/A和六档。

发布审计已通过：12个原件（含manifest）、47个ZIP成员、28行主统计。独立从实际序列化ROM解码全部ID仍为a020c67a…；去除lookup和归一bases参数传递后的像素逻辑逐字节相同，SHA为 `c5b69bc56cac4ef8b763a7381728dc6fe87400acf5d1fab7c95ff5ca827b7a0e`。没有重跑正式性能来完成发布审计。

本机首次实际执行的主命令如下，`PY`为现有Python3.12；已存在的输出目录应换新路径，不覆写原件。相同二进制重放可从发布包恢复新DLL/ROM，依赖及旧控制按manifest所列旧包恢复，完整SHA由计划和结果绑定。

```text
PY -X utf8 scripts/profile_banked_dictionary.py --output artifacts/p16-banked-dictionary-profile-v1 --freeze
PY -X utf8 scripts/profile_banked_dictionary.py --output artifacts/p16-banked-dictionary-profile-v1
PY -X utf8 scripts/generate_banked_dictionary.py
PY -X utf8 scripts/freeze_banked_dictionary.py --old-build artifacts/p16-compact-dictionary-build-v1 --old-roms artifacts/p16-compact-dictionary-rom-v1
PY -X utf8 scripts/export_banked_dictionary.py --output artifacts/p16-banked-dictionary-rom-v1
PY -X utf8 scripts/build_banked_dictionary.py --output artifacts/p16-banked-dictionary-build-v1
PY -X utf8 scripts/verify_banked_dictionary.py --build artifacts/p16-banked-dictionary-build-v1 --roms artifacts/p16-banked-dictionary-rom-v1 --output artifacts/p16-banked-dictionary-verify-v1
PY -X utf8 scripts/bench_banked_dictionary.py --build artifacts/p16-banked-dictionary-build-v1 --roms artifacts/p16-banked-dictionary-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --output artifacts/p16-banked-dictionary-perf-v1
```
