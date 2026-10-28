# 单头性能修复：本机实测与原始证据

实现提交为 `271e10f`，基于 `aad1871`；完整说明见[阶段报告](../../../docs/stages/2026-10-28-header-performance-repair.md)。实际环境为 Windows11 / Ryzen9 8945HX / GCC15.2 Release C++17/C99 / Python3.12.14、NumPy1.26.4；CPU亲和0/2/4/6，OMP等待PASSIVE，不锁频。

- `quality.json`：5套模型、20条C++完整RGB8流及5条独立C99流，400项有限比较全部一致。
- `catalog.json`、`results.json`：本轮20配置、热映射/首批40点；一次完整场次分成2种计时上下文。19配置A/A通过，default U8 1T失败；首批单次观测没有稳定资格。严格选择按各点实际状态过滤。
- `regression.json`、`regression-summary.json`：旧评分库、修复前、修复后三方；640次正式调用和40次预热，所有输出SHA一致，24组A/A仅8组通过，不补轮择优。热映射的描述性fixed/before比约0.40～0.48；4T准备至首批约0.123/0.131且各自对照A/A通过。当前没有稳定追平旧库的资格。
- CTest和Python日志：AVX2/OpenMP与Scalar无OpenMP各15项合同通过，相关Python共41项通过；新direct合同包含347496项比较。`freestanding.json`只说明两个宿主端侧裁剪对象无未定义符号。
- `selected-fastest.json`、`cpp-selection-parity.json`：新目录的预算、连续加权和最小容量三种请求在C++/Python一致；实际百图入口记录另存，绑定模型、库和输出SHA。
- `raw-evidence.zip`：整个原始场次、三方全部周期/JSONL、此前原因分析原件、实际源码快照、构建命令/链接回执、修复前头和验证源；没有改写失败记录。模型包复用仓库已有7套内容寻址资产，本轮实测其中5套。
- `coordination*.json`：完整相关正文与意见检查、88条索引、连接器失败与重试，保留Discussion4不可读取缺口。PR保持Draft，不合并、不关闭issue。

`manifest.json`记录成员SHA和尺寸。归档复算只检查身份、统计与引用，不代表再执行数值或性能：

```powershell
python scripts/verify_frontier_evidence.py --evidence report/data/p16-header-performance-20261028
```

arena含完整准备临时区，宿主实际保留，不等于RSS硬上界。首次输出旧API含模型读盘、新API模型已读；旧prepare固定4T，新按请求线程。不能把1T首批对照作为同线程准备算法结论。没有实际移动/嵌入式板卡、Xeon6140、官方Threshold或未知LUT成绩。
