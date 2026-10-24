# 完全相同盒的查询共享：几何门通过，完整安全表仍超门

Agent：Codex `/root/tail`；Operator：WyEhNf（本会话用户）。任务为16题精度独立分支的离线完整安全表示研究；状态为原point资源门失败，未产生候选、未修改默认模型。

本阶段没有产生新精度模型。将相同首级RGB包围盒与相同gold的后缀查询共享后，完整171271输入的5284765个逻辑状态只需27817组、1267197个实际组状态查询，低于4194304查询门。但按原输入展开的危险点为17620，安全行1525836，分别超过8192和500000上限，严格STOP，不建CP、不求解、不改cap或节点半径。主、独立路径各查询1267197个状态，执行合计2534394。

这是离线研究表示的有界结果。原[全部最劣点扩展](2026-10-24-p16-cinema-current-outside-max-scale.md)的±2逐point状态门失败、[±1缩域](2026-10-24-p16-cinema-current-all-max-unit.md)安全规模通过、随后[有限CP的INFEASIBLE](2026-10-24-p16-cinema-current-cap40-feasible.md)及[GAC未判定](2026-10-24-p16-cinema-current-cap40-gac.md)全部保持各自原范围，不改写为本次已证可行或全局无解。

## 只改变枚举表示

固定模型仍为91d868d首级、904e/95cb/5b8后缀，轴、逐级RGB8 half-up语义均不变。消费b425b230阶段已认证的同273物理节点、全部RGB分量相对91d±2并clip、171271完整真实正支撑、全部231个原q41输入、原60图整数频数和支撑外固定直方图。已有完整16M正支撑重建和342542个独立uint64端点证明被绑定复用，没有为本次重选节点、删除零训练频数点或扫描照片。

静态检查既有实现后才立新协议。旧`channel_capped_risk.enumerate_stats/collect_allowed`对每offset的全部原point直接查询；±1独立检查的“分组展开”是分块拼接原point状态再归约，不共享相同盒查询。既有后级拟合的`(固定arrivalRGB,goldRGB)`联合频数压缩，也没有处理本次可变首级包围盒。未发现已执行过相同九字节盒共享的阶段。

新分组键严格为九个uint8：`(loR,loG,loB,hiR,hiG,hiB,goldR,goldG,goldB)`。只完全相同才共享，不按哈希近似、相同宽度或部分颜色合并。NumPy字典序unique保存组代表、完整inverse和重数；独立标准库tuple/dict重建全部171271行及同一稳定组序。相同盒中的每个RGB状态经过固定后缀、与相同gold比较，整数误差平方必相同，因此共享后能向每个原point完整散回。

未来即使安全表可容纳，也不能因此合并不同point的Q16节点约束。它们的完整acc、正权系数和共享节点耦合仍可能不同。本阶段没有生成这样的求解问题。

## 先几何计数，再单独授权真实查询

两个执行阶段使用独立协议、冻结和输出目录。几何入口没有导入后缀lookup。真实screen冻结只在已通过几何门与独立重构后建立，旧执行源码不改。

| 项目 | 纯几何阶段 | 真实screen阶段 |
| --- | ---: | ---: |
| 冻结来源 | 21源、20输入 | 24源、25输入 |
| 新有限合同 | 6小例＋2门边界＋3非法域拒绝 | 4小例 |
| 完整原输入 | 171271 | 171271 |
| 完全相同盒组 | 27817 | 27817 |
| 原point逻辑状态 | 5284765 | 5284765 |
| 主路径真实后缀查询 | 0 | 1267197 |
| 独立真实后缀查询 | 0 | 1267197 |
| 执行合计真实查询 | 0 | 2534394 |
| CP／原生apply／性能采样 | 0 | 0 |

几何有限合同覆盖同盒异gold、同宽异位置、重复和打乱行、0/255端点、空输入、零训练质量、门的恰等于与超过边界。每个小例按原point完整笛卡尔展开，统计和安全CSR必须等于分组散回。screen有限另核同一次查询同步生成统计与安全CSR，不能再调用`collect_allowed`悄悄查询第二遍。

真实主路径每组只查一次全部笛卡尔状态，同时计算min/max/count/safe_count/safe_max并保存完整组安全RGB CSR。独立路径以Python真整数三重循环和地址`((R*256)+G)*256+B`逐状态重放，不复用主offset归约。全部组统计、字典序安全CSR、完整inverse散回、原point危险集合及门值一致。

原4194304门在执行前明确按主路径与独立路径各自的完整查询数计算，二者执行合计另外完整报告，不能隐藏验证成本。旧5284765个逐point逻辑状态与其0查询STOP原件未改。

## 原point规模仍须完整计算

| 资源或可表示性条件 | 实测 | 固定上限 | 判定 |
| --- | ---: | ---: | --- |
| 每组完整真实查询 | 1267197 | 4194304 | 通过 |
| 单盒状态数 | 至多125 | 125 | 通过 |
| 原point危险点 | 17620 | 8192 | 失败 |
| 原point安全表行 | 1525836 | 500000 | 失败 |
| 无安全状态的原point | 0 | 0 | 通过 |

某危险组含m个point，则危险点贡献m，安全行贡献m乘该组safe_count。没有用组数替换原point数或折扣安全行。零训练频数point也保留。组安全CSR是完整离线中间证据；因原point两个资源门失败，没有生成原point的`danger-allowed.npz`，更没有把较小组CSR冒充已过500000门的CP表。

本结果说明此次精确查询共享确实降低后缀重复枚举，但既定后续约束规模仍超预算。空表为0只说明逐point必要条件未阻断，不说明存在共同节点赋值。它也没有证明该±2盒数学不可行，不能把资源STOP扩大为精度下界。

## 身份与运行记录

纯几何唯一session68694完整exit0，随后独立tuple全量重构通过；真实screen唯一session49233完整exit0，随后独立全状态重放通过。两者均在授权非性能窗口执行，结束主动释放CPU；没有重复模型拟合、原生质量、100图或速度测试。host并行背景按该质量窗口协调，不把这些时间用作性能结论。

实际运行环境为Windows 11、AMD Ryzen 9 8945HX，原只读研究环境Python 3.12.14／NumPy 1.26.4；具体解释器字符串、NumPy／psutil版本及字节序见本阶段两个冻结JSON。没有在隔离ORTools环境执行。主统计用有界int32误差平方与uint8计数；每盒至多125状态、平方差总和至多195075。独立geometry用标准库tuple/dict重建全部组；独立screen以Python真整数计算位址和三通道平方和，NumPy用于NPZ／映射表读取及数组字节比较，不复用主offset枚举或归约函数。本阶段消费原真实uint64端点证明，不冒称重新运行了节点端点或16M支撑重建。

| 原件 | SHA256 |
| --- | --- |
| geometry frozen | 6753527ad70f63659cd93ac29517e68525a39b2375170c4e7ebce3cb1fea8c8a |
| geometry contract | 63cb7e96b44eaf4b312c4938c84665631fd4cdc21cc2a1ef404758ac5024f6b0 |
| geometry groups | e0d2ad708d65adac99c7c571b8889c74b85382d4bae3fc410b21745fc4e2bf70 |
| geometry summary | 76b48dbfd6e6a081148c1048986ffcd0156b033603342a9720d05b7b404c7ec0 |
| geometry independent | f3b0dbf4e30fa7dc45baa8b97ed89f435c6faf3576c763d8607b5331c2ccb141 |
| screen frozen | d1103997455ee40d99381840b00291e102cd9721c1600420af79d71a638bd9fb |
| screen contract | 71e3fd8c7de270a7a1f6d8c1c05b42da6db6c0fee217e74c43c69587e1cb9727 |
| group screen | 464b0349c80ef5ee23d992519d43c7359c213868d6a2c1d021e6c11cfae5ffc5 |
| point screen | 37b00e42e30a5a1a56a8706efde5770b404e00b38855ca1154b59487c3f7e6ec |
| screen summary | faceafb72f5c4d7e2253d1da8840a55a8686fc15a54663f35ef2bcc226794aee |
| screen independent | 8bd29e5315224c0b658233ae83da2559e3979215386f20eb30dce03ab98b790b |

几何数组有效载荷原输入5483360B、组表示1357061B；计数进程观察peak working set64753664B、peak pagefile46608384B。这些是离线数组及进程观察，不能当作运行时部署RAM节省。真实screen的数组、分块暂态与进程观察保留在原summary，后续封存时如实列出；本阶段没有部署库或RSS性能资格。

实际首次执行命令如下。工作树和输入身份绑定上述冻结，原输出目录目前均已存在；脚本会拒绝覆盖，不应原地再次执行。需要重放时应恢复相同输入和无输出的隔离快照；跨绝对路径则须另立机械身份协议，不能修改本次执行源或把新SHA写回旧证明。以下是执行记录，不是授权在正式计时窗口运行：

```powershell
Set-Location -LiteralPath 'F:/Hackathon/worktrees/p16-tail-20261023'
$p16Python = 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
& $p16Python scripts/count_cinema_current_box_group.py freeze
& $p16Python scripts/count_cinema_current_box_group.py contract
& $p16Python scripts/count_cinema_current_box_group.py count
& $p16Python scripts/audit_cinema_current_box_group.py --output artifacts/cinema-current-box-group-geometry-v1/independent.json
& $p16Python scripts/screen_cinema_current_box_group.py freeze
& $p16Python scripts/screen_cinema_current_box_group.py contract
& $p16Python scripts/screen_cinema_current_box_group.py run
& $p16Python scripts/audit_cinema_current_box_group_screen.py --output artifacts/cinema-current-box-group-screen-v1/independent.json
```

原件在独立artifact目录。归档入口为`archive_cinema_current_box_group.py`，Git原字节核入口为`audit_cinema_current_box_group_git.py --git-ref :/HEAD --output <新的审计文件>`。归档要求原始JSON/NPZ及父阶段收据进入ZIP、每成员SHA256/CRC32回读，并保留外置短summary；不将大型数组展开JSON进Git，不重新执行像素或性能。正式性能窗口期间不压缩、计算哈希或Git写入，只有窗口释放及明确index交接后才执行封存。
