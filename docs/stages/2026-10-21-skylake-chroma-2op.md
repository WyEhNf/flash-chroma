# 两指令通道差索引：指令减少但周期未改善

**相对修订23的整体三倍吞吐仍未完成。** 目前唯一有效完整墙钟候选40的纯映射单/四线程吞吐为2.6444/3.1200倍，真实输出3.3066/4.3069倍。本阶段61在事前周期筛查失败，没有新增墙钟成绩。

本阶段从[Draft PR #58](https://github.com/WyEhNf/flash-chroma/pull/58)的`226a0c49982ee61b6f372c082e408e79560ea9f8`开分支`codex/skylake-chroma-2op-20261021`。60的输入展开把24字节RGB转换为8个`[R,G,B,0]`，随后移位、逐字节减法、掩码形成`[R,G-R,B-G,0]`。61只把展开结果变为`[R,G,B,B]`，于是逐字节减法的最高字节为`B-B=0`，删除`VPAND`和常量掩码；CMake目标、修订号和诊断格式分别为`jshc_skylake_chroma_2op`、61、19。表的实际SHA与60完全相同：`724157d16331a4ad0a917e25fb4f613ddb16a193809a692bb9eb774b5f557833`。原模型、整数插值/舍入、公共默认、单级/未获证回退和只读`AGENTS.md`未改。

实际环境为Ryzen9 8945HX、Windows11宿主、WSL2 Ubuntu Linux6.18.33.2、GCC15.2、Python3.14.4。Release SIMD翻译单元使用`-mavx2 -mtune=skylake -ffp-contract=off`；无AVX-512、PEXT、gather、fast-math。实汇编候选对象静态指令数由60的1794降至61的1757，原参考回退对象字节相同；该数字不是动态周期或吞吐结论。

[冻结构建计划](../../experiments/skylake-chroma-2op-v1.json)在首次构建前记录源码SHA、唯一改动与正确性合同。独立表读取全部16,777,216色与已验逐级整数输出流逐字节相同；原地与分离输出共24组完整RGB8 API配置通过。有限原地2208、分离/别名4416、保护页736、全部目标对齐1280、API拒绝44及直表拒绝9组通过，零字节/哨兵差异。实际16MiB直表在本机完整THP覆盖；固定模型精度不下降，没有重新拟合。

在首次计数前另冻结[同场策略](../../experiments/skylake-chroma-2op-pmu-v1.json)：相对40，单线程周期比≤0.95且四线程≤1.05才进入整轮墙钟。100张已见1024×768 RGB8照片，每角色/线程各一次预热、一次计数，输出SHA相同；计数running/enabled均≥0.99。

| 同场40→61 | 周期/像素 | 指令/像素 | 通用cache miss/像素 | 周期比 |
| --- | ---: | ---: | ---: | ---: |
| 1线程 | 3.00724→3.04899 | 5.40104→5.40474 | 0.10068→0.06333 | **1.013883** |
| 4线程合计 | 3.99914→4.12497 | 5.44405→5.46482 | 0.11688→0.08645 | 1.031462 |

61虽然减少静态指令和通用miss，单线程周期增加约1.39%，筛查失败。40在不同计数场次的绝对周期明显不同，不能跨场次拿60的3.24477与61的3.04899相除宣称61较快；只看各自同场比。按冻结规则停止，不重计挑选、不运行整轮墙钟。通用cache事件不代表某个确定缓存级；WSL来宾vCPU绑定不保证宿主物理核固定，未测试真正Skylake。

[原始档案](../../report/data/skylake-chroma-2op-v1/README.md)保存测量源码、二进制、汇编、完整域和计数。依赖原模型、照片及首级oracle流以两个冻结JSON内SHA识别；复现应在新目录顺序运行`scripts/build_skylake_runtime.py`、`scripts/inspect_skylake_chroma_2op.py`、`scripts/verify_skylake_chroma_2op_linux.py`和`scripts/profile_skylake_chroma_2op_pmu.py`，参数接口沿用[上一阶段复现说明](2026-10-21-skylake-chroma-delta.md)。本分支只交付Draft研究，不合并或关闭[issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)；派生表许可、资源预算、官方Threshold和实板仍待确认。
