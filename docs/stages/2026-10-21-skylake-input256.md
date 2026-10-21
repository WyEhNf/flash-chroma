# 单YMM输入组合因热区栈spill停止

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23至少三倍吞吐；Status：Failed（81静态门槛）/ Draft，整体In Progress。基于Draft [PR75](https://github.com/WyEhNf/flash-chroma/pull/75)头`99cdfe7182e417ddea7a63cb48f2a665fd346af6`。

修订81只改变有效多线程原地的输入路径：每8像素一次32B输入，经VPERMD与VPSHUFB形成八个零高字节RGB24索引，分别按四ID屏障读取原调色板，保留当前预排NT输出、NTA、SFENCE及65536像素连续static分块。单线程原地及真正分离输出仍79 pair48，缺BMI1保持原精确线性回退；新多线程路径纯AVX2，不要求BMI。两个pair48及原linear TU含原导出名逐字节保持79，Handle及真正分离函数不变，没有新表、拟合或强制环境开关。新资格getter只报告AVX2与直表条件，不能作为实际内核执行证明。

输入整形已有修订34先例；34使用B低旧表、两级gather、32像素普通输出。50/51用两次窄读取合并，58拆XMM，59将50与预排输出组合，均没有当前标量四ID。这里验证的是完整组合，不声称输入机制首创。每8像素输入load由79的4次减为1次，但请求输入字节仍32B，64B对齐主体8次载荷有3次跨缓存行；输出预排与输入重排争用资源且新增共同依赖。[VPERMD](https://uops.info/html-instr/VPERMD_YMM_YMM_YMM.html)和[VEXTRACTI128](https://uops.info/html-instr/VEXTRACTI128_XMM_YMM_I8.html)的Skylake寄存器形式原始测量均为3周期依赖、1*p5，不能套用为新内存形式或整内核吞吐预测。

[计划](../../experiments/skylake-input256-v1.json)SHA`84150d8fcd166e94efb6ffe570cdf6fd9d1702c71f82d3477077243a2e188778`，72项冻结源；新TU SHA`6121a4146a49cc9e9007ad4ba378b2a07b39a984d436ed3544e9c47c9b8f48cc`。源码冻结后仅构建一次，环境Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu Linux6.18.33.2 / GCC15.2 / Python3.14.4，Release、通用AVX2与Skylake调优，仅两个保留pair TU加BMI1。构建SHA`ef6d8f23189c507142c746e2005adce18dbf9601ac10fc1539bfd491d9e355d8`；参考仍23的`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`，候选库SHA`8be24dcad16fb801914c32529c6326bb878a23381d48162b030dcfc9bb09a7db`。

静态筛查读取完整64/32像素区段。64主体`0xe8..0x727`共285条宏指令，8次输入均折叠进内存VPERMD，最大读200B；32区段4次，最大读104B，均在既有72/40像素的216/120B窗口内，精确24B尾原字节不变。四ID及全部输入/调色板早于图像写入成立，没有循环内RIP常量加载。三个保留对象.text等79，ISA范围通过。

64主体在`0x4c9`执行`vmovdqa %ymm1,-0x20(%rsp)`，在`0x6e9`重新加载`vmovdqa -0x20(%rsp),%ymm7`，是真实32B栈spill。预先冻结的无热区栈门槛失败，立即停止；32区段无栈不能豁免64失败。宏指令数相对79减少并非收益证据。初版checker把该spill存储计入图像输出，连带误报写入次数/先读后写；保留原件，v2只分类栈与图像写入，唯一失败仍为64主体无栈门槛，没有改候选、对象或验收条件。

本阶段未加载候选库，像素、完整RGB8、有限/保护页/地址偏移、性能和确认执行次数均0；新verify/bench胶水只派生并保存，未经执行，不能引用79/80精度成绩替代81。新模型资源仅源级保持，不虚构实测model_bytes。本轮静态停止不证明运行时精度有错，也不构成性能改善或退化的实测。

复现需先按前序档案恢复固定输入并核对SHA，使用新输出目录；本分支失败证据不覆盖、不继续计时：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-input256-v1.json --output artifacts/skylake-input256-linux-build-v1
python3 -P artifacts/skylake-input256-static-v1/check.py
```

正式v2结果SHA`5b3d7c9a3b3688cbedd66e79baca69d29f21895834a0b3959b172ea06ab4c9b2`；独立结果SHA`977cb954ff4133eaf8285d61182c9491203aa4c27b30a39995cefae061f36d08`同样仅64主体无栈门槛失败。独立解析覆盖五对象全部可执行节字节、输入标签到标量ID/palette、四ID及分派，没有模拟全部最终打包，也没有运行候选。32区段`0x768..0xaa5`共151条。独立报告没有用root结果作为结论。

v2保留初件，仅修统计分类；[34份证据原件](../../report/data/skylake-input256-v1/README.md)与72项冻结源/构建ZIP逐字节核对通过。归档解释器为Windows11/Anaconda Python3.13.12标准库。不能直接在已有目录覆盖重跑。

操作前fetch GitHub，读取69份完整PR正文与前68份比较仅新增75，其余相同；75正文/全部评论/review/行内为空，updated issue无新增。main仍b19c5a0，337a3dd、876e15b8、397cc367为本地祖先。issue7既知修复保留，issue8正式接口、资源预算及实板继续跟踪。Discussion接口不可读取，保留缺口，不合并或关闭事项。真实Skylake、缺BMI硬件、官方派生表许可/预算/Threshold与整体三倍尚未完成。
