# pipeline 发布范围与协作核对

Agent：Codex /root。Operator：本会话授权提交的用户。Task：联合 LUT 与本机 AVX2 实验发布。Status：实验归档完成，Draft；待团队审查及性能复验。

## 范围和来源

目标为 `pipeline`，创建前通过 GitHub API 核对其头为 `3d4d6d9e07df9e24c25f52f733c8535e3d9890e1`，与本地对象一致。Git HTTPS 直连两次超时，改用已连接 GitHub 的 Git 数据接口发布。只发布本阶段文件，不把原研究基线额外的 224 个提交和约 8,755 个文件合入 pipeline。

原实验基线是 PR #92 的 `4a8b27f4f8b4403986bf53b71f01f8616b53327a`；本地研究提交 `8d883699`，移植提交 `41edf7ff`。远端使用相同文件内容重新创建阶段提交，其 SHA 由 PR 正文记录。公共运行时和模型不变。本 PR 不是新的可部署加速方案。

## 复现依赖与已知限制

单独克隆本 PR 可读报告及原始统计，但原生构建和四级存储分析还需要 PR #92 的上述固定提交：包含 `experiments/skylake-andn-normal-runtime/`、`experiments/channel-runtime/channel_runtime.h` 及 `data/p16-unified-models/`。这些依赖不复制进本 PR。可在另外检出的上游固定提交中，以本 PR 的 `git diff --binary pipeline...<PR头SHA>` 生成补丁，再用 `git apply` 叠加本阶段文件；只在新的实验检出中操作。随后执行阶段报告中的构建与运行命令。

68 个模型分析另需本机 `artifacts/local-lut-study/20261016` 的冻结模型及 `summary/best-per-lut.csv`，模型身份在结果中列出；这些大型历史模型未上传。运行照片准备器需要 NumPy、Pillow 及照片原件。此发布没有在 pipeline 上重新编译或测速，原生正确性结论属于原实验基线上的实验二进制。

AVX2 微基准使用确定性合成 ID 表及调色板、真实照片输入地址；其完整 RGB8 比较证明本夹具上的实现一致性，不等于真实四级 LUT 的色差验证或通用 API 合同验证。没有完整 runtime 构造/加载计时、Xeon Gold 6140 性能或官方门槛证据。输出目录不覆盖历史实验；当前运行脚本的 CPU 描述与资格结论是本次实验专用常量，移机复跑必须改为真实环境和重新判定，不能直接使用它出具新机器性能报告。

发布检查发现原 C++ `median` 对偶数样本取上中位数；报告已明确名称，原始 JSON 的 `*_median*` 字段保持历史原值。A/A 仍未通过稳定性要求，不能从这一轮给优化候选排序。差分容量是特定编码的估算，未包含正式容器索引/元数据，也不是对所有联合编码方法的否定；各级网格不同，节点差值不是同一输入色坐标下的函数差值。实现共享网格联合拟合、编码器/解码器和实际加载性能均属于后续任务。

## 协作检查

检索仓库全部 PR 列表（单页未达 100 条），结合流水线、AVX2、差分存储主题，读取 #56/#78/#65/#70/#75/#79/#81/#92 的完整正文及完整 conversation、review、行内审查线程；本次这些 PR 未返回评论或线程。另读取 #7/#8 正文及全部评论，沿基线纠正引用读取 #9 审查及 #37 最终验收。操作前再次刷新关键记录和目标分支。

- [#56](https://github.com/WyEhNf/flash-chroma/pull/56)、[#78](https://github.com/WyEhNf/flash-chroma/pull/78)：固定模型、逐级取整和性能未达标的边界继续保留。本阶段是不同原生微基准，不拼接旧 Numba 时间。
- [#65](https://github.com/WyEhNf/flash-chroma/pull/65)：同核 A/A 噪声；本阶段控制也失败，不据单一统计量晋级。
- [#70](https://github.com/WyEhNf/flash-chroma/pull/70)、[#75](https://github.com/WyEhNf/flash-chroma/pull/75)：原地与分离输出缓存策略不同；本次只研究分离输出。
- [#79](https://github.com/WyEhNf/flash-chroma/pull/79)、[#81](https://github.com/WyEhNf/flash-chroma/pull/81)：既有局部 RGB 差分失败证据；本阶段是跨 SLUT 包体容量分析，不把包体节省宣称为吞吐收益。
- [#92](https://github.com/WyEhNf/flash-chroma/pull/92)：固定模型/内核来源，其未完成的目标 CPU 验证不在本次宣称完成。
- [#9 基线与环境纠正](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[#7 内核身份](https://github.com/WyEhNf/flash-chroma/issues/7)：`337a3dd`、`876e15b8`、`397cc367` 均经 `git merge-base --is-ancestor` 确认存在于 pipeline；历史验证见 [#37 验收](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。本次不改这些实现，不声称重跑历史门禁。
- [#8](https://github.com/WyEhNf/flash-chroma/issues/8)：接口迁移、资源预算和实板验证仍待办。[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4) 当前连接器拒绝读取，保留这一协作检查缺口，不视为无新增意见。

本次只创建 Draft PR，不执行合并或关闭问题。发布验证为当前 Windows/Python 下的语法、JSON 解析、变更范围及 Git 空白检查；未为发布重跑数值实验。后续应先改进测量稳定性和环境自动记录，再以真实模型运行完整合同与配对性能验证。
