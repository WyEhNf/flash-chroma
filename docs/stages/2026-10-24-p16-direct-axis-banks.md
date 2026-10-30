# max41均匀轴分bank：24种完整域表示均被拒绝

Agent：Codex `/root/axis_delivery`；Operator：本会话用户；任务：第16题精度分支的精确8位表示普查交付。状态：数学普查和独立重放已完成，没有生成新native候选，不改变默认版本。对应提交为包含本说明、两份执行源、冻结提案和阶段证据目录的中文阶段提交；实际Git对象与ZIP完整性以独立审计回执为准。

## 结果与停止范围

在已认证max41完整物理uint16表上，固定输入R/G/B三个轴，各检查2、4、8、16、32、64、128、256个等宽bank，共24种配置。每bank最多256个精确RGB32颜色才允许8位ID；本次24种配置全部存在超界bank，确定选择结果为`None`，严格停止。没有导出新的8位ID表或bank palette，没有候选容量值、native prepare/apply、拟合、照片或性能采样。

| 输入轴 | 2 bank | 4 | 8 | 16 | 32 | 64 | 128 | 256 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R，各配置最大发色数 | 311 | 309 | 303 | 294 | 294 | 294 | 294 | 292 |
| G，各配置最大发色数 | 334 | 331 | 320 | 310 | 304 | 297 | 297 | 296 |
| B，各配置最大发色数 | 333 | 326 | 312 | 303 | 298 | 295 | 289 | 287 |

即使单轴细分到完整256坐标，最大bank仍分别有292、296、287色。每个失败配置保留首个超界bank、其中257种RGB及各色最小物理输入见证。这个结论只拒绝本模型的24种均匀单轴方案，不证明任意多轴、不等宽、树结构或所有8位表示都不可行；本阶段没有继续扫描这些新分区。

旧`gbank8`名称中的8表示8位ID，实际方案是输入G的256个bank。其旧三模型的失败及max41当时因1MiB cache资格不足的前置停止保持。此次max41基于已验证293导出的完整物理表，补上的是此前缺失的这个固定模型的轴色集，不恢复旧方案或旧289固定10位的速度资格。

## 数据、算法与独立覆盖

物理输入顺序固定为`c=R|(G<<8)|(B<<16)`。原表16,777,216个uint16 ID指向613个whole-cache颜色，其中完整原输入实际命中344色。按实际RGB值去重、升序映射，不能把不同旧ID误当不同颜色；活动色与原9位表示沿同一冻结身份。

主路径一次完整扫原ID，为三个轴的每个0..255坐标和每种活动色保存最小输入见证，形成3×256×344个uint32格、有效载荷1,056,768B。均匀粗bank由连续坐标格的逐色最小值归并得到，24配置不各自重复扫16M。先固定最少bank数、再R/G/B顺序的选择规则，本次因全部拒绝而没有进入选中表的编码/解码。

独立路径不导入主枚举、选择函数、NumPy或native模块，以标准库`struct`逐原ID读取、Python整数位址及三个轴的字典/最小见证重建完整矩阵；核全部264,192格、24配置、逐bank色数、全部首溢见证、活动频数和`selected=None`。主、独立各扫描16,777,216个逻辑表项，合计33,554,432；选中表解码为0。这个计数不包含身份SHA、序列化或OS页行为，不能称全部I/O或性能数据。

新有限合同包含4个主例：三个轴位址边界、同RGB异旧ID、恰256色、257色；另有8种owned-guard长度、合法ID255、人工全部24配置拒绝/选择为空的配置夹具，以及palette257色和编码ID256/65535的3项显式拒绝。人工presence矩阵只是配置逻辑夹具，不冒充真实RGB模型。主有限合同与完整独立重放全部通过，不以它们代替未实现的native安全合同。

本轮实际读取7项上游证据：9位阶段的frozen/results/independent JSON和四份二进制表。上游223源/13输入仅作为冻结谱系绑定，未在本轮重新加载293 DLL、模型、gold、oracle或照片，也没有重跑历史native质量。归档另核这些实际7项的既有SHA/长度，不把谱系数量写成本轮执行源数。

## 环境、复现与身份

实际环境为Windows11 x64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、psutil5.9.0、little-endian；主路径使用NumPy和Python，独立路径为纯标准库。此次没有编译器、AVX或OMP像素后端；不从普查进程行为推断任何native吞吐或跨平台性能。原件记录时刻的working set/peak working set为79,052,800B，PrivateUsage为30,801,920B，均含Python、映射和离线暂态，不能作部署RAM或prepare峰节省。

已有正式输出目录拒绝覆盖。原路径/身份快照下，唯一执行序列为`python scripts/census_direct_axis_banks.py freeze`、同脚本`contract`、同脚本`run`，再`python scripts/audit_direct_axis_banks.py --output artifacts/p16-direct-axis-banks-v1/independent.json`。跨路径或已有目录重放须新建明确机械版本并重新冻结，不能修改已执行源后覆盖本版。发布归档由`archive_direct_axis_banks.py`封存已有证据，Git核由`audit_direct_axis_banks_git.py --git-ref :|HEAD --output <新回执>`执行，不重新计算数值或调用native。

| 原件 | SHA256 |
| --- | --- |
| frozen | 081efe0a94ed789dc970b2804e1015f4f1a74178676b60532548c4467875194d |
| contract | fdac4ec9d65792026cd4da734de863d7e0b9ecc3db193b304527cb868fb9f7cf |
| first-input-u32.bin | a8fa7d0bfb1cbbb1b8efeba6bde77a7edf00d6befb82ed642e422fbf0dbfd33e |
| active-colors-u32.bin | e3a91175bf850756330c4a9d221dddb2ea05d315e50a61f1d323981360e0a224 |
| results | 61fde9e61595260cc5b5c954ff32a0d1313193b5603240cbb8243aca4155601b |
| independent | 7eff395b9159dee0be981ed67140dfd718b2a62e2e64a613db59337c49561078 |

阶段目录`report/data/p16-direct-axis-banks-20261024`的source ZIP只含3份执行源/提案和3份交付源/说明；raw ZIP保存本轮7份原件与7份实际上游输入。两ZIP逐成员核字节SHA、长度和CRC；Git index/HEAD再核原字节与引用关系，CRLF原件不得归一化。这个交付只证明可表示性负例与证据完整性，没有取得任何新的精度/速度档，原36格矩阵和合格方案不变。
