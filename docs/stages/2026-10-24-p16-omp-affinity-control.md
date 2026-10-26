# 逐OpenMP线程控制：独立质量与两项失败证据

本阶段为后续性能实验补充Windows逐线程控制工具。旧实验的进程允许集合`0/2/4/6`并不保证每个OpenMP工作线程固定；当前实际libgomp文件的两个affinity入口仅为`ret`，不能凭`GOMP_CPU_AFFINITY`字符串宣称已经绑定。本阶段没有正式计时、没有生产内核变更，不改变任何旧A/A失效或低于50%的判定。

## 范围与环境

- 分支`codex/p16-tail-20261023`，沿同一`16ae431`基线；前一阶段为`a330cf6`。本阶段提交以Git历史为准。
- Windows 11 build 26200，Ryzen 9 8945HX，16核32逻辑CPU；独立Python 3.12.14进程，NumPy 1.26.4、psutil 5.9；没有在目标i7-14700运行。
- GCC 15.2.0，`E:/mingw64/bin/g++.exe` SHA256 `ebb478487f7dd90ae89c9afc36750e31afc48a9986109e1380723619f7d2272f`。
- 通用x64 helper，`-O2 -std=c++17 -shared -fopenmp -Wall -Wextra -pedantic -fstack-usage -MMD -MP`，没有AVX512或AVX/BMI编译选项。现有87/94模型调用仍为原AVX2后端。
- 实际加载且唯一的`E:/mingw64/bin/libgomp-1.dll` SHA256 `fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88`；不是仅凭PE依赖名推断路径。

## 工具合同

`experiments/p16-omp-affinity-control-v1/control.cpp`导出固定72B记录的`p16_omp_affinity`。它只接受单processor group、进程允许Mask为`0x55`、四线程team。action0读取各omp_tid对应的OS TID、Mask/Group和CPU；action1将四线程分别设为0/2/4/6的单bit；action2根据首次绑定保存的旧Mask恢复，先核同一OS TID，避免恢复到错误池成员。参数拒绝不写输出缓冲。

WinAPI可能逐线程部分成功后另一个线程失败，helper不保证事务性恢复。调用者遇到任何非零返回必须结束该独立测试进程，不能继续计时或假称已无损回退。恢复U策略时还须独立核全部Mask为`0x55`，不能把中间P→P调用返回的单bit误作原始Mask。

## 实际结果与失败保留

|阶段|实际结果|边界|
|---|---|---|
|build-v1|编译调用之后，SHA记录器把字符串当Path而抛AttributeError|DLL/日志/冻结原件保留；没有保存编译返回码，不宣称首次构建成功|
|build-v2|只修记录器的Path转换；构建返回0，PE导入libgomp与两项线程Mask API|helper DLL SHA256 `fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f`|
|quality-v1|65537像素虽然请求4线程，实际按65536块限制只启用2线程；随后池中另两项TID更换，质量断言失败|首次构造后的TID本来相同，不能描述成构造失败；partial/frozen/原脚本保留，无已记录输出或计时|
|quality-v2|固定786432像素，即12块、实际4线程；沿用同一helper DLL|12次team快照、87/94各两轮共4组输出零差、6项拒绝、唯一实际libgomp及恢复均通过；性能调用0|

成功只证明这批连续实际四线程调用能保持池成员和Mask。不能泛称任意1/2/4线程生命周期一次绑定即可；未来单线程与四线程场景应分开进程，逐组核真实TID和Mask。固定线程也可能减少可获调度时间，本阶段没有速度收益、频率原因或旧漂移原因的证明。

原模型为a399：首级`8136e92d…`、sidecar `85b045f0…`及原后三级，完整身份在`quality-frozen.json`；既有全色域oracle为`3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22`。本阶段4组只是固定786432像素夹具，并非新一次全色域质量或100图验收。

## 复现与证据

使用原项目`artifacts/error-study-py312/Scripts/python.exe`。原build-v1和quality-v1是有意保留的失败入口；独立v2入口不覆盖原源与目录。以下命令需从本worktree运行，输出目录必须全新：

```powershell
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe scripts/build_omp_affinity_control_v2.py --output artifacts/p16-omp-affinity-control-build-v2
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe scripts/check_omp_affinity_control_v2.py --library artifacts/p16-omp-affinity-control-build-v2/libp16_omp_affinity.dll --output artifacts/p16-omp-affinity-control-quality-v2 --cache-root F:/Hackathon/projects/16-lut-color
& F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe scripts/archive_omp_affinity_control.py --output report/data/p16-omp-affinity-control-v1
```

封存数据在`report/data/p16-omp-affinity-control-v1/`：两失败JSON、成功构建与质量、冻结身份、全部构建/质量原件`raw.zip`、实际源闭包`source.zip`，逐成员SHA/CRC在`independent-check.json`。外部编译器、libgomp、原模型与既有oracle按冻结路径及SHA核身份，不把整个SDK或重复模型副本打入本阶段。封存脚本只离线核原记录，不重跑模型或计时；脚本自身额外归档不冒充早于构建冻结。

实际执行源与原件以`-text`保持原字节；Git审计只允许本阶段说明与`.gitattributes`的既有LF规范化。不能用本工具质量通过替代后续性能实验的A/A或用户六档底线。

## 一手依据与未完成项

[Microsoft SetThreadAffinityMask](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadaffinitymask)说明成功返回旧Mask、零表示失败，且须属于进程允许集合；[GetThreadGroupAffinity](https://learn.microsoft.com/en-us/windows/win32/api/processtopologyapi/nf-processtopologyapi-getthreadgroupaffinity)读取真实线程Group/Mask。[GCC 15.2 configure.tgt](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-15.2.0/libgomp/configure.tgt)及[通用affinity.c](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-15.2.0/libgomp/affinity.c)仅作源码背景，Windows实物证据单独核验。

尚未完成逐TID控制下的新正式性能、Intel目标机、Linux、多processor group和其他OpenMP运行库验证。helper只供当前研究进程控制，没有主张生产可移植性改善或端到端冷启动收益。后续若只研究热性能，应明确排除的setup成本，不能冒充计入创建与首批输出的收益。
