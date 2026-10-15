# 日常摄影样本（Kodak）

五张普通曝光的自然照片，用于 LUT 色彩映射的可视化和小规模精度检查。原始图片来自 [Kodak Lossless True Color Image Suite](https://r0k.us/graphics/kodak/)，不是合成色条、随机噪声或极端曝光压力图。

| 图片 | 场景 | 摄影者 | 来源与预览 |
|---|---|---|---|
| kodim03 | 彩色帽子、日常商品 | Don Cochran | [来源](https://r0k.us/graphics/kodak/kodim03.html) · [原图](original/kodim03.png) |
| kodim06 | 海边帆船、旅行风景 | Don Cochran | [来源](https://r0k.us/graphics/kodak/kodim06.html) · [原图](original/kodim06.png) |
| kodim07 | 窗户、墙面与花草 | Don Cochran | [来源](https://r0k.us/graphics/kodak/kodim07.html) · [原图](original/kodim07.png) |
| kodim08 | 城镇建筑、街景 | Alfons Rudolph | [来源](https://r0k.us/graphics/kodak/kodim08.html) · [原图](original/kodim08.png) |
| kodim12 | 沙滩游客、自然光下的人物 | Don Cochran | [来源](https://r0k.us/graphics/kodak/kodim12.html) · [原图](original/kodim12.png) |

## 文件与转换

- `original/`：下载的 PNG 原始字节，RGB8，768×512。
- `rgb8-1024x768/`：符合赛题尺寸的 RGB8 PNG 副本。
- `manifest.json`：下载时间、来源、摄影者、尺寸、文件大小与 SHA-256。
- `eval.txt`：五张评测副本的路径，均相对于仓库根目录，可供已有接收图片列表的评测命令显式使用。

副本遵循当前 `python/lutlab/data.py::_to_frame` 的处理约定：EXIF方向处理、必要时旋转为横向，再以 Lanczos 缩放到1024×768。这里768×512原图从3:2拉伸为4:3；不裁剪，也不调整色彩、曝光或饱和度。原图单独保留，方便后续改用其他统一尺寸政策。

运行时图片仍位于被Git忽略的 `data/`。这组小样本放在已有版本化图片目录 `assets/` 下，不改变数据生成器、原有29图/100图清单或既有验收记录。它是已有Kodak家族的显式子集，不能称为新的独立数据家族，也不能代替100图测速集。

## 来源声明

托管页写明其理解是 Kodak 已将图片发布供不受限制的使用。这里保留该来源声明及摄影者署名，不将其改写为本仓库的MIT/CC0授权。逐张来源和原始文件哈希见manifest。
