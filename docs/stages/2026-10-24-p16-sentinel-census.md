# 精确255色哨兵路线：两固定排名的完整模型普查

宽索引288仍有A/A未确认，10bit索引289已有有效低于50%的反例。本阶段先检查另一条精确路线的必要覆盖条件：255个原RGB32颜色作为热palette，ID255仅作哨兵，未命中按原模型回退。实际原生哨兵内核尚未实现，覆盖率不等于速度。

分支`codex/p16-tail-20261023`仍沿`16ae431`共同基线。仅普查原max_first与p99_first，不改模型、不借新max²48失败见证、没有gold/照片/官方源LUT输入或拟合。固定协议`experiments/p16-sentinel-census-plan-v1.json`已在执行前存在；运行源与模型冻结SHA为`ddcc27123076038336ec262d3f39192116c785ffbc3cf4266de3418da9312320`。

## 方法与口径

冻结288 DLL为`d95332e9ac8b56a9d589bf176a5b020e2d60a176d1f360594a0300b5efae5b9f`，两个模型各prepare一次，安全copy ABI导出whole-cache、完整升序RGB32 palette及16,777,216项实际uint16 ID。物理表按`R|(G<<8)|(B<<16)`排列，末端4B owned guard单列且为零；不能当作canonical的`R<<16|G<<8|B`输入顺序。

cache排名对全部cache槽计频，包含未填充零槽；domain排名对完整逻辑ID计频。两者均固定频数降序、RGB32升序取前255，没有扫描数量、剔除零或按结果改排名。对每种排名分别按canonical B最快的连续8输入，以及物理R最快的8项控制顺序，记录哨兵lane数0..8全部直方图。

NumPy分块精确计数与独立Python整数Counter分别核完整域/缓存频数、前255名、两顺序逐8项直方图；所有包总数为2,097,152，lane加权总数恰等未命中像素数。没有第二份完整canonical ID表，普查只持有一份32MiB导出ID，频数块65536项、canonical布尔块最多4个R平面。原运行时完整prepare的暂态与句柄容量照实保留，普查过程不当作部署内存峰值。

## 实际覆盖

|固定模型|whole-cache色数|全域实际色数|排名|像素命中率|任一miss包率|全miss包率|
|---|---:|---:|---|---:|---:|---:|
|max_first|603|336|cache top255|96.810532%|11.462116%|0.966406%|
|max_first|603|336|domain top255|99.782550%|1.049328%|见完整直方图|
|p99_first|703|380|cache top255|94.177049%|19.876051%|1.731730%|
|p99_first|703|380|domain top255|98.489189%|7.259846%|见完整直方图|

表中包率为canonical顺序，不是100张照片的包率。若任一miss导致整8lane执行原首级插值与后缀cache，约97%的像素命中仍可能伴随约11%的回退包；不能从像素命中率直接计算速度。两种排名的共同热颜色仅233/229个，固定cache频数并不等于实际输入域频数。

零RGB是合法输出：max_first全域有922,236项，p99_first有923,008项，均进入cache top255。whole-cache零槽分别17,941/18,029，其中几何范围可证明非法未填充的均为17,822。其余119/207个合法零槽不能直接归为不可达；本阶段没有逐合法cache槽的可达性证明，也没有用“零是空洞”删掉实际零输出。

max_first/p99_first原288持久容量分别35,495,456/35,495,856B；其32MiB ID载荷为33,554,436B含guard。本普查没有实现更小的native表，因此不把设想16MiB表填入内存/速度六档矩阵。实际导出ID（含guard）的SHA分别`09c3ae1b51927a517498469249dbca6611d590b9dec4a7c30d32f363e00090e8`、`31ece1ec1599131c45987ad759d55fdadeaca1038efaf137f01db33c6bc33ea7`。

## 准备成本与下一步边界

cache排名可以在已有cache准备后计频，随后将每个cache值映射到0..254或哨兵，进行一次首级全域编译。domain排名需先得到全域频数，因而需要额外完整域工作，或32MiB uint16暂表再压成16MiB；本阶段的离线排名不能作为免费运行时输入。两个固定排名都保留，当前仅考虑先实现cache排名的独立候选，不事后挑更有利排名宣称已达标。

设想回退保持原逐级RGB8 Q16四面体语义；旧whole-cache≤255的8bit成功应继续优先。新哨兵路径的资格、全部输出/边界/guard、prepare峰值、热与完整作业计时仍须独立冻结与验证。任何有效模式低于50%继续拒绝，A/A失效不授档，不恢复288/289结论。派生表及sidecar的官方许可仍未知。

## 环境、复现与证据

Windows 11 build26200、Ryzen9 8945HX、32逻辑CPU、Python3.12.14/NumPy1.26.4；原DLL为GCC15.2的AVX2实现，OpenMP4、DYNAMIC=FALSE、WAIT_POLICY=PASSIVE，OPENBLAS/MKL各1。本阶段无正式计时、无AVX512、无Intel服务器或跨平台验证；原生prepare诊断中的时间仅随状态保存，不授吞吐资格。

```powershell
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe scripts/census_direct_sentinel.py --freeze --output artifacts/p16-sentinel-census-frozen-v1
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe scripts/census_direct_sentinel.py --frozen artifacts/p16-sentinel-census-frozen-v1/frozen.json --output artifacts/p16-sentinel-census-v1
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe scripts/archive_direct_sentinel_census.py --output report/data/p16-sentinel-census-v1
```

输出目录必须全新，不能覆盖原件。`report/data/p16-sentinel-census-v1/`保存原冻结/结果/协议、全部ID与cache快照`raw.zip`、实际执行Python源`source.zip`及去重原稀疏模型`models.zip`，manifest和independent-check逐成员SHA/CRC。原288构建闭包仍见既有`p16-direct-u16-ilp-native-20261024`阶段，本次未重新构建。额外封存脚本不冒充早于普查冻结。Git按显式白名单核stage/HEAD原字节，仅说明及attrs沿用LF。

[Lemire/Boytsov](https://arxiv.org/abs/1209.2137)提供整数压缩与例外处理的研究背景，但其顺序批量解码结果不能直接外推本RGB随机查询或哨兵包回退的速度。本阶段只提供两固定排名的必要普查，不主张新的原生后端已经通过用户底线。
