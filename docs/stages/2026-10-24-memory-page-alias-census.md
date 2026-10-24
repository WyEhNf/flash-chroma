# 16题内存独立分支：固定4KiB精确页别名唯一普查

Agent：`/root/memory`；Operator：当前16题用户；Status：Completed（仅普查与可行性门）。没有实际部署、MapViewOfFile3、native构建或计时；分支`codex/p16-memory-20261023`，Draft PR由root维护。

## 目的和固定边界

[只读loader](2026-10-24-memory-readonly-loader.md)保留了合格linear计算内核，却未减少ROM容量。新假设是把完全相同的输入ID页共享文件backing，通过虚拟页别名仍给原DLL连续16MiB table，避免软件dictionary的串行索引链。这只是机制假设，不是加速或物理RAM结论。

固定OS自然4KiB，不扫描尺寸或模型。只读取原M16D SHA`146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5`的16MiB ID载荷（原文件偏移1056），不读照片/gold。原ID流SHA`a020c67a…`，a399和230项合法palette不改；实际命中色数221的纠正也不改。

[设计与停止条件](../../experiments/page-alias-census-design-v1.md)在执行前保留；AST/源与ROM身份被冻结为计划 **`f98d7c098f5d84b181d53dffa63c83e869cd29475e1df7b878e2c50fc8863d84`**，只运行一次。Windows11 26200/AMD64、Ryzen9 8945HX、Python3.12.14，stdlib单线程，无NumPy/OMP；root授权非性能窗，可与其它质量并行，未将耗时当吞吐。

## 唯一普查与独立复核

4096个逻辑4KiB页按首次出现编号，用完整bytes比较相等才共享，不只比较hash。每页0/1/4094/4095四个预定偏移共16384有限公式检查，另2个越界code拒绝；原header/metadata/最大code边界均通过。完整源ROM SHA、全16MiB ID SHA、独立pool回放SHA相等；独立exact-byte Counter频数一致。

| 项目 | 实际普查/投影值 |
|---|---:|
| 逻辑页数 | 4096 |
| unique页数 | 3082 |
| 重复页引用数 | 1014 |
| unique pool投影 | 12623872B |
| 固定header页 | 4096B |
| 4096项LE32 pageID | 16384B |
| **backing文件投影** | **12644352B** |
| owner必要状态原型实际sizeof | 48B |
| 原model | 1056B |
| **backing+原型状态+model投影** | **12645456B** |
| 基线ROM+model | 16779328B |
| **净backing投影节省** | **4133872B** |
| 预设门槛 | ≥1048576B，通过 |

48B原型含file/section/base/span及mapped_pages/split_pages/state/reserved，偏移0/8/16/24/32/36/40/44；不是已经实装alias owner、Python包装或OS总成本。后续若增加必需常驻字段或索引，应重新扣账，不能隐去并继续沿用初筛节省。

离线复核只按封存pageID重放原字节、首次编号、频数与边界，不重新归类或调参，同样恢复全16MiB ID摘要。results原SHA **`0d78fbb7395be67c113903a5ddb741e92cf35e4453788eb3629cf870bc3d4677`**，support原SHA **`bfc96db68384a70c40c7df596b8d6a1fb1411a189d8059620b44e58b02dc3025`**。

普查进程峰WS44392448B、峰private29646848B，含Python/唯一页字节、Counter及JSON，不是将来部署RAM、PTE/VAD成本或核心scratch。

## 地址与成本边界

原payload从1056起，不能把原文件4KiB页边界直接当table页。未来布局须把原1056B header放独立4KiB页末尾，blob=虚拟base+3040、table=base+4096；元数据不出现在原逻辑blob内。虚拟映射跨度仍16781312B，原逻辑blob_bytes仍16778272B，未因去重缩短。

[MapViewOfFile3官方文档](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile3)为MEM_REPLACE_PLACEHOLDER的4KiB对齐提供API依据，实际支持、精确范围及回收尚未执行。[QueryWorkingSetEx字段文档](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-psapi_working_set_ex_block)中的ShareCount是进程数（上限7），Shared仅表示可共享，均不是同进程别名数；没有可见PFN，不据此精确计独立物理页。WS可能重复计虚拟页，PTE/VAD等OS成本尚未测，不能把unique backing称为实测物理RAM或虚拟capacity下降。

table/ROM palette的对齐位置也会变化。若后续部署，需同header页末/同table对齐但不去重的RO控制，以区分布局和别名效应；不能因机器码相同就把速度变化全归页复用。符号缺失fallback、零/部分映射失败清理、startup成本和实际owner等须另立单版协议。该方案需要Windows新API，不宣称portable C99本身增强。

## 原件、复现和未完成项

[发布manifest](../../report/data/p16-page-alias-census-v1/manifest.json)含raw、封存源/计划、完整pageID/频数/页面SHA/边界探针及独立复核。ZIP只是发布，不是容量。阶段字节/CRC和HEAD另核，默认、旧RO失效场及其它字典失败都保持。

```powershell
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/freeze_page_alias_census.py
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/profile_page_alias.py --output artifacts/p16-page-alias-census-v1
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/audit_page_alias_census.py --input artifacts/p16-page-alias-census-v1
```

以上是唯一已执行记录，不覆盖原计划或目录重跑。结果只允许进入后续部署可行性研究，没有新ROM/loader、运行时完整域、速度六档或物理RAM结论，不新增实际容量前沿点。后续先静态API/cleanup状态机，由root另授执行。
