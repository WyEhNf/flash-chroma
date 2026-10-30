# 修订78的发射槽及队列资源诊断

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23达到三倍吞吐；Status：In Progress。本阶段只诊断既有78，不新增或重测吞吐验收，整体目标尚未完成。分支从Draft [PR #71](https://github.com/WyEhNf/flash-chroma/pull/71)头`92d6b1ab54eb7d978f0c030d24a3142cad7a28a7`继续，源码、模型、直表及78运行时不改。

此前六事件只能观察加载等待，不能区分发射资源。新增[事件支持](../../scripts/zen4_dispatch_pmu_support.py)、[可调度性探测](../../scripts/probe_skylake_dispatch_pmu.py)和[逐TID诊断](../../scripts/diagnose_skylake_dispatch_linux.py)，使用两个各6项的pinned事件组：

| 组 | 事件及raw config | 单位 |
| --- | --- | --- |
| A | cycles `76`、instructions `c0` | 周期、退休指令 |
| A | frontend `1000001a0`、backend `100001ea0` | 空/受阻派发槽，除同组`6×cycles` |
| A | LQ `2ae`、SQ `4ae` | token导致派发受阻周期 |
| B | cycles `76`、整数PRF `1ae`、retire token `20af` | 各自周期 |
| B | 整数调度队列并集 `01000faf` | `AF/0f,CMASK=1`，每周期最多记1 |
| B | 最老op未完成 `2d6`、其中等load `a2d6` | 无退休的等待周期，后者为前者子集 |

编码使用64位config，扩展Event位35:32与CMASK位31:24分离。依据[Linux v6.18事件](https://raw.githubusercontent.com/torvalds/linux/v6.18/tools/perf/pmu-events/arch/x86/amdzen4/other.json)、[退休事件](https://raw.githubusercontent.com/torvalds/linux/v6.18/tools/perf/pmu-events/arch/x86/amdzen4/core.json)、[槽位公式](https://raw.githubusercontent.com/torvalds/linux/v6.18/tools/perf/pmu-events/arch/x86/amdzen4/pipeline.json)及[AMD PPR 56713 Rev3.05](https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/programmer-references/56713-B1_3_05.zip)第216—217、272、275页。1A0的01/1e是枚举，不OR；AF低4位是可组合原因位，CMASK=1按至少一个原因去除同周期多次计数。各阻塞原因可重叠，不相加；调度队列受阻不是利用率，整数PRF不覆盖SIMD资源。

实际环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu Linux6.18.33.2、GCC15.2构建的既有78、Python3.14.4标准库；限定CPU family25/model97及CPU0/2/4/6。事件不适用于Skylake。两个新事件组各一次Python工作探测通过，enabled/running均完整、基础计数和单位范围通过，未加载候选库；可调度不代表宿主已校准全部虚拟PMU语义，零事件不能自动证明没有瓶颈。

冻结[v2协议](../../experiments/skylake-dispatch-diagnostic-v2.json)，SHA`7549c82eae9dc5821352dd9043977c6b886931c57538789072da0b034c842865`。照片1/4、灰色4/1四案例分别按AB/BA/BA/AB组顺序展开8项，各一次预热、一次计数，共16次apply。只用一句柄，前后核对实际ANDN、16MiB精确VMA/全THP、输出/源/保护区及团队/TID绑定。各TID保存72字节原始组读数，全部断言前落盘；按1200个连续static块推定名义像素数，不是线程内部计量。包含OpenMP调度、barrier、收尾自旋及Python启停边界，不能分离为纯像素循环。

v1和诊断初版在执行前的独立复核发现失败留证缺口：原生返回后disable失败会少记调用，后面TID读取失败可能丢前面读数，清理异常可能掩盖原始错误。旧源码、未执行v1和审计说明按原字节保存；v2在返回后立即内存登记，正常先全部disable再IO，逐TID读取后保存，清理错误另记。支持源和已验probe没改，没有重复探测或候选计数。

复现先恢复既有78的冻结源、构建、完整域、静态v2、固定模型及大流，使用新目录，不覆盖原件：

```sh
python3 scripts/probe_skylake_dispatch_pmu.py --output artifacts/skylake-dispatch-diagnostic-probe-v1/results.json
python3 scripts/diagnose_skylake_dispatch_linux.py --policy experiments/skylake-dispatch-diagnostic-v2.json --output artifacts/skylake-dispatch-diagnostic-v1
```

执行结果通过：8次预热、8次计数，新增wallclock验收0次。8项输出SHA、源与保护区、1/4实际团队及CPU0/2/4/6绑定、前后16MiB全THP均通过，各参与TID running/enabled=1。完整RGB8精度沿用PR71已冻结证明，本轮仅有照片及固定灰色的输出校验，不能冒称重新执行全域。

| 负载/线程 | A周期/名义像素 | FE空槽 | BE受阻槽 | LQ受阻周期 | SQ受阻周期 | B周期/名义像素 | 最老load未完成 | retire token受阻 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 照片1 | 3.037135 | 0.8418% | 76.8163% | 71.1115% | 0.00137% | 3.069969 | 57.7912% | 0.3323% |
| 照片4 | 3.925479 | 2.4253% | 78.9969% | 72.9366% | 0.00126% | 4.085005 | 65.4601% | 0.2560% |
| 灰色4 | 2.682598 | 1.1133% | 72.8510% | 27.3892% | 0.02902% | 2.634122 | 15.6568% | 38.0615% |
| 灰色1 | 1.287710 | 0.2259% | 47.9912% | 34.3898% | 0.00208% | 1.289786 | 5.3634% | 1.5955% |

照片B组整数PRF为0.00154%/0.00243%，整数scheduler并集0.02384%/0.03554%。原始逐TID值保留，表中是参与者求和后以同组sum(cycles)归一；四线程周期/像素是各TID周期总和/总像素，不能当作墙钟或与单线程直接相除求吞吐。A/B分别调用，表格并列不把它们当成同一时刻的因果分解。灰色4线程retire token高于1线程，含调度/barrier/自旋，不能据此归因为store或照片的同一瓶颈。

有限推论：照片的前端空槽比例低而LQ受阻较高，支持尝试用额外拆位算术换取更少输入load指令。拟研究每两像素一次mem64 ANDN，只减少输入加载指令，不减少16MiB表、ID/palette随机加载或源DRAM字节，也未证明输入load是LQ占用主因。每对额外MOV/AND24/SHR可能增加整数执行、依赖和寄存器压力，必须先审计静态形态、spill、四ID先行和先读后写；不以本轮计数宣称方案提速。

[完整档案](../../report/data/skylake-dispatch-diagnostic-v1/README.md)保留raw/probe/未执行v1及失败留证修正/独立审计；未重试或挑选样本。源码和模型未改，本阶段不修改系统权限、频率、大页或安全设置，不宣称Skylake实测、根因已被证明或三倍达标。

独立离线审计通过32份raw（20参与/12旁观）、91个源码ZIP项、18份表页状态、9份空闲回执及8+8调用数，回执SHA `788f7de92f13d8e10cf1f0051fdd5358a17c9a5cc81c591e994e396cf4e08c20`。首次审计把WSL绝对路径与仓库相对路径直接比较而误报，旧脚本及失败回执保留；仅规范化路径并核对库SHA后复算，无原生重测。归档56份原件清单及依赖/源码SHA通过；提交前65份实验/脚本/档案暂存blob与磁盘逐字节一致、Python语法与空白检查通过。该交付检查在Windows11/Python3.13.12标准库执行，不新增Linux像素或计时。

协作检查：重新fetch GitHub，完整读取65份PR正文与前阶段64份逐项比较，仅新增71，其余内容完全一致；71正文、全部评论、review与行内线程已刷新，后三者均空。读取issue7/8最新正文及全部评论，7修复337a3dd已入main，8双C99已集成但接口/预算/实板继续跟踪。main b19c5a0及337a3dd/876e15b8/397cc367均包含在当前分支。Discussion接口仍不可读取，不能视为无新问题；本次仅Draft诊断交付，不合并或关闭事项。整体三倍、官方派生表许可/预算/Threshold及真实Skylake继续待验证。
