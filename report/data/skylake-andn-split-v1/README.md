# ANDN分入口编译：完整精度通过，整体三倍失败

对应[阶段说明](../../../docs/stages/2026-10-21-skylake-andn-split.md)。75—77在静态门槛停止，未加载候选库、执行像素或性能；78静态及完整RGB8通过，但首次受控长批次纯apply单/四线程为2.970394/2.525664倍，整体目标未完成。两档A/A有效，按事前规则跳过唯一确认，新增确认调用0，不重测择优、不采用。

- `manifest.json`逐字节标识163份原始档案；不自包含，也不包含后补README、audit、远端记录、补充只读profile及本文档。
- 四个`*-linux-build-v1`保存实际库、构建命令/日志/编译清单、测量源码ZIP和其余中间产物ZIP。服务器必须按冻结源重新构建，归档.so只作WSL/glibc2.43本机证据。
- 四个`*-static-v1`保存反汇编、检查器和独立审计。75保留UTF-8读取前置失败；77保留回边识别结果及补充32像素直线审计；78保留死掩码误判初件和正式v2。热区无栈不表示全函数无栈。
- `*-preflight-v1`保存策略生成器及76/77准备后未执行的验证/性能框架；未执行脚本不代表测试通过。78的完整域、构建和静态v2绑定后才生成正式性能身份。
- `skylake-andn-split-linux-full-v1`记录独立16,777,216色物理表重建及24组完整RGB8接口配置，另有有限/保护页/对齐/API检查，全部字节和哨兵零差。
- `skylake-andn-split-long-perf-v1`保存四个串行新进程的全部1920内轮数组、绑定/THP/源与边界诊断、48次预热及批末SHA。批内均值形成各进程配对比，再取四对中位；非逐内轮独立SHA。
- `audit.json`由`archive.py`只读独立复算全部中位、A/A及计数，未新增像素或计时。`confirmation-decision.json`按首次失败跳过确认，绑定首次结果和策略SHA。
- `remote-check.json`及`remote-snapshot.zip`记录相关PR全文、意见、issue7/8当前正文/历史评论及差异核对。Discussion刷新接口不可用，保留缺口，不把缺口当作没有意见，不合并或关闭事项。
- `skylake-brick2-packed-profile-v1`另有3份原件和独立清单：2³砖块3bit解码完整域零差，但行集合比0.83619高于事前0.80，因此停止，没有原生或性能。环境单列为Windows11、Anaconda Python3.13.12、NumPy2.4.6，不当作Linux执行结果。

环境为Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu Linux6.18.33.2、GCC15.2、Python3.14.4标准库；通用AVX2/Skylake调优，仅独立ANDN TU增加BMI1并有CPU检测回退。未在真实Skylake或缺BMI1硬件执行，未锁频控温。模型由`report/data/skylake-palette-v1/fixed-models.zip`恢复，大流按各计划SHA恢复；不改冻结原件或在原目录覆盖重跑。
