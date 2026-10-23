# 第16题速度第二阶段：后缀缓存准备复用AVX2

Agent：Codex /root/speed；Operator：当前用户；分支：`codex/p16-speed-20261023`；基于前阶段提交`dee46cd`。本阶段只优化完整prepare，保持最新Cinema a399四级模型、85直接ID编译方式、常驻格式和全部稳态像素TU。

85准备后缀缓存时，仍对合法颜色序列逐像素执行后三层标量映射。87在CPU/OS支持AVX2时，将该序列的完整八像素部分交给已存在的精确通用`avx2_chain`，不足八像素继续标量；没有AVX2仍用原标量。构建宏`P16_PREPARE_SIMD`只在独立新目标启用，实验revision为87。85冻结DLL原字节保留，没有重新链接它，也不改公共默认。

## 完整整数与资源验证

实际环境与前阶段一致：Windows11 26200 x64、Ryzen9 8945HX、GCC15.2 Release `-O3 -DNDEBUG`，仅像素TU启用AVX2、原80三个pair/normal TU另加BMI1，无AVX512/FMA/fast-math；Python3.12.14、NumPy1.26.4，进程CPU0/2/4/6，原生请求1/4线程。

87与85全部4,194,304个直接表词及256项palette相同，直表SHA仍为`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`。完整16,777,216色以原四级标量为oracle，87 AVX2原地/真分离1/4均零字节差，五个输出SHA均为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。另通过504组边界/偏移/哨兵/同址/真分离、11项拒绝和单级回退。固定模型mean、p99与max均保持原输出。

两者四级句柄均18,579,204 B，palette准备已知临时峰值容量均18,262,016 B，单级无派生表均272,859 B。这里是容量记账，没有执行RSS测量。独立核对五个复用像素/计时COFF对象的`.text`，87与85全部相同；本阶段没有新增稳态吞吐结论，不能用静态相同替代实测。

## 同场完整prepare确认

在执行前冻结[新计划](../../experiments/p16-prepare-simd-confirm-v1.json)：四个新进程，顺序AB/BA/BA/AB，每进程五组交错底层`jshc_cc_create`，共40次创建。prepare含本地热文件缓存下的读取、解析/合同校验、模型与后缀缓存/直表准备；Python文件hash、DLL加载、destroy和导表hash在计时外。输入和库SHA在计时外核验，第一/末组导出完整直接表检查。新协议额外在执行前核对脚本及支持脚本SHA，避免错用源码版本。

本次是85之后的增量优化，独立冻结门槛为中位耗时比≤0.95、任意进程≤1.05。没有将85首次准备优化的0.75门槛事后套用或改写；两项研究有各自事前计划。性能窗口内全体其它分支静默，本进程未结束时只等待其session，没有编译、JIT或原生验收并发。没有锁频控温或证明宿主完全独占，不作为Intel目标服务器的测量。

| 进程 | 87 / 85完整prepare中位耗时比 |
| --- | ---: |
| AB | 0.922218 |
| BA | 0.925282 |
| BA | 0.923781 |
| AB | 0.900454 |
| 四进程比值中位 | **0.923000** |

完整prepare再下降**7.7000%**，所有进程均改善，冻结门槛通过。不能把本场87/85与旧场85/80相乘并称为同场87/80。前阶段85稳态控制失败的结论保持，86真分离未入围的结论也保持；本阶段不是对它们的重试或补发通过。

87 DLL SHA为`58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158`，分母为冻结85 SHA `3778f0b46c161134837c54e4b19edc35cc38281a7776a2e7cea3aab2b8ecf018`。[精简证据](../../report/data/p16-prepare-simd-v1/README.md)保留原始40次create、完整验证、源/库/对象身份和只读独立复算。

复现先恢复对应提交的脚本与模型，使冻结SHA一致，再构建独立`jshc_direct_prepare_simd`目标；不要重建并覆盖85原件。运行入口：

```powershell
cmake --build artifacts/p16-speed-direct-build-v1 --target jshc_direct_prepare_simd -j 1
python -X utf8 scripts/confirm_p16_direct_prepare.py --plan experiments/p16-prepare-simd-confirm-v1.json --output <新目录>
```

阶段结论为后缀准备的增量优化通过，暂不升级公共默认。分配失败注入、真实无AVX2硬件、嵌套OpenMP、Linux、目标Intel和87稳态吞吐未新增验证；16MiB派生表的官方许可/预算仍未解决。未推送、创建PR、合并或更改AGENTS.md，提交由父任务统一交付。

交付检查同时修复前提交的归档原字节问题：先暂存后追加`-text`规则时，Git缓存未重读44份首阶段CRLF原件，导致归档blob被规范化为LF。实际artifacts、磁盘原件、原始计时及数值结论没有改变；本提交对限定阶段路径执行`git add --renormalize`恢复原字节，不改写旧提交历史。两阶段共60项归档文件现均逐blob与清单SHA一致，三个入口语法、只读统计复算、暂存空白和AGENTS未修改检查通过。
