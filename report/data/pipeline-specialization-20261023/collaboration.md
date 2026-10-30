# 发布前协作检查

Agent：Codex /root；Operator：本会话授权提交的用户；日期：2026-10-23。Task：固定四级专门化实验归档至performance；Status：实验及发布检查完成，PR待审。

用户明确要求从pipeline创建performance。本次以pipeline的3d4d6d9e07df9e24c25f52f733c8535e3d9890e1为起点；工作分支codex/pipeline-specialization-20261023只添加本实验包，不直接向目标分支提交实验，也不执行合并。

检索仓库全部PR与issue正文，针对pipeline、固定四级、专门化、计时控制和误差语义，完整读取#5/#9/#12/#37/#38/#41/#42/#43/#44/#55/#56/#65/#68/#72/#77正文及分页评论、review和行内意见，读取#7/#8正文和全部评论。关键#42/#55/#56/#65/#68/#72/#77的GraphQL审查线程均为空；Discussion #4全文、评论和回复已读取，全部分页完成。最初GraphQL请求超出节点上限，缩小查询后成功，不存在未读取却当作没有问题的讨论缺口。原始记录见collaboration.zip。

|相关意见|当前处理及本次证据|
|---|---|
|[#9基线和环境](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[#7执行内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7)|修复337a3dd实际包含于pipeline祖先，casebook仍调用execution_proof。876e15b8、397cc367也已包含。历史验收见[#37](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。本次不改这些实现、不冒称重新运行旧回归；实验固定模型/尺寸/代码/输入哈希，完整色域和逐次百图输出核对。|
|[#5素材与色彩域](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072)、[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)|模型相对源LUT的RGB欧氏误差与运行时逐字节正确性分开；不称CIEDE2000，不称真实ISP或盲测，不把零运行时差异称为零拟合误差。|
|[#42](https://github.com/WyEhNf/flash-chroma/pull/42)、[#56](https://github.com/WyEhNf/flash-chroma/pull/56)|分别提供固定数值源码和六组模型/恢复组合。两者当前无评论、review或行内意见。本次完整色域只证明这六组候选与动态基线一致；不替代#42的C++验收。|
|[#43](https://github.com/WyEhNf/flash-chroma/pull/43)、[#44](https://github.com/WyEhNf/flash-chroma/pull/44)|已存在原生固定组合与多项负结果；本次为Intel/Numba六组实验，不声称首创专门化，也不与AMD原生时间拼接速度比。|
|[#65控制校准](https://github.com/WyEhNf/flash-chroma/pull/65)、[#68](https://github.com/WyEhNf/flash-chroma/pull/68)、[#72](https://github.com/WyEhNf/flash-chroma/pull/72)、[#77](https://github.com/WyEhNf/flash-chroma/pull/77)|保留环境噪声和原生性能缺口。本次两新进程、同内核A/A控制、同轮配对，失败不重试择优；不将外部PMU现象归因到本机Numba。|
|[#8接口/资源/实板](https://github.com/WyEhNf/flash-chroma/issues/8)|双C99已集成，但接口迁移、预算、实板仍待完成。本次不声称解决、不关闭issue。|

本次候选统一采用门槛未通过，保留负结果且不替换默认。原生后端、其他模型、线程扩展、启动成本、正式数据和资源验收继续待办。PR仅归档有界研究，保持Draft以明确性能推进仍未达到采用条件；不执行merge或关闭事项。

提交时静态复核代码语法、全部归档成员SHA、六组完整色域证据、逐轮输出SHA、配对统计和门槛。环境为Windows 11 / Python 3.12.7；未重新测速或拟合。对应提交及操作前刷新结果见PR正文；检查成功不等于批准合并。
