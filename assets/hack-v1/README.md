# 独立压力图片与小型反例回放

本目录由 `python -m lutlab hackset build` 构造，配方、源字节哈希及验收边界见 [数据集说明](../../datasets/problem16-hack-v1/README.md)。

- `stress.txt`：14 张合成压力图，全部为 1024×768 RGB8 PPM；与自然照片和历史 benchmark100 分开。
- `images/`：四种颜色分布的三种布局，以及两张局部窄峰诊断图。
- `replay/`：恒等控制与采样漏峰候选，各含四张合法 m17 稀疏表、固定颜色和两套参考输出。

这些文件没有使用外部图片素材。真实场景对照引用原有 [100 张日常照片](../photos/README.md)，不复制或变更其来源说明与使用范围。
