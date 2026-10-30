# 历史研究策略向当前赛事交付的迁移审计

Agent：Codex `/root`、`framework_strategy`、`framework_contract`、`history_storage_audit`；Operator：本会话项目用户；日期：2026-10-30；状态：静态审计完成，整合缺口待开发。本阶段只新增报告与核验材料，生产代码、拟合模型、交付 hpp/EXE 和既有计时原件均未改变。

## 结论与范围

**没有应用历史研究中所有有价值的策略。** 当前已形成可运行、可回退的通用赛事基线，RGB24 的主要热路径优化也已补齐；精度模型生成、连续参数入口及低内存所有权仍未完整整合。应分别记录“当前已执行”“库中存在但本模型未触发”“框架未接入”“仅有条件正例”和“历史失败或当前规则不适用”，不能用函数存在代替实际命中，也不能把旧 Cinema 模型收益直接授予新 LUT。

审计固定于 `111b0dfd73edd68927642c8dafca69b516285737`（PR #99 头），实际性能配置为四级 m33、FrameworkStep 网格、chain_ls、DirectRGB24、AVX2、算法单线程。建立了 262 份阶段 Markdown、255 份 report Markdown 条目的标题/哈希索引及 89 个远端分支索引；其中包含归档副本，**不是 517 项独立研究，也不是全部逐字复读或逐项重跑**。随后围绕精度、热执行、准备、存储、参数和部署逐项比对关键历史报告、当前调用链及冻结回执。非祖先分支不等于遗漏实现，还检查了新的可分离校准、流水专门化与官方框架测试研究。

完整账本：[精度](../../report/strategy-audit-20261030/precision.md)、[执行与准备](../../report/strategy-audit-20261030/runtime-prepare.md)、[内存与部署](../../report/strategy-audit-20261030/storage-deployment.md)；[索引](../../report/strategy-audit-20261030/inventory.json)、[实物身份](../../report/strategy-audit-20261030/delivery-check.json)。

## 策略状态与优先级

优先级表示后续整合顺序，不授予新候选性能或精度资格。

| 方向 | 当前状态 | 缺口、条件与影响 |
| --- | --- | --- |
| Q16 四面体、逐级 RGB8 舍入、Scalar/AVX2、四级融合 | 已应用 | 保留数值合同和通用回退；Direct 表是该模型的等价执行缓存。 |
| RGB24 独立八路查表、64 像素打包、输入预取、65536 分块、安全尾部 | 已应用且当前执行 | PR #99 已有相同模型/单线程的受控新旧核比较；本轮不重复授予历史百分比。默认普通写，NT 仍为显式候选。 |
| 两种固定网格、完整域独立 LS、真实到达→整链 gold 的末层 LS | 已应用 | chain_ls 固定前三层；最终完整域 mean/SSE 双门控已存在，但不是全链离散优化或尾部全面保护。 |
| LUT 曲率/DP 非均匀轴 | **P1：框架未接入** | Python 有 LUT-only 方法，当前入口只有 uniform/framework。可先接三轴生成再复用现有恢复器；新表仍需对照验收。 |
| 真实 Q16/RGB8 终点整数节点搜索、前/中层联合支撑与后缀重放 | **P1：仅部分思想迁入** | 当前 integer_sweeps 优化未舍入二次代理；没有真实欧氏距离指导的 ±1/RGB 联合搜索，前三层也不会调整。末层 LS 不能消除所有前缀信息碰撞。 |
| 分输出坐标 sidecar、坐标校准 | **P1 候选：底层有，框架未接入** | hpp 支持 9216B 分输出分数表，adapter 不生成或传入；768B 精确曲线是另一能力。须保留结构证明和表示许可边界。 |
| p99/max/CVaR、固定锚点保护 | **P1：框架未接入** | 现有 mean/SSE 接受不能保证尾部不退。应作明确质量档/约束，不能把全部旧硬约束无条件设为默认。 |
| 每级 mixed m、连续 A/B/C 偏好与硬预算 | **P1：执行能力有，自动入口不完整** | 混合 m 可手填；fc::select、Preference/HardLimits 已在头中，赛事 main 没调用，CLI 没暴露连续权重和预算。需要本轮 LUT/机器绑定的候选表，不能直接用旧 Cinema 目录。连续的是偏好域，输出仍为合格的离散模型/执行计划。 |
| RGB24 双像素 u64 输入、BMI ANDN | **P2：RGB24 未迁入，收益待测** | pair48/BMI 已在 U8/U16；RGB24 主循环仍 8×u32，3×u64 只用于精确尾部。值得独立 A/B，历史没有隔离证明它会让当前 RGB24 再变快。 |
| 首级小域精确后缀缓存、100 扫描线准备 | 库中已有，当前未触发 | 冻结首级需要 66,846,976 槽，超过 524,288 槽上限，合法回退到通用 sparse8 全域建表。不可强开约 255MiB 缓存来宣称优化。 |
| 通用扫描线准备、四级共享性编译期专门化、adapter 免重复清零 | **P2：尚未完整迁入** | 当前无脱离小域条件的扫描线后备；无固定四级共享模式模板；adapter vector 会先清零约 49MiB arena。对 Direct 主要影响准备/首次输出，不等于官方热 TimeCost。专门化也有历史失败场，须同场测。 |
| 小域后缀作为低内存热表示 | 有历史条件正例，当前无独立表示 | 现库仅用于 direct 准备缓存；未来压色 LUT 可重新评估，当前首级不满足条件。 |
| 对象精确共享、去包装节点副本、owned compact sparse | **P2：框架未接入** | 当前 Stage blob、out.data、packed 暂态共存；冻结最终 stage2/3 完整 SHA 相同，仍各持一份。可按拟合后完整对象去重，不能直接假定新正式表重复或清空被借用的源。 |
| 只读预生成表、RGB24 sparse、P4/精确块 | 有条件内存候选，当前未接入 | 旧模型部分方案有容量收益，也有显著吞吐损失或控制失败；应作内存优先档，不能代替当前快档。 |
| 单 hpp 与端侧开关 | 核心具备，框架交付边界需分清 | 当前主机交付确实一个聚合 hpp；它含 vector/ifstream/拟合/异常，不是裸机零堆头。独立 core.hpp/C99.h、端侧宏可用于另建端侧交付；没有移动 ARM NEON 或真实板上性能资格。 |

## 不应为了“全用上”而加入默认的策略

- 比赛要求单线程 CPU，历史四线程、GPU/NPU 路线不适用。来自图片的频数、质量权重和训练损失不能进入新框架压缩；完整 RGB 域经 LUT 推导的到达频数与图片频数应分清。
- 373a、max_first、max41 是固定 Cinema 成品，不能复制为新四表模型。其机制须改成通用 LUT-only 方法后重新验收；旧误差、压缩率和百分比不继承。
- AVX-512、本机失败的字典/降位/地址布局、增加预取、stage-major 等都有负例或缺少资格，不属于“已证明通用有效、只差开关”。prefix-split 曾有单线程约 4.34% 正例，但原条件为非共享首级，当前全 shared 且 RGB24 热循环不跑 tetra。
- tri/tetra matched、箱约束、IRLS/minimax 等存在精度负例或原生部署缺口，保留为显式研究候选。连续 SSE 改善不保证真实 RGB8 mean 改善，mean 改善也不保证 max/CVaR 或每张照片改善。
- 额外检查的[10-23 固定流水专门化](https://github.com/WyEhNf/flash-chroma/blob/d0fc98ed680c6c2d41e3e3ff2d4377c5802d2bf1/report/data/pipeline-specialization-20261023/report.md)两轮统一门槛未通过，且是 Numba/TBB4T，不是原生 AVX2 证据。[68 LUT 可分离校准](https://github.com/WyEhNf/flash-chroma/blob/e8d15af36f687c11fae06bdfb34ea6a9b6cbd09c/report/data/pr42-separable-20261021/report.md)只有 19/136 设置获得完整域零误差，7 个可分离设置仍回退，不能推广为所有表可精确校准。

## 现场配置必须显式说明

实际交付 `run.ps1` 默认 `sample / uniform / auto`；`auto` 在此是结构/后端选择，并非连续 ABC 最优器。生成 README 的 chain_ls 示例也漏写 `-Grid framework`，因此不能用该简写复现已验证配置。本次审计未改交付包或重编译，先在报告给出完整命令：

```powershell
Set-Location 'F:/Hackathon/极速焕彩测试框架/FlashChroma'
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Backend avx2 -Grid framework -Fit chain_ls
```

该命令会按脚本重新编译并运行；不是本次静态审计实际执行的命令。更改网格/拟合会更改模型身份，不能沿用另一配置的误差回执。

## 身份、验证与协作记录

| 对象 | SHA256 |
| --- | --- |
| include/flash_chroma.hpp | 9e5fa9ac474c6f9f60c05c19ad859353bf9b6fe88983cc01c3bee21cf1e11953 |
| 实物 flash_chroma_framework.hpp | f28d672c46a13180516741ff181d32414770ef331700cec8354bdb204473bb31 |
| 实物 main_flash_chroma.exe | b363723be4d64073b9a8e1369e8268b59985293a22711b72b900b658f9be7c47 |

审计环境为 Windows11 26200 x64 / Ryzen9 8945HX / PowerShell / Python3.12.14。只做源码/分支检索、少量冻结模型解析、来源清单/实物 SHA 和 Markdown 链接核验；没有编译，没有新增完整域正确性、拟合、照片或性能测试。已确认实物只有一个 hpp，无私有工程 include，5 个交付源/配置匹配清单，EXE 匹配回执，core 匹配工作树；执行验证见下方命令和[静态回执](../../report/strategy-audit-20261030/verification.json)。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' -X utf8 report/strategy-audit-20261030/verify.py
```

PR #99 的对应提交六项 CI 均 success：[默认/Scalar/Docker](https://github.com/WyEhNf/flash-chroma/actions/runs/40921847192)、[三类 QEMU](https://github.com/WyEhNf/flash-chroma/actions/runs/40921847210)。这是既有源码 CI 的结果，不是本审计新增实板、精度或性能证明。

创建审计 PR 前 fetch 并刷新 #95/#96/#98/#99 正文、完整评论/reviews/行内线程，均无新增意见；检索 10-28 后相关 PR，读取 #96 的版本化 review，刷新 issues #7/#8 全文与完整评论。记录见[协作快照](../../report/strategy-audit-20261030/collaboration.json)。#7 的历史修复 337a3dd/876e15b8/397cc367 仍在基线祖先中；#96 两项旧验证编排/目录证据绑定 P2 仍未修复，不把新框架绕开旧路径称作修复；#8 接口决策/实板仍待完成。Discussion4 沿用接口不可读取的缺口，不据此作可合并结论。本阶段不合并、不关闭事项，审计 PR 保持 Draft。

主要文件为本文、三份专项账本及 report/strategy-audit-20261030 的索引/身份/协作/核验材料，对应提交见本阶段 PR 的提交记录。基础实现与归档提交为 be11fc9/111b0df；本审计不改它们。

## 后续开发顺序与未完成事项

先补精度生成和可观测入口：LUT-only 曲率/DP、真实整数终点后优化、尾部保护，以及连续偏好/预算 CLI 和实际准备路径诊断。再扩展前/中层联合优化、许可明确的 sidecar 和混合容量搜索。热速度侧独立评估 RGB24 pair48；准备侧评估免清零/通用扫描线；内存侧按目标预算做精确去重与 compact 模式。

每一项应冻结当前已验证版作对照，先验证数值/来源/边界，再在相同模型、机器和计时范围下测收益。不能把这些候选相乘为预计总提速。正式阈值、服务器、额外 Direct 缓存许可、规定 GCC13.2 与实际端设备仍未验收。本阶段完成的是缺口审计，不是这些缺口的开发或“历史最优已全部集成”的验收。
