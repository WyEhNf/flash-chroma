# 新第二级后的两项末级补充：单扫未降尾部，局部MILP超时

Agent：Codex `/root`。Operator：本会话授权用户。Task：16题精度研究。Status：In Progress / Draft。本阶段没有可升级候选，保留两项独立预注册负例。

## 问题与起点

第二级max_first候选已独立验收完整色域mean0.799073807、p993、max√50；上一阶段对其全部热组做49整数球交均可行，没有取得固定前缀50下界。可行只是必要条件，尚不说明共享末级节点可同时实现这些输出。本阶段固定该候选的前三级，只探究末级节点，未替换287正式性能的模型。

先将已核验10633条第一级联合支撑，经独立uint64新第二级和原第三级前向，再按(arrival,gold)无损合并为1219条联合行、386个到达值、113个正支撑节点。用int64 `np.add.at` 保留全部16777216频数，用原60图质量累加；前阶段公开ZIP manifest逐字节绑定原支撑/候选。原末级的支撑输出与独立完整RGB流代表源、压缩直方图均一致。

这是离线压缩设计：几何117024B，4份78方向收益2538432B，不是运行时RAM优化，未测峰值RSS。

## 末级单扫

预注册 `p16-cinema-post-second-last-v1.json`：max_first与p99_first各自从同一0.799073807候选开始，78个±1/±2/±4方向，各一次八色扫描。双mean/双RMS及尾部九项绝对上限取当前起点，>8与>49计数每批不增，cap为 `max(49,起点d²)`，不回到更弱的旧best借预算。

| 策略 | mean | RMS | p99 | max | 最坏1% CVaR | 节点分量变化 |
|---|---:|---:|---:|---:|---:|---:|
| 起点 | 0.799073807 | 1.197668459 | 3 | √50 | 4.029054534 | 0 |
| max_first | 0.788901965 | 1.185099987 | 3 | √50 | 4.020245900 | 42 |
| p99_first | 0.799003354 | 1.187548034 | 3 | √50 | 3.988411576 | 57 |

全部颜色批次用新节点独立uint64重算，累计器、预测收益、真实九项预算与cap一致；原60图mean/RMS也不退。但两者的旧max50计数116均未减少，p99仍3，没有达到预注册“p99或max严格降低”的晋级门，因此两者均不升级，不追加新完整四级/native/百图/速度测试，也不以平均误差下降冒充尾部目标完成。新拟合原件保留以便后续另立协议研究，不回写旧阶段。

## 跨parity局部MILP

另一预注册 `p16-cinema-second-milp-v1.json` 从同一已独立验收0.799073807模型开始，而不是上述mean-only拟合。所有113个正支撑节点同时在±2盒内移动，目标max²≤49，p99阈值平方9，约束双mean/双RMS、>9计数及距离阈值3超额不增。

新模块显式参数化p99阈值，不修改旧阈值12模块及其记录。Q16 half-up保留精确整数舍入区间，平方误差用覆盖全部整数差值的线性下界；范数采用合法Cauchy支撑平面，实际输出须再经独立uint64和真实mean/RMS/CVaR门禁。有限9/12两模型均取得solver最优且实际输出0差；3个非法参数拒绝，outlier与CVaR约束阈值也独立检查。

实际问题9150变量、96097行、32086范数割。冻结协议允许最多4次合法范数细化，每次20秒/20000节点/gap0/线程1；但首轮约20.23秒到时，无incumbent，立即停止，实际只执行1轮。没有新节点候选，没有放大盒/延长时限/改目标。SciPy对`threads`的转发警告原样记录。

这个结果是有界离线求解未取得解；不是MILP不可行，更不是全模型的max50形式下界。不能由每个独立RGB球可行推断共享LUT节点可行，也不能由20秒无解声称已经最优。

## 环境与重放

实际Windows11 x64/Ryzen9 8945HX，Python3.12.14、NumPy1.26.4、Numba0.60、SciPy1.15.2；Numba请求4线程，BLAS/OMP环境1，HiGHS请求1线程。与其他代理质量构建/归档并行，全部seconds仅离线过程描述，不作运行时或官方服务器吞吐。没有新的照片训练/验证、原生映射或指定i7服务器成绩。

先设置UTF-8、BLAS/OMP线程1、`OMP_DYNAMIC=FALSE`、`OMP_WAIT_POLICY=PASSIVE`，使用原Python环境：

```text
python scripts/run_cinema_post_second_last.py --study artifacts/cinema-second-nodes-v1 --accept artifacts/cinema-second-accept-max_first-v1 --output artifacts/cinema-post-second-last-v1
python scripts/check_integer_target_last_milp.py --output artifacts/cinema-second-milp-v1-contract.json
python scripts/run_cinema_second_milp.py --contract artifacts/cinema-second-milp-v1-contract.json --output artifacts/cinema-second-milp-v1
python scripts/archive_cinema_second_refinement.py --output report/data/p16-cinema-second-refinement-v1
```

所有脚本拒绝覆盖输出。前阶段大输入/原始流与本阶段支撑、计划、实际执行源、原始结果的SHA均保留。封存目录见 [`p16-cinema-second-refinement-v1`](../../report/data/p16-cinema-second-refinement-v1/README.md)，本阶段仍在精度Draft PR90，提交时列实际commit，不合并。

实现参考的是本项目既有整数末级研究与[SciPy1.15.2 milp官方接口](https://docs.scipy.org/doc/scipy-1.15.2/reference/generated/scipy.optimize.milp.html)；范数切平面是本阶段明确的数值放松，不将官方求解器文档当本数据可行性证明。
