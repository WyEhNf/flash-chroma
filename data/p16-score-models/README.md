# 均值口径候选模型

本目录新增max_first与max48，结合原 `data/p16-unified-models` 的default/max41构成四模型对照。[清单](manifest.json)的path_root指向仓库根目录，模型参数对全部图像固定；sidecar仅首级非空。所有模型均为已有Cinema链的稀疏派生，不是任意新LUT的通用答案。

max_first来自`cinema-second-nodes-v1/max_first/candidate`，max48来自`cinema-first-safe-cpsat-accept-v2/candidate`；来源身份及旧独立预测流见[评分选择历史核对](../../docs/stages/2026-10-27-p16-score-selection.md)。本轮统一CPU库已重新验证完整RGB8和真实百图，四张密集原表另独立复核平均误差，见[本轮报告](../../docs/stages/2026-10-27-p16-score-candidate.md)。

同一Striped Purple四张原LUT、固定上游、MIT许可及烘焙约定沿用[原模型来源说明](../p16-unified-models/README.md)；[原MIT文本](../p16-unified-models/LICENSE.stripedpurple)随最终包按原字节复制。这里没有重新分发照片，照片许可不因模型打包而改变。

最终精简包仅选择default和max_first，位于[submission/p16-cpu](../../submission/p16-cpu/manifest.json)。max48和max41保留本次对照身份，不作为均值优先档的默认。
