# 阶段说明：四级误差来源与热点整数精化

## 结论

本阶段完成用户要求的第 1/2 项算法研究：固定四个案例、m33，实际实现并运行误差归因、敏感性加权和热点整数精化。**大误差的主要证据指向固定表示下的陡峭局部变化、节点裁剪及四级非线性传播，不能简单归因于运行时算错或 CG 未收敛。** 两个单级案例还得到了固定 Q16 权重下、对任意合法 RGB8 节点都成立的局部必要误差下界。

本轮候选在完整 RGB 色域有改善，但三个真实案例都至少有一项自然照片指标退化。它们保留为研究结果，没有替换默认拟合器、case 冠军或历史测量。不存在官方 Threshold 或官方得分结论。

工程前置修复已在 `337a3dd` 完成，进入 [PR #12](https://github.com/WyEhNf/flash-chroma/pull/12)；本研究基于该提交，使用 `codex/analyze-chain-error` 独立分支/后续 PR，核心研究提交为 `38d8350`，补充干预、控制方法验收和归档随本阶段后续提交交付。

## 固定范围、实现及实验步骤

计划在实验前保存为 [chain-error-study-v1.json](../../experiments/chain-error-study-v1.json)。只研究：

| 案例 | 级数 | 基线 | 目的 |
| --- | ---: | --- | --- |
| Lomochrome Purple 2 | 1 | 均匀网格 + ls_tetra_int，m33 | 真实 LUT 的边界尾部；单级诊断不是比赛四级成绩 |
| Velvia Vivid | 1 | 曲率网格 + ls_tetra_int，m33 | 高分辨率源的局部陡变与裁剪；同上 |
| Cinema chain 2 | 4 | 四级曲率网格 + ls_tetra_int，m33 | PR #9 的 1910s/1920s/1930s/1940s 数值链 |
| cascade-zoom-d8 | 4 | 四级均匀网格 + ls_tetra_int，m33 | 已冻结 hack-v2 的压缩、阈值、8 倍放大与通道置换 |

真实源按 PR #9 的政策从原网格三线性恢复，再 clip/round 为 RGB8 完整表；未知摄影色彩域仍未知，Cinema 链仅是数值压力组合。控制例由冻结生成器导出，四张完整源表逐一核对原有 SHA-256。没有修改源 LUT、照片、旧 catalog、留出划分或矩阵分母。

实现文件：

- [error_analysis.py](../../python/lutlab/error_analysis.py)：逐级向量分解、替换干预、离散后缀敏感性、Q16/舍入诊断、热点回放、加权重拟合及守护选择。
- [error_certificate.py](../../python/lutlab/error_certificate.py)：纯整数三点关系，给出固定权重表示的必要误差。
- [run_chain_error_study.py](../../scripts/run_chain_error_study.py)：来源/环境绑定缓存、四例有界流程、独立整数 oracle 和原生后端验收。
- [explain_chain_counterexamples.py](../../scripts/explain_chain_counterexamples.py)：补充全部 16 种阶段干预和既有控制方法验收，不重新拟合主实验。
- [report_chain_error_study.py](../../scripts/report_chain_error_study.py)：整理指标、模型/图片反例和科学图，不重新拟合或计时。

发现集为固定 seed 的 262144 个颜色，guard 为另一个 seed 的 65536 个颜色，两者初始 RGB 不重合；先基线全色域找 top-128，再加入 ±1 码值邻域。选定一级，其他级的模型字节保持不变。比较 5 个配置：baseline、只按实际到达分布重拟合、后缀敏感性加权重拟合、热点 Q16 整数精化、加权与精化组合。

所有新增拟合标签都是**该级自己的完整 LUT 在相同该级输入上的值**，没有将复合真值/残差作为节点标签。整数精化要求同级训练/guard 的真实 RGB8 输出不退化；整链候选再要求 guard 的 mean/RMS/p99/max 均不增，至少一项严格改善，按 max、p99、mean、RMS 选择。随后冻结选择，才评价固定的另一批 262144 颜色、100 张完整照片和候选完整色域。

guard 属于优化/选择数据；完整色域也用于发现热点，不能称盲测。最终固定探针的初始 RGB 与发现/guard 不重合，但不声称与基线拟合点或全域热点邻域完全分离。100 张照片是既有真实场景对照，未宣称未知 LUT 或新照片上的泛化。

## 1. 已测指标与实际收益/退化

指标全部为题面 `rgb_l2_code_value = sqrt(dR²+dG²+dB²)`，不是 Lab/CIEDE2000。每个全色域指标覆盖 16777216 种 RGB 输入。

| 案例 / guard 选中方案 | 全色域 mean | RMS | p99 | max |
| --- | ---: | ---: | ---: | ---: |
| Lomo：基线 → combined | 0.907090 → 0.865251 | 1.687408 → 1.634050 | 7.000000 → 6.633250 | 49.193496 → 48.363209 |
| Velvia：基线 → combined | 1.031289 → 1.009488 | 1.992443 → 1.938867 | 7 → 7 | 54 → 51 |
| Cinema：基线 → distribution_ls | 2.022233 → 1.873270 | 2.399168 → 2.199747 | 5.830952 → 5.385165 | 9.848858 → 9.848858 |
| Zoom：基线 → hotspot_integer | 22.895813 → 21.409677 | 38.268361 → 36.554682 | 144.225518 → 144 | 177.994382 → 177.409132 |

照片为每例 100 张 1024×768 RGB8，p99 列是**最差单图 p99**，不是将所有照片像素混合后的全局 p99：

| 案例 | 100 图 mean | 最差单图 p99 | 照片 max |
| --- | ---: | ---: | ---: |
| Lomo | 0.814611 → 0.786736 | **13.190906 → 13.341664，退化** | 49.193496 → 48.363209 |
| Velvia | **1.123080 → 1.127346，退化** | **7.071068 → 10，退化** | **49 → 50.009999，退化** |
| Cinema | **1.759132 → 1.821517，退化** | 9.848858 → 6.403124 | 9.848858 → 9.848858 |
| Zoom | 27.690542 → 26.081353 | 158.215044 → 152.161099 | 177.994382 → 177.361213 |

自然图 RMS、阈值 ≥1/2/3/5 比例、CVaR1%、固定探针、各候选 guard 和 800 条逐图明细均保留在[证据目录](../../report/data/chain-error-v1)。这里的阈值只是描述性切片，不冒称官方门槛。三个真实基线的照片 mean 与 PR #9 已提交汇总一致，但未据此宣称其未上传模型也已逐字节复现。

## 2. 原因一：陡峭局部变化与固定表示的限制

两个单级选中阶段的 262144 个诊断颜色上，Q16 坐标量化引起的连续输出变化很小：Lomo max 约 **0.002081**，Velvia约 **0.000961**。最终 RGB8 舍入引起的单级变化分别最多约 **0.8536/0.8592**，而未裁剪浮点拟合的误差 max 已分别约 **33.9608/46.9349**。这是该诊断集合的结果，不是所有颜色的量化上界；也不能把不同分量范数直接相加。

基线最坏点的参考自身在 ±1 的三维邻域中有大变化：Lomo 邻域最大约 52.78，Velvia约 39.12；因此参考 LUT 本身具有陡峭区域。参考跳变与模型响应差异分别记录，未把参考自身跳变叫作实现不稳定。[切片图](../../report/data/chain-error-v1/hotspot-slices.png)

进一步对任意三个输入，令各节点的权重二阶差分为 `alpha = W0 - 2W1 + W2`，各行 Q16 权重和为 65536，因此 `sum(alpha)=0`。对任意合法节点 `n∈[0,255]`，模型未舍入输出二阶差分绝对值不超过：

`B = 255 × sum(alpha_positive) / 65536`。

三次舍入按系数 `[1,-2,1]` 的误差余量不超过 2。若三点最大通道误差为整数 E，则必须满足 `|D_reference| <= B + 2 + 4E`。由此只用整数算术取得必要误差下界，**不依赖当前节点拟合结果**：

- **Lomo：固定当前网格/idx/frac 的任意 RGB8 节点，至少有一个输入的 RGB 距离 ≥13。** 证书三点为 `(247,0,72)/(247,0,76)/(247,0,80)`。
- **Velvia：同条件下至少有一个输入的 RGB 距离 ≥23。** 证书三点为 `(255,247,0)/(255,251,0)/(255,255,0)`，原表 B 输出为 `0/0/123`。

完整标签、节点系数、分母和证书在 [explanations.json](../../report/data/chain-error-v1/explanations.json)。这证明当前固定表示存在局部限制，**不证明 49/54 已最优，不涵盖其他网格、其他恢复算子，也不是任意四级链的最终误差下界**。两个四级案例所得三点下界为 0，只表示该证书未能约束，不能解释成可零误差。

## 3. 原因二：先求解再裁剪会改变已求得的近似

所选阶段没有零支撑节点；CG 均按既定准则收敛，通常只需 11–12 次迭代。Lomo/Velvia 连续解分别有 **6742/13782** 个节点分量越出 `[0,255]`。在诊断颜色上，裁剪本身使连续输出最多改变约 **13.713/23.343**，之后还有整数节点精化及输出舍入。

这不是非法节点进入运行时，最终模型均为合法 RGB8。它说明“求解器收敛”与“裁剪后的整数模型精度”是不同问题。现有 R26 已有箱约束路线，后续应将其作为针对这两个真实源的消融；本轮没有再次运行箱约束算法，也没有把它说成已经消除了尾部错误。

## 4. 原因三：小的前级偏差可跨过后级判定边界

逐级使用以下**向量恒等式**，并保存平方误差交互项：

`S_k(sparse_prefix) - T_k(exact_prefix)`

`= [S_k(sparse_prefix) - T_k(sparse_prefix)] + [T_k(sparse_prefix) - T_k(exact_prefix)]`。

Zoom 的反例 `(125,29,120)`：第一级完整输出为 `(111,99,111)`，稀疏输出为 `(112,100,110)`。R 从 111 变为 112，跨过第二级阈值；第二级完整表在该稀疏输入上输出 `(112,132,110)`。实际第二级模型输出 `(112,121,109)`，第三级随后将 G 从精确路径的 24 放大为 200。主要问题发生在阈值与放大之前，不能通过只精确计算最后一级修复。

对两条四级链另枚举全部 16 种“某级用完整表、其余用稀疏表”的诊断干预，只在固定发现颜色上执行，不作为运行方案。Zoom 的最终 MSE 干预分配约为：第一级 **171.350**、第二级 **1295.836**、第三级 **−0.0315**、第四级 **0.5839**；负项表示轻微抵消。Cinema 分配约为 **0.7274/1.2390/1.8200/1.9601**，误差更分散。分配包含交互且依赖这组输入，不是唯一的物理贡献比例。[误差分解图](../../report/data/chain-error-v1/stage-error-attribution.png)

Zoom 的后缀 ±1 LSB 增益在发现颜色上恒为 8，归一化后敏感性权重全相同，因此 `sensitive_ls` 与 `distribution_ls` 相同，**本轮标量增益权重没有提供额外信息**。只改善平均拟合还会恶化 guard max：该重拟合的 max 从 176.411 上升至 217.021，故被拒绝。真正值得继续研究的是前级输出跨越后级边界的离散风险，而非仅给所有颜色乘同一个增益。

## 5. 原因四：色域测度与照片测度不同，选择目标也不同

Cinema 全色域 mean 下降约 7.4%，照片 mean 却上升约 3.5%；Lomo 照片 mean/max 改善，但最差单图 p99 上升；Velvia 的照片多项指标退化。映射逐像素独立，均匀色域与照片的颜色频率不同，因此 guard 在一种分布上不退化，并不能保证另一种分布。

敏感性加权没有胜过 Cinema 的仅分布重拟合；单级两例没有后缀，敏感性为 1，两种 LS 路线相同，这是预期消融结果。三线性也不是直接换核即可取胜：已分别记录相同节点换算子、匹配三线性 LS 两种同输入对照，没有把恢复失配叫作拟合优化。

## 6. 已有方法对照，避免把较弱基线改善当成突破

Zoom 另测既有 `lookahead_bins/m33`：全色域 **mean 3.527344、RMS 13.844702、p99 80、max 80**，明显好于本轮热点整数精化的 mean 21.409677/max 177.409132。此对照说明压缩/阶梯场景应优先研究分箱与到达域结构。它仍有误差，不是全链精确；本轮没有对该控制方案新增完整 100 图评价。

## 环境、验证及复现

- 环境沿用工程独立环境：Windows 11 10.0.26200、Ryzen 9 8945HX、Python 3.12.14、NumPy 1.26.4、SciPy 1.15.2、Numba 0.60.0；研究映射 4 线程，OMP/BLAS 单线程。原生验收为 GCC 15.2 Release、标量/AVX2/C99、单线程，构建目录 `build-engineering-alignment`。
- 新归因合同测试 **2/2**，覆盖向量/SSE 恒等式、替换结果、分位数、参考跳变和解析三点证书。工程默认/标量各 CTest 3/3、Python 45/45；研究专用测试没有替代原有门禁。
- 9 个模型配置完成全色域统计：4 基线、4 guard 选中候选、1 既有控制。每个冻结输出均与独立 NumPy 整数 oracle 的全流 SHA-256 一致。23 条原生全色域流也一致：单级只验标量/AVX2，四级另验 C99，控制方案补验三后端。[完整记录](../../report/data/chain-error-v1/native-parity.json)
- 工程提交 `337a3dd` 的[默认/标量/Docker](https://github.com/WyEhNf/flash-chroma/actions/runs/38895302161)和[三个 QEMU 目标](https://github.com/WyEhNf/flash-chroma/actions/runs/38895302299)六项均通过。Linux 默认环境为 31 passed、2 个可选研究模块 skipped；Windows 独立研究环境为 45 passed、无跳过，二者不混称。QEMU 中 portable 的 32 位模型/链对象为 3108/32 字节；RTOS 2048 字任务栈剩余 Cortex-M3 798 字、RV32 761 字，属于整套测试任务的高水位，不能当作纯库或实板资源。[摘录](../../report/data/chain-error-v1/engineering-ci.json)
- 保存 20 条候选选择、10 条逐级分解、8 条最终汇总、800 条逐图指标，70 份模型/选择文件/1024×768 RGB8 热点图片及其哈希。ZIP 约 3.3 MB，完整源表和输出流在本机忽略缓存，仓库保留原始来源和重建方式。
- 未执行容量/方法全矩阵、随机噪声扩展、官方评分、性能比较或实板测量。本阶段不声称通用 SOTA，未自动合并 PR 或关闭关联 issue。

```powershell
$env:PYTHONPATH='python'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:PATH='E:\mingw64\bin;C:\Program Files (x86)\CMake\bin;' + $env:PATH
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:JSHC_FULL_FIT_LIB=(Resolve-Path build-engineering-alignment/libjshc_full_fit.dll).Path
artifacts/error-study-py312/Scripts/python.exe scripts/run_chain_error_study.py `
  --output artifacts/chain-error-study-rerun --executable build-engineering-alignment/jshc.exe
artifacts/error-study-py312/Scripts/python.exe scripts/explain_chain_counterexamples.py `
  --input artifacts/chain-error-study-rerun --executable build-engineering-alignment/jshc.exe
artifacts/error-study-py312/Scripts/python.exe scripts/report_chain_error_study.py `
  --input artifacts/chain-error-study-rerun --output artifacts/chain-error-study-rerun/report
```

环境、代码和计划变化时必须使用新输出目录。拟合缓存单独绑定来源、原始数值源码、准备代码及环境，不将这次研究追加到 PR #9 的旧 run。精简归档位于 [report/data/chain-error-v1](../../report/data/chain-error-v1)。

## 下一步由本轮证据支持的方向

1. 对真实陡峭区域，优先改变网格位置或恢复表示，并以箱约束重拟合作为有界消融；固定表示已证明的下界不会因增加 CG 次数消失。
2. 对压缩/阈值链，优先既有分箱路线及前级跨边界风险；后缀的均匀放大系数不够区分困难颜色。
3. 对均匀色域/自然图的冲突，冻结新的选择集并报告 Pareto；当前 100 图已观察，后续用于选择时不能再称独立验收。所有已有正、负结果保留，不只发布均值下降。

Agent：Codex

Operator：本次会话的项目用户

Task：工程对齐后的四级误差原因研究与第 1/2 项算法推进

Status：四例有界实验及归档完成；实验候选尚未替换默认，后续 PR 待审查
