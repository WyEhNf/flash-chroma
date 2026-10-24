# 首级逐分量窄域的完整成本规模普查

Agent：`/root/tail`。Operator：本任务用户。状态：有限合同、真实完整支撑与唯一只读规模普查、独立审计完成；通过固定资源门，尚未构造CP模型或求解，没有新候选。

上一宽域在86节点各分量±2时，需32,842点和975,852安全表行，超过预先冻结的两项资源门。本阶段保留该负例，另取原max_first与741e55f的max48见证之间的逐分量闭整数区间。零delta分量固定，节点、坐标、轴和后三层之外的语义不变，最终预算仍取原max_first；不借见证稍差的mean，也不使用100图选择窄域。见证源自原60图约束和完整色域，并非盲测产物。

## 固定对象与数学边界

原first NPZ为0ea0a380，固定904e/95cb/5b8后缀、85b0分输出侧表和143e5cc0完整流；见证为`741e55f55c674384543511dc20b98ecd7d6a1ed4c1b9bb17406cabd7cc86bea0`。全部输入完整SHA在frozen与run中。该见证此前相对原max_first六项预算失败的结论保持；另一次三分母质量资格也没有提供本阶段的额外预算。

若见证分量变化为d，则本阶段delta域为`[min(0,d),max(0,d)]`。实际剩53物理节点、95活动RGB分量，全部跨度最多2。原模型和见证都包含在窄域中，但分别不能证明同时满足cap与八预算。缩小域会丢失原宽域的其他解，门内不代表存在可行解。

单点端点使用实际Q16非负四面体权，保留固定节点完整累加。对某一输出分量，从所有下端逐节点递增到上端，每个节点的一步权重不超过65536，舍入结果每步只增0或1，因此覆盖端点间全部整数。三个输出分量的变量互不相同，故单点可达RGB集等于端点AABB。不同输入仍共享节点变量；逐点安全不能替代整模型联合可行性。

## 实际检查与规模

执行前独立AST通过，冻结25份源和12项输入，frozen SHA `f4a308ff64592ed33c98116b30b8ddb936925dee0dad91d4d617ff77f40452a7`。17³/33³有限合同分别在1,331个RGB点完整枚举36个混合节点赋值，覆盖共享角、固定角、不同输出分量活动、0/255边界及零delta；八角与独立四角正支撑、端点、全部可达RGB集合相等。

真实数据从53节点的两侧idx盒重新构造正支撑，候选几何行138,487，经实际正权筛和去重得到47,013输入。再独立扫描全部16,777,216输入的四角支撑，与新构造逐点一致。旧70,571并集只在构造结束后核包含关系，没有用它过滤或删点。原116个max50热点全部包含，外部固定域max²48。

两端点独立uint64四角重放通过；原模型输出与原完整流一致，见证在新完整支撑max²48。唯一成本普查完整枚举117,010个单点AABB状态。只有全盒安全且误差平方恒等于原值的36,678点省约束，其余点全部保留；其中9,843点的训练频数为0，仍保留全域作用。

| 资源 | 宽域已执行负例 | 本次窄域 | 固定上限 |
| --- | ---: | ---: | ---: |
| 保留点 | 32,842 | 10,335 | 16,384 |
| 安全RGB表行 | 975,852 | 51,926 | 500,000 |
| 不同误差平方选择器 | 93,564 | 21,825 | 131,072 |

三项均在门内。按本次结构预测95个节点分量变量、31,005个舍入输出变量、10,165个误差平方变量及21,825个布尔选择器，共63,090变量；31,005条精确舍入行。这只是模型规模推算，尚未创建这些变量或调用solver。

## 精度成本与资源计账

原预算的全域mean为0.7990738071534367、RMS为1.1976684589597302、p99为3、CVaR为4.029054534445704；原60图mean为0.6823481783784588、RMS为1.1366130440332765、p99为sqrt12、CVaR为4.303192100572805。保留全部47,185,920训练像素的整数频数与支撑外固定直方图。

mean和固定阈值CVaR沿用已完整验证的`ceil(2^20×差值)`整数成本，只允许保守退款；RMS使用平方差，p99使用固定阈值上方计数。所有零扰动成本为0，原完整根差合同及本次第二种整数符号平方算法核对2,550个实际成本池项通过。最大成本绝对总界24,922,879,913，逐项均小于2^62，没有使用双精度近似成本替代整数约束。

保存数组有效载荷3,508,248B；域/支撑相关数组4,747,593B；当前可见分块数组和峰173,224B，最大分块2,926状态。三者存在重叠，不能相加作为RAM峰值。baseline、gold、suffix各映射50,331,648B，训练mass映射67,108,864B；这些不是RSS结论，未来CP求解仍须另记资源。

独立离线audit重新由两固定节点数组构造分量域，核原误差、固定外部直方图、完整扫描计数、成本池、资源门和int64界，全部通过。安全状态数和不同误差平方计数复用唯一完整普查数组；没有第二次状态枚举、建CP、拟合、原生性能或RSS测量。

环境为Windows x86-64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4/Numba0.60.0；OMP/Numba上限4、BLAS1。质量共享主机，可与memory的1线程小型纯模型普查并行，数值阶段结束后明确释放CPU。没有本阶段速度比较，也未引入AVX512。

主要文件为`python/lutlab/channel_component_box.py`和`check/census/audit/archive_cinema_first_narrow_cost.py`；协议是`experiments/p16-cinema-first-narrow-cost-census-v1.json`，归档位于`report/data/p16-cinema-first-narrow-cost-census-20261024`。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_narrow_cost.py --output artifacts/cinema-first-narrow-cost-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/census_cinema_first_narrow_cost.py --contract artifacts/cinema-first-narrow-cost-contract-v1.json --output artifacts/cinema-first-narrow-cost-census-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_narrow_cost.py --stage artifacts/cinema-first-narrow-cost-census-v1 --output artifacts/cinema-first-narrow-cost-independent-v1.json
```

后续直接预算CP必须另立单次协议与有限合同，继续保护原max_first八预算及全域cap49；本阶段只说明资源门内，没有可行性、最优性、速度50%或综合升级结论。侧表与整链联合语义的官方许可仍未知。
