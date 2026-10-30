# 统一运行时的固定Cinema研究模型

本目录随阶段代码提供两套固定稀疏模型：`default/`为373a，`max41/`为最大误差平方41的精度选项。每套包含四个SLUT和首级Q16侧表，共457,468B；逐文件身份见 [manifest.json](manifest.json)。模型来自已有精度研究，用户更换输入LUT时需要重新稀疏化拟合，不能将这两套固定模型当作任意新LUT的答案。

## 第三方来源、版权与许可

这条Cinema链使用四张真实发布的创意LUT，依次为 Striped Purple 的 **1910s、1920s、1930s、1940s**，均来自 [stripedpurple/color-grading-luts](https://github.com/stripedpurple/color-grading-luts/tree/9757e8b5147693cab49c3fd674bf23dbe28d6c8e/Cinema%20Through%20The%20Ages)。它不是由本项目随机生成的合成LUT。

上游固定提交为 `9757e8b5147693cab49c3fd674bf23dbe28d6c8e`；原下载包SHA256为 `2eb1ababfb493c97a2936eca8fe0a77bbc861fefc30e2098be214a98348a2668`。原始来源与逐文件URL分别保存在 [source-lock.json](../../assets/LUT/source-lock.json) 和 [LUT manifest](../../assets/LUT/manifest.json)，收集入口为 [collect_existing_luts.py](../../scripts/collect_existing_luts.py)。这些既有锁文件未因本次模型打包改写。

原作者的许可为 **MIT License，Copyright (c) 2020 Nixua**。本目录 [LICENSE.stripedpurple](LICENSE.stripedpurple) 从仓库保存的 [上游LICENSE](../../assets/LUT/sources/stripedpurple/LICENSE) 按原始字节复制，SHA256均为 `f9ec0414792341c7d72b8a95049ba770d543357836d4cfe71ec103460fdb242c`，保留完整版权、许可条件及免责条款。重新分发这些原始或派生资产时须继续保留该声明；不把第三方资产重新改授其他代码许可证。锁定来源仅列出LICENSE，本地该源目录没有单独NOTICE，故没有编造一份上游NOTICE。

原 [UPSTREAM_README.md](../../assets/LUT/sources/stripedpurple/UPSTREAM_README.md) 保留作者说明：大部分或全部LUT通过Photoshop的Color Lookup Table Export Plugin创建，并仅在Photoshop中测试。这里按其声明归属来源，不把它扩写成所有文件的逐项制作证明或色彩空间认证。

| 串联级 | 原始文件（位于 `assets/LUT/sources/stripedpurple/Cinema Through The Ages/`） | 原始字节SHA256 | 展开256³ RGB8表SHA256 |
| --- | --- | --- | --- |
| 1 | `Striped Purple - 1910s.cube` | `2ae2f4c62d028e41cf132f0d87f9098240fb8232195e602ed316c94cc0d38538` | `37b1fa642957a648294301c281d6e261391857e93bd163fe2fd592df7f673944` |
| 2 | `Striped Purple - 1920s.cube` | `8f4f6ece25f0979b952c77e0d62a0e695310201a882fa8d7002471af0ff430f4` | `ccd454354df9a9e7da30e1022da31e66d65d2051b775a15995b76de09523aae8` |
| 3 | `Striped Purple - 1930s.cube` | `a82f33eaeb5e834c15d845e3ce2cda26d9f2aadb179af3dd25b79cceec838bf9` | `733f2578420247456b7b5bd07aa570c8d1b6a50173b1494a27c7dbaa5c330cfd` |
| 4 | `Striped Purple - 1940s.cube` | `d568987e472432d63afba500d4daa26022c86d1db1739056c19431e5175baee7` | `5ffcbb5032b6c8a10aaad2c6649fa1ad85fd7e920121d8b0460ec6f181cb7b00` |

## 参考表与派生模型配方

四张原始CUBE均为64³网格，输入域0..1。原 [source_lut.py](../../python/lutlab/source_lut.py) 的 `bake_source` 和 [研究驱动](../../scripts/run_chain_error_study.py) 将每张表以三线性插值展开到完整RGB8输入域；输入是RGB8归一化码值，轴语义R/G/B、文件R最快。输出先裁剪到0..255，再按 `floor(x+0.5)` 取整为RGB8。四表完整真值按上述顺序独立查表串联，每级均保持整数边界。

完整源表的路径、SHA和数值政策由 [cinema-current-anchor-v1.json](../../experiments/cinema-current-anchor-v1.json) 的 `tables` 以及原 `artifacts/chain-error-cache/source-*/ready.json` 绑定。本目录仅交付稀疏派生模型，不复制四张约48MiB的展开参考表，也不改变原CUBE文件。

`default`沿用首级73dc15fe…、原第二级933a4311…、第三级95cb685e…和mean-budget末级5b8be3d…，对应373a完整RGB预测流。`max41`由首级07c9f252…、第二级904e30a1…、相同第三级及末级组成，来自固定可行性求解后的完整质量验收。首级 `channel-frac.bin` 为研究中的分输出Q16坐标，不是完整输入域答案表。完整路径与SHA见 [三方向汇总](../../docs/stages/2026-10-26-p16-unified-research.md)；对应阶段为 [末级预算研究](../../docs/stages/2026-10-24-cinema-arrival-budget.md)、[第二级节点研究](../../docs/stages/2026-10-24-cinema-second-nodes.md)及 [max41完整质量](../../docs/stages/2026-10-24-p16-cinema-current-full-quality.md)。

Cinema在这里表示上述创意LUT的数值四级组合，没有各级摄影色彩域相容的证据，不能据此称为经过认证的ISP、自然摄影或真实相机处理管线。原始64³源表先经固定插值展开，参考表本身带有该来源结构，也不能把这类数据的拟合表现推广至任意未知LUT。此处保留 [PR5素材审查意见](https://github.com/WyEhNf/flash-chroma/pull/5#issuecomment-6209812072) 所涉来源、色彩域与使用边界；本地MIT来源确认不等于赛事官方认可分输出侧表或派生direct缓存格式。

## 数据与运行时使用边界

已报告的百图精度使用 [固定100张日常照片](../../assets/photos/README.md)：5张Kodak、14张DPED和81张DIV2K，来源与权利说明见 [照片manifest](../../assets/photos/manifest.json)。这些照片在历史拟合/验证研究中已经被使用，60/20/20划分保留为历史分组，不重新描述为新盲测。照片许可独立于上述MIT LUT许可；特别是DIV2K仅供学术研究的使用限制不因模型打包改变。本目录没有新增分发照片像素。

离线完整RGB8 oracle用于核对稀疏模型、各后端和真实百图输出。manifest只保留其SHA256；**运行时不读取oracle，不按输入图片修改稀疏化参数**。派生direct表若启用，应从已固定四级稀疏模型按逐级整数语义等价生成，不能加载参考输出流代替计算。模型逐字节正确、历史精度值、官方阈值通过和目标机吞吐是不同结论，分别以各自验证记录为准。

本说明由Codex在2026-10-26静态核对：四张本地原始CUBE的实际SHA均与既有manifest相同，许可拷贝SHA相同；没有重新下载、烘焙参考表、拟合、图像映射或性能测试，也没有修改模型manifest或二进制。
