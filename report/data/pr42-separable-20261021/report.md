# PR #42 在68个LUT中的可分离LUT测试

### 阶段 A：校准覆盖范围

|设置|精确校准成功|可分离但需回退|非可分离，继续通用方法|
|---|---:|---:|---:|
|17³|10|3|55|
|33³|9|4|55|

13/68 个源通过严格完整 RGB8 色域可分离检测（19.1%）；19/26 个可分离设置可校准（73.1%），占全部 136 个设置的 14.0%。19 份成功模型实际展开完整 256³ 色域后，与冻结参考逐字节相同；不是仅凭图片抽样宣布零误差。其余 7 份可分离模型保留原恢复误差，26 份实测均与解析统计一致。

算法：保持 DP 网格、节点、单元索引和端点不变，求各输入码对应的 Q16 舍入可行区间，再施加单调性和最大偏移 4096（1/16 单元）约束。成功时只修改分数坐标查找表；失败返回原 DP 模型，不偷偷改节点或放宽约束。非可分离源不进入该校准。

|失败案例|设置|直接证据|后续方向|
|---|---|---|---|
|Cherry Champagne|17³、33³|蓝通道输入255目标240，固定末节点239，当前单元无法达到目标|拟合时固定真实端点或局部修正节点|
|Filmic 02|17³、33³|输入255目标193，末段节点均为192|端点约束优先，单改坐标无效|
|Filmic 05|33³|输入63需分数至少16384，超过允许4096|对偏移上限做消融，再考虑节点/坐标联合优化|
|Amber Haze|17³、33³|分别输入251/221需分数至少10923，超过允许4096|同上；不得称为不可表示的源|

### 阶段 A：100 张完整图片的代表验证

色差统一为 RGB8 欧氏距离 `sqrt(dR²+dG²+dB²)`，不是 CIE ΔE00。下表均值覆盖每张 1024×768 的全部像素；图像等尺寸，逐图均值平均等于全像素平均。

|LUT|设置|原 DP 图片均值|校准/回退后均值|后最大色差|状态|
|---|---|---:|---:|---:|---|
|Filmic sRGB 06 High Contrast|17³|0.125111|0.000000|0.000000|exact_monotone_calibrated|
|Filmic sRGB 06 High Contrast|33³|0.063911|0.000000|0.000000|exact_monotone_calibrated|
|Striped Purple - Emerald Malaise|17³|0.030829|0.000000|0.000000|exact_monotone_calibrated|
|Striped Purple - Emerald Malaise|33³|0.035075|0.000000|0.000000|exact_monotone_calibrated|
|Filmic sRGB 05 Medium High Contrast|17³|0.129552|0.000000|0.000000|exact_monotone_calibrated|
|Filmic sRGB 05 Medium High Contrast|33³|0.064727|0.064727|1.732051|structured_dp_fallback|
|Striped Purple - Amber Haze|17³|0.033148|0.033148|1.732051|structured_dp_fallback|
|Striped Purple - Amber Haze|33³|0.033444|0.033444|1.414214|structured_dp_fallback|

完整色域与实际图片分布权重不同，不能直接把二者均值作增减比较。全部 26 份可分离模型全域结果见 `evidence.zip 内 data/validation.json`；全部 136 个适用性判定与失败约束见 `evidence.zip 内 data/survey.json`。

Filmic 05 的17³成功而33³失败，不代表33³通常更差：两档重新选择的网格与拟合节点不同，固定节点后的可行域并不嵌套。33³在输入63处需要跨越至少1/4单元的分数坐标，而本轮仅允许1/16单元。需要将原模型误差大小和当前约束下是否能校准为零分别评价。


## 环境与验证范围

- 工作区源提交：`ac9e0ab555e4e36262f776d278b60bb53f9daf37`；隔离读取 PR #42 提交：`59586f7bd6dd248cf0b68bcbdff8e41cf95ac572`。未把 PR #42 合入当前 Luts 分支。
- 实际环境：Windows-11-10.0.26200-SP0；Intel(R) Core(TM) Ultra 5 125H；AMD64；Python 3.12.7 | packaged by Anaconda, Inc. | (main, Oct  4 2024, 13:17:27) [MSC v.1929 64 bit (AMD64)]。
- 依赖：`{"numpy": "1.26.4", "scipy": "1.15.2", "numba": "0.60.0", "llvmlite": "0.43.0", "Pillow": "10.4.0", "tifffile": "2023.4.12", "psutil": "5.9.0"}`。
- Numba LLVM CPU JIT，4 线程，线程层 `tbb`；float64、未启用 fastmath。OMP/MKL/OpenBLAS 环境设为1，不代表 Numba 仅1线程。未指定独立ISA目标，采用本机JIT默认目标；未执行C++/GPU/NEON/AVX原生内核性能验证。
- 完整性：核对 68 源 LUT、136 冻结 DP 模型、全部参考表、100 图片 SHA256；四级所选模型另外核对。输入哈希和环境见两个 run JSON。
- 阶段 A：26份可分离模型实际展开全部16,777,216输入颜色；与解析均值一致；19份零误差。四个代表源 × 两档 ×100图完整像素验证。非可分离55源只完成结构和回退判定，未重跑所有通用拟合。
- 这100张图已参与旧筛选，不是新的独立盲测集；不存在跨硬件加速结论。冻结完整参考由既有三线性源烘焙得到，结论依赖其RGB8契约。

本阶段只验证固定 DP 模型的坐标校准；55 个非可分离源保留原模型，未重新拟合全部136模型，没有新增单级性能结论。派生模型遵循原来源授权，来源与许可证保留在仓库 assets/LUT/sources 和素材 manifest，不宣称重新授权。

下一步优先处理 Cherry Champagne / Filmic02 的端点约束，再对 Amber Haze / Filmic05 做偏移上限消融；不能将19个成功设置推广为所有LUT零误差。

## 协作检查与本次提交范围

Agent：Codex；Operator：本会话授权提交的用户；Status：已完成本阶段实验和归档，待团队审查。分支基于 main `b19c5a0`；本次只发布研究代码与证据，不合入 PR #42 生产实现、不升级默认模型。对应提交以本 PR 正文实际 SHA 为准。

提交前检索全部现有 PR/issue 正文，重点读取 #5/#9/#12/#13/#14/#37/#38/#39/#41/#42 的完整评论、review 和行内意见，读取 #7/#8 正文及评论、Discussion #4 全文与评论，并检索后续原生性能 PR #43–#54 的相关主题。分页完整；#42 当前没有评论、review 或行内意见。

- [#9 基线及环境意见](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[#7 内核身份问题](https://github.com/WyEhNf/flash-chroma/issues/7)：修复 `337a3dd` 实际包含于本次主干基线；检查了尺寸选择与环境身份实现，历史验证为 [#12 审计](https://github.com/WyEhNf/flash-chroma/pull/12#issuecomment-6229792983) 和 [#37 集成验收](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。本阶段同尺寸配对、冻结输入并保留本机环境，不把静态检查当成重跑这些回归。
- [#5 色彩域意见](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072)、[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)：RGB 欧氏距离、源插值/舍入约定、数值压力链与实际摄影流程、正确性与近似精度分别说明。
- [#38](https://github.com/WyEhNf/flash-chroma/pull/38)、[#41](https://github.com/WyEhNf/flash-chroma/pull/41) 是冻结输入及诊断来源；[#42](https://github.com/WyEhNf/flash-chroma/pull/42) 仅采用固定提交 `59586f7` 的研究源码。不是对 #42 全部原生实现、一般三维模型或性能承诺的验收。
- [#8](https://github.com/WyEhNf/flash-chroma/issues/8) 的接口迁移、资源预算与实板仍未完成；官方数据/Threshold、独立新图和目标 C++ 性能仍待后续，不在本 PR 宣称解决。不合并 PR、不关闭 issue。

## 代码、证据与复现

`evidence.zip` 保存本阶段原始 JSON/日志及共同原始运行脚本；`manifest.json` 保存每个成员的 SHA256。原始脚本曾连续执行两部分实验，为保留真实代码身份，作为 provenance 保持字节不变；本 PR 的可读入口已按阶段拆开，另一阶段的数值结果不在此包。原始环境和脚本哈希不因提交时更改路径而改写。

独立入口只做路径/流程拆分，数值循环不变。本次发布做 AST/语法、原字节 SHA、汇总复算和归档完整性检查，没有为发布重跑完整色域、图片性能或全仓测试；实际数值和计时证据来自 2026-10-21 已审核实验。`delivery-check.json` 是发布静态检查回执，不能代替数值验证。

先在仓库根目录运行下列静态核查命令。若重跑实验，复制本目录到 `report/data/` 下新的同层目录，保留代码、使用空 data 输出；需本地旧研究 `artifacts/local-lut-study/20261016` 的同哈希模型/参考表、assets 图片/LUT及所列版本依赖。本包不包含这些大型历史输入，单独克隆本 PR 不足以完整复跑；禁止把新拟合模型冒充原输入。

`code/prepare_source.py` 从本地 Git 对象提取固定 PR42 Python 源到 `tmp/stage-a-pr42`，已有快照拒绝覆盖，需按原 run 哈希核验后复用。运行使用 Windows 11 / Python 3.12.7；PowerShell 可设置 `$env:PYTHONIOENCODING='utf-8'`。

`code/survey.py`：68源/136设置普查与校准；`code/validate.py`：26次全域及8组百图验证；`summary.csv`：136设置可读总表。

`code/prepare_source.py`：只读恢复固定研究源码；`code/verify_archive.py`：静态核对压缩成员、公开文件、计算函数与结果覆盖。`evidence.zip` 内的 JSON 保留所有逐图结果、实际环境和原始输入哈希。

静态核查：`python report/data/pr42-separable-20261021/code/verify_archive.py`。新的空输出目录中，准备固定源码后先运行 `code/survey.py`，再运行 `code/validate.py`。大规模复跑依赖上述历史输入；本次发布未重新测速。
