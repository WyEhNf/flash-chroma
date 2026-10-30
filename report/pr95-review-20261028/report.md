# PR #95 单一路线审查与跨 LUT 泛化测试

Agent：Codex /root；Operator：本会话用户；Task：PR #95 审查与跨组合测试；Status：测试与审查完成，两个缺口待修复。

交付方式：通过独立工作分支向 #95 的源分支 `codex/p16-frontier-header-20261027` 提交补充 PR「补全#95的审查和测试」。本阶段交付报告、审查意见、复现代码和小体积证据，不修复运行库或两个流程缺口，不代表批准 #95。审查正文见 [review.md](review.md)，可复核证据见 [evidence/manifest.json](evidence/manifest.json)。

## 1. 范围与结论

审查提交为 `fb7e195215f14df9f635394d75cde0e0e69c82c9`，基于 `b7d7e3ed0b3f95e9a2fcf68341b360debeb6f55e`。2026-10-28 提交前 fetch 并再次确认远端 PR #95 仍指向该提交、状态为 Draft；本地审查分支已包含目标头，无需额外整合。本次在独立工作树和 `codex/review-pr95-generalization-20261028` 分支进行，没有修改运行库或合并 PR。阶段对应提交以本补充 PR 提交列表为准，测试对象仍是上述固定 SHA。

共固定 8 条数值链，使用 25 个不同源 LUT，生成 20 套新模型。100 个执行配置中，78 个成功并保持探针/照片输出一致，22 个因 U8/U16 调色板容量不足被明确拒绝。容量拒绝是运行库的合法结果，但公开验证脚本未正确处理这一情况。另复现部署入口对目录误差和稳定性缺少原始证据绑定的问题。

**结论：本次覆盖范围内，运行时计算可迁移到这些新模型；小调色板路径适用性与拟合精度不能从 Cinema 单链直接外推。公开新模型验证流程和证据绑定仍有两个 P2 缺口。**

## 2. 实际环境与判定口径

- Windows 11 10.0.26200、x86-64，Intel Core Ultra 5 125H；不是 Xeon Gold 6140。
- MinGW GCC/G++ 8.1.0，C++17 `-O3 -DNDEBUG -fopenmp`；独立 C99 `-std=c99 -O3 -DNDEBUG`。编译器位于 `D:/codeblocks/MinGW/bin`。
- Python 3.12.7、NumPy 1.26.4、SciPy 1.15.2、Numba 0.60.0、Pillow 10.4.0、pytest 7.4.4。
- CPU-only；Sparse Scalar 1 线程；Sparse AVX2、DirectU8/U16/RGB24 为 4 线程；C99 对照为普通 CPU 调用，未使用 GPU/NPU。
- DLL SHA256：`e6eebe25fa61a5500618a83a13b827fd7f13de9f0915ce9b7e9f210b9ba1c507`。本会话直接从审查头编译；未生成项目标准链接回执，`plan.json` 如实保留 `build_receipt: null`。不能把事后源文件哈希冒充编译时回执。
- GCC 8 编译曾提示请求的 32 字节对齐超过其 16 字节上限；本次已运行的路径未见不一致，但未因此宣称所有 ABI/编译器均通过。
- 运行时正确性：相同固定模型下，要求输出 RGB8 字节完全相等。
- 拟合误差：对每个像素计算 `sqrt((R-Rref)^2+(G-Gref)^2+(B-Bref)^2)`，通道为 0..255；mean 为均值，p99 为 NumPy 默认线性分位数，max 为最大值。**这是 RGB 欧氏误差，不是 CIEDE2000，也不是已获官方阈值认证的成绩。**
- 参考链为各源 LUT 按仓库 `source_lut.bake_source` 规则转为 256³ RGB8 稠密表后，逐级查表。继承仓库格式解析、域裁剪和逐级量化规则，没有另行认证摄影色彩域。
- 6 张完整 1024×768 照片：kodim03、kodim06、sony-034、sony-041、DIV2K 0801、0802，共 4,718,592 像素。来自现有评测集，不是全新保留集。

## 3. 模型和测试覆盖

| 链 | 四级 LUT 顺序 |
| --- | --- |
| cinema | 1910s → 1920s → 1930s → 1940s |
| avant | Amber Haze → Arcade Dayz → Blow Me Down → Caramel Plum Cake |
| scenic | Grey Matter → December Greens → Emerald Malaise → Irish Uprising |
| cinema_reverse | 1940s → 1930s → 1920s → 1910s |
| mixed_tail | Lomochrome Purple 2 → Classic Chrome → Tension 1 warm → Filmic 06 |
| mixed_hdr | HDR2SDR 01 DRG → Provia Std → Arcade Dayz → Filmic 04 |
| zoology | Ara → Boa → Dodo → Great Auk |
| filmsim | Acros → Classic Chrome → Provia Std → Velvia Vivid |

源数据覆盖 cube、TIFF、3dl，来自 stripedpurple、filmsim、christophwurst、blender-filmic、hdr2sdr。完整路径和源 SHA 在 `artifacts/pr95-review/plan.json`。这些组合用于数值压力测试，**不是已经认证输入/输出色彩域相容的真实摄影流水线**。

基础 16 模型：每条链各拟合全 17³ 和全 33³，公开 `fit_candidate`，均匀网格加 `sample_interp`。每模型 65,536 个固定随机探针加 8 个角点，以独立 NumPy int64 排序四面体累加和每级 half-up 为对照；另与独立 C99 对照。独立 oracle 的算术独立，但仍读取同一解析后的模型坐标表，不是独立文件格式解析器。所有成功配置运行六张完整照片，并覆盖原地处理长度 1/7/8/9/63/64/65/257。

补充 4 模型：mixed_tail 的 `[17,25,33,17]` 均匀采样、mixed_hdr 的 `[33,17,25,33]` 曲率网格采样、两条链各一个全 33³ 曲率网格 `ls_tetra_int`。后者先做四面体最小二乘拟合，再做整数节点精化，仍然逐级独立拟合，没有四级联合调优。补测各含 65,536 个不同种子的随机探针、1,728 个固定边界探针、六张完整照片及 C99 对照。该固定边界集不穷尽所有非均匀网格切换点。

| 执行配置 | 成功模型 / 20 | 容量拒绝 | 成功配置的探针/照片不一致 |
| --- | ---: | ---: | ---: |
| Sparse Scalar | 20 | 0 | 0 |
| Sparse AVX2 | 20 | 0 | 0 |
| DirectU8 AVX2 | 8 | 12 | 0 |
| DirectU16 AVX2 | 10 | 10 | 0 |
| DirectRGB24 AVX2 | 20 | 0 | 0 |

另外，cinema-m33、mixed_hdr-m33 各遍历完整 16,777,216 RGB8 输入，Scalar 与 RGB24 无差异，同时对稠密参考链统计误差。完整域 mean/max 分别为 2.753518/16.186414 和 2.588994/145.013792。后者照片 max 为 130，说明照片样本没有覆盖其完整域最坏点。公开验证器复现还执行了 avant-m33 的 Sparse Scalar/C99 与 AVX2 完整域遍历，随后在 U16 准备时失败，详见第 6 节；不把失败回执说成完整流程通过。

## 4. 精度结果与解释

以下为六张照片全部像素合并后的统计；逐图数据保存在 results.json 与 supplement-results.json。

| 链 | 17³ mean | 33³ mean | 17³ p99 | 33³ p99 | 17³ max | 33³ max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cinema | 4.8141 | 2.8466 | 11.2250 | 8.1240 | 28.3019 | 16.1864 |
| avant | 2.8991 | 1.8776 | 15.2643 | 9.4868 | 38.2230 | 27.3313 |
| scenic | 1.5506 | 1.3654 | 3.3166 | 3.1623 | 5.3852 | 4.6904 |
| cinema_reverse | 2.5755 | 1.8149 | 12.2066 | 9.8489 | 73.7631 | 47.6865 |
| mixed_tail | 3.6049 | 2.4580 | 19.0000 | 9.4868 | 92.4338 | 95.0474 |
| mixed_hdr | 5.0554 | 2.9286 | 40.0625 | 25.4951 | 150.0033 | 130.0000 |
| zoology | 1.2304 | 0.6765 | 10.3923 | 6.9282 | 46.7654 | 24.2487 |
| filmsim | 2.4069 | 1.8856 | 8.6603 | 7.0711 | 19.0526 | 13.3041 |

| 补测模型 | mean | p99 | max |
| --- | ---: | ---: | ---: |
| mixed_tail，17/25/33/17，均匀采样 | 2.7696 | 16.4924 | 95.0053 |
| mixed_hdr，33/17/25/33，曲率采样 | 4.8346 | 44.5982 | 151.0132 |
| mixed_tail，全 33³，曲率 + 整数最小二乘 | 2.0704 | 8.6023 | 71.0704 |
| mixed_hdr，全 33³，曲率 + 整数最小二乘 | 2.4785 | 22.0454 | 131.0000 |

8 条链从 17³ 到 33³ 的 mean、p99 均改善，但 mixed_tail 的 max 从 92.4338 上升到 95.0474。网格加密不保证逐点/最大误差单调改善，不能仅凭均值称全面更好。

全 33³ 曲率 + 整数最小二乘相对全 33³ 均匀采样：mixed_tail 的 mean 约下降 15.77%，max 约下降 25.23%；mixed_hdr 的 mean 约下降 15.37%，但 max 从 130 升到 131。这里同时改变了网格与拟合方法，不能单独归因于某一个因素。混合 m 的两个样例只证明运行时支持，尚未搜索最优内存分配。

本次没有重新训练 373a/max_first，因此这些结果不能解释为二者在新链上的泛化成绩，也不能与其 Cinema 评分直接排名。

## 5. 性能观测的边界

基础实验对每个成功配置预热一次，再记录 5 次原生 apply 调用（含 Python FFI 边界）耗时。六张图已解码并拼成连续 RGB8 输入；不含离线拟合、prepare、读盘、编码、输出核对。计时外将输出填入固定字节并逐次验证正确性；全部样本保存在 results.json，不只保留最快轮。

没有绑核、锁频、随机化次序或 A/A 控制，Core Ultra 混合核心调度与系统负载未受控。因此这里只记录本场观测，不发布稳定加速比，也不比较 PR 原有 Ryzen/GCC15.2 数据。补充四模型只验证正确性与拟合误差，不测稳定性能。

真正可确定的泛化边界是表示适用性：U8 仅 8/20、U16 仅 10/20，不能将 Cinema 小调色板性能直接推广到所有 LUT。完整域 RGB24 和 Sparse 在所测模型均可用；选择器应依据实际可达输出色数量、内存预算和本机实测选择表示。

## 6. Review 发现与验收建议

### P2：新链调色板超容量会中断公开验证流程

位置：`scripts/verify_flash_chroma.py:63-69`。脚本根据 profile 名称强制选择 U8/U16，并在全部完成后才写回执。通过公开拟合入口生成的 `fitted` avant-m33 模型，Sparse Scalar/C99 和 AVX2 完整域步骤完成后，U16 返回 `10 调色板容量不足`，整个命令退出 1；即使带 `--all-representations` 也到不了可用的 RGB24，之前的成功结果没有输出回执。运行库按容量拒绝是正确行为；缺陷位于编排层。

证据：`artifacts/pr95-review/verifier-repro.log`、avant-m33/source-manifest.json、results.json 中对应成功 Sparse/RGB24 记录。后续 benchmark 要求验证回执，故这会阻断新链公开流程。`bench_flash_chroma.py:54-60` 同样按既有 profile 白名单列举 direct 路径，修复时应一起取消对模型名称的能力假设。

建议：允许显式指定表示；对容量拒绝记录为不适用并继续已支持的配置，保存已完成记录；实际执行错误继续失败。新增大于 65,536 个可达输出色的链回归，要求 Sparse/RGB24 可验证、U8/U16 不适用状态可追踪。

### P2：部署入口没有把目录质量和稳定性重新绑定原始证据

位置：`scripts/run_flash_chroma.py:92-99`，影响后续 226 行附近继承质量的逻辑。当前绑定检查 completed、库 SHA、输入 SHA、配置、输出摘要格式，但没有核对目录中的误差、计时、time_stable 与所引用原始测量。

已在新建的独立夹具目录中复现：原 `default-direct_u8-avx2-1t` 的 A/A 为 false、mean=0.695486159、batch_ms=46.6617。只把目录副本改为 time_stable=true、mean=0.01、worst_image_mean=0.02、batch_ms=0.001，保留原始证据文件；重新正常选择且更新 selection 的目录摘要，`max_error=0.03` 仍选中并通过 bind_selection、bind_model、bind_evidence 三层检查。

证据：`scripts/review_pr95_evidence_binding.py` 与 `artifacts/pr95-review/binding-repro/result.json`。这是元数据绑定复现，没有执行错误目录的图像处理，没有修改原档案，也没有证据证明现存报告误记。本轮原档案专项审计通过。

建议：选择/继承质量前，把误差、计时范围与统计、A/A、模型/输出身份绑定到可复算的原始记录及其质量证据；目录不一致应拒绝。阶段专用的 verify_frontier_evidence 检查不能替代部署入口的通用强制绑定。补充误差、稳定性、耗时分别失配的拒绝测试，以及匹配记录的正向测试。

## 7. 既有门禁、协作记录与未覆盖项

本机执行相关 Python 测试 41/41 通过（3.32 秒）。对 `report/data/p16-header-performance-20261028` 执行专项证据审计通过：20 配置、40 目录点、1 测量场次、2 上下文、7 模型、19 A/A 通过。这是档案复算，不是重新跑原 Ryzen 性能。

协作检查覆盖仓库 issue/PR 全量索引第一页及空第二页，按单头、证据、direct、性能主题筛选；读取 #95/#94/#89 正文、完整相关评论与审查线程，以及 #43/#48/#62/#71/#73/#75 的正文和意见；读取 #5/#9/#12/#37 的历史纠正意见、#7/#8 正文及评论。发布前刷新 #95 仍无新提交或意见。Discussion #4 接口读取失败，未将其视为无意见，不执行依赖此结论的合并或关闭。

- [#7](https://github.com/WyEhNf/flash-chroma/issues/7)：历史 Casebook 内核绑定问题修复为 337a3dd，并由 #37 集成；与本次新部署目录指标绑定缺口区分。本次保留 issue，不声称新缺口已修复。
- [#8](https://github.com/WyEhNf/flash-chroma/issues/8)：共同 C99 数值合同已集成，最终接口分层与实板资源/实时性仍待完成；本次 Windows C99 探针对照不能替代实板。
- [#9](https://github.com/WyEhNf/flash-chroma/pull/9)：历史 m33 基线及环境归属纠正保留；本轮明确同一稠密参考、同机比较和 RGB 误差定义。
- [#95](https://github.com/WyEhNf/flash-chroma/pull/95)：原报告已承认三方 A/A 不全通过及 Xeon 缺测；本次不把描述性结果升级为稳定性能结论。

未覆盖：68 个 LUT 的全部组合、独立保留照片全集、所有模型的完整色域精度、侧车模型新泛化训练、373a/max_first 跨链联合优化、实际摄影域匹配、官方色差/Threshold、Xeon6140、实板、NEON/AVX512。没有在本机执行 CMake/CTest 全套；不把远端既有 CI 当作本机结果。

## 8. 文件作用、复现与下一步

| 文件 | 作用 |
| --- | --- |
| scripts/review_pr95_generalization.py | 冻结源 LUT/照片、生成 16 模型、独立 oracle、跨表示/短尾检查、计时原样本、两模型全色域检查 |
| scripts/review_pr95_supplement.py | 混合 m、曲率网格及整数最小二乘四模型补测 |
| scripts/review_pr95_evidence_binding.py | 仅在副本中复现目录证据失配可被接受 |
| artifacts/pr95-review/plan.json、supplement-plan.json | 输入来源、哈希、参数、环境、预定范围 |
| artifacts/pr95-review/results.json、supplement-results.json | 逐模型/配置/照片误差、输出摘要、容量状态及原计时样本 |
| artifacts/pr95-review/*/source-manifest.json | 新模型、源稠密表和拟合代码的 SHA 与参数 |
| artifacts/pr95-review/*full-hist.npy | 两条链完整色域平方误差直方图，可复算统计 |
| artifacts/pr95-review/*.log | 成功、容量失败、专项审计与门禁原日志 |
| scripts/archive_pr95_review.py | 归档小体积原始证据，并只读核对 SHA、配置计数和全域直方图 |
| report/pr95-review-20261028/evidence/ | 上述小体积文件的版本化归档；无需本机 artifacts 即可复核结果 |

归档保留 58 份文件，包括源数据计划、完整结果与计时原样本、20 套模型的拟合起始记录及 manifest、成功和失败日志、目录失配夹具。每份文件记录源 SHA、归档 SHA 和转换方式；UTF16 日志仅转 UTF8，两个 int64 全域直方图以非零项 JSON 无损保存。原始绝对路径仅作历史来源，不要求审查者拥有这些目录。源照片/LUT 已在仓库；DLL、对象文件、稠密表与新模型二进制保留本地，模型可按脚本重建并核对 manifest。归档中的 audit-manifest 是先前本地快照，包含历史路径/发布状态，不作为本补充 PR 的当前状态或编译回执。

本次打包检查在同一 Windows/Python 环境运行 `python scripts/archive_pr95_review.py --verify`：58 份文件 SHA 一致，20 模型、78 成功配置、22 容量拒绝计数相符，两个全域直方图复算与结果相符。此为数据完整性检查，不是新一轮数值或性能测试；拟合和运行时源码未变，不无意义重复前述实验。

只读复核已提交证据：

```powershell
python scripts/archive_pr95_review.py --verify
```

工作目录为本独立工作树。以下为实际命令；复跑拟合与夹具需使用新的输出目录或新的干净工作树，脚本拒绝覆盖已有模型，不能直接删掉旧证据：

```powershell
gcc -std=c99 -O3 -DNDEBUG -Iinclude -c single_header/c_bridge.c -o artifacts/pr95-review/c_bridge.o
g++ -std=c++17 -O3 -DNDEBUG -fopenmp -Iinclude -shared single_header/bridge.cpp artifacts/pr95-review/c_bridge.o -o artifacts/pr95-review/review.dll
$env:PYTHONIOENCODING='utf-8'
python scripts/review_pr95_generalization.py
python scripts/review_pr95_supplement.py
python scripts/review_pr95_evidence_binding.py
python -m pytest tests/test_p16_frontier.py tests/test_flash_chroma_support.py tests/test_run_flash_chroma.py tests/test_p16_submission.py tests/test_flash_chroma_regression.py -q --basetemp=artifacts/pr95-review/pytest-temp
python scripts/verify_frontier_evidence.py --evidence report/data/p16-header-performance-20261028
```

公开验证器失败复现（Python 3.12 在本机需要显式添加 MinGW DLL 搜索目录）：

```powershell
python -c "import os,sys,runpy; d=os.add_dll_directory('D:/codeblocks/MinGW/bin'); sys.path.insert(0,'scripts'); sys.argv=['verify_flash_chroma.py','--library','artifacts/pr95-review/review.dll','--manifest','artifacts/pr95-review/avant-m33/source-manifest.json','--all-representations','--output','artifacts/pr95-review/avant-official-verifier.json']; runpy.run_path('scripts/verify_flash_chroma.py',run_name='__main__')"
```

下一步先修两个流程缺口并做定向回归；然后冻结更多链及独立照片集，按可达色数选择 Sparse/U8/U16/RGB24，在同机受控 A/A 下测准备成本、热批次、端到端和内存。拟合研究应分别对网格、整数拟合、联合调优做消融，并同时保护 mean/p99/max 与逐图误差。当前阶段不建议直接宣告通用最优或通过最终验收。
