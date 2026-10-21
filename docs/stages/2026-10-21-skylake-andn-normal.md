# 有效多线程原地普通写

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23至少三倍吞吐；Status：Failed（80四线程纯apply）/ Draft，整体In Progress。基于Draft [PR74](https://github.com/WyEhNf/flash-chroma/pull/74)头`f82fb2d93edfdbc09b4997eb60a2b52befe5980e`研究新修订80，不重测79或拼接历史结果。

本阶段只在同一新构建中改变有效多线程原地路径：[normal TU](../../experiments/skylake-andn-normal-runtime/normal_inplace/channel_avx2.cpp)从78无栈原地ANDN32复制，保留四ID先行、64像素全部读完再写、当前pack_stream预排/合并、64B对齐和连续static分块，仅NTA改T0、三个存储原语展开的六次NT写改普通对齐32B写，并删除该TU已无用途的streamed/SFENCE。精确24B尾、72/40及406边界不改。不能把预排值交给旧68的普通output_four，字节格式不同。

79两个pair48 TU含原导出名逐字节保留；有效workers=1的原地及全部真正分离输出仍走原pair48 NTA/NT/SFENCE。分派依据`omp_in_parallel()?1:min(blocks,threads)`，不是裸请求线程；非OpenMP固定1，嵌套不额外并行。构造一次BMI检测，无BMI保留原线性，分配失败仍精确回退；无新增表或句柄字段。readonly `andn_normal_enabled`只报告句柄ANDN资格，不能当成普通写实际执行证明。

未发现直接重复：68是MOV+AND输入/旧输出且所有原地线程T0普通写；71另加入static,1交错；74本机实际PREFETCHW普通写、T0仅不支持时回退，仍无ANDN；75—79专用ANDN均NTA/NT。68旧单次四线程PMU方向信号不足以证明三倍可达，也不把历史收益相乘。相对79，新多线程路径减少拆位指令但输入load由每8像素4次恢复8次，T0/普通写可能加剧源和16MiB表竞争；78低SQ停顿不能证明store无影响或已确定根因。

[计划](../../experiments/skylake-andn-normal-v1.json)SHA`29c15d22fcf1ad4c90f7dae0dc1bdd613021eede441f0d0d6c4e57079c2bf0ff`，72项冻结源。实际环境Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu Linux6.18.33.2 / GCC15.2 / Python3.14.4标准库，GNU Release、通用AVX2与Skylake调优，仅三个专用TU加BMI1；不是真实Skylake。build SHA`ad44e981abb7271889d4556f9718078b65aee14bec8aedede67e1d9339de6b2a`，候选库SHA`a5723ba0cd328d80921f25aa7fe459808eb5ab309b131ce349958811d3ed1b3a`；参考仍23的`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。

静态正式结果SHA`24ff9a6779c94aa61997c790ea0cd9e6fa2a1019945dbf4cd8ec72f1b8ab4e01`通过六宽区段：pair原地321/170、分离319/168，两个pair对象及主线性`.text`与79相同；新normal257/138，64/32次mem32 ANDN、输入范围193/97B、四ID与先读后写、无热区栈、只有T0/普通store且无NT/SFENCE。normal64六条vmovdqa覆盖192B，32尾三条vmovdqu覆盖96B。分派器与三个BMI TU隔离通过。

首次执行前发现初版checker将dispatcher多个ELF节偏移套入主.text的问题，初件未执行且保留，正式v2按各可执行节核对字节，源/对象/门槛不改。独立回执v2 SHA`18bed41e82039fc0ef69ad1cc616f3dcdb64de3f8f08677f707d6d455a441635`完整覆盖五对象各可执行节与输入/写入/分派；其初版误把runtime既存构造循环的static总数当成apply/apply_to数量而false，旧源/回执保留，v2只限定审计范围，没有改候选。

完整精度结果SHA`2e858c5f36d7b9ace81e0d514d2c149fb949fbf2acffb7698819c88d915213fc`通过独立16,777,216色物理表、24组完整RGB8原地/分离、2208有限后端/偏移、4416分离/同缓冲、736保护页、原1280对齐、44分离/9直表拒绝与null资格检查；byte/sentinel零差。完整域每批262144像素覆盖4块，4线程请求走新normal；旧257像素对齐夹具只有1块，不能说它覆盖normal。因此额外65793像素跨两块，以显式64B对齐基址加offset严格覆盖实际0..63，64次全部输出和两侧全哨兵通过。资格API结合冻结分派/输入块数说明路径覆盖，不冒称内核内计数。

模型记账reference single272835/chain11269404，candidate single272859/chain28046644，仍+24/+24+16MiB，不是RSS或官方预算。直表SHA不变，实际资格single0/chain1；全域只是冻结模型运行时精度不变，不是重新拟合。

完整域后冻结[验证身份](../../experiments/skylake-andn-normal-validation-v1.json)SHA`bf5a8580a708bb7e1f7d516f5abf3fb417ac307a09091aaae72085bcc2d73016`和[性能策略](../../experiments/skylake-andn-normal-long-perf-v1.json)SHA`1118b57055c89c94cd27845c171e8c1fd3cd7f1e14fb6e92232dd627fb91a642`。与79归一比较，bench只有身份变化，正确性旧矩阵保留、仅增加双块64偏移夹具及结果字段；原三倍/A/A/ABBA/16与64内轮/quiet/绑定/THP/唯一条件确认完全相同。

首次受控四串行新进程长批次完成，结果SHA`bb29645b05b16d6818e304745674b0e265eab0c1e124b3e7fe88b86f2bd954dc`。同句柄A/A、每批1/4线程分别16/64内轮，共1920轮，48次预热和48次批末SHA，非每内轮独立SHA。批内均值形成四进程配对比，再取中位：

| 接口 | 1线程耗时比 / 吞吐 | 4线程耗时比 / 吞吐 |
| --- | ---: | ---: |
| 纯apply | 0.317161 / **3.152974倍** | 0.471095 / **2.122713倍** |
| 真正分离输出 | 0.253066 / 3.951544倍 | 0.208565 / 4.794678倍 |
| 旧copy+apply | 0.478835 / 2.088401倍 | 0.759635 / 1.316421倍 |
| 准备+首组分离输出 | 0.656558 | 0.864293 |

纯apply进程比1线程`[0.324083,0.319710,0.314612,0.312783]`，4线程`[0.471732,0.471652,0.470538,0.467386]`。A/A中位B/A为1.016711/1.008858，单对范围0.968992—1.023759、0.997452—1.037749，两档控制均有效。全部输出/源/保护区、实际团队/TID绑定、前后精确VMA/16MiB全THP通过。唯一失败是四线程纯apply，按冻结规则跳过确认，新增系列/原生调用0，不重试择优、不采用默认。

[133份原件及原始数组复算](../../report/data/skylake-andn-normal-v1/README.md)完整保留，1920轮均独立重算一致。80对79不是同场直接配对，不能拿跨场数字证明普通写的独立性能差异；结论仅是新80未达到本轮原门槛。密集ID预取与当前输入/输出的完整组合虽未测过，但39和56已有负面证据，重复未来输入加载/地址计算和提示的负担未消除，高LQ计数不证明预取能释放资源或逆转旧结果，因此本阶段没有为该假设编写或运行候选。

复现恢复PR73依赖的固定模型、大流及独立oracle并核对SHA，使用新输出目录：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-andn-normal-v1.json --output artifacts/skylake-andn-normal-linux-build-v1
python3 -P artifacts/skylake-andn-normal-static-v1/check-v2.py
python3 scripts/verify_skylake_andn_normal_linux.py --plan experiments/skylake-andn-normal-v1.json --build artifacts/skylake-andn-normal-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-andn-normal-linux-full-v1 --affinity-cpus 0,2,4,6
python3 artifacts/skylake-andn-normal-preflight-v1/prepare-performance.py
python3 scripts/bench_skylake_andn_normal_long_linux.py --policy experiments/skylake-andn-normal-long-perf-v1.json --output artifacts/skylake-andn-normal-long-perf-v1
```

交付核对133份清单、72项冻结源和构建/全域/静态身份、155份暂存实验/脚本/档案blob逐字节一致，语法及空白检查通过。冻结patch上下文前缀空格使用单独属性，不改原字节。Windows11/Anaconda Python3.13.12标准库的只读交付生成器首次内联引号错误未执行，改成独立Python文件后核对通过；无原生重测，补充留证不改原始清单。

操作前fetch GitHub，完整读取68份PR正文与前67份逐项比较仅新增74，其余相同；74正文/全部评论/review/行内再刷新均无新意见，updated检索无新PR/issue。main b19c5a0及337a3dd/876e15b8/397cc367均包含，issue7修复保留，issue8接口/预算/实板继续跟踪。Discussion接口仍不能读取，保留缺口，不合并或关闭事项。

实际Skylake、缺BMI1硬件、官方派生表许可/预算/Threshold仍未验证，未锁频控温或保证宿主独占，整体三倍未完成。
