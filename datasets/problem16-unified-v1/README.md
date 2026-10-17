# 第16题合并数据集 v1

这是原数据与两批 hack image/LUT 的统一入口。**274 个命名空间 case、273 条不同的有序源链、455 份不同图片 RGB 内容**已经合并登记。case ID、生成参数、原划分、文件/RGB 哈希及历史证据归属都保留，不把新样本的登记当成拟合通过。

[catalog.json](catalog.json) 是机器可读总索引；`python -m lutlab dataset` 提供读取、显式重建和核对入口。原目录继续保存冻结版本，合并不覆写旧 catalog、原账本观测、冠军或 7,917 项矩阵分母。

| 来源 | LUT case | 图片别名 | 定位 |
| --- | ---: | ---: | --- |
| corpus-v1 | 200 | 320 | 原分类、强度和 seed 划分 |
| axis-bins-v1 | 3 | 0 | 原分箱容量控制 |
| legacy | 9 | 0 | 已有账本中的历史源身份 |
| hack-v1 | 26 | 14 | 网格边界、内部窄峰和基本回放 |
| hack-v2 | 36 | 21 | 三维局部峰谷、斜薄带、周期耦合、舍入与串联 |
| natural100 | 0 | 100 | 已合入的日常照片及原来源/使用范围 |
| photos-v1 | 0 | 5 | 五张 Kodak 的历史别名，已包含在 natural100 中 |

总索引保留 460 个图片别名，按 RGB 字节归并为 455 份不同内容。两条恒等控制链使用相同源表，保留别名并只计作一条不同源链；原有两条轴置换链的最终变换也相同。重复组在索引中公开，不靠删除样本隐藏。

## 可直接使用的队列

下表清单均使用项目根目录相对路径。源 case 划分与图片划分是不同对象。

| 队列 | 图数 | 用途 |
| --- | ---: | --- |
| [corpus-v1](cohorts/corpus-v1.txt) | 320 | 原合成图全部成员 |
| [corpus-development](cohorts/corpus-development.txt) | 80 | 原开发图 |
| [corpus-calibration](cohorts/corpus-calibration.txt) | 80 | 原校准图 |
| [corpus-holdout](cohorts/corpus-holdout.txt) | 160 | 保留原标签，不能仅凭名称宣称从未用于其他研究 |
| [stress](cohorts/stress.txt) | 35 | 两批压力图，11 组原序/重排/聚集布局及两张诊断图 |
| [development](cohorts/development.txt) | 115 | 原开发图与压力图，排除已知留出冲突 |
| [natural100](cohorts/natural100.txt) | 100 | 固定自然照片对照，不宣称独立盲测 |
| [photos-v1](cohorts/photos-v1.txt) | 5 | 旧 Kodak 队列，便于对照历史范围 |
| [benchmark100-legacy](cohorts/benchmark100-legacy.txt) | 100 | 保留原吞吐队列成员与顺序，包含多个图片划分 |
| [all-inventory](cohorts/all-inventory.txt) | 455 | 去重后的全量资产盘点，**包含留出图，不作调参队列** |

合并清单规范化路径和换行，因此它们具有自己的列表哈希。即便成员相同，也不直接继承旧绝对路径列表的资格、速度或历史阈值结果。

## 身份、重复与留出边界

- 源 case 使用 `命名空间--原ID`，保留原 ID 与原定义引用；四张完整源表按顺序绑定 SHA-256。
- [legacy-identities.json](legacy-identities.json) 只冻结旧账本的源身份与元数据，不复制观测和冠军。原账本后续增加测量不使本数据定义失效。
- [composites.json](composites.json) 为两批共 62 个新增 case 保存完整逐级 RGB8 真值哈希，用于识别相同最终变换；没有执行稀疏模型评价。
- 目前可检查的源链、最终变换、图像哈希中，未发现训练/留出冲突。**12 个历史 case 缺少最终变换哈希**，不能据此宣称全部分布绝无重复或统计独立。
- 若后续版本发现完整源链、最终变换或图片跨训练/留出重合，总索引标记隔离，并从合并开发队列排除相关图片；不会自动重新分配原划分。
- 新增 62 个 case 的质量均为 `unmeasured`。有限探针的回放通过，不自动获得全色域、100图或官方验收资格。

运行时以同一量化模型相对独立整数 oracle 的 **0 字节差异**验收。拟合误差采用明确命名的 `rgb_l2_code_value`，不是 CIEDE2000；阈值暂为空。完整口径见 [acceptance.json](../problem16-hack-v1/acceptance.json)。

## 获取与复现

Git 保存总索引、来源元数据、生成器、35 张新增压力图片和三组小型回放。原 320 张合成图与完整大 LUT 继续按项目规则放在忽略的 `data/`，不会把数十 GB 数据加入 Git；本机已有的对象保持原位。

在已配置 `PYTHONPATH=python` 的项目环境中：

```bash
# 只核对元数据，无需生成大表或原合成图
python -m lutlab dataset inspect

# 读取一条完整原始配方及源身份
python -m lutlab dataset show --case hack-v2--box-peak-w1

# 从冻结配方显式恢复原320张合成图，约720 MiB；不构造完整 LUT 或拟合
python -m lutlab dataset restore --cohort corpus-v1
# 也可只恢复一张原图
python -m lutlab dataset restore --image corpus-v1--neutral_ramp-i0-s0

# 文件齐备后，一次核对全部455个实际图片文件及其RGB字节
python -m lutlab dataset inspect --verify-files

# 只导出一条新增压力链的四张完整源表，约192 MiB
python -m lutlab dataset export --case hack-v2--box-peak-w1 --output data/unified-v1
```

`restore` 不下载自然照片、不覆写不同字节，也不隐式生成模型。旧完整 LUT 仍使用原版本生成器/冻结源码和其环境恢复，本轮没有重建或重新审计数十 GB 的历史源对象。

已测数据构造环境是 Windows、Python 3.13.12，依赖见 [reproduce-requirements.txt](reproduce-requirements.txt)。可在独立环境安装该文件，不要替换默认 Linux/Pixi 锁文件。本轮没有认证 Linux/Pixi 重构的全部字节；版本差异导致哈希不同会直接报错，不更新历史哈希。

再次 `dataset build` 会使用已经冻结的复合真值哈希建立相同索引；依赖内容改变则应追加版本。常规 CI 不执行构造大表、全色域拟合或性能矩阵。

## 本轮核对范围

455 张实际图片的文件/RGB 哈希、35 张压力图的布局多重集与所有队列已集中核对。28 项 Python 回归通过，新增耦合回放在 7 个整数后端上与独立 oracle 一致；C99 与结构化调度的第二级正确使用通用 `tetra` 路径。原数值实现保持不变。

首次合并遇到旧 CSV 的 UTF-8 BOM，已修正读取适配并保留失败日志。[阶段记录](../../report/data/unified-v1/README.md)、[机器可读验证](validation.json)。未执行方法/容量矩阵、预留源拟合质量、全色域稀疏误差或性能扫描。
