# 首级节点分量±2盒的必要误差下界

Agent：`/root/tail`。Operator：本任务用户。状态：完成，未发现盒内不可行障碍，也未证明联合可行。没有新模型或默认升级。

上一阶段一次八色扫描把 max50 计数从116降至91，但最大误差仍为√50。本阶段回到原始 `max_first`（首级0ea0、第二级904e、第三级95cb、末级5b8、完整流143e），只检查原116个 max50 输入在86个选中物理节点分量±2盒内的必要条件，不使用失败八色候选的节点或预算。

## 必要下界及适用范围

对86个节点的每个RGB分量，分别允许原值±2并与[0,255]取交；其他节点及全部Q16坐标、三级后缀固定。由于四面体权重非负，逐点各输出通道的最小/最大未舍入acc可通过把全部变量取其分量下/上界精确得到。half-up后得到首级RGB8包围盒，每通道至多5个整数值，单点至多125个首级RGB8候选。

将该包围盒所有整数RGB查入当前固定后缀，得到到真实gold的最小平方误差。它是**放松必要下界**：盒内中间整数RGB可能有节点整数可达间隙，而且不同热点共享相同节点、不能各自独立选择其最优arrival。这两个限制被有意放松，没有当作已经解决。

若任一点的这个下界大于49，即可证明整个固定86节点分量±2盒不可能将全域max²降至49，甚至不必额外要求mean/RMS/p99/CVaR预算。反过来，全部下界≤49只能说明该必要条件没有发现障碍，不能说多节点联合可行或全局最优。

## 实际结果

固定116点、86节点一共枚举8,993个整数首级RGB8，全部116点的放松最小平方误差均为22，阻塞点为0。因此本阶段**没有得到±2盒不可行证书**，也没有获得可部署的联合节点修改。

这116个旧max50点的真实gold全部为(0,0,0)。例如原色(36,43,142)的盒中首级(7,6,5)可在固定后缀得到(3,2,3)，平方误差为22。该记录说明某些逐点放松arrival可以明显低于49；不能把它当作86节点能同时实现全部这些arrival、保护其余旁侧输入或满足原60图平均/尾部预算的证据。

有限17/33模型合同包括2个独立全低/全高端点和16个随机内部节点模型，验证纯Python整数acc范围与独立uint64前向一致。真实证书在查询前冻结完整输入、源、协议和环境身份；另一个独立检查器通过八角解析权重和uint64累加复算全部116点端点，并重新枚举全部8,993个RGB8查表值，比较最小值、首个argmin和完整误差直方图，全部通过。首级与最终原基线RGB、真实gold、模型及后缀SHA也同时核对。

测试环境为共享Windows x86-64主机及项目Python3.12环境，Python整数/NumPy uint64计算，无新的原生编译、速度测量或百图选型。精简归档为 [report/data/p16-cinema-first-box-20261024](../../report/data/p16-cinema-first-box-20261024)；其中保留完整系数、acc端点、放松盒、误差直方图、所有argmin原件，以及执行前冻结身份、合同与独立复核。模型和完整后缀复用已归档的首级热点阶段，manifest SHA明确关联。

## 参考与边界

经典 [Agar与Allebach的minimax网格分配研究](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/cic/4/1/art00002) 以最大插值误差为目标，提示应将极值目标与MSE取舍分开；本用户另要求平均精度保护，因此不能只套用其最大误差收益。[Garcia与Gupta的lattice regression研究](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/cic/18/1/art00062) 强调直接优化实际插值后的误差。本项目进一步保留真实Q16和逐级RGB8整数语义，但本阶段只做必要条件诊断，没有复现这两篇论文的连续优化算法。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_box.py --output artifacts/cinema-first-box-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/certify_cinema_first_box.py --contract artifacts/cinema-first-box-contract-v1.json --output artifacts/cinema-first-box-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_box.py --certificate artifacts/cinema-first-box-v1.json --output artifacts/cinema-first-box-independent-v1.json
```

主要源为 `python/lutlab/integer_first_box.py` 及 `scripts/{check,certify,audit,archive}_cinema_first_box.py`，协议为 `experiments/p16-cinema-first-box-v1.json`。未执行新的完整四级/native/百图/性能验收，也未改变分输出坐标研究表示的官方许可状态。
