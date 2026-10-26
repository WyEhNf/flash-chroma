# 对齐双mean与p99/max目标的独立节点试验

代理 `/root/tail` 按本会话用户授权执行。本阶段独立于上一轮cap1522五预算试验，从其冻结末节点和固定相容stripe场开始，尝试较宽但仍好于原模型的max上界、较大步长和mean优先目标。原3e5f比较基线不变。结果改善了RMS/max/CVaR，但完整域和训练mean仍分别比原模型高1.322%/1.312%，因此拒绝，不追加本机制的轮数，也不将旧五预算失败改写为通过。

## 为什么重定向及冻结内容

旧一轮结束时最大超预算由两项mean主导（约+1.7%），RMS平方不是最终主导约束；它仅在第0色后短暂最大。因此删除RMS本身不足以保证扭转。本轮的额外机会明确为：从已有p99超阈余量开始，先追回双mean；max硬上界d²1522→1600（max≤40仍小于原41.012193）；方向从26个RGB±1扩大为26方向×步长{1,2}，以跨越整数平台。

预算为一次颜色组0..7，按节点号升序选择52提案；每节点完整支撑，硬max≤1600，d²>40计数在每个接受步骤始终不超过原3e5f的165930。目标只使用双mean正超额 `(max,sum)`，再训练mean/uniform mean；RMS/CVaR仅观察，不参与选择。最终原3e5f双mean与p99count三项全部通过才能继续正式独立整域/照片/边界验收。没有中途照片选型、额外扫数或临时放宽。

`channel_tail_nodes.gains`增加默认1的可选整数步长，节点合法性和输出舍入都使用实际步长。新合同在m17/33各2056点、各138个合法节点方向核对独立物理u64/fresh/设计输出，零字节差；包含0/255节点±2越界拒绝，gain误差<3.6e-12、cap计数零差。旧调用默认步长1的数学语义保持，历史源码/测量字节保存在各自阶段ZIP，没有改旧证据。

## 真实结果与拒绝

| 完整域指标 | 原3e5f | 旧五预算末节点 | 本轮mean优先末节点 |
| --- | --- | --- | --- |
| mean | 0.886672865 | 0.901736680 | 0.898392959 |
| RMS | 1.648294036 | 1.652026856 | 1.646305260 |
| p99 | 6.324555320 | 6.324555320 | 6.324555320 |
| max | 41.012193309 | 38.052595181 | 38.000000000 |
| 最差1% CVaR | 9.984283370 | 9.933105661 | 9.881696102 |
| d²>40数量 | 165930 | 164072 | 165846 |
| 60图频率mean | 0.850324782 | 0.864688121 | 0.861483530 |

每组fresh全域输出与累加器零字节差，gain预测误差最大1.111e-8，hardmax和p99count预算始终通过；两项mean最终仍高于原预算，三约束门禁失败。RMS改善也说明不能把均值失败只归因于之前额外RMS约束；本次连续场、现有节点空间与固定预算未找到同时满足用户重点的方案。

为完整披露观察量，拟合结束后用分块研究前向对两项冻结末模型各补一次完整域直方图，得到表中的精确研究核p99/CVaR/RMS；输出均值/max与各自fit summary重算一致。该补充文件单独保存，未修改旧五预算run/summary。它不是独立u64整域终验；本失败候选没有照片、后拟合边界、原生或受控性能验收，不把研究核max38当成可直接替换的正式升级。

## 内存、环境与文件

Windows11 26200/AMD64、Ryzen9 8945HX，Python3.12.14、NumPy1.26.4、Numba0.60.0、psutil5.9；Numba4线程、OMP/BLAS/MKL环境1。开跑前可用内存4,782,912KB（约4.56GiB），已向协调者提前报告预计低于3GiB；八批记录最低2,688,974,848B（约2.50GiB），进程RSS最高2,105,348,096B（约1.96GiB）。这是离线研究进程数据，不是模型运行内存；未关闭他人程序或重设WSL。新插值仍不被现有ChannelLut/native支持，无速度50%底线结论，未切默认。

实现为 `run_velvia_mean_first_nodes.py`，扩展合同为 `verify_oriented_tail_nodes.py --steps 1 2`，观察为 `observe_velvia_mean_first.py`，静态归档为 `archive_velvia_mean_first.py`。[精简证据](../../report/data/velvia-mean-first-20261024/README.md)含冻结策略/预算、完整批次ZIP、失败研究模型、观察量、边界节点合同和实际源码SHA。旧试验仍在[独立阶段](2026-10-24-velvia-stripe-nodes.md)，本阶段只读引用其末节点。

```powershell
& $py scripts/verify_oriented_tail_nodes.py --steps 1 2 --output artifacts/oriented-tail-contract-v2-steps12.json
& $py scripts/run_velvia_mean_first_nodes.py --cache-root F:/Hackathon/projects/16-lut-color --contract artifacts/oriented-tail-contract-v2-steps12.json --output artifacts/velvia-mean-first-nodes-v1
& $py scripts/observe_velvia_mean_first.py --cache-root F:/Hackathon/projects/16-lut-color --output artifacts/velvia-mean-first-observations-v1.json
& $py scripts/archive_velvia_mean_first.py --output artifacts/velvia-mean-first-archive-v1
```

输出须不存在，先复现前一冻结节点项；`$py`指向上述环境。研究进程完成后释放设计内存。本阶段按冻结预算结束，不把局部失败推成该表示全局不可能，也不把mean代价隐去。
