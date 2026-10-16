# 现成LUT素材库：68个

收集五个上游仓库公开发布的LUT，供不同稀疏化与插值恢复方案比较。文件按来源放在 `sources/`，保留原始字节、目录层次、内嵌版权声明和许可证；未重新拟合、裁剪或展开成256³整数表。

## 来源与内容

| 来源 | 数量 | 格式 | 场景 | 上游声明的许可证 |
|---|---:|---|---|---|
| [Striped Purple](https://github.com/stripedpurple/color-grading-luts) | 49 | `.cube` | 创意调色、年代风格、景色、胶片模拟；包含少量红外等特殊风格 | [MIT](sources/stripedpurple/LICENSE) |
| [HDR2SDR-LUTs](https://github.com/sverit/HDR2SDR-LUTs) | 5 | `.cube` | 色调压缩与饱和度调整 | [GPL-3.0](sources/hdr2sdr/LICENSE) |
| [FilmSim](https://github.com/sguyader/FilmSim) | 4 | HaldCLUT `.tif` | Acros、Classic Chrome、Provia、Velvia | [CC0-1.0](sources/filmsim/LICENSE) |
| [ChristophWurst](https://github.com/ChristophWurst/haldclut) | 3 | HaldCLUT `.tif` | Tension warm/cold、Krakow | [CC BY-SA 4.0](sources/christophwurst/LICENSE) |
| [Blender Filmic sRGB](https://github.com/Lauloque/LUTs-Linear-to-Blender-s-Filmic-sRGB) | 7 | `.3dl` | 线性输入→Filmic sRGB，七档对比度 | [GPL-3.0](sources/blender-filmic/LICENSE) |
| **合计** | **68** | **54 CUBE＋7 Hald TIFF＋7 3DL** | | |

这些是第三方数据资产，不统一改授本仓库代码许可证。各源的许可证原文、原有版权注释和可用的上游README均已保留。上游README属于第三方原文，未翻译或改写其声明。逐文件来源链接固定到具体提交，见[manifest.json](manifest.json)。

## 文件与清单

- [luts.txt](luts.txt)：68个LUT文件路径，相对于仓库根目录。
- [manifest.json](manifest.json)：来源提交、许可证位置、源文件URL、文件SHA-256、格式、网格、数值范围、结构检查和数值去重结果。
- [source-lock.json](source-lock.json)：五个上游仓库的固定提交、下载包URL、SHA-256及所选文件，用于重建。
- `sources/<来源>/`：上游LUT、许可证和可用的 `UPSTREAM_README.md`。

## 结构检查结果

| 表示 | 网格边长 | 数量 | 检查 |
|---|---:|---:|---|
| CUBE | 16 | 4 | 节点行数=m³、三通道、有限值、有效输入域 |
| CUBE | 32 | 21 | 同上 |
| CUBE | 33 | 3 | 同上 |
| CUBE | 64 | 26 | 同上 |
| HaldCLUT TIFF | 144 | 7 | 单页RGB8、1728×1728，Hald level=12，节点数=144³ |
| 3DL | 17 | 7 | 输入轴严格递增、4913个RGB整数节点、非负有限输出 |

68个文件全部通过表示结构检查；原始文件哈希与下载包内成员一致。按格式、网格、输入域与节点数值计算的68个数值哈希互不相同。这仅排除该定义下的完全重复，不保证视觉风格独立，也不证明不同表示、不同插值方式之间不存在函数等价。

这批LUT素材约257MiB，未把下载包、示例照片、第三方程序或巨大256³展开表一起纳入Git。最大单个素材文件约8.6MiB。

## 用于本题前的约定

1. 当前 `lutlab fit --inputs` 接收的是四张完整 `256³×RGB8` 表，不能直接把这里的 `.cube/.3dl/.tif` 当作该二进制输入。后续需要独立转换步骤，明确轴序、输入域、恢复插值、输出裁剪和取整。
2. 外部素材的原网格边长不受赛题17–33约束；赛题约束适用于待评测算法的输出稀疏表示。由稀疏源展开出的256³真值须注明来源插值结构，避免将天然匹配误判为算法优势。
3. Hald TIFF是LUT编码图，不是自然测试照片。这里7张均为144³ RGB8节点；不能按普通图片缩放、旋转或调整色彩。
4. 3DL源文件输入轴为0–1023，节点输出为另一整数码值尺度；不因输入轴最大值1023就把输出也除以1023。需按上游格式/烘焙约定确认归一化，不根据观察到的输出最大值自行拉伸。
5. Blender Filmic组明确以Linear为输入、Filmic sRGB为输出；其他创意LUT若没有声明色彩空间，就保持未知，不能默认所有素材均为sRGB或能任意四级串接。HDR2SDR作者仅描述levels压缩及饱和度调整，不能据文件名将其当成标准PQ/HLG变换。
6. `Striped Purple - Lobster.cube`包含负输出与大于1的输出，已保留并在manifest记录范围；本轮未裁剪。测试转换时应显式固定该政策。

本次只完成素材采集和格式核验，未运行图像映射、精度门槛、拟合或性能测试，不宣称任何LUT组合已通过赛题要求。

## 复现

在已安装NumPy和tifffile的Python环境中，从仓库根目录运行：

```powershell
python scripts/collect_existing_luts.py --sources assets/LUT/source-lock.json --download
```

命令按锁定提交下载缺失源包到被忽略的 `tmp/lut-sources/`，验证源包哈希，只读取清单中指定成员，再原样写入 `assets/LUT/sources/` 并重建清单。不会执行第三方程序。已有源包时可省略 `--download`。不同环境重建时生成时间与工具版本字段会变化，LUT原始字节应保持相同。
