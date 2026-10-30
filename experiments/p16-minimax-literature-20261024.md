# 误差尾部优化的补充一级资料与适用边界

检索日期为2026-10-24。本记录只整理原文或作者机构记录，不把论文结果当作本项目测试。

- [Monga、Bala，2010，作者所在机构记录](https://pure.psu.edu/en/publications/algorithms-for-color-look-up-table-lut-design-via-joint-optimizat)：讨论节点位置和值的交替优化。对本项目的启发是同时审视坐标与节点自由度；本题四级RGB8量化目标不因此具有凸性。当前固定122节点集合的下界也不能代表变更坐标后的下界。
- [Andriani等，2021，IS&T完整原文](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/ei/33/16/art00002)：非均匀坐标分配可改善存储与误差的权衡，但暗部节点过密会牺牲亮部。对本项目的启发是设置全域与逐图门，而非仅按局部高误差加密；其ICtCp指标和实验收益不移用到本题RGB欧式误差。
- [Agar、Allebach，1996，出版社摘要](https://library.imaging.org/cic/articles/4/1/art00002)：以最大绝对误差设计顺序线性插值网格。这里只读到摘要，未据此实现完整算法；单通道绝对误差与本题三通道欧式误差也不同。
- [Celebi等，MACT原文](https://arxiv.org/pdf/1009.0854)：研究已知色空间函数的minimax近似。当前任意艺术LUT链没有已证明的解析分解，不能直接套其函数近似或速度结论。

本阶段实际安排仍为：先由完整整数直方图检查固定可调支撑外的p99/最大误差下界，再决定是否扩大支撑、修改节点或坐标。任何新拟合候选仍需全部色域和百图后验门、三分母速度资格及容量账单；不以minL1代理、文献平均误差或感知指标替代用户要求。
