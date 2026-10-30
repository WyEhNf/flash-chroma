# 16题：P4 C99四字节原样复制的独立验证

Agent：`/root/memory`；Operator：当前16题研究用户；Status：唯一构建、机器码门、完整质量及唯一正式已完成。旧P4阶段589f9d1和全部原件保持，整体研究继续。

本单版检验同一P4表示的C99实现是否能减少palette读取与字节组装。实际常驻仍12,633,164B，原ROM、40B ABI、旧prepare/validate和AVX对象逐SHA复用。新C99精度100%保留，原生4T原地/分离各达50档；1T分离有效45.385871%低于底线，1T原地控制失效，因此四模式联合拒绝50。旧P4 AVX全局通过不替新C99背书。

## 从实汇编提出唯一改动

旧P4 Clang对象的前7项palette读取均为WORD+BYTE，再shl/or；旧合格linear C99的emit8直接memcpy4，已实际生成单DWORD读取。固定新入口只将`colors[lane][0..2]=color[0..2]`和第4B置0替换为`memcpy(colors[lane],color,4)`，其余8输入先读、8颜色先求、前7次组内重叠4B写/末3B写、短尾和IO验证不变。没有添加restrict、预取、ISA、输入选择或编译参数扫描。

palette每项真实完整占4B且prepare验证高字节为0。原字节[R,G,B,0]复制端序无关、非对齐合法，ID255最后项也没有越界；guard没有用来放宽外部src/dst。C99仍不依赖C++、OpenMP、AVX或堆，OMP仅桌面可选适配器。

独立符号`jshc_p4_apply_copy4`和`jshc_p4_apply_copy4_parallel`与旧入口并存，避免误测旧apply。新路由kernel0明确调用copy4；kernel1链接原AVX对象，只作数学一致性控制。整个质量阶段原P4 core对象SHA`4c6b215a054708a6803628bbfa9ea419a262b9447a18ddec658be53b45260216`及AVX对象SHA`4385fe648dd618daa11de9c4760f8253f84eacc7d6d317513a5bd36b1f539dd9`保持。

## 冻结、真实机器码及质量

唯一质量协议SHA为`9f6b8f226e8ea0bfc1609dae694e8f5b699666d05ba57e1829ed72d2af7919be`，25份执行源、23份输入在运行前冻结。Windows11 10.0.26200、AMD Ryzen9 8945HX/x64、Python3.12.14/NumPy1.26.4；C99由原Clang21.1.0、严格C99 generic x64无AVX参数编译，可选OMP适配器为GCC15.2.0。所有编译串行-j1，不重编旧core/AVX，不重新导出ROM。

唯一build session83934 exit0。新对象0x1f2/1f6/1fa/1fe/202/206/20a/20e实际是八个连续DWORD palette load，基址来自Model的palette字段；不再是原来的2B+1B组合。禁用的可选ISA指令为空。这个机器码门只证明预期机制实现，不证明实际速度。

门过后唯一quality session80764 exit0。主DLL SHA`0a61d36b6844ff54fce4f49ecd783cb3f1265e6c7a676f0fb85631bda7752090`；独立C99 DLL SHA`968a27907d1e34e32873f3c61d367e3922d6d2bd81a851e874bd16658b9819a5`。新旧apply绑定地址不同；纯C99新入口411次、主库新OMP C99入口1174次、AVX路由1176次均记录在原件中，含拒绝调用，不是像素/指令计数。主库直接core的另1次只是关闭Model拒绝，不能当成额外完整域。

九条完整色域输出摘要全为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`，九条完整百图流均为`f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528`，100张图逐图独立u64 oracle也全相等。有限890、IO拒绝113、格式拒绝21、src/dst guard180、ROM guard36、非对齐72全部通过。原/新模型mean/p99/max误差完全一致，保留100%、增幅0，并非相对数学参考误差为零。

新C99单函数静态帧120B，旧P4为136B；OMP入口128B/工作函数96B不变。这不是调用链或四线程栈总峰。质量进程峰WS148,561,920B、峰PrivateUsage93,954,048B包含Python、oracle、夹具、库和OMP，不能当prepare峰或纯模型RAM，也不能由不同质量进程40KiB级差异推断收益。逐图堆scratch0；总句柄155→253含库/运行时启动，不称全部回基线或OS泄漏。

独立离线audit只读取既有原件，重新核全部冻结SHA、新符号地址/调用记录、原对象、八DWORD门、九模式/逐图及全部合同计数，已通过；没有重新运行native、WASM或性能。

## 正式计时前协议

计划`fa7e029e4b0a3719b5cd4e6df78975bc7fdf99ea45338bae3acebfdcb1f47587`绑定35源、55输入。固定ref78/ref80、linear C99、旧P4 C99、新copy4 C99五角色，四fresh0x55；每角色两个phase各5 timed，完整role镜像，外围ref80控制和五角色自己的phase2/phase1全部须在[.8,1.25]，任一失效整cell全清档。每cell65调用，四worker共1040，其中800 timed，另五fresh RSS。

主比值仍同worker/同phase最快78/80除以候选，取所有phase/worker最劣；新对旧P4或linear仅辅助，不救底线。四模式均有效且最劣≥50才授全局档，失败原样保留，不补跑。每worker及每RSS还在自身进程记录实际依赖模块的准备前/后/close后绝对路径/SHA/数量，不把磁盘多目录或旧单fresh观察当它们实际加载证据。

独立预检只运行AST、身份和明确标为synthetic的整数协议用例：精确50、外围上界1.25、单角色自身漂移令整cell五角色失效、不能用合并phase救线。其native调用为0、实际RSS进程为0，不能挪用为速度或内存成绩。后续真实测量与synthetic分别封存。

## 唯一真实1040调用与判定

启动前只读1秒相关进程CPU增量预检通过，未杀未知进程或输出完整命令行，也不称宿主绝对独占。正式session31745完整exit0，四worker各260调用，另五RSS。所有源/库/实际模块身份、native返回、1040次完整百图SHA及CPU允许集检查通过，没有补跑、缩样或修改加载顺序。

96项控制中只有worker1、1T原地的新copy4自身phase2/phase1=0.793243582…低于0.8；原始五次中位数为150,348,900ns→119,263,300ns，外围ref80比0.807285690…仍有效。虽然候选后阶段变快，预定的稳定性下界仍适用。该cell的全部五角色失效，整个1T原地模式清档；其raw36.374593%只保留观察，不能作有效低50反例。其余15个worker/cell及三个模式全部有效。

| 角色 | 1T原地 | 1T分离% | 4T原地% | 4T分离% | 四模式联合 |
| --- | --- | ---: | ---: | ---: | --- |
| 原linear C99 | 控制失效 | 52.201191 | 62.525877 | 59.829194 | 有失效，未证 |
| 旧P4 C99 | 控制失效 | 40.906080 | 44.777827 | 44.039977 | 有效低50拒绝 |
| 新copy4 C99 | 控制失效 | 45.385871 | 51.675694 | 51.640240 | 有效低50拒绝 |

比值是各有效模式四worker×两phase共八比值最劣，主分母均为同phase更快78/80。新对旧P4同phase辅助吞吐保留比最劣在1T分离/4T原地/4T分离分别1.005859177/1.070717585/1.129476143；四线程有真实增益，但1T分离的有效45.385871%仍严格越线。不能将新旧不同阶段绝对耗时或历史最好worker拼起来。

本版要求四模式联合时，精度100/90/80/70/60/50与速度100/90/80/70/60/50的36格均不升级，依据是有效1T分离小于最宽松50底线。若产品只使用4T原地或4T分离，两种模式各自可进入精度100%/速度50%档、容量12,633,164B；这是x64纯C99核加可选OMP适配器的本机限定结论，不保证WASM、单线程或MCU速度。

独立60位Decimal审计后另用Fraction有理数复核1040真实调用、96控制、20模式最劣与同phase辅助比，结果逐项一致：15有效cell、1失效cell。没有根据复算结果新增采样。

## 每进程真实依赖与内存

本次四worker在同一进程内实际观察到四依赖各1份，全部来自ref78的`p16-memory-build-v2`目录。五个RSS均独立实际观察：ref80使用其原目录libgomp SHA`0ee0eacd…`、libgcc SHA`b1339579…`；其余各自目录为libgomp`fc756927…`、libgcc`46c950eb…`。stdc++和winpthread摘要一致。每份路径/数量/SHA都属于冻结输入；准备前为0、准备后/close后各1，关闭模型不等于卸载DLL。这些是本次各进程证据，补齐了前一单fresh观察不能外推RSS的范围。

| fresh角色 | prepare WS B | prepare PrivateUsage B | 进程峰WS B | 进程峰PrivateUsage B |
| --- | ---: | ---: | ---: | ---: |
| ref78 | 65458176 | 54661120 | 133513216 | 122740736 |
| ref80 | 65384448 | 54693888 | 133468160 | 122683392 |
| linear C99 | 53895168 | 24387584 | 53903360 | 24387584 |
| 旧P4 C99 | 49668096 | 24219648 | 49676288 | 24219648 |
| 新copy4 C99 | 49418240 | 23969792 | 49426432 | 23969792 |

新旧P4的prepare WS减去各自baseline均为13,393,920B，因此不把约250KiB绝对进程差异当成新的模型RAM节省。capacity保持不变，静态帧少16B单列；全部RSS含Python/imports、流式身份预检和实际模块枚举元数据，进程峰不是prepare专属峰或纯物理RAM。

## 已执行入口与交付边界

工作树为`F:/Hackathon/worktrees/p16-memory-20261023`，解释器为`F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe`。主入口如下，原目录均拒绝覆盖；完整命令、版本和stdout/stderr随raw保留。

```powershell
$p4Python = 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe'
& $p4Python scripts/freeze_page_id16_copy4.py
& $p4Python scripts/run_page_id16_copy4_quality.py --step build --output artifacts/p16-page-id16-copy4-v1
& $p4Python scripts/run_page_id16_copy4_quality.py --step quality --output artifacts/p16-page-id16-copy4-v1
& $p4Python scripts/audit_page_id16_copy4_quality.py --input artifacts/p16-page-id16-copy4-v1 --output artifacts/p16-page-id16-copy4-v1/quality-audit.json
& $p4Python scripts/freeze_page_id16_copy4_performance.py
& $p4Python scripts/preflight_page_id16_copy4_performance.py --output artifacts/p16-page-id16-copy4-preflight-v1
& $p4Python scripts/run_page_id16_copy4_performance.py --output artifacts/p16-page-id16-copy4-performance-v1
& $p4Python scripts/audit_page_id16_copy4_performance.py --input artifacts/p16-page-id16-copy4-performance-v1 --output artifacts/p16-page-id16-copy4-performance-v1/summary.json
```

原件见[发布manifest](../../report/data/p16-page-id16-copy4-v1/manifest.json)。旧ROM引用前一P4包中的实际字节，不重复导出；新源码/两库/对象/依赖/实汇编/全部真实和synthetic分区raw一并保留。独立WASM/ARM/RV32/BE方案仅静态，新C99全局50门未达到，未进入实现；是否另作纯功能验证须独立决定，不以移植补跑恢复速度资格。
