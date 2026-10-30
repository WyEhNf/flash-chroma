# cap40完整关系的补集成本普查

Agent：Codex `/root`；Operator：本会话用户；任务：16题精度独立分支；状态：本阶段普查与独立审核通过，未建新CP、未求解、未生成候选。本提交承载本阶段文档及证据；后续PR同步仍保持Draft。

## 目的与实际结果

只消费既有±2盒筛查和独立审核的9个固定JSON/NPZ，统计全部171271个原支撑point的关系大小，不重新查询suffix/gold/LUT/照片。按组省下的查询数量不能代替原point计费。

| 完整原point账单 | 数量 |
| --- | ---: |
| 危险point / 空安全表 | 17620 / 0 |
| 逐point允许表总行数 | 1525836 |
| 逐point禁止表总行数 | 187688 |
| 逐point取较短关系总行数 | 182274 |
| 较短关系选正表 / 禁表的point | 307 / 17313 |
| group禁止行 / 混合行 | 52952 / 50494 |

相同完整闭盒D下，允许S与禁止D\S语义等价；平手固定选禁表。非危险point方向0，选正表方向1，选禁表方向2，完整171271B方向表保留。混合表示行数减少约88.05%，这是已有关系的表示成本结论，不是新解、传播速度或部署内存。

原8192危险point与500000正表行的两门仍失败。若另建每危险point三个输出变量，仍投影为53679个整数变量和52860条Q16舍入约束；新行数低于500000不自动取得资源资格。任何后续编码须另定实际JSON/PB字节、内存及求解时间门。旧±1 INFEASIBLE和GAC固定点未判定结论均不改。

## 验证与环境

Windows11 x64、Ryzen9 8945HX；固定解释器`F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe`，Python3.12.14、NumPy1.26.4、psutil5.9；BLAS/MKL=1。主路径NumPy只读计数，独立路径仅stdlib按NPY头与小端整数逐point、逐group重数重建。未编译、未加载native、未import ORTools，没有性能采样；无需以线程/ISA结果解释本次整数计数。

先冻结4源（含只读AGENTS）和9输入，再执行6点边界/1空/5非法/7重复组合同、唯一完整普查和独立审核，四个命令均退出0。手算样本正131/禁132/混7；整数先拓宽再相减，避免uint8下溢。输入/源SHA首尾保持，完整原point、组散回、方向字节及投影一致。

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/census_cinema_cap40_complements.py freeze
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/census_cinema_cap40_complements.py contract
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/census_cinema_cap40_complements.py run
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_cap40_complements.py --output artifacts/cinema-cap40-complement-census-v1/independent.json
```

冻结SHA `4ef00659b21a3e2fd32efc645300812fb4f5f2f5011617ebbcd288ada6d9d665`，结果SHA `f6111ce032c9445c7325ae3e170072ddc08444dc0c4587f922c39d3b888a32cb`。主审计源与提案在`scripts/*cinema_cap40_complements*.py`及`experiments/p16-cinema-cap40-complement-census-v1.md`；原结果在`artifacts/cinema-cap40-complement-census-v1/`，可交付原件及7源/6原件的13成员ZIP在`report/data/p16-cinema-cap40-complements-20261024/`。Git审核独立检查本阶段实际blob与ZIP，不能称全历史重新验证。

## 资料与使用边界

读了[AAAI2017出版页及七页全文](https://ojs.aaai.org/index.php/AAAI/article/view/11127/10986)。其CTneg通过冲突数与有效域笛卡尔积比较来判断支持，负短表还要求元组不重叠。这里仅借鉴“表示禁止状态”的方向；未实现CTneg、短表或通配符，也不推断当前CP-SAT采用该论文的传播器。论文的实验不构成本项目性能证据。

[OR-Tools官方Python接口](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html)明确提供forbidden assignments，输入为单变量仿射表达式及禁止元组。已安装9.15.6755源码的同名方法亦有对应negated路径；本阶段没有导入或调用它。后续共享节点、Q16舍入、均值/p99、完整域与100图、速度50%底线仍各自需要验证。
