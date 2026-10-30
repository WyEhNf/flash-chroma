# 修订78两组发射诊断档案

原始环境：Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu Linux6.18.33.2 / Python3.14.4；运行时为PR71冻结GCC15.2 AVX2+可选BMI1构建。不是Skylake实测。

`raw/`为8项诊断全部原件，`probe/`为一次事件可调度性探测，`preflight/`保留执行前发现的失败留证缺口及从未执行的v1；`independent/`独立解码32组原始72字节计数、单位/求和/身份/输出/页状态。`manifest.json`记录原字节，`archive.py`只复制并核对身份，不加载原生库。复用PR71已保存的78及driver构建，不重复保存二进制；大输入和固定模型仍按冻结SHA恢复。

目的为负载诊断，不计算相对23吞吐，不重测旧失败候选。8预热+8计数全部输出/源/保护区/实际团队和绑定/THP通过；完整RGB8证明来自未变的PR71。事件解释、单位、限制和有限后续假设见[阶段说明](../../../docs/stages/2026-10-21-skylake-dispatch-diagnostic.md)。可重叠阻塞原因不相加，两组不是同一时刻；WSL可调度并非全部vPMU语义已校准，零事件不证明没有瓶颈。

`remote-snapshot.json`保存新71全文及评论/review/线程、issue7/8正文/全部评论和旧64份全文一致性回执；旧正文仍在PR71档案内。Discussion接口缺口保留，不合并或关闭。总体三倍尚未完成。
