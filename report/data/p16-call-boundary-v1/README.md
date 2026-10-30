# 同87调用边界原始证据

Agent：Codex /root/speed；Operator：当前用户。实际2026-10-24 Windows11 x64、Ryzen9 8945HX、GCC15.2 Release、Python3.12.14/NumPy1.26.4。CPU允许集合0/2/4/6，非逐TID绑定；未锁频控温、宿主独占或Intel实测。[阶段说明](../../../docs/stages/2026-10-24-p16-call-boundary.md)完整说明两类模型、18场景及3项控制失败。

`raw-evidence.zip`原字节STORE保存冻结计划、正确性、结果、四进程完整/partial共11份JSON；`raw-members.json`绑定大小和SHA。另直接保存前三份供审阅。144个正式记录、全部控制数组保留，不重试失败场景。probe是同87函数指针的纯原生整批/逐图驱动，没有Python逐图循环；没有新的批API或纯fork成本数据。

`execution-sources.zip`保留9份实际执行的Python依赖原字节，`identity.json`给出工作区执行SHA、旧Git blob SHA与换行一致性，防止CRLF被当成旧Git LF原件。未修改旧依赖。probe自身源码、脚本/审计、构建参数和DLL身份另记录，原87模型/库不变。固定a399模型可复用`../p16-final-model-pair-v1/fixed-models.zip`，ordinary首级由冻结计划指定SHA。

只读复算不加载DLL、不计时：

```powershell
python -X utf8 scripts/audit_p16_call_boundary.py report/data/p16-call-boundary-v1/raw-evidence.zip
```

新目录从头复现先构建probe，再verify/measure；重建库SHA变化须另建计划，不改旧身份或覆盖原件：

```powershell
cmake -S experiments/p16-call-boundary -B artifacts/p16-call-boundary-build-new -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe
cmake --build artifacts/p16-call-boundary-build-new -j 1
python -X utf8 scripts/study_p16_call_boundary.py --plan experiments/p16-call-boundary-v1.json --output artifacts/p16-call-boundary-new --mode verify
python -X utf8 scripts/study_p16_call_boundary.py --plan experiments/p16-call-boundary-v1.json --output artifacts/p16-call-boundary-new --mode measure
```

`offline-audit.json`为独立复算；`manifest.json`绑定除清单自身的全部原字节。指标仅为已有调用边界，新segment入口将另行验证和测量，不把本轮收益冒充新API实测。
