# 协作者意见审计与研究栈集成

Agent：Codex

Operator：WyEhNf

Task：审计协作者建议、对齐开放PR并按用户明确授权合入main

Status：审计完成，集成正确性及合并状态以PR的最终记录为准

## 范围与结论

用户明确授权“审计Collaborator对我的PR的建议，完成对齐后直接将我的PR merge进去”。当前属于WyEhNf的开放工作为#12至#34，共23个PR，线性依赖从main的dec1020到e8e3629。此授权允许完成合并，不修改AGENTS.md，不升级默认/冠军，也不将研究候选的已披露精度失败视作官方达标。

逐项读取23个PR全文、完整评论/review/行内线程、关联#5/#6/#9及issues #7/#8，检索全仓问题。共17条协作者审计评论；#28至#33无单独评论，栈顶#34的整体复测及各阶段既有证据分别保留。直接使用GitHub GraphQL读取Discussion #4全文，确认评论为0、无后续分页；此前网页404的访问缺口于本轮消除，不改写旧阶段记录。

全部23个原头提交各有六项CI成功，共138个原检查；无提交review或行内线程。完整公开快照、头SHA、依赖、审查原链接与CI链接在[审计证据](../../report/data/pr-stack-audit-20261017/audit.json)，不以CI绿色或协作者结论代替源码核对。

## 逐项对齐

| 来源 | 意见与核对 | 本轮处理 |
| --- | --- | --- |
| #12审计、#9两项P2、#7 | m33唯一基线、环境恢复身份、实际执行内核绑定 | 核对337a3dd实际在最终栈，报告调用唯一选择器、恢复调用claim_run、登记调用执行证明；已有正/负回归纳入本轮集成门禁 |
| #12审计、#8 | 双C99接口范围与portable集成状态 | 合入当前共同合同，保留embedded/portable各自API、所有权及失败语义，不在本次选择删除或强制迁移；两套实现已有共用oracle/宿主差分/QEMU，接口最终迁移和实板资源继续由#8跟踪 |
| #13至#27审计 | 研究收益、照片退化、局部界和有限搜索的边界 | 保留原始负结果和预算，不升级默认模型；#26的CVaR保护已由#27补齐，后续相等mean误拒由#29修复，集成最终状态包含两者 |
| #34整体审计 | 117项研究合同、归档SHA、有限箱穷举交叉核对、真实全域输出 | 与本机输入/模型/流及现有源审计证据核对；协作者的WSL复测为引用证据，与本机及托管CI分开记录，不冒称本机重跑这些实验 |
| Discussion #4、#5素材意见 | RGB距离口径、表达能力限制、源插值和素材许可 | 直接核对讨论无新意见；保留RGB欧氏码值、逐级RGB8、未知摄影域、授权及源适配边界 |
| 各PR合并顺序建议 | 原始阶段次序、父base和合并后CI | 保留全部原始提交次序，以最终栈建立一个集成PR统一验收后合入main，再将原PR的目标对齐main核对包含关系；避免把已由后续修复的历史中间态单独作为最终状态合入 |

协作者17条意见均未报告新增阻塞缺陷。本轮没有因此放宽验收或豁免已知缺陷：最终栈实际包含337a3dd、#27和#29修复，研究中的未达标指标、后续接口迁移/实板以及未知官方阈值均明确保留。

## 集成方式和验证目的

原main dec1020是栈顶e8e3629的祖先。只读`git merge-tree --write-tree dec1020 e8e3629`结果与栈顶树完全相同：`5483439a1cf9763727e016dd3f3b0549a2b4fe71`。不存在要靠覆盖解决的内容冲突。新集成分支只增加本阶段说明和审计证据，算法/运行时/数据/模型/构建设置不再变化，历史源码身份和归档保持。

以merge commit保留原SHA及其依赖顺序，不squash/rebase，不删除开发分支。集成PR目标为main；原PR更新合入依据并对齐目标，待其头实际被main包含后检查GitHub的merged状态，不能以手动closed代替已合并。用户的授权来自当前会话，协作者评论本身不是合并授权。

测试目的为最终合入状态的数值契约、缺陷回归和跨实现一致性；没有新拟合、性能扫描、100图调参或实板实验。本机复用已有Release默认原生产物，因为Git核对#12至#34的cpp/portable/embedded、CMake/锁文件与共享资产完全相同；这一来源边界明确保留，原生库不以Python头SHA冒充重新编译。

环境：Windows11 10.0.26200 / AMD Ryzen9 8945HX16核32线程；Python3.12.14、NumPy1.26.4、SciPy1.15.2、Numba0.60.0、llvmlite0.43.0、Pillow10.4.0、pytest8.4.2；MinGW GCC15.2、Release、默认AVX2/OpenMP开启，完整拟合库/portable/embedded及共有夹具启用。OMP/BLAS/MKL=1、NUMBA_NUM_THREADS=4；原有内核合同自行覆盖适用线程路径。托管默认/标量/Docker与三类QEMU的最终集成提交证据在PR补记，不借用原23头的绿灯。

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:PATH='E:\mingw64\bin;C:\Program Files (x86)\CMake\bin;'+$env:PATH
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:NUMBA_NUM_THREADS='4'
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/check_correctness.py --build-dir build-engineering-alignment
```

本机一次集成回归成功：CTest **3/3**（28.95秒），Python **117 passed / 0 skipped**（131.00秒）。15条警告为既有NumPy构建信息展示提示及matplotlib/pyparsing弃用提示，未作为失败或被忽略的研究测试。原生程序SHA `ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a`，完整拟合库SHA `ae2ce37ed38a34b21435f797bced96c0f551f872c057eeb263cc719c1f98d061`；源码对应e8e3629，随后仅添加本阶段文档/证据。完整日志与哈希保留，不重跑所有阶段实验。

## 引用复测与未完成工作

[协作者#12审计](https://github.com/WyEhNf/flash-chroma/pull/12#issuecomment-6229792983)报告默认/标量各45通过；[#34整体审计](https://github.com/WyEhNf/flash-chroma/pull/34#issuecomment-6229807001)报告两配置各117通过、CTest各3/3、固定30个小箱750赋值穷举交叉核对。WSL2/i7-13700H/Python3.12.15/GCC16.2.1，与本机环境不同，不作性能比较；各两条NumPy建议安装PyYAML的显示警告，未跳过研究测试。

协作者另重建Velvia参考表SHA `6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7`，PR32模型在三种原生路径全域输出SHA均为`7d07c9a27bb0a9dad4620fcd3d36bb8d5db505de2b1e1d433b69ef6423fae62f`，7865色独立有理源审计0字节差异；与本项目冻结证据一致。这是协作者复测声明及相同哈希的交叉证据，不冒称本轮又进行了全域/100图重新验收。

官方数据/Threshold未取得；照片历史已见、非盲验。Lomo/Velvia仍有历史尾部失败，#33/#34无新精度收益。跨实现数值兼容与QEMU不等于实板速度、实时性或功耗。#7/#8不因本次合并自动关闭；原问题已修复部分与持续待办将在协作记录对齐。
