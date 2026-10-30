# 赛前快速调试：四张新LUT到逐图验收

本入口把比赛输入、拟合、运行参数和阈值集中到一份JSON，便于换数据、换机器和定位失败。照片工作台用于看图、调组合和解释当前图像结果；正式四LUT与百图验收使用命令行，避免把展示用预设或Cinema历史成绩当成新比赛数据的结果。

规则依据是仓库的[原题快照及用户补充](../PROBLEM.md)。官方测试集、Threshold数值、最终文件协议和精确计时起止尚未提供，本文不推算正式得分。

## 1. 已确认的边界

| 项目 | 当前实施口径 |
| --- | --- |
| 原始LUT | 四个256³整型三维映射，按给定顺序串联；比赛原文要求四次独立且不同的颜色调整 |
| 稀疏表示 | 每级m独立位于17..33；选定参数后全批固定，不按单图重新拟合或更换模型 |
| 输入图像 | 正式批次100张1024×768、3通道RGB8；入口不静默缩放、转BGR或降低位深 |
| 数值执行 | 当前交付为四级Q16四面体，每级half-up生成RGB8整数，再送入下一级；派生direct保持同一结果 |
| 精度门槛 | 每图所有像素的RGB欧氏距离取平均，使用未舍入mean严格 `< Threshold`；p99/max和全批平均另报 |
| 运行平台 | 用户指定CPU-only，不用GPU/NPU；初步目标Xeon Gold6140；记录实际机器，不从本机成绩外推 |
| 内存 | 分别记录模型、准备arena、图像缓冲及进程观测；模型包磁盘压缩不等于运行RAM下降 |

原题参考的1.5s/张不是固定满分线；精度40、速度40、架构创新20的具体换分、Threshold和最终计时范围仍待比赛方确认。[EVALUATION.md](../EVALUATION.md)顶部已经明确其中表格属于历史实验，不能作为当前版本或新LUT的性能承诺。

## 2. 先把环境跑通

Linux/Pixi使用已有锁定环境构建当前单头库：

```bash
pixi run --locked build-header
pixi run --locked test-header
```

默认库为`build-single-header/libflash_chroma_bridge.so`。Windows使用MinGW，配置时显式指定本机的GCC、G++和make；本机已经验证的修复库是`artifacts/single-header-perf-build/libflash_chroma_bridge.dll`。DLL的依赖目录需要在当前Python进程可见；另一台Linux机器应重新构建`.so`，不能直接复制Windows DLL。

以下命令中的`python`指含NumPy、SciPy和Pillow的同一个环境；Linux可统一写作`pixi run --locked python`。不要在拟合、doctor和run之间随意更换解释器或库路径。

## 3. 三分钟检查：先用现成样例

```bash
python scripts/p16_event.py init --output artifacts/event/session.json
python scripts/p16_event.py doctor --config artifacts/event/session.json --output artifacts/event/doctor.json
python scripts/p16_event.py run --config artifacts/event/session.json --limit 1 --output artifacts/event/probe-01
```

`init`默认使用现有Cinema `max_first`模型和`assets/photos/eval.txt`。它用于确认路径、依赖和运行库能加载，不代表已经接入正式新LUT。需要指定库时，在init后追加`--library`及实际路径。

`doctor`读取实际配置，检查依赖、模型/库身份、工作区配置和输入。无OpenMP构建请求4线程时应调整为1线程，不能把不支持的请求静默当成功。`--limit 1`明确属于调试子集；它能快速发现格式、链接和执行问题，不能代表100图精度或吞吐验收。

`expected_images`默认100。无`--limit`时，清单数量必须与它相等，否则完整执行拒绝，并保留失败记录；doctor遇到数量不符也不会报告就绪。任何显式`--limit`都标为`debug_subset:true`，即使写`--limit 100`且实际处理完整百图，也不授正式批次数量资格。若把`expected_images`显式改成非100做小样检查，结果同样标为调试。

Cinema样例的四张密集原表位于既有研究缓存，可能没有随源码复制到新机器。仅检查运行库时，可以在**样例配置**中将`source_luts`设为`[]`、`threshold`保持`null`，此时只做模型执行/C99核对，不产生拟合精度结果。正式接入则必须换入真实四表并重新fit，不能把缺失参考当成精度通过。

所有输出默认拒绝覆盖。重复调试时使用`probe-02`、`probe-03`等新目录，保留失败回执，便于比较。

## 4. 收到四张正式LUT后

先复制一份会话配置，修改这些字段：

- `source_luts`：四张**新的**原始密集LUT路径，按正式给定顺序排列；不能只换图片而继续用旧Cinema模型。
- `dense_format`：当前仅接收`rgb8-r-g-b-c-bfast`。每个文件恰为50331648B，无文件头，节点为uint8 RGB；索引是`table[R,G,B,C]`，B轴最快，节点内通道RGB。若正式文件是带头、int32、BGR或R轴最快，先按实际协议适配，不能靠改后缀解决。
- `image_list`、`image_root`：正式图片列表与根目录；列表每行一张图。配置中的相对路径按**配置所在目录**解析，列表里的相对图片路径按`image_root`解析。
- `fit.m`、`fit.method`、`fit.grid`：先用四级`[33,33,33,33]`、`sample_interp`、`uniform`确认链路；这只是可运行起点，不保证任意LUT满足精度门槛。
- `threshold`：未知时保留`null`；收到真实数值后填写。没有阈值时不会声明逐图过线。
- `runtime`：先保持`representation:"sparse"`，明确线程、块大小及arena预算；新LUT不保证具有U8/U16 direct所需的调色板容量。

```bash
python scripts/p16_event.py fit --config artifacts/event/session.json --output artifacts/event/fit-01
python scripts/p16_event.py doctor --config artifacts/event/fit-01/run-config.json --output artifacts/event/fit-01-doctor.json
python scripts/p16_event.py run --config artifacts/event/fit-01/run-config.json --limit 1 --output artifacts/event/new-lut-probe-01
python scripts/p16_event.py run --config artifacts/event/fit-01/run-config.json --output artifacts/event/full-01
```

fit生成四个真实SLUT、来源SHA和`source-manifest.json`，并另写`run-config.json`指向新模型、`profile:"fitted"`；不会覆盖原会话配置。新配置会重新定位相对路径。运行核对源LUT与模型来源；不匹配时应重新拟合或改正配置，不能绕过校验继续使用旧模型。

需要继续降低误差时，现有`fit.method`还支持`sample`、`ls_tetra_int`、`ls_tetra_jitter`，`fit.grid`支持`uniform`、`curvature`、`dp`。只在离线阶段比较，且每个候选另建输出目录；哪一项更好必须以新四LUT的最终逐图结果判断，不根据方法名预判过线。

正式执行移除`--limit`，使用完整100图和同一组冻结参数。新入口按图流式处理，避免为了调试固定分配两份整百图像素数组；它的计时模式与旧的整百图预载基准不同，不能直接沿用旧目录的绝对时间或排名。

## 5. 先看什么结果

1. **输入和执行身份**：确认四张源LUT、四级模型、实际库、图片顺序和配置的SHA一致，且实际后端/线程符合当前机器能力。
2. **执行正确性**：`validate_c99:true`时核对当前模型C++与独立C99的实际输出。相同只说明模型执行一致，不代表该稀疏模型逼近原始LUT的误差合格。
3. **逐图精度**：提供源LUT后，以独立的四张密集表逐级查找为参考；看每图mean及最差单图mean，不能只看整批均值。任一图未严格过线就不能将全批写成通过。
4. **时间口径**：把离线稀疏拟合、模型准备、纯映射调用及含解码/校验/写盘的应用wall分开；首次准备和热映射也分别记录。
5. **资源**：看实际模型与arena，加图像/验证暂态及进程RSS。Sparse先确认可靠，再为同模型测试direct资格及本机速度；不要拿更小包体替代RAM账本。

`results.json`重点字段为`images_completed`、`competition_size_batch`、`quality.all_image_mean_pass`、`actual_runtime`、`mapping_total_ms`、`native_prepare_ms`和`application_wall_ms`。run的逐图门禁失败返回退出码2，运行错误返回1；doctor未就绪也返回2，须结合命令与错误信息判断。`completed:true`只说明所请求工作完成；子集、缺少T、缺参考和不稳定时间都不会因此变成官方验收。

同一新LUT比较多个参数时，各次都使用同一批图片、源LUT和计时设置，输出到独立目录。拟合完成后再以**最终四级输出**检查每张图，不能只凭单级误差选定整条链。

## 6. 最容易踩的五个坑

| 现象 | 优先检查与处理 |
| --- | --- |
| 新图集运行被旧目录拒绝 | `run_flash_chroma.py`本来就绑定已测catalog的库及图片像素SHA；新比赛输入用本页的配置入口，不修改旧证据冒充新场次 |
| 换了正式四LUT，画面仍像Cinema | 核对`source_luts`及新fit产物；用`fit-01/run-config.json`，不继续用init带入的样例manifest |
| 机器上DLL/.so加载失败或4线程Unsupported | 用doctor确认实际解释器、平台库和依赖；目标机重新构建；无OpenMP用1线程，不预设任何机器都能绑定CPU0/2/4/6 |
| DirectU8/U16 Capacity或Budget | 新LUT不保证224/336色，先回Sparse确认精度；显式direct和预算失败不是数据损坏，也不能通过暗换模型掩盖 |
| 图像“很好看”但正式验收失败 | 工作台是可视化，展示用identity、禁用级和创意CUBE并不自动满足正式四张不同映射；用密集原表参考和真实逐图Threshold验收 |

原生接口、部署宏和资源定义见[单头接入说明](single-header-runtime.md)；已有数据与权利范围见[DATA.md](../DATA.md)和[照片说明](../assets/photos/README.md)。本页不把任何未执行的正式数据、目标机速度或官方分数标作已验证。

### 旧验证/目录入口的已知边界

[PR #96](https://github.com/WyEhNf/flash-chroma/pull/96)记录的两项P2在旧入口中仍待修复：`verify_flash_chroma.py`会按profile强制准备U8/U16 direct，对超出对应调色板容量的有效模型可能中断，不能把这种表示资格失败当作Sparse输出错误；`run_flash_chroma.py`的`bind_evidence`尚未逐项将目录指标绑定回原始测量值，不能仅靠目录文件自洽就继承精度、时间和资源资格。

本页的`p16_event.py`默认Sparse，不调用该全域验证器，也不读取旧目录或调用`bind_evidence`；它按配置加载当前四级模型，在请求图集上重新计算实际输出、资源、时间及可选密集参考误差。显式请求不适用的direct仍会如实失败。此整合避开了上述路径，不表示旧P2已修复，也不把当前图集的C99一致性升级为完整RGB8域验证。

## 7. 评测接口变化时：直接使用C++接入层

[`single_header/event_run.cpp`](../single_header/event_run.cpp)只依赖交付的`flash_chroma.hpp`和C++17标准库。它读取四份SLUT和可选四份sidecar，以固定配置逐帧映射连续RGB8；没有Python、图片解码或JSON依赖库。若评测系统直接给像素缓冲，可替换该文件的读写层，保留`Runtime::requirements → prepare → apply`调用。

```bash
cmake --build build-single-header --target flash_chroma_run --parallel 2
build-single-header/flash_chroma_run --models artifacts/event/fit-01/stage1.slut artifacts/event/fit-01/stage2.slut artifacts/event/fit-01/stage3.slut artifacts/event/fit-01/stage4.slut --input input.rgb --output artifacts/event/cpp-output.rgb --report artifacts/event/cpp-run.json --width 1024 --height 768 --count 100 --backend auto --representation sparse --threads 4 --block-pixels 65536 --workspace-bytes 50331648
```

Windows执行相应构建目录中的`flash_chroma_run.exe`。`input.rgb`必须是已解码的逐帧、逐行、RGB通道连续字节，没有文件头或行padding；长度须恰为`width*height*3*count`。不能把PNG/JPEG直接改名传入；现阶段收到图片文件时使用前面的Python入口即可。

需要sidecar时追加`--sidecars stage1.sidecar - - -`，四槽必须齐全，`-`为空槽。`--help`列出后端、表示、线程、块大小、workspace预算及部署目标参数。width/height/count可为小尺寸探针，不能把非正式尺寸/数量写成比赛验收。

raw输出和可选JSON报告均排他创建；拒绝覆盖已有文件，处理中失败保留已经写出的片段。JSON分别记录`prepare`、`apply_only_sum`、`raw_io_sum`和`whole_wall`，前者仅包围`Runtime::prepare`，整体wall另含模型读取、检查、分配及raw读写；不含离线拟合或本JSON输出。它不计算色差或内置文件SHA，始终将`quality_verified`与`official_score_available`记为false，内容身份和精度仍由外部清单及参考验证负责。

本机验证为Windows AMD64 / MinGW G++15.2 Release：两帧19×11 RGB8、非整8宽度和13像素块，独立C++示例输出与Python FFI及独立C99逐字节相同；另检查既有输出/报告、零线程、尺寸溢出、长度不符、AVX-512及预算拒绝，共8项。该小型接入验证不是新的完整色域、100图性能、Clang或正式目标机结论。
