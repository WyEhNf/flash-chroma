Agent：Codex /root
Operator：本会话明确授权审查的用户
Task：PR #95 完整单一路线审查与跨 LUT 泛化测试
Status：审查及本机测试完成；两个 P2 缺口待修复，建议保持 Draft

审查固定于 `fb7e195215f14df9f635394d75cde0e0e69c82c9`。没有修改运行库，也没有执行合并。结论是：**本次覆盖内的运行时输出一致，但小调色板适用性、拟合精度和性能不能从 Cinema 单链直接推广；公开验证流程和部署证据绑定仍有缺口。**

### 两项待修复问题

1. **P2：公开验证器按 profile 名强制 U8/U16，容量不足会阻断可用模型的流程。** 新拟合 `fitted` 模型在 U16 超过 65,536 色时直接退出，`--all-representations` 也到不了 RGB24，且此前已完成的 Sparse 验证不写回执。avant-m33 已实际复现：Scalar/C99、AVX2 完整 RGB8 步骤完成，然后报 `10 调色板容量不足`、退出 1；独立测试中同模型 Sparse/RGB24 均正常。建议显式选择表示、记录容量不适用并继续支持的配置，保留成功记录；真正数值错误继续失败。benchmark 同样按既有 profile 白名单枚举 direct 路径，需同步检查。
2. **P2：bind_evidence 未核对目录误差、计时及 time_stable 与原始记录。** 使用原有 `default-direct_u8-avx2-1t` 原始证据（A/A=false、mean=0.695486159、batch_ms=46.6617），只在目录副本改成 time_stable=true、mean=0.01、worst_image_mean=0.02、batch_ms=0.001，再正常重选并计算新 selection 摘要，`max_error=0.03` 仍选中并通过 bind_selection、bind_model、bind_evidence。这是独立元数据夹具，不是实际错误目录图像运行，也没有修改原档案或发现历史造假。建议在继承质量/接受稳定性前复算并绑定原始证据，增加各指标失配拒绝与匹配正例。

### 跨链实测

固定 8 条链、25 个不同源 LUT，覆盖 cube/TIFF/3dl 和 5 个来源集合。链为 Cinema、Avant、Scenic、Cinema 逆序、Lomochrome→Classic Chrome→Tension→Filmic06、HDR2SDR→Provia→Arcade→Filmic04、Zoology、FilmSim。它们是数值压力组合，**未认证摄影输入/输出色彩域相容**。

- 16 套基础模型：每链全 17³/全 33³，公开 fit_candidate，uniform + sample_interp。
- 4 套补测：混合 17/25/33 大小、curvature 采样、两条困难链全 33³ curvature + ls_tetra_int。没有重训 373a/max_first，也没有四级联合调优。
- 每模型 65,536 个固定随机探针、C99 和独立 NumPy int64 四面体算术对照；基础另加 8 角点及原地短尾，补测另加 1,728 固定边界探针。oracle 算术独立，但读取相同已解析坐标表。
- 六张完整 1024×768 历史照片：kodim03/06、sony-034/041、DIV2K0801/0802，共 4,718,592 像素。
- 100 配置尝试：78 成功、22 合法容量拒绝；成功配置探针与照片 **0 字节差异**。
- Sparse Scalar、Sparse AVX2、RGB24 均 20/20 可用；U8 8/20、U16 10/20 可用。因此 Cinema 小 palette 的优势不能直接代表其他链。
- cinema-m33、mixed_hdr-m33 各遍历完整 16,777,216 RGB8 输入：Scalar/RGB24 无差异；相对稠密参考链完整域 mean/max 分别为 2.753518/16.186414、2.588994/145.013792。

误差为 RGB8 通道欧氏距离，**不是 CIEDE2000 或官方阈值成绩**。六图合并像素统计：

| 链 | 17³ mean | 33³ mean | 17³ max | 33³ max |
| --- | ---: | ---: | ---: | ---: |
| Cinema | 4.8141 | 2.8466 | 28.3019 | 16.1864 |
| Avant | 2.8991 | 1.8776 | 38.2230 | 27.3313 |
| Scenic | 1.5506 | 1.3654 | 5.3852 | 4.6904 |
| Cinema逆序 | 2.5755 | 1.8149 | 73.7631 | 47.6865 |
| mixed_tail | 3.6049 | 2.4580 | 92.4338 | 95.0474 |
| mixed_hdr | 5.0554 | 2.9286 | 150.0033 | 130.0000 |
| Zoology | 1.2304 | 0.6765 | 46.7654 | 24.2487 |
| FilmSim | 2.4069 | 1.8856 | 19.0526 | 13.3041 |

八链 mean/p99 都随 33³ 改善，但 mixed_tail 的 max 反而上升。全 33³ 曲率+整数最小二乘让 mixed_tail mean/max 达 2.0704/71.0704，mixed_hdr 达 2.4785/131；后者均值改善但 max 比均匀采样的 130 略差。同时改变网格与拟合方法，不能单独归因。

### 环境、证据与限制

实际本机：Windows11 26200 x64 / Intel Core Ultra5 125H / MinGW GCC8.1.0，C++17 -O3 -DNDEBUG -fopenmp、C99 -O3 -DNDEBUG；Python3.12.7、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、Pillow10.4.0。CPU-only，Sparse Scalar1T，其余AVX2 4T。DLL SHA256 `e6eebe25fa61a5500618a83a13b827fd7f13de9f0915ce9b7e9f210b9ba1c507`。会话直接从审查头编译，但没有项目标准链接回执，未把事后哈希冒充编译时回执。

相关 pytest **41/41通过**；原 `p16-header-performance-20261028` 证据审计通过（20配置、40点、19个A/A通过）。这不替代重新执行原 Ryzen 性能。新链仅记录预热后5次 apply 原样本，无绑核/锁频/随机化/A/A，故不发布稳定加速比。未验证 Xeon6140、实板、全部68个LUT组合、全照片保留集、所有模型全色域精度或官方Threshold。

完整报告见 [report.md](report.md)，原始计划/结果、全部计时、模型 manifest 和失败日志的版本化副本见 [evidence](evidence)。复现代码为仓库 `scripts/review_pr95_generalization.py`、`review_pr95_supplement.py`、`review_pr95_evidence_binding.py`；执行 `python scripts/archive_pr95_review.py --verify` 可只读复核归档 SHA、配置统计和全域直方图，不依赖本机 artifacts。DLL、稠密表及新模型二进制保留本地，可按报告命令重建。

协作检查：检查仓库完整 issue/PR 索引及空第二页，读取 #95/#94/#89 正文、完整评论/审查线程及 #43/#48/#62/#71/#73/#75 相关正文和意见，补读 #5/#9/#12/#37 的纠正记录及 [#7](https://github.com/WyEhNf/flash-chroma/issues/7)/[#8](https://github.com/WyEhNf/flash-chroma/issues/8) 全文/评论；发布前刷新 #95 无新提交/意见。#7 历史修复337a3dd仍在本头祖先中，本次是新部署目录绑定缺口，未把旧问题重新判为未修复；#8 的实板/接口决策继续保留。Discussion4接口无法读取，明确保留缺口，不执行合并或关闭。

下一步优先修复上述两个流程问题，再冻结更多链和独立照片集，根据可达色数/预算枚举表示并做同机受控 A/A；精度优化同时保护逐图 mean/p99/max，避免只优化均值。

## 发布状态

本意见以「补全#95的审查和测试」补充 PR 的版本化文件交付，目标为 #95 所在分支；不代表 APPROVE 或合并决定。两个代码位置分别是 scripts/verify_flash_chroma.py:63–69 和 scripts/run_flash_chroma.py:92–98，具体问题及修复建议见正文。尚未作为 GitHub 正式行内 review 发布。
