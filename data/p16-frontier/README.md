# 连续目标与三维权衡目录

A为验证集平均RGB欧氏误差，B为绑定工作负载的批次总耗时，C为该处理方式的运行内存。每图全像素均值阈值先严格检查`<T`，时间与容量预算使用`<=`。`catalog.schema.json`规定结构，`scripts/p16_frontier.py validate`另检查引用、布尔验证标志、有限值、资源关系和部署限制；结构合法不代表引用证据已经重新执行。

已交付的[实际目录](../../report/data/p16-frontier-header-20261027/catalog.json)覆盖5套模型、20种执行配置的热批次/首批共40个指标点；两场次保留为四个独立比较上下文。模型包另保留max41/max48，共7套资产，它们没有本轮新库的性能资格。当前测量使用桌面宿主、整百图分离缓冲；移动/嵌入式有功能与裁剪合同，尚无实际设备性能目录。完整口径见[阶段报告](../../docs/stages/2026-10-27-p16-frontier-header.md)。

`seed-models.json`登记既有四套固定Cinema模型，未替新单头库填写测量结果。新增实测catalog必须绑定同一组原始四LUT、数据SHA、真实平台、构建、计时范围和图像存储方式；不同context不参与相互支配或速度排名。时间不稳定默认不能进入三维选择，必须显式传`--allow-unstable-time`才允许描述性选择，结果带`provisional: true`。

## 连续偏好与预算

```sh
python scripts/p16_frontier.py select --catalog path/to/catalog.json --context CONTEXT_ID --weights 0.85 0.60 0.25 --target desktop
python scripts/p16_frontier.py select --catalog path/to/catalog.json --context CONTEXT_ID --goal fastest --max-error 1.2 --max-runtime-bytes 536870912 --max-workspace-bytes 20971520
python scripts/p16_frontier.py frontier --catalog path/to/catalog.json --context CONTEXT_ID
```

三个权重均属于`[0,1]`且不能全为零，按和归一化；它们表示偏好，不表示精度百分比或速度保证。指标在本次请求的可行集合中按各轴min/max归一化，常量轴贡献0。单项目标只使用其对应权重。相同分数按平均误差、最差单图均值、时间、运行内存、工作区和id确定性排序。

先按上下文、目标、可用后端、线程上限及预算筛选，再计算三维非支配集合。完整catalog保留原记录；改变阈值后必须重算，不能只保存一次无约束前沿。前沿算法保留非凸点，epsilon预算可选中加权和难以选中的中间方案。返回的执行参数保持测量时原值，修改线程、分块或表示后须形成新的候选记录。

未知时间不能填零当作最快。仅在`--ignore-time --goal accurate`或`--ignore-time --goal compact`等不优化时间的请求中允许忽略时间；误差、正确性和资源仍必须已经验证。所有精度只属于绑定验证数据，不能保证未知图像、未知LUT或正式赛事分数。

## 生成候选与实际离线拟合

```sh
python scripts/p16_frontier.py plan --source-luts lut1.lut256 lut2.lut256 lut3.lut256 lut4.lut256 --m-values 17 25 33 --output artifacts/frontier-plan.json
python scripts/p16_frontier.py fit --source-luts lut1.lut256 lut2.lut256 lut3.lut256 lut4.lut256 --m 17 25 25 33 --method sample_interp --grid uniform --output artifacts/frontier-fit/mixed
```

计划枚举四级m的笛卡尔积，不要求各级相同；运行时domain组合目标、真实后端、表示、线程及块大小，嵌入式/可移植域固定单线程稀疏标量。`--max-models`限制模型搜索预算。计划只生成待办，不自动把未执行任务标为verified。

`fit`真正调用现有`lutlab.fit.fit_model`逐级独立拟合，产出四个SLUT、源SHA、各级m、参数、源码身份与可用于打包的`source-manifest.json`。`--grid curvature`时`--grid-alpha`和`--grid-exponent`连续参数会实际改变网格；量化后的节点和运行性能仍会分段变化。拟合成功状态明确为`fitted_pending_chain_accuracy_and_runtime_validation`，需要随后测最终四级输出、后端一致性和资源/时间。原始密集LUT格式为每张`256³×3`字节RGB8；新输出路径拒绝覆盖，失败记录保留。

部署端的`fc::Candidate`、`fc::Request`、`fc::select`及`fc::frontier`直接使用原始数组，无堆分配。请求中的context是调用方提供的完整证据上下文身份；C++接口不在像素热路径解析JSON或检查外部文件。`frontier`容量不足时报告所需容量并保持输出索引不变。

## 按保存的选择执行

```sh
python scripts/p16_frontier.py select --catalog path/to/catalog.json --context CONTEXT_ID --goal fastest --output artifacts/my-selection.json
python scripts/run_flash_chroma.py --catalog path/to/catalog.json --selection artifacts/my-selection.json --library build-single/libflash_chroma_bridge.so --images assets/photos/eval.txt --image-root . --output artifacts/my-selected-run --write-images
```

执行入口重新核对catalog摘要、所选候选整行与连续请求，执行原记录中的真实参数。模型记录必须含`manifest`、`manifest_sha256`、`profile`及`source_luts_sha256`，相对manifest和evidence路径以catalog目录为基准；原始证据格式为可读`results.json#记录id`。库SHA与百图解码像素SHA须精确匹配context，输出还须匹配原始证据。模型文件、模型内存、图片、清单及部署输入在运行后再次核验。

入口实际生成100张图像的像素，`--write-images`将其按批次索引写PNG。运行记录分列原生准备、整批apply、准备至首批和读图至输出的wall；当前进程平台指纹单独报告，指纹不同不继承同机速度最优结论。没有密集原表时仅明确继承已验同输入/同模型/同输出的误差；增加`--reference-luts`四路径和可选`--threshold`可在计时外重新执行独立四级参考与逐图严格门槛。输出路径必须不存在，失败过程保留诊断。
