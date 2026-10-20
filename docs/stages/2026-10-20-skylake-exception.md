# 精确例外池：相对修订22再提升超过50%吞吐

Agent：Codex；Operator：WyEhNf；Task：继续优化，直到相对刚完成的修订22再提高至少50%吞吐，精度及其余要求不变；Status：Completed（本机固定模型研究完成，Draft待审；Skylake实机性能与官方许可待验收）。

本轮修订23直接对修订22比较，唯一80轮中，1/4线程apply吞吐分别再提高 **70.91%/70.90%**，copy+apply提高 **62.40%/54.32%**，均超过50%。完整256³与100图逐字节相同，Linux也完成完整域验证。新例外池占1,078,832字节，加24字节元数据，四级句柄10,190,548→11,269,404字节。此结果属于本机固定模型，不是Skylake实测或正式比赛成绩。

工作从`b3d7f4c`开始，fetch后main仍为`b19c5a0`，已经包含；没有覆盖其他本地修改。分支为`codex/skylake-palette-exceptions-20261020`，依赖[PR #45](https://github.com/WyEhNf/flash-chroma/pull/45)，参考完全使用其已验22。新构建参考的运行时对象SHA `22e73fce9c12a2c69f73f26af45803d2d8e8d2ecc74f19693175fa84bf4a7748`、AVX2对象SHA `e161879acb6d82287a2bb8d89273b02ca11e27e5059806a8bf0a13e58b4c9882`均与前轮22候选逐字节相同，不能以旧16充当新基线。主要提交以本阶段PR实际头为准；计划、源、模型、构建、二进制和各回执均另绑SHA。

## 优化内容

修订22的2,097,152个主块中，1,962,299块可用3bit差值表示；其余134,853块的低8位为255。旧逻辑只要8个图像像素中的任意lane遇到此哨兵，整包就执行原16的首级插值与后缀缓存读取。已见100图中这种包约21.42%，是这次直接消除的计算成本。

修订23保持原3bit编码和230项精确调色板。对于不能编码的块，改用两个u32保存该8个输入各自的完整8bit调色板ID，主词高24位存例外池中的词索引，低8位仍为255。池前放两个零保护词：混合包中的非例外lane，地址被掩到0或1，绝不能拿主块中的3bit载荷当作例外地址。

AVX2仍每次8像素，先读主词并解码普通ID。如果任意lane是例外，额外gather一次例外词、按B低位提取字节ID，然后blend回普通ID；最后统一gather调色板并写回。所有输入都走精确查表，不再因例外块计算首级插值。普通包两次gather，混合/例外包三次。尾部和显式标量入口仍保留原四级Q16/逐级RGB8算法。

例外池只从构造阶段已生成的原稀疏链标签建立，按RGB次序顺序分配，不使用照片、完整源LUT或旧oracle生成。构造仍使用4线程，不能因为之后是1线程映射就隐藏准备并行成本。已启用表时pool索引上界由块数证明小于24bit；非四级、布局不符、未获证、调色板超过255项或分配失败保留原路径。候选23没有改模型、排序、8像素块宽或3bit参数，没有扫描其他压缩配置。

[Intel gather文档](https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/intrinsics-for-gather-operations.html)用于核对32bit元素和索引缩放边界；本实现使用AVX2全lane gather及有效零保护地址，不需要AVX512。新函数完整汇编95条指令、没有外部调用；旧22完整函数328条包含较重回退，不能把两者指令数之比当作加速比。本阶段没有以MCA模型代替真实缓存访问计时。

## 唯一同场性能比较

实际环境：Windows11 26200 x64 / Ryzen9 8945HX，16核32线程；MinGW GCC15.2，Python3.12.14、NumPy1.26.4、Pillow10.4、psutil5.9。Release为`-O3 -DNDEBUG`，独立AVX2 TU为`-mavx2 -mtune=skylake -ffp-contract=off`，没有全局march、AVX512、FMA或fast-math。原回退对象在新参考与候选之间也分别相同。

固定CPU0/2/4/6四个同L3物理核；没有锁频或控温。四串行新进程AB/BA/BA/AB，1/4线程顺序平衡，每配置5轮完整100张1024×768 RGB8图，总80轮。原生apply与copy+apply分列，235,929,600字节源预载，不含IO、解码、拟合、分配及SHA。逐次CABI repeats=1，计时外验证完整100图SHA；不删轮、不补测。每个计时候选句柄都核对真实启用例外池、269,708词及1,078,832字节。

每进程先取5轮中位，再计算候选/参考，最后取四个配对比的中位。绝对时间只作同轮说明，不能用两角色的绝对中位相除替代配对值。

| 请求线程 | apply毫秒/图，22→23 | 配对耗时比 | 耗时下降 | 吞吐提高 | copy+apply耗时比／吞吐提高 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 3.737775→2.123760 | 0.585101 | 41.49% | 70.91% | 0.615778／62.40% |
| 4 | 0.994270→0.560800 | 0.585134 | 41.49% | 70.90% | 0.647997／54.32% |

apply四进程比：1线程0.59557/0.59287/0.57733/0.53515；4线程0.54981/0.57839/0.59188/0.61254。copy+apply四线程进程2/3分别为0.69803/0.70835，这两个进程自身没有达到50%吞吐提升；预先规定的四配对中位满足目标，没有把“中位达标”写成每轮达标。

门槛固定为两线程档apply和copy+apply中位比均≤2/3，任一apply进程比≤0.9，准备＋已预热首100图copy+apply中位比≤1，全部通过。[独立标准库复算](../../report/data/skylake-exception-v1/audit/results.json)核对实际22/23修订、库与输入SHA、CPU集合、80轮输出及全部配对公式，没有新计时。

本轮22的绝对时间与前轮22不同，虽然对象字节相同，也不能跨次混用。这里所有百分比只来自本轮直接配对，不与上一阶段85%/91%相乘推导新成绩，也不把温度/频率未控制的本机结果升级为Skylake保证。

## 准备成本与容量

| 容量核算 | 修订22 | 修订23 |
| --- | ---: | ---: |
| 单级句柄 | 272,811 | 272,835 |
| 四级句柄 | 10,190,548 | 11,269,404 |
| 主块表 | 8,388,608 | 8,388,608 |
| 新例外池，含2保护词 | 0 | 1,078,832 |
| 新vector元数据 | 0 | 24 |

这是真实句柄及vector capacity核算，不是RSS。构造期间临时RGB流、反查表、去重工作向量与新表容量合计77,318,704字节，含最终主表/例外池；不含调用者图片、原句柄和解释器，不能称进程峰值RSS。临时流创建后释放。

准备墙钟：本轮22约80.63–98.51ms，23约79.27–98.59ms；这些样本不证明新建表算法没有额外成本。**准备＋首个已预热100图copy+apply**的配对中位比为1线程0.676647、4线程0.841013，八个进程配对均未退化。这项指标排除中间预热成本，不是冷启动端到端或单图延迟。

其他模型可能有更多例外：正负斜率m33补验的例外池约16.09MB、句柄25.18MB。理论池上限为16,777,224字节（两个保护词加所有块的八个ID），不能把实际1.08MB宣传成通用固定上限。官方内存预算与派生表许可仍需确认。

## 正确性与移植验证

| 验证目的 | 覆盖及结果 |
| --- | --- |
| 原基础/缓存合同 | 55组/6非法侧表；另55组与24,000合成槽，全部通过 |
| 原域证书诊断 | 8状态、24条失败不写；当前32³单元获证，零差 |
| 新编码独立全表重建 | 从旧独立oracle重建全部16,777,216颜色；2,097,152主词、134,853例外地址及269,708池词逐项核验，零差 |
| 快/例外/混合/边界 | 55组，含“7普通＋1例外”、交替、端点、0/7/8/9/4095/4096/4097等长度、四种偏移、两库标量及AVX2请求1/4，共1,320比较；14条只读诊断/复制拒绝，零差 |
| 其他网格及斜率 | m17/18/25/33、48组×8,203像素；不同例外密度，独立整数比较及哨兵零差 |
| 大调色板拒绝 | 6249色、证书成立，23不建池，18组×4,105像素零差，空池只读复制通过 |
| Windows实际输出 | 两库单级/四级×标量1/AVX2请求4，共8组完整256³与100图逐图/合并SHA全部相同 |
| Linux实际输出 | 同AMD的WSL2 Ubuntu / Linux6.18.33.2 / GCC15.2 / Python3.14.4标准库，528次有限比较及12组完整256³零差；新池实际启用，未测Linux性能 |
| 证据完整性 | 100份原始文件、12份源快照、714项源成员SHA独立核验通过；没有新增原生或性能调用 |

全部色域等价使原模型精度不下降。单级输出SHA `7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146`，四级 `3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，100图合并 `f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`。没有重新拟合或再作精度选型；既有RGB欧氏误差结果继续适用，不是CIEDE2000或官方Threshold验收，百图为已见数据。

初次packed验证器因局部哨兵数组`storage`遮蔽导入容量函数，在独立解码前失败；只改函数别名`compiled_storage`，原生源码/构建/模型不变。validation-v1和失败源ZIP保留，v2固定修改后的验证器，再通过全部重建及完整输出后才执行唯一性能比较。另一次生成补验脚本的PowerShell命令因引号语法失败，未生成脚本或运行数值；改为生成器文件后成功。没有以脚本修复为由重跑性能。分配失败未注入，真实Skylake与其他CPU尚未执行。

## 文件、复现与协作

主实现为`experiments/skylake-exception-runtime`，计划为`experiments/skylake-exception-v1.json`，验证/性能策略分别为`skylake-exception-validation-v1/v2.json`和`skylake-exception-perf-v1.json`；`scripts/*skylake_exception*.py`与`exception_support.py`是独立入口。原22代码、计划和既有数据不变。

[原始档案](../../report/data/skylake-exception-v1/README.md)约5.2MB，保存源、二进制/对象、全部轮次、完整回执、失败和协作快照。小模型复用[22档案](../../report/data/skylake-palette-v1/README.md)中的`fixed-models.zip`；三个大流按同一SHA从原[服务器包](../../report/data/skylake-domain-server-v2/README.md)恢复。此证据目录不含235MB照片流或两个50MB完整域流，不是独立无数据运行包。

源码须从`windows-build/measured-source.zip`按原字节恢复后构建，旧依赖存在Git换行归一化；不得修改旧计划SHA绕过校验。Windows实际入口：

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/build_skylake_runtime.py --plan experiments/skylake-exception-v1.json --output artifacts/skylake-exception-build-v1 --compiler E:/mingw64/bin/g++.exe --c-compiler E:/mingw64/bin/gcc.exe --generator 'MinGW Makefiles'
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/bench_skylake_exception.py --policy experiments/skylake-exception-perf-v1.json --output artifacts/skylake-exception-perf-v1
```

完整验证命令及已验输入身份见各run.json；性能只允许在同构建完整验收后执行。复现要使用新输出目录。Linux标准库完整入口：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-exception-v1.json --output artifacts/skylake-exception-linux-build-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
python3 scripts/verify_skylake_exception_linux.py --plan experiments/skylake-exception-v1.json --build artifacts/skylake-exception-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-exception-linux-full-v1 --affinity-cpus 0,2,4,6
```

服务器CPU集合不能照抄本机；先核对实际SKU、OS、编译器、NUMA/缓存、微码与GDS状态，完成同一模型完整正确性，再冻结目标构建和新的性能策略。旧Windows策略绑定本轮DLL与验收，不应篡改旧回执跨机使用。采用AVX2且Linux输出已验，只证明相应兼容性，不承诺Skylake缓存收益，不关闭安全缓解。

创建Draft前全量获取39个PR、2个独立issue、2个Discussion及119组REST评论/review/行内记录，GraphQL线程0，分页完整。已有意见/Discussion与前轮一致，新增PR #45没有评论/review/线程，头仍b3d7f4c。[协作核对](../../report/data/skylake-exception-v1/remote-check.json)保留来源与修复祖先；337a3dd（[#9基线/环境](https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540)、[#7内核绑定](https://github.com/WyEhNf/flash-chroma/issues/7)）、876e15b8（[#27保护](https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096)）、397cc367（[#29相等mean](https://github.com/WyEhNf/flash-chroma/pull/29)）实际包含，相关公共代码未改，历史集成证据见[#37](https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676)。

[#42](https://github.com/WyEhNf/flash-chroma/pull/42)/[#43](https://github.com/WyEhNf/flash-chroma/pull/43)/[#44](https://github.com/WyEhNf/flash-chroma/pull/44)/[#45](https://github.com/WyEhNf/flash-chroma/pull/45)的精度、不同运行时及失败分别保留，不跨阶段拼接。[Discussion #4](https://github.com/WyEhNf/flash-chroma/discussions/4)的实现/模型误差区分落实；[#8](https://github.com/WyEhNf/flash-chroma/issues/8)接口/实板和GUI #40仍独立待办。保持Draft，不合并或关闭issue；官方派生缓存/侧表许可、预算、Threshold与Skylake实机结果仍待验收。普通全仓CI另看本PR实际头，不替代本阶段的实验库验证。
