# 官方试跑阶段交付说明

Agent：Codex /root；Operator：本会话授权提交的用户；Task：把官方框架试跑代码和结果提交到仓库；Status：本机实验与归档完成，Draft 待审。

## 范围和分支

工作分支 `codex/official-pr95-tests-20261029`，目标为 #95 的 `codex/p16-frontier-header-20261027`。起点与实测内核均为 fb7e195215f14df9f635394d75cde0e0e69c82c9。阶段提交及实际 PR 状态见本阶段 PR 的提交列表；本次不合并。

本阶段新增 `code/official-pr95-20261029`、`report/official-pr95-20261029`，并为代码和证据设置 Git 原字节属性。六份实测源保持原字节；另加归档核验器和复现目录说明。原 C++ 生成物与官方框架放入 executed-sources.zip，供审查差异。报告列出网格与节点采样、Q16 恢复、官方均值、补充 p99/max、时间和内存。未改变 #95 内核、默认模型或 CI。

没有带入此前 c4a1d794 审查材料或 594fbae8 本地流程修复提交。官方大数据约 856 MB、模型/图片输出/可执行文件继续保留本地；输入与全部本地输出的身份可由清单追溯。归档中的 evidence-manifest.json 是原实验目录的历史清单，不意味着其每个大文件都被上传；archive-manifest.json 才是本次实际发布的文件集合。

## 已完成的验证

实验结果见[report.md](report.md)。本次发布只进行静态及证据复算：Windows11 / Python3.12.7，Python AST 解析、源字节与 zip 对照、全部 SHA、8 份逐图平方误差直方图复算、两组汇总、未绑核与绑核场次的全部 144 条批次耗时复算、官方均值核对、Git 差异及暂存字节核验。命令为 `python code/official-pr95-20261029/verify_archive.py`。没有为提交再做拟合、数值全域、性能或全仓门禁；原实测的机器、编译器和所有未覆盖范围继续保留。

## 协作检查与关联事项

读取完整仓库 issue/PR 索引 90 项，第二页为空；按单头运行库、官方接入、线程、证据绑定主题核对 #95/#96/#97/#94/#89 的完整正文、conversation/review/行内线程，均无返回意见。沿引用检查 #7/#8 全文和完整评论、#9/#12/#37 历史纠正意见及版本化 #96 review.md。关键词“官方”搜索无命中不能代替完整索引检查；索引发现了新增 #97，已补读。

| 原始记录 | 当前状态与本阶段处理 |
| --- | --- |
| [#95](https://github.com/WyEhNf/flash-chroma/pull/95) | 仍为 fb7e195；精确提取两份头文件。旧 4T 成绩不适用于本次官方单线程约束，新增 1T 结果，不改写旧证据。 |
| [#96](https://github.com/WyEhNf/flash-chroma/pull/96) | 验证器容量中断、目录指标绑定两个 P2 在目标分支仍未修复。本次独立测试器记录 Capacity 并继续，不走旧目录选择器，不宣称修复旧入口。594fbae8 本地修复不在本 PR 中。 |
| [#97](https://github.com/WyEhNf/flash-chroma/pull/97) | 新工作台/赛事包以 RGB8 二进制表为入口，仍报告官方协议未知、含 1/4T 验证。本次官方包实际是 256³ 文本整数、/16 量化、轴/通道反序约定、禁止多线程且不允许用图拟合；需后续单独整合，不能把本次结果当作 #97 已接入。 |
| [#94](https://github.com/WyEhNf/flash-chroma/pull/94)、[#89](https://github.com/WyEhNf/flash-chroma/pull/89) | 既有性能 A/A 失败、未知 LUT 与 direct 许可待办保留；本次未授予稳定加速资格。 |
| [#7](https://github.com/WyEhNf/flash-chroma/issues/7)、[#9基线与环境意见](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540) | 337a3dd、876e15b8、397cc367 实际均为本次目标祖先，历史审计见 [#12](https://github.com/WyEhNf/flash-chroma/pull/12#issuecomment-6229792983)、[#37](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。没有重判旧修复失效，也没有冒称重跑历史回归。 |
| [#8](https://github.com/WyEhNf/flash-chroma/issues/8) | 最终接口迁移、实板和资源预算仍待办，本次 Windows 官方样例不能替代。 |
| [Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4) | 本次连接器拒绝该端点，保留无法读取的缺口；不等同没有问题，不执行依赖该检查的合并或关闭。 |

发布前已成功 fetch origin，目标没有新提交需要整合。初次 fetch 因沙箱 .git 只读失败，授权范围内提升执行后成功；提交前第二次 fetch 遇到 GitHub 443 连接失败，同轮连接器刷新仍确认 #95 为 fb7e195、#96/#97 的头及空意见未变，保留网络失败记录。原始 Windows CRLF 证据使用 -text 保留，空白检查明确将 CR 识别为行终止字符；不改写原始测量以消除格式提示。具体实际提交号与发布状态在 PR 中记录。

## 未完成事项

GCC13.2 / Xeon6140、官方分数与阈值、direct 表许可、最终百图和未知四 LUT 组合均未验证。Readme 说明 Test1 不用于最终验收；Test2/3/4 完全相同，样例覆盖有限。保持 Draft；提交的是可复核实验，不是赛事达标声明。
