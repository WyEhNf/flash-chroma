# Velvia误差是否主要出在裁剪附近

Agent：Codex；Operator：WyEhNf；状态：完成一次只读归因，未提交、推送或PR。

本阶段没有继续拟合，而是读取原2dd已保存的完整输出、原表与原60训练图频数，按参考RGB是否有0/255、邻饱和码或三个通道完全内部做互斥统计，并拆开饱和通道自身与其它通道残差。

照片主要误差没有集中在裁剪附近：内部组占69.642%像素、73.531%距离误差；端点和邻饱和合计占30.358%像素、26.469%误差。参考端点通道自身仅占全部照片SSE6.111%。cube较大尾部确与端点/邻饱和有关，但G/B=255条件的大部分误差来自其它通道，不能把相关性写成裁剪成因。内部组也不等于检测出内部陡变。

据此停止把clip-aware当作双mean主要改进路线，本轮不追加候选。完整cube和60图测度的逐组mean/RMS、数量/误差和及>3/>7贡献，六种端点通道条件的残差拆分，均保存于[精简归档](../../report/data/velvia-output-clipping-v1/README.md)。脚本为`scripts/explain_velvia_output_clipping.py`，计划为`experiments/velvia-output-clipping-v1.json`。

环境为Windows11 26200/Ryzen9 8945HX，Python3.12.14/NumPy1.26.4、BLAS环境1；目的为已有数据关联归因。来源、频数数组与training分组SHA均核对；0模型前向、0图片解码，没有原生后端、新全域输出、百图或性能测试。没有修改核心/根driver、默认或已验基线，没有官方/SOTA结论。
