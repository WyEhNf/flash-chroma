# 三方向独立分支的协作核对

Agent：Codex `/root`；Operator：本会话项目用户；日期：2026-10-24（Asia/Shanghai）。本次三个分支均从`16ae431030a5c734a1485089c8b58d15b21902f6`开始，分别研究精度、速度、内存及可移植性。PR目标统一为依赖基线分支`codex/wsl-memory-budget-20261023`，不把三方向相互合并，也不自动合入main。

创建前已fetch GitHub；main仍`b19c5a0c8f67c3b4822692682698fb06462b7ed7`，依赖头仍16ae431。完整PR集合79项与初始快照逐正文/头比较无变化。读取相关#42、#64、#67、#75、#78、#85正文及全部可用comment/review/行内线程；核对仓库全部22条issue conversation与空行内评论集合，沿#5/#9/#12/#13/#14/#15/#16/#27/#37核对来源、基线/环境、完整域与逐图风险、CVaR保护等记录。原始正文/评论及具体范围保存在[协作原文](../../report/data/p16-three-directions-collaboration/README.md)。

- [PR9基线/恢复环境意见](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)及[Issue7实际内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7)的修复337a3dd实际为共同基线祖先；876e15b8的CVaR提交保护、397cc367的相等mean修复同样包含。本轮保留原实现及历史验证，不用这次新实验冒充重跑旧测试。
- [Issue8](https://github.com/WyEhNf/flash-chroma/issues/8)最新正文已说明两套C99共同集成。最终接口决策/迁移、完整目标资源预算、实板与功耗仍未完成；新增实验ROM及wasm32核验不等于这些事项已关闭。
- [PR42](https://github.com/WyEhNf/flash-chroma/pull/42)的分输出表示与普通SLUT区分继续保留；[PR64](https://github.com/WyEhNf/flash-chroma/pull/64)/[PR67](https://github.com/WyEhNf/flash-chroma/pull/67)/[PR75](https://github.com/WyEhNf/flash-chroma/pull/75)旧三倍及A/A失败不被重写为成功。本次六档标准来自用户新要求，50%指精度与吞吐保留底线，并非内存必须减半。
- [素材意见](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072)的色彩域/许可边界保留：Cinema为数值四表链；100张照片已见，非新盲测。未上传RAW、照片像素、大型参考表或厂商二进制。
- Discussion4当前fetch接口不支持，旧审计成功不能替代本轮最新回复刷新；明确保留读取缺口。本轮只交付Draft研究PR，不执行合并或issue关闭，因此没有依赖缺失检查作合并决定。

本轮每个阶段的源码、模型/输入/产物SHA、环境、目的、原始轮次、实际核验范围与负结果分别由各阶段文档绑定；没有官方Threshold/派生表许可、指定服务器或实板的新验收结论。PR保持Draft并持续研究，不升级公共默认或冠军。创建前还会再次确认目标头与新增意见，发布后续提交前同样按本规范检查。
