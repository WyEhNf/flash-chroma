# 完整域实际颜色重编号与9/10bit精确表：只读必要普查

Agent：`/root`，Operator：本会话用户。状态：新静态方案，尚未冻结或执行。它不替代即将执行的293/294正式性能，也不修改旧u16、RGB24、哨兵或Gbank负例。

## 原因与边界

293的max41整体缓存包含613个精确RGB32值，但其中一部分可能不被任何RGB8原输入命中。613不能直接证明完整域需要10bit，也不能从照片颜色数作精确表减项。旧max_first/p99_first的纯模型全域普查已经区分实际颜色数与whole-cache颜色数；新方案只为此前未覆盖的max41导出实际逻辑ID频数，并完整保留所有16,777,216输入，不读取gold、照片或官方源表，不采样或近似颜色。

## 固定一次普查

唯一模型为已完整质量通过的max41，唯一运行时为293 DLL `f70f0e6ac98c753c15496e23fe1c2684dec04b6c0cdec47539d83e6df67c51a5`。执行前以SHA绑定217源/29输入的已有完整质量冻结及独立质量结果；本次重新核验实际使用的源、模型、DLL与四依赖，不重新读取历史照片/输出流来复核其字节。一个fresh进程只prepare该模型一次，实际核cache/domain/wide启用、uint16格式和容量；只读导出完整physical IDs（R最快顺序、排除4B guard）和sorted RGB32 palette，并核原质量记录的物理表SHA。没有native apply或计时调用。

NumPy uint64频数和独立分块Python Counter分别核全部16M ID、颜色频数及总数。实际命中色依RGB32升序稳定重编号，不按频数、图片或gold取前缀，不丢任何低频色。若实际颜色≤512选9bit，否则≤1024选10bit，否则本方案STOP；不再扫描其它宽度。已有8bit成功的best优先路径不变，本普查不重构best或声称免费prepare。

## 精确位表示与有限合同

逻辑紧密payload为`N*bits/8`（N=2^24），末尾额外4B owned zero guard。9bit地址为`byte=code+(code>>3)`、`shift=code&7`；10bit为`byte=code+(code>>2)`、`shift=2*(code&3)`。一次4B无对齐读取、右移并mask得到精确ID，再读RGB32 palette。位流只涉及非负整数，跨byte/4B/缓存行/末地址完整定义；C/C++实现若随后获准必须使用memcpy/loadu避免别名与对齐未定义行为，不把Python位表示通过冒充native合同。

先对bits9/10、全0/全最大/交替/递增固定模式、长度0..33及63/64/65/255/256/257/65535/65536/65537，以独立逐bit Python打包/读取核生产向量布局、4B读取和guard。最大byte地址及4B范围用Python真整数单独证明。真实16M紧密表随后完整解码，逐ID和RGB32与旧uint16表相等；完整重编号频数由独立Counter核。没有新拟合、新精度或速度档。

## 成本账单和停止

候选9bit payload18,874,368B或10bit20,971,520B，另有4B guard及实际palette。普查同时保留native原32MiB表、32MiB导出副本、重编号compact额外32MiB、packed表、频数和分块暂态，不能称native峰值节省；未来运行时若需先造32MiB临时u16再压缩，必须计入prepare时间和峰，不能借本离线表免费部署。旧289 whole-cache固定10bit已有有效低于50%的负例；本次离线重编号不能恢复它的速度资格，若仍需10bit不能以改ID名称作为重做相同native路线的理由。暂不实现AVX512、特殊页、prefetch、native SIMD或自动完整照片/性能。

输出使用独立新目录，先源/输入冻结，再唯一run；首身份/格式/有限/解码错误保存STOP，不覆写原件。后续只有实际color count和位合同通过才另静态讨论一个固定native packed实现；正式构建、native质量、三分母冷热50%和fresh RSS均需独立预注册。本阶段不能授任何速度/可移植性收益。
