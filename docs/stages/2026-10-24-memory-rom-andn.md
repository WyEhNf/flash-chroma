# 线性ROM接入原78的两种ANDN入口

Agent：Codex `/root/memory`；Operator：本会话项目用户；Task：16题方向3第二阶段；Status：本轮验证与性能完成，100%速度目标未达到。基于`a88107b`，不更新第一阶段字典结论或公共默认。

上一阶段线性ROM省40.17%常驻容量，但只复用普通线性`to`内核，原地路径没有原78的BMI1入口。本阶段分别复制原78原地和分离两个像素TU，只替换命名空间及table形参类型为字节指针。RGB24读取、ANDN、NTA/NT/SFENCE、边界和输出组织保留，未加新像素算法或参数。支持BMI1时按原地/分离接口进入对应函数，其余情况使用首阶段已验generic函数。字典对象逐字节复用，C99公式与模型不变。另将header的GNU visibility限制为GNU/Clang，其他C99编译器留空；Windows导出支路不变。

`experiments/memory-rom-andn-v1.json`在构建前冻结8份源SHA。增量构建只编译C99、dispatcher和两个ANDN TU，不重新构建或挑选旧AVX2对象。环境与第一阶段相同：Windows11 26200/Ryzen9 8945HX/GCC15.2，显式AVX2/BMI1局部TU，OMP_DYNAMIC=FALSE、OMP_WAIT_POLICY=PASSIVE，未锁频/绑核。构建7.5秒；15配置完整256³、3850有限合同、304保护页/非对齐和23拒绝全部通过，完整域及百图SHA不变。未在缺BMI1硬件运行，generic函数复用第一阶段已验对象。

随后只比较78、80和新线性ROM三个角色。沿用四新进程、交错线程和双接口、每配置1预热＋5次完整100图，以及每模式尾部80 A/A控制。计时排除准备、copy、IO和hash，首尾hash核对；共240个主要计时轮次、80个A/A轮次。速度分母仍为每个同场worker中78/80较快者，不拼接前阶段绝对时间。

| 运行情形 | 候选中位吞吐保留 | 最劣worker保留 | A/A比中位 | 资格 |
| --- | ---: | ---: | ---: | --- |
| 原地1线程 | 88.52% | 71.65% | 1.0568 | 单对1.251089超1.25，拒绝正式结论 |
| 原地4线程 | 97.40% | 90.98% | 0.9988 | 本轮符合90%速度档 |
| 分离输出1线程 | 102.17% | 94.26% | 0.8251 | 中位低于1/1.10，拒绝正式结论 |
| 分离输出4线程 | 100.94% | 88.88% | 0.9843 | 本轮符合80%速度档 |

预设A/A要求单对0.8..1.25、中位1/1.10..1.10，不能因1.251089只略越界而放宽。单线程两类失败记录原样保留，不排除worker、不补挑轮次，不宣称100%或整体通过。四线程有效情形全部保留100%精度；90%原地档和80%分离档可用16,779,328字节容量，较28,046,644字节基线省40.17%。更小字典仍按第一阶段各接口的真实档位，不把不同库/场次优势拼成一个已验候选。新库没有增加model结构或运行堆scratch。

复现时沿用[首阶段](2026-10-23-memory-rom-tiers.md)的`$py`与线程环境，输出目录必须不存在：

```powershell
& $py -X utf8 scripts/build_memory_rom_andn.py --base-build <第一阶段build绝对路径> --output artifacts/new-memory-andn-build
& $py -X utf8 scripts/study_memory_rom.py verify --library artifacts/new-memory-andn-build/jshc_memory_rom.dll --roms <第一阶段ROM目录> --data-root <原模型根目录> --output artifacts/new-memory-andn-full
& $py -X utf8 scripts/verify_memory_rom_contract.py --library artifacts/new-memory-andn-build/jshc_memory_rom.dll --roms <第一阶段ROM目录> --output artifacts/new-memory-andn-contract
& $py -X utf8 scripts/bench_memory_rom_andn.py --build <新build绝对路径> --roms <第一阶段ROM目录> --ref80 <同源80绝对路径> --data-root <原模型根目录> --output artifacts/new-memory-andn-perf
```

[证据包](../../report/data/p16-memory-andn-v3/README.md)保存生成源、库、全部四worker数组、RSS和A/A失败限定。归档前两次因相对路径转ZIP成员失败，未重跑数值或计时；规范化绝对路径后仅重做归档，两个失败中间目录保持未提交。后续固定8像素C99批读取另作独立阶段，没有混入本次库或数据。没有新的官方Threshold、Skylake或ARM实板成绩。
