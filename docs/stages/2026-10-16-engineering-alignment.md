# 阶段说明：证据链修复与两套 C99 的共同验证

## 目标及已完成事项

本阶段落实用户要求的工程对齐，解决此前审查中的三处实际缺陷，并补齐 portable/embedded 共用模型验证。基于 `d0a0172`，提交进入现有集成草稿 PR #12；后续误差研究使用独立工作分支与 PR，不在本阶段扩大算法矩阵。

1. **报告基线**：新增 `study_reporting.select_baseline`，要求唯一的 `sample_tetra/m33`，不再按记录顺序取首条。报告入口调用该函数，缺失/重复基线明确拒绝。`correct_pr9_baseline.py` 由现有 CSV 复算勘误，68 行中修正 8 行；原始测量、最优候选、耗时及历史表保留。总体降幅中位数仍为 43.41744357268762%，不能据此忽略逐行错误。[勘误](../../report/data/pr9-baseline-correction/correction.json)
2. **续跑身份**：研究身份升为 schema 2，绑定 Python/依赖、CPU/ISA、系统、NumPy 构建、Numba 实际线程层及线程环境。`claim_run` 原子发布初始 run 来源；相同身份只读核验，不刷新旧时间/提交字段；不同身份或旧身份记录在写入前被拒绝。旧实验不得在新源码上续写，需新目录。[实现](../../python/lutlab/study_provenance.py)
3. **账本执行内核**：登记同时核对 CPU 后端、实际内核和适用的命令参数。新 `cube` 输出解析后的真实内核；`auto` 必须有实际解析结果。历史 cube 没有 JSON 输出，只有明确非 auto 命令才作为旧格式证据接受，单独标明其证据层级。不一致时不发布观测或修改索引/冠军。[校验](../../python/lutlab/execution_proof.py)
4. **C99 数值对齐**：在同一组序列化模型上加入 portable 默认/强制通用、embedded 和独立 u64 oracle 的共同契约；额外构造曲线/常量模型，确认捷径实际触发。宿主全色域互操作纳入 portable 与结构化 AVX2；三类 QEMU 工作流显式打开共用检查。保留两套接口的所有权、范围及失败状态差异。[共同合同](../c99-shared-contract.md)

没有修改 AGENTS.md、历史 LUT/image、冻结报告、既有拟合器和插值器；不更改台账观测、冠军或矩阵分母。PR #9 的历史工作流指纹继续描述其冻结版本，当前被修复的报告/恢复代码具有新的源码身份。

## 相关审查记录与当前状态

- [PR #9 审查评论](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)：基线和恢复环境问题已在本分支落实修复及回归，尚未进入 main。
- [Issue #7](https://github.com/WyEhNf/flash-chroma/issues/7)：执行内核绑定缺口已修复并验证，保留旧记录、无自动关闭。
- [Issue #8 与更新评论](https://github.com/WyEhNf/flash-chroma/issues/8#issuecomment-6213698494)：推进共同合同、宿主差分和 portable 的系统级 QEMU 接入；接口合并/迁移由维护者确定，实板工作未完成，不关闭该议题。
- [PR #12](https://github.com/WyEhNf/flash-chroma/pull/12)：本阶段作为该集成草稿的后续提交。已读正文、全部评论、审查线程，沿 #9、#7、#8 核对源码；操作前再刷新。没有把历史 CI 成功或评论中的补丁当成已落地修复。
- Discussion #4 原始方案由用户提供；此前网页读取为 404，最新回复仍有访问缺口，在 PR 披露，不执行 GitHub 合并或 issue 关闭。

## 测试环境与目的

- Windows 11 10.0.26200、x86_64、AMD Ryzen 9 8945HX（16 核/32 线程）。MinGW GCC/G++ 15.2.0、CMake 4.2.0、MinGW Makefiles、Release。
- 独立研究环境 `artifacts/error-study-py312`，Python 3.12.14、NumPy 1.26.4、SciPy 1.15.2、Numba 0.60.0、llvmlite 0.43.0、Pillow 10.4.0、tifffile 2023.4.12、psutil 5.9.0、pytest 8.4.2；依赖来自 `experiments/local-study-requirements.txt`，完整冻结另存证据目录。不覆盖默认 Pixi 或原 Python 环境。
- 默认构建启用 AVX2/OpenMP；另构建 AVX2/OpenMP 关闭的标量配置；两者均开启完整离线库、portable、embedded 和共用 C99 契约。OMP/BLAS 环境单线程，内核夹具另显式覆盖 1/4 线程；不执行吞吐比较。
- 目的：验证三项缺陷被拒绝/修正、合法恢复与登记保持可用、跨实现位精确及专属错误契约；CSV 勘误只复算已有数据；历史账本检查只读核对执行内核，不重新验证历史质量或速度。

## 集中验证及结果

默认和标量配置均构建成功，各 **CTest 3/3、Python 45/45** 通过，没有可选研究模块跳过。NumPy 构建信息产生一条建议安装 PyYAML 的展示警告，不影响身份采集和测试结论。后续只扩充 C99 曲线/常量夹具，两配置各增量构建并针对 `embedded_contract` 复查 1/1，未重跑未变的 Python 门禁。

- 完整 `256³` 的独立整数 oracle、混合 m 与非均匀轴通过；新 cube 的 auto 实际内核回执由真实子进程验证，并抽取输出像素对照独立 Python 算子。
- 环境变更被拒绝且原 run 字节不变；相同身份恢复保留最初元数据；内核/后端不一致被拒绝且账本原状保留；m17/m33 同时存在及顺序变化不会选错基线。
- 只读核对总账本 212 个 case 的 4602 条观测：4528 条为旧显式命令绑定、74 条为已有 backends 格式绑定，未发现不一致或证据缺失。该结论不升级旧记录的证据强度，也不证明历史拟合已达标。[机器记录](../../report/data/engineering-alignment/native-evidence-binding-audit.json)
- 本机无三类 QEMU 工具链，本阶段系统级结果等待对应提交的远端 CI，后续将以实际日志补记，不以宿主通过替代。
- 未执行新拟合/误差/性能扫描、官方评分、实板或功耗测试。三个修复的最小回归集中加入既有门禁，不扩张无关单元测试。

复现命令：

```powershell
$env:PATH='E:\mingw64\bin;C:\Program Files (x86)\CMake\bin;' + $env:PATH
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
cmake -S . -B build-engineering-alignment -G 'MinGW Makefiles' `
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe `
  -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe -DJSHC_ENABLE_FULL_FIT=ON `
  -DJSHC_ENABLE_AVX2=ON -DJSHC_ENABLE_PORTABLE_C=ON -DJSHC_ENABLE_EMBEDDED=ON `
  -DJSHC_EMBEDDED_PORTABLE_PARITY=ON
cmake --build build-engineering-alignment --parallel 8
artifacts/error-study-py312/Scripts/python.exe scripts/check_correctness.py --build-dir build-engineering-alignment
# 标量目录使用相同参数，另设 -DJSHC_ENABLE_AVX2=OFF -DJSHC_ENABLE_OPENMP=OFF。
python scripts/correct_pr9_baseline.py --output report/data/pr9-baseline-correction
```

本机详细日志在忽略目录 `artifacts/engineering-alignment`；持久化的精简日志、依赖冻结、哈希和结果见 [证据目录](../../report/data/engineering-alignment)。本阶段不自动合并 PR。

Agent：Codex

Operator：本次会话的项目用户

Task：工程对齐与后续误差研究的前置修复

Status：本机修复与验证完成，远端 CI 待对应提交执行，集成草稿待审查
