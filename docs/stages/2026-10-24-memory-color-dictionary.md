# 16题内存第十三阶段：RGB32预展开精确块

Agent：`/root/memory`；Operator：本次16题研究用户；分支：`codex/p16-memory-20261023`。Status：Completed（研究完成，候选不升级）。固定原a399模型，唯一新表示从旧3B map→ID→palette改成3B map→RGB32；省去最后一次串行palette读取，代价是块池扩大四倍。完整域无损，但只有分离四线程达到速度50档，且同场旧3B更快、更小，未进入Pareto前沿。默认路径与旧3B原件不变。

## 格式与容量

没有扫描块尺寸或颜色参数。M16C v1保持107707个16像素块及顺序，3MiB LE24 map指向64B LE RGB32块，最高颜色字节为零。32B头+3145728B map+6893248B pool=**10039008B ROM**，实际新借用对象为32B，完整常驻**10039040B**。比本分支78/80基线的28046644B少64.21%，比旧3B的4871152B大106.09%。六档速度须另行实测，较小容量或更短依赖链均不能替代速度证据。

新的ctypes对象在prepare前查询DLL真实`sizeof`，只接受32B ABI，不能复用旧1056B/1072B对象。ROM借用不可变，核心零堆；prepare验证24bit总范围、所有map块起点、每项64B范围与所有RGB32最高字节。C99显式LE24取偏移，RGB32作为序列化字节复制，保持端序独立。8像素先读全输入对应颜色地址，前7项4B重叠写、末项3B，短尾3B；不要求用户padding。AVX2只改变颜色读取与移除palette依赖，输入循环、预取、输出布局及线程块保持原3B算法。

## 已执行质量

执行前冻结计划`cc6f9b27988e580776e36895c9cdca19468948872610c8861f302cc9c7d19ba2`，随后唯一导出/构建/质量各执行一次。导出仅读取冻结M16D，不用gold/照片选型；独立解码全16MiB逻辑ID与RGB32，原/新颜色摘要一致。ROM SHA为`aa0267aab4c7137d4cdccf7d087b559a7bec0ba5b33da5ea65fa3ce0db27ec30`；桌面DLL为`0d65c5d7239c7af4c1cb1102740390d8b796fade356597473b19e11e3f1a7b77`，独立C99 DLL为`e1c16bbfd3cb60443aa10832a3193a6c4695dcafcfdde01c8df9764516bc3b8c`。

纯C99、桌面scalar、AVX2单/四线程四次完整256³输出SHA均为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，逐字节与a399一致，精度及逐图输出保留100%。原完整域mean0.9811105967、p993.7416573868、max8.1240384046不变。另通过367项有限/非对齐/原地/分离检查、26项格式/地址/重叠拒绝、90项图像保护页（包括C99八像素尾部）和12项ROM保护页。

最后map被强制指向最后64B pool，并以输入`ffffff`访问最后RGB32，ROM真实末端紧贴`PAGE_NOACCESS`，独立期望取最后3B；同时测试任意RGB24高值`abcdef`，没有230色窄域限制。AVX2 map末项4B读取额外一字节在合法非空pool内并被mask；最后颜色4B恰好结束于ROM末端。C99 map只读3B。

实际环境Windows11 26200 AMD64、AMD Ryzen9 8945HX、Python3.12.14/NumPy1.26.4、GCC/G++15.2。C99为`-O3 -std=c99 -pedantic-errors -Wall -Wextra -fstack-usage`；桌面C++17/OpenMP，仅像素TU增加`-mavx2 -mtune=skylake -ffp-contract=off`，无AVX512/native/LTO。OMP环境1线程、dynamic关闭、wait passive，显式API测试1/4线程；NumPy/Numba限制单线程。质量与tail的16bit非计时质量按root授权并行，不产生速度结论。

离线导出峰值工作集102391808B、峰值private commit89083904B，包括Python/NumPy与临时对象，不是运行时容量。GCC静态stack usage为prepare80B、C99 apply144B、AVX2原地256B/分离272B、桌面适配器160B/OMP worker112B；这些是各函数报告，不是调用链峰值或MCU实板RAM。

## 正式性能与失效场次

五角色78、80、旧3B、新AVX2、新C99在同一正式排他窗口完整执行一次；四新worker、双接口、单/四线程各预热1+5完整百图，较快78/80作分母，全部worker最劣分别判断100/90/80/70/60/50档。A/A逐对0.8..1.25且中位1/1.1..1.1，失败清空对应正式档位。235929600B百图按原顺序连接，一次API处理完整批次；输入恢复不计时。未锁频、未绑核、未控制温度；root/speed/tail计时期间静默，所有原始轮次保留，无补跑。旧3B不作为速度资格分母，也不因本轮配对撤销此前有效39.8454%反例。

原地1的worker2 A/A为0.7725569822，低于0.8；原地4的worker3为1.4933383790，高于1.25。尽管两列A/A中位0.9866395854/1.0200732756均在门槛内，仍将两列全部100..50档清空。分离1/4的四单对全部合格，中位为0.9278630535/0.9981805027。下表`*`为无效场描述，不作资格。

| 角色 | 常驻B | 原地1*最劣 | 原地4*最劣 | 分离1最劣 | 分离4最劣 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 旧3B AVX2 | 4871152 | 52.4010%* | 60.9709%* | 47.5278% | 65.3590% |
| 新RGB32 AVX2 | 10039040 | 43.8922%* | 37.0671%* | 41.9474% | 53.4480% |
| 新RGB32 C99/桌面OMP | 10039040 | 24.6768%* | 28.9301%* | 25.5382% | 29.4260% |

所有精度均100%，但不能用中位替代最劣worker：新AVX分离1中位49.1844%仍失败，分离4中位54.3280%、最劣53.4480%仅过50。新C99有效两情形全部低于50，没有可移植速度资格；四线程是桌面OMP适配器，独立C99 DLL没有单独计时。原地1/4无效，不作“算法必然低50”的结论。

有效分离4下，同场旧3B耗时/新RGB32耗时中位0.8212963696、最劣0.8141024281，新格式吞吐较旧3B下降约17.87%且常驻扩大106.09%，没有形成内存/速度前沿。分离1配对中位0.8421632383、最劣0.6385111285也无收益。更短源码依赖链并未转成可接受的综合结果；没有干预证据把原因归咎于缓存容量、某个核心或迁移。

六档按本场五角色与有效控制复算。`参考`为28046644B固定78，`旧3B`为4871152B。新RGB32虽分离4达50，但同场更小旧3B已达60，因此不被容量最小规则选中；不把本场旧3B的单模式资格推广成跨场稳健全情形推荐。

| 速度/精度底线 | 原地1 | 原地4 | 分离1 | 分离4 |
| --- | --- | --- | --- | --- |
| 100% | A/A无效 | A/A无效 | 无固定单库过线 | 无固定单库过线 |
| 90% | A/A无效 | A/A无效 | 参考 | 参考 |
| 80% | A/A无效 | A/A无效 | 参考 | 参考 |
| 70% | A/A无效 | A/A无效 | 参考 | 参考 |
| 60% | A/A无效 | A/A无效 | 参考 | 旧3B |
| 50% | A/A无效 | A/A无效 | 参考 | 旧3B |

旧3B此前八worker通过和后来有效原地39.8454%反例均保持；本次又出现**A/A有效分离1最劣47.5278%**，因此不能恢复稳健全情形50推荐。旧DLL SHA与原件一致，未知因果继续保留；没有选择较好的worker或补跑。

## 新进程RSS与限制

| 角色 | 准备前工作集B | 准备后工作集B | 峰值工作集B | 峰值private commit B |
| --- | ---: | ---: | ---: | ---: |
| 78 | 35446784 | 64630784 | 132845568 | 121122816 |
| 80 | 35377152 | 64782336 | 132919296 | 120987648 |
| 旧3B | 35483648 | 41238528 | 41238528 | 27361280 |
| RGB32 AVX2桌面 | 35450880 | 46137344 | 46137344 | 32464896 |
| RGB32 C99桌面 | 35450880 | 46198784 | 46198784 | 32468992 |

五份RSS为独立新进程相同导入群，模型准备后、照片数组分配前读取；预检`file_digest`流式读取输入，不构造235MB整文件。峰值包括Python/NumPy、loader、库和预检，不能当纯模型RAM。相同桌面DLL的C99与AVX2角色独立进程略有差别不作核心容量差异解释。

独立C99完成Windows x64实际运行与严格语言编译，未执行WASM或ARM实板。官方对派生ROM许可仍未知。亲和性干预仍[仅静态设计](../../experiments/dictionary-affinity-intervention-design-v1.md)，没有纳入本场，更没有用于恢复资格。

## 证据与复现

主要源为`experiments/color-dictionary-runtime/`，生成/冻结/导出/构建/质量/性能工具均为`scripts/*color_dictionary.py`。精简包位于[report/data/p16-color-dictionary-v1](../../report/data/p16-color-dictionary-v1/)，包括原始质量、完整原始性能与A/A、五RSS、源及对象、原/新ROM、SHA清单。`execution.stdout`保留底层bench打印的过滤前档位，正式`performance.json`由冻结外层驱动清空失效场，再由审计逐项复算，不能把旧stdout升级为有效资格。

PowerShell环境设置OMP/NumPy/Numba单线程和OMP passive后，实际关键命令为：

```text
python -X utf8 scripts/generate_color_dictionary.py
python -X utf8 scripts/freeze_color_dictionary.py
python -X utf8 scripts/export_color_dictionary.py --output artifacts/p16-color-dictionary-rom-v1
python -X utf8 scripts/build_color_dictionary.py --output artifacts/p16-color-dictionary-build-v1
python -X utf8 scripts/verify_color_dictionary.py --build artifacts/p16-color-dictionary-build-v1 --roms artifacts/p16-color-dictionary-rom-v1 --output artifacts/p16-color-dictionary-quality-v1
python -X utf8 scripts/bench_color_dictionary.py --build artifacts/p16-color-dictionary-build-v1 --roms artifacts/p16-color-dictionary-rom-v1 --ref80 F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll --data-root F:/Hackathon/projects/16-lut-color --repeats 5 --output artifacts/p16-color-dictionary-perf-v1
```

这里`python`实际为原仓`artifacts/error-study-py312/Scripts/python.exe`；输出目录首次运行须不存在，冻结计划已存在时复现直接验证原计划，不覆盖。构建器记录完整编译器路径、二进制SHA、命令和返回码。发布与审计脚本分别为`archive_color_dictionary.py`、`audit_color_dictionary.py`；审计重建全部RGB32、核暂存字节/ZIP CRC/哈希/实际ABI/旧原DLL，并复算80条原始角色记录、20项主比值及四控制与六档，不再次计时。
