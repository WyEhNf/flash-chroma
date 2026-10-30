# 赛事连续偏好入口：独立审查

- Agent：`/root/history_storage_audit`；操作人：当前任务用户。
- 分支：`codex/p16-framework-preferences-20261030`；日期：2026-10-30。
- 状态：合同与新实现静态审查完成，未发现阻断问题。本文件不构成性能或官方得分验收。
- 范围：只读查看原赛事模板、适配入口、`fc::select`、历史 #96 证据绑定缺口；不修改生产，不运行完整色域／性能场次。

## 必须保留的赛事合同

1. 原模板 `now_sec`、参考 `lut_sparse_ref/apply_lut256/apply_3d_lut_ref`、RGB欧氏误差 `color_dalta_calc` 不应修改。成功路径 `t0 → Image result17 → apply_3d_lut → t1 → cost` 必须保持，输出申请／清零仍在 apply 计时内；不能拿预分配热计时代替原成绩。
2. 所有拟合、候选选择和联合准备在读第一张图片前完成。赛事 Readme 明确“不利用图片信息”；合成RGB域或预声明探针可以用于LUT独立预处理，测试图和直方图不能参与节点、候选或缓存拟合。
3. 单线程CPU；不能为新标定启用OpenMP、后台候选并发或GPU/NPU。额外Direct表仍需如实列出约48MiB容量，不能用稀疏模型文件大小代表运行内存。
4. 原C/C++模板和data不改，生成独立工程。交付仍为一个完整hpp＋框架main.cpp；新增模块必须进入amalgamate并消除本地include依赖。

依据：`F:/Hackathon/极速焕彩测试框架/Readme.md`；`F:/Hackathon/极速焕彩测试框架/C++/main.cpp:298`；[现有生成器](../../scripts/install_framework.py:123)。

## 指标来源与参数语义

- 新候选必须现场由本次四张原LUT生成，并现场评估质量／时间／资源。建议身份包含按阶段顺序的LUT内容、m/网格/拟合方案、最终模型内容、编译器/构建宏、CPU能力、合成输入生成算法与种子、测量范围与单位；输出足以确认选中项实际被执行。
- 连续的是ABC偏好权重，实际执行仍选择有限候选。`fc::Preference`每维合法范围为[0,1]、总和>0；NaN、Inf、负数、全零、参数溢出均应明确拒绝。偏好不是精度、速度、RAM的线性插值保证。
- `fc::select`要求 `context/model_id/evidence` 非空，它不自行验证这些字符串代表的真实来源，调用方必须负责。不能只把“verified=true”和随意字符串填上，就认为修复了证据绑定。
- 合成采样mean/max是质量代理，不是正式照片集的平均/最差单图误差。若复用 `worst_image_mean` 字段，需要在context/日志说明是synthetic proxy；只有完整RGB域max才可作任意照片mean的保守上界。`max-error`若作用于探针，必须显式说明其保证范围。
- 合成图像ms、逐张图ms和整批Count×图像ms须分开。`max-ms`必须明确时间范围；不要让100图阈值与一张合成图时间混用。
- `auto`原义为“结构证明成功才用曲线，否则Sparse”；ABC选择应有独立开关/模式，不应静默改变旧命令含义。显式指定m/representation/backend与自动候选集合的优先级必须确定并在help中说明。

依据：[选择器字段](../../src/flash_chroma_selection.inc:11)、[输入校验](../../src/flash_chroma_selection.inc:79)、[上下文与预算过滤](../../src/flash_chroma_selection.inc:110)。

## 稳定时间与运行身份

- 默认 `require_stable_time=true`。候选实际计时>0不等于稳定；需要保存重复原值、预热策略、稳定性门限与判定。若没有可解释稳定门禁，应保留time_stable=false，给出不可行/暂定结果，不能硬设true。
- 单轮计时或对本候选重复一致只说明该测量范围内的稳定性，不能称跨机、跨图片或官方性能保证。不要为通过门禁挑最好子集或把失败记录丢弃。
- `Chain.info()`是实际执行后端和表示的来源。结构证明分支会把请求AVX2／direct变为实际Scalar／Sparse；候选记录不能只抄请求值。
- `Chain`不可复制移动，且借用Stage地址与blob。构建候选列表若复制Stage、移动vector或保存 `c_str()` 指针，必须确认直到select和最终执行均有效。重建选中模型后再次核对实际身份、资源和预算，不可只把选中配置名打印出来。
- U8/U16超palette容量是候选不适用，应该记录原因并继续，不应中止其余可用RGB24/Sparse候选，也不能把它算成Sparse数值失败。

依据：[稳定过滤](../../src/flash_chroma_selection.inc:131)、[实际结构分支](../../framework/flash_chroma_adapter.hpp:183)、[不可移动与借用](../../framework/flash_chroma_adapter.hpp:143)。

## RAM硬预算

- 工作区预算约束整个arena：persistent＋temporary＋对齐，当前框架长期持有arena全部容量。运行RAM须至少包含最终模型、arena、Chain与Stage对象，以及若最终main保留的包装节点副本；sidecar_bytes是object_bytes子集，不能重复累加。
- `runtime_bytes >= workspace_bytes`；config.max_workspace_bytes与Request.max_workspace_bytes须一致地约束实际prepare。若模块报告“自有运行内存”，需区别完整进程RSS、原密集参考、拟合/标定峰值和图片缓冲。
- 如果调优时同时保留全部候选Stage、测量向量与参考数据，它们是准备阶段峰值；进入赛事计时前应释放不需要的候选。不能把选中单项RAM当成仍驻留的全部模型RAM。
- `target=embedded/portable`在选择器只允许Scalar／Sparse／单线程；运行配置与实际build宏均须符合。主机框架含vector/ifstream/拟合器，因此其target选项是运行策略或约束，并不自动产出裸机零堆工程。

依据：[对象/arena记账](../../framework/flash_chroma_adapter.hpp:182)、[整arena持有](../../framework/flash_chroma_adapter.hpp:203)、[资源及target校验](../../src/flash_chroma_selection.inc:103)。

## #96目录指标绑定缺口

旧 `scripts/run_flash_chroma.py:78` 的 `bind_evidence` 只验证原测量completed、库SHA、像素SHA、config与输出hash格式；没有将candidate mean_error、worst_image_mean、batch_ms和time_stable逐项重算／绑定回原观测。`p16_frontier.validate_catalog`也只检查结构与自洽，已有docstring明确不新增数值资格。因此修改目录指标、重新生成选择记录及目录摘要后，旧三层绑定仍可能接受；这不是SHA摘要能自动解决的问题。

新入口应完全不读旧catalog，所有进入`fc::select`的候选记录直接来自本次原LUT与实际运行结果。避开旧入口不表示历史P2已经修复；正式交付说明仍应保留该边界。

依据：[旧绑定代码](../../scripts/run_flash_chroma.py:78)、[目录校验](../../scripts/p16_frontier.py:61)、[已有事项说明](../../docs/event-quickstart.md:102)。

## 实现复审记录

- 已发现并向主任务反馈包装节点capacity问题：原main先按位置m（默认33）创建`model.data`，选中更小m后`assign`保留旧capacity，按size计硬预算会低估。主任务已改成新vector构造后swap，避免保留旧节点容量；资源报告也明确shared控制块为估算，不冒充RSS/allocator实耗。
- 生成入口已增加最终`Chain.info()`与选择回执核对，并在进入读图前释放SelectionResult；该保护方向正确，仍待与模块的资源公式及模型身份字段一起核验。
- 已核对图片metadata预检时序：预检从Start Time之前移到SpareLut Time之前，处于选择、最终prepare与raw LUT释放之后；因此即使首次打开图片文件，也发生在计划固定以后，原apply计时片段未受该改动影响。

### 新模块静态复核

- [完整域入口](../../framework/preference_selection.hpp:336)直接接收本次四张uint16原LUT，计算按阶段原值指纹；独立原四级`target`生成256³完整真值，随后逐模型Scalar/Sparse完整域质量评估。没有访问旧catalog、图片路径或图像直方图。
- [质量统计](../../framework/preference_selection.hpp:219)计算RGB欧氏mean、RMS和max。max进入core的`worst_image_mean`字段，报告明确是完整RGB域最大像素误差、可作任意图mean上界，没有冒称实测照片mean。均值／最大像素预算先过滤，再执行原选择器；等于预算允许通过。
- [实际表示合同](../../framework/preference_selection.hpp:233)逐块遍历全部16,777,216输入，输出先投毒再逐字节比较本模型Scalar完整期望流，并记录verified_pixels/hash。U8/U16容量不适用保留错误后继续后续表示。
- [时间标定](../../framework/preference_selection.hpp:180)每次fresh vector resize＋apply在计时内，释放、逐字节比较及消费在外；输入由固定算法生成，与照片无关。重复计时前后各保存交替AB/BA的A/A原值，默认前后均通过5%门才授time_stable；显式allow_unstable才允许暂定时间。该门限是单次本机合成校准控制，不能升级为跨候选随机化或照片性能结论。
- [资源核对](../../framework/preference_selection.hpp:100)与生成器使用相同可控容量公式：model＋整个arena＋对象＋原main节点副本＋shared管理估算；sidecar不重复计，原LUT/图片/prepare峰值/allocator/RSS排除范围在JSON明确。资源条件超限会排除候选，最终main再次按actual Info与预算核验。
- `models/records`预reserve全部空间，所有id/context/model_id的`c_str()`在构建完成后才绑定；选择过程中不再扩容或修改这些字符串。返回选中已拟合Stage的副本，生成器只move到固定shared对象，再prepare；不重新拟合，不读取回执指标驱动旧模型。
- 逐stage/m缓存只复用本次同阶段、同m的采样或independent_ls基础模型；chain_ls仍在各模型的实际前三层下重新拟合第四层，未把不同前缀的拟合结果共用。
- 新模块已进入amalgamate名单，并替换其本地fit_chain_experiment include，保持一个hpp交付。无图选择函数内局部候选、真值、Scalar流与标定缓冲在返回时销毁；SelectionResult在最终prepare核验后、图片预检前释放。

### 已反馈但不阻断的说明

- 模块注释“一次只保留一个Chain。参考已释放”不准确：truth仍保留到函数退出。已通知作者删除“参考已释放”，不改变算法或最终常驻记账。
- 新JSON明确FNV-1a64只用于本次绑定指纹，编译器版本／能力也有输出；它没有独立记录整个EXE／单hpp的密码学SHA。由于不读取旧回执复用选择，不存在旧#96那种目录数值继承路径；归档时仍需将本次报告与实际EXE、单hpp及构建/环境SHA一起绑定，不能孤立文件宣称完整可复现。
- 本审查只读源码，没有运行新全域或性能。数值／性能通过与否以主任务和合同agent的实测结果为准；历史#96旧入口仍未修复。
